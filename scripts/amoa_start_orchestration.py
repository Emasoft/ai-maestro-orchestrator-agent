#!/usr/bin/env python3
"""
EOA Start Orchestration Script

Activates Orchestration Phase Mode after plan approval.
Sets up module tracking and prepares for agent assignment.

Usage:
    python3 eoa_start_orchestration.py
    python3 eoa_start_orchestration.py --project-id PVT_kwDOBxxxxxx
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

# State file locations
PLAN_STATE_FILE = Path(".claude/orchestrator-plan-phase.local.md")
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Start Orchestration Phase")
    parser.add_argument("--project-id", help="GitHub Project ID for Kanban sync")

    args = parser.parse_args()

    # Check prerequisites
    if not PLAN_STATE_FILE.exists():
        print("ERROR: Plan Phase not found")
        print("Run /start-planning first, then /approve-plan")
        return 1

    plan_data, _ = parse_frontmatter(PLAN_STATE_FILE)
    if not plan_data.get("plan_phase_complete"):
        print("ERROR: Plan Phase not approved")
        print("Run /approve-plan first")
        return 1

    if not EXEC_STATE_FILE.exists():
        print("ERROR: Orchestration Phase state file not found")
        print("Run /approve-plan to create it")
        return 1

    # Load and update orchestration state
    exec_data, _ = parse_frontmatter(EXEC_STATE_FILE)
    if not exec_data:
        print("ERROR: Could not parse orchestration state file")
        return 1

    # Check if already started
    if exec_data.get("status") == "executing":
        print("Orchestration Phase already active")
        print("Use /orchestration-status to view progress")
        return 0

    # Update state
    exec_data["status"] = "executing"
    exec_data["started_at"] = datetime.now(timezone.utc).isoformat()

    if args.project_id:
        exec_data["github_project_id"] = args.project_id
        exec_data["sync_enabled"] = True

    # Update body
    plan_id = exec_data.get("plan_id", "unknown")
    modules_total = exec_data.get("modules_total", 0)

    new_body = f"""# Orchestration Phase: {plan_id}

## Status

**EXECUTING** - Implementation in progress

## Modules

{modules_total} modules to implement.

## Active Instructions

1. Register remote agents with `/register-agent`
2. Assign modules with `/assign-module`
3. Execute Instruction Verification Protocol before each agent starts
4. Poll agents every 10-15 minutes with `/check-agents`
5. Use MANDATORY questions in every poll
6. Complete 4 verification loops before allowing PRs

## Stop Hook

Exit is blocked until:
- ALL modules complete
- ALL GitHub Project items done
- ALL Claude Tasks complete
- 4 verification loops passed
"""

    if not write_state_file(EXEC_STATE_FILE, exec_data, new_body):
        return 1

    # Print summary
    print("╔" + "═" * 66 + "╗")
    print("║" + "ORCHESTRATION PHASE ACTIVATED".center(66) + "║")
    print("╠" + "═" * 66 + "╣")
    print(f"║ Plan ID: {plan_id:<55} ║")
    print(f"║ Modules: {modules_total:<56} ║")
    if args.project_id:
        print(f"║ GitHub Project: {args.project_id[:48]:<48} ║")
    print("╠" + "═" * 66 + "╣")
    print("║" + "NEXT STEPS".center(66) + "║")
    print("╠" + "═" * 66 + "╣")
    print("║ 1. /register-agent ai <agent_id> --session <session_name>        ║")
    print("║ 2. /assign-module <module_id> <agent_id>                         ║")
    print("║ 3. Execute Instruction Verification Protocol                     ║")
    print("║ 4. /check-agents (every 10-15 minutes)                           ║")
    print("╚" + "═" * 66 + "╝")

    return 0


if __name__ == "__main__":
    sys.exit(main())
