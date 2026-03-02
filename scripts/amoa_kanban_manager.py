#!/usr/bin/env python3
"""
EOA Kanban Manager

Manages GitHub Project kanban for task assignment and tracking.
Only EOA (Orchestrator) should use this script.

Usage:
    python eoa_kanban_manager.py create-task --title <title> --body <body> --agent <name> [--priority <p>]
    python eoa_kanban_manager.py assign-task --issue <number> --agent <name>
    python eoa_kanban_manager.py update-status --issue <number> --status <status>
    python eoa_kanban_manager.py set-dependency --issue <number> --blocked-by <issue>
    python eoa_kanban_manager.py check-ready-tasks
    python eoa_kanban_manager.py notify-agent --issue <number> --agent <name>
    python eoa_kanban_manager.py sync-from-github
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

# GitHub configuration
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_OWNER = os.environ.get("GITHUB_OWNER", "Emasoft")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")

# Project configuration
PROJECT_ID = os.environ.get("GITHUB_PROJECT_ID", "")

# Kanban columns
KANBAN_COLUMNS = {
    "backlog": "Backlog",
    "todo": "Todo",
    "in-progress": "In Progress",
    "ai-review": "AI Review",
    "human-review": "Human Review",
    "merge-release": "Merge/Release",
    "done": "Done",
    "blocked": "Blocked",
}

# Local cache for task state
CACHE_DIR = Path.home() / ".eoa" / "kanban-cache"


def get_timestamp() -> str:
    """Get current ISO8601 timestamp."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_gh_command(args: list[str]) -> tuple[int, str, str]:
    """Run a GitHub CLI command."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True,
        env={**os.environ, "GH_TOKEN": GITHUB_TOKEN},
    )
    return result.returncode, result.stdout, result.stderr


def check_gh_project_scopes() -> bool:
    """Verify gh auth has project scopes before kanban operations.

    The default gh auth login does not include 'project' and 'read:project'
    scopes. Without them, all GitHub Projects V2 operations will fail.
    Scopes must be added by a human via interactive browser:
        gh auth refresh -h github.com -s project,read:project
    """
    result = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    if "project" not in combined:
        print(
            "ERROR: gh auth is missing 'project' and 'read:project' scopes.\n"
            "A human must run: gh auth refresh -h github.com -s project,read:project\n"
            "This requires interactive browser approval and cannot be automated.",
            file=sys.stderr,
        )
        return False
    return True


def load_team_registry(repo_path: str | None = None) -> dict[str, Any]:
    """Load team registry from repository."""
    if repo_path:
        registry_path = Path(repo_path) / ".emasoft" / "team-registry.json"
    else:
        # Try current directory
        registry_path = Path(".emasoft") / "team-registry.json"

    if not registry_path.exists():
        raise FileNotFoundError(f"Team registry not found: {registry_path}")

    with open(registry_path, encoding="utf-8") as f:
        return cast(dict[str, Any], json.load(f))


def get_agent_address(registry: dict[str, Any], agent_name: str) -> str | None:
    """Get AI Maestro address for an agent from registry."""
    # Check team agents
    for agent in registry.get("agents", []):
        if agent["name"] == agent_name:
            return cast(str, agent["ai_maestro_address"])

    # Check shared agents
    for agent in registry.get("shared_agents", []):
        if agent["name"] == agent_name:
            return cast(str, agent["ai_maestro_address"])

    return None


def send_ai_maestro_message(
    to: str,
    subject: str,
    content: dict[str, Any],
    priority: str = "normal",
    from_agent: str = "eoa-orchestrator",
) -> bool:
    """Send a message via AI Maestro AMP CLI."""
    try:
        msg_type = (
            content.get("type", "notification")
            if isinstance(content, dict)
            else "notification"
        )
        msg_text = (
            content.get("message", str(content))
            if isinstance(content, dict)
            else str(content)
        )
        result = subprocess.run(
            [
                "amp-send",
                to,
                subject,
                msg_text,
                "--priority",
                priority,
                "--type",
                msg_type,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Failed to send message: {e}", file=sys.stderr)
        return False


def create_task_issue(
    title: str,
    body: str,
    assigned_agent: str,
    priority: str = "normal",
    dependencies: list[int] | None = None,
    task_requirements_doc: str | None = None,
) -> dict[str, Any] | None:
    """Create a GitHub issue for a task."""

    # Build labels
    labels = [f"assign:{assigned_agent}", f"priority:{priority}"]

    # Build body with agent identity section
    full_body = f"""{body}

---

## Task Assignment

| Field | Value |
|-------|-------|
| Assigned Agent | `{assigned_agent}` |
| Priority | {priority} |
| Assigned At | {get_timestamp()} |
| Assigned By | eoa-orchestrator |

"""

    if dependencies:
        dep_list = ", ".join([f"#{d}" for d in dependencies])
        full_body += f"\n**Dependencies**: Blocked by {dep_list}\n"

    if task_requirements_doc:
        full_body += f"""
---

## Task Requirements Document

{task_requirements_doc}
"""

    # Create issue via gh CLI
    args = [
        "issue",
        "create",
        "--repo",
        f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "--title",
        title,
        "--body",
        full_body,
        "--label",
        ",".join(labels),
    ]

    returncode, stdout, stderr = run_gh_command(args)

    if returncode != 0:
        print(f"Failed to create issue: {stderr}", file=sys.stderr)
        return None

    # Parse issue URL to get number
    # stdout is like: https://github.com/owner/repo/issues/42
    issue_url = stdout.strip()
    issue_number = int(issue_url.split("/")[-1])

    return {
        "number": issue_number,
        "url": issue_url,
        "title": title,
        "assigned_agent": assigned_agent,
        "priority": priority,
        "dependencies": dependencies or [],
        "created_at": get_timestamp(),
    }


def assign_task_to_agent(issue_number: int, agent_name: str) -> bool:
    """Assign a task (issue) to an agent by adding the label.

    Removes any existing assign:* labels first to prevent
    multiple assignment labels on reassignment.
    """
    # 1. Get current labels to find existing assign:* labels
    args = [
        "issue",
        "view",
        str(issue_number),
        "--repo",
        f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "--json",
        "labels",
    ]

    returncode, stdout, _ = run_gh_command(args)
    if returncode != 0:
        print("Failed to get issue labels", file=sys.stderr)
        return False

    # 2. Find and remove existing assign:* labels
    current_labels = json.loads(stdout).get("labels", [])
    labels_to_remove = [
        label["name"] for label in current_labels if label["name"].startswith("assign:")
    ]

    for label in labels_to_remove:
        args = [
            "issue",
            "edit",
            str(issue_number),
            "--repo",
            f"{GITHUB_OWNER}/{GITHUB_REPO}",
            "--remove-label",
            label,
        ]
        run_gh_command(args)  # Ignore errors on removal

    # 3. Add the new assign label
    args = [
        "issue",
        "edit",
        str(issue_number),
        "--repo",
        f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "--add-label",
        f"assign:{agent_name}",
    ]

    returncode, _, stderr = run_gh_command(args)

    if returncode != 0:
        print(f"Failed to assign task: {stderr}", file=sys.stderr)
        return False

    return True


def update_task_status(issue_number: int, status: str) -> bool:
    """Update task status by changing labels."""

    if status not in KANBAN_COLUMNS:
        print(
            f"Invalid status: {status}. Valid: {list(KANBAN_COLUMNS.keys())}",
            file=sys.stderr,
        )
        return False

    # Remove old status labels and add new one
    status_labels = [f"status:{s}" for s in KANBAN_COLUMNS.keys()]

    # Get current labels
    args = [
        "issue",
        "view",
        str(issue_number),
        "--repo",
        f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "--json",
        "labels",
    ]

    returncode, stdout, _ = run_gh_command(args)
    if returncode != 0:
        return False

    current_labels = json.loads(stdout).get("labels", [])
    labels_to_remove = [
        label["name"] for label in current_labels if label["name"] in status_labels
    ]

    # Remove old status labels
    for label in labels_to_remove:
        args = [
            "issue",
            "edit",
            str(issue_number),
            "--repo",
            f"{GITHUB_OWNER}/{GITHUB_REPO}",
            "--remove-label",
            label,
        ]
        run_gh_command(args)

    # Add new status label
    args = [
        "issue",
        "edit",
        str(issue_number),
        "--repo",
        f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "--add-label",
        f"status:{status}",
    ]

    returncode, _, stderr = run_gh_command(args)
    if returncode != 0:
        print(f"Failed to update status: {stderr}", file=sys.stderr)
        return False

    return True


def close_issue_safely(issue_number: int, comment: str = "Task completed.") -> bool:
    """Close an issue with a guard for Done-column auto-close.

    GitHub Projects V2 auto-closes issues when moved to the Done column.
    This function checks the issue state before attempting to close it,
    preventing redundant close attempts and misleading error logs.
    """
    # Check current state
    args = [
        "issue",
        "view",
        str(issue_number),
        "--repo",
        f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "--json",
        "state",
    ]

    returncode, stdout, _ = run_gh_command(args)
    if returncode != 0:
        print(f"Failed to check issue #{issue_number} state", file=sys.stderr)
        return False

    state = json.loads(stdout).get("state", "OPEN")

    if state == "CLOSED":
        print(
            f"INFO: Issue #{issue_number} is already closed "
            f"(likely auto-closed by Done column)"
        )
        return True

    # Close with comment
    args = [
        "issue",
        "close",
        str(issue_number),
        "--repo",
        f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "--comment",
        comment,
    ]

    returncode, _, stderr = run_gh_command(args)
    if returncode != 0:
        print(f"Failed to close issue #{issue_number}: {stderr}", file=sys.stderr)
        return False

    return True


def set_task_dependency(issue_number: int, blocked_by: list[int]) -> bool:
    """Set task dependencies by adding a comment and label."""

    # Add blocked label
    args = [
        "issue",
        "edit",
        str(issue_number),
        "--repo",
        f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "--add-label",
        "blocked",
    ]
    run_gh_command(args)

    # Add comment with dependencies
    dep_list = ", ".join([f"#{d}" for d in blocked_by])
    comment = f"**Dependencies**: This task is blocked by {dep_list}"

    args = [
        "issue",
        "comment",
        str(issue_number),
        "--repo",
        f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "--body",
        comment,
    ]

    returncode, _, stderr = run_gh_command(args)
    if returncode != 0:
        print(f"Failed to set dependency: {stderr}", file=sys.stderr)
        return False

    return True


def check_dependencies_resolved(dependencies: list[int]) -> bool:
    """Check if all dependencies are resolved (closed)."""

    for dep in dependencies:
        args = [
            "issue",
            "view",
            str(dep),
            "--repo",
            f"{GITHUB_OWNER}/{GITHUB_REPO}",
            "--json",
            "state",
        ]

        returncode, stdout, _ = run_gh_command(args)
        if returncode != 0:
            return False

        state = json.loads(stdout).get("state", "")
        if state != "CLOSED":
            return False

    return True


def get_ready_tasks(registry: dict[str, Any]) -> list[dict[str, Any]]:
    """Get tasks that are ready to be worked on (dependencies resolved)."""

    # Get all open issues with assign labels
    args = [
        "issue",
        "list",
        "--repo",
        f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "--state",
        "open",
        "--json",
        "number,title,labels,body",
        "--limit",
        "100",
    ]

    returncode, stdout, _ = run_gh_command(args)
    if returncode != 0:
        return []

    issues = json.loads(stdout)
    ready_tasks = []

    for issue in issues:
        labels = [label["name"] for label in issue.get("labels", [])]

        # Check if assigned to an agent
        assigned_agent = None
        for label in labels:
            if label.startswith("assign:"):
                assigned_agent = label.replace("assign:", "")
                break

        if not assigned_agent:
            continue

        # Check if blocked
        is_blocked = "blocked" in labels or "status:blocked" in labels

        # Check if already in progress
        in_progress = "status:in-progress" in labels or "status:ai-review" in labels

        if is_blocked or in_progress:
            continue

        # Check if in to-do
        is_todo = "status:todo" in labels or not any(
            label.startswith("status:") for label in labels
        )

        if is_todo:
            # Verify agent exists in registry
            address = get_agent_address(registry, assigned_agent)
            if address:
                ready_tasks.append(
                    {
                        "number": issue["number"],
                        "title": issue["title"],
                        "assigned_agent": assigned_agent,
                        "agent_address": address,
                    }
                )

    return ready_tasks


def notify_agent_of_task(
    registry: dict[str, Any],
    issue_number: int,
    agent_name: str,
    task_title: str,
    task_requirements_doc: str | None = None,
) -> bool:
    """Notify an agent that they have a task assigned."""

    address = get_agent_address(registry, agent_name)
    if not address:
        print(f"Agent not found in registry: {agent_name}", file=sys.stderr)
        return False

    # Get agent info from registry
    agent_info = None
    for agent in registry.get("agents", []):
        if agent["name"] == agent_name:
            agent_info = agent
            break

    team_name = registry.get("team", {}).get("name", "unknown-team")
    repo_url = registry.get("team", {}).get("project", {}).get("repository", "")

    content = {
        "type": "task-assignment",
        "message": f"You have been assigned task #{issue_number}: {task_title}",
        "task": {
            "issue_number": issue_number,
            "issue_url": f"{repo_url}/issues/{issue_number}",
            "title": task_title,
        },
        "sender_identity": {
            "name": "eoa-orchestrator",
            "role": "orchestrator",
            "plugin": "emasoft-orchestrator-agent",
            "team": team_name,
        },
        "recipient_identity": {
            "name": agent_name,
            "role": agent_info["role"] if agent_info else "unknown",
            "plugin": agent_info["plugin"] if agent_info else "unknown",
        },
        "instructions": "Please review the task and begin work. Report progress to me (orchestrator). Let me know if you need clarifications.",
    }

    if task_requirements_doc:
        content["task_requirements_document"] = task_requirements_doc

    return send_ai_maestro_message(
        to=address,
        subject=f"[TASK ASSIGNED] #{issue_number}: {task_title}",
        content=content,
        priority="high",
    )


def request_pr_review(
    registry: dict[str, Any],
    pr_number: int,
    pr_title: str,
    task_issue: int,
    submitting_agent: str,
) -> bool:
    """Request PR review from integrator."""

    # Find integrator
    integrator_address = None
    for agent in registry.get("shared_agents", []):
        if agent["role"] == "integrator":
            integrator_address = agent["ai_maestro_address"]
            break

    if not integrator_address:
        print("Integrator not found in registry", file=sys.stderr)
        return False

    team_name = registry.get("team", {}).get("name", "unknown-team")
    repo_url = registry.get("team", {}).get("project", {}).get("repository", "")

    content = {
        "type": "pr-review-request",
        "message": f"Please review PR #{pr_number}: {pr_title}",
        "pull_request": {
            "number": pr_number,
            "url": f"{repo_url}/pull/{pr_number}",
            "title": pr_title,
            "related_issue": task_issue,
        },
        "submitting_agent": submitting_agent,
        "sender_identity": {
            "name": "eoa-orchestrator",
            "role": "orchestrator",
            "plugin": "emasoft-orchestrator-agent",
            "team": team_name,
        },
        "instructions": "Review the PR for compliance with task requirements. Run tests. Merge if approved, reject with detailed feedback if not.",
    }

    return send_ai_maestro_message(
        to=integrator_address,
        subject=f"[PR REVIEW] #{pr_number}: {pr_title}",
        content=content,
        priority="high",
    )


def report_to_manager(message_type: str, message: str, details: dict[str, Any]) -> bool:
    """Report to the manager (EAMA)."""

    content = {
        "type": message_type,
        "message": message,
        "details": details,
        "sender_identity": {
            "name": "eoa-orchestrator",
            "role": "orchestrator",
            "plugin": "emasoft-orchestrator-agent",
        },
    }

    return send_ai_maestro_message(
        to="eama-assistant-manager",
        subject=f"[{message_type.upper()}] {message[:50]}...",
        content=content,
        priority="normal",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="EOA Kanban Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Create task
    create_parser = subparsers.add_parser("create-task", help="Create a new task")
    create_parser.add_argument("--title", required=True, help="Task title")
    create_parser.add_argument("--body", required=True, help="Task description")
    create_parser.add_argument("--agent", required=True, help="Agent to assign")
    create_parser.add_argument("--priority", default="normal", help="Priority level")
    create_parser.add_argument(
        "--blocked-by", type=int, nargs="*", help="Blocking issues"
    )
    create_parser.add_argument("--requirements-doc", help="Path to requirements doc")
    create_parser.add_argument("--notify", action="store_true", help="Notify agent")

    # Assign task
    assign_parser = subparsers.add_parser("assign-task", help="Assign task to agent")
    assign_parser.add_argument("--issue", type=int, required=True, help="Issue number")
    assign_parser.add_argument("--agent", required=True, help="Agent name")
    assign_parser.add_argument("--notify", action="store_true", help="Notify agent")

    # Update status
    status_parser = subparsers.add_parser("update-status", help="Update task status")
    status_parser.add_argument("--issue", type=int, required=True, help="Issue number")
    status_parser.add_argument(
        "--status", required=True, choices=list(KANBAN_COLUMNS.keys())
    )

    # Set dependency
    dep_parser = subparsers.add_parser("set-dependency", help="Set task dependency")
    dep_parser.add_argument("--issue", type=int, required=True, help="Issue number")
    dep_parser.add_argument(
        "--blocked-by", type=int, nargs="+", required=True, help="Blocking issues"
    )

    # Check ready tasks
    ready_parser = subparsers.add_parser(
        "check-ready-tasks", help="Check tasks ready for work"
    )
    ready_parser.add_argument(
        "--notify", action="store_true", help="Notify agents of ready tasks"
    )

    # Notify agent
    notify_parser = subparsers.add_parser(
        "notify-agent", help="Notify agent about task"
    )
    notify_parser.add_argument("--issue", type=int, required=True, help="Issue number")
    notify_parser.add_argument("--agent", required=True, help="Agent name")

    # Request PR review
    pr_parser = subparsers.add_parser(
        "request-pr-review", help="Request PR review from integrator"
    )
    pr_parser.add_argument("--pr", type=int, required=True, help="PR number")
    pr_parser.add_argument("--title", required=True, help="PR title")
    pr_parser.add_argument(
        "--issue", type=int, required=True, help="Related issue number"
    )
    pr_parser.add_argument("--agent", required=True, help="Submitting agent")

    args = parser.parse_args()

    # Pre-flight check: verify gh auth has project scopes
    if not check_gh_project_scopes():
        return 1

    # Load team registry
    try:
        registry = load_team_registry()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        if args.command == "create-task":
            requirements_doc = None
            if args.requirements_doc:
                with open(args.requirements_doc, encoding="utf-8") as f:
                    requirements_doc = f.read()

            result = create_task_issue(
                title=args.title,
                body=args.body,
                assigned_agent=args.agent,
                priority=args.priority,
                dependencies=args.blocked_by,
                task_requirements_doc=requirements_doc,
            )

            if result:
                print(f"Created task: #{result['number']} - {result['url']}")

                if args.notify:
                    notify_agent_of_task(
                        registry,
                        result["number"],
                        args.agent,
                        args.title,
                        requirements_doc,
                    )
                    print(f"Notified agent: {args.agent}")

                return 0
            return 1

        elif args.command == "assign-task":
            if assign_task_to_agent(args.issue, args.agent):
                print(f"Assigned #{args.issue} to {args.agent}")

                if args.notify:
                    # Get issue title
                    rc, stdout, _ = run_gh_command(
                        [
                            "issue",
                            "view",
                            str(args.issue),
                            "--repo",
                            f"{GITHUB_OWNER}/{GITHUB_REPO}",
                            "--json",
                            "title",
                        ]
                    )
                    title = (
                        json.loads(stdout).get("title", "Unknown")
                        if rc == 0
                        else "Unknown"
                    )

                    notify_agent_of_task(registry, args.issue, args.agent, title)
                    print(f"Notified agent: {args.agent}")

                return 0
            return 1

        elif args.command == "update-status":
            if update_task_status(args.issue, args.status):
                print(f"Updated #{args.issue} status to {args.status}")
                # When moving to "done", close the issue safely
                # (guards against Done-column auto-close)
                if args.status == "done":
                    close_issue_safely(args.issue)
                return 0
            return 1

        elif args.command == "set-dependency":
            if set_task_dependency(args.issue, args.blocked_by):
                print(f"Set #{args.issue} blocked by {args.blocked_by}")
                return 0
            return 1

        elif args.command == "check-ready-tasks":
            ready_tasks = get_ready_tasks(registry)
            print(f"Found {len(ready_tasks)} ready tasks:")
            for task in ready_tasks:
                print(
                    f"  #{task['number']}: {task['title']} -> {task['assigned_agent']}"
                )

                if args.notify:
                    notify_agent_of_task(
                        registry, task["number"], task["assigned_agent"], task["title"]
                    )
                    print(f"    Notified {task['assigned_agent']}")

            return 0

        elif args.command == "notify-agent":
            # Get issue title
            rc, stdout, _ = run_gh_command(
                [
                    "issue",
                    "view",
                    str(args.issue),
                    "--repo",
                    f"{GITHUB_OWNER}/{GITHUB_REPO}",
                    "--json",
                    "title",
                ]
            )
            title = json.loads(stdout).get("title", "Unknown") if rc == 0 else "Unknown"

            if notify_agent_of_task(registry, args.issue, args.agent, title):
                print(f"Notified {args.agent} about #{args.issue}")
                return 0
            return 1

        elif args.command == "request-pr-review":
            if request_pr_review(registry, args.pr, args.title, args.issue, args.agent):
                print(f"Requested PR review for #{args.pr}")
                return 0
            return 1

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
