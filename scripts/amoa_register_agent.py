#!/usr/bin/env python3
"""
EOA Register Agent Script

Registers a remote agent (AI or human) for module assignment
during Orchestration Phase.

Usage:
    python3 eoa_register_agent.py ai implementer-1 --session helper-agent-generic
    python3 eoa_register_agent.py human dev-alice
"""

import argparse
import sys
from pathlib import Path

import yaml

# State file location
EXEC_STATE_FILE = Path(".claude/orchestrator-exec-phase.local.md")


def parse_frontmatter(file_path: Path) -> tuple[dict, str]:
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


def write_state_file(file_path: Path, data: dict, body: str) -> bool:
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


def register_ai_agent(data: dict, agent_id: str, session_name: str) -> bool:
    """Register an AI agent."""
    agents = data.get("registered_agents", {})
    ai_agents = agents.get("ai_agents", [])

    # Check if already registered
    for agent in ai_agents:
        if agent.get("agent_id") == agent_id:
            print(f"ERROR: AI agent '{agent_id}' already registered")
            return False

    ai_agents.append(
        {"agent_id": agent_id, "session_name": session_name, "assigned_by_user": True}
    )

    agents["ai_agents"] = ai_agents
    data["registered_agents"] = agents

    print(f"✓ Registered AI agent: {agent_id}")
    print(f"  Session: {session_name}")
    print("  Communication: AI Maestro messages")
    return True


def register_human_developer(data: dict, agent_id: str) -> bool:
    """Register a human developer."""
    agents = data.get("registered_agents", {})
    human_devs = agents.get("human_developers", [])

    # Check if already registered
    for dev in human_devs:
        if dev.get("github_username") == agent_id:
            print(f"ERROR: Human developer '{agent_id}' already registered")
            return False

    human_devs.append({"github_username": agent_id, "assigned_by_user": True})

    agents["human_developers"] = human_devs
    data["registered_agents"] = agents

    print(f"✓ Registered human developer: {agent_id}")
    print("  Communication: GitHub notifications")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Register a remote agent for module assignment"
    )
    parser.add_argument("type", choices=["ai", "human"], help="Agent type")
    parser.add_argument("agent_id", help="Unique identifier for the agent")
    parser.add_argument(
        "--session", "-s", help="AI Maestro session name (required for AI agents)"
    )

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

    # Validate arguments
    if args.type == "ai" and not args.session:
        print("ERROR: --session is required for AI agents")
        print("Usage: /register-agent ai <agent_id> --session <session_name>")
        return 1

    # Register agent
    if args.type == "ai":
        success = register_ai_agent(data, args.agent_id, args.session)
    else:
        success = register_human_developer(data, args.agent_id)

    if success:
        if not write_state_file(EXEC_STATE_FILE, data, body):
            return 1
        print()
        print("Next steps:")
        print(f"  /assign-module <module_id> {args.agent_id}")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
