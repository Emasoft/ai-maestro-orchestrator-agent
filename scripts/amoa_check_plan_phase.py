#!/usr/bin/env python3
"""
EOA Check Plan Phase -- Verify Plan Phase Completion

Checks whether the Plan Phase is complete by examining:
  1. The plan_phase_complete flag in .emasoft/orchestration-state.json
  2. The existence of USER_REQUIREMENTS.md in the project root
  3. Whether modules are defined in the orchestration state
  4. Whether acceptance criteria are present in the orchestration state

This script is used by the EOA stop hook to determine if the orchestrator
can safely stop during the Plan Phase.

NO external dependencies -- Python 3.8+ stdlib only.

Usage:
    python3 eoa_check_plan_phase.py
    python3 eoa_check_plan_phase.py --project-root /path/to/project
    python3 eoa_check_plan_phase.py --verbose

Exit codes:
    0 - Plan phase is complete (all checks pass)
    2 - Plan phase is incomplete (one or more checks fail)
    1 - Error (could not read state file, invalid JSON, etc.)

Examples:
    # Check plan phase in current directory:
    python3 eoa_check_plan_phase.py
    # Output: {"complete": true, "reason": "All plan phase checks passed", "checks": {...}}

    # Check plan phase in a specific project:
    python3 eoa_check_plan_phase.py --project-root /home/user/my-project
    # Output: {"complete": false, "reason": "USER_REQUIREMENTS.md not found", "checks": {...}}

    # Verbose output with details printed to stderr:
    python3 eoa_check_plan_phase.py --verbose
"""

import argparse
import json
import sys
from pathlib import Path


# State file location relative to the project root
STATE_FILE_REL = ".emasoft/orchestration-state.json"

# Requirements file that must exist in the project root
REQUIREMENTS_FILE = "USER_REQUIREMENTS.md"


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


def check_plan_phase_complete_flag(state: dict) -> tuple[bool, str]:
    """Check whether the plan_phase_complete flag is set to true.

    Args:
        state: The orchestration state dictionary.

    Returns:
        Tuple of (passed, detail_message).
    """
    flag = state.get("plan_phase_complete", False)
    if flag is True:
        return True, "plan_phase_complete flag is true"
    return False, "plan_phase_complete flag is false or missing"


def check_requirements_file(project_root: Path) -> tuple[bool, str]:
    """Check whether USER_REQUIREMENTS.md exists and is non-empty.

    Args:
        project_root: Absolute path to the project root directory.

    Returns:
        Tuple of (passed, detail_message).
    """
    req_path = project_root / REQUIREMENTS_FILE
    if not req_path.exists():
        return False, "USER_REQUIREMENTS.md not found at {}".format(req_path)
    try:
        content = req_path.read_text(encoding="utf-8").strip()
        if not content:
            return False, "USER_REQUIREMENTS.md exists but is empty"
        return True, "USER_REQUIREMENTS.md exists and is non-empty"
    except OSError as exc:
        return False, "Could not read USER_REQUIREMENTS.md: {}".format(exc)


def check_modules_defined(state: dict) -> tuple[bool, str]:
    """Check whether modules are defined in the orchestration state.

    Modules can be stored as 'modules' (list) or 'modules_status' (list)
    in the state file. At least one module must be defined.

    Args:
        state: The orchestration state dictionary.

    Returns:
        Tuple of (passed, detail_message).
    """
    # Check both possible keys for module definitions
    modules = state.get("modules", [])
    if not modules:
        modules = state.get("modules_status", [])
    if not modules:
        modules = state.get("module_list", [])

    if not isinstance(modules, list):
        return False, "modules field is not a list"
    if len(modules) == 0:
        return False, "No modules defined in orchestration state"
    return True, "{} module(s) defined".format(len(modules))


def check_acceptance_criteria(state: dict) -> tuple[bool, str]:
    """Check whether acceptance criteria are present in the orchestration state.

    Acceptance criteria can be stored as 'acceptance_criteria' (list or dict)
    in the state file.

    Args:
        state: The orchestration state dictionary.

    Returns:
        Tuple of (passed, detail_message).
    """
    criteria = state.get("acceptance_criteria", None)
    if criteria is None:
        return False, "No acceptance_criteria field in orchestration state"
    if isinstance(criteria, list) and len(criteria) == 0:
        return False, "acceptance_criteria list is empty"
    if isinstance(criteria, dict) and len(criteria) == 0:
        return False, "acceptance_criteria dict is empty"
    if isinstance(criteria, str) and not criteria.strip():
        return False, "acceptance_criteria string is empty"

    # Criteria exist and are non-empty
    if isinstance(criteria, list):
        return True, "{} acceptance criterion/criteria defined".format(len(criteria))
    return True, "Acceptance criteria present"


def main() -> int:
    """Main entry point for plan phase completion check.

    Runs all checks, outputs JSON to stdout, and returns the appropriate
    exit code.

    Returns:
        0 if plan phase is complete, 2 if incomplete, 1 on error.
    """
    parser = argparse.ArgumentParser(
        description="Check if the Plan Phase is complete"
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
            "checks": {
                "state_file_loaded": False,
                "plan_phase_complete_flag": False,
                "requirements_file_exists": False,
                "modules_defined": False,
                "acceptance_criteria_present": False,
            },
        }
        print(json.dumps(result, indent=2))
        return 2

    # Run all checks
    checks = {}
    all_passed = True
    first_failure_reason = ""

    # Check 1: plan_phase_complete flag
    passed, detail = check_plan_phase_complete_flag(state)
    checks["plan_phase_complete_flag"] = passed
    if args.verbose:
        status = "PASS" if passed else "FAIL"
        print("[{}] plan_phase_complete_flag: {}".format(status, detail), file=sys.stderr)
    if not passed:
        all_passed = False
        if not first_failure_reason:
            first_failure_reason = detail

    # Check 2: USER_REQUIREMENTS.md exists
    passed, detail = check_requirements_file(project_root)
    checks["requirements_file_exists"] = passed
    if args.verbose:
        status = "PASS" if passed else "FAIL"
        print("[{}] requirements_file_exists: {}".format(status, detail), file=sys.stderr)
    if not passed:
        all_passed = False
        if not first_failure_reason:
            first_failure_reason = detail

    # Check 3: modules defined
    passed, detail = check_modules_defined(state)
    checks["modules_defined"] = passed
    if args.verbose:
        status = "PASS" if passed else "FAIL"
        print("[{}] modules_defined: {}".format(status, detail), file=sys.stderr)
    if not passed:
        all_passed = False
        if not first_failure_reason:
            first_failure_reason = detail

    # Check 4: acceptance criteria present
    passed, detail = check_acceptance_criteria(state)
    checks["acceptance_criteria_present"] = passed
    if args.verbose:
        status = "PASS" if passed else "FAIL"
        print("[{}] acceptance_criteria_present: {}".format(status, detail), file=sys.stderr)
    if not passed:
        all_passed = False
        if not first_failure_reason:
            first_failure_reason = detail

    # Build result
    if all_passed:
        reason = "All plan phase checks passed"
    else:
        reason = first_failure_reason

    result = {
        "complete": all_passed,
        "reason": reason,
        "checks": checks,
    }

    print(json.dumps(result, indent=2))

    if all_passed:
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
