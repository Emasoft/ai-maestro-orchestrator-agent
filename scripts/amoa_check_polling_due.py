#!/usr/bin/env python3
"""
EOA: Proactive Progress Polling Check
MANDATORY ENFORCEMENT HOOK

This UserPromptSubmit hook checks if any active assignments have overdue
polling and reminds the orchestrator. Part of the Proactive Progress
Polling protocol enforcement.

Exit codes:
- 0: Always (this is a reminder, not a blocker)

Output:
- systemMessage: Warning if polling is overdue
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# State file path (relative to project root)
EXEC_PHASE_FILE = Path(".claude/orchestrator-exec-phase.local.md")

# Polling interval (in minutes)
POLLING_INTERVAL_MINUTES = 15
POLLING_WARNING_MINUTES = 10  # Warn when approaching poll interval


def log_error(message: str) -> None:
    """Log error message to stderr."""
    import sys

    print(f"[ERROR] eoa_check_polling_due: {message}", file=sys.stderr)


def parse_frontmatter(file_path: Path) -> tuple[dict, bool]:
    """Parse YAML frontmatter from markdown file.

    Returns:
        Tuple of (data_dict, success_bool)
        - On success: (parsed_dict, True)
        - On failure: ({}, False) with error logged
    """
    if not file_path.exists():
        return {}, True  # Not existing is not an error

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        log_error(f"Failed to read file {file_path}: {e}")
        return {}, False

    if not content.startswith("---"):
        return {}, True  # No frontmatter is valid

    end_idx = content.find("---", 3)
    if end_idx == -1:
        return {}, True  # Malformed but not critical

    try:
        import yaml

        result = yaml.safe_load(content[3:end_idx]) or {}
        return result, True
    except ImportError:
        log_error("PyYAML not installed - cannot parse state file")
        return {}, False
    except Exception as e:
        log_error(f"YAML parsing error: {e}")
        return {}, False


def check_polling_status() -> tuple[list, list]:
    """
    Check polling status for all active assignments.

    Returns:
        tuple: (overdue_list, warning_list)
        - overdue_list: Assignments where polling is overdue (>15 min)
        - warning_list: Assignments approaching poll interval (10-15 min)
    """
    # Check if we're in orchestration phase
    if not EXEC_PHASE_FILE.exists():
        return [], []

    state, parse_success = parse_frontmatter(EXEC_PHASE_FILE)
    if not parse_success:
        # ISSUE 10 FIX: Log error and return empty instead of silently failing
        log_error("Failed to parse state file - cannot check polling status")
        return [], []
    if not state:
        return [], []

    # Check if phase is orchestration
    if state.get("phase") != "orchestration":
        return [], []

    # Get active assignments
    active_assignments = state.get("active_assignments", [])
    if not active_assignments:
        return [], []

    now = datetime.now()
    overdue = []
    warning = []

    for assignment in active_assignments:
        agent = assignment.get("agent", "unknown")
        module = assignment.get("module", "unknown")
        status = assignment.get("status", "unknown")

        # Only check assignments that are actively being worked
        if status not in ("working", "in-progress", "in_progress"):
            continue

        # Get polling info
        polling = assignment.get("progress_polling", {})
        last_poll_str = polling.get("last_poll")
        next_poll_due_str = polling.get("next_poll_due")

        # If no polling data, consider it overdue
        if not last_poll_str:
            overdue.append(
                {
                    "agent": agent,
                    "module": module,
                    "minutes_overdue": "never polled",
                    "poll_count": polling.get("poll_count", 0),
                }
            )
            continue

        # Parse timestamps
        try:
            if next_poll_due_str:
                iso_str = next_poll_due_str.replace("Z", "+00:00")
                next_poll_due = datetime.fromisoformat(iso_str)
                if next_poll_due.tzinfo:
                    next_poll_due = next_poll_due.replace(tzinfo=None)
            else:
                # Calculate from last poll
                last_poll = datetime.fromisoformat(last_poll_str.replace("Z", "+00:00"))
                if last_poll.tzinfo:
                    last_poll = last_poll.replace(tzinfo=None)
                next_poll_due = last_poll + timedelta(minutes=POLLING_INTERVAL_MINUTES)
        except (ValueError, TypeError):
            # If timestamp parsing fails, add to overdue
            overdue.append(
                {
                    "agent": agent,
                    "module": module,
                    "minutes_overdue": "timestamp error",
                    "poll_count": polling.get("poll_count", 0),
                }
            )
            continue

        # Check if overdue or approaching
        time_diff = (now - next_poll_due).total_seconds() / 60

        if time_diff > 0:
            # Overdue
            overdue.append(
                {
                    "agent": agent,
                    "module": module,
                    "minutes_overdue": round(time_diff, 1),
                    "poll_count": polling.get("poll_count", 0),
                }
            )
        elif time_diff > -POLLING_WARNING_MINUTES:
            # Approaching poll interval (within warning window)
            warning.append(
                {
                    "agent": agent,
                    "module": module,
                    "minutes_until_due": round(-time_diff, 1),
                    "poll_count": polling.get("poll_count", 0),
                }
            )

    return overdue, warning


def format_reminder(overdue: list, warning: list) -> str:
    """Format the polling reminder message."""
    lines = []

    if overdue:
        lines.append("🚨 POLLING OVERDUE - MANDATORY ACTION REQUIRED:")
        for item in overdue:
            lines.append(
                f"  • {item['agent']} ({item['module']}): "
                f"{item['minutes_overdue']} min overdue, "
                f"{item['poll_count']} polls so far"
            )
        lines.append("")
        lines.append(
            "The Proactive Progress Polling protocol requires polling every 10-15 min."
        )
        lines.append(
            "Use /check-agents now to poll active agents with the 6 MANDATORY questions:"
        )
        lines.append("  1. Current progress (% complete, what's done)")
        lines.append("  2. Next steps (what working on now)")
        lines.append("  3. Are there any issues or problems?")
        lines.append("  4. Is anything unclear?")
        lines.append("  5. Any unforeseen difficulties?")
        lines.append("  6. Do you need anything from me?")
        lines.append("")

    if warning:
        lines.append("⚠️ POLLING DUE SOON:")
        for item in warning:
            lines.append(
                f"  • {item['agent']} ({item['module']}): "
                f"due in {item['minutes_until_due']} min"
            )
        lines.append("")

    return "\n".join(lines)


def main():
    """
    Main hook execution.

    Reads user prompt from stdin (JSON format) and checks polling status.
    Always exits 0 (this is a reminder, not a blocker).
    """
    # Read stdin for hook context (if any)
    # Note: hook_input reserved for future use when context-aware decisions needed
    try:
        stdin_data = sys.stdin.read()
        if stdin_data.strip():
            _ = json.loads(stdin_data)  # Parse to validate, may use context later
    except (json.JSONDecodeError, Exception):
        pass  # No hook context available

    # Check polling status
    overdue, warning = check_polling_status()

    result = {
        "status": "ok",
        "overdue_count": len(overdue),
        "warning_count": len(warning),
        "timestamp": datetime.now().isoformat(),
    }

    # Add reminder if there are overdue or warning items
    if overdue or warning:
        result["systemMessage"] = format_reminder(overdue, warning)

    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()
