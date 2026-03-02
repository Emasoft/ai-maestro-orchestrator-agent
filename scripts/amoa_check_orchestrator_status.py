#!/usr/bin/env python3
"""
eoa_check_orchestrator_status.py - Check orchestrator loop status and pending tasks.

Displays the current state of the orchestrator loop including:
- Whether a loop is active
- Current iteration count
- Pending tasks from each source (Claude Tasks, GitHub, task file, TODO)
- Configuration settings

NO external dependencies - Python 3.8+ stdlib only.

Usage:
    python3 eoa_check_orchestrator_status.py
    python3 eoa_check_orchestrator_status.py --verbose

Exit codes:
    0 - Success (status displayed)
    1 - Error
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def parse_yaml_frontmatter(content: str) -> dict[str, Any]:
    """Parse YAML frontmatter from markdown content.

    Args:
        content: Markdown content with YAML frontmatter

    Returns:
        Dictionary of frontmatter fields
    """
    data: dict[str, Any] = {}
    if not content.startswith("---"):
        return data

    lines = content.split("\n")
    in_frontmatter = False
    frontmatter_lines: list[str] = []

    for line in lines:
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter:
            frontmatter_lines.append(line)

    # Simple YAML parsing for key: value pairs
    for line in frontmatter_lines:
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            # Convert types
            if value.lower() == "true":
                data[key] = True
            elif value.lower() == "false":
                data[key] = False
            elif value.lower() == "null":
                data[key] = None
            elif value.isdigit():
                data[key] = int(value)
            else:
                data[key] = value

    return data


def check_claude_tasks() -> tuple[int, list[str]]:
    """Check Claude Code native Tasks for pending items.

    Returns:
        Tuple of (pending_count, list of task summaries)
    """
    # Claude Tasks are checked via the TaskList tool
    # This script cannot directly access them, so we return placeholder
    return 0, ["(Use TaskList to check Claude Tasks)"]


def check_github_projects(project_id: str | None) -> tuple[int, list[str]]:
    """Check GitHub Projects for open items.

    Args:
        project_id: GitHub Project ID (optional)

    Returns:
        Tuple of (pending_count, list of item summaries)
    """
    if not project_id:
        return 0, []

    try:
        # Use gh CLI to check project items
        result = subprocess.run(
            [
                "gh",
                "project",
                "item-list",
                project_id,
                "--format",
                "json",
                "--limit",
                "50",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            items = data.get("items", [])
            open_items = [
                i
                for i in items
                if i.get("status", "").lower() not in ("done", "closed")
            ]
            summaries = [
                f"  - {i.get('title', 'Untitled')[:60]}" for i in open_items[:5]
            ]
            return len(open_items), summaries
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass

    return 0, ["(Could not check GitHub Projects)"]


def check_task_file(task_file: str | None) -> tuple[int, list[str]]:
    """Check markdown task file for unchecked items.

    Args:
        task_file: Path to task file

    Returns:
        Tuple of (pending_count, list of task summaries)
    """
    if not task_file or task_file == "null":
        return 0, []

    path = Path(task_file)
    if not path.exists():
        return 0, [f"(Task file not found: {task_file})"]

    try:
        content = path.read_text(encoding="utf-8")
        lines = content.split("\n")
        unchecked = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("- [ ]"):
                task_text = stripped[5:].strip()[:60]
                unchecked.append(f"  - {task_text}")

        return len(unchecked), unchecked[:5]
    except OSError:
        return 0, [f"(Could not read task file: {task_file})"]


def main() -> int:
    """Main entry point for orchestrator status check.

    Returns:
        Exit code: 0 for success, 1 for error
    """
    parser = argparse.ArgumentParser(
        description="Check orchestrator loop status and pending tasks"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed debug information"
    )
    args = parser.parse_args()

    state_file = Path(".claude/orchestrator-loop.local.md")

    print("=" * 60)
    print("ORCHESTRATOR LOOP STATUS")
    print("=" * 60)
    print()

    # Check if loop is active
    if not state_file.exists():
        print("Status: INACTIVE")
        print()
        print("No orchestrator loop is currently running.")
        print()
        print("To start a loop, use: /orchestrator-loop")
        print("=" * 60)
        return 0

    # Read state file
    try:
        content = state_file.read_text(encoding="utf-8")
        state = parse_yaml_frontmatter(content)
    except OSError as e:
        print(f"Error reading state file: {e}", file=sys.stderr)
        return 1

    print("Status: ACTIVE")
    print()

    # Display configuration
    print("Configuration:")
    iteration = state.get("iteration", "?")
    max_iter = state.get("max_iterations", 100)
    print(f"  Iteration:           {iteration} / {max_iter}")
    print(f"  Started at:          {state.get('started_at', 'unknown')}")

    promise = state.get("completion_promise")
    if promise and promise != "null":
        print(f"  Completion promise:  {promise}")

    task_file = state.get("task_file")
    if task_file and task_file != "null":
        print(f"  Task file:           {task_file}")

    print(f"  Check Tasks:         {state.get('check_tasks', True)}")
    print(f"  Check GitHub:        {state.get('check_github', True)}")

    github_project = state.get("github_project_id")
    if github_project:
        print(f"  GitHub Project:      {github_project}")

    # Verification mode
    if state.get("verification_mode"):
        remaining = state.get("verification_remaining", 0)
        print(f"  Verification mode:   ON ({remaining} loops remaining)")

    print()

    # Check task sources
    print("Pending Tasks:")
    total_pending = 0

    # Claude Tasks
    if state.get("check_tasks", True):
        count, summaries = check_claude_tasks()
        print(f"  Claude Tasks:        {count} pending")
        total_pending += count

    # GitHub Projects
    if state.get("check_github", True):
        count, summaries = check_github_projects(github_project)
        print(f"  GitHub Projects:     {count} open items")
        if summaries and args.verbose:
            for s in summaries:
                print(s)
        total_pending += count

    # Task file
    if task_file and task_file != "null":
        count, summaries = check_task_file(task_file)
        print(f"  Task file:           {count} unchecked")
        if summaries and args.verbose:
            for s in summaries:
                print(s)
        total_pending += count

    print()
    print(f"Total pending: {total_pending}")
    print()

    # Show body content (the prompt)
    if args.verbose:
        # Extract body after frontmatter
        parts = content.split("---", 2)
        if len(parts) >= 3:
            body = parts[2].strip()
            if body:
                print("Initial prompt:")
                print(f"  {body[:200]}...")
                print()

    print(f"State file: {state_file}")
    print(f"To cancel:  rm {state_file}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
