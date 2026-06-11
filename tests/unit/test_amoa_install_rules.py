#!/usr/bin/env python3
"""Real-subprocess tests for amoa_install_rules.py.

SessionStart hook. It copies the plugin's shipped rule files
(`<CLAUDE_PLUGIN_ROOT>/rules/*.md`) into every active install scope's
`.claude/rules/` directory so Claude Code's rule loader picks them up. A scope
is "active" when its settings file mentions the plugin name. Idempotency is
byte-size based: a destination that already exists with the SAME size is
skipped; a different size is overwritten.

No mocks: the actual script is invoked as a real subprocess with a fully
hermetic environment (`HOME`, `CLAUDE_PROJECT_DIR`, `CLAUDE_PLUGIN_ROOT` all
point at tmp_path-rooted dirs, via `env -i`-style isolation) so the test can
never touch the developer's real `~/.claude`. All assertions are made against
the real filesystem state the subprocess leaves behind.
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "amoa_install_rules.py"
)

PLUGIN_NAME = "ai-maestro-orchestrator-agent"
RULE_NAME = "memory-protocol.md"
RULE_BODY = "# Memory protocol\n\nfirst version of the rule body.\n"


def _make_plugin(plugin_root: Path, *, with_rules: bool, body: str = RULE_BODY) -> None:
    """Create a fake plugin tree; optionally ship one rule under rules/."""
    plugin_root.mkdir(parents=True, exist_ok=True)
    if with_rules:
        rules_dir = plugin_root / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        (rules_dir / RULE_NAME).write_text(body, encoding="utf-8")


def _make_project_scope(project_dir: Path) -> None:
    """Create a project scope whose settings.json references this plugin."""
    claude_dir = project_dir / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    (claude_dir / "settings.json").write_text(
        json.dumps({"enabledPlugins": [PLUGIN_NAME]}), encoding="utf-8"
    )


def run_install(
    home: Path, project_dir: Path | None, plugin_root: Path, stdin_text: str = "{}"
):
    """Invoke amoa_install_rules.py as a real subprocess with a hermetic env.

    Returns (exit_code, parsed_stdout_json_or_None, raw_stdout, raw_stderr).
    `HOME` is forced to a tmp dir so the user-scope detection branch can never
    match the developer's real ~/.claude/settings.json.
    """
    env = {
        "HOME": str(home),
        "CLAUDE_PLUGIN_ROOT": str(plugin_root),
        # Keep PATH so the interpreter's shared libs resolve on every platform.
        "PATH": _current_path(),
    }
    if project_dir is not None:
        env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        input=stdin_text,
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    out = result.stdout.strip()
    try:
        parsed = json.loads(out) if out else None
    except json.JSONDecodeError:
        parsed = None
    return result.returncode, parsed, out, result.stderr


def _current_path() -> str:
    import os

    return os.environ.get("PATH", "/usr/bin:/bin")


def test_installs_shipped_rules_into_active_scope(tmp_path):
    """Copies rules/*.md into the active scope's .claude/rules/ with identical bytes."""
    home = tmp_path / "home"
    project = tmp_path / "project"
    plugin = tmp_path / "plugin"
    home.mkdir()
    _make_plugin(plugin, with_rules=True)
    _make_project_scope(project)

    code, parsed, _out, err = run_install(home, project, plugin)

    # The hook must succeed and never crash the session.
    assert code == 0, f"non-zero exit; stderr={err!r}"

    # The shipped rule landed in the project scope's rules dir, byte-for-byte.
    installed = project / ".claude" / "rules" / RULE_NAME
    assert installed.is_file(), "rule was not installed into the active scope"
    assert installed.read_text(encoding="utf-8") == RULE_BODY

    # On a real install the hook reports what it installed via systemMessage.
    assert parsed is not None
    assert RULE_NAME in parsed["systemMessage"]
    assert PLUGIN_NAME in parsed["systemMessage"]


def test_idempotent_on_rerun_no_duplicate_no_error(tmp_path):
    """A second identical run copies nothing (same byte size), errors not, duplicates not."""
    home = tmp_path / "home"
    project = tmp_path / "project"
    plugin = tmp_path / "plugin"
    home.mkdir()
    _make_plugin(plugin, with_rules=True)
    _make_project_scope(project)

    # First run installs the rule.
    code1, parsed1, _o1, _e1 = run_install(home, project, plugin)
    assert code1 == 0
    assert parsed1 is not None and RULE_NAME in parsed1["systemMessage"]

    installed = project / ".claude" / "rules" / RULE_NAME
    first_bytes = installed.read_bytes()

    # Second run: destination already exists with the SAME size -> skip. The
    # script prints a systemMessage ONLY when it actually copied something, so
    # an idempotent re-run must produce EMPTY stdout (parsed is None).
    code2, parsed2, out2, err2 = run_install(home, project, plugin)
    assert code2 == 0, f"idempotent re-run failed; stderr={err2!r}"
    assert out2 == "", f"idempotent re-run should copy nothing; got stdout={out2!r}"
    assert parsed2 is None

    # No duplication: exactly one rule file, identical content to the first run.
    rules_dir = project / ".claude" / "rules"
    rule_files = sorted(p.name for p in rules_dir.iterdir() if p.suffix == ".md")
    assert rule_files == [RULE_NAME]
    assert installed.read_bytes() == first_bytes


def test_missing_source_rules_dir_is_graceful_noop(tmp_path):
    """A plugin with no rules/ dir is a silent no-op: exit 0, no output, nothing installed."""
    home = tmp_path / "home"
    project = tmp_path / "project"
    plugin = tmp_path / "plugin"
    home.mkdir()
    _make_plugin(plugin, with_rules=False)  # deliberately NO rules/ subdir
    _make_project_scope(project)

    code, parsed, out, err = run_install(home, project, plugin)

    # Missing source dir -> install_rules() returns [] -> main() exits 0 and
    # prints nothing. The hook must never crash a session over a missing dir.
    assert code == 0, f"missing rules/ dir should not crash; stderr={err!r}"
    assert out == "", f"no rules to install -> empty stdout; got {out!r}"
    assert parsed is None

    # Nothing was created in the project scope (no rules dir conjured up).
    assert not (project / ".claude" / "rules").exists()
