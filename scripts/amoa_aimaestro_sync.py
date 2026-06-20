#!/usr/bin/env python3
"""
AMOA AI Maestro Task Sync

Syncs task state between GitHub Projects V2 kanban and AI Maestro's task API.
Uses AMP wrapper scripts — never direct API calls (Plugin Abstraction Principle).

Usage:
    python amoa_aimaestro_sync.py sync-task --issue <number> --status <status> [--agent <name>] [--priority <p>]
    python amoa_aimaestro_sync.py full-sync --team-id <id>
    python amoa_aimaestro_sync.py get-tasks --team-id <id>
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

# Column mapping: AMOA 8-column → AI Maestro status key
AMOA_TO_AIMAESTRO_STATUS = {
    "backlog": "backlog",
    "todo": "todo",
    "in-progress": "in-progress",
    "ai-review": "ai-review",
    "human-review": "human-review",
    "merge-release": "merge-release",
    "done": "done",
    "blocked": "blocked",
}

# Reverse mapping: AI Maestro → AMOA
AIMAESTRO_TO_AMOA_STATUS = {v: k for k, v in AMOA_TO_AIMAESTRO_STATUS.items()}

# Priority mapping
PRIORITY_MAP = {
    "critical": 1,
    "high": 2,
    "normal": 3,
    "low": 4,
}

GITHUB_OWNER = os.environ.get("GITHUB_OWNER", "Emasoft")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")
TEAM_ID = os.environ.get("AIMAESTRO_TEAM_ID", "")


def _find_script(name: str) -> str:
    """Find an AMP/AI Maestro wrapper script on PATH or in ~/.local/bin/."""
    found = shutil.which(name)
    if found:
        return found
    fallback = os.path.expanduser(f"~/.local/bin/{name}")
    if os.path.isfile(fallback) and os.access(fallback, os.X_OK):
        return fallback
    print(f"ERROR: {name} not found on PATH or in ~/.local/bin/", file=sys.stderr)
    sys.exit(1)


def _run_task_command(args: list[str], timeout: int = 30) -> tuple[int, str, str]:
    """Run an aimaestro-task.sh command."""
    script = _find_script("aimaestro-task.sh")
    try:
        result = subprocess.run(
            [script] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except FileNotFoundError:
        return 1, "", f"{script} not found"


def _run_gh_command(args: list[str]) -> tuple[int, str, str]:
    """Run a GitHub CLI command."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def kanban_column_to_aimaestro_status(column: str) -> str:
    """Convert AMOA kanban column to AI Maestro status key."""
    return AMOA_TO_AIMAESTRO_STATUS.get(column, column)


def aimaestro_status_to_kanban_column(status: str) -> str:
    """Convert AI Maestro status key to AMOA kanban column."""
    return AIMAESTRO_TO_AMOA_STATUS.get(status, status)


def priority_to_number(priority: str) -> int:
    """Convert priority string to numeric value."""
    return PRIORITY_MAP.get(priority.lower(), 3)


def sync_task(
    team_id: str,
    issue_number: int,
    issue_title: str,
    status: str,
    agent_id: str | None = None,
    priority: str = "normal",
    labels: list[str] | None = None,
    previous_status: str | None = None,
) -> bool:
    """Sync a single task to AI Maestro's task API.

    Creates or updates the task in AI Maestro to match the GitHub state.
    """
    task_data = {
        "subject": issue_title,
        "status": kanban_column_to_aimaestro_status(status),
        "externalRef": f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/issues/{issue_number}",
        "priority": priority_to_number(priority),
    }

    if agent_id:
        task_data["assigneeAgentId"] = agent_id
    if labels:
        task_data["labels"] = labels
    if previous_status and status == "blocked":
        task_data["previousStatus"] = kanban_column_to_aimaestro_status(previous_status)
    if status == "done":
        task_data["completedAt"] = datetime.now(timezone.utc).isoformat()

    # Use aimaestro-task.sh to upsert the task
    returncode, _, stderr = _run_task_command([
        "upsert",
        "--team", team_id,
        "--external-ref", str(task_data["externalRef"]),
        "--data", json.dumps(task_data),
    ])

    if returncode != 0:
        print(f"Failed to sync task #{issue_number} to AI Maestro: {stderr}", file=sys.stderr)
        return False

    return True


def get_aimaestro_tasks(team_id: str) -> list[dict[str, Any]]:
    """Read current AI Maestro kanban state for a team."""
    returncode, stdout, stderr = _run_task_command([
        "list",
        "--team", team_id,
        "--format", "json",
    ])

    if returncode != 0:
        print(f"Failed to get AI Maestro tasks: {stderr}", file=sys.stderr)
        return []

    try:
        data = json.loads(stdout)
        return data.get("tasks", data) if isinstance(data, dict) else data
    except json.JSONDecodeError:
        print(f"Invalid JSON from AI Maestro task API: {stdout[:200]}", file=sys.stderr)
        return []


def get_github_issues() -> list[dict[str, Any]]:
    """Get all open issues from the GitHub repo with their labels."""
    returncode, stdout, stderr = _run_gh_command([
        "issue", "list",
        "--repo", f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "--state", "all",
        "--limit", "500",
        "--json", "number,title,labels,state,assignees",
    ])

    if returncode != 0:
        print(f"Failed to list GitHub issues: {stderr}", file=sys.stderr)
        return []

    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return []


def extract_status_from_labels(labels: list[dict[str, str]]) -> str:
    """Extract AMOA kanban status from issue labels."""
    for label in labels:
        name = label.get("name", "")
        if name.startswith("status:"):
            return name.removeprefix("status:")
    return "backlog"


def extract_agent_from_labels(labels: list[dict[str, str]]) -> str | None:
    """Extract assigned agent from issue labels."""
    for label in labels:
        name = label.get("name", "")
        if name.startswith("assign:"):
            return name.removeprefix("assign:")
    return None


def extract_priority_from_labels(labels: list[dict[str, str]]) -> str:
    """Extract priority from issue labels."""
    for label in labels:
        name = label.get("name", "")
        if name.startswith("priority:"):
            return name.removeprefix("priority:")
    return "normal"


def bulk_sync(team_id: str) -> dict[str, int]:
    """Full sync: reconcile all GitHub issues with AI Maestro tasks.

    Returns counts: {"created": N, "updated": N, "orphaned": N}
    """
    github_issues = get_github_issues()
    aimaestro_tasks = get_aimaestro_tasks(team_id)

    # Index AI Maestro tasks by external ref
    am_by_ref: dict[str, dict[str, Any]] = {}
    for task in aimaestro_tasks:
        ref = task.get("externalRef", "")
        if ref:
            am_by_ref[ref] = task

    counts = {"created": 0, "updated": 0, "orphaned": 0}

    # Sync each GitHub issue to AI Maestro
    for issue in github_issues:
        issue_number = issue["number"]
        labels = issue.get("labels", [])
        label_names = [lbl.get("name", "") for lbl in labels]

        # Skip issues without task labels
        if not any(name.startswith("status:") for name in label_names):
            continue

        status = extract_status_from_labels(labels)
        agent = extract_agent_from_labels(labels)
        priority = extract_priority_from_labels(labels)
        ref = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/issues/{issue_number}"

        existed = ref in am_by_ref

        success = sync_task(
            team_id=team_id,
            issue_number=issue_number,
            issue_title=issue["title"],
            status=status,
            agent_id=agent,
            priority=priority,
            labels=label_names,
        )

        if success:
            if existed:
                counts["updated"] += 1
            else:
                counts["created"] += 1
            am_by_ref.pop(ref, None)

    # Remaining AI Maestro tasks have no GitHub counterpart
    counts["orphaned"] = len(am_by_ref)

    return counts


def notify_sync_result(team_id: str, counts: dict[str, int]) -> None:
    """Report sync results to the assistant manager via AMP."""
    amp_send = _find_script("amp-send.sh")
    message = (
        f"Full kanban sync complete for team {team_id}. "
        f"Created: {counts['created']}, Updated: {counts['updated']}, "
        f"Orphaned (AI Maestro only): {counts['orphaned']}"
    )
    try:
        subprocess.run(
            [amp_send, "amama-assistant-manager", "Kanban Sync Report", message,
             "--priority", "normal", "--type", "sync-report"],
            capture_output=True, text=True, timeout=30,
        )
    except Exception:
        pass  # Best-effort notification


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AMOA AI Maestro Task Sync",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Sync single task
    sync_parser = subparsers.add_parser("sync-task", help="Sync a single task to AI Maestro")
    sync_parser.add_argument("--issue", type=int, required=True, help="Issue number")
    sync_parser.add_argument("--title", required=True, help="Issue title")
    sync_parser.add_argument("--status", required=True, help="AMOA kanban status")
    sync_parser.add_argument("--agent", help="Assigned agent ID")
    sync_parser.add_argument("--priority", default="normal", help="Priority level")
    sync_parser.add_argument("--team-id", default=TEAM_ID, help="AI Maestro team ID")
    sync_parser.add_argument("--previous-status", help="Previous status (for blocked)")

    # Full sync
    full_sync_parser = subparsers.add_parser("full-sync", help="Full reconciliation sync")
    full_sync_parser.add_argument("--team-id", default=TEAM_ID, help="AI Maestro team ID")

    # Get tasks
    get_parser = subparsers.add_parser("get-tasks", help="Get AI Maestro tasks")
    get_parser.add_argument("--team-id", default=TEAM_ID, help="AI Maestro team ID")

    args = parser.parse_args()

    if args.command == "sync-task":
        team_id = args.team_id
        if not team_id:
            print("ERROR: --team-id or AIMAESTRO_TEAM_ID required", file=sys.stderr)
            return 1
        success = sync_task(
            team_id=team_id,
            issue_number=args.issue,
            issue_title=args.title,
            status=args.status,
            agent_id=args.agent,
            priority=args.priority,
            previous_status=args.previous_status,
        )
        return 0 if success else 1

    elif args.command == "full-sync":
        team_id = args.team_id
        if not team_id:
            print("ERROR: --team-id or AIMAESTRO_TEAM_ID required", file=sys.stderr)
            return 1
        counts = bulk_sync(team_id)
        notify_sync_result(team_id, counts)
        print(json.dumps(counts, indent=2))
        return 0

    elif args.command == "get-tasks":
        team_id = args.team_id
        if not team_id:
            print("ERROR: --team-id or AIMAESTRO_TEAM_ID required", file=sys.stderr)
            return 1
        tasks = get_aimaestro_tasks(team_id)
        print(json.dumps(tasks, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
