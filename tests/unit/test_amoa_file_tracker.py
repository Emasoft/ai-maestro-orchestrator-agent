#!/usr/bin/env python3
"""Real-subprocess tests for amoa_file_tracker.py.

PostToolUse hook (matcher Edit|MultiEdit|Write). It reads the tool payload on
stdin and, for file-modifying tools only, appends to a JSON tracking log at
`$CLAUDE_PROJECT_DIR/.claude/orchestrator/modified_files.json` (falling back to
CWD when CLAUDE_PROJECT_DIR is unset). It always exits 0; non-file tools and
malformed input are no-ops.

No mocks: the actual script is invoked as a subprocess with crafted stdin and a
real temp project dir under tmp_path (passed via CLAUDE_PROJECT_DIR).
"""

import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "amoa_file_tracker.py"


def run_hook(project_dir: Path, stdin_text: str):
    """Invoke the tracker as a real subprocess with CLAUDE_PROJECT_DIR set; return (exit_code, raw_stderr)."""
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        input=stdin_text,
        capture_output=True,
        text=True,
        cwd=str(project_dir),
        env=env,
        timeout=60,
    )
    return result.returncode, result.stderr


def _tracking_file(project_dir: Path) -> Path:
    return project_dir / ".claude" / "orchestrator" / "modified_files.json"


def test_records_a_file_edit(tmp_path):
    """A Write payload is recorded in modified_files.json with the path, count and tool."""
    payload = json.dumps(
        {"tool_name": "Write", "tool_input": {"file_path": "/proj/src/app.py"}}
    )
    code, _err = run_hook(tmp_path, payload)
    assert code == 0
    tf = _tracking_file(tmp_path)
    assert tf.exists()
    data = json.loads(tf.read_text(encoding="utf-8"))
    assert "/proj/src/app.py" in data["files"]
    entry = data["files"]["/proj/src/app.py"]
    assert entry["modification_count"] == 1
    assert entry["tools_used"] == ["Write"]


def test_ignores_non_file_tools(tmp_path):
    """A non-file tool (Bash) is a no-op: exit 0 and no tracking file is created."""
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls -la"}})
    code, _err = run_hook(tmp_path, payload)
    assert code == 0
    assert not _tracking_file(tmp_path).exists()


def test_malformed_stdin(tmp_path):
    """Malformed JSON on stdin is a no-op: exit 0 and no tracking file is created."""
    code, _err = run_hook(tmp_path, "{ this is not valid json")
    assert code == 0
    assert not _tracking_file(tmp_path).exists()


def test_exit_contract_increments_on_repeat_edit(tmp_path):
    """Exit contract is 0 on success, and a second edit of the same file bumps modification_count to 2."""
    payload = json.dumps(
        {"tool_name": "Edit", "tool_input": {"file_path": "/proj/src/mod.py"}}
    )
    code1, _e1 = run_hook(tmp_path, payload)
    code2, _e2 = run_hook(tmp_path, payload)
    assert code1 == 0
    assert code2 == 0
    data = json.loads(_tracking_file(tmp_path).read_text(encoding="utf-8"))
    assert data["files"]["/proj/src/mod.py"]["modification_count"] == 2
    assert data["files"]["/proj/src/mod.py"]["tools_used"] == ["Edit"]
