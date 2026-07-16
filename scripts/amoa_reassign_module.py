#!/usr/bin/env python3
"""
AMOA Reassign Module Script

Reassigns a module from one agent to another.
Notifies both old and new agents.

--reason is REQUIRED and is delivered verbatim to the agent losing the module:
taking work from an agent is a refusal of its work, and a refusal is a design
review, not a verdict (USER-ratified fleet principle, 2026-07-16).

Usage:
    python3 amoa_reassign_module.py auth-core --to implementer-2 \
        --reason "Blocked 3 polls on the OAuth callback; impl-2 has the token-store context. Ping me if you were nearly through it."
"""

import argparse
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# WHY: shared state helpers deduped into shared/amoa_state.py (TRDD-03DYGXJW jscpd gate)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shared"))
from amoa_state import EXEC_STATE_FILE
from amoa_state import parse_frontmatter as _shared_parse_frontmatter


def parse_frontmatter(file_path: Path) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter and return (data, body)."""
    return _shared_parse_frontmatter(file_path)


def write_state_file(file_path: Path, data: dict[str, Any], body: str) -> bool:
    """Write a state file with YAML frontmatter."""
    try:
        yaml_content = yaml.dump(
            data, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
        content = f"---\n{yaml_content}---\n\n{body}"
        file_path.write_text(content, encoding="utf-8")
        return True
    except Exception as e:
        print(f"ERROR: Failed to write state file: {e}")
        return False


def find_agent(
    data: dict[str, Any], agent_id: str
) -> tuple[str | None, dict[str, Any] | None]:
    """Find an agent by ID."""
    agents = data.get("registered_agents", {})

    for agent in agents.get("ai_agents", []):
        if agent.get("agent_id") == agent_id:
            return "ai", agent

    for dev in agents.get("human_developers", []):
        if dev.get("github_username") == agent_id:
            return "human", dev

    return None, None


def send_ai_maestro_message(session_name: str, subject: str, message: str) -> bool:
    """Send a message via AI Maestro."""
    try:
        result = subprocess.run(
            [
                "amp-send",
                session_name,
                subject,
                message,
                "--priority",
                "high",
                "--type",
                "info",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        return result.returncode == 0
    except Exception:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reassign a module to a different agent"
    )
    parser.add_argument("module_id", help="ID of the module to reassign")
    parser.add_argument(
        "--to", required=True, dest="new_agent", help="ID of the new agent"
    )
    # A reassignment is a REFUSAL of the current agent's work, and the
    # USER-ratified "an approver is a guide, not a gate" principle (2026-07-16)
    # forbids a reasonless no. This is required, not defaulted: a default reason
    # would be a content-free string that satisfies the check and tells the
    # agent nothing — the exact failure the principle exists to prevent.
    parser.add_argument(
        "--reason",
        required=True,
        help=(
            "WHY the module is being taken from the current agent. Must carry "
            "the precise defect, the bar for acceptance, and an invitation to "
            "respond — see --help output on refusal."
        ),
    )

    args = parser.parse_args()

    if not args.reason.strip():
        print(
            "ERROR: --reason must not be empty.\n"
            "\n"
            "Taking a module from an agent is a refusal of its work, and a\n"
            "refusal is a design review, not a verdict. The reason you send it\n"
            "must carry all four elements:\n"
            "  1. The precise defect — which behavior/output/step, not 'not working out'.\n"
            "  2. The bar — what would have kept the assignment.\n"
            "  3. An explicit invitation to respond (it may be right about half your call).\n"
            "  4. A push toward alternatives — refuse the implementation, never the need.\n"
            "\n"
            "An agent overridden without explanation stops proposing approaches,\n"
            "and you never see what you lost.",
            file=sys.stderr,
        )
        return 1

    # Check if in orchestration phase
    if not EXEC_STATE_FILE.exists():
        print("ERROR: Not in Orchestration Phase")
        return 1

    data, body = parse_frontmatter(EXEC_STATE_FILE)
    if not data:
        print("ERROR: Could not parse orchestration state file")
        return 1

    # Find module
    module = None
    for m in data.get("modules_status", []):
        if m.get("id") == args.module_id:
            module = m
            break

    if not module:
        print(f"ERROR: Module '{args.module_id}' not found")
        return 1

    # Check module status
    if module.get("status") == "complete":
        print("ERROR: Cannot reassign completed module")
        return 1

    old_agent = module.get("assigned_to")
    if not old_agent:
        print("ERROR: Module is not currently assigned")
        print("Use /assign-module instead")
        return 1

    if old_agent == args.new_agent:
        print(f"ERROR: Module already assigned to '{args.new_agent}'")
        return 1

    # Find new agent
    new_type, new_agent_data = find_agent(data, args.new_agent)
    if not new_agent_data:
        print(f"ERROR: Agent '{args.new_agent}' not registered")
        return 1

    # Find old agent for notification
    old_type, old_agent_data = find_agent(data, old_agent)

    # Notify old agent (AI agents only). The reason travels IN the message: a
    # --reason that only lands in a log is a decision the agent never received,
    # which is the same as no reason at all. The reply invitation is part of the
    # payload for the same rationale — the thread stays open for its
    # counter-arguments.
    if old_type == "ai" and old_agent_data:
        session = old_agent_data.get("session_name")
        if isinstance(session, str):
            send_ai_maestro_message(
                session,
                f"[STOP] Module: {module.get('name', args.module_id)} - Reassigned",
                f"This module has been reassigned to another agent.\n"
                f"\n"
                f"WHY: {args.reason}\n"
                f"\n"
                f"Please stop work immediately and report current progress.\n"
                f"Do NOT commit any incomplete changes.\n"
                f"\n"
                f"This is a design review, not a verdict on you. If you think\n"
                f"the reason above is wrong or incomplete, reply and say so —\n"
                f"the decision is reversible and you may be right.",
            )
            print(f"Notified old agent: {old_agent} (reason delivered)")
        else:
            # No session to message = the refusal cannot be delivered. Say so
            # loudly rather than letting the reassignment look communicated.
            print(
                f"WARNING: agent '{old_agent}' has no session_name — the reason "
                f"was NOT delivered. Tell it another way.",
                file=sys.stderr,
            )

    # Remove old assignment
    assignments = data.get("active_assignments", [])
    data["active_assignments"] = [
        a for a in assignments if a.get("module") != args.module_id
    ]

    # Create new assignment
    task_uuid = f"task-{uuid.uuid4().hex[:12]}"

    new_assignment = {
        "agent": args.new_agent,
        "agent_type": new_type,
        "module": args.module_id,
        "github_issue": module.get("github_issue"),
        "task_uuid": task_uuid,
        "status": "pending_verification",
        "assigned_at": datetime.now(timezone.utc).isoformat(),
        "instruction_verification": {
            "status": "awaiting_repetition",
            "repetition_received": False,
            "repetition_correct": False,
            "questions_asked": 0,
            "questions_answered": 0,
            "authorized_at": None,
        },
        "progress_polling": {
            "last_poll": None,
            "poll_count": 0,
            "poll_history": [],
            "next_poll_due": None,
        },
    }

    data["active_assignments"].append(new_assignment)

    # Update module
    module["assigned_to"] = args.new_agent
    module["status"] = "assigned"

    # Notify new agent (AI agents only)
    if new_type == "ai" and new_agent_data:
        session = new_agent_data.get("session_name")
        if isinstance(session, str):
            criteria = module.get("acceptance_criteria", "See GitHub Issue")
            message = f"""## Assignment (Reassigned)

You have been assigned to implement: **{module.get("name", args.module_id)}**

GitHub Issue: {module.get("github_issue", "N/A")}
Task UUID: {task_uuid}

## Acceptance Criteria
- {criteria}

## MANDATORY: Instruction Verification

Before you begin, please:
1. Repeat the key requirements in your own words
2. List any questions
3. Confirm your understanding

I will verify before authorizing implementation."""

            send_ai_maestro_message(
                session,
                f"[TASK] Module: {module.get('name', args.module_id)} - UUID: {task_uuid}",
                message,
            )
            print(f"Notified new agent: {args.new_agent}")

    # Write state
    if not write_state_file(EXEC_STATE_FILE, data, body):
        return 1

    print()
    print(f"✓ Reassigned module '{args.module_id}'")
    print(f"  From: {old_agent}")
    print(f"  To: {args.new_agent}")
    print(f"  New UUID: {task_uuid}")
    print()
    print("IMPORTANT: Execute Instruction Verification Protocol with new agent")

    return 0


if __name__ == "__main__":
    sys.exit(main())
