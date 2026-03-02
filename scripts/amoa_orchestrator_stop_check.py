#!/usr/bin/env python3
"""
EOA Orchestrator Stop Check -- Phase-Aware Stop Hook Enforcement

Reads orchestration state from .emasoft/orchestration-state.json to determine
the current phase and checks if stopping is allowed.

Decision logic:
  - No state file or unknown phase: allow stop (exit 0)
  - Plan Phase with plan_phase_complete=false: block stop (exit 2)
  - Plan Phase with plan_phase_complete=true: allow stop (exit 0)
  - Orchestration Phase with incomplete modules: block stop (exit 2)
  - Orchestration Phase with verification_loops_remaining > 0: block stop (exit 2)
  - Orchestration Phase with all complete and no loops: allow stop (exit 0)
  - Corrupt or empty state file: allow stop (exit 0, fail-safe)

Output: JSON to stdout with keys: decision, reason, systemMessage, outputToUser
Exit codes: 0 = allow stop, 2 = block stop

Usage:
    python3 eoa_orchestrator_stop_check.py

    # The script reads .emasoft/orchestration-state.json from the
    # current working directory (the project root).

Examples:
    # In a project with no orchestration state (allows stop):
    cd /path/to/project && python3 /path/to/eoa_orchestrator_stop_check.py
    # Output: {"decision": "allow", "reason": "No orchestration state found", ...}
    # Exit code: 0

    # In a project with incomplete plan phase (blocks stop):
    cd /path/to/project && python3 /path/to/eoa_orchestrator_stop_check.py
    # Output: {"decision": "block", "reason": "Plan phase is not complete", ...}
    # Exit code: 2
"""

import json
import sys
from pathlib import Path


# State file location relative to the working directory
STATE_FILE_PATH = ".emasoft/orchestration-state.json"


def output_allow(reason):
    """Print an allow decision as JSON to stdout and exit with code 0.

    Args:
        reason: Human-readable reason for allowing the stop.
    """
    result = {
        "decision": "allow",
        "reason": reason,
        "systemMessage": "Stop allowed: " + reason,
        "outputToUser": reason,
    }
    print(json.dumps(result, indent=2))
    sys.exit(0)


def output_block(reason, system_message=None, output_to_user=None):
    """Print a block decision as JSON to stdout and exit with code 2.

    Args:
        reason: Human-readable reason for blocking the stop.
        system_message: Optional system message override.
        output_to_user: Optional user-facing message override.
    """
    result = {
        "decision": "block",
        "reason": reason,
        "systemMessage": system_message if system_message else "Stop blocked: " + reason,
        "outputToUser": output_to_user if output_to_user else reason,
    }
    print(json.dumps(result, indent=2))
    sys.exit(2)


def load_state():
    """Load orchestration state from the JSON state file.

    Returns:
        A dictionary with the state data, or None if the file does not
        exist, is empty, or contains invalid JSON.
    """
    state_path = Path(STATE_FILE_PATH)
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


def check_plan_phase(state):
    """Check if the plan phase allows stopping.

    Args:
        state: The orchestration state dictionary.

    Returns:
        True if stop should be blocked, False if stop is allowed.
        When blocked, calls output_block and does not return.
    """
    plan_complete = state.get("plan_phase_complete", False)
    if not plan_complete:
        output_block(
            reason="Plan phase is not complete. All requirements must be documented "
                   "and the plan must be approved before the orchestrator can stop.",
            system_message="BLOCKED: Plan phase incomplete - cannot stop orchestrator",
            output_to_user="The plan phase is not yet complete. Please finish documenting "
                          "requirements and getting plan approval before stopping.",
        )
    # Plan is complete, allow stop
    return False


def check_orchestration_phase(state):
    """Check if the orchestration phase allows stopping.

    Args:
        state: The orchestration state dictionary.

    Returns:
        True if stop should be blocked, False if stop is allowed.
        When blocked, calls output_block and does not return.
    """
    # Check module completion
    modules = state.get("modules_status", [])
    incomplete_modules = []
    for module in modules:
        module_id = module.get("id", "unknown")
        module_status = module.get("status", "unknown")
        if module_status not in ("complete", "done"):
            incomplete_modules.append({"id": module_id, "status": module_status})

    if incomplete_modules:
        module_list = ", ".join(
            "{} ({})".format(m["id"], m["status"]) for m in incomplete_modules
        )
        output_block(
            reason="Orchestration phase has {} incomplete module(s): {}. "
                   "All modules must be complete before stopping.".format(
                       len(incomplete_modules), module_list
                   ),
            system_message="BLOCKED: {} module(s) incomplete - cannot stop orchestrator".format(
                len(incomplete_modules)
            ),
            output_to_user="The following modules are not yet complete: {}. "
                          "Please wait for all modules to finish.".format(module_list),
        )

    # Check verification loops
    verification_remaining = state.get("verification_loops_remaining", 0)
    if isinstance(verification_remaining, int) and verification_remaining > 0:
        output_block(
            reason="{} verification loop(s) remaining. All verification loops "
                   "must complete before stopping.".format(verification_remaining),
            system_message="BLOCKED: {} verification loop(s) remaining".format(
                verification_remaining
            ),
            output_to_user="There are {} verification loop(s) still pending. "
                          "Please wait for verification to complete.".format(
                              verification_remaining
                          ),
        )

    # All modules complete and no verification loops remaining
    return False


def main():
    """Main entry point for the phase-aware stop hook enforcement.

    Reads the orchestration state file and decides whether to allow or
    block the orchestrator from stopping.

    Exit codes:
        0 - Allow stop
        2 - Block stop
    """
    # Load orchestration state
    state = load_state()

    # No state file or invalid state: allow stop (fail-safe)
    if state is None:
        output_allow("No orchestration state found")
        return  # output_allow calls sys.exit, but this is for clarity

    # Determine current phase
    phase = state.get("phase", "")

    if phase == "plan":
        # In plan phase: check if plan is complete
        check_plan_phase(state)
        # If we reach here, plan phase is complete
        output_allow("Plan phase is complete")

    elif phase == "orchestration":
        # In orchestration phase: check modules and verification
        check_orchestration_phase(state)
        # If we reach here, all modules complete and no verification loops
        output_allow("All modules complete and verification finished")

    else:
        # Unknown phase or no phase specified: allow stop (fail-safe)
        output_allow("Unknown or unrecognized phase: {}".format(phase if phase else "(none)"))


if __name__ == "__main__":
    main()
