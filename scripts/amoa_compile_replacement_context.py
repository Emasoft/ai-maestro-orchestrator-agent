#!/usr/bin/env python3
"""
EOA Compile Replacement Context Script

Gathers ALL information about a FAILED agent's work for agent replacement.
This is DIFFERENT from eoa_compile_handoff.py (which compiles module specs
for new assignments). This script compiles the full context of what a failed
agent was working on, including task state, git history, GitHub issues, design
docs, and known blockers, so the replacement agent can pick up exactly where
the failed agent left off.

Data sources:
  1. State file (.emasoft/orchestration-state.json) - task assignments, progress, blockers
  2. Git branch analysis (git log, git diff --stat)
  3. GitHub Issues (gh issue list --assignee)
  4. Design docs in design/ directory

Usage:
    python3 eoa_compile_replacement_context.py --failed-agent NAME --output FILE
    python3 eoa_compile_replacement_context.py --failed-agent impl-1 --output context.md
    python3 eoa_compile_replacement_context.py --failed-agent impl-1 --output context.md --project-root /path/to/project

Exit codes:
    0 - Success
    1 - Error (missing state file, invalid arguments, or I/O failure)

Examples:
    # Compile context for a failed implementer agent:
    python3 eoa_compile_replacement_context.py \
        --failed-agent implementer-1 --output replacement-context.md

    # Compile context with explicit project root:
    python3 eoa_compile_replacement_context.py \
        --failed-agent implementer-1 --output context.md \
        --project-root /home/user/myproject
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


# State file location relative to the project root
STATE_FILE_PATH = ".emasoft/orchestration-state.json"


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


def get_agent_task_assignments(state, failed_agent):
    """Extract all task assignments for the failed agent from state.

    Searches both active_assignments and modules_status for entries
    that reference the failed agent.

    Args:
        state: The orchestration state dictionary.
        failed_agent: The agent ID of the failed agent.

    Returns:
        A list of assignment dictionaries for the failed agent.
    """
    assignments = []

    # Check active_assignments list
    active = state.get("active_assignments", [])
    if isinstance(active, list):
        for entry in active:
            if isinstance(entry, dict) and entry.get("agent") == failed_agent:
                assignments.append(entry)

    return assignments


def get_agent_modules(state, failed_agent):
    """Extract all modules assigned to the failed agent from state.

    Args:
        state: The orchestration state dictionary.
        failed_agent: The agent ID of the failed agent.

    Returns:
        A list of module status dictionaries for the failed agent.
    """
    modules = state.get("modules_status", [])
    if not isinstance(modules, list):
        return []
    return [
        m for m in modules
        if isinstance(m, dict) and m.get("assigned_to") == failed_agent
    ]


def get_agent_blockers(state, failed_agent):
    """Extract known blockers for the failed agent from state.

    Checks both a top-level 'blockers' list and per-module blocker fields.

    Args:
        state: The orchestration state dictionary.
        failed_agent: The agent ID of the failed agent.

    Returns:
        A list of blocker description strings.
    """
    blockers = []

    # Top-level blockers list
    top_blockers = state.get("blockers", [])
    if isinstance(top_blockers, list):
        for blocker in top_blockers:
            if isinstance(blocker, dict):
                agent = blocker.get("agent", "")
                if agent == failed_agent or not agent:
                    desc = blocker.get("description", blocker.get("reason", str(blocker)))
                    blockers.append(desc)
            elif isinstance(blocker, str):
                blockers.append(blocker)

    # Per-module blockers
    modules = state.get("modules_status", [])
    if isinstance(modules, list):
        for module in modules:
            if not isinstance(module, dict):
                continue
            if module.get("assigned_to") != failed_agent:
                continue
            module_blockers = module.get("blockers", [])
            if isinstance(module_blockers, list):
                for b in module_blockers:
                    blockers.append("{}: {}".format(module.get("id", "unknown"), b))
            elif isinstance(module_blockers, str) and module_blockers:
                blockers.append("{}: {}".format(module.get("id", "unknown"), module_blockers))

    return blockers


def run_git_command(args, project_root, timeout=15):
    """Run a git command and return its stdout, or None on failure.

    Args:
        args: List of arguments to pass to git (without the 'git' prefix).
        project_root: Path to the project root (used as cwd).
        timeout: Timeout in seconds for the git command.

    Returns:
        The stdout string on success, or None on any failure.
    """
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(project_root),
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def gather_git_status(project_root):
    """Gather comprehensive git status for the project.

    Collects: current branch, uncommitted changes, recent commit log,
    diff stats, and commits ahead of main.

    Args:
        project_root: Path to the project root directory.

    Returns:
        A dictionary with git state information. Keys may be absent
        if the corresponding git command failed.
    """
    git_info = {}

    # Current branch
    branch = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], project_root)
    if branch:
        git_info["branch"] = branch

    # Modified files (staged + unstaged)
    porcelain = run_git_command(["status", "--porcelain"], project_root)
    if porcelain is not None:
        files = [line.strip() for line in porcelain.split("\n") if line.strip()]
        git_info["modified_files"] = files
        git_info["has_uncommitted_changes"] = len(files) > 0
    else:
        git_info["has_uncommitted_changes"] = False

    # Recent commits (last 15)
    log_output = run_git_command(
        ["log", "--oneline", "-15", "--format=%h %s"],
        project_root,
    )
    if log_output:
        git_info["recent_commits"] = [
            line for line in log_output.split("\n") if line.strip()
        ]

    # Diff stat against main (shows files changed and lines added/removed)
    diff_stat = run_git_command(["diff", "--stat", "origin/main...HEAD"], project_root)
    if diff_stat:
        git_info["diff_stat_vs_main"] = diff_stat

    # Commits ahead of main
    ahead_count = run_git_command(
        ["rev-list", "--count", "HEAD", "--not", "origin/main"],
        project_root,
    )
    if ahead_count:
        try:
            git_info["commits_ahead_of_main"] = int(ahead_count)
        except ValueError:
            pass

    # Last commit details
    last_commit = run_git_command(
        ["log", "-1", "--format=%H|%an|%ai|%s"],
        project_root,
    )
    if last_commit and "|" in last_commit:
        parts = last_commit.split("|", 3)
        if len(parts) == 4:
            git_info["last_commit_hash"] = parts[0]
            git_info["last_commit_author"] = parts[1]
            git_info["last_commit_date"] = parts[2]
            git_info["last_commit_message"] = parts[3]

    return git_info


def gather_github_issues(failed_agent, project_root):
    """Fetch open GitHub issues assigned to the failed agent.

    Uses the gh CLI tool to list issues. Tries both --assignee filter
    and label-based filter (assigned:<agent>).

    Args:
        failed_agent: The agent ID to search for.
        project_root: Path to the project root (used as cwd for gh).

    Returns:
        A list of issue dictionaries with number, title, state, labels,
        and assignees fields. Returns an empty list on failure.
    """
    issues = []

    # Try by assignee
    try:
        result = subprocess.run(
            ["gh", "issue", "list",
             "--assignee", failed_agent,
             "--state", "open",
             "--json", "number,title,state,labels,assignees,body",
             "--limit", "50"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(project_root),
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            if isinstance(data, list):
                issues.extend(data)
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError, OSError):
        pass

    # Also try by label (assigned:<agent>)
    seen_numbers = {i.get("number") for i in issues}
    label = "assigned:{}".format(failed_agent)
    try:
        result = subprocess.run(
            ["gh", "issue", "list",
             "--label", label,
             "--state", "open",
             "--json", "number,title,state,labels,assignees,body",
             "--limit", "50"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(project_root),
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            if isinstance(data, list):
                for issue in data:
                    if issue.get("number") not in seen_numbers:
                        issues.append(issue)
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError, OSError):
        pass

    return issues


def gather_design_docs(project_root):
    """Scan the design/ directory for design documents.

    Collects file paths and first-line summaries of markdown files
    found in the design/ directory tree.

    Args:
        project_root: Path to the project root directory.

    Returns:
        A list of dictionaries with 'path' and 'summary' keys.
        Returns an empty list if the design/ directory does not exist.
    """
    design_dir = Path(project_root) / "design"
    if not design_dir.exists() or not design_dir.is_dir():
        return []

    docs = []
    # Collect all markdown files recursively, sorted by path
    md_files = sorted(design_dir.rglob("*.md"))
    for md_file in md_files:
        relative = md_file.relative_to(project_root)
        summary = ""
        try:
            # Read first non-empty, non-heading line as summary
            content = md_file.read_text(encoding="utf-8")
            for line in content.split("\n"):
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    summary = stripped[:120]
                    break
        except OSError:
            pass
        docs.append({
            "path": str(relative),
            "summary": summary,
        })

    return docs


def build_replacement_context_document(
    failed_agent,
    timestamp,
    project_root,
    state,
    assignments,
    modules,
    blockers,
    git_info,
    github_issues,
    design_docs,
):
    """Build the full replacement context markdown document.

    Compiles all gathered information into a structured markdown document
    that a replacement agent can use to understand exactly what the failed
    agent was working on and where it stopped.

    Args:
        failed_agent: The agent ID of the failed agent.
        timestamp: ISO-format timestamp string for the document header.
        project_root: Path to the project root directory.
        state: The full orchestration state dict (or None).
        assignments: List of task assignment dicts for the failed agent.
        modules: List of module status dicts for the failed agent.
        blockers: List of blocker description strings.
        git_info: Dictionary with git state information.
        github_issues: List of GitHub issue dicts.
        design_docs: List of design document info dicts.

    Returns:
        The replacement context document as a string.
    """
    lines = []

    # -- Header with metadata --
    lines.append("# Replacement Context: {}".format(failed_agent))
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|-------|-------|")
    lines.append("| **Failed Agent** | {} |".format(failed_agent))
    lines.append("| **Generated At** | {} |".format(timestamp))
    lines.append("| **Project Root** | {} |".format(project_root))
    phase = state.get("phase", "unknown") if state else "unknown"
    lines.append("| **Orchestration Phase** | {} |".format(phase))
    lines.append("")

    # -- Task Assignments --
    lines.append("## Task Assignments")
    lines.append("")
    if assignments:
        for assignment in assignments:
            module_id = assignment.get("module", "N/A")
            status = assignment.get("status", "N/A")
            task_uuid = assignment.get("task_uuid", "N/A")
            lines.append("### Module: {}".format(module_id))
            lines.append("")
            lines.append("- **Task UUID**: {}".format(task_uuid))
            lines.append("- **Status**: {}".format(status))
            gh_issue = assignment.get("github_issue", "")
            if gh_issue:
                lines.append("- **GitHub Issue**: #{}".format(gh_issue))
            verification = assignment.get("instruction_verification", {})
            if isinstance(verification, dict) and verification:
                v_status = verification.get("status", "")
                if v_status:
                    lines.append("- **Verification Status**: {}".format(v_status))
            lines.append("")
    elif modules:
        for module in modules:
            module_id = module.get("id", "N/A")
            status = module.get("status", "N/A")
            lines.append("### Module: {}".format(module_id))
            lines.append("")
            lines.append("- **Status**: {}".format(status))
            gh_issue = module.get("github_issue", "")
            if gh_issue:
                lines.append("- **GitHub Issue**: #{}".format(gh_issue))
            deps = module.get("dependencies", [])
            if deps:
                lines.append("- **Dependencies**: {}".format(", ".join(str(d) for d in deps)))
            lines.append("")
    else:
        lines.append("No task assignments found for agent {}.".format(failed_agent))
        lines.append("")

    # -- Git Status --
    lines.append("## Git Status")
    lines.append("")
    if git_info:
        branch = git_info.get("branch", "N/A")
        lines.append("- **Branch**: {}".format(branch))
        has_uncommitted = git_info.get("has_uncommitted_changes", False)
        lines.append("- **Uncommitted Changes**: {}".format("Yes" if has_uncommitted else "No"))
        ahead = git_info.get("commits_ahead_of_main", "N/A")
        lines.append("- **Commits Ahead of Main**: {}".format(ahead))
        last_hash = git_info.get("last_commit_hash", "")
        last_msg = git_info.get("last_commit_message", "")
        if last_hash:
            lines.append("- **Last Commit**: {} {}".format(last_hash[:10], last_msg))
        lines.append("")

        # Modified files
        modified = git_info.get("modified_files", [])
        if modified:
            lines.append("### Modified Files")
            lines.append("")
            for f in modified[:30]:
                lines.append("- {}".format(f))
            if len(modified) > 30:
                lines.append("- ... and {} more files".format(len(modified) - 30))
            lines.append("")

        # Recent commits
        recent = git_info.get("recent_commits", [])
        if recent:
            lines.append("### Recent Commits")
            lines.append("")
            for commit in recent:
                lines.append("- {}".format(commit))
            lines.append("")

        # Diff stat
        diff_stat = git_info.get("diff_stat_vs_main", "")
        if diff_stat:
            lines.append("### Diff vs Main")
            lines.append("")
            lines.append("```")
            lines.append(diff_stat)
            lines.append("```")
            lines.append("")
    else:
        lines.append("Git status information unavailable.")
        lines.append("")

    # -- Open Issues --
    lines.append("## Open Issues")
    lines.append("")
    if github_issues:
        for issue in github_issues:
            number = issue.get("number", "?")
            title = issue.get("title", "Untitled")
            labels_list = issue.get("labels", [])
            label_names = []
            for label in labels_list:
                if isinstance(label, dict):
                    label_names.append(label.get("name", ""))
                elif isinstance(label, str):
                    label_names.append(label)
            labels_str = ", ".join(label_names) if label_names else "none"
            lines.append("### Issue #{}: {}".format(number, title))
            lines.append("")
            lines.append("- **Labels**: {}".format(labels_str))
            body = issue.get("body", "")
            if body:
                # Truncate very long bodies
                if len(body) > 1500:
                    body = body[:1500] + "\n\n... (truncated)"
                lines.append("- **Description**:")
                lines.append("")
                lines.append(body)
            lines.append("")
    else:
        lines.append("No open GitHub issues found for agent {}.".format(failed_agent))
        lines.append("")

    # -- Design Documents --
    lines.append("## Design Documents")
    lines.append("")
    if design_docs:
        for doc in design_docs:
            path = doc.get("path", "")
            summary = doc.get("summary", "")
            if summary:
                lines.append("- **{}** - {}".format(path, summary))
            else:
                lines.append("- **{}**".format(path))
        lines.append("")
    else:
        lines.append("No design documents found in design/ directory.")
        lines.append("")

    # -- Known Blockers --
    lines.append("## Known Blockers")
    lines.append("")
    if blockers:
        for blocker in blockers:
            lines.append("- {}".format(blocker))
        lines.append("")
    else:
        lines.append("No known blockers recorded for agent {}.".format(failed_agent))
        lines.append("")

    # -- Recommendations for Replacement Agent --
    lines.append("## Recommendations for Replacement Agent")
    lines.append("")
    lines.append("1. Read this context document thoroughly before starting work")
    lines.append("2. Review all listed design documents in design/ for requirements")
    lines.append("3. Check out the relevant git branch and inspect uncommitted changes")
    lines.append("4. Review all open GitHub issues assigned to the failed agent")
    lines.append("5. Address known blockers before resuming implementation")
    lines.append("6. Complete the Instruction Verification Protocol with the orchestrator")
    lines.append("7. ACK receipt of this context to the orchestrator before beginning work")
    lines.append("")

    return "\n".join(lines)


def main():
    """Main entry point for replacement context compilation.

    Parses arguments, gathers context from all data sources, builds
    the replacement context document, and writes it to the output file.

    Returns:
        Exit code: 0 for success, 1 for error.
    """
    parser = argparse.ArgumentParser(
        description="Compile replacement context for a failed agent"
    )
    parser.add_argument(
        "--failed-agent", required=True,
        help="ID of the failed agent whose context to compile"
    )
    parser.add_argument(
        "--output", required=True,
        help="Output file path for the replacement context document"
    )
    parser.add_argument(
        "--project-root", type=str, default=".",
        help="Path to the project root directory (default: current directory)"
    )

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    if not project_root.is_dir():
        print(
            json.dumps({"error": "Project root does not exist: {}".format(args.project_root)}),
            file=sys.stderr,
        )
        return 1

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1. Load orchestration state
    state = load_state(project_root)

    # 2. Extract agent-specific data from state
    assignments = []
    modules = []
    blockers = []
    if state:
        assignments = get_agent_task_assignments(state, args.failed_agent)
        modules = get_agent_modules(state, args.failed_agent)
        blockers = get_agent_blockers(state, args.failed_agent)

    # 3. Gather git branch analysis
    git_info = gather_git_status(project_root)

    # 4. Gather GitHub issues
    github_issues = gather_github_issues(args.failed_agent, project_root)

    # 5. Gather design documents
    design_docs = gather_design_docs(project_root)

    # Build the context document
    context_document = build_replacement_context_document(
        failed_agent=args.failed_agent,
        timestamp=timestamp,
        project_root=str(project_root),
        state=state,
        assignments=assignments,
        modules=modules,
        blockers=blockers,
        git_info=git_info,
        github_issues=github_issues,
        design_docs=design_docs,
    )

    # Write output file
    output_path = Path(args.output)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(context_document, encoding="utf-8")
    except OSError as e:
        print(
            json.dumps({"error": "Failed to write output file: {}".format(str(e))}),
            file=sys.stderr,
        )
        return 1

    # Output JSON summary to stdout
    result = {
        "output_file": str(output_path),
        "failed_agent": args.failed_agent,
        "timestamp": timestamp,
        "state_found": state is not None,
        "assignments_found": len(assignments),
        "modules_found": len(modules),
        "blockers_found": len(blockers),
        "git_state_available": bool(git_info),
        "github_issues_found": len(github_issues),
        "design_docs_found": len(design_docs),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
