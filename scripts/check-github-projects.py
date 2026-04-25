#!/usr/bin/env python3
"""check-github-projects.py - Query GitHub Projects V2 API for pending items.

This script is called by the orchestrator stop hook (tasks.py) to check
if there are pending tasks on the GitHub Project board.

Usage:
    ./check-github-projects.py [--project PROJECT_NUMBER]

Environment Variables:
    GITHUB_PROJECT_NUMBER - Project number (alternative to --project flag)
    GITHUB_OWNER         - Repository owner (optional, auto-detected from git)
    REPO_NAME            - Repository name (optional, auto-detected from git)
    CLAUDE_PROJECT_DIR   - Project directory (optional, for .github/project.json lookup)

Output (JSON):
    {
        "available": true|false,
        "pending_count": N,
        "tasks": [{"id": "...", "title": "...", "status": "...", "assignee": "..."}],
        "error": ""
    }

Exit Codes:
    0 - Success (JSON output on stdout)
    0 - Error (JSON output with error field set)
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

# Statuses considered "pending" / active work
PENDING_STATUSES = frozenset({
    "In Progress",
    "AI Review",
    "Human Review",
    "Merge/Release",
    "Blocked",
})

# GraphQL query for user-owned projects
USER_QUERY = """
query($owner: String!, $number: Int!) {
  user(login: $owner) {
    projectV2(number: $number) {
      items(first: 100) {
        nodes {
          id
          content {
            ... on Issue {
              title
              number
              assignees(first: 1) {
                nodes {
                  login
                }
              }
            }
            ... on DraftIssue {
              title
            }
            ... on PullRequest {
              title
              number
            }
          }
          fieldValues(first: 10) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field {
                  ... on ProjectV2SingleSelectField {
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""

# GraphQL query for organization-owned projects
ORG_QUERY = """
query($owner: String!, $number: Int!) {
  organization(login: $owner) {
    projectV2(number: $number) {
      items(first: 100) {
        nodes {
          id
          content {
            ... on Issue {
              title
              number
              assignees(first: 1) {
                nodes {
                  login
                }
              }
            }
            ... on DraftIssue {
              title
            }
            ... on PullRequest {
              title
              number
            }
          }
          fieldValues(first: 10) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field {
                  ... on ProjectV2SingleSelectField {
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""


def output_json(
    available: bool,
    pending_count: int,
    tasks: list[dict],
    error: str,
) -> str:
    """Build the standard JSON output string."""
    return json.dumps({
        "available": available,
        "pending_count": pending_count,
        "tasks": tasks,
        "error": error,
    })


def output_error(error_msg: str) -> NoReturn:
    """Print a JSON error envelope and exit 0 (matches bash behaviour)."""
    print(output_json(available=False, pending_count=0, tasks=[], error=error_msg))
    sys.exit(0)


def run_gh(*args: str) -> subprocess.CompletedProcess[str]:
    """Run a gh CLI command, capturing stdout/stderr."""
    return subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
    )


def read_project_number_from_config(config_path: Path) -> str:
    """Try to read project_number or number from a .github/project.json file."""
    if not config_path.is_file():
        return ""
    try:
        data = json.loads(config_path.read_text())
        # Mirror jq: .project_number // .number // empty
        value = data.get("project_number") or data.get("number")
        return str(value) if value else ""
    except (json.JSONDecodeError, OSError):
        return ""


def determine_project_number(cli_value: str | None) -> str:
    """Resolve the project number from CLI flag, env vars, or config files."""
    # 1. CLI argument
    if cli_value:
        return cli_value

    # 2. Environment variable
    env_val = os.environ.get("GITHUB_PROJECT_NUMBER", "")
    if env_val:
        return env_val

    # 3. .github/project.json in cwd
    number = read_project_number_from_config(Path(".github/project.json"))
    if number:
        return number

    # 4. .github/project.json under CLAUDE_PROJECT_DIR
    claude_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if claude_dir:
        number = read_project_number_from_config(
            Path(claude_dir) / ".github" / "project.json"
        )
        if number:
            return number

    return ""


def determine_owner() -> str:
    """Resolve the repository owner from env var or gh CLI."""
    owner = os.environ.get("GITHUB_OWNER", "")
    if owner:
        return owner

    # Try to get from git remote via gh
    result = run_gh("repo", "view", "--json", "owner", "-q", ".owner.login")
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()

    return ""


def run_graphql_query(query: str, owner: str, number: str) -> dict | None:
    """Execute a GraphQL query via gh api and return parsed JSON, or None on failure."""
    result = run_gh(
        "api", "graphql",
        "-f", f"query={query}",
        "-F", f"owner={owner}",
        "-F", f"number={number}",
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def extract_items(data: dict, entity_key: str) -> list[dict] | None:
    """Drill into the GraphQL response to get project item nodes.

    entity_key is either "user" or "organization".
    Returns None if the path doesn't exist or projectV2 is null.
    """
    entity = (data.get("data") or {}).get(entity_key)
    if not entity:
        return None
    project = entity.get("projectV2")
    if project is None:
        return None
    items = (project.get("items") or {}).get("nodes")
    return items  # may be [] which is valid


def get_status(item: dict) -> str | None:
    """Extract the Status field value from an item's fieldValues."""
    for fv in (item.get("fieldValues") or {}).get("nodes") or []:
        field = fv.get("field") or {}
        if field.get("name") == "Status":
            return fv.get("name")
    return None


def get_assignee(item: dict) -> str:
    """Extract the first assignee login, or 'unassigned'."""
    content = item.get("content") or {}
    assignees = (content.get("assignees") or {}).get("nodes") or []
    if assignees and assignees[0].get("login"):
        return assignees[0]["login"]
    return "unassigned"


def get_title(item: dict) -> str:
    """Extract the title from the content, defaulting to 'Draft Issue'."""
    content = item.get("content") or {}
    return content.get("title") or "Draft Issue"


def filter_pending_tasks(items: list[dict]) -> list[dict]:
    """Filter items to those with a pending status and format them."""
    tasks: list[dict] = []
    for item in items:
        status = get_status(item)
        if status and status in PENDING_STATUSES:
            tasks.append({
                "id": item.get("id", ""),
                "title": get_title(item),
                "status": status,
                "assignee": get_assignee(item),
            })
    return tasks


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Query GitHub Projects V2 API for pending items.",
    )
    parser.add_argument(
        "--project",
        dest="project_number",
        default=None,
        help="GitHub Project number",
    )
    args = parser.parse_args()

    # --- Pre-flight checks ---

    if not shutil.which("gh"):
        output_error("gh CLI not installed")

    # Check gh authentication
    auth_result = run_gh("auth", "status")
    if auth_result.returncode != 0:
        output_error("gh CLI not authenticated")

    # --- Resolve configuration ---

    project_number = determine_project_number(args.project_number)
    if not project_number:
        output_error(
            "No project configured "
            "(set GITHUB_PROJECT_NUMBER or create .github/project.json)"
        )

    owner = determine_owner()
    if not owner:
        output_error("Cannot determine repository owner")

    # --- Query GitHub Projects API ---

    # Try user query first
    result = run_graphql_query(USER_QUERY, owner, project_number)
    items = None
    if result is not None:
        items = extract_items(result, "user")

    # Fall back to organization query
    if items is None:
        result = run_graphql_query(ORG_QUERY, owner, project_number)
        if result is None:
            output_error("Failed to query GitHub Projects API")
        items = extract_items(result, "organization")

    if items is None:
        output_error("Project not found or no access")

    # --- Filter and format ---

    pending_tasks = filter_pending_tasks(items)
    pending_count = len(pending_tasks)
    # Limit to first 5 tasks for the output (matches bash behaviour)
    sample_tasks = pending_tasks[:5]

    print(output_json(
        available=True,
        pending_count=pending_count,
        tasks=sample_tasks,
        error="",
    ))


if __name__ == "__main__":
    main()
