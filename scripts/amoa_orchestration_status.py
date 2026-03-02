#!/usr/bin/env python3
"""
EOA Orchestration Status -- Display Orchestration Phase Progress

Shows the current orchestration phase progress including:
  - Current phase (plan / orchestration / unknown)
  - Module completion count and per-module status
  - Active agent assignments
  - Verification status (loops remaining)
  - Polling schedule information

This is DIFFERENT from eoa_check_orchestrator_status.py which shows the
orchestrator LOOP status (iteration count, task sources). This script shows
the PHASE status (modules, agents, assignments, verification).

NO external dependencies -- Python 3.8+ stdlib only.

Usage:
    python3 eoa_orchestration_status.py
    python3 eoa_orchestration_status.py --project-root /path/to/project
    python3 eoa_orchestration_status.py --verbose
    python3 eoa_orchestration_status.py --modules-only
    python3 eoa_orchestration_status.py --agents-only
    python3 eoa_orchestration_status.py --format json

Exit codes:
    0 - Success (status displayed)
    1 - Error (could not read state file, invalid JSON, etc.)

Examples:
    # Show full status in human-readable text:
    python3 eoa_orchestration_status.py

    # Show only module statuses:
    python3 eoa_orchestration_status.py --modules-only

    # Show only agent assignments:
    python3 eoa_orchestration_status.py --agents-only

    # Output as JSON for programmatic use:
    python3 eoa_orchestration_status.py --format json

    # Verbose output with extra details:
    python3 eoa_orchestration_status.py --verbose
"""

import argparse
import json
import sys
from pathlib import Path


# State file location relative to the project root
STATE_FILE_REL = ".emasoft/orchestration-state.json"

# Module statuses that count as "complete"
COMPLETE_STATUSES = {"verified", "complete", "done"}


def load_state(project_root: Path) -> dict | None:
    """Load orchestration state from the JSON state file.

    Args:
        project_root: Absolute path to the project root directory.

    Returns:
        A dictionary with the state data, or None if the file does not
        exist, is empty, or contains invalid JSON.
    """
    state_path = project_root / STATE_FILE_REL
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


def get_modules(state: dict) -> list:
    """Extract the module list from the state.

    Args:
        state: The orchestration state dictionary.

    Returns:
        A list of module dictionaries.
    """
    modules = state.get("modules_status", [])
    if not modules:
        modules = state.get("modules", [])
    if not isinstance(modules, list):
        return []
    return modules


def get_assignments(state: dict) -> list:
    """Extract active assignments from the state.

    Args:
        state: The orchestration state dictionary.

    Returns:
        A list of assignment dictionaries.
    """
    assignments = state.get("active_assignments", [])
    if not isinstance(assignments, list):
        return []
    return assignments


def format_text(state: dict, verbose: bool, modules_only: bool, agents_only: bool) -> str:
    """Format the orchestration status as human-readable text.

    Args:
        state: The orchestration state dictionary.
        verbose: Whether to include extra detail.
        modules_only: If True, show only module information.
        agents_only: If True, show only agent information.

    Returns:
        A formatted string to print.
    """
    lines = []

    phase = state.get("phase", "unknown")

    if not modules_only and not agents_only:
        lines.append("=" * 60)
        lines.append("ORCHESTRATION PHASE STATUS")
        lines.append("=" * 60)
        lines.append("")
        lines.append("Current phase:  {}".format(phase))

        # Plan phase completion
        plan_complete = state.get("plan_phase_complete", False)
        lines.append("Plan complete:  {}".format("Yes" if plan_complete else "No"))

        # Timestamps
        started = state.get("started_at", state.get("created_at", "unknown"))
        updated = state.get("updated_at", "unknown")
        lines.append("Started:        {}".format(started))
        if verbose:
            lines.append("Last updated:   {}".format(updated))

        lines.append("")

    # --- Modules section ---
    if not agents_only:
        modules = get_modules(state)
        complete_count = 0
        total_count = len(modules)

        for m in modules:
            if not isinstance(m, dict):
                continue
            status = m.get("status", "unknown").lower()
            if status in COMPLETE_STATUSES:
                complete_count += 1

        lines.append("Modules: {} / {} complete".format(complete_count, total_count))
        lines.append("-" * 40)

        if total_count == 0:
            lines.append("  (no modules defined)")
        else:
            for m in modules:
                if not isinstance(m, dict):
                    continue
                mid = m.get("id", m.get("name", "unknown"))
                status = m.get("status", "unknown")
                priority = m.get("priority", "")
                assigned = m.get("assigned_to", m.get("agent", ""))

                status_marker = "[x]" if status.lower() in COMPLETE_STATUSES else "[ ]"
                line = "  {} {} -- {}".format(status_marker, mid, status)
                if priority:
                    line += " (priority: {})".format(priority)
                if assigned:
                    line += " [assigned: {}]".format(assigned)
                lines.append(line)

                if verbose:
                    desc = m.get("description", "")
                    if desc:
                        lines.append("      Description: {}".format(desc[:80]))
                    issue = m.get("github_issue", m.get("issue_number", ""))
                    if issue:
                        lines.append("      GitHub issue: #{}".format(issue))

        lines.append("")

    # --- Agents / Assignments section ---
    if not modules_only:
        assignments = get_assignments(state)
        lines.append("Active Assignments: {}".format(len(assignments)))
        lines.append("-" * 40)

        if not assignments:
            lines.append("  (no active assignments)")
        else:
            for a in assignments:
                if not isinstance(a, dict):
                    continue
                agent = a.get("agent", a.get("agent_id", "unknown"))
                module = a.get("module", "unknown")
                status = a.get("status", "unknown")
                lines.append("  {} -> module: {} (status: {})".format(agent, module, status))

                if verbose:
                    task_uuid = a.get("task_uuid", "")
                    if task_uuid:
                        lines.append("      Task UUID: {}".format(task_uuid))
                    verification = a.get("instruction_verification", {})
                    if verification:
                        v_status = verification.get("status", "pending")
                        lines.append("      Verification: {}".format(v_status))

        lines.append("")

    # --- Verification section ---
    if not modules_only and not agents_only:
        loops_remaining = state.get("verification_loops_remaining", 0)
        if not isinstance(loops_remaining, int):
            try:
                loops_remaining = int(loops_remaining)
            except (ValueError, TypeError):
                loops_remaining = 0

        lines.append("Verification:")
        lines.append("-" * 40)
        lines.append("  Loops remaining: {}".format(loops_remaining))

        # Blocking issues
        blockers = state.get("blocking_issues", [])
        if isinstance(blockers, list) and blockers:
            active = [
                b for b in blockers
                if isinstance(b, dict) and b.get("status", "active") not in ("resolved", "closed")
            ]
            lines.append("  Blocking issues: {}".format(len(active)))
            for b in active:
                desc = b.get("description", b.get("id", str(b)))
                lines.append("    - {}".format(desc))
        else:
            lines.append("  Blocking issues: 0")

        lines.append("")

        # Poll schedule
        poll_interval = state.get("poll_interval_minutes", state.get("poll_interval", ""))
        next_poll = state.get("next_poll_at", "")
        if poll_interval or next_poll:
            lines.append("Polling:")
            lines.append("-" * 40)
            if poll_interval:
                lines.append("  Poll interval: {} minutes".format(poll_interval))
            if next_poll:
                lines.append("  Next poll at:  {}".format(next_poll))
            lines.append("")

        lines.append("State file: {}".format(STATE_FILE_REL))
        lines.append("=" * 60)

    return "\n".join(lines)


def format_json(state: dict) -> str:
    """Format the orchestration status as JSON.

    Args:
        state: The orchestration state dictionary.

    Returns:
        A JSON string with the status summary.
    """
    modules = get_modules(state)
    assignments = get_assignments(state)

    complete_count = 0
    module_summaries = []
    for m in modules:
        if not isinstance(m, dict):
            continue
        mid = m.get("id", m.get("name", "unknown"))
        status = m.get("status", "unknown")
        if status.lower() in COMPLETE_STATUSES:
            complete_count += 1
        module_summaries.append({"id": mid, "status": status})

    assignment_summaries = []
    for a in assignments:
        if not isinstance(a, dict):
            continue
        assignment_summaries.append({
            "agent": a.get("agent", a.get("agent_id", "unknown")),
            "module": a.get("module", "unknown"),
            "status": a.get("status", "unknown"),
        })

    loops_remaining = state.get("verification_loops_remaining", 0)
    if not isinstance(loops_remaining, int):
        try:
            loops_remaining = int(loops_remaining)
        except (ValueError, TypeError):
            loops_remaining = 0

    result = {
        "phase": state.get("phase", "unknown"),
        "plan_phase_complete": state.get("plan_phase_complete", False),
        "modules_complete": complete_count,
        "modules_total": len(module_summaries),
        "modules": module_summaries,
        "active_assignments": assignment_summaries,
        "verification_loops_remaining": loops_remaining,
        "blocking_issues_count": len([
            b for b in state.get("blocking_issues", [])
            if isinstance(b, dict) and b.get("status", "active") not in ("resolved", "closed")
        ]),
    }

    return json.dumps(result, indent=2)


def main() -> int:
    """Main entry point for orchestration status display.

    Returns:
        0 on success, 1 on error.
    """
    parser = argparse.ArgumentParser(
        description="Display Orchestration Phase progress"
    )
    parser.add_argument(
        "--project-root",
        type=str,
        default=".",
        help="Path to the project root directory (default: current directory)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show extra detail (descriptions, task UUIDs, verification status)",
    )
    parser.add_argument(
        "--modules-only",
        action="store_true",
        help="Show only module status information",
    )
    parser.add_argument(
        "--agents-only",
        action="store_true",
        help="Show only agent assignment information",
    )
    parser.add_argument(
        "--format",
        dest="output_format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    if args.modules_only and args.agents_only:
        print("ERROR: --modules-only and --agents-only are mutually exclusive", file=sys.stderr)
        return 1

    project_root = Path(args.project_root).resolve()

    state = load_state(project_root)
    if state is None:
        if args.output_format == "json":
            result = {
                "phase": "unknown",
                "plan_phase_complete": False,
                "modules_complete": 0,
                "modules_total": 0,
                "modules": [],
                "active_assignments": [],
                "verification_loops_remaining": 0,
                "blocking_issues_count": 0,
                "error": "No orchestration state found at {}".format(
                    project_root / STATE_FILE_REL
                ),
            }
            print(json.dumps(result, indent=2))
        else:
            print("=" * 60)
            print("ORCHESTRATION PHASE STATUS")
            print("=" * 60)
            print()
            print("No orchestration state found.")
            print()
            print("Expected state file: {}".format(project_root / STATE_FILE_REL))
            print()
            print("To start orchestration, use: /eoa-start-orchestration")
            print("=" * 60)
        return 0

    if args.output_format == "json":
        print(format_json(state))
    else:
        print(format_text(state, args.verbose, args.modules_only, args.agents_only))

    return 0


if __name__ == "__main__":
    sys.exit(main())
