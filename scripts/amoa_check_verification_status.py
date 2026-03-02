#!/usr/bin/env python3
"""
EOA: Instruction Verification Status Check
MANDATORY ENFORCEMENT HOOK

This PreToolUse hook checks if instruction verification is complete
before allowing agent work to proceed. Part of the Instruction Verification
Protocol enforcement.

Exit codes:
- 0: Verification complete or not in orchestration phase
- 2: Verification incomplete - blocks the tool use
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# State file path (relative to project root)
EXEC_PHASE_FILE = Path(".claude/orchestrator-exec-phase.local.md")


def log_error(message: str) -> None:
    """Log error message to stderr for visibility."""
    print(f"[ERROR] eoa_check_verification_status: {message}", file=sys.stderr)


def parse_frontmatter(file_path: Path) -> tuple[dict[str, Any], bool]:
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


def check_verification_status() -> tuple[bool, str]:
    """
    Check if all active assignments have completed instruction verification.

    Returns:
        tuple: (is_ok, message)
        - is_ok: True if all verifications complete or not in orchestration phase
        - message: Description of status
    """
    # Check if we're in orchestration phase
    if not EXEC_PHASE_FILE.exists():
        return True, "Not in orchestration phase"

    state, parse_success = parse_frontmatter(EXEC_PHASE_FILE)
    if not parse_success:
        # ISSUE 10 FIX: Return blocking status on parse failure for safety
        log_error("Failed to parse state file - blocking for safety")
        return False, "State file parse error - verification status unknown"
    if not state:
        return True, "No state data found"

    # Check if phase is orchestration
    if state.get("phase") != "orchestration":
        return True, "Not in active orchestration"

    # Get active assignments
    active_assignments = state.get("active_assignments", [])
    if not active_assignments:
        return True, "No active assignments"

    # Check each assignment's instruction verification status
    unverified = []
    pending_updates = []

    for assignment in active_assignments:
        agent = assignment.get("agent", "unknown")
        module = assignment.get("module", "unknown")
        verification = assignment.get("instruction_verification", {})

        status = verification.get("status", "pending")
        authorized_at = verification.get("authorized_at")

        # Initial verification is incomplete if:
        # - status is not "verified"
        # - OR authorized_at is null/missing
        if status != "verified" or not authorized_at:
            unverified.append(
                {
                    "agent": agent,
                    "module": module,
                    "status": status,
                    "verification_type": "initial",
                    "authorized": bool(authorized_at),
                }
            )

    # GAP 2 FIX: Also check instruction_updates for pending mid-impl verifications
    # This ensures update verifications are completed before agents report progress
    instruction_updates = state.get("instruction_updates", [])
    for update in instruction_updates:
        update_agent = update.get("agent", "unknown")
        update_module = update.get("module", "unknown")
        update_status = update.get("verification_status", "pending")

        # Update verification is pending if status is not "verified"
        if update_status != "verified":
            pending_updates.append(
                {
                    "agent": update_agent,
                    "module": update_module,
                    "status": update_status,
                    "verification_type": "update",
                    "update_id": update.get("update_id", "unknown"),
                }
            )

    # Combine both types of incomplete verifications
    all_incomplete = unverified + pending_updates

    if all_incomplete:
        # Format message based on verification types
        initial_list = [
            u for u in all_incomplete if u.get("verification_type") == "initial"
        ]
        update_list = [
            u for u in all_incomplete if u.get("verification_type") == "update"
        ]

        messages = []
        if initial_list:
            agents_str = ", ".join(
                f"{u['agent']} ({u['module']})" for u in initial_list
            )
            messages.append(f"Initial verification incomplete: {agents_str}")
        if update_list:
            updates_str = ", ".join(
                f"{u['agent']} ({u['module']}, update: {u['update_id']})"
                for u in update_list
            )
            messages.append(f"Update verification pending: {updates_str}")

        return False, "; ".join(messages)

    return True, "All assignments have verified instructions (initial and updates)"


def main() -> None:
    """
    Main hook execution.

    Reads tool input from stdin (JSON format) and checks verification status.
    """
    # Read stdin for hook context (if any)
    # Note: hook_input reserved for future use when context-aware decisions needed
    try:
        stdin_data = sys.stdin.read()
        if stdin_data.strip():
            _ = json.loads(stdin_data)  # Parse to validate, may use context later
    except (json.JSONDecodeError, Exception):
        pass  # No hook context available

    # Check verification status
    is_ok, message = check_verification_status()

    if is_ok:
        # Allow tool use to proceed
        result: dict[str, Any] = {
            "status": "ok",
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }
        print(json.dumps(result))
        sys.exit(0)
    else:
        # Block tool use - verification incomplete
        result = {
            "decision": "block",
            "reason": message,
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"INSTRUCTION VERIFICATION PROTOCOL: {message}. "
                    "Complete the verification protocol before proceeding."
                ),
            },
            "systemMessage": f"⚠️ INSTRUCTION VERIFICATION REQUIRED: {message}\n\n"
            "The Instruction Verification Protocol is MANDATORY.\n"
            "Before any agent begins work:\n"
            "1. Agent must repeat the key requirements in their own words\n"
            "2. Orchestrator must verify the repetition is correct\n"
            "3. Answer any clarifying questions\n"
            "4. Issue formal authorization to proceed\n\n"
            "Use /check-agents to see verification status.",
            "timestamp": datetime.now().isoformat(),
        }
        # Exit code 2 indicates blocking error
        print(json.dumps(result), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
