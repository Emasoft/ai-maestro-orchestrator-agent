#!/usr/bin/env python3
"""
EOA Update Verification -- Instruction Update Verification Protocol Manager

Manages the Instruction Update Verification Protocol for mid-implementation
changes. This is DIFFERENT from the initial Instruction Verification Protocol
(managed by eoa_verify_instructions.py). This script handles changes that
arrive AFTER an agent has already started working.

The 5-stage verification flow:
  1. pending_receipt   -- Update sent, waiting for agent to acknowledge receipt
  2. awaiting_feasibility -- Agent received update, assessing feasibility impact
  3. addressing_concerns  -- Agent raised concerns, orchestrator resolving them
  4. ready_to_resume      -- Concerns resolved, agent authorized to resume work
  5. resumed              -- Agent confirmed resumption of work with new instructions

State is stored in: .emasoft/update-verification-state.json

NO external dependencies -- Python 3.8+ stdlib only.

Subcommands:
    send              -- Create a new update verification entry (stage: pending_receipt)
    record-receipt    -- Record that the agent acknowledged the update (-> awaiting_feasibility)
    record-feasibility -- Record feasibility assessment result (-> addressing_concerns or ready_to_resume)
    resolve-concerns  -- Record that concerns have been resolved (-> ready_to_resume)
    authorize-resume  -- Authorize the agent to resume work (-> resumed)
    history           -- Show the history of transitions for an update
    pending           -- List all updates that have not reached "resumed" stage

Usage:
    python3 eoa_update_verification.py send --update-id UV-001 --agent implementer-1 --notes "Changed auth module API"
    python3 eoa_update_verification.py record-receipt --update-id UV-001 --agent implementer-1
    python3 eoa_update_verification.py record-feasibility --update-id UV-001 --agent implementer-1 --notes "Feasible, no concerns"
    python3 eoa_update_verification.py record-feasibility --update-id UV-001 --agent implementer-1 --notes "Concern: API backward compat" --has-concerns
    python3 eoa_update_verification.py resolve-concerns --update-id UV-001 --agent implementer-1 --notes "Backward compat handled via adapter"
    python3 eoa_update_verification.py authorize-resume --update-id UV-001 --agent implementer-1
    python3 eoa_update_verification.py history --update-id UV-001
    python3 eoa_update_verification.py pending

Exit codes:
    0 - Success
    1 - Error (invalid state transition, missing arguments, file I/O error, etc.)

Examples:
    # Full flow for a mid-implementation instruction update:

    # Step 1: Orchestrator sends update to agent
    python3 eoa_update_verification.py send \
        --update-id UV-001 --agent implementer-1 \
        --notes "Changed auth module: use OAuth2 instead of API keys"

    # Step 2: Agent acknowledges receipt
    python3 eoa_update_verification.py record-receipt \
        --update-id UV-001 --agent implementer-1

    # Step 3a: Agent reports feasibility with no concerns
    python3 eoa_update_verification.py record-feasibility \
        --update-id UV-001 --agent implementer-1 \
        --notes "OAuth2 migration feasible, estimated 4 hours"

    # Step 4: Orchestrator authorizes resume
    python3 eoa_update_verification.py authorize-resume \
        --update-id UV-001 --agent implementer-1

    # Alternative Step 3b: Agent raises concerns
    python3 eoa_update_verification.py record-feasibility \
        --update-id UV-001 --agent implementer-1 \
        --notes "OAuth2 requires new dependency" --has-concerns

    # Step 3c: Orchestrator resolves concerns
    python3 eoa_update_verification.py resolve-concerns \
        --update-id UV-001 --agent implementer-1 \
        --notes "Approved: add oauth2-client library"

    # Then Step 4 as above...
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


# State file location relative to the project root
STATE_FILE_REL = ".emasoft/update-verification-state.json"

# Valid stages in order
STAGES = [
    "pending_receipt",
    "awaiting_feasibility",
    "addressing_concerns",
    "ready_to_resume",
    "resumed",
]

# Valid transitions: from_stage -> list of valid next stages
VALID_TRANSITIONS = {
    "pending_receipt": ["awaiting_feasibility"],
    "awaiting_feasibility": ["addressing_concerns", "ready_to_resume"],
    "addressing_concerns": ["ready_to_resume"],
    "ready_to_resume": ["resumed"],
    "resumed": [],  # Terminal stage
}


def now_iso() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def load_state(project_root: Path) -> dict:
    """Load update verification state from the JSON file.

    Args:
        project_root: Absolute path to the project root directory.

    Returns:
        A dictionary with the state data. Returns a new empty state
        if the file does not exist or is invalid.
    """
    state_path = project_root / STATE_FILE_REL
    if not state_path.exists():
        return {"updates": {}}

    try:
        content = state_path.read_text(encoding="utf-8").strip()
        if not content:
            return {"updates": {}}
        data = json.loads(content)
        if not isinstance(data, dict):
            return {"updates": {}}
        if "updates" not in data:
            data["updates"] = {}
        return data
    except (json.JSONDecodeError, OSError):
        return {"updates": {}}


def save_state(project_root: Path, state: dict) -> bool:
    """Save update verification state to the JSON file.

    Creates the .emasoft directory if it does not exist.

    Args:
        project_root: Absolute path to the project root directory.
        state: The state dictionary to save.

    Returns:
        True if saved successfully, False on error.
    """
    state_path = project_root / STATE_FILE_REL
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return True
    except OSError as exc:
        print("ERROR: Could not save state file: {}".format(exc), file=sys.stderr)
        return False


def get_update(state: dict, update_id: str) -> dict | None:
    """Get an update entry by ID.

    Args:
        state: The full state dictionary.
        update_id: The update identifier string.

    Returns:
        The update dictionary, or None if not found.
    """
    result: dict | None = state.get("updates", {}).get(update_id)  # explicit type to satisfy mypy no-any-return
    return result


def transition_stage(
    update: dict, target_stage: str, notes: str
) -> tuple[bool, str]:
    """Transition an update to a new stage.

    Validates that the transition is allowed according to VALID_TRANSITIONS.

    Args:
        update: The update entry dictionary.
        target_stage: The stage to transition to.
        notes: Notes for the transition log entry.

    Returns:
        Tuple of (success, message).
    """
    current_stage = update.get("current_stage", "pending_receipt")

    if target_stage not in VALID_TRANSITIONS.get(current_stage, []):
        return False, "Invalid transition: {} -> {} (allowed: {})".format(
            current_stage,
            target_stage,
            ", ".join(VALID_TRANSITIONS.get(current_stage, [])),
        )

    # Record the transition
    transition_entry = {
        "from": current_stage,
        "to": target_stage,
        "timestamp": now_iso(),
        "notes": notes,
    }

    if "history" not in update:
        update["history"] = []
    update["history"].append(transition_entry)

    update["current_stage"] = target_stage
    update["updated_at"] = now_iso()

    return True, "Transitioned from {} to {}".format(current_stage, target_stage)


# --- Subcommand handlers ---


def cmd_send(project_root: Path, args) -> int:
    """Handle the 'send' subcommand: create a new update verification entry."""
    state = load_state(project_root)

    update_id = args.update_id
    if update_id in state.get("updates", {}):
        print("ERROR: Update ID '{}' already exists".format(update_id), file=sys.stderr)
        return 1

    update = {
        "update_id": update_id,
        "agent": args.agent,
        "current_stage": "pending_receipt",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "notes": args.notes if args.notes else "",
        "history": [
            {
                "from": None,
                "to": "pending_receipt",
                "timestamp": now_iso(),
                "notes": "Update sent to agent: {}".format(args.notes if args.notes else "(no notes)"),
            }
        ],
    }

    state["updates"][update_id] = update

    if not save_state(project_root, state):
        return 1

    print("Created update verification: {} (agent: {}, stage: pending_receipt)".format(
        update_id, args.agent
    ))
    return 0


def cmd_record_receipt(project_root: Path, args) -> int:
    """Handle the 'record-receipt' subcommand."""
    state = load_state(project_root)
    update = get_update(state, args.update_id)

    if update is None:
        print("ERROR: Update ID '{}' not found".format(args.update_id), file=sys.stderr)
        return 1

    if args.agent and update.get("agent") != args.agent:
        print(
            "ERROR: Agent mismatch: update is for '{}', got '{}'".format(
                update.get("agent"), args.agent
            ),
            file=sys.stderr,
        )
        return 1

    notes = args.notes if args.notes else "Agent acknowledged receipt"
    success, msg = transition_stage(update, "awaiting_feasibility", notes)

    if not success:
        print("ERROR: {}".format(msg), file=sys.stderr)
        return 1

    if not save_state(project_root, state):
        return 1

    print("{} -- {} (agent: {})".format(args.update_id, msg, update.get("agent")))
    return 0


def cmd_record_feasibility(project_root: Path, args) -> int:
    """Handle the 'record-feasibility' subcommand."""
    state = load_state(project_root)
    update = get_update(state, args.update_id)

    if update is None:
        print("ERROR: Update ID '{}' not found".format(args.update_id), file=sys.stderr)
        return 1

    if args.agent and update.get("agent") != args.agent:
        print(
            "ERROR: Agent mismatch: update is for '{}', got '{}'".format(
                update.get("agent"), args.agent
            ),
            file=sys.stderr,
        )
        return 1

    notes = args.notes if args.notes else "Feasibility assessed"

    if args.has_concerns:
        target_stage = "addressing_concerns"
    else:
        target_stage = "ready_to_resume"

    success, msg = transition_stage(update, target_stage, notes)

    if not success:
        print("ERROR: {}".format(msg), file=sys.stderr)
        return 1

    if not save_state(project_root, state):
        return 1

    print("{} -- {} (agent: {})".format(args.update_id, msg, update.get("agent")))
    return 0


def cmd_resolve_concerns(project_root: Path, args) -> int:
    """Handle the 'resolve-concerns' subcommand."""
    state = load_state(project_root)
    update = get_update(state, args.update_id)

    if update is None:
        print("ERROR: Update ID '{}' not found".format(args.update_id), file=sys.stderr)
        return 1

    if args.agent and update.get("agent") != args.agent:
        print(
            "ERROR: Agent mismatch: update is for '{}', got '{}'".format(
                update.get("agent"), args.agent
            ),
            file=sys.stderr,
        )
        return 1

    notes = args.notes if args.notes else "Concerns resolved"
    success, msg = transition_stage(update, "ready_to_resume", notes)

    if not success:
        print("ERROR: {}".format(msg), file=sys.stderr)
        return 1

    if not save_state(project_root, state):
        return 1

    print("{} -- {} (agent: {})".format(args.update_id, msg, update.get("agent")))
    return 0


def cmd_authorize_resume(project_root: Path, args) -> int:
    """Handle the 'authorize-resume' subcommand."""
    state = load_state(project_root)
    update = get_update(state, args.update_id)

    if update is None:
        print("ERROR: Update ID '{}' not found".format(args.update_id), file=sys.stderr)
        return 1

    if args.agent and update.get("agent") != args.agent:
        print(
            "ERROR: Agent mismatch: update is for '{}', got '{}'".format(
                update.get("agent"), args.agent
            ),
            file=sys.stderr,
        )
        return 1

    notes = args.notes if args.notes else "Agent authorized to resume with updated instructions"
    success, msg = transition_stage(update, "resumed", notes)

    if not success:
        print("ERROR: {}".format(msg), file=sys.stderr)
        return 1

    if not save_state(project_root, state):
        return 1

    print("{} -- {} (agent: {})".format(args.update_id, msg, update.get("agent")))
    return 0


def cmd_history(project_root: Path, args) -> int:
    """Handle the 'history' subcommand: show transition history for an update."""
    state = load_state(project_root)
    update = get_update(state, args.update_id)

    if update is None:
        print("ERROR: Update ID '{}' not found".format(args.update_id), file=sys.stderr)
        return 1

    print("Update Verification History: {}".format(args.update_id))
    print("=" * 60)
    print("Agent:         {}".format(update.get("agent", "unknown")))
    print("Current stage: {}".format(update.get("current_stage", "unknown")))
    print("Created at:    {}".format(update.get("created_at", "unknown")))
    print("Updated at:    {}".format(update.get("updated_at", "unknown")))
    print()

    history = update.get("history", [])
    if not history:
        print("No transitions recorded.")
        return 0

    print("Transitions:")
    for i, entry in enumerate(history, 1):
        from_stage = entry.get("from", "(initial)")
        to_stage = entry.get("to", "unknown")
        timestamp = entry.get("timestamp", "unknown")
        notes = entry.get("notes", "")
        print("  {}. {} -> {} [{}]".format(i, from_stage, to_stage, timestamp))
        if notes:
            print("     Notes: {}".format(notes))

    print()
    print("=" * 60)
    return 0


def cmd_pending(project_root: Path, args) -> int:
    """Handle the 'pending' subcommand: list all non-resumed updates."""
    state = load_state(project_root)
    updates = state.get("updates", {})

    pending = []
    for uid, update in updates.items():
        stage = update.get("current_stage", "unknown")
        if stage != "resumed":
            pending.append(update)

    if not pending:
        print("No pending update verifications.")
        return 0

    print("Pending Update Verifications ({})".format(len(pending)))
    print("=" * 60)
    for update in pending:
        uid = update.get("update_id", "unknown")
        agent = update.get("agent", "unknown")
        stage = update.get("current_stage", "unknown")
        updated = update.get("updated_at", "unknown")
        notes = update.get("notes", "")
        print("  {} | agent: {} | stage: {} | updated: {}".format(
            uid, agent, stage, updated
        ))
        if notes:
            print("    Notes: {}".format(notes))
    print("=" * 60)
    return 0


def main() -> int:
    """Main entry point for the update verification protocol manager.

    Parses subcommands and dispatches to the appropriate handler.

    Returns:
        0 on success, 1 on error.
    """
    parser = argparse.ArgumentParser(
        description="Manage the Instruction Update Verification Protocol"
    )
    parser.add_argument(
        "--project-root",
        type=str,
        default=".",
        help="Path to the project root directory (default: current directory)",
    )

    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommand to execute")
    subparsers.required = True

    # --- send ---
    p_send = subparsers.add_parser("send", help="Create a new update verification entry")
    p_send.add_argument("--update-id", required=True, help="Unique update identifier (e.g. UV-001)")
    p_send.add_argument("--agent", required=True, help="Target agent identifier")
    p_send.add_argument("--notes", default="", help="Notes describing the update")

    # --- record-receipt ---
    p_receipt = subparsers.add_parser("record-receipt", help="Record agent acknowledged the update")
    p_receipt.add_argument("--update-id", required=True, help="Update identifier")
    p_receipt.add_argument("--agent", default="", help="Agent identifier (for validation)")
    p_receipt.add_argument("--notes", default="", help="Optional notes")

    # --- record-feasibility ---
    p_feas = subparsers.add_parser("record-feasibility", help="Record feasibility assessment")
    p_feas.add_argument("--update-id", required=True, help="Update identifier")
    p_feas.add_argument("--agent", default="", help="Agent identifier (for validation)")
    p_feas.add_argument("--notes", default="", help="Feasibility assessment notes")
    p_feas.add_argument(
        "--has-concerns",
        action="store_true",
        help="Agent has concerns that need resolution (transitions to addressing_concerns instead of ready_to_resume)",
    )

    # --- resolve-concerns ---
    p_resolve = subparsers.add_parser("resolve-concerns", help="Record that concerns have been resolved")
    p_resolve.add_argument("--update-id", required=True, help="Update identifier")
    p_resolve.add_argument("--agent", default="", help="Agent identifier (for validation)")
    p_resolve.add_argument("--notes", default="", help="Resolution notes")

    # --- authorize-resume ---
    p_auth = subparsers.add_parser("authorize-resume", help="Authorize agent to resume work")
    p_auth.add_argument("--update-id", required=True, help="Update identifier")
    p_auth.add_argument("--agent", default="", help="Agent identifier (for validation)")
    p_auth.add_argument("--notes", default="", help="Optional notes")

    # --- history ---
    p_hist = subparsers.add_parser("history", help="Show transition history for an update")
    p_hist.add_argument("--update-id", required=True, help="Update identifier")

    # --- pending ---
    subparsers.add_parser("pending", help="List all updates not yet at 'resumed' stage")

    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()

    # Dispatch to subcommand handler
    handlers = {
        "send": cmd_send,
        "record-receipt": cmd_record_receipt,
        "record-feasibility": cmd_record_feasibility,
        "resolve-concerns": cmd_resolve_concerns,
        "authorize-resume": cmd_authorize_resume,
        "history": cmd_history,
        "pending": cmd_pending,
    }

    handler = handlers.get(args.subcommand)
    if handler is None:
        print("ERROR: Unknown subcommand '{}'".format(args.subcommand), file=sys.stderr)
        return 1

    return handler(project_root, args)


if __name__ == "__main__":
    sys.exit(main())
