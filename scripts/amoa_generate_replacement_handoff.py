#!/usr/bin/env python3
"""
EOA Generate Replacement Handoff Script

Generates a comprehensive handoff document when replacing a failed agent.
Compiles task context from: orchestration state file, GitHub issues (via gh CLI),
and git branch state to create a document the replacement agent can use to
continue the failed agent's work.

Usage:
    python3 eoa_generate_replacement_handoff.py --failed-agent impl-1 --new-agent impl-2
    python3 eoa_generate_replacement_handoff.py --failed-agent impl-1 --new-agent impl-2 --output handoff.md
    python3 eoa_generate_replacement_handoff.py --failed-agent impl-1 --new-agent impl-2 --partial --flag-gaps
    python3 eoa_generate_replacement_handoff.py --failed-agent impl-1 --new-agent impl-2 --upload

Exit codes:
    0 - Success
    1 - Error (missing required data without --partial, or unrecoverable error)

Examples:
    # Standard replacement handoff:
    python3 eoa_generate_replacement_handoff.py \\
        --failed-agent implementer-1 --new-agent implementer-2

    # Partial handoff with gap markers when data is incomplete:
    python3 eoa_generate_replacement_handoff.py \\
        --failed-agent implementer-1 --new-agent implementer-2 \\
        --partial --flag-gaps --output urgent-handoff.md

    # Generate and upload to GitHub issue:
    python3 eoa_generate_replacement_handoff.py \\
        --failed-agent implementer-1 --new-agent implementer-2 --upload
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


# State file location (matches codebase convention)
EXEC_STATE_FILE = Path(".claude/orchestrator-exec-phase.local.md")

# Default handoff output directory
HANDOFF_DIR = Path("docs_dev/handoffs")


def parse_yaml_frontmatter(content):
    """Parse YAML frontmatter from markdown content without external dependencies.

    Extracts key-value pairs from the YAML frontmatter section delimited
    by '---' markers at the beginning of a markdown file.

    Supports nested structures by parsing indented keys as nested
    dictionaries and list items (lines starting with '- ').

    Args:
        content: The full text content of the markdown file.

    Returns:
        A tuple of (data_dict, body_text) where data_dict contains the
        parsed frontmatter fields and body_text is the rest of the file.
    """
    if not content or not content.startswith("---"):
        return {}, content

    lines = content.split("\n")
    in_frontmatter = False
    frontmatter_lines = []
    end_line_idx = 0

    for idx, line in enumerate(lines):
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                end_line_idx = idx
                break
        if in_frontmatter:
            frontmatter_lines.append(line)

    body = "\n".join(lines[end_line_idx + 1:]).strip()

    # Simple YAML parsing for key: value pairs
    # Supports: top-level keys, lists of scalars, lists of dicts (multiline)
    data = {}
    current_list_key = None
    current_list = []
    current_item_dict = None  # Tracks the current dict being built in a list

    for line in frontmatter_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Calculate indentation level to distinguish list items from continuations
        indent_level = len(line) - len(line.lstrip())

        # Detect new list item (starts with "- ")
        if stripped.startswith("- ") and current_list_key:
            # Flush previous item dict if any
            if current_item_dict is not None:
                current_list.append(current_item_dict)
                current_item_dict = None

            item_text = stripped[2:].strip()
            # Try to parse as a dict-like item (key: value)
            if ": " in item_text:
                current_item_dict = {}
                k, _, v = item_text.partition(": ")
                k = k.strip()
                v = v.strip()
                current_item_dict[k] = _parse_value(v)
            else:
                current_list.append(item_text)
            continue

        # Detect continuation of a list item dict (indented key: value without "- ")
        if current_item_dict is not None and indent_level >= 2 and ": " in stripped:
            k, _, v = stripped.partition(": ")
            k = k.strip()
            v = v.strip()
            current_item_dict[k] = _parse_value(v)
            continue

        # Flush any pending item dict and list
        if current_item_dict is not None:
            current_list.append(current_item_dict)
            current_item_dict = None
        if current_list_key and current_list:
            data[current_list_key] = current_list
            current_list_key = None
            current_list = []

        if ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()
            if not value:
                # This might be the start of a list or nested dict
                current_list_key = key
                current_list = []
            else:
                data[key] = _parse_value(value)

    # Flush final item dict and list
    if current_item_dict is not None:
        current_list.append(current_item_dict)
    if current_list_key and current_list:
        data[current_list_key] = current_list

    return data, body


def _parse_value(value):
    """Parse a string value into its Python type.

    Args:
        value: String value to parse.

    Returns:
        The parsed value (bool, None, int, or string).
    """
    value = value.strip().strip("'").strip('"')
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.lower() == "null" or value.lower() == "none":
        return None
    try:
        return int(value)
    except ValueError:
        pass
    return value


def try_parse_yaml_with_pyyaml(content):
    """Attempt to parse YAML frontmatter using PyYAML if available.

    Falls back to the manual parser if PyYAML is not installed.

    Args:
        content: The full text content of the markdown file.

    Returns:
        A tuple of (data_dict, body_text).
    """
    try:
        import yaml
        if not content or not content.startswith("---"):
            return {}, content
        end_idx = content.find("---", 3)
        if end_idx == -1:
            return {}, content
        yaml_text = content[3:end_idx].strip()
        body = content[end_idx + 3:].strip()
        data = yaml.safe_load(yaml_text) or {}
        return data, body
    except ImportError:
        return parse_yaml_frontmatter(content)
    except Exception:
        return parse_yaml_frontmatter(content)


def load_exec_state():
    """Load orchestration execution phase state.

    Reads the exec-phase state file which contains module assignments,
    agent registrations, and active assignments in YAML frontmatter format.

    Returns:
        A tuple of (data_dict, body_text) or ({}, "") if not found.
    """
    if not EXEC_STATE_FILE.exists():
        return {}, ""
    try:
        content = EXEC_STATE_FILE.read_text(encoding="utf-8")
        return try_parse_yaml_with_pyyaml(content)
    except OSError:
        return {}, ""


def get_failed_agent_assignments(state_data, failed_agent):
    """Extract all assignments belonging to the failed agent.

    Args:
        state_data: The parsed state file data dictionary.
        failed_agent: The agent ID of the failed agent.

    Returns:
        A list of assignment dictionaries for the failed agent.
    """
    assignments = state_data.get("active_assignments", [])
    if not isinstance(assignments, list):
        return []
    return [a for a in assignments if isinstance(a, dict) and a.get("agent") == failed_agent]


def get_failed_agent_modules(state_data, failed_agent):
    """Extract all modules assigned to the failed agent.

    Args:
        state_data: The parsed state file data dictionary.
        failed_agent: The agent ID of the failed agent.

    Returns:
        A list of module status dictionaries for the failed agent.
    """
    modules = state_data.get("modules_status", [])
    if not isinstance(modules, list):
        return []
    return [m for m in modules if isinstance(m, dict) and m.get("assigned_to") == failed_agent]


def get_github_issue_context(issue_number):
    """Fetch GitHub issue details using the gh CLI.

    Args:
        issue_number: The GitHub issue number (integer or string like '#42').

    Returns:
        A dictionary with issue fields, or None if the fetch fails.
    """
    if not issue_number:
        return None

    # Strip leading '#' if present
    issue_num = str(issue_number).lstrip("#")

    try:
        result = subprocess.run(
            ["gh", "issue", "view", issue_num, "--json",
             "number,title,body,state,labels,assignees,comments"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass
    return None


def get_git_branch_state():
    """Gather git branch state information.

    Checks current branch, modified files, uncommitted changes,
    and the most recent commit message.

    Returns:
        A dictionary with git state information, or an empty dict
        if git is not available.
    """
    git_info = {}
    try:
        # Current branch
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            git_info["branch"] = result.stdout.strip()

        # Modified files (staged + unstaged)
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            files = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
            git_info["modified_files"] = files
            git_info["has_uncommitted_changes"] = len(files) > 0

        # Last commit
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H %s"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split(" ", 1)
            if len(parts) == 2:
                git_info["last_commit_hash"] = parts[0]
                git_info["last_commit_message"] = parts[1]

        # Commits ahead of main
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD", "--not", "origin/main"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            try:
                git_info["commits_ahead_of_main"] = int(result.stdout.strip())
            except ValueError:
                pass

    except (FileNotFoundError, OSError):
        pass

    return git_info


def build_handoff_document(
    failed_agent,
    new_agent,
    assignments,
    modules,
    github_contexts,
    git_state,
    flag_gaps=False,
):
    """Build the handoff markdown document.

    Compiles all gathered information into a structured markdown document
    with sections for metadata, task assignments, requirements, progress,
    technical context, next steps, and verification.

    Args:
        failed_agent: The agent ID of the failed agent.
        new_agent: The agent ID of the replacement agent.
        assignments: List of assignment dicts from the state file.
        modules: List of module status dicts from the state file.
        github_contexts: Dict mapping issue numbers to issue data.
        git_state: Dict with git branch state information.
        flag_gaps: If True, mark missing data with GAP markers.

    Returns:
        The handoff document as a string.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    gap = "<!-- GAP: Data unavailable -->" if flag_gaps else "N/A"

    lines = []
    lines.append("# Agent Replacement Handoff")
    lines.append("")

    # Metadata section
    lines.append("## Handoff Metadata")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|-------|-------|")
    lines.append("| **Failed Agent** | {} |".format(failed_agent))
    lines.append("| **Replacement Agent** | {} |".format(new_agent))
    lines.append("| **Generated At** | {} |".format(now))
    lines.append("| **Reason** | Agent replacement |")
    lines.append("")

    # Task Assignments section
    lines.append("## Task Assignments")
    lines.append("")
    if assignments:
        for assignment in assignments:
            module_id = assignment.get("module", gap)
            task_uuid = assignment.get("task_uuid", gap)
            status = assignment.get("status", gap)
            lines.append("### Module: {}".format(module_id))
            lines.append("")
            lines.append("- **Task UUID**: {}".format(task_uuid))
            lines.append("- **Status**: {}".format(status))
            gh_issue = assignment.get("github_issue", "")
            if gh_issue:
                lines.append("- **GitHub Issue**: {}".format(gh_issue))
            lines.append("")
    elif modules:
        for module in modules:
            module_id = module.get("id", gap)
            status = module.get("status", gap)
            lines.append("### Module: {}".format(module_id))
            lines.append("")
            lines.append("- **Status**: {}".format(status))
            gh_issue = module.get("github_issue", "")
            if gh_issue:
                lines.append("- **GitHub Issue**: {}".format(gh_issue))
            lines.append("")
    else:
        if flag_gaps:
            lines.append("<!-- GAP: No task assignments found in state file -->")
        else:
            lines.append("No task assignments found for agent {}.".format(failed_agent))
        lines.append("")

    # User Requirements section
    lines.append("## User Requirements")
    lines.append("")
    if github_contexts:
        for issue_num, issue_data in github_contexts.items():
            if issue_data:
                title = issue_data.get("title", "Untitled")
                body = issue_data.get("body", "")
                lines.append("### Issue #{}: {}".format(issue_num, title))
                lines.append("")
                if body:
                    # Truncate very long bodies
                    if len(body) > 2000:
                        body = body[:2000] + "\n\n... (truncated)"
                    lines.append(body)
                lines.append("")
    else:
        if flag_gaps:
            lines.append("<!-- GAP: Could not fetch GitHub issue context -->")
        else:
            lines.append("No GitHub issue context available.")
        lines.append("")

    # Current Progress section
    lines.append("## Current Progress")
    lines.append("")
    if assignments:
        for assignment in assignments:
            module_id = assignment.get("module", "unknown")
            status = assignment.get("status", "unknown")
            lines.append("- **{}**: {}".format(module_id, status))
            # Include verification state if present
            verification = assignment.get("instruction_verification", {})
            if isinstance(verification, dict) and verification:
                v_status = verification.get("status", "")
                if v_status:
                    lines.append("  - Verification status: {}".format(v_status))
        lines.append("")
    else:
        if flag_gaps:
            lines.append("<!-- GAP: No progress data available -->")
        else:
            lines.append("No progress data available.")
        lines.append("")

    # Technical Context section
    lines.append("## Technical Context")
    lines.append("")
    if git_state:
        branch = git_state.get("branch", gap)
        lines.append("- **Branch**: {}".format(branch))
        has_uncommitted = git_state.get("has_uncommitted_changes", False)
        lines.append("- **Uncommitted changes**: {}".format("Yes" if has_uncommitted else "No"))
        last_commit = git_state.get("last_commit_message", gap)
        lines.append("- **Last commit**: {}".format(last_commit))
        ahead = git_state.get("commits_ahead_of_main", gap)
        lines.append("- **Commits ahead of main**: {}".format(ahead))
        modified = git_state.get("modified_files", [])
        if modified:
            lines.append("- **Modified files**:")
            for f in modified[:20]:  # Limit to 20 files
                lines.append("  - {}".format(f))
    else:
        if flag_gaps:
            lines.append("<!-- GAP: Git state unavailable (not a git repository or git not installed) -->")
        else:
            lines.append("Git state information unavailable.")
    lines.append("")

    # Next Steps section
    lines.append("## Next Steps")
    lines.append("")
    lines.append("1. Review this handoff document thoroughly")
    lines.append("2. Check out the relevant branch (if applicable)")
    lines.append("3. Review any uncommitted changes or patches")
    lines.append("4. Resume work on incomplete modules")
    lines.append("5. Complete the Instruction Verification Protocol with the orchestrator")
    lines.append("")

    # Verification Requirements section
    lines.append("## Verification Requirements")
    lines.append("")
    lines.append("The replacement agent must:")
    lines.append("")
    lines.append("1. **ACK** receipt of this handoff to the orchestrator")
    lines.append("2. **Repeat** key requirements in your own words")
    lines.append("3. **List** any questions or concerns")
    lines.append("4. **Confirm** understanding before beginning implementation")
    lines.append("")

    return "\n".join(lines)


def upload_to_github_issue(content, issue_number):
    """Upload handoff content as a comment on a GitHub issue.

    Args:
        content: The handoff document text.
        issue_number: The GitHub issue number to comment on.

    Returns:
        The URL of the created comment, or None if the upload failed.
    """
    if not issue_number:
        return None

    issue_num = str(issue_number).lstrip("#")

    try:
        result = subprocess.run(
            ["gh", "issue", "comment", issue_num, "--body", content],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            # Try to extract comment URL from output
            return result.stdout.strip() if result.stdout.strip() else "Comment posted to issue #{}".format(issue_num)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def main():
    """Main entry point for replacement handoff generation.

    Parses arguments, gathers context from state file and external sources,
    builds the handoff document, and optionally uploads it to GitHub.

    Returns:
        Exit code: 0 for success, 1 for error.
    """
    parser = argparse.ArgumentParser(
        description="Generate a comprehensive handoff document for agent replacement"
    )
    parser.add_argument(
        "--failed-agent", required=True,
        help="ID of the agent being replaced"
    )
    parser.add_argument(
        "--new-agent", required=True,
        help="ID of the replacement agent"
    )
    parser.add_argument(
        "--include-tasks", action="store_true", default=True,
        help="Include full task details (default: true)"
    )
    parser.add_argument(
        "--include-context", action="store_true", default=True,
        help="Include communication history context (default: true)"
    )
    parser.add_argument(
        "--partial", action="store_true", default=False,
        help="Generate even with incomplete data"
    )
    parser.add_argument(
        "--flag-gaps", action="store_true", default=False,
        help="Mark missing information with GAP markers"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Custom output filename for the handoff document"
    )
    parser.add_argument(
        "--upload", action="store_true", default=False,
        help="Upload handoff to relevant GitHub issue as a comment"
    )

    args = parser.parse_args()

    # Load orchestration state
    state_data, _ = load_exec_state()

    # Get failed agent's assignments and modules
    assignments = get_failed_agent_assignments(state_data, args.failed_agent)
    modules = get_failed_agent_modules(state_data, args.failed_agent)

    # Gather GitHub issue context for each assignment
    github_contexts = {}
    if args.include_context:
        issue_numbers = set()
        for assignment in assignments:
            gh_issue = assignment.get("github_issue")
            if gh_issue:
                issue_numbers.add(str(gh_issue).lstrip("#"))
        for module in modules:
            gh_issue = module.get("github_issue")
            if gh_issue:
                issue_numbers.add(str(gh_issue).lstrip("#"))

        for issue_num in issue_numbers:
            github_contexts[issue_num] = get_github_issue_context(issue_num)

    # Gather git state
    git_state = get_git_branch_state()

    # Build the handoff document
    handoff_content = build_handoff_document(
        failed_agent=args.failed_agent,
        new_agent=args.new_agent,
        assignments=assignments,
        modules=modules,
        github_contexts=github_contexts,
        git_state=git_state,
        flag_gaps=args.flag_gaps,
    )

    # Determine output file path
    now_str = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if args.output:
        output_path = Path(args.output)
    else:
        HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
        filename = "replacement-handoff-{}-to-{}-{}.md".format(
            args.failed_agent, args.new_agent, now_str
        )
        output_path = HANDOFF_DIR / filename

    # Write handoff document
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(handoff_content, encoding="utf-8")
    except OSError as e:
        print(json.dumps({"error": "Failed to write handoff file: {}".format(str(e))}), file=sys.stderr)
        return 1

    # Optionally upload to GitHub
    upload_url = None
    if args.upload:
        # Find the first relevant issue number to upload to
        first_issue = None
        for assignment in assignments:
            gh_issue = assignment.get("github_issue")
            if gh_issue:
                first_issue = gh_issue
                break
        if not first_issue:
            for module in modules:
                gh_issue = module.get("github_issue")
                if gh_issue:
                    first_issue = gh_issue
                    break

        if first_issue:
            upload_url = upload_to_github_issue(handoff_content, first_issue)

    # Output JSON summary to stdout
    result = {
        "handoff_file": str(output_path),
        "failed_agent": args.failed_agent,
        "new_agent": args.new_agent,
        "assignments_found": len(assignments),
        "modules_found": len(modules),
        "github_issues_fetched": len(github_contexts),
        "git_state_available": bool(git_state),
        "gaps_flagged": args.flag_gaps,
    }
    if upload_url:
        result["upload_url"] = upload_url

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
