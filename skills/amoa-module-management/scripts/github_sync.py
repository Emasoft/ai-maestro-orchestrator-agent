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

# State file location
EXEC_STATE_FILE = Path(".claude/orchestrator-exec-phase.local.md")

# Required labels
REQUIRED_LABELS = {
    "module": {"color": "0052CC", "description": "EOA orchestration module"},
    "priority:critical": {"color": "B60205", "description": "Critical priority"},
    "priority:high": {"color": "D93F0B", "description": "High priority"},
    "priority:medium": {"color": "FBCA04", "description": "Medium priority"},
    "priority:low": {"color": "0E8A16", "description": "Low priority"},
    "status:backlog": {"color": "D4C5F9", "description": "In backlog"},
    "status:todo": {"color": "EDEDED", "description": "Not yet started"},
    "status:in-progress": {"color": "5319E7", "description": "Work in progress"},
    "status:ai-review": {"color": "BFDADC", "description": "Awaiting AI review"},
    "status:human-review": {"color": "D4C5F9", "description": "Awaiting human review"},
    "status:merge-release": {"color": "C2E0C6", "description": "Ready to merge/release"},
    "status:blocked": {"color": "B60205", "description": "Blocked by dependency"},
    "status:done": {"color": "0E8A16", "description": "Completed"},
}


def parse_frontmatter(file_path: Path) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter and return (data, body)."""
    if not file_path.exists():
        return {}, ""

    content = file_path.read_text(encoding="utf-8")

    if not content.startswith("---"):
        return {}, content

    end_index = content.find("---", 3)
    if end_index == -1:
        return {}, content

    yaml_content = content[3:end_index].strip()
    body = content[end_index + 3:].strip()

    try:
        data = yaml.safe_load(yaml_content) or {}
        return data, body
    except yaml.YAMLError:
        return {}, content


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
            title = f"[Module] {module.get('name', module.get('id'))}"
            body = generate_issue_body(module, plan_id)
            labels = ["module", f"priority:{module.get('priority', 'medium')}"]

            status = module.get("status", "todo")
            status_map = {
                "backlog": "status:backlog",
                "todo": "status:todo",
                "in-progress": "status:in-progress",
                "in_progress": "status:in-progress",
                "ai-review": "status:ai-review",
                "human-review": "status:human-review",
                "merge-release": "status:merge-release",
                "blocked": "status:blocked",
                "done": "status:done",
            }
            labels.append(status_map.get(status, "status:todo"))

            new_issue = gh_issue_create(title, body, labels)
            if new_issue:
                module["github_issue"] = new_issue
                result["issue"] = new_issue
                result["success"] = True
                result["message"] = f"Recreated issue as {new_issue}"
            else:
                result["message"] = "Failed to recreate issue"
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

            # Status label
            status = module.get("status", "todo")
            status_map = {
                "backlog": "status:backlog",
                "todo": "status:todo",
                "in-progress": "status:in-progress",
                "in_progress": "status:in-progress",
                "ai-review": "status:ai-review",
                "human-review": "status:human-review",
                "merge-release": "status:merge-release",
                "blocked": "status:blocked",
                "done": "status:done",
            }
            expected_status = status_map.get(status, "status:todo")
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

        title = f"[Module] {module.get('name', module.get('id'))}"
        body = generate_issue_body(module, plan_id)
        labels = ["module", f"priority:{module.get('priority', 'medium')}"]

        status = module.get("status", "todo")
        status_map = {
            "backlog": "status:backlog",
            "todo": "status:todo",
            "in-progress": "status:in-progress",
            "in_progress": "status:in-progress",
            "ai-review": "status:ai-review",
            "human-review": "status:human-review",
            "merge-release": "status:merge-release",
            "blocked": "status:blocked",
            "done": "status:done",
        }
        labels.append(status_map.get(status, "status:todo"))

        new_issue = gh_issue_create(title, body, labels)
        if new_issue:
            module["github_issue"] = new_issue
            result["issue"] = new_issue
            result["success"] = True
            result["message"] = f"Created {new_issue}"
        else:
            result["message"] = "Failed to create issue"

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
        description="GitHub Issue synchronization for EOA modules"
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
