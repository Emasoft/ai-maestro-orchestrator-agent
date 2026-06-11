#!/usr/bin/env python3
"""Real-subprocess tests for amoa_check_polling_due.py.

UserPromptSubmit reminder hook. It ALWAYS exits 0 (it is a reminder, never a
blocker) and emits {"status": "ok", "overdue_count": N, "warning_count": M,
...}. When any actively-worked assignment is past its poll-due time (or has no
poll data at all) it additionally attaches a "systemMessage" reminder.

The decision is driven by the orchestration state file
`.claude/orchestrator-exec-phase.local.md` relative to CWD.

No mocks: the actual script is invoked as a subprocess with crafted stdin and
a real temp state file under tmp_path.
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "amoa_check_polling_due.py"
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


PROMPT_STDIN = json.dumps({"prompt": "do the next thing"})


def test_reminder_when_overdue(tmp_path):
    """Exit 0 with overdue_count>=1 and a systemMessage when an active assignment is past poll-due."""
    # next_poll_due 30 minutes in the past -> overdue. Uses real datetime math
    # in the script (this path crashed before the aware/naive-UTC fix).
    past_last = (datetime.now(timezone.utc) - timedelta(minutes=45)).isoformat()
    past_due = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
    _write_state(
        tmp_path,
        "---\n"
        "phase: orchestration\n"
        "active_assignments:\n"
        "  - agent: agent-a\n"
        "    module: mod-a\n"
        "    status: working\n"
        "    progress_polling:\n"
        f'      last_poll: "{past_last}"\n'
        f'      next_poll_due: "{past_due}"\n'
        "      poll_count: 1\n"
        "---\nbody\n",
    )
    code, parsed, _out, _err = run_hook(tmp_path, PROMPT_STDIN)
    assert code == 0
    assert parsed is not None
    assert parsed["overdue_count"] >= 1
    assert "systemMessage" in parsed
    assert "OVERDUE" in parsed["systemMessage"]


def test_silent_when_not_due(tmp_path):
    """Exit 0 with zero overdue/warning and NO systemMessage when the next poll is comfortably in the future."""
    # next_poll_due 60 minutes ahead -> beyond the 10-minute warning window -> silent.
    future_last = datetime.now(timezone.utc).isoformat()
    future_due = (datetime.now(timezone.utc) + timedelta(minutes=60)).isoformat()
    _write_state(
        tmp_path,
        "---\n"
        "phase: orchestration\n"
        "active_assignments:\n"
        "  - agent: agent-a\n"
        "    module: mod-a\n"
        "    status: working\n"
        "    progress_polling:\n"
        f'      last_poll: "{future_last}"\n'
        f'      next_poll_due: "{future_due}"\n'
        "      poll_count: 3\n"
        "---\nbody\n",
    )
    code, parsed, _out, _err = run_hook(tmp_path, PROMPT_STDIN)
    assert code == 0
    assert parsed is not None
    assert parsed["overdue_count"] == 0
    assert parsed["warning_count"] == 0
    assert "systemMessage" not in parsed


def test_malformed_stdin(tmp_path):
    """Malformed stdin does not crash the reminder; exit 0 with a well-formed status object."""
    # Garbage stdin + no state file -> swallowed parse error, no assignments -> silent ok.
    code, parsed, _out, _err = run_hook(tmp_path, "not valid json <<<")
    assert code == 0
    assert parsed is not None
    assert parsed["status"] == "ok"
    assert parsed["overdue_count"] == 0


def test_missing_state(tmp_path):
    """Exit 0 with zero counts and no reminder when no orchestrator-exec-phase state file exists."""
    code, parsed, _out, _err = run_hook(tmp_path, PROMPT_STDIN)
    assert code == 0
    assert parsed is not None
    assert parsed["status"] == "ok"
    assert parsed["overdue_count"] == 0
    assert parsed["warning_count"] == 0
    assert "systemMessage" not in parsed
