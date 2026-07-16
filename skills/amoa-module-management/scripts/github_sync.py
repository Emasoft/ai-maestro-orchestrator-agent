#!/usr/bin/env python3
"""
GitHub Issue Synchronization Script

Synchronizes module state with GitHub Issues.
Used by the module-management-commands skill.

Usage:
    python3 github_sync.py sync-all        # Sync all modules
    python3 github_sync.py sync MODULE_ID  # Sync specific module
    python3 github_sync.py verify          # Verify sync status
    python3 github_sync.py create-labels   # Create required labels
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "shared"))
from amoa_kanban_vocab import (
    KANBAN_COLUMNS,
    STATUS_LABEL_COLORS,
    STATUS_LABEL_DESCRIPTIONS,
    resolve_column,
)
from amoa_state import EXEC_STATE_FILE
from amoa_state import parse_frontmatter as _shared_parse_frontmatter

# One `status:<column>` label per ratified column, styled from the shared
# vocabulary (issue #27). This script used to hand-list 8 labels of the
# pre-2026-06-20 vocabulary plus its own status→label map, so a module in a
# column the list did not know (e.g. `dev`) was silently labelled `status:todo`.
# Deriving the labels FROM the vocabulary makes that drift impossible: add a
# column, get its label.
REQUIRED_LABELS: dict[str, dict[str, str]] = {
    "module": {"color": "0052CC", "description": "AMOA orchestration module"},
    "priority:critical": {"color": "B60205", "description": "Critical priority"},
    "priority:high": {"color": "D93F0B", "description": "High priority"},
    "priority:medium": {"color": "FBCA04", "description": "Medium priority"},
    "priority:low": {"color": "0E8A16", "description": "Low priority"},
    **{
        f"status:{column}": {
            "color": STATUS_LABEL_COLORS[f"status:{column}"],
            "description": STATUS_LABEL_DESCRIPTIONS[f"status:{column}"],
        }
        for column in KANBAN_COLUMNS
    },
}


def parse_frontmatter(file_path: Path) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter and return (data, body)."""
    return _shared_parse_frontmatter(file_path)


def write_state_file(file_path: Path, data: dict[str, Any], body: str) -> bool:
    """Write a state file with YAML frontmatter."""
    try:
        yaml_content = yaml.dump(
            data, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
        content = f"---\n{yaml_content}---\n\n{body}"
        file_path.write_text(content, encoding="utf-8")
        return True
    except Exception as e:
        print(f"ERROR: Failed to write state file: {e}")
        return False


def gh_issue_exists(issue_num: str) -> bool:
    """Check if a GitHub Issue exists."""
    try:
        result = subprocess.run(
            ["gh", "issue", "view", issue_num, "--json", "number"],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def gh_issue_create(
    title: str, body: str, labels: list[str]
) -> str | None:
    """Create a GitHub Issue and return the issue number."""
    try:
        result = subprocess.run(
            [
                "gh", "issue", "create",
                "--title", title,
                "--body", body,
                "--label", ",".join(labels)
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            output = result.stdout.strip()
            if "/issues/" in output:
                return f"#{output.split('/issues/')[-1]}"
        return None
    except Exception as e:
        print(f"Error creating issue: {e}")
        return None


def gh_issue_update(
    issue_num: str,
    title: str | None = None,
    body: str | None = None,
    add_labels: list[str] | None = None,
    remove_labels: list[str] | None = None
) -> bool:
    """Update a GitHub Issue."""
    try:
        cmd = ["gh", "issue", "edit", issue_num]

        if title:
            cmd.extend(["--title", title])
        if body:
            cmd.extend(["--body", body])
        if add_labels:
            for label in add_labels:
                cmd.extend(["--add-label", label])
        if remove_labels:
            for label in remove_labels:
                cmd.extend(["--remove-label", label])

        result = subprocess.run(cmd, capture_output=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        print(f"Error updating issue: {e}")
        return False


def gh_get_issue_labels(issue_num: str) -> list[str]:
    """Get labels from a GitHub Issue."""
    try:
        result = subprocess.run(
            ["gh", "issue", "view", issue_num, "--json", "labels"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            return [label["name"] for label in data.get("labels", [])]
        return []
    except Exception:
        return []


def generate_issue_body(module: dict[str, Any], plan_id: str) -> str:
    """Generate the issue body for a module."""
    return f"""## Module: {module.get('name', module.get('id'))}

### Description
Implementation of the {module.get('name', module.get('id'))} module.

### Acceptance Criteria
- [ ] {module.get('acceptance_criteria', 'No criteria defined')}

### Priority
{module.get('priority', 'medium')}

### Related
- Plan ID: {plan_id}
- Module ID: {module.get('id')}
"""


def _create_module_issue(
    module: dict[str, Any],
    plan_id: str,
    result: dict[str, Any],
    success_template: str,
    failure_message: str,
) -> None:
    """Create the module's GitHub Issue and record the outcome in ``result``.

    Shared by the create and recreate paths of sync_module; the two callers
    differ only in the wording of the outcome messages.

    Args:
        module: The module entry (mutated: github_issue is set on success).
        plan_id: The plan identifier for the issue body.
        result: The sync result dict (mutated: issue/success/message).
        success_template: Message template with a {new_issue} placeholder.
        failure_message: Message recorded when issue creation fails.
    """
    title = f"[Module] {module.get('name', module.get('id'))}"
    body = generate_issue_body(module, plan_id)
    labels = ["module", f"priority:{module.get('priority', 'medium')}"]

    # Resolve to a ratified column: a legacy status migrates, an unknown one
    # aborts the create. Previously an unknown status was labelled `status:todo`,
    # which put untriaged work in the ready-to-start lane where check-ready-tasks
    # would hand it to an agent (issue #27).
    status = module.get("status", "todo")
    try:
        column = resolve_column(status)
    except ValueError as exc:
        result["message"] = f"cannot create issue for {module.get('id')}: {exc}"
        return
    labels.append(f"status:{column}")

    new_issue = gh_issue_create(title, body, labels)
    if new_issue:
        module["github_issue"] = new_issue
        result["issue"] = new_issue
        result["success"] = True
        result["message"] = success_template.format(new_issue=new_issue)
    else:
        result["message"] = failure_message


def sync_module(module: dict[str, Any], plan_id: str, update_state: bool = True) -> dict[str, Any]:
    """Sync a single module with GitHub Issue."""
    result = {
        "module_id": module.get("id"),
        "action": None,
        "success": False,
        "issue": module.get("github_issue"),
        "message": ""
    }

    issue = module.get("github_issue")

    if issue:
        # Issue exists, update it
        issue_num = issue.replace("#", "")

        if not gh_issue_exists(issue_num):
            result["action"] = "create"
            result["message"] = "Issue no longer exists, recreating"

            # Create new issue
            _create_module_issue(
                module, plan_id, result,
                "Recreated issue as {new_issue}", "Failed to recreate issue",
            )
        else:
            # Update existing issue
            result["action"] = "update"
            title = f"[Module] {module.get('name', module.get('id'))}"
            body = generate_issue_body(module, plan_id)

            # Get current labels to determine what to change
            current_labels = gh_get_issue_labels(issue_num)

            # Determine label changes
            add_labels = []
            remove_labels = []

            # Priority label
            priority = module.get("priority", "medium")
            expected_priority = f"priority:{priority}"
            for label in current_labels:
                if label.startswith("priority:") and label != expected_priority:
                    remove_labels.append(label)
            if expected_priority not in current_labels:
                add_labels.append(expected_priority)

            # Status label — same resolve-or-refuse contract as the create path;
            # a stale legacy label on the issue is replaced by the resolved one.
            status = module.get("status", "todo")
            try:
                expected_status = f"status:{resolve_column(status)}"
            except ValueError as exc:
                result["message"] = f"cannot update issue #{issue_num}: {exc}"
                return result
            for label in current_labels:
                if label.startswith("status:") and label != expected_status:
                    remove_labels.append(label)
            if expected_status not in current_labels:
                add_labels.append(expected_status)

            # Module label
            if "module" not in current_labels:
                add_labels.append("module")

            success = gh_issue_update(
                issue_num,
                title=title,
                body=body,
                add_labels=add_labels if add_labels else None,
                remove_labels=remove_labels if remove_labels else None
            )

            result["success"] = success
            result["message"] = "Updated" if success else "Failed to update"

    else:
        # No issue, create one
        result["action"] = "create"

        _create_module_issue(
            module, plan_id, result,
            "Created {new_issue}", "Failed to create issue",
        )

    return result


def cmd_sync_all(args: argparse.Namespace) -> int:
    """Sync all modules with GitHub Issues."""
    data, body = parse_frontmatter(EXEC_STATE_FILE)
    if not data:
        print("ERROR: Could not parse state file")
        return 1

    modules = data.get("modules_status", [])
    plan_id = data.get("plan_id", "unknown")

    if not modules:
        print("No modules found")
        return 0

    print(f"Syncing {len(modules)} modules...\n")

    success_count = 0
    fail_count = 0

    for module in modules:
        result = sync_module(module, plan_id)
        status = "OK" if result["success"] else "FAIL"
        print(f"  [{status}] {result['module_id']}: {result['message']}")

        if result["success"]:
            success_count += 1
        else:
            fail_count += 1

    # Write updated state
    if not write_state_file(EXEC_STATE_FILE, data, body):
        print("Warning: Could not update state file")

    print(f"\nCompleted: {success_count} succeeded, {fail_count} failed")
    return 0 if fail_count == 0 else 1


def cmd_sync(args: argparse.Namespace) -> int:
    """Sync a specific module."""
    data, body = parse_frontmatter(EXEC_STATE_FILE)
    if not data:
        print("ERROR: Could not parse state file")
        return 1

    modules = data.get("modules_status", [])
    plan_id = data.get("plan_id", "unknown")

    module = None
    for m in modules:
        if m.get("id") == args.module_id:
            module = m
            break

    if not module:
        print(f"ERROR: Module '{args.module_id}' not found")
        return 1

    result = sync_module(module, plan_id)
    status = "OK" if result["success"] else "FAIL"
    print(f"[{status}] {result['module_id']}: {result['message']}")

    # Write updated state
    if result["success"]:
        if not write_state_file(EXEC_STATE_FILE, data, body):
            print("Warning: Could not update state file")

    return 0 if result["success"] else 1


def cmd_verify(args: argparse.Namespace) -> int:
    """Verify sync status of all modules."""
    data, body = parse_frontmatter(EXEC_STATE_FILE)
    if not data:
        print("ERROR: Could not parse state file")
        return 1

    modules = data.get("modules_status", [])

    if not modules:
        print("No modules found")
        return 0

    print(f"Verifying {len(modules)} modules...\n")

    issues = []

    for module in modules:
        module_id = module.get("id")
        issue = module.get("github_issue")

        if not issue:
            issues.append(f"{module_id}: No GitHub Issue linked")
            print(f"  [MISSING] {module_id}: No issue")
        else:
            issue_num = issue.replace("#", "")
            if gh_issue_exists(issue_num):
                # Check labels
                labels = gh_get_issue_labels(issue_num)
                expected_priority = f"priority:{module.get('priority', 'medium')}"

                if "module" not in labels:
                    issues.append(f"{module_id}: Missing 'module' label")

                has_priority = any(label.startswith("priority:") for label in labels)
                if not has_priority:
                    issues.append(f"{module_id}: Missing priority label")
                elif expected_priority not in labels:
                    issues.append(f"{module_id}: Priority mismatch (expected {expected_priority})")

                print(f"  [OK] {module_id}: {issue}")
            else:
                issues.append(f"{module_id}: Issue {issue} does not exist")
                print(f"  [MISSING] {module_id}: Issue {issue} not found")

    if issues:
        print(f"\nFound {len(issues)} issues:")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    else:
        print("\nAll modules synced correctly")
        return 0


def cmd_create_labels(args: argparse.Namespace) -> int:
    """Create required labels in the repository."""
    print("Creating required labels...\n")

    for label, config in REQUIRED_LABELS.items():
        try:
            result = subprocess.run(
                [
                    "gh", "label", "create", label,
                    "--color", config["color"],
                    "--description", config["description"],
                    "--force"
                ],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                print(f"  [OK] {label}")
            else:
                # Label might already exist
                if "already exists" in result.stderr.lower():
                    print(f"  [EXISTS] {label}")
                else:
                    print(f"  [FAIL] {label}: {result.stderr.strip()}")
        except Exception as e:
            print(f"  [ERROR] {label}: {e}")

    print("\nLabel creation complete")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="GitHub Issue synchronization for AMOA modules"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # sync-all command
    subparsers.add_parser("sync-all", help="Sync all modules with GitHub Issues")

    # sync command
    sync_parser = subparsers.add_parser("sync", help="Sync specific module")
    sync_parser.add_argument("module_id", help="Module ID to sync")

    # verify command
    subparsers.add_parser("verify", help="Verify sync status")

    # create-labels command
    subparsers.add_parser("create-labels", help="Create required labels")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Check if in orchestration phase (except for create-labels)
    if args.command != "create-labels" and not EXEC_STATE_FILE.exists():
        print("ERROR: Not in Orchestration Phase")
        print("State file not found:", EXEC_STATE_FILE)
        return 1

    commands = {
        "sync-all": cmd_sync_all,
        "sync": cmd_sync,
        "verify": cmd_verify,
        "create-labels": cmd_create_labels,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
