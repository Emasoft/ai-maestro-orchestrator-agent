#!/usr/bin/env python3
"""Real-subprocess tests for amoa_check_verification_status.py.

PreToolUse matcher:Task BLOCKING hook. Fires on every Task call. It reads a
JSON payload on stdin (only to validate it -- the decision is driven entirely
by the orchestration state file `.claude/orchestrator-exec-phase.local.md`
resolved relative to the process CWD) and emits:

  * exit 0 + {"status": "ok", ...}      -> allow the Task to proceed
  * exit 2 + {"decision": "block", ...} -> deny the Task (verification pending)

No mocks: the actual script is invoked as a subprocess with crafted stdin and
a real temp state file under tmp_path.
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "amoa_check_verification_status.py"
)


def run_hook(cwd: Path, stdin_text: str = ""):
    """Invoke the hook as a real subprocess; return (exit_code, parsed_json_or_None, raw_stdout, raw_stderr)."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        input=stdin_text,
        capture_output=True,
        text=True,
        cwd=str(cwd),
        timeout=60,
    )
    stdout = result.stdout.strip()
    try:
        parsed = json.loads(stdout) if stdout else None
    except json.JSONDecodeError:
        parsed = None
    return result.returncode, parsed, stdout, result.stderr


def _write_state(cwd: Path, body: str) -> Path:
    """Write the orchestrator-exec-phase state file under cwd/.claude and return its path."""
    state_dir = cwd / ".claude"
    state_dir.mkdir(parents=True, exist_ok=True)
    state_file = state_dir / "orchestrator-exec-phase.local.md"
    state_file.write_text(body, encoding="utf-8")
    return state_file


# A valid Task-call payload (the hook validates but ignores it for the decision).
TASK_STDIN = json.dumps(
    {"tool_name": "Task", "tool_input": {"subagent_type": "general-purpose"}}
)


def test_blocks_when_verification_incomplete(tmp_path):
    """Exit 2 + decision=block when an active assignment's verification is pending/unauthorized."""
    _write_state(
        tmp_path,
        "---\n"
        "phase: orchestration\n"
        "active_assignments:\n"
        "  - agent: agent-x\n"
        "    module: mod-x\n"
        "    instruction_verification:\n"
        "      status: pending\n"
        "      authorized_at: null\n"
        "---\nbody\n",
    )
    code, parsed, _out, _err = run_hook(tmp_path, TASK_STDIN)
    assert code == 2
    assert parsed is not None
    assert parsed["decision"] == "block"
    assert parsed["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "agent-x" in parsed["reason"]


def test_allows_when_verification_complete(tmp_path):
    """Exit 0 + status=ok when every active assignment is verified and authorized."""
    _write_state(
        tmp_path,
        "---\n"
        "phase: orchestration\n"
        "active_assignments:\n"
        "  - agent: agent-x\n"
        "    module: mod-x\n"
        "    instruction_verification:\n"
        "      status: verified\n"
        '      authorized_at: "2026-01-01T00:00:00Z"\n'
        "---\nbody\n",
    )
    code, parsed, _out, _err = run_hook(tmp_path, TASK_STDIN)
    assert code == 0
    assert parsed is not None
    assert parsed["status"] == "ok"
    assert "decision" not in parsed


def test_passes_through_when_not_in_orchestration(tmp_path):
    """Exit 0 (pass-through) when a Task payload arrives but phase is not orchestration."""
    # State file exists but phase != orchestration -> the hook never blocks Task work.
    _write_state(tmp_path, "---\nphase: plan\n---\nbody\n")
    code, parsed, _out, _err = run_hook(tmp_path, TASK_STDIN)
    assert code == 0
    assert parsed is not None
    assert parsed["status"] == "ok"


def test_malformed_stdin_is_fail_safe(tmp_path):
    """Malformed stdin does not crash; the decision still follows the (absent) state file -> allow."""
    # No state file + garbage stdin: the stdin parse error is swallowed and the
    # decision falls through to "Not in orchestration phase" -> allow, exit 0.
    code, parsed, _out, _err = run_hook(tmp_path, "this is not json {{{")
    assert code == 0
    assert parsed is not None
    assert parsed["status"] == "ok"


def test_missing_state_file_allows(tmp_path):
    """Exit 0 + status=ok when no orchestrator-exec-phase state file exists at all."""
    # tmp_path has no .claude/orchestrator-exec-phase.local.md.
    code, parsed, _out, _err = run_hook(tmp_path, TASK_STDIN)
    assert code == 0
    assert parsed is not None
    assert parsed["status"] == "ok"
    assert "orchestration phase" in parsed["message"].lower()


def test_exit_code_contract_block_is_2_allow_is_0(tmp_path):
    """The exit-code contract: blocking verification -> 2, complete verification -> 0 (same dir, two states)."""
    state = _write_state(
        tmp_path,
        "---\n"
        "phase: orchestration\n"
        "active_assignments:\n"
        "  - agent: agent-y\n"
        "    module: mod-y\n"
        "    instruction_verification:\n"
        "      status: pending\n"
        "      authorized_at: null\n"
        "---\nbody\n",
    )
    code_block, parsed_block, _o, _e = run_hook(tmp_path, TASK_STDIN)
    assert code_block == 2
    assert parsed_block is not None  # block path MUST emit parseable JSON
    assert parsed_block["decision"] == "block"

    # Flip the same assignment to verified -> the very same hook now allows.
    state.write_text(
        "---\n"
        "phase: orchestration\n"
        "active_assignments:\n"
        "  - agent: agent-y\n"
        "    module: mod-y\n"
        "    instruction_verification:\n"
        "      status: verified\n"
        '      authorized_at: "2026-01-01T00:00:00Z"\n'
        "---\nbody\n",
        encoding="utf-8",
    )
    code_allow, parsed_allow, _o2, _e2 = run_hook(tmp_path, TASK_STDIN)
    assert code_allow == 0
    assert parsed_allow is not None  # allow path MUST emit parseable JSON
    assert parsed_allow["status"] == "ok"
