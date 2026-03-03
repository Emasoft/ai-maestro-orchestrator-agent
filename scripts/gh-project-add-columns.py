#!/usr/bin/env python3
"""gh-project-add-columns.py - Safely add columns to a GitHub Project V2 Status field.

This script SAFELY adds new columns to an existing GitHub Project V2
by preserving all existing option IDs. This is critical because the
updateProjectV2Field GraphQL mutation REPLACES all options -- if existing
option IDs are not preserved, items lose their column assignments.

Usage:
  ./gh-project-add-columns.py --project <number> --field "Status" --add "Column Name" [--add "Another"]

Options:
  --project <number>   GitHub Project number (required)
  --field <name>       Field name to modify (default: "Status")
  --add <name>         Column name to add (can be repeated)
  --owner <name>       GitHub owner/org (default: from GITHUB_OWNER env or "Emasoft")
  --dry-run            Show what would be done without making changes

Environment Variables:
  GITHUB_OWNER - Repository owner (default: "Emasoft")

Exit Codes:
  0 - Success
  1 - Error (missing arguments, API failure, verification failed)
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys


def run_gh(*args: str, input_data: str | None = None) -> str:
    """Run a gh CLI command and return its stdout. Raises on failure."""
    result = subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
        input=input_data,
    )
    if result.returncode != 0:
        # Return combined output so caller can inspect errors
        return result.stdout + result.stderr
    return result.stdout


def error(msg: str) -> None:
    """Print an error message to stderr."""
    print(f"ERROR: {msg}", file=sys.stderr)


def main() -> int:
    # Check gh CLI is available
    if shutil.which("gh") is None:
        error("gh CLI not found on PATH. Install it from https://cli.github.com/")
        return 1

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Safely add columns to a GitHub Project V2 single-select field.",
    )
    parser.add_argument(
        "--project",
        type=int,
        required=True,
        help="GitHub Project number",
    )
    parser.add_argument(
        "--field",
        default="Status",
        help='Field name to modify (default: "Status")',
    )
    parser.add_argument(
        "--add",
        action="append",
        required=True,
        dest="new_columns",
        metavar="COLUMN",
        help="Column name to add (can be repeated)",
    )
    parser.add_argument(
        "--owner",
        default=os.environ.get("GITHUB_OWNER", "Emasoft"),
        help='GitHub owner/org (default: from GITHUB_OWNER env or "Emasoft")',
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    args = parser.parse_args()

    project_number: int = args.project
    field_name: str = args.field
    new_columns: list[str] = args.new_columns
    owner: str = args.owner
    dry_run: bool = args.dry_run

    # Pre-flight check: verify gh auth has project scopes
    auth_output = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
        text=True,
    )
    auth_combined = auth_output.stdout + auth_output.stderr
    if "project" not in auth_combined:
        error("gh auth is missing 'project' scope.")
        error("A human must run: gh auth refresh -h github.com -s project,read:project")
        return 1

    print(f"Querying project #{project_number} field '{field_name}'...")

    # Step 1: Query existing field options with their IDs
    query = """
  query($owner: String!, $number: Int!) {
    user(login: $owner) {
      projectV2(number: $number) {
        id
        fields(first: 20) {
          nodes {
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
    raw = run_gh(
        "api", "graphql",
        "-f", f"query={query}",
        "-f", f"owner={owner}",
        "-F", f"number={project_number}",
    )

    try:
        field_data = json.loads(raw)
    except json.JSONDecodeError:
        error(f"Failed to parse GraphQL response:\n{raw}")
        return 1

    # Check for GraphQL-level errors
    if "errors" in field_data and field_data["errors"]:
        error("GraphQL query failed:")
        print(json.dumps(field_data["errors"], indent=2), file=sys.stderr)
        return 1

    # Extract the field info -- find the matching single-select field
    nodes = field_data.get("data", {}).get("user", {}).get("projectV2", {}).get("fields", {}).get("nodes", [])
    field_json: dict | None = None
    for node in nodes:
        if node.get("name") == field_name and "options" in node:
            field_json = node
            break

    if field_json is None:
        error(f"Field '{field_name}' not found or is not a single-select field")
        return 1

    field_id: str = field_json["id"]
    existing_options: list[dict] = field_json["options"]
    existing_count = len(existing_options)

    print(f"Found field '{field_name}' (ID: {field_id}) with {existing_count} existing columns:")
    for opt in existing_options:
        print(f"  - {opt['name']}")

    # Step 2: Check for duplicates and build new options lists
    existing_names = {opt["name"] for opt in existing_options}
    skipped: list[str] = []
    to_add: list[str] = []

    for new_col in new_columns:
        if new_col in existing_names:
            skipped.append(new_col)
        else:
            to_add.append(new_col)

    if skipped:
        print()
        print("Skipping (already exist):")
        for s in skipped:
            print(f"  - {s}")

    if not to_add:
        print()
        print("All requested columns already exist. Nothing to do.")
        return 0

    print()
    print("Adding new columns:")
    for a in to_add:
        print(f"  + {a}")

    # Step 3: Build the complete options array (existing with IDs + new without IDs)
    options_json: list[dict] = [{"id": opt["id"], "name": opt["name"]} for opt in existing_options]
    for new_col in to_add:
        options_json.append({"name": new_col})

    total_count = len(options_json)
    print()
    print(f"Total columns after update: {total_count}")

    if dry_run:
        print()
        print("[DRY RUN] Would send mutation with these options:")
        print(json.dumps(options_json, indent=2))
        print("[DRY RUN] No changes made.")
        return 0

    # Step 4: Execute the updateProjectV2Field mutation
    print()
    print("Executing updateProjectV2Field mutation...")

    mutation_query = """mutation($fieldId: ID!, $name: String!, $options: [ProjectV2SingleSelectFieldOptionInput!]!) {
    updateProjectV2Field(input: {
      fieldId: $fieldId
      name: $name
      singleSelectOptions: $options
    }) {
      projectV2Field {
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
  }"""

    # Build the full GraphQL request body (gh api graphql does not support --argjson)
    request_body = json.dumps({
        "query": mutation_query,
        "variables": {
            "fieldId": field_id,
            "name": field_name,
            "options": options_json,
        },
    })

    mutation_raw = run_gh("api", "graphql", "--input", "-", input_data=request_body)

    try:
        mutation_result = json.loads(mutation_raw)
    except json.JSONDecodeError:
        error(f"Failed to parse mutation response:\n{mutation_raw}")
        return 1

    if "errors" in mutation_result and mutation_result["errors"]:
        error("Mutation failed:")
        print(json.dumps(mutation_result["errors"], indent=2), file=sys.stderr)
        return 1

    # Step 5: Verify existing assignments survived
    print("Verifying existing columns preserved...")

    updated_field = mutation_result.get("data", {}).get("updateProjectV2Field", {}).get("projectV2Field", {})
    updated_options: list[dict] = updated_field.get("options", [])
    updated_count = len(updated_options)

    print(f"Updated field has {updated_count} columns:")
    for opt in updated_options:
        print(f"  - {opt['name']}")

    # Verify all existing option IDs are still present
    updated_ids = {opt["id"] for opt in updated_options}
    preserved = True
    for old_opt in existing_options:
        if old_opt["id"] not in updated_ids:
            print(
                f"WARNING: Existing column '{old_opt['name']}' (ID: {old_opt['id']}) was NOT preserved!",
                file=sys.stderr,
            )
            preserved = False

    if preserved:
        print()
        print(f"SUCCESS: All existing columns preserved. {len(to_add)} new column(s) added.")
        return 0
    else:
        print()
        print("WARNING: Some existing columns may have lost their assignments. Check the board!", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
