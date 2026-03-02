#!/usr/bin/env python3
"""
EOA Check Orchestration Phase -- Verify Orchestration Phase Completion

Checks whether the Orchestration Phase is complete by examining:
  1. All modules have status "verified" or "complete" (no pending/in-progress)
  2. No verification loops remaining (verification_loops_remaining == 0)
  3. No blocking issues listed in the state

This script is used by the EOA stop hook to determine if the orchestrator
can safely stop during the Orchestration Phase.

NO external dependencies -- Python 3.8+ stdlib only.

Usage:
    python3 eoa_check_orchestration_phase.py
    python3 eoa_check_orchestration_phase.py --project-root /path/to/project
    python3 eoa_check_orchestration_phase.py --verbose

Exit codes:
    0 - Orchestration phase is complete (all modules done, no loops, no blockers)
    2 - Orchestration phase is incomplete
    1 - Error (could not read state file, invalid JSON, etc.)

Examples:
    # Check orchestration phase in current directory:
    python3 eoa_check_orchestration_phase.py
    # Output: {"complete": true, "reason": "...", "modules_complete": 5, ...}

    # Check with verbose stderr output:
    python3 eoa_check_orchestration_phase.py --verbose
    # Stderr shows per-module status details

    # Check in a specific project:
    python3 eoa_check_orchestration_phase.py --project-root /home/user/project
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


def check_module_completion(state: dict, verbose: bool) -> tuple[bool, str, int, int, list]:
    """Check whether all modules have a complete status.

    Args:
        state: The orchestration state dictionary.
        verbose: If True, print per-module details to stderr.

    Returns:
        Tuple of (all_complete, reason, complete_count, total_count, incomplete_list).
        incomplete_list contains dicts with "id" and "status" for each incomplete module.
    """
    # Modules can be stored under different keys
    modules = state.get("modules_status", [])
    if not modules:
        modules = state.get("modules", [])

    if not isinstance(modules, list):
        return False, "modules field is not a list", 0, 0, []

    if len(modules) == 0:
        # No modules defined means nothing to complete -- treat as incomplete
        return False, "No modules defined in orchestration state", 0, 0, []

    complete_count = 0
    total_count = len(modules)
    incomplete_list = []

    for module in modules:
        if not isinstance(module, dict):
            continue
        module_id = module.get("id", module.get("name", "unknown"))
        module_status = module.get("status", "unknown").lower()

        if verbose:
            marker = "OK" if module_status in COMPLETE_STATUSES else "INCOMPLETE"
            print(
                "  [{}] {} -> {}".format(marker, module_id, module_status),
                file=sys.stderr,
            )

        if module_status in COMPLETE_STATUSES:
            complete_count += 1
        else:
            incomplete_list.append({"id": module_id, "status": module_status})

    if incomplete_list:
        ids = ", ".join(m["id"] for m in incomplete_list)
        reason = "{} of {} module(s) incomplete: {}".format(
            len(incomplete_list), total_count, ids
        )
        return False, reason, complete_count, total_count, incomplete_list

    return True, "All {} module(s) complete".format(total_count), complete_count, total_count, []


def check_verification_loops(state: dict, verbose: bool) -> tuple[bool, str, int]:
    """Check whether any verification loops remain.

    Args:
        state: The orchestration state dictionary.
        verbose: If True, print details to stderr.

    Returns:
        Tuple of (no_loops_remaining, reason, loops_remaining_count).
    """
    remaining = state.get("verification_loops_remaining", 0)

    # Validate type -- treat non-integer as 0 (fail-safe)
    if not isinstance(remaining, int):
        try:
            remaining = int(remaining)
        except (ValueError, TypeError):
            remaining = 0

    if verbose:
        print(
            "  Verification loops remaining: {}".format(remaining),
            file=sys.stderr,
        )

    if remaining > 0:
        reason = "{} verification loop(s) still remaining".format(remaining)
        return False, reason, remaining

    return True, "No verification loops remaining", 0


def check_blocking_issues(state: dict, verbose: bool) -> tuple[bool, str, list]:
    """Check whether any blocking issues are listed in the state.

    Blocking issues are stored in the 'blocking_issues' field as a list.

    Args:
        state: The orchestration state dictionary.
        verbose: If True, print details to stderr.

    Returns:
        Tuple of (no_blockers, reason, blocker_list).
    """
    blockers = state.get("blocking_issues", [])

    if not isinstance(blockers, list):
        blockers = []

    # Filter out resolved blockers if they have a status field
    active_blockers = []
    for blocker in blockers:
        if isinstance(blocker, dict):
            blocker_status = blocker.get("status", "active").lower()
            if blocker_status not in ("resolved", "closed", "dismissed"):
                active_blockers.append(blocker)
        elif isinstance(blocker, str) and blocker.strip():
            # Plain string blockers are always active
            active_blockers.append({"description": blocker, "status": "active"})

    if verbose:
        print(
            "  Active blocking issues: {}".format(len(active_blockers)),
            file=sys.stderr,
        )
        for b in active_blockers:
            desc = b.get("description", b.get("id", str(b)))
            print("    - {}".format(desc), file=sys.stderr)

    if active_blockers:
        descriptions: list[str] = []
        for b in active_blockers:
            # Extract a human-readable description from the blocker dict
            desc = b.get("description") or b.get("id") or str(b)
            descriptions.append(str(desc))
        reason = "{} blocking issue(s): {}".format(
            len(active_blockers), "; ".join(descriptions)
        )
        return False, reason, active_blockers

    return True, "No blocking issues", []


def main() -> int:
    """Main entry point for orchestration phase completion check.

    Runs all checks, outputs JSON to stdout, and returns the appropriate
    exit code.

    Returns:
        0 if orchestration phase is complete, 2 if incomplete, 1 on error.
    """
    parser = argparse.ArgumentParser(
        description="Check if the Orchestration Phase is complete"
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
        help="Print detailed check information to stderr",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()

    # Load state file
    state = load_state(project_root)
    if state is None:
        result = {
            "complete": False,
            "reason": "Could not load orchestration state from {}".format(
                project_root / STATE_FILE_REL
            ),
            "modules_complete": 0,
            "modules_total": 0,
            "blocking": [],
        }
        print(json.dumps(result, indent=2))
        return 2

    if args.verbose:
        print("Checking orchestration phase completion...", file=sys.stderr)

    # Check 1: Module completion
    if args.verbose:
        print("Module status:", file=sys.stderr)
    modules_ok, modules_reason, complete_count, total_count, incomplete = (
        check_module_completion(state, args.verbose)
    )

    # Check 2: Verification loops
    if args.verbose:
        print("Verification loops:", file=sys.stderr)
    loops_ok, loops_reason, loops_remaining = check_verification_loops(
        state, args.verbose
    )

    # Check 3: Blocking issues
    if args.verbose:
        print("Blocking issues:", file=sys.stderr)
    blockers_ok, blockers_reason, active_blockers = check_blocking_issues(
        state, args.verbose
    )

    # Determine overall result
    all_complete = modules_ok and loops_ok and blockers_ok

    if all_complete:
        reason = "All {} module(s) complete, no verification loops, no blockers".format(
            total_count
        )
    else:
        # Report the first failure as the primary reason
        reasons = []
        if not modules_ok:
            reasons.append(modules_reason)
        if not loops_ok:
            reasons.append(loops_reason)
        if not blockers_ok:
            reasons.append(blockers_reason)
        reason = "; ".join(reasons)

    # Build blocking list for output
    blocking_output = []
    for mod in incomplete:
        blocking_output.append(
            "module:{} status:{}".format(mod["id"], mod["status"])
        )
    if loops_remaining > 0:
        blocking_output.append(
            "verification_loops_remaining:{}".format(loops_remaining)
        )
    for b in active_blockers:
        desc = b.get("description", b.get("id", str(b)))
        blocking_output.append("blocker:{}".format(desc))

    result = {
        "complete": all_complete,
        "reason": reason,
        "modules_complete": complete_count,
        "modules_total": total_count,
        "blocking": blocking_output,
    }

    print(json.dumps(result, indent=2))

    if all_complete:
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
