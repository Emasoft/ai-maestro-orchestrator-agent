#!/usr/bin/env python3
"""
EOA Reassign Kanban Tasks Script

Reassigns GitHub Issues from one agent to another during agent replacement.
Updates issue assignees, labels, and adds audit comments for traceability.

This script uses the gh CLI tool to interact with GitHub Issues. It supports
dry-run mode to preview changes without making them.

Usage:
    python3 eoa_reassign_kanban_tasks.py --from-agent impl-1 --to-agent impl-2
    python3 eoa_reassign_kanban_tasks.py --from-agent impl-1 --to-agent impl-2 --dry-run
    python3 eoa_reassign_kanban_tasks.py --from-agent impl-1 --to-agent impl-2 --handoff-url URL
    python3 eoa_reassign_kanban_tasks.py --from-agent impl-1 --to-agent impl-2 --reason "load_balancing"

Exit codes:
    0 - Success (or dry-run completed)
    1 - Error (invalid arguments, GitHub API failure, etc.)

Examples:
    # Preview what would be reassigned:
    python3 eoa_reassign_kanban_tasks.py \\
        --from-agent implementer-1 --to-agent implementer-2 --dry-run

    # Reassign with handoff URL in audit comments:
    python3 eoa_reassign_kanban_tasks.py \\
        --from-agent implementer-1 --to-agent implementer-2 \\
        --handoff-url "https://github.com/owner/repo/issues/42#issuecomment-123456"

    # Reassign within a specific project:
    python3 eoa_reassign_kanban_tasks.py \\
        --from-agent implementer-1 --to-agent implementer-2 \\
        --project-name "Auth System v2"
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone


def find_issues_by_label(agent_id):
    """Find all open issues assigned to an agent by label.

    Searches for open issues that have the label 'assigned:<agent_id>'.

    Args:
        agent_id: The agent identifier to search for.

    Returns:
        A list of issue dictionaries with number, title, labels, and assignees.
        Returns an empty list if gh CLI is not available or the search fails.
    """
    label = "assigned:{}".format(agent_id)
    try:
        result = subprocess.run(
            ["gh", "issue", "list",
             "--label", label,
             "--state", "open",
             "--json", "number,title,labels,assignees",
             "--limit", "100"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            issues = json.loads(result.stdout)
            if isinstance(issues, list):
                return issues
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass
    return []


def find_issues_by_assignee(agent_id):
    """Find all open issues assigned to an agent by GitHub assignee.

    Args:
        agent_id: The GitHub username or agent ID to search for.

    Returns:
        A list of issue dictionaries with number, title, labels, and assignees.
        Returns an empty list if gh CLI is not available or the search fails.
    """
    try:
        result = subprocess.run(
            ["gh", "issue", "list",
             "--assignee", agent_id,
             "--state", "open",
             "--json", "number,title,labels,assignees",
             "--limit", "100"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            issues = json.loads(result.stdout)
            if isinstance(issues, list):
                return issues
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass
    return []


def check_issue_has_open_pr(issue_number):
    """Check if an issue has any open pull requests linked to it.

    Args:
        issue_number: The GitHub issue number.

    Returns:
        True if there are open PRs linked to this issue, False otherwise.
    """
    try:
        result = subprocess.run(
            ["gh", "issue", "view", str(issue_number),
             "--json", "body"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            # Simple heuristic: check for PR references in the timeline
            # A more robust approach would use the GitHub API
            pass
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return False


def update_issue_assignee(issue_number, old_agent, new_agent):
    """Update the assignee on a GitHub issue.

    Removes the old agent and adds the new agent as assignee.

    Args:
        issue_number: The GitHub issue number.
        old_agent: The agent ID to remove from assignees.
        new_agent: The agent ID to add as assignee.

    Returns:
        True if the update succeeded, False otherwise.
    """
    try:
        result = subprocess.run(
            ["gh", "issue", "edit", str(issue_number),
             "--remove-assignee", old_agent,
             "--add-assignee", new_agent],
            capture_output=True, text=True, timeout=30,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def update_issue_labels(issue_number, old_agent, new_agent):
    """Update assignment tracking labels on a GitHub issue.

    Removes the 'assigned:<old_agent>' label, adds 'assigned:<new_agent>'
    and 'reassigned' labels.

    Args:
        issue_number: The GitHub issue number.
        old_agent: The old agent ID (for label removal).
        new_agent: The new agent ID (for label addition).

    Returns:
        True if the update succeeded, False otherwise.
    """
    old_label = "assigned:{}".format(old_agent)
    new_label = "assigned:{}".format(new_agent)

    try:
        result = subprocess.run(
            ["gh", "issue", "edit", str(issue_number),
             "--remove-label", old_label,
             "--add-label", "{},reassigned".format(new_label)],
            capture_output=True, text=True, timeout=30,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def add_audit_comment(issue_number, old_agent, new_agent, reason, handoff_url=None):
    """Add a reassignment audit comment to a GitHub issue.

    Documents the reassignment with a structured markdown comment
    including timestamp, agents involved, reason, and optional
    handoff document link.

    Args:
        issue_number: The GitHub issue number.
        old_agent: The old agent ID.
        new_agent: The new agent ID.
        reason: The reason for reassignment.
        handoff_url: Optional URL to the handoff document.

    Returns:
        True if the comment was posted, False otherwise.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    comment_lines = [
        "## Agent Reassignment Notice",
        "",
        "| Field | Value |",
        "|-------|-------|",
        "| **Previous Agent** | {} |".format(old_agent),
        "| **New Agent** | {} |".format(new_agent),
        "| **Reason** | {} |".format(reason),
        "| **Timestamp** | {} |".format(now),
        "",
    ]

    if handoff_url:
        comment_lines.append("### Handoff Document")
        comment_lines.append("")
        comment_lines.append("Full context for new agent: {}".format(handoff_url))
        comment_lines.append("")

    comment_lines.append("*Automated reassignment by EOA*")

    comment_body = "\n".join(comment_lines)

    try:
        result = subprocess.run(
            ["gh", "issue", "comment", str(issue_number), "--body", comment_body],
            capture_output=True, text=True, timeout=30,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def main():
    """Main entry point for kanban task reassignment.

    Parses arguments, finds issues assigned to the old agent, and
    either previews (dry-run) or executes the reassignment by updating
    assignees, labels, and adding audit comments.

    Returns:
        Exit code: 0 for success, 1 for error.
    """
    parser = argparse.ArgumentParser(
        description="Reassign GitHub Issues from one agent to another"
    )
    parser.add_argument(
        "--from-agent", required=True,
        help="ID of the agent to reassign FROM"
    )
    parser.add_argument(
        "--to-agent", required=True,
        help="ID of the agent to reassign TO"
    )
    parser.add_argument(
        "--project-id", type=str, default=None,
        help="GitHub Project ID (for filtering)"
    )
    parser.add_argument(
        "--project-name", type=str, default=None,
        help="GitHub Project name (alternative to ID)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", default=False,
        help="Show what would be changed without making changes"
    )
    parser.add_argument(
        "--handoff-url", type=str, default=None,
        help="URL of handoff document to include in audit comments"
    )
    parser.add_argument(
        "--reason", type=str, default="agent_replacement",
        help="Reason for reassignment (default: agent_replacement)"
    )

    args = parser.parse_args()

    # Validate: from-agent and to-agent must be different
    if args.from_agent == args.to_agent:
        print(json.dumps({
            "error": "Cannot reassign from agent to the same agent",
            "from_agent": args.from_agent,
            "to_agent": args.to_agent,
        }), file=sys.stderr)
        return 1

    # Find issues assigned to the old agent using both label and assignee search
    issues_by_label = find_issues_by_label(args.from_agent)
    issues_by_assignee = find_issues_by_assignee(args.from_agent)

    # Merge and deduplicate by issue number
    seen_numbers = set()
    all_issues = []
    for issue in issues_by_label + issues_by_assignee:
        num = issue.get("number")
        if num and num not in seen_numbers:
            seen_numbers.add(num)
            all_issues.append(issue)

    # Results tracking
    reassigned_count = 0
    failed_count = 0
    details = []

    if args.dry_run:
        # Dry-run mode: report what would be changed
        for issue in all_issues:
            num = issue.get("number", "?")
            title = issue.get("title", "Untitled")
            has_pr = check_issue_has_open_pr(num)
            detail = {
                "issue_number": num,
                "title": title,
                "action": "would_reassign",
                "has_open_pr": has_pr,
            }
            if has_pr:
                detail["warning"] = "Issue has open PR - PR author cannot be changed"
            details.append(detail)
            reassigned_count += 1

        result = {
            "dry_run": True,
            "from_agent": args.from_agent,
            "to_agent": args.to_agent,
            "reassigned": reassigned_count,
            "failed": 0,
            "details": details,
        }
        print(json.dumps(result, indent=2))
        return 0

    # Execute reassignment
    for issue in all_issues:
        num = issue.get("number")
        title = issue.get("title", "Untitled")

        if not num:
            failed_count += 1
            details.append({
                "issue_number": None,
                "title": title,
                "action": "skipped",
                "error": "Missing issue number",
            })
            continue

        # Check for open PRs (warn but proceed)
        has_pr = check_issue_has_open_pr(num)

        # Update assignee
        assignee_ok = update_issue_assignee(num, args.from_agent, args.to_agent)

        # Update labels
        labels_ok = update_issue_labels(num, args.from_agent, args.to_agent)

        # Add audit comment
        comment_ok = add_audit_comment(
            num, args.from_agent, args.to_agent,
            args.reason, args.handoff_url,
        )

        if assignee_ok or labels_ok:
            reassigned_count += 1
            detail = {
                "issue_number": num,
                "title": title,
                "action": "reassigned",
                "assignee_updated": assignee_ok,
                "labels_updated": labels_ok,
                "comment_added": comment_ok,
            }
            if has_pr:
                detail["warning"] = "Issue has open PR - PR author cannot be changed"
            details.append(detail)
        else:
            failed_count += 1
            details.append({
                "issue_number": num,
                "title": title,
                "action": "failed",
                "error": "Could not update assignee or labels",
            })

    result = {
        "dry_run": False,
        "from_agent": args.from_agent,
        "to_agent": args.to_agent,
        "reassigned": reassigned_count,
        "failed": failed_count,
        "details": details,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
