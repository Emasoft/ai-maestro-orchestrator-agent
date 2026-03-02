#!/usr/bin/env python3
"""
EOA Create Module Issues Script

Creates GitHub issues for modules from orchestration state.
Updates module records with issue numbers.
Optionally adds issues to GitHub Project.

Usage:
    python3 eoa_create_module_issues.py
    python3 eoa_create_module_issues.py --module auth-core
    python3 eoa_create_module_issues.py --all --project-id PVT_kwDOBxxxxxx
    python3 eoa_create_module_issues.py --dry-run
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

# Issue labels
DEFAULT_LABELS = ["module", "orchestration"]

# Priority to label mapping
PRIORITY_LABELS = {
    "critical": "priority-critical",
    "high": "priority-high",
    "medium": "priority-medium",
    "low": "priority-low",
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
        yaml_content = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
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


def create_issue(
    title: str,
    body: str,
    labels: list[str],
) -> tuple[str | None, str | None]:
    """Create a GitHub issue and return (issue_number, issue_url)."""
    args = [
        "issue", "create",
        "--title", title,
        "--body", body,
    ]

    for label in labels:
        args.extend(["--label", label])

    success, output = gh_command(args)

    if not success:
        print(f"ERROR: Failed to create issue: {output}")
        return None, None

    # Output is the issue URL
    issue_url = output
    # Extract issue number from URL
    if "/" in issue_url:
        issue_number = issue_url.split("/")[-1]
        return issue_number, issue_url

    return None, None


def add_issue_to_project(project_id: str, issue_url: str) -> bool:
    """Add an issue to a GitHub Project."""
    success, _ = gh_command([
        "project", "item-add", project_id,
        "--owner", "@me",
        "--url", issue_url,
    ])

    return success


def ensure_labels_exist(labels: list[str]) -> list[str]:
    """Ensure labels exist, create if missing. Return list of existing labels."""
    existing = []

    for label in labels:
        success, _ = gh_command(["label", "list", "--search", label, "--json", "name"])
        if success:
            existing.append(label)
        else:
            # Try to create the label
            color = "0052CC"  # Default blue
            if "critical" in label:
                color = "B60205"
            elif "high" in label:
                color = "D93F0B"
            elif "medium" in label:
                color = "FBCA04"
            elif "low" in label:
                color = "0E8A16"

            gh_command(["label", "create", label, "--color", color])
            existing.append(label)

    return existing


def build_issue_body(module: dict[str, Any]) -> str:
    """Build the issue body from module data."""
    lines = [
        "## Module Information",
        "",
        f"**Module ID:** {module.get('id', 'N/A')}",
        f"**Priority:** {module.get('priority', 'medium')}",
        f"**Status:** {module.get('status', 'todo')}",
        "",
    ]

    if module.get("dependencies"):
        lines.append(f"**Dependencies:** {', '.join(module['dependencies'])}")
        lines.append("")

    if module.get("description"):
        lines.extend([
            "## Description",
            "",
            module["description"],
            "",
        ])

    if module.get("acceptance_criteria"):
        lines.extend([
            "## Acceptance Criteria",
            "",
        ])
        for criterion in module["acceptance_criteria"]:
            lines.append(f"- [ ] {criterion}")
        lines.append("")

    if module.get("assigned_to"):
        lines.extend([
            "## Assignment",
            "",
            f"**Assigned to:** {module['assigned_to']}",
            "",
        ])

    lines.extend([
        "---",
        "",
        "*This issue was created by the EOA orchestration system.*",
    ])

    return "\n".join(lines)


def create_module_issue(
    module: dict[str, Any],
    project_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Create a GitHub issue for a module."""
    module_id = module.get("id", "")
    module_name = module.get("name", module_id)
    priority = module.get("priority", "medium")

    # Build title
    title = f"[Module] {module_name}"

    # Build labels
    labels = DEFAULT_LABELS.copy()
    if priority in PRIORITY_LABELS:
        labels.append(PRIORITY_LABELS[priority])

    result = {
        "module_id": module_id,
        "title": title,
        "labels": labels,
        "success": False,
    }

    # Check if module already has an issue
    if module.get("github_issue"):
        result["skipped"] = True
        result["message"] = f"Module already has issue #{module['github_issue']}"
        result["success"] = True
        return result

    if dry_run:
        result["dry_run"] = True
        result["success"] = True
        return result

    # Build issue body
    body = build_issue_body(module)

    # Ensure labels exist
    ensure_labels_exist(labels)

    # Create issue
    issue_number, issue_url = create_issue(title, body, labels)

    if issue_number:
        result["success"] = True
        result["issue_number"] = issue_number
        result["issue_url"] = issue_url

        # Add to project if specified
        if project_id and issue_url:
            project_added = add_issue_to_project(project_id, issue_url)
            result["added_to_project"] = project_added
    else:
        result["error"] = "Failed to create issue"

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Create GitHub issues for modules")
    parser.add_argument("--module", "-m", help="Create issue for specific module ID")
    parser.add_argument("--all", action="store_true", help="Create issues for all modules without issues")
    parser.add_argument("--project-id", help="GitHub Project ID to add issues to")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Load orchestration state
    if not EXEC_STATE_FILE.exists():
        if args.json:
            print(json.dumps({"success": False, "error": "Orchestration state file not found"}))
        else:
            print("ERROR: Orchestration state file not found")
            print("Run /start-orchestration first")
        return 1

    exec_data, body = parse_frontmatter(EXEC_STATE_FILE)

    # Get project ID
    project_id = args.project_id or exec_data.get("github_project_id")

    # Get modules
    modules = exec_data.get("modules", [])
    if not modules:
        if args.json:
            print(json.dumps({"success": True, "message": "No modules found", "created": 0}))
        else:
            print("No modules found in orchestration state")
        return 0

    # Filter modules
    if args.module:
        modules = [m for m in modules if m.get("id") == args.module]
        if not modules:
            if args.json:
                print(json.dumps({"success": False, "error": f"Module not found: {args.module}"}))
            else:
                print(f"ERROR: Module not found: {args.module}")
            return 1
    elif args.all:
        # Only modules without issues
        modules = [m for m in modules if not m.get("github_issue")]
    else:
        # Default: show status
        if args.json:
            status = {
                "total_modules": len(modules),
                "with_issues": len([m for m in modules if m.get("github_issue")]),
                "without_issues": len([m for m in modules if not m.get("github_issue")]),
            }
            print(json.dumps(status, indent=2))
        else:
            print("Module issue status:")
            for m in modules:
                issue = m.get("github_issue")
                issue_status = f"#{issue}" if issue else "no issue"
                print(f"  {m.get('id')}: {issue_status}")
            print()
            print("Use --module <id> to create issue for specific module")
            print("Use --all to create issues for all modules without issues")
        return 0

    # Create issues
    results = []
    updated_modules = False

    for module in modules:
        result = create_module_issue(
            module=module,
            project_id=project_id,
            dry_run=args.dry_run,
        )
        results.append(result)

        # Update module in state file
        if result.get("success") and result.get("issue_number") and not args.dry_run:
            for m in exec_data.get("modules", []):
                if m.get("id") == module.get("id"):
                    m["github_issue"] = result["issue_number"]
                    m["github_issue_url"] = result.get("issue_url")
                    updated_modules = True
                    break

    # Save updated state
    if updated_modules:
        write_state_file(EXEC_STATE_FILE, exec_data, body)

    # Output results
    output = {
        "success": True,
        "dry_run": args.dry_run,
        "project_id": project_id,
        "total": len(results),
        "results": results,
        "summary": {
            "created": len([r for r in results if r.get("issue_number")]),
            "skipped": len([r for r in results if r.get("skipped")]),
            "failed": len([r for r in results if not r.get("success")]),
        },
    }

    if args.json:
        print(json.dumps(output, indent=2))
    else:
        print(f"Issue creation {'(dry run)' if args.dry_run else 'complete'}")
        print(f"  Total: {len(results)}")
        print(f"  Created: {output['summary']['created']}")
        print(f"  Skipped: {output['summary']['skipped']}")
        if output["summary"]["failed"]:
            print(f"  Failed: {output['summary']['failed']}")

        if output["summary"]["created"] > 0:
            print()
            print("Created issues:")
            for r in results:
                if r.get("issue_number"):
                    print(f"  {r['module_id']}: #{r['issue_number']}")
                    if r.get("added_to_project"):
                        print("    Added to project")

    return 0 if output["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
