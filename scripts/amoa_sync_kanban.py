#!/usr/bin/env python3
"""
EOA Sync Kanban Script

Synchronizes modules with GitHub Projects kanban board.
Reads active modules from orchestration state and updates GitHub Project items.

Usage:
    python3 eoa_sync_kanban.py
    python3 eoa_sync_kanban.py --project-id PVT_kwDOBxxxxxx
    python3 eoa_sync_kanban.py --dry-run
    python3 eoa_sync_kanban.py --create-missing
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

import yaml

# State file location
EXEC_STATE_FILE = Path(".claude/orchestrator-exec-phase.local.md")

# Status to column mapping
STATUS_TO_COLUMN = {
    "backlog": "Backlog",
    "todo": "Todo",
    "assigned": "In Progress",
    "in-progress": "In Progress",
    "ai-review": "AI Review",
    "human-review": "Human Review",
    "merge-release": "Merge/Release",
    "blocked": "Blocked",
    "done": "Done",
    "complete": "Done",
}

# Priority field values
PRIORITY_VALUES = {
    "critical": "Critical",
    "high": "High",
    "medium": "Medium",
    "low": "Low",
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
    body = content[end_index + 3 :].strip()

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


def gh_command(args: list[str], timeout: int = 30) -> tuple[bool, str]:
    """Execute a gh command and return (success, output)."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except FileNotFoundError:
        return False, "gh CLI not found"
    except Exception as e:
        return False, str(e)


def get_project_items(project_id: str) -> list[dict[str, Any]]:
    """Get all items from a GitHub Project."""
    query = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          items(first: 100) {
            nodes {
              id
              content {
                ... on Issue {
                  number
                  title
                }
                ... on DraftIssue {
                  title
                }
              }
              fieldValues(first: 10) {
                nodes {
                  ... on ProjectV2ItemFieldTextValue {
                    text
                    field { ... on ProjectV2Field { name } }
                  }
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    name
                    field { ... on ProjectV2SingleSelectField { name } }
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    success, output = gh_command(
        [
            "api",
            "graphql",
            "-f",
            f"query={query}",
            "-f",
            f"projectId={project_id}",
        ]
    )

    if not success:
        print(f"ERROR: Failed to get project items: {output}")
        return []

    try:
        data = json.loads(output)
        items = data.get("data", {}).get("node", {}).get("items", {}).get("nodes", [])
        return cast(list[dict[str, Any]], items)
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON response: {output}")
        return []


def get_project_fields(project_id: str) -> dict[str, Any]:
    """Get project field IDs for Status and Priority."""
    query = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          fields(first: 20) {
            nodes {
              ... on ProjectV2Field {
                id
                name
              }
              ... on ProjectV2SingleSelectField {
                id
                name
                options {
                  id
                  name
                }
              }
            }
          }
        }
      }
    }
    """

    success, output = gh_command(
        [
            "api",
            "graphql",
            "-f",
            f"query={query}",
            "-f",
            f"projectId={project_id}",
        ]
    )

    if not success:
        return {}

    try:
        data = json.loads(output)
        fields = data.get("data", {}).get("node", {}).get("fields", {}).get("nodes", [])

        field_map = {}
        for field in fields:
            name = field.get("name", "")
            if name in ["Status", "Priority"]:
                field_map[name] = {
                    "id": field.get("id"),
                    "options": {
                        opt["name"]: opt["id"] for opt in field.get("options", [])
                    },
                }

        return field_map
    except json.JSONDecodeError:
        return {}


def create_project_item(project_id: str, title: str, body: str = "") -> str | None:
    """Create a draft issue in the project."""
    mutation = """
    mutation($projectId: ID!, $title: String!, $body: String) {
      addProjectV2DraftIssue(input: {projectId: $projectId, title: $title, body: $body}) {
        projectItem {
          id
        }
      }
    }
    """

    success, output = gh_command(
        [
            "api",
            "graphql",
            "-f",
            f"query={mutation}",
            "-f",
            f"projectId={project_id}",
            "-f",
            f"title={title}",
            "-f",
            f"body={body}",
        ]
    )

    if not success:
        print(f"ERROR: Failed to create project item: {output}")
        return None

    try:
        data = json.loads(output)
        item_id = (
            data.get("data", {})
            .get("addProjectV2DraftIssue", {})
            .get("projectItem", {})
            .get("id")
        )
        return cast(str | None, item_id)
    except json.JSONDecodeError:
        return None


def update_project_item_field(
    project_id: str, item_id: str, field_id: str, option_id: str
) -> bool:
    """Update a single select field on a project item."""
    mutation = """
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $projectId,
        itemId: $itemId,
        fieldId: $fieldId,
        value: { singleSelectOptionId: $optionId }
      }) {
        projectV2Item {
          id
        }
      }
    }
    """

    success, _ = gh_command(
        [
            "api",
            "graphql",
            "-f",
            f"query={mutation}",
            "-f",
            f"projectId={project_id}",
            "-f",
            f"itemId={item_id}",
            "-f",
            f"fieldId={field_id}",
            "-f",
            f"optionId={option_id}",
        ]
    )

    return success


def find_item_by_title(
    items: list[dict[str, Any]], title: str
) -> dict[str, Any] | None:
    """Find a project item by title."""
    for item in items:
        content = item.get("content", {})
        item_title = content.get("title", "")
        if item_title == title:
            return item
    return None


def sync_module_to_project(
    module: dict[str, Any],
    project_id: str,
    items: list[dict[str, Any]],
    fields: dict[str, Any],
    dry_run: bool = False,
    create_missing: bool = False,
) -> dict[str, Any]:
    """Sync a single module to the project."""
    module_id = module.get("id", "")
    module_name = module.get("name", module_id)
    status = module.get("status", "todo")
    priority = module.get("priority", "medium")

    # Create title for project item
    title = f"[{module_id}] {module_name}"

    result = {
        "module_id": module_id,
        "title": title,
        "status": status,
        "priority": priority,
        "action": "none",
        "success": True,
    }

    # Find existing item
    existing_item = find_item_by_title(items, title)

    if existing_item:
        result["item_id"] = existing_item.get("id")
        result["action"] = "update"

        if dry_run:
            result["dry_run"] = True
            return result

        # Update status
        status_field = fields.get("Status", {})
        if status_field:
            column = STATUS_TO_COLUMN.get(status, "Todo")
            option_id = status_field.get("options", {}).get(column)
            if option_id:
                update_project_item_field(
                    project_id,
                    existing_item["id"],
                    status_field["id"],
                    option_id,
                )

        # Update priority
        priority_field = fields.get("Priority", {})
        if priority_field:
            priority_value = PRIORITY_VALUES.get(priority, "Medium")
            option_id = priority_field.get("options", {}).get(priority_value)
            if option_id:
                update_project_item_field(
                    project_id,
                    existing_item["id"],
                    priority_field["id"],
                    option_id,
                )

    elif create_missing:
        result["action"] = "create"

        if dry_run:
            result["dry_run"] = True
            return result

        # Create body with module details
        body_lines = [
            f"**Module ID:** {module_id}",
            f"**Priority:** {priority}",
            "",
        ]
        if module.get("dependencies"):
            body_lines.append(f"**Dependencies:** {', '.join(module['dependencies'])}")
        if module.get("description"):
            body_lines.append(f"\n{module['description']}")

        body = "\n".join(body_lines)

        # Create item
        item_id = create_project_item(project_id, title, body)
        if item_id:
            result["item_id"] = item_id

            # Update fields
            status_field = fields.get("Status", {})
            if status_field:
                column = STATUS_TO_COLUMN.get(status, "Todo")
                option_id = status_field.get("options", {}).get(column)
                if option_id:
                    update_project_item_field(
                        project_id, item_id, status_field["id"], option_id
                    )

            priority_field = fields.get("Priority", {})
            if priority_field:
                priority_value = PRIORITY_VALUES.get(priority, "Medium")
                option_id = priority_field.get("options", {}).get(priority_value)
                if option_id:
                    update_project_item_field(
                        project_id, item_id, priority_field["id"], option_id
                    )
        else:
            result["success"] = False
            result["error"] = "Failed to create item"
    else:
        result["action"] = "missing"
        result["message"] = "Item not found (use --create-missing to create)"

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync modules with GitHub Projects kanban"
    )
    parser.add_argument(
        "--project-id", help="GitHub Project ID (e.g., PVT_kwDOBxxxxxx)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be synced"
    )
    parser.add_argument(
        "--create-missing", action="store_true", help="Create missing project items"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Load orchestration state
    if not EXEC_STATE_FILE.exists():
        if args.json:
            print(
                json.dumps(
                    {"success": False, "error": "Orchestration state file not found"}
                )
            )
        else:
            print("ERROR: Orchestration state file not found")
            print("Run /start-orchestration first")
        return 1

    exec_data, body = parse_frontmatter(EXEC_STATE_FILE)

    # Get project ID
    project_id = args.project_id or exec_data.get("github_project_id")
    if not project_id:
        if args.json:
            print(json.dumps({"success": False, "error": "No project ID provided"}))
        else:
            print("ERROR: No GitHub Project ID provided")
            print("Use --project-id or set github_project_id in state file")
        return 1

    # Get modules
    modules = exec_data.get("modules", [])
    if not modules:
        if args.json:
            print(
                json.dumps(
                    {"success": True, "message": "No modules to sync", "synced": 0}
                )
            )
        else:
            print("No modules to sync")
        return 0

    # Get project fields
    if not args.dry_run:
        fields = get_project_fields(project_id)
        if not fields:
            if args.json:
                print(
                    json.dumps(
                        {"success": False, "error": "Could not get project fields"}
                    )
                )
            else:
                print("ERROR: Could not get project fields")
                print("Make sure you have access to the project")
            return 1

        # Get existing items
        items = get_project_items(project_id)
    else:
        fields = {}
        items = []

    # Sync each module
    results = []
    for module in modules:
        result = sync_module_to_project(
            module=module,
            project_id=project_id,
            items=items,
            fields=fields,
            dry_run=args.dry_run,
            create_missing=args.create_missing,
        )
        results.append(result)

    # Update state file with sync timestamp
    if not args.dry_run:
        exec_data["last_kanban_sync"] = datetime.now(timezone.utc).isoformat()
        write_state_file(EXEC_STATE_FILE, exec_data, body)

    # Output results
    output = {
        "success": True,
        "project_id": project_id,
        "dry_run": args.dry_run,
        "total_modules": len(modules),
        "results": results,
        "summary": {
            "updated": len([r for r in results if r["action"] == "update"]),
            "created": len([r for r in results if r["action"] == "create"]),
            "missing": len([r for r in results if r["action"] == "missing"]),
            "failed": len([r for r in results if not r["success"]]),
        },
    }

    if args.json:
        print(json.dumps(output, indent=2))
    else:
        print(f"Kanban sync {'(dry run)' if args.dry_run else 'complete'}")
        print(f"  Project: {project_id}")
        print(f"  Total modules: {len(modules)}")
        print(f"  Updated: {output['summary']['updated']}")
        print(f"  Created: {output['summary']['created']}")
        print(f"  Missing: {output['summary']['missing']}")
        if output["summary"]["failed"]:
            print(f"  Failed: {output['summary']['failed']}")

        if output["summary"]["missing"] > 0 and not args.create_missing:
            print()
            print("Use --create-missing to create missing items")

    return 0 if output["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
