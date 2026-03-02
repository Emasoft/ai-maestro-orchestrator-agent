#!/usr/bin/env python3
"""
EOA Modify Module Script

Handles add, modify, and remove operations for modules during
Orchestration Phase. Supports dynamic flexibility.

Usage:
    python3 eoa_modify_module.py add "Password Reset" --criteria "Reset via email"
    python3 eoa_modify_module.py modify auth-core --priority critical
    python3 eoa_modify_module.py remove legacy-api
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

import yaml

# State file location
EXEC_STATE_FILE = Path(".claude/orchestrator-exec-phase.local.md")


def parse_frontmatter(file_path: Path) -> tuple[dict, str]:
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
    body = content[end_index + 3 :].strip()

    try:
        data = yaml.safe_load(yaml_content) or {}
        return data, body
    except yaml.YAMLError:
        return {}, content


def write_state_file(file_path: Path, data: dict, body: str) -> bool:
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

    labels = f"module,priority-{priority},status-todo"

    try:
        result = subprocess.run(
            [
                "gh",
                "issue",
                "create",
                "--title",
                f"[Module] {module_name}",
                "--body",
                body,
                "--label",
                labels,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            output = result.stdout.strip()
            if "/issues/" in output:
                return f"#{output.split('/issues/')[-1]}"
        return None
    except Exception:
        return None


def add_module(data: dict, name: str, criteria: str, priority: str) -> bool:
    """Add a new module during orchestration."""
    modules = data.get("modules_status", [])
    module_id = normalize_id(name)

    # Check if already exists
    for module in modules:
        if module.get("id") == module_id:
            print(f"ERROR: Module '{module_id}' already exists")
            return False

    # Create GitHub Issue
    plan_id = data.get("plan_id", "unknown")
    issue_num = create_github_issue(name, criteria, priority, plan_id)

    new_module = {
        "id": module_id,
        "name": name,
        "status": "pending",
        "assigned_to": None,
        "github_issue": issue_num,
        "pr": None,
        "verification_loops": 0,
        "acceptance_criteria": criteria,
        "priority": priority,
    }

    modules.append(new_module)
    data["modules_status"] = modules
    data["modules_total"] = len(modules)

    print(f"✓ Added module: {module_id}")
    print(f"  Name: {name}")
    print(f"  Criteria: {criteria}")
    print(f"  Priority: {priority}")
    if issue_num:
        print(f"  GitHub Issue: {issue_num}")
    else:
        print("  GitHub Issue: (failed to create)")

    return True


def modify_module(
    data: dict,
    module_id: str,
    new_name: str | None,
    new_criteria: str | None,
    new_priority: str | None,
) -> bool:
    """Modify an existing module."""
    modules = data.get("modules_status", [])

    for module in modules:
        if module.get("id") == module_id:
            # Check if can be modified
            status = module.get("status", "pending")
            if status == "complete":
                print("ERROR: Cannot modify completed module")
                return False

            changes = []
            if new_name:
                module["name"] = new_name
                changes.append(f"Name: {new_name}")
            if new_criteria:
                module["acceptance_criteria"] = new_criteria
                changes.append("Criteria updated")
            if new_priority:
                module["priority"] = new_priority
                changes.append(f"Priority: {new_priority}")

            if changes:
                print(f"✓ Modified module: {module_id}")
                for change in changes:
                    print(f"  {change}")

                # Notify if assigned (would need to implement notification)
                if module.get("assigned_to"):
                    print(f"  ⚠ Agent '{module.get('assigned_to')}' should be notified")

            return True

    print(f"ERROR: Module '{module_id}' not found")
    return False


def remove_module(data: dict, module_id: str, force: bool) -> bool:
    """Remove a pending module."""
    modules = data.get("modules_status", [])

    for i, module in enumerate(modules):
        if module.get("id") == module_id:
            status = module.get("status", "pending")

            if status in ("in-progress", "in_progress", "complete") and not force:
                print(f"ERROR: Cannot remove module with status '{status}'")
                return False

            if module.get("assigned_to") and not force:
                print(f"ERROR: Module is assigned to '{module.get('assigned_to')}'")
                print("Use --force to remove anyway")
                return False

            modules.pop(i)
            data["modules_status"] = modules
            data["modules_total"] = len(modules)

            # Also remove from active assignments
            assignments = data.get("active_assignments", [])
            data["active_assignments"] = [
                a for a in assignments if a.get("module") != module_id
            ]

            print(f"✓ Removed module: {module_id}")

            # Close GitHub Issue
            issue = module.get("github_issue")
            if issue:
                try:
                    issue_num = issue.replace("#", "")
                    subprocess.run(
                        [
                            "gh",
                            "issue",
                            "close",
                            issue_num,
                            "-c",
                            "Module removed from plan",
                        ],
                        capture_output=True,
                        timeout=10,
                    )
                    print(f"  Closed GitHub Issue: {issue}")
                except Exception:
                    print(f"  Warning: Could not close GitHub Issue {issue}")

            return True

    print(f"ERROR: Module '{module_id}' not found")
    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Add, modify, or remove modules during orchestration"
    )
    parser.add_argument(
        "action", choices=["add", "modify", "remove"], help="Action to perform"
    )
    parser.add_argument(
        "name_or_id", help="Module name (for add) or ID (for modify/remove)"
    )
    parser.add_argument("--criteria", "-c", help="Acceptance criteria")
    parser.add_argument(
        "--priority",
        "-p",
        choices=["critical", "high", "medium", "low"],
        default="medium",
    )
    parser.add_argument("--name", "-n", help="New name (for modify)")
    parser.add_argument(
        "--force", "-f", action="store_true", help="Force the operation"
    )

    args = parser.parse_args()

    # Check if in orchestration phase
    if not EXEC_STATE_FILE.exists():
        print("ERROR: Not in Orchestration Phase")
        return 1

    data, body = parse_frontmatter(EXEC_STATE_FILE)
    if not data:
        print("ERROR: Could not parse orchestration state file")
        return 1

    success = False

    if args.action == "add":
        if not args.criteria:
            print("ERROR: --criteria is required for add")
            return 1
        success = add_module(data, args.name_or_id, args.criteria, args.priority)

    elif args.action == "modify":
        success = modify_module(
            data,
            args.name_or_id,
            args.name,
            args.criteria,
            args.priority if args.priority != "medium" else None,
        )

    elif args.action == "remove":
        success = remove_module(data, args.name_or_id, args.force)

    if success:
        if not write_state_file(EXEC_STATE_FILE, data, body):
            return 1

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
