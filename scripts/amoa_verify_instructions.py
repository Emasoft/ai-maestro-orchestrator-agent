#!/usr/bin/env python3
"""
EOA Verify Instructions Script

Manages the Instruction Verification Protocol for remote agents.
Tracks verification status and handles the verification flow.

Usage:
    python3 eoa_verify_instructions.py status implementer-1
    python3 eoa_verify_instructions.py record-repetition implementer-1 --correct
    python3 eoa_verify_instructions.py record-questions implementer-1 --count 2
    python3 eoa_verify_instructions.py authorize implementer-1
"""

import argparse
import subprocess
import sys
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


def find_assignment(data: dict[str, Any], agent_id: str) -> dict[str, Any] | None:
    """Find active assignment for an agent."""
    assignments: list[dict[str, Any]] = data.get("active_assignments", [])
    for assignment in assignments:
        if assignment.get("agent") == agent_id:
            return assignment
    return None


def find_agent_session(data: dict[str, Any], agent_id: str) -> str | None:
    """Find the session name for an AI agent."""
    agents: dict[str, Any] = data.get("registered_agents", {})
    ai_agents: list[dict[str, Any]] = agents.get("ai_agents", [])
    for agent in ai_agents:
        if agent.get("agent_id") == agent_id:
            session_name: str | None = agent.get("session_name")
            return session_name
    return None


def send_message(session: str, subject: str, message: str) -> bool:
    """Send AI Maestro message via AMP CLI."""
    try:
        result = subprocess.run(
            [
                "amp-send",
                session,
                subject,
                message,
                "--priority",
                "high",
                "--type",
                "request",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0
    except Exception:
        return False


def show_status(data: dict[str, Any], agent_id: str) -> int:
    """Show verification status for an agent."""
    assignment = find_assignment(data, agent_id)
    if not assignment:
        print(f"ERROR: No active assignment for '{agent_id}'")
        return 1

    verification = assignment.get("instruction_verification", {})

    print(f"Instruction Verification Status: {agent_id}")
    print("=" * 50)
    print(f"Module: {assignment.get('module')}")
    print(f"Task UUID: {assignment.get('task_uuid')}")
    print()
    print(f"Status: {verification.get('status', 'pending')}")
    print(
        f"Repetition received: {'Yes' if verification.get('repetition_received') else 'No'}"
    )
    print(
        f"Repetition correct: {'Yes' if verification.get('repetition_correct') else 'No'}"
    )
    print(f"Questions asked: {verification.get('questions_asked', 0)}")
    print(f"Questions answered: {verification.get('questions_answered', 0)}")

    auth_at = verification.get("authorized_at")
    if auth_at:
        print(f"Authorized at: {auth_at}")
    else:
        print("Authorized: No")

    # Show next action
    print()
    print("Next Action:")
    status = verification.get("status", "pending")
    if status == "awaiting_repetition":
        print("  Wait for agent to repeat instructions")
    elif status == "correcting":
        print("  Wait for agent to provide corrected understanding")
    elif status == "questioning":
        print("  Answer agent's questions")
    elif status == "verified":
        print("  Agent is authorized to work")
    else:
        print("  Send assignment with verification request")

    return 0


def record_repetition(
    data: dict[str, Any], body: str, agent_id: str, correct: bool
) -> int:
    """Record that agent has repeated instructions."""
    assignment = find_assignment(data, agent_id)
    if not assignment:
        print(f"ERROR: No active assignment for '{agent_id}'")
        return 1

    verification = assignment.get("instruction_verification", {})
    verification["repetition_received"] = True
    verification["repetition_correct"] = correct

    if correct:
        verification["status"] = "questioning"
        print(f"✓ Recorded: {agent_id} correctly repeated instructions")
        print("  Status: questioning (waiting for Q&A)")
    else:
        verification["status"] = "correcting"
        print(f"✗ Recorded: {agent_id} needs to correct understanding")
        print("  Send corrections and wait for revised repetition")

        # Notify agent
        session = find_agent_session(data, agent_id)
        if session:
            module = assignment.get("module")
            send_message(
                session,
                f"RE: [TASK] Module: {module} - CORRECTION NEEDED",
                "Your understanding summary has issues. Please revise and confirm again.",
            )

    assignment["instruction_verification"] = verification

    if not write_state_file(EXEC_STATE_FILE, data, body):
        return 1

    return 0


def record_questions(
    data: dict[str, Any], body: str, agent_id: str, count: int, answered: int
) -> int:
    """Record questions asked by agent."""
    assignment = find_assignment(data, agent_id)
    if not assignment:
        print(f"ERROR: No active assignment for '{agent_id}'")
        return 1

    verification = assignment.get("instruction_verification", {})
    verification["questions_asked"] = count
    verification["questions_answered"] = answered

    if answered >= count:
        verification["status"] = "verified"
        print(f"✓ All {count} questions answered")
        print("  Ready to authorize implementation")
    else:
        remaining = count - answered
        print(f"ℹ {answered}/{count} questions answered")
        print(f"  {remaining} questions remaining")

    assignment["instruction_verification"] = verification

    if not write_state_file(EXEC_STATE_FILE, data, body):
        return 1

    return 0


def authorize_agent(data: dict[str, Any], body: str, agent_id: str) -> int:
    """Authorize agent to begin implementation."""
    assignment = find_assignment(data, agent_id)
    if not assignment:
        print(f"ERROR: No active assignment for '{agent_id}'")
        return 1

    verification = assignment.get("instruction_verification", {})

    # Check prerequisites
    if not verification.get("repetition_received"):
        print("ERROR: Agent has not repeated instructions yet")
        return 1

    if not verification.get("repetition_correct"):
        print("ERROR: Agent's understanding is not verified as correct")
        return 1

    questions = verification.get("questions_asked", 0)
    answered = verification.get("questions_answered", 0)
    if questions > answered:
        print(f"ERROR: {questions - answered} questions still unanswered")
        return 1

    # Authorize
    now = datetime.now(timezone.utc)
    verification["status"] = "verified"
    verification["authorized_at"] = now.isoformat()
    assignment["instruction_verification"] = verification
    assignment["status"] = "working"

    # Send authorization message
    session = find_agent_session(data, agent_id)
    if session:
        module = assignment.get("module")
        message = """Your understanding is verified. You may begin implementation.

**Reminders:**
- Report progress every 15 minutes
- Ask questions immediately if you encounter blockers
- Do NOT create PR until all tests pass
- Follow the 4-verification-loop protocol for PR requests

Begin work now."""

        send_message(
            session, f"RE: [TASK] Module: {module} - AUTHORIZED TO PROCEED", message
        )
        print(f"✓ Authorization message sent to {agent_id}")

    if not write_state_file(EXEC_STATE_FILE, data, body):
        return 1

    print(f"✓ Agent '{agent_id}' authorized to implement")
    print(f"  Module: {assignment.get('module')}")
    print(f"  Authorized at: {now.isoformat()}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manage Instruction Verification Protocol"
    )
    parser.add_argument(
        "action",
        choices=["status", "record-repetition", "record-questions", "authorize"],
        help="Action to perform",
    )
    parser.add_argument("agent_id", help="Agent identifier")
    parser.add_argument("--correct", action="store_true", help="Repetition was correct")
    parser.add_argument(
        "--count", type=int, default=0, help="Number of questions asked"
    )
    parser.add_argument(
        "--answered", type=int, default=0, help="Number of questions answered"
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

    if args.action == "status":
        return show_status(data, args.agent_id)
    elif args.action == "record-repetition":
        return record_repetition(data, body, args.agent_id, args.correct)
    elif args.action == "record-questions":
        return record_questions(data, body, args.agent_id, args.count, args.answered)
    elif args.action == "authorize":
        return authorize_agent(data, body, args.agent_id)

    return 1


if __name__ == "__main__":
    sys.exit(main())
