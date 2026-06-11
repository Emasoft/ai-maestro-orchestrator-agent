#!/usr/bin/env python3
"""Real-subprocess tests for the WIRED Stop hook: `python -m amoa_stop_check.main`.

hooks/hooks.json wires the Stop hook as:

    cd ${CLAUDE_PLUGIN_ROOT}/scripts && python3 -m amoa_stop_check.main

i.e. the MODULAR `amoa_stop_check` package, NOT the standalone
`scripts/amoa_orchestrator_stop_check.py` script (which has its own test file,
test_amoa_orchestrator_stop_check.py). This file closes that coverage gap by
exercising the exact module the harness invokes.

Contract of the modular hook (verified empirically, not assumed):

  * It gates EVERYTHING on the existence of the orchestrator-loop state file
    `.claude/orchestrator-loop.local.md` resolved relative to the process CWD.
    If that file is ABSENT, the hook allows exit immediately.
  * The hook ALWAYS exits 0. A "block" is signaled by a JSON object on STDOUT
    containing `{"decision": "block", ...}` (the harness reads stdout, not the
    exit code, to decide whether to block). An "allow" prints no decision.
  * Malformed/empty stdin is swallowed (treated as `{}`); the decision then
    follows the (absent) state file -> allow.

No mocks: the package is invoked as a real subprocess, mirroring the wired
command — `python -m amoa_stop_check.main` with CWD set to a tmp dir (so state
files are read from tmp_path) and PYTHONPATH pointed at scripts/ (so the
`amoa_stop_check` package import resolves, exactly as `cd scripts` does for the
hook). All state files are real files written under tmp_path.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"


def run_stop_hook(cwd: Path, stdin_text: str = "{}"):
    """Invoke `python -m amoa_stop_check.main` as the wired hook does.

    CWD is the supplied tmp dir (state files are CWD-relative). PYTHONPATH adds
    scripts/ so the package resolves while CWD stays at the tmp dir — the same
    effect as the hook's `cd ${CLAUDE_PLUGIN_ROOT}/scripts`.

    Returns (exit_code, parsed_stdout_json_or_None, raw_stdout, raw_stderr).
    """
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        f"{SCRIPTS_DIR}{os.pathsep}{existing}" if existing else str(SCRIPTS_DIR)
    )
    # Defensive: clear the recursion guard so a nested test runner env can't
    # short-circuit the hook before it does any work.
    env.pop("ORCHESTRATOR_RECURSION_GUARD", None)
    result = subprocess.run(
        [sys.executable, "-m", "amoa_stop_check.main"],
        input=stdin_text,
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
        timeout=60,
    )
    out = result.stdout.strip()
    try:
        parsed = json.loads(out) if out else None
    except json.JSONDecodeError:
        parsed = None
    return result.returncode, parsed, out, result.stderr


def _write_orchestrator_loop(cwd: Path) -> Path:
    """Write the orchestrator-loop state file that ARMS the hook (CWD-relative)."""
    claude = cwd / ".claude"
    claude.mkdir(parents=True, exist_ok=True)
    f = claude / "orchestrator-loop.local.md"
    f.write_text(
        "---\n"
        "iteration: 0\n"
        "max_iterations: 100\n"
        "check_github: false\n"  # never shell out to gh in tests
        "---\nbody\n",
        encoding="utf-8",
    )
    return f


def _write_plan_phase(cwd: Path, *, complete: bool) -> Path:
    """Write the plan-phase state file; `complete=False` makes the hook block."""
    claude = cwd / ".claude"
    claude.mkdir(parents=True, exist_ok=True)
    f = claude / "orchestrator-plan-phase.local.md"
    if complete:
        body = (
            "---\n"
            "plan_phase_complete: true\n"
            "status: approved\n"
            "requirements_complete: true\n"
            "---\nbody\n"
        )
    else:
        body = (
            "---\n"
            "plan_phase_complete: false\n"
            "status: drafting\n"
            "requirements_complete: false\n"
            "---\nbody\n"
        )
    f.write_text(body, encoding="utf-8")
    return f


def test_blocks_exit_with_open_tasks(tmp_path):
    """Blocks exit (stdout decision=block) when the orchestrator loop is armed and Plan Phase is incomplete."""
    # Arm the hook (state file present) AND put it in an incomplete Plan Phase:
    # the plan is still drafting with requirements incomplete -> the hook must
    # refuse to allow exit and emit a blocking decision on stdout.
    _write_orchestrator_loop(tmp_path)
    _write_plan_phase(tmp_path, complete=False)

    code, parsed, out, err = run_stop_hook(tmp_path, json.dumps({"transcript_path": ""}))

    # The block is signaled via stdout JSON, NOT the exit code (always 0).
    assert code == 0, f"hook must always exit 0; stderr={err!r}"
    assert parsed is not None, f"expected a blocking JSON decision; stdout={out!r}"
    assert parsed["decision"] == "block"
    # The reason must explain WHY (Plan Phase incomplete), proving the decision
    # was driven by real state, not a blanket block.
    assert "plan" in parsed["reason"].lower()
    assert "systemMessage" in parsed


def test_allows_exit_when_all_complete(tmp_path):
    """Allows exit (exit 0, no block decision) when the orchestrator loop is not active."""
    # No orchestrator-loop state file at all -> the hook's first gate allows
    # exit immediately. This is the genuine "nothing pending, let me stop" path.
    code, parsed, out, err = run_stop_hook(tmp_path, json.dumps({"transcript_path": ""}))

    assert code == 0, f"hook must exit 0 when allowing; stderr={err!r}"
    # Allow path emits no decision (empty stdout, or at least no block).
    assert out == "" or (parsed is not None and parsed.get("decision") != "block")
    # And concretely: there is no block decision.
    if parsed is not None:
        assert parsed.get("decision") != "block"


def test_malformed_stdin_is_fail_safe(tmp_path):
    """Malformed/empty stdin does not crash; with no active loop the hook allows exit."""
    # Garbage on stdin: the JSON parse error is swallowed (treated as {}), then
    # the decision falls through to the absent orchestrator-loop state file ->
    # allow. A Stop hook must never trap the user on a bad/empty payload.
    code, parsed, out, err = run_stop_hook(tmp_path, "this is not json {{{")

    assert code == 0, f"malformed stdin must not crash the hook; stderr={err!r}"
    if parsed is not None:
        assert parsed.get("decision") != "block"

    # Same fail-safe for a completely EMPTY stdin payload.
    code_empty, parsed_empty, _out2, err2 = run_stop_hook(tmp_path, "")
    assert code_empty == 0, f"empty stdin must not crash; stderr={err2!r}"
    if parsed_empty is not None:
        assert parsed_empty.get("decision") != "block"
