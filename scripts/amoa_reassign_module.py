#!/usr/bin/env python3
"""
EOA Reassign Module Script

Reassigns a module from one agent to another.
Notifies both old and new agents.

Usage:
    python3 eoa_reassign_module.py auth-core --to implementer-2
"""

import argparse
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# State file location
EXEC_STATE_FILE = Path(".claude/orchestrator-exec-phase.local.md")


def parse_frontmatter(file_path: Path) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter and return (data, body)."""
    if not file_path.exists():
        return {}, ""

    content = file_path.read_text(encoding="utf-8")

    if not content.startswith("---"):
        return {}, content

    end_index = content.find("---", 3)
    if end_index == -1:
        return {}, content

    yaml_content = content[3:end_index].strip()
    body = content[end_index + 3 :].strip()

    try:
        data = yaml.safe_load(yaml_content) or {}
        return data, body
    except yaml.YAMLError:
        return {}, content


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
                "notification",
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

    args = parser.parse_args()

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

    # Notify old agent (AI agents only)
    if old_type == "ai" and old_agent_data:
        session = old_agent_data.get("session_name")
        if isinstance(session, str):
            send_ai_maestro_message(
                session,
                f"[STOP] Module: {module.get('name', args.module_id)} - Reassigned",
                "This module has been reassigned to another agent.\n"
                "Please stop work immediately and report current progress.\n"
                "Do NOT commit any incomplete changes.",
            )
            print(f"Notified old agent: {old_agent}")

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
