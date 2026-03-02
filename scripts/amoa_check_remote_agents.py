#!/usr/bin/env python3
"""
EOA Check Remote Agents Script

Polls all active remote agents for progress updates using the
MANDATORY Proactive Progress Polling Protocol.

Usage:
    python3 eoa_check_remote_agents.py
    python3 eoa_check_remote_agents.py --agent implementer-1
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


def find_agent_session(data: dict[str, Any], agent_id: str) -> str | None:
    """Find the session name for an AI agent."""
    agents: dict[str, Any] = data.get("registered_agents", {})
    for agent in agents.get("ai_agents", []):
        if agent.get("agent_id") == agent_id:
            session_name: str | None = agent.get("session_name")
            return session_name
    return None


def create_poll_message(_agent_id: str, _poll_count: int) -> str:
    """Create the MANDATORY poll message with all required questions."""
    del _agent_id, _poll_count  # Explicitly mark as unused
    return """## Status Request

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


def send_poll_message(session_name: str, module_name: str, poll_number: int) -> bool:
    """Send poll message via AI Maestro AMP CLI."""
    try:
        message = create_poll_message(module_name, poll_number)
        subject = f"[POLL] Module: {module_name} - Progress Check #{poll_number}"
        result = subprocess.run(
            [
                "amp-send",
                session_name,
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


def poll_agent(data: dict[str, Any], assignment: dict[str, Any]) -> dict[str, Any]:
    """Poll a single agent and update state."""
    agent_id: str | None = assignment.get("agent")
    agent_type: str | None = assignment.get("agent_type")
    module_id: str | None = assignment.get("module")

    # Find module name
    module_name: str = module_id if module_id else "unknown"
    for m in data.get("modules_status", []):
        if m.get("id") == module_id:
            module_name = m.get("name", module_id) or module_name
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
    }

    poll_history: list[dict[str, Any]] = polling.get("poll_history", [])
    poll_history.append(poll_record)

    polling["last_poll"] = now.isoformat()
    polling["poll_count"] = poll_count
    polling["poll_history"] = poll_history
    polling["next_poll_due"] = (now + timedelta(minutes=15)).isoformat()

    assignment["progress_polling"] = polling

    # Send message for AI agents
    result: dict[str, Any] = {
        "agent": agent_id,
        "module": module_name,
        "poll_number": poll_count,
        "sent": False,
    }

    if agent_type == "ai" and agent_id is not None:
        session = find_agent_session(data, agent_id)
        if session:
            sent = send_poll_message(session, module_name, poll_count)
            result["sent"] = sent
            if sent:
                print(f"  ✓ {agent_id} ({module_name}): Poll #{poll_count} sent")
            else:
                print(f"  ⚠ {agent_id} ({module_name}): Failed to send poll")
        else:
            print(f"  ⚠ {agent_id}: Session not found")
    elif agent_type != "ai":
        # Human agents - just record the poll time
        print(f"  ℹ {agent_id} ({module_name}): Human agent - check GitHub")
        result["sent"] = True  # Mark as "sent" for humans

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Poll active agents with MANDATORY questions"
    )
    parser.add_argument("--agent", help="Poll specific agent only")

    args = parser.parse_args()

    # Check if in orchestration phase
    if not EXEC_STATE_FILE.exists():
        print("ERROR: Not in Orchestration Phase")
        return 1

    data, body = parse_frontmatter(EXEC_STATE_FILE)
    if not data:
        print("ERROR: Could not parse orchestration state file")
        return 1

    assignments = data.get("active_assignments", [])

    if not assignments:
        print("No active assignments to poll")
        return 0

    # Filter to specific agent if requested
    if args.agent:
        assignments = [a for a in assignments if a.get("agent") == args.agent]
        if not assignments:
            print(f"No active assignments for agent '{args.agent}'")
            return 1

    # Filter to working agents only (skip pending_verification)
    working_assignments = [
        a
        for a in assignments
        if a.get("status")
        in ("working", "in-progress", "in_progress", "pending_verification")
    ]

    if not working_assignments:
        print("No agents currently working")
        return 0

    print(f"Polling {len(working_assignments)} active agent(s)...")
    print()

    results = []
    for assignment in working_assignments:
        result = poll_agent(data, assignment)
        results.append(result)

    # Write updated state
    if not write_state_file(EXEC_STATE_FILE, data, body):
        return 1

    # Summary
    print()
    sent_count = sum(1 for r in results if r["sent"])
    print(f"Polls sent: {sent_count}/{len(results)}")
    print()
    print("REMINDER: Every poll MUST include the 6 mandatory questions:")
    print("  1. Current progress")
    print("  2. Next steps")
    print("  3. Any issues or problems?")
    print("  4. Anything unclear?")
    print("  5. Any unforeseen difficulties?")
    print("  6. Do you need anything from me?")

    return 0


if __name__ == "__main__":
    sys.exit(main())
