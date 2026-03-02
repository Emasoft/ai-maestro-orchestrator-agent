#!/usr/bin/env python3
"""
EOA Assign Module Script

Assigns a module to a registered agent and initiates the
Instruction Verification Protocol.

Usage:
    python3 eoa_assign_module.py auth-core implementer-1
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
    """Find an agent by ID. Returns (type, agent_data) or (None, None)."""
    agents = data.get("registered_agents", {})

    for agent in agents.get("ai_agents", []):
        if agent.get("agent_id") == agent_id:
            return "ai", agent

    for dev in agents.get("human_developers", []):
        if dev.get("github_username") == agent_id:
            return "human", dev

    return None, None


def find_module(data: dict[str, Any], module_id: str) -> dict[str, Any] | None:
    """Find a module by ID."""
    modules_status: list[dict[str, Any]] = data.get("modules_status", [])
    for module in modules_status:
        if module.get("id") == module_id:
            return module
    return None


def send_ai_maestro_message(session_name: str, subject: str, message: str) -> bool:
    """Send a message via AI Maestro AMP CLI."""
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
                "task",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0
    except Exception:
        return False


def create_assignment_message(
    module: dict[str, Any], task_uuid: str, plan_id: str
) -> str:
    """Create the assignment message with Instruction Verification request."""
    mod_name = module.get("name", module.get("id"))
    issue = module.get("github_issue", "N/A")
    criteria = module.get("acceptance_criteria", "No criteria defined")

    return f"""## Assignment

You have been assigned to implement: **{mod_name}**

GitHub Issue: {issue}
Task UUID: {task_uuid}
Plan ID: {plan_id}

## Requirements Summary

Implement the {mod_name} module according to the specifications in the GitHub Issue.

## Acceptance Criteria

- {criteria}

## MANDATORY: Instruction Verification

Before you begin implementation, please:

1. **Repeat the key requirements** in your own words (3-5 bullet points)
2. **List any questions** you have about the requirements
3. **Confirm your understanding** of the acceptance criteria

I will verify your understanding before authorizing implementation.

Reply with your understanding summary."""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Assign a module to a registered agent"
    )
    parser.add_argument("module_id", help="ID of the module to assign")
    parser.add_argument("agent_id", help="ID of the registered agent")

    args = parser.parse_args()

    # Check if in orchestration phase
    if not EXEC_STATE_FILE.exists():
        print("ERROR: Not in Orchestration Phase")
        print("Run /start-orchestration first")
        return 1

    data, body = parse_frontmatter(EXEC_STATE_FILE)
    if not data:
        print("ERROR: Could not parse orchestration state file")
        return 1

    # Find module
    module = find_module(data, args.module_id)
    if not module:
        print(f"ERROR: Module '{args.module_id}' not found")
        return 1

    # Check module status
    if module.get("status") not in ("pending", "planned"):
        print(f"ERROR: Module '{args.module_id}' is not available for assignment")
        print(f"Current status: {module.get('status')}")
        return 1

    # Check if already assigned
    if module.get("assigned_to"):
        assigned = module.get("assigned_to")
        print(f"ERROR: Module '{args.module_id}' already assigned to {assigned}")
        print("Use /reassign-module to change assignment")
        return 1

    # Find agent
    agent_type, agent_data = find_agent(data, args.agent_id)
    if not agent_data:
        print(f"ERROR: Agent '{args.agent_id}' not registered")
        print("Use /register-agent to register first")
        return 1

    # Generate task UUID
    task_uuid = f"task-{uuid.uuid4().hex[:12]}"
    plan_id = data.get("plan_id", "unknown")

    # Create assignment record
    assignment = {
        "agent": args.agent_id,
        "agent_type": agent_type,
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

    # Add to active assignments
    assignments = data.get("active_assignments", [])
    assignments.append(assignment)
    data["active_assignments"] = assignments

    # Update module status
    module["assigned_to"] = args.agent_id
    module["status"] = "assigned"

    # Send assignment message for AI agents
    if agent_type == "ai" and agent_data is not None:
        session_name: str | None = agent_data.get("session_name")
        if session_name is None:
            print("ERROR: Agent has no session_name configured")
            return 1
        subject = (
            f"[TASK] Module: {module.get('name', args.module_id)} - UUID: {task_uuid}"
        )
        message = create_assignment_message(module, task_uuid, plan_id)

        print(f"Sending assignment to {session_name}...")
        sent = send_ai_maestro_message(session_name, subject, message)
        if sent:
            print("✓ Assignment message sent via AI Maestro")
        else:
            print("⚠ Could not send via AI Maestro - send manually")
            print(f"\nSubject: {subject}")
            print(f"\n{message}")

    # Write updated state
    if not write_state_file(EXEC_STATE_FILE, data, body):
        return 1

    # Print summary
    print()
    print(f"✓ Module '{args.module_id}' assigned to '{args.agent_id}'")
    print(f"  Task UUID: {task_uuid}")
    print("  Status: pending_verification")
    print()
    print("IMPORTANT: Execute Instruction Verification Protocol")
    print("  1. Wait for agent to repeat instructions")
    print("  2. Verify understanding is correct")
    print("  3. Answer any questions")
    print("  4. Authorize implementation when verified")

    return 0


if __name__ == "__main__":
    sys.exit(main())
