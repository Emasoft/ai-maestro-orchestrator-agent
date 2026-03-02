#!/usr/bin/env python3
"""
EOA Poll Agent Script

Sends a MANDATORY progress poll with all 6 required questions.
Tracks poll history and issues reported.

Usage:
    python3 eoa_poll_agent.py implementer-1
    python3 eoa_poll_agent.py implementer-1 --record-response --issues "Token expiry unclear"
"""

import argparse
import subprocess
import sys
from datetime import datetime, timezone, timedelta
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
        data: dict[str, Any] = yaml.safe_load(yaml_content) or {}
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


def create_poll_message(_: str, poll_number: int) -> str:
    """Create the MANDATORY poll message with all 6 required questions."""
    return f"""## Status Request - Poll #{poll_number}

Please provide:
1. **Current progress** (% complete, what's done)
2. **Next steps** (what you're working on now)

## MANDATORY Questions (Answer ALL)

3. **Are there any issues or problems?** (technical, environmental, dependencies)
4. **Is anything unclear?** (requirements, acceptance criteria, expected behavior)
5. **Any unforeseen difficulties?** (complexity higher than expected, missing info)
6. **Do you need anything from me?** (documentation, clarification, decisions)

If all is clear, respond: "No blockers. Proceeding as planned."

Expected response time: 5 minutes"""


def send_poll(session: str, module_name: str, poll_number: int) -> bool:
    """Send poll message via AI Maestro AMP CLI."""
    try:
        message = create_poll_message(module_name, poll_number)
        subject = f"[POLL] Module: {module_name} - Progress Check #{poll_number}"
        result = subprocess.run(
            [
                "amp-send",
                session,
                subject,
                message,
                "--priority",
                "normal",
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


def send_poll_to_agent(data: dict[str, Any], body: str, agent_id: str) -> int:
    """Send a progress poll to an agent."""
    assignment = find_assignment(data, agent_id)
    if not assignment:
        print(f"ERROR: No active assignment for '{agent_id}'")
        return 1

    # Check agent type
    if assignment.get("agent_type") != "ai":
        print(f"ERROR: '{agent_id}' is not an AI agent")
        print("Human agents tracked via GitHub")
        return 1

    # Check status
    status = assignment.get("status")
    if status not in ("working", "in-progress", "in_progress"):
        print(f"ERROR: Agent status is '{status}', not actively working")
        return 1

    # Find module name
    module_id: str | None = assignment.get("module")
    module_name: str | None = module_id
    modules_status: list[dict[str, Any]] = data.get("modules_status", [])
    for m in modules_status:
        if m.get("id") == module_id:
            module_name = m.get("name", module_id)
            break

    # Update polling state
    polling: dict[str, Any] = assignment.get("progress_polling", {})
    poll_count: int = polling.get("poll_count", 0) + 1
    now = datetime.now(timezone.utc)

    poll_record: dict[str, Any] = {
        "poll_number": poll_count,
        "timestamp": now.isoformat(),
        "status": "sent",
        "issues_reported": False,
        "clarifications_needed": False,
    }

    poll_history: list[dict[str, Any]] = polling.get("poll_history", [])
    poll_history.append(poll_record)

    polling["last_poll"] = now.isoformat()
    polling["poll_count"] = poll_count
    polling["poll_history"] = poll_history
    polling["next_poll_due"] = (now + timedelta(minutes=15)).isoformat()

    assignment["progress_polling"] = polling

    # Send poll message
    session = find_agent_session(data, agent_id)
    if not session:
        print(f"ERROR: Could not find session for '{agent_id}'")
        return 1

    # module_name is guaranteed to be str at this point (default is module_id which comes from assignment)
    final_module_name: str = module_name if module_name is not None else "unknown"

    print(f"Sending poll #{poll_count} to {agent_id}...")
    sent = send_poll(session, final_module_name, poll_count)

    if sent:
        print(f"Poll #{poll_count} sent to {agent_id}")
        print()
        print("MANDATORY Questions Included:")
        print("  1. Current progress")
        print("  2. Next steps")
        print("  3. Any issues or problems?")
        print("  4. Anything unclear?")
        print("  5. Any unforeseen difficulties?")
        print("  6. Do you need anything from me?")
        print()
        print(f"Next poll due: {polling['next_poll_due']}")
    else:
        print(f"Failed to send poll to {agent_id}")
        return 1

    if not write_state_file(EXEC_STATE_FILE, data, body):
        return 1

    return 0


def record_response(
    data: dict[str, Any],
    body: str,
    agent_id: str,
    issues: str | None,
    clarifications: str | None,
    resolved: bool,
) -> int:
    """Record poll response from agent."""
    assignment = find_assignment(data, agent_id)
    if not assignment:
        print(f"ERROR: No active assignment for '{agent_id}'")
        return 1

    polling: dict[str, Any] = assignment.get("progress_polling", {})
    poll_history: list[dict[str, Any]] = polling.get("poll_history", [])

    if not poll_history:
        print("ERROR: No polls sent yet")
        return 1

    # Update last poll record
    last_poll = poll_history[-1]
    last_poll["status"] = "responded"

    if issues:
        last_poll["issues_reported"] = True
        last_poll["issue_description"] = issues
        last_poll["issue_resolved"] = resolved
        if resolved:
            last_poll["resolution"] = "Resolved by orchestrator"
        print(f"Recorded issue: {issues}")
        print(f"  Resolved: {'Yes' if resolved else 'No - action required!'}")

    if clarifications:
        last_poll["clarifications_needed"] = True
        last_poll["clarification_request"] = clarifications
        print(f"Recorded clarification needed: {clarifications}")

    if not issues and not clarifications:
        print("Recorded: No blockers reported")

    polling["poll_history"] = poll_history
    assignment["progress_polling"] = polling

    if not write_state_file(EXEC_STATE_FILE, data, body):
        return 1

    return 0


def show_poll_history(data: dict[str, Any], agent_id: str) -> int:
    """Show poll history for an agent."""
    assignment = find_assignment(data, agent_id)
    if not assignment:
        print(f"ERROR: No active assignment for '{agent_id}'")
        return 1

    polling: dict[str, Any] = assignment.get("progress_polling", {})

    print(f"Poll History: {agent_id}")
    print("=" * 50)
    print(f"Module: {assignment.get('module')}")
    print(f"Total polls: {polling.get('poll_count', 0)}")
    print(f"Last poll: {polling.get('last_poll', 'Never')}")
    print(f"Next poll due: {polling.get('next_poll_due', 'N/A')}")
    print()

    poll_history: list[dict[str, Any]] = polling.get("poll_history", [])
    if not poll_history:
        print("No polls sent yet")
        return 0

    print("History:")
    for poll in poll_history:
        status_icon = "OK" if poll.get("status") == "responded" else "PENDING"
        print(
            f"  {status_icon} Poll #{poll.get('poll_number')}: {poll.get('timestamp')}"
        )
        if poll.get("issues_reported"):
            resolved_status = "RESOLVED" if poll.get("issue_resolved") else "UNRESOLVED"
            print(f"      Issue: {poll.get('issue_description')} [{resolved_status}]")
        if poll.get("clarifications_needed"):
            print(f"      Clarification: {poll.get('clarification_request')}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Send MANDATORY progress poll to agent"
    )
    parser.add_argument("agent_id", help="Agent identifier")
    parser.add_argument(
        "--record-response", action="store_true", help="Record poll response"
    )
    parser.add_argument("--issues", help="Issues reported by agent")
    parser.add_argument("--clarifications", help="Clarifications requested")
    parser.add_argument("--resolved", action="store_true", help="Issues were resolved")
    parser.add_argument("--history", action="store_true", help="Show poll history")

    args = parser.parse_args()

    # Check if in orchestration phase
    if not EXEC_STATE_FILE.exists():
        print("ERROR: Not in Orchestration Phase")
        return 1

    data, body = parse_frontmatter(EXEC_STATE_FILE)
    if not data:
        print("ERROR: Could not parse orchestration state file")
        return 1

    if args.history:
        return show_poll_history(data, args.agent_id)
    elif args.record_response:
        return record_response(
            data, body, args.agent_id, args.issues, args.clarifications, args.resolved
        )
    else:
        return send_poll_to_agent(data, body, args.agent_id)


if __name__ == "__main__":
    sys.exit(main())
