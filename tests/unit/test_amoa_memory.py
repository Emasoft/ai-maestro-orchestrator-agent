#!/usr/bin/env python3
"""Tests for amoa_memory.py -- the memory recall/write helper (issue #12).

Real subprocess tests, no mocks: each test invokes the script exactly as the
orchestrator-memory-recall / orchestrator-memory-write skills do. The
memgrep-backed recall test runs only where memgrep is installed (skipped
otherwise — CI may lack the binary by design; the fallback tests always run).
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "amoa_memory.py"


def run_script(args, cwd, extra_env=None):
    """Run the memory helper with given args; return (code, stdout, stderr)."""
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)] + args,
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
        timeout=60,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


@pytest.fixture()
def memdir(tmp_path):
    """Fixture memory dir with three notes: surface match, body match, unrelated."""
    d = tmp_path / "memory"
    d.mkdir()
    (d / "project_rotator-login.md").write_text(
        "---\n"
        "name: project_rotator-login\n"
        'description: "rotator failed had to log in manually — where are the creds"\n'
        "metadata:\n"
        "  node_type: memory\n"
        "  type: project\n"
        "---\n\n"
        "Creds live in the macOS keychain under service ai-maestro.\n",
        encoding="utf-8",
    )
    (d / "reference_body-only.md").write_text(
        "---\n"
        "name: reference_body-only\n"
        'description: "unrelated surface about widget colors"\n'
        "metadata:\n"
        "  node_type: memory\n"
        "  type: reference\n"
        "---\n\n"
        "Once the rotator failed because the login token expired mid-run.\n",
        encoding="utf-8",
    )
    (d / "user_unrelated.md").write_text(
        "---\n"
        "name: user_unrelated\n"
        'description: "prefers tables with unicode borders"\n'
        "metadata:\n"
        "  node_type: memory\n"
        "  type: user\n"
        "---\n\n"
        "Always render test results as bordered tables.\n",
        encoding="utf-8",
    )
    return d


class TestRecallFallback:
    """Fallback recall (memgrep absent) — must degrade, never break."""

    def test_fallback_ranks_surface_match_first(self, memdir, tmp_path):
        """Description-match note outranks body-only note in fallback recall."""
        code, out, _ = run_script(
            [
                "recall",
                "rotator failed log in",
                "--memdir",
                str(memdir),
                "--no-memgrep",
            ],
            tmp_path,
        )
        assert code == 0
        lines = out.splitlines()
        assert lines, "expected at least one recalled note"
        assert "project_rotator-login.md" in lines[0]
        assert "rotator failed had to log in manually" in lines[0]

    def test_fallback_finds_body_only_match_when_no_surface_hit(self, memdir, tmp_path):
        """A query hitting only a note body still recalls that note."""
        code, out, _ = run_script(
            [
                "recall",
                "token expired mid-run",
                "--memdir",
                str(memdir),
                "--no-memgrep",
            ],
            tmp_path,
        )
        assert code == 0
        assert "reference_body-only.md" in out

    def test_fallback_no_match_is_empty_success(self, memdir, tmp_path):
        """Zero matches prints nothing and exits 0 (valid result, not error)."""
        code, out, _ = run_script(
            [
                "recall",
                "kubernetes ingress timeout",
                "--memdir",
                str(memdir),
                "--no-memgrep",
            ],
            tmp_path,
        )
        assert code == 0
        assert out == ""

    def test_missing_memdir_is_empty_success(self, tmp_path):
        """An absent memory dir means 'no memories yet', not a failure."""
        code, out, _ = run_script(
            ["recall", "anything", "--memdir", str(tmp_path / "nope"), "--no-memgrep"],
            tmp_path,
        )
        assert code == 0
        assert out == ""

    def test_index_files_are_excluded_from_recall(self, memdir, tmp_path):
        """MEMORY.md (the index) is never returned as a note."""
        (memdir / "MEMORY.md").write_text(
            "- [Rotator](project_rotator-login.md) — rotator failed log in\n",
            encoding="utf-8",
        )
        code, out, _ = run_script(
            [
                "recall",
                "rotator failed log in",
                "--memdir",
                str(memdir),
                "--no-memgrep",
            ],
            tmp_path,
        )
        assert code == 0
        assert "MEMORY.md —" not in out
        assert "/MEMORY.md" not in out.splitlines()[0]


@pytest.mark.skipif(shutil.which("memgrep") is None, reason="memgrep not installed")
class TestRecallMemgrep:
    """Recall through the real memgrep binary (runs only where installed)."""

    def test_memgrep_recall_returns_ranked_notes(self, memdir, tmp_path):
        """memgrep-backed recall surfaces the description-matching note."""
        code, out, _ = run_script(
            ["recall", "rotator failed log in", "--memdir", str(memdir)],
            tmp_path,
        )
        assert code == 0
        assert "project_rotator-login" in out


class TestWrite:
    """Note authoring — schema-valid note + MEMORY.md index line."""

    def test_write_creates_schema_valid_note_and_index_line(self, tmp_path):
        """Write produces frontmatter with name/description/metadata + index line."""
        memdir = tmp_path / "memory"
        code, out, _ = run_script(
            [
                "write",
                "--type",
                "project",
                "--slug",
                "kanban-label-cardinality",
                "--description",
                "assign label rejected / duplicate status labels",
                "--body",
                "Exactly one status:* label per issue.",
                "--memdir",
                str(memdir),
            ],
            tmp_path,
        )
        assert code == 0
        note = memdir / "project_kanban-label-cardinality.md"
        assert note.exists()
        assert out == str(note)
        text = note.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        assert "name: project_kanban-label-cardinality" in text
        assert 'description: "assign label rejected / duplicate status labels"' in text
        assert "node_type: memory" in text
        assert "type: project" in text
        assert "Exactly one status:* label per issue." in text
        index = (memdir / "MEMORY.md").read_text(encoding="utf-8")
        assert "(project_kanban-label-cardinality.md)" in index
        assert index.count("(project_kanban-label-cardinality.md)") == 1

    def test_write_then_recall_roundtrip(self, tmp_path):
        """Test B of the dual-test method: a written note is recallable from its symptom."""
        memdir = tmp_path / "memory"
        run_script(
            [
                "write",
                "--type",
                "feedback",
                "--slug",
                "ack-timeout",
                "--description",
                "implementer never acknowledged the assignment",
                "--body",
                "Reassign after 30 minutes without ACK. **Why:** stalls. **How to apply:** poll.",
                "--memdir",
                str(memdir),
            ],
            tmp_path,
        )
        code, out, _ = run_script(
            [
                "recall",
                "implementer never acknowledged",
                "--memdir",
                str(memdir),
                "--no-memgrep",
            ],
            tmp_path,
        )
        assert code == 0
        assert "feedback_ack-timeout.md" in out

    def test_write_refuses_duplicate_without_update(self, tmp_path):
        """A second write to the same note is refused (exit 3) unless --update."""
        memdir = tmp_path / "memory"
        args = [
            "write",
            "--type",
            "reference",
            "--slug",
            "retry-cap",
            "--description",
            "widget kept retrying / how many times",
            "--body",
            "The cap is 3.",
            "--memdir",
            str(memdir),
        ]
        code1, _, _ = run_script(args, tmp_path)
        assert code1 == 0
        code2, _, err2 = run_script(args, tmp_path)
        assert code2 == 3
        assert "refused" in err2
        code3, _, _ = run_script(args + ["--update"], tmp_path)
        assert code3 == 0

    def test_write_rejects_invalid_type(self, tmp_path):
        """An out-of-taxonomy type exits 2 with the reason on stderr."""
        code, _, err = run_script(
            [
                "write",
                "--type",
                "gossip",
                "--slug",
                "x",
                "--description",
                "d",
                "--body",
                "b",
                "--memdir",
                str(tmp_path / "memory"),
            ],
            tmp_path,
        )
        assert code == 2
        assert "type must be one of" in err

    def test_write_rejects_empty_body(self, tmp_path):
        """A note without a body is invalid (exit 2)."""
        code, _, err = run_script(
            [
                "write",
                "--type",
                "project",
                "--slug",
                "empty-body",
                "--description",
                "something failed somewhere",
                "--memdir",
                str(tmp_path / "memory"),
            ],
            tmp_path,
        )
        assert code == 2
        assert "body must not be empty" in err


INSTALLER_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "amoa_install_rules.py"
)


class TestRulesInstaller:
    """SessionStart rules installer — isolated HOME/project, real subprocess."""

    def _run_installer(self, tmp_path, plugin_root):
        """Run the installer hook with HOME and CLAUDE_PROJECT_DIR sandboxed."""
        home = tmp_path / "home"
        project = tmp_path / "project"
        (project / ".claude").mkdir(parents=True, exist_ok=True)
        (home / ".claude").mkdir(parents=True, exist_ok=True)
        # Project-scope settings reference the plugin -> project scope active.
        (project / ".claude" / "settings.json").write_text(
            '{"enabledPlugins": {"ai-maestro-orchestrator-agent@x": true}}',
            encoding="utf-8",
        )
        env = os.environ.copy()
        env["HOME"] = str(home)
        env["CLAUDE_PROJECT_DIR"] = str(project)
        env["CLAUDE_PLUGIN_ROOT"] = str(plugin_root)
        result = subprocess.run(
            [sys.executable, str(INSTALLER_PATH)],
            capture_output=True,
            text=True,
            env=env,
            input="{}",
            timeout=60,
        )
        return result, project

    def test_installer_copies_rules_into_project_scope(self, tmp_path):
        """rules/*.md from the plugin root land in <project>/.claude/rules/."""
        plugin_root = Path(__file__).resolve().parents[2]
        result, project = self._run_installer(tmp_path, plugin_root)
        assert result.returncode == 0
        installed = project / ".claude" / "rules" / "memory-protocol.md"
        assert installed.exists()
        src = plugin_root / "rules" / "memory-protocol.md"
        assert installed.read_bytes() == src.read_bytes()
        assert "memory-protocol.md" in result.stdout

    def test_installer_is_idempotent_and_silent_when_up_to_date(self, tmp_path):
        """A second run with an unchanged rule copies nothing and prints nothing."""
        plugin_root = Path(__file__).resolve().parents[2]
        self._run_installer(tmp_path, plugin_root)
        result2, _ = self._run_installer(tmp_path, plugin_root)
        assert result2.returncode == 0
        assert result2.stdout.strip() == ""

    def test_installer_noop_without_plugin_root(self, tmp_path):
        """Missing CLAUDE_PLUGIN_ROOT exits 0 silently (never blocks a session)."""
        env = os.environ.copy()
        env["HOME"] = str(tmp_path)
        env.pop("CLAUDE_PLUGIN_ROOT", None)
        env.pop("CLAUDE_PROJECT_DIR", None)
        result = subprocess.run(
            [sys.executable, str(INSTALLER_PATH)],
            capture_output=True,
            text=True,
            env=env,
            input="{}",
            timeout=60,
        )
        assert result.returncode == 0
        assert result.stdout.strip() == ""
