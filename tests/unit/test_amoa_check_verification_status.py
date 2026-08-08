#!/usr/bin/env python3
"""Real-subprocess tests for amoa_check_verification_status.py.

PreToolUse BLOCKING hook, matcher `^(Task|Agent)$`. Fires on every subagent
spawn -- the tool is named `Agent` on current Claude Code and `Task` on older
builds, and the matcher is anchored so it does NOT also fire on `ListAgents`,
`TaskCreate`, `TaskOutput`, or `TaskStop`. It reads a JSON payload on stdin
(only to validate it -- the decision is driven entirely by the orchestration
state file `.claude/orchestrator-exec-phase.local.md` resolved relative to the
process CWD) and emits:

  * exit 0 + {"status": "ok", ...}      -> allow the spawn to proceed
  * exit 2 + {"decision": "block", ...} -> deny the spawn (verification pending)

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


# A valid subagent-spawn payload (the hook validates but ignores it for the
# decision). `Agent` is the tool name on current Claude Code; `Task` is the name
# older builds used, and the anchored matcher accepts both.
SUBAGENT_STDIN = json.dumps(
    {"tool_name": "Agent", "tool_input": {"subagent_type": "general-purpose"}}
)
LEGACY_TASK_STDIN = json.dumps(
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
    code, parsed, _out, _err = run_hook(tmp_path, SUBAGENT_STDIN)
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
    code, parsed, _out, _err = run_hook(tmp_path, SUBAGENT_STDIN)
    assert code == 0
    assert parsed is not None
    assert parsed["status"] == "ok"
    assert "decision" not in parsed


def test_passes_through_when_not_in_orchestration(tmp_path):
    """Exit 0 (pass-through) when a Task payload arrives but phase is not orchestration."""
    # State file exists but phase != orchestration -> the hook never blocks Task work.
    _write_state(tmp_path, "---\nphase: plan\n---\nbody\n")
    code, parsed, _out, _err = run_hook(tmp_path, SUBAGENT_STDIN)
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
    code, parsed, _out, _err = run_hook(tmp_path, SUBAGENT_STDIN)
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
    code_block, parsed_block, _o, _e = run_hook(tmp_path, SUBAGENT_STDIN)
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
    code_allow, parsed_allow, _o2, _e2 = run_hook(tmp_path, SUBAGENT_STDIN)
    assert code_allow == 0
    assert parsed_allow is not None  # allow path MUST emit parseable JSON
    assert parsed_allow["status"] == "ok"


def test_decision_is_payload_agnostic(tmp_path):
    """Identical verdict for tool_name Agent and legacy Task -- the payload never steers it."""
    # WHY this test exists: the matcher was widened from "Task" to "^(Task|Agent)$"
    # because current Claude Code names the subagent tool `Agent`, so the old
    # matcher had silently stopped firing. Widening it is only safe because the
    # hook derives its verdict entirely from the state file and ignores the
    # payload -- if anyone later makes the decision depend on the payload shape,
    # the two builds would diverge and this test is what catches it.
    _write_state(
        tmp_path,
        "---\n"
        "phase: orchestration\n"
        "active_assignments:\n"
        "  - agent: agent-z\n"
        "    module: mod-z\n"
        "    instruction_verification:\n"
        "      status: pending\n"
        "---\nbody\n",
    )
    agent_code, agent_parsed, _o, _e = run_hook(tmp_path, SUBAGENT_STDIN)
    task_code, task_parsed, _o2, _e2 = run_hook(tmp_path, LEGACY_TASK_STDIN)

    assert agent_code == task_code == 2
    assert agent_parsed is not None and task_parsed is not None
    assert agent_parsed["decision"] == task_parsed["decision"] == "block"
