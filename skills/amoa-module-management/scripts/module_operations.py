#!/usr/bin/env python3
"""
Module Operations Script

Provides programmatic access to all module management operations.
Used by the module-management-commands skill.

Usage:
    python3 module_operations.py add "Module Name" --criteria "Criteria"
    python3 module_operations.py modify module-id --priority critical
    python3 module_operations.py remove module-id
    python3 module_operations.py list
    python3 module_operations.py validate
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

# State file location
EXEC_STATE_FILE = Path(".claude/orchestrator-exec-phase.local.md")


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
    except yaml.YAMLError as e:
        print(f"ERROR: YAML parse error: {e}")
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


def normalize_id(name: str) -> str:
    """Convert a name to a valid ID (kebab-case)."""
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", name.lower())
    return normalized.strip("-")


def create_github_issue(
    module_name: str, criteria: str, priority: str, plan_id: str
) -> str | None:
    """Create a GitHub Issue for a new module."""
    body = f"""## Module: {module_name}

### Description
Implementation of the {module_name} module (added during orchestration).

### Acceptance Criteria
- [ ] {criteria}

### Priority
{priority}

### Related
- Plan ID: {plan_id}
- Added during: Orchestration Phase
"""

    labels = f"module,priority:{priority},status:todo"

    try:
        result = subprocess.run(
            [
                "gh", "issue", "create",
                "--title", f"[Module] {module_name}",
                "--body", body,
                "--label", labels
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            output = result.stdout.strip()
            if "/issues/" in output:
                return f"#{output.split('/issues/')[-1]}"
        else:
            print(f"Warning: GitHub Issue creation failed: {result.stderr}")
        return None
    except Exception as e:
        print(f"Warning: Could not create GitHub Issue: {e}")
        return None


def close_github_issue(issue: str | None, comment: str) -> bool:
    """Close a GitHub Issue with a comment."""
    if not issue:
        return False

    try:
        issue_num = issue.replace("#", "")
        result = subprocess.run(
            ["gh", "issue", "close", issue_num, "-c", comment],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Warning: Could not close GitHub Issue: {e}")
        return False


def update_github_issue_labels(
    issue: str | None, old_priority: str | None, new_priority: str
) -> bool:
    """Update GitHub Issue labels for priority change."""
    if not issue:
        return False

    try:
        issue_num = issue.replace("#", "")

        # Remove old label if exists
        if old_priority:
            subprocess.run(
                ["gh", "issue", "edit", issue_num,
                 "--remove-label", f"priority:{old_priority}"],
                capture_output=True,
                timeout=10
            )

        # Add new label
        result = subprocess.run(
            ["gh", "issue", "edit", issue_num,
             "--add-label", f"priority:{new_priority}"],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Warning: Could not update GitHub Issue labels: {e}")
        return False


def cmd_add(args: argparse.Namespace, data: dict[str, Any], body: str) -> bool:
    """Add a new module."""
    modules = data.get("modules_status", [])
    module_id = normalize_id(args.name)

    # Check if already exists
    for module in modules:
        if module.get("id") == module_id:
            print(f"ERROR: Module '{module_id}' already exists")
            return False

    # Create GitHub Issue
    plan_id = data.get("plan_id", "unknown")
    issue_num = create_github_issue(args.name, args.criteria, args.priority, plan_id)

    new_module = {
        "id": module_id,
        "name": args.name,
        "status": "pending",
        "assigned_to": None,
        "github_issue": issue_num,
        "pr": None,
        "verification_loops": 0,
        "acceptance_criteria": args.criteria,
        "priority": args.priority
    }

    modules.append(new_module)
    data["modules_status"] = modules
    data["modules_total"] = len(modules)

    print(f"Added module: {module_id}")
    print(f"  Name: {args.name}")
    print(f"  Criteria: {args.criteria}")
    print(f"  Priority: {args.priority}")
    if issue_num:
        print(f"  GitHub Issue: {issue_num}")
    else:
        print("  GitHub Issue: (failed to create)")

    return True


def cmd_modify(args: argparse.Namespace, data: dict[str, Any], body: str) -> bool:
    """Modify an existing module."""
    modules = data.get("modules_status", [])

    for module in modules:
        if module.get("id") == args.module_id:
            status = module.get("status", "pending")
            if status == "complete":
                print("ERROR: Cannot modify completed module")
                return False

            changes = []
            old_priority = module.get("priority")

            if args.name:
                module["name"] = args.name
                changes.append(f"Name: {args.name}")

            if args.criteria:
                module["acceptance_criteria"] = args.criteria
                changes.append("Criteria updated")

            if args.priority:
                module["priority"] = args.priority
                changes.append(f"Priority: {args.priority}")
                # Update GitHub Issue labels
                update_github_issue_labels(
                    module.get("github_issue"), old_priority, args.priority
                )

            if changes:
                print(f"Modified module: {args.module_id}")
                for change in changes:
                    print(f"  {change}")

                if module.get("assigned_to"):
                    print(f"  Agent '{module.get('assigned_to')}' should be notified")

            return True

    print(f"ERROR: Module '{args.module_id}' not found")
    return False


def cmd_remove(args: argparse.Namespace, data: dict[str, Any], body: str) -> bool:
    """Remove a pending module."""
    modules = data.get("modules_status", [])

    for i, module in enumerate(modules):
        if module.get("id") == args.module_id:
            status = module.get("status", "pending")

            if status in ("in-progress", "in_progress", "complete") and not args.force:
                print(f"ERROR: Cannot remove module with status '{status}'")
                return False

            if module.get("assigned_to") and not args.force:
                print(f"ERROR: Module is assigned to '{module.get('assigned_to')}'")
                print("Use --force to remove anyway")
                return False

            # Remove module
            modules.pop(i)
            data["modules_status"] = modules
            data["modules_total"] = len(modules)

            # Remove from active assignments
            assignments = data.get("active_assignments", [])
            data["active_assignments"] = [
                a for a in assignments if a.get("module") != args.module_id
            ]

            print(f"Removed module: {args.module_id}")

            # Close GitHub Issue
            issue = module.get("github_issue")
            if issue:
                if close_github_issue(issue, "Module removed from plan"):
                    print(f"  Closed GitHub Issue: {issue}")
                else:
                    print(f"  Warning: Could not close GitHub Issue {issue}")

            return True

    print(f"ERROR: Module '{args.module_id}' not found")
    return False


def cmd_list(args: argparse.Namespace, data: dict[str, Any], body: str) -> bool:
    """List all modules."""
    modules = data.get("modules_status", [])

    if not modules:
        print("No modules found")
        return True

    print(f"\nModules ({len(modules)} total):\n")
    print(f"{'ID':<25} {'Name':<30} {'Status':<15} {'Priority':<10} {'Issue':<8}")
    print("-" * 90)

    for module in modules:
        print(
            f"{module.get('id', 'N/A'):<25} "
            f"{module.get('name', 'N/A')[:28]:<30} "
            f"{module.get('status', 'N/A'):<15} "
            f"{module.get('priority', 'N/A'):<10} "
            f"{module.get('github_issue', 'N/A'):<8}"
        )

    return True


def cmd_validate(args: argparse.Namespace, data: dict[str, Any], body: str) -> bool:
    """Validate module state consistency."""
    issues = []
    modules = data.get("modules_status", [])
    assignments = data.get("active_assignments", [])

    # Check module count
    if data.get("modules_total") != len(modules):
        issues.append(
            f"Module count mismatch: modules_total={data.get('modules_total')}, "
            f"actual={len(modules)}"
        )

    # Check for duplicate IDs
    ids = [m.get("id") for m in modules]
    if len(ids) != len(set(ids)):
        issues.append("Duplicate module IDs found")

    # Check assignments reference valid modules
    module_ids = set(ids)
    for assignment in assignments:
        if assignment.get("module") not in module_ids:
            issues.append(
                f"Assignment references non-existent module: {assignment.get('module')}"
            )

    # Check assigned modules have corresponding assignments
    assigned_modules = {m.get("id") for m in modules if m.get("assigned_to")}
    assignment_modules = {a.get("module") for a in assignments}
    orphan_assignments = assignment_modules - assigned_modules
    if orphan_assignments:
        issues.append(f"Orphan assignments (no module marked assigned): {orphan_assignments}")

    # Check required fields
    for module in modules:
        if not module.get("id"):
            issues.append(f"Module missing ID: {module}")
        if not module.get("name"):
            issues.append(f"Module {module.get('id')} missing name")
        if not module.get("acceptance_criteria"):
            issues.append(f"Module {module.get('id')} missing acceptance_criteria")

    if issues:
        print("Validation FAILED:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("Validation PASSED")
        print(f"  Modules: {len(modules)}")
        print(f"  Active assignments: {len(assignments)}")
        return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Module operations for EOA orchestration"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new module")
    add_parser.add_argument("name", help="Module name")
    add_parser.add_argument("--criteria", "-c", required=True, help="Acceptance criteria")
    add_parser.add_argument(
        "--priority", "-p",
        choices=["critical", "high", "medium", "low"],
        default="medium",
        help="Priority level"
    )

    # Modify command
    modify_parser = subparsers.add_parser("modify", help="Modify a module")
    modify_parser.add_argument("module_id", help="Module ID to modify")
    modify_parser.add_argument("--name", "-n", help="New name")
    modify_parser.add_argument("--criteria", "-c", help="New acceptance criteria")
    modify_parser.add_argument(
        "--priority", "-p",
        choices=["critical", "high", "medium", "low"],
        help="New priority"
    )

    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a pending module")
    remove_parser.add_argument("module_id", help="Module ID to remove")
    remove_parser.add_argument("--force", "-f", action="store_true", help="Force removal")

    # List command
    subparsers.add_parser("list", help="List all modules")

    # Validate command
    subparsers.add_parser("validate", help="Validate module state")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Check if in orchestration phase
    if not EXEC_STATE_FILE.exists():
        print("ERROR: Not in Orchestration Phase")
        print("State file not found:", EXEC_STATE_FILE)
        return 1

    data, body = parse_frontmatter(EXEC_STATE_FILE)
    if not data:
        print("ERROR: Could not parse orchestration state file")
        return 1

    # Execute command
    commands = {
        "add": cmd_add,
        "modify": cmd_modify,
        "remove": cmd_remove,
        "list": cmd_list,
        "validate": cmd_validate,
    }

    success = commands[args.command](args, data, body)

    # Write state for commands that modify it
    if success and args.command in ("add", "modify", "remove"):
        if not write_state_file(EXEC_STATE_FILE, data, body):
            return 1

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
