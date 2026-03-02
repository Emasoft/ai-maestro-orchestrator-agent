#!/usr/bin/env python3
"""
EOA Cross-Agent Search

Searches across all agents' documents using the pre-built indexes.

Usage:
    python eoa_search.py by-task TASK_ID
    python eoa_search.py by-agent AGENT_NAME
    python eoa_search.py by-date 2024-01-15
    python eoa_search.py by-category reports
    python eoa_search.py blockers
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def get_design_root() -> Path:
    """Get Design storage root from environment or current directory."""
    if "DESIGN_STORAGE_ROOT" in os.environ:
        return Path(os.environ["DESIGN_STORAGE_ROOT"])
    if "PROJECT_ROOT" in os.environ:
        return Path(os.environ["PROJECT_ROOT"]) / "design"
    return Path.cwd() / "design"


def search_by_task(task_id: str, design_root: Path) -> dict[str, Any]:
    """Search for all documents related to a task."""
    index_path = design_root / "index" / "by-task" / f"{task_id}.json"

    if not index_path.exists():
        return {"found": False, "task_id": task_id, "message": "No index found for task"}

    try:
        index = json.loads(index_path.read_text())
        return {"found": True, "task_id": task_id, **index}
    except json.JSONDecodeError:
        return {"found": False, "task_id": task_id, "error": "Invalid index file"}


def search_by_agent(agent_name: str, design_root: Path) -> dict[str, Any]:
    """Search for all documents from an agent."""
    index_path = design_root / "index" / "by-agent" / f"{agent_name}.json"

    if not index_path.exists():
        return {"found": False, "agent": agent_name, "message": "No index found for agent"}

    try:
        index = json.loads(index_path.read_text())
        return {"found": True, **index}
    except json.JSONDecodeError:
        return {"found": False, "agent": agent_name, "error": "Invalid index file"}


def search_by_date(date_str: str, design_root: Path) -> dict[str, Any]:
    """Search for all documents from a specific date."""
    # Parse date
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        year_month = date.strftime("%Y-%m")
        day = date.strftime("%d")
    except ValueError:
        return {"found": False, "date": date_str, "error": "Invalid date format. Use YYYY-MM-DD"}

    index_path = design_root / "index" / "by-date" / year_month / f"{day}.json"

    if not index_path.exists():
        return {"found": False, "date": date_str, "message": "No documents found for date"}

    try:
        documents = json.loads(index_path.read_text())
        return {"found": True, "date": date_str, "documents": documents, "count": len(documents)}
    except json.JSONDecodeError:
        return {"found": False, "date": date_str, "error": "Invalid index file"}


def search_by_category(category: str, design_root: Path) -> dict[str, Any]:
    """Search for all documents in a category."""
    index_path = design_root / "index" / "by-category" / f"{category}.json"

    if not index_path.exists():
        return {"found": False, "category": category, "message": "No documents found for category"}

    try:
        documents = json.loads(index_path.read_text())
        return {"found": True, "category": category, "documents": documents, "count": len(documents)}
    except json.JSONDecodeError:
        return {"found": False, "category": category, "error": "Invalid index file"}


def search_blockers(design_root: Path) -> dict[str, Any]:
    """Find all blocker reports across all agents (critical operation)."""
    # Search by category for blockers
    result = search_by_category("reports", design_root)

    if not result["found"]:
        # Also check reports category which contains blockers subcategory
        blockers: list[dict] = []

        # Direct search in agents directories
        agents_dir = design_root / "agents"
        if agents_dir.exists():
            for agent_dir in agents_dir.iterdir():
                if not agent_dir.is_dir():
                    continue

                blockers_dir = agent_dir / "received" / "reports"
                if not blockers_dir.exists():
                    continue

                for task_dir in blockers_dir.iterdir():
                    if not task_dir.is_dir():
                        continue

                    blocker_dir = task_dir / "blockers"
                    if blocker_dir.exists():
                        for md_file in blocker_dir.glob("*.md"):
                            blockers.append({
                                "agent": agent_dir.name,
                                "task_id": task_dir.name,
                                "path": str(md_file.relative_to(design_root)),
                                "filename": md_file.name,
                            })

        return {
            "found": bool(blockers),
            "blockers": blockers,
            "count": len(blockers),
            "critical": len(blockers) > 0,
        }

    # Filter for blocker reports from category index
    blockers = [
        doc for doc in result.get("documents", [])
        if "blocker" in doc.get("path", "").lower()
    ]

    return {
        "found": bool(blockers),
        "blockers": blockers,
        "count": len(blockers),
        "critical": len(blockers) > 0,
    }


def search_fulltext(pattern: str, design_root: Path) -> dict[str, Any]:
    """Search document contents for a pattern."""
    results: list[dict] = []
    agents_dir = design_root / "agents"

    if not agents_dir.exists():
        return {"found": False, "pattern": pattern, "message": "No agents directory"}

    for agent_dir in agents_dir.iterdir():
        if not agent_dir.is_dir():
            continue

        received_dir = agent_dir / "received"
        if not received_dir.exists():
            continue

        for md_file in received_dir.rglob("*.md"):
            try:
                content = md_file.read_text()
                if pattern.lower() in content.lower():
                    # Extract context
                    lines = content.split("\n")
                    matching_lines = [
                        (i, line) for i, line in enumerate(lines)
                        if pattern.lower() in line.lower()
                    ]

                    results.append({
                        "agent": agent_dir.name,
                        "path": str(md_file.relative_to(design_root)),
                        "matches": len(matching_lines),
                        "preview": matching_lines[:3] if matching_lines else [],
                    })
            except (UnicodeDecodeError, PermissionError):
                continue

    return {
        "found": bool(results),
        "pattern": pattern,
        "results": results,
        "count": len(results),
    }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="EOA Cross-Agent Document Search"
    )

    subparsers = parser.add_subparsers(dest="command", help="Search commands")

    # by-task
    task_parser = subparsers.add_parser("by-task", help="Search by task ID")
    task_parser.add_argument("task_id", help="Task ID (e.g., GH-42)")
    task_parser.add_argument("--design-root", type=Path, help="Design root")
    task_parser.add_argument("--json", action="store_true", help="JSON output")

    # by-agent
    agent_parser = subparsers.add_parser("by-agent", help="Search by agent name")
    agent_parser.add_argument("agent_name", help="Agent full name")
    agent_parser.add_argument("--design-root", type=Path, help="Design root")
    agent_parser.add_argument("--json", action="store_true", help="JSON output")

    # by-date
    date_parser = subparsers.add_parser("by-date", help="Search by date")
    date_parser.add_argument("date", help="Date (YYYY-MM-DD)")
    date_parser.add_argument("--design-root", type=Path, help="Design root")
    date_parser.add_argument("--json", action="store_true", help="JSON output")

    # by-category
    cat_parser = subparsers.add_parser("by-category", help="Search by category")
    cat_parser.add_argument("category", help="Category name")
    cat_parser.add_argument("--design-root", type=Path, help="Design root")
    cat_parser.add_argument("--json", action="store_true", help="JSON output")

    # blockers
    block_parser = subparsers.add_parser("blockers", help="Find all blocker reports")
    block_parser.add_argument("--design-root", type=Path, help="Design root")
    block_parser.add_argument("--json", action="store_true", help="JSON output")

    # fulltext
    ft_parser = subparsers.add_parser("fulltext", help="Full-text search")
    ft_parser.add_argument("pattern", help="Search pattern")
    ft_parser.add_argument("--design-root", type=Path, help="Design root")
    ft_parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    design_root = args.design_root or get_design_root()

    if args.command == "by-task":
        result = search_by_task(args.task_id, design_root)
    elif args.command == "by-agent":
        result = search_by_agent(args.agent_name, design_root)
    elif args.command == "by-date":
        result = search_by_date(args.date, design_root)
    elif args.command == "by-category":
        result = search_by_category(args.category, design_root)
    elif args.command == "blockers":
        result = search_blockers(design_root)
    elif args.command == "fulltext":
        result = search_fulltext(args.pattern, design_root)
    else:
        parser.print_help()
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Pretty print
        if not result.get("found"):
            print(f"Not found: {result.get('message', result.get('error', 'No results'))}")
            return 0

        if args.command == "by-task":
            print(f"\n=== Task: {result['task_id']} ===\n")
            print(f"Status: {result.get('status', 'unknown')}")
            print(f"Created: {result.get('created', '?')}")
            print(f"\nAssigned Agents ({len(result.get('assigned_agents', []))}):")
            for agent in result.get("assigned_agents", []):
                print(f"  - {agent.get('agent')} (assigned: {agent.get('assigned_at', '?')[:10]})")
            print(f"\nDocuments ({len(result.get('documents', []))}):")
            for doc in result.get("documents", []):
                print(f"  [{doc.get('type')}] {doc.get('path')}")

        elif args.command == "by-agent":
            print(f"\n=== Agent: {result.get('agent')} ===\n")
            print(f"Tasks ({len(result.get('tasks', []))}):")
            for task in result.get("tasks", []):
                print(f"  - {task}")
            print(f"\nDocuments ({len(result.get('documents', []))}):")
            for doc in result.get("documents", [])[-10:]:  # Last 10
                print(f"  [{doc.get('task_id')}] {doc.get('category')}: {doc.get('path')}")
            if len(result.get("documents", [])) > 10:
                print(f"  ... and {len(result.get('documents', [])) - 10} more")

        elif args.command == "by-date":
            print(f"\n=== Date: {result['date']} ===\n")
            print(f"Documents ({result.get('count', 0)}):")
            for doc in result.get("documents", []):
                print(f"  [{doc.get('agent')}] {doc.get('task_id')}: {doc.get('category')}")

        elif args.command == "by-category":
            print(f"\n=== Category: {result['category']} ===\n")
            print(f"Documents ({result.get('count', 0)}):")
            for doc in result.get("documents", [])[-20:]:
                print(f"  [{doc.get('agent')}] {doc.get('task_id')}")

        elif args.command == "blockers":
            print("\n=== BLOCKER REPORTS ===\n")
            if result.get("critical"):
                print("!!! CRITICAL: Active blockers found !!!\n")
            print(f"Total blockers: {result.get('count', 0)}\n")
            for blocker in result.get("blockers", []):
                print(f"  [{blocker.get('agent')}] {blocker.get('task_id')}")
                print(f"    Path: {blocker.get('path')}")

        elif args.command == "fulltext":
            print(f"\n=== Search: '{result['pattern']}' ===\n")
            print(f"Found in {result.get('count', 0)} file(s):\n")
            for r in result.get("results", []):
                print(f"  [{r.get('agent')}] {r.get('path')} ({r.get('matches')} matches)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
