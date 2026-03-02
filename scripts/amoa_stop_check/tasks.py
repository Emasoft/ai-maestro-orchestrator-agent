"""
tasks.py - Task source checking functions for orchestrator stop hook.

This module provides functions to check various task sources:
- Claude Code native Tasks (via transcript/TODO list)
- GitHub Projects for pending items
- Markdown task files for pending items

Each function returns a tuple of (count, list_of_items) or just count,
allowing the caller to aggregate pending tasks across all sources.
"""
# mypy: disable-error-code="import-not-found"

import json
import os
import re
from pathlib import Path
from typing import Any

from .utils import debug, error, warn, retry_command

# Retry configuration constant (must match main script)
MAX_RETRIES = 3


def check_claude_tasks(transcript_path: str) -> tuple[int, list[str]]:
    """Check Claude Code native Tasks via transcript.

    Claude Code's native TaskCreate/TaskUpdate/TaskList tools persist tasks
    across context compacting. This function parses the transcript JSON to
    find pending and in-progress tasks.

    Args:
        transcript_path: Path to transcript JSON file (can be empty to skip)

    Returns:
        Tuple of (pending_count, sample_tasks) where:
        - pending_count: Number of pending + in-progress tasks
        - sample_tasks: List of up to 2 sample task subjects prefixed with [Task]
    """
    # Skip if no transcript path or file doesn't exist
    if not transcript_path or not Path(transcript_path).exists():
        debug("Claude Tasks check skipped (no transcript)")
        return (0, [])

    debug("Checking Claude Code native Tasks")

    try:
        content = Path(transcript_path).read_text(encoding="utf-8")

        # Find all todos arrays in the transcript using balanced bracket matching
        # The simple regex r'"todos":\s*(\[[^\]]*\])' fails when task subjects contain ]
        todos_arrays: list[list[dict[str, Any]]] = []
        search_start = 0

        while True:
            # Find next "todos": in content
            todos_pos = content.find('"todos":', search_start)
            if todos_pos == -1:
                break

            # Find the opening [ after "todos":
            bracket_start = content.find("[", todos_pos)
            if bracket_start == -1:
                break

            # Parse the array using balanced bracket counting (handles nested ] in strings)
            bracket_count = 0
            in_string = False
            escape_next = False
            end_pos = bracket_start

            for i, char in enumerate(content[bracket_start:], start=bracket_start):
                if escape_next:
                    escape_next = False
                    continue
                if char == "\\" and in_string:
                    escape_next = True
                    continue
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                if not in_string:
                    if char == "[":
                        bracket_count += 1
                    elif char == "]":
                        bracket_count -= 1
                        if bracket_count == 0:
                            end_pos = i + 1
                            break

            if bracket_count == 0 and end_pos > bracket_start:
                array_str = content[bracket_start:end_pos]
                try:
                    parsed = json.loads(array_str)
                    if isinstance(parsed, list):
                        todos_arrays.append(parsed)
                except json.JSONDecodeError:
                    pass  # Skip malformed arrays

            search_start = end_pos if end_pos > bracket_start else todos_pos + 1

        if not todos_arrays:
            debug("Claude Tasks pending: 0 (no todos found)")
            return (0, [])

        # Use the last todos array (most recent state)
        todos = todos_arrays[-1]

        # Filter for pending and in-progress tasks
        pending_tasks = [
            t
            for t in todos
            if isinstance(t, dict) and t.get("status") in ("pending", "in-progress", "in_progress")
        ]

        count = len(pending_tasks)
        if count > 0:
            # Extract sample task subjects (max 2)
            samples = []
            for task in pending_tasks[:2]:
                subject = task.get("subject", "Unknown task")
                status = task.get("status", "pending")
                samples.append(f"[Task:{status}] {subject}")

            debug(f"Claude Tasks pending: {count}")
            return (count, samples)

        debug("Claude Tasks pending: 0")
        return (0, [])
    except OSError:
        debug("Failed to read transcript for Claude Tasks")
        return (0, [])


def check_github_projects(script_dir: Path, project_id: str) -> tuple[int, list[str]]:
    """Check GitHub Projects for pending items.

    This function calls the check-github-projects.sh helper script to
    query GitHub Projects API for open/pending items. Requires gh CLI
    to be installed and authenticated.

    Args:
        script_dir: Path to scripts directory containing helper scripts
        project_id: GitHub project ID (optional, can be empty or "null")

    Returns:
        Tuple of (pending_count, sample_tasks) where:
        - pending_count: Number of pending items (-1 if script failed)
        - sample_tasks: List of up to 2 sample items prefixed with [GitHub]
    """
    script_path = script_dir / "check-github-projects.sh"

    # Skip if script not found or not executable
    if not script_path.exists() or not os.access(script_path, os.X_OK):
        debug("GitHub check skipped (script not found or not executable)")
        return (0, [])

    debug("Checking GitHub Projects")

    # Build command with optional project ID
    command = [str(script_path)]
    if project_id and project_id != "null":
        command.extend(["--project", project_id])

    # Execute the helper script with retries
    result = retry_command("GitHub check", command)

    if result is None:
        error(f"GitHub check script failed after {MAX_RETRIES} attempts")
        return (-1, [])

    # Validate JSON output from the script
    try:
        data = json.loads(result)
        available = data.get("available", False)
        count = int(data.get("pending_count", 0))
        gh_error = data.get("error", "")
        tasks = data.get("tasks", [])[:2]  # Max 2 samples for brevity

        if available and count > 0:
            debug(f"GitHub pending: {count}")
            return (count, [f"[GitHub] {task}" for task in tasks])
        elif gh_error:
            # GitHub check returned error (gh not installed, not authenticated, etc.)
            # This is expected in some environments - don't count as script failure
            debug(f"GitHub check unavailable: {gh_error}")

        debug(f"GitHub pending: {count}")
        return (0, [])
    except (json.JSONDecodeError, ValueError):
        error("GitHub script returned invalid JSON")
        return (-1, [])


def check_task_file(task_file: str) -> tuple[int, list[str]]:
    """Check markdown task file for pending items.

    Scans a markdown file for task list items using standard checkbox syntax:
    - [ ] Pending task (unchecked)
    - [~] In-progress task (tilde marker)

    Both are counted as pending/incomplete tasks.

    Args:
        task_file: Path to the markdown task file (can be empty or "null" to skip)

    Returns:
        Tuple of (pending_count, sample_tasks) where:
        - pending_count: Number of pending + in-progress tasks
        - sample_tasks: List of up to 2 sample task descriptions prefixed with [File]
    """
    # Skip if no task file configured
    if not task_file or task_file == "null":
        return (0, [])

    task_path = Path(task_file)

    # Validate file exists
    if not task_path.exists():
        debug(f"Task file not found: {task_file}")
        return (0, [])

    # Validate file is readable
    if not task_path.is_file() or not os.access(task_path, os.R_OK):
        warn(f"Task file exists but is not readable: {task_file}")
        return (0, [])

    debug(f"Checking task file: {task_file}")

    try:
        content = task_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Regex patterns for unchecked and in-progress tasks
        pending_pattern = re.compile(r"^\s*-\s*\[\s\]")  # - [ ] style
        in_progress_pattern = re.compile(r"^\s*-\s*\[~\]")  # - [~] style

        # Find matching lines
        pending_lines = [line for line in lines if pending_pattern.match(line)]
        in_progress_lines = [line for line in lines if in_progress_pattern.match(line)]

        count = len(pending_lines) + len(in_progress_lines)

        if count > 0:
            # Extract sample tasks (max 2) with checkbox prefix removed
            samples = []
            for line in (pending_lines + in_progress_lines)[:2]:
                task_text = re.sub(r"^\s*-\s*\[.\]\s*", "", line)
                if task_text:
                    samples.append(f"[File] {task_text}")

            debug(f"Task file pending: {count}")
            return (count, samples)

        debug(f"Task file pending: {count}")
        return (0, [])
    except OSError:
        warn(f"Failed to read task file: {task_file}")
        return (0, [])


def check_todo_list(transcript_path: str) -> int:
    """Check Claude's internal TODO list via transcript.

    Parses the transcript JSON file to find the last todos array and
    counts items with status "pending" or "in-progress".

    Args:
        transcript_path: Path to transcript JSON file (can be empty to skip)

    Returns:
        Number of pending + in-progress TODO items (0 if not found or error)
    """
    # Skip if no transcript path or file doesn't exist
    if not transcript_path or not Path(transcript_path).exists():
        debug("No transcript path or file not found")
        return 0

    debug("Checking Claude TODO list in transcript")

    try:
        content = Path(transcript_path).read_text(encoding="utf-8")

        # Find all todos arrays in the transcript (there may be multiple)
        todos_match = re.findall(r'"todos":\s*\[[^\]]*\]', content)
        if not todos_match:
            debug("TODO list pending: 0")
            return 0

        # Use the last todos array (most recent state)
        last_todos = todos_match[-1]

        # Count pending and in-progress items by status field
        pending_count = len(re.findall(r'"status":\s*"pending"', last_todos))
        in_progress_count = len(re.findall(r'"status":\s*"in.progress"', last_todos))

        count = pending_count + in_progress_count
        debug(f"TODO list pending: {count}")
        return count
    except OSError:
        debug("Failed to read transcript")
        return 0
