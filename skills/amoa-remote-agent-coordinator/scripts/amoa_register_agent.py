#!/usr/bin/env python3
"""
EOA Agent Registration

Registers a new remote agent in the orchestrator's tracking system.
Creates the agent folder structure and metadata file.

Usage:
    python eoa_register_agent.py --name AGENT_NAME --platform PLATFORM --architecture ARCH
    python eoa_register_agent.py --name helper-agent-macos-arm64 --platform macos --architecture arm64
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_design_root() -> Path:
    """Get Design storage root from environment or current directory."""
    if "ATLAS_STORAGE_ROOT" in os.environ:
        return Path(os.environ["ATLAS_STORAGE_ROOT"])
    if "PROJECT_ROOT" in os.environ:
        return Path(os.environ["PROJECT_ROOT"]) / "design"
    return Path.cwd() / "design"


def register_agent(
    name: str,
    platform: str,
    architecture: str,
    session_id: str | None = None,
    design_root: Path | None = None,
) -> dict:
    """Register a new agent in the orchestrator's tracking system."""
    if design_root is None:
        design_root = get_design_root()

    agents_dir = design_root / "agents"
    agent_dir = agents_dir / name

    # Check if already registered
    agent_json = agent_dir / "agent.json"
    if agent_json.exists():
        existing = json.loads(agent_json.read_text())
        existing["last_activity"] = datetime.now(timezone.utc).isoformat()
        if session_id:
            existing["ai_maestro_session"] = session_id
        agent_json.write_text(json.dumps(existing, indent=2))
        return {
            "success": True,
            "action": "updated",
            "agent_name": name,
            "agent_dir": str(agent_dir),
            "message": "Agent already registered, updated last_activity",
        }

    # Create agent directory structure
    directories = [
        agent_dir,
        agent_dir / "received" / "reports",
        agent_dir / "received" / "acks",
        agent_dir / "received" / "sync",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    # Create agent metadata
    metadata = {
        "schema_version": "2.0.0",
        "agent_name": name,
        "agent_type": "remote",
        "platform": platform,
        "architecture": architecture,
        "first_seen": datetime.now(timezone.utc).isoformat(),
        "last_activity": datetime.now(timezone.utc).isoformat(),
        "total_tasks_assigned": 0,
        "total_tasks_completed": 0,
        "total_documents_received": 0,
        "ai_maestro_session": session_id or "",
    }

    agent_json.write_text(json.dumps(metadata, indent=2))

    # Update orchestrator metadata
    orchestrator_json = design_root / "orchestrator.json"
    if orchestrator_json.exists():
        try:
            orch_meta = json.loads(orchestrator_json.read_text())
            if name not in orch_meta.get("registered_agents", []):
                orch_meta.setdefault("registered_agents", []).append(name)
                orchestrator_json.write_text(json.dumps(orch_meta, indent=2))
        except json.JSONDecodeError:
            pass

    return {
        "success": True,
        "action": "registered",
        "agent_name": name,
        "agent_dir": str(agent_dir),
        "platform": platform,
        "architecture": architecture,
        "message": f"Agent {name} registered successfully",
    }


def list_agents(design_root: Path | None = None) -> list[dict]:
    """List all registered agents."""
    if design_root is None:
        design_root = get_design_root()

    agents_dir = design_root / "agents"
    agents: list[dict[str, object]] = []

    if not agents_dir.exists():
        return agents

    for agent_dir in agents_dir.iterdir():
        if not agent_dir.is_dir():
            continue
        if agent_dir.name.startswith("."):
            continue

        agent_json = agent_dir / "agent.json"
        if agent_json.exists():
            try:
                metadata = json.loads(agent_json.read_text())
                agents.append(metadata)
            except json.JSONDecodeError:
                agents.append(
                    {"agent_name": agent_dir.name, "error": "invalid metadata"}
                )
        else:
            agents.append({"agent_name": agent_dir.name, "error": "no metadata"})

    return agents


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Register a remote agent in EOA orchestrator"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # register command
    reg_parser = subparsers.add_parser("register", help="Register a new agent")
    reg_parser.add_argument(
        "--name", required=True, help="Agent full name (e.g., helper-agent-macos-arm64)"
    )
    reg_parser.add_argument(
        "--platform",
        required=True,
        choices=["macos", "linux", "windows"],
        help="Platform",
    )
    reg_parser.add_argument(
        "--architecture",
        required=True,
        choices=["x64", "arm64", "universal"],
        help="Architecture",
    )
    reg_parser.add_argument("--session", help="AI Maestro session ID")
    reg_parser.add_argument("--design-root", type=Path, help="Design storage root")
    reg_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # list command
    list_parser = subparsers.add_parser("list", help="List registered agents")
    list_parser.add_argument("--design-root", type=Path, help="Design storage root")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.command:
        # Default to register if arguments provided
        if len(sys.argv) > 1:
            parser.print_help()
        return 1

    if args.command == "register":
        result = register_agent(
            name=args.name,
            platform=args.platform,
            architecture=args.architecture,
            session_id=args.session,
            design_root=getattr(args, 'design_root', None),
        )

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result["success"]:
                print(f"[{result['action'].upper()}] {result['agent_name']}")
                print(f"  Directory: {result['agent_dir']}")
                print(f"  Message: {result['message']}")
            else:
                print(f"ERROR: {result.get('message', 'Unknown error')}")
                return 1

    elif args.command == "list":
        agents = list_agents(getattr(args, 'design_root', None))

        if args.json:
            print(json.dumps(agents, indent=2))
        else:
            if not agents:
                print("No agents registered")
            else:
                print(f"\nRegistered Agents ({len(agents)}):\n")
                for agent in agents:
                    name = agent.get("agent_name", "unknown")
                    platform = agent.get("platform", "?")
                    arch = agent.get("architecture", "?")
                    last = (
                        agent.get("last_activity", "?")[:10]
                        if agent.get("last_activity")
                        else "?"
                    )
                    tasks = agent.get("total_tasks_completed", 0)
                    print(f"  {name}")
                    print(f"    Platform: {platform}/{arch}")
                    print(f"    Last active: {last}")
                    print(f"    Tasks completed: {tasks}")
                    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
