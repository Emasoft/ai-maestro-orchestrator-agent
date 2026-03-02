#!/usr/bin/env python3
"""
AMOA Sync GitHub Issues Script

Synchronizes modules from orchestration state with GitHub Issues lifecycle.
Reads module data from .ai-maestro/orchestration-state.json and uses the gh CLI
to create, update, and close GitHub issues to keep them in sync with module
status.

Label mapping for module statuses:
    planning    -> status:planning
    assigned    -> status:assigned
    in-progress -> status:in-progress
    review      -> status:review
    verified    -> status:verified
    complete    -> status:complete

Usage:
    python3 amoa_sync_github_issues.py
    python3 amoa_sync_github_issues.py --dry-run
    python3 amoa_sync_github_issues.py --create-missing --update-labels --close-completed
    python3 amoa_sync_github_issues.py --repo owner/repo --dry-run
    python3 amoa_sync_github_issues.py --project-root /path/to/project

Exit codes:
    0 - Success (all sync operations completed or dry-run finished)
    1 - Error (missing state file, gh CLI failure, or invalid arguments)

Examples:
    # Dry-run to preview what would be synced:
    python3 amoa_sync_github_issues.py --dry-run --create-missing --update-labels

    # Create missing issues and update labels:
    python3 amoa_sync_github_issues.py --create-missing --update-labels

    # Full sync including closing completed modules:
    python3 amoa_sync_github_issues.py \
        --create-missing --update-labels --close-completed

    # Sync for a specific repo:
    python3 amoa_sync_github_issues.py \
        --repo Emasoft/my-project --create-missing --update-labels
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


# State file location relative to the project root
STATE_FILE_PATH = ".ai-maestro/orchestration-state.json"

# Module status to GitHub label mapping
STATUS_LABEL_MAP = {
    "planning": "status:planning",
    "assigned": "status:assigned",
    "in-progress": "status:in-progress",
    "review": "status:review",
    "verified": "status:verified",
    "complete": "status:complete",
}

# All status labels (used to remove stale labels when updating)
ALL_STATUS_LABELS = list(STATUS_LABEL_MAP.values())

# Default label applied to all module issues
MODULE_LABEL = "module"


def load_state(project_root):
    """Load orchestration state from the JSON state file.

    Args:
        project_root: Path to the project root directory.

    Returns:
        A dictionary with the state data, or None if the file does not
        exist, is empty, or contains invalid JSON.
    """
    state_path = Path(project_root) / STATE_FILE_PATH
    if not state_path.exists():
        return None

    try:
        content = state_path.read_text(encoding="utf-8").strip()
        if not content:
            return None
        data = json.loads(content)
        if not isinstance(data, dict):
            return None
        return data
    except (json.JSONDecodeError, OSError):
        return None


def get_modules(state):
    """Extract the modules list from orchestration state.

    Args:
        state: The orchestration state dictionary.

    Returns:
        A list of module dictionaries. Each module has at minimum
        an 'id' and 'status' field.
    """
    modules = state.get("modules_status", [])
    if not isinstance(modules, list):
        return []
    return [m for m in modules if isinstance(m, dict) and m.get("id")]


def gh_command(args, project_root, timeout=30):
    """Execute a gh CLI command and return (success, stdout).

    Args:
        args: List of arguments to pass to gh (without the 'gh' prefix).
        project_root: Path to the project root (used as cwd).
        timeout: Timeout in seconds for the command.

    Returns:
        A tuple of (success_bool, output_string). On failure, output
        contains the stderr message.
    """
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(project_root),
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except FileNotFoundError:
        return False, "gh CLI not found -- install from https://cli.github.com/"
    except OSError as e:
        return False, str(e)


def find_existing_issue(module_id, project_root, repo=None):
    """Find an existing GitHub issue for a module by searching title or label.

    Searches for open issues with the 'module' label whose title contains
    the module ID.

    Args:
        module_id: The module identifier to search for.
        project_root: Path to the project root (used as cwd for gh).
        repo: Optional owner/repo to search in. If None, uses current repo.

    Returns:
        A dictionary with issue 'number' and 'title', or None if not found.
    """
    args = [
        "issue", "list",
        "--label", MODULE_LABEL,
        "--state", "open",
        "--search", module_id,
        "--json", "number,title,labels,state",
        "--limit", "20",
    ]
    if repo:
        args.extend(["--repo", repo])

    success, output = gh_command(args, project_root)
    if not success or not output:
        return None

    try:
        issues = json.loads(output)
    except json.JSONDecodeError:
        return None

    if not isinstance(issues, list):
        return None

    # Find an issue whose title contains the module ID
    for issue in issues:
        title = issue.get("title", "")
        if module_id in title:
            return issue

    return None


def get_issue_labels(issue_number, project_root, repo=None):
    """Get the current labels on a GitHub issue.

    Args:
        issue_number: The GitHub issue number.
        project_root: Path to the project root (used as cwd for gh).
        repo: Optional owner/repo. If None, uses current repo.

    Returns:
        A list of label name strings. Returns an empty list on failure.
    """
    args = [
        "issue", "view", str(issue_number),
        "--json", "labels",
    ]
    if repo:
        args.extend(["--repo", repo])

    success, output = gh_command(args, project_root)
    if not success or not output:
        return []

    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        return []

    labels = data.get("labels", [])
    return [
        label.get("name", "") if isinstance(label, dict) else str(label)
        for label in labels
    ]


def ensure_label_exists(label_name, project_root, repo=None):
    """Ensure a GitHub label exists, creating it if missing.

    Args:
        label_name: The label name to ensure exists.
        project_root: Path to the project root (used as cwd for gh).
        repo: Optional owner/repo. If None, uses current repo.

    Returns:
        True if the label exists or was created, False on failure.
    """
    # Determine color based on label name
    color = "0052CC"  # Default blue
    if "planning" in label_name:
        color = "BFD4F2"
    elif "assigned" in label_name:
        color = "D4C5F9"
    elif "in-progress" in label_name:
        color = "FBCA04"
    elif "review" in label_name:
        color = "F9D0C4"
    elif "verified" in label_name:
        color = "0E8A16"
    elif "complete" in label_name:
        color = "006B75"

    args = ["label", "create", label_name, "--color", color, "--force"]
    if repo:
        args.extend(["--repo", repo])

    success, _ = gh_command(args, project_root)
    return success


def create_issue_for_module(module, project_root, repo=None, dry_run=False):
    """Create a GitHub issue for a module that does not have one yet.

    Args:
        module: The module dictionary from orchestration state.
        project_root: Path to the project root (used as cwd for gh).
        repo: Optional owner/repo. If None, uses current repo.
        dry_run: If True, do not actually create the issue.

    Returns:
        A result dictionary with 'action', 'module_id', 'success',
        and optionally 'issue_number', 'issue_url', or 'error'.
    """
    module_id = module.get("id", "unknown")
    status = module.get("status", "planning")
    description = module.get("description", "")
    priority = module.get("priority", "medium")
    assigned_to = module.get("assigned_to", "")
    deps = module.get("dependencies", [])

    result = {
        "action": "create",
        "module_id": module_id,
        "success": False,
    }

    if dry_run:
        result["dry_run"] = True
        result["success"] = True
        result["would_create"] = "[Module] {}".format(module_id)
        return result

    # Build issue body
    body_lines = [
        "## Module Information",
        "",
        "| Field | Value |",
        "|-------|-------|",
        "| **Module ID** | {} |".format(module_id),
        "| **Status** | {} |".format(status),
        "| **Priority** | {} |".format(priority),
    ]
    if assigned_to:
        body_lines.append("| **Assigned To** | {} |".format(assigned_to))
    if deps:
        body_lines.append("| **Dependencies** | {} |".format(", ".join(str(d) for d in deps)))
    body_lines.append("")

    if description:
        body_lines.extend(["## Description", "", description, ""])

    body_lines.extend([
        "---",
        "",
        "*This issue was created by the AMOA orchestration system.*",
    ])
    body = "\n".join(body_lines)

    title = "[Module] {}".format(module_id)

    # Determine labels
    labels = [MODULE_LABEL]
    status_label = STATUS_LABEL_MAP.get(status)
    if status_label:
        labels.append(status_label)

    # Ensure labels exist
    for label in labels:
        ensure_label_exists(label, project_root, repo)

    # Build gh command
    args = [
        "issue", "create",
        "--title", title,
        "--body", body,
    ]
    for label in labels:
        args.extend(["--label", label])
    if repo:
        args.extend(["--repo", repo])

    success, output = gh_command(args, project_root)
    if success:
        result["success"] = True
        result["issue_url"] = output
        # Extract issue number from URL
        if "/" in output:
            result["issue_number"] = output.split("/")[-1]
    else:
        result["error"] = output

    return result


def update_issue_labels(issue_number, new_status, project_root, repo=None, dry_run=False):
    """Update the status label on a GitHub issue.

    Removes all existing status:* labels and adds the label
    corresponding to the new status.

    Args:
        issue_number: The GitHub issue number.
        new_status: The new module status string (e.g. 'in-progress').
        project_root: Path to the project root (used as cwd for gh).
        repo: Optional owner/repo. If None, uses current repo.
        dry_run: If True, do not actually update labels.

    Returns:
        A result dictionary with 'action', 'issue_number', 'success',
        and optionally 'old_labels', 'new_label', or 'error'.
    """
    result = {
        "action": "update_labels",
        "issue_number": str(issue_number),
        "new_status": new_status,
        "success": False,
    }

    new_label = STATUS_LABEL_MAP.get(new_status)
    if not new_label:
        result["error"] = "Unknown status: {}".format(new_status)
        return result

    # Get current labels
    current_labels = get_issue_labels(issue_number, project_root, repo)
    result["current_labels"] = current_labels

    # Find status labels to remove
    labels_to_remove = [
        label for label in current_labels
        if label in ALL_STATUS_LABELS and label != new_label
    ]

    # Check if the new label is already present
    if new_label in current_labels and not labels_to_remove:
        result["success"] = True
        result["message"] = "Label already correct"
        return result

    if dry_run:
        result["dry_run"] = True
        result["success"] = True
        result["would_remove"] = labels_to_remove
        result["would_add"] = new_label
        return result

    # Ensure the new label exists
    ensure_label_exists(new_label, project_root, repo)

    # Remove old status labels
    for old_label in labels_to_remove:
        args = ["issue", "edit", str(issue_number), "--remove-label", old_label]
        if repo:
            args.extend(["--repo", repo])
        gh_command(args, project_root)

    # Add new status label
    args = ["issue", "edit", str(issue_number), "--add-label", new_label]
    if repo:
        args.extend(["--repo", repo])

    success, output = gh_command(args, project_root)
    if success:
        result["success"] = True
        result["removed_labels"] = labels_to_remove
        result["added_label"] = new_label
    else:
        result["error"] = output

    return result


def close_issue(issue_number, project_root, repo=None, dry_run=False):
    """Close a GitHub issue for a completed module.

    Args:
        issue_number: The GitHub issue number to close.
        project_root: Path to the project root (used as cwd for gh).
        repo: Optional owner/repo. If None, uses current repo.
        dry_run: If True, do not actually close the issue.

    Returns:
        A result dictionary with 'action', 'issue_number', 'success',
        and optionally 'error'.
    """
    result = {
        "action": "close",
        "issue_number": str(issue_number),
        "success": False,
    }

    if dry_run:
        result["dry_run"] = True
        result["success"] = True
        result["would_close"] = str(issue_number)
        return result

    args = ["issue", "close", str(issue_number), "--reason", "completed"]
    if repo:
        args.extend(["--repo", repo])

    success, output = gh_command(args, project_root)
    if success:
        result["success"] = True
    else:
        result["error"] = output

    return result


def main():
    """Main entry point for GitHub Issues sync.

    Reads orchestration state, compares module statuses with existing
    GitHub issues, and performs create/update/close operations as
    requested by CLI flags.

    Returns:
        Exit code: 0 for success, 1 for error.
    """
    parser = argparse.ArgumentParser(
        description="Sync modules with GitHub Issues lifecycle"
    )
    parser.add_argument(
        "--project-root", type=str, default=".",
        help="Path to the project root directory (default: current directory)"
    )
    parser.add_argument(
        "--repo", type=str, default=None,
        help="GitHub repository in OWNER/REPO format (default: current repo)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", default=False,
        help="Preview what would be done without executing any changes"
    )
    parser.add_argument(
        "--create-missing", action="store_true", default=False,
        help="Create GitHub issues for modules that do not have one"
    )
    parser.add_argument(
        "--update-labels", action="store_true", default=False,
        help="Update status labels on existing issues to match module status"
    )
    parser.add_argument(
        "--close-completed", action="store_true", default=False,
        help="Close GitHub issues for modules with status 'complete'"
    )

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    if not project_root.is_dir():
        print(
            json.dumps({"error": "Project root does not exist: {}".format(args.project_root)}),
            file=sys.stderr,
        )
        return 1

    # Load orchestration state
    state = load_state(project_root)
    if state is None:
        print(
            json.dumps({"error": "Orchestration state file not found at {}".format(STATE_FILE_PATH)}),
            file=sys.stderr,
        )
        return 1

    # Get modules from state
    modules = get_modules(state)
    if not modules:
        print(json.dumps({
            "success": True,
            "message": "No modules found in orchestration state",
            "operations": [],
        }, indent=2))
        return 0

    # Check that at least one operation is requested
    if not args.create_missing and not args.update_labels and not args.close_completed:
        print(json.dumps({
            "success": True,
            "message": "No operations requested. Use --create-missing, --update-labels, or --close-completed.",
            "modules_found": len(modules),
        }, indent=2))
        return 0

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    operations = []

    for module in modules:
        module_id = module.get("id", "unknown")
        status = module.get("status", "planning")
        github_issue = module.get("github_issue")

        # Try to find existing issue if not recorded in state
        existing_issue = None
        if github_issue:
            existing_issue = {"number": github_issue}
        else:
            existing_issue = find_existing_issue(module_id, project_root, args.repo)

        issue_number = None
        if existing_issue:
            issue_number = existing_issue.get("number")

        # CREATE: If no existing issue and --create-missing
        if not existing_issue and args.create_missing:
            op_result = create_issue_for_module(
                module, project_root, args.repo, args.dry_run
            )
            operations.append(op_result)
            # If we just created the issue, use the new number for further ops
            if op_result.get("issue_number"):
                issue_number = op_result["issue_number"]

        # UPDATE LABELS: If issue exists and --update-labels
        if issue_number and args.update_labels:
            op_result = update_issue_labels(
                issue_number, status, project_root, args.repo, args.dry_run
            )
            operations.append(op_result)

        # CLOSE: If module is complete and --close-completed
        if issue_number and args.close_completed and status in ("complete", "done"):
            op_result = close_issue(
                issue_number, project_root, args.repo, args.dry_run
            )
            operations.append(op_result)

    # Count successes and failures
    total = len(operations)
    successes = sum(1 for op in operations if op.get("success"))
    failures = total - successes

    # Output summary
    summary = {
        "success": failures == 0,
        "timestamp": timestamp,
        "dry_run": args.dry_run,
        "modules_found": len(modules),
        "operations_total": total,
        "operations_succeeded": successes,
        "operations_failed": failures,
        "operations": operations,
    }
    print(json.dumps(summary, indent=2))

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
