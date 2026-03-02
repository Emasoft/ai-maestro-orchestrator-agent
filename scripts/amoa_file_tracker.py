#!/usr/bin/env python3
"""
File Tracker - Track file modifications for orchestration context.

This PostToolUse hook script tracks files modified via Edit, MultiEdit, or Write
operations and logs them for orchestration awareness.

Usage:
    Called automatically by Claude Code as a PostToolUse hook.
    Receives tool output via stdin as JSON.

Exit codes:
    0 - Success (file tracked or not applicable)
    2 - Blocking error (shown to Claude)
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast


def get_project_root() -> Path:
    """Get the project root directory."""
    # Try CLAUDE_PROJECT_DIR first
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_dir:
        return Path(project_dir)
    # Fall back to current working directory
    return Path.cwd()


def get_tracking_file() -> Path:
    """Get the path to the file tracking log."""
    project_root = get_project_root()
    tracking_dir = project_root / ".claude" / "orchestrator"
    tracking_dir.mkdir(parents=True, exist_ok=True)
    return tracking_dir / "modified_files.json"


def load_tracking_data() -> dict[str, Any]:
    """Load existing tracking data."""
    tracking_file = get_tracking_file()
    if tracking_file.exists():
        try:
            with open(tracking_file, encoding="utf-8") as f:
                return cast(dict[str, Any], json.load(f))
        except (json.JSONDecodeError, OSError):
            pass
    return {"session_start": datetime.now(timezone.utc).isoformat(), "files": {}}


def save_tracking_data(data: dict[str, Any]) -> None:
    """Save tracking data atomically."""
    tracking_file = get_tracking_file()
    temp_file = tracking_file.with_suffix(".tmp")
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        temp_file.replace(tracking_file)
    except OSError as e:
        # Non-fatal - just log to stderr
        print(f"Warning: Could not save tracking data: {e}", file=sys.stderr)


def track_file(file_path: str, tool_name: str) -> None:
    """Track a file modification."""
    data = load_tracking_data()
    now = datetime.now(timezone.utc).isoformat()

    if file_path not in data["files"]:
        data["files"][file_path] = {
            "first_modified": now,
            "last_modified": now,
            "modification_count": 1,
            "tools_used": [tool_name],
        }
    else:
        entry = data["files"][file_path]
        entry["last_modified"] = now
        entry["modification_count"] += 1
        if tool_name not in entry["tools_used"]:
            entry["tools_used"].append(tool_name)

    save_tracking_data(data)


def main() -> int:
    """Main entry point."""
    # Read hook input from stdin
    try:
        stdin_data = sys.stdin.read()
        if not stdin_data.strip():
            # No input - nothing to track
            return 0
        hook_input = json.loads(stdin_data)
    except json.JSONDecodeError:
        # Invalid JSON - not a fatal error for tracking
        return 0

    # Extract tool information
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    # Only track file modification tools
    if tool_name not in ("Edit", "MultiEdit", "Write"):
        return 0

    # Extract file path based on tool type
    file_path = None
    if tool_name == "Write":
        file_path = tool_input.get("file_path")
    elif tool_name == "Edit":
        file_path = tool_input.get("file_path")
    elif tool_name == "MultiEdit":
        # MultiEdit may have multiple files
        edits = tool_input.get("edits", [])
        for edit in edits:
            edit_path = edit.get("file_path")
            if edit_path:
                track_file(edit_path, tool_name)
        return 0

    # Track single file
    if file_path:
        track_file(file_path, tool_name)

    return 0


if __name__ == "__main__":
    sys.exit(main())
