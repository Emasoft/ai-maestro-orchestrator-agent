#!/usr/bin/env python3
"""
EOA Orchestrator Storage Initialization

Initializes the orchestrator's document storage structure for tracking
documents from all remote agents, including:
- Per-agent folders for received documents
- Sent documents tracking
- Cross-agent search indexes
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_project_root() -> Path:
    """Get project root from environment or current directory."""
    if "PROJECT_ROOT" in os.environ:
        return Path(os.environ["PROJECT_ROOT"])
    return Path.cwd()


def init_orchestrator_storage(project_root: Path) -> dict:
    """Initialize orchestrator storage structure."""
    design_root = project_root / "design"

    # Directory structure for orchestrator
    directories = [
        design_root / "agents",
        design_root / "sent" / "all-agents" / "sync",
        design_root / "index" / "by-task",
        design_root / "index" / "by-agent",
        design_root / "index" / "by-date",
        design_root / "index" / "by-category",
        design_root / "archive" / "acks",
    ]

    created = []
    for directory in directories:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            created.append(str(directory.relative_to(project_root)))

    # Create .gitkeep files
    gitkeep_dirs = [
        design_root / "agents",
        design_root / "sent",
        design_root / "index",
        design_root / "archive",
    ]
    for directory in gitkeep_dirs:
        gitkeep = directory / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()

    # Create orchestrator metadata
    metadata_path = design_root / "orchestrator.json"
    if not metadata_path.exists():
        metadata = {
            "schema_version": "2.0.0",
            "role": "orchestrator",
            "initialized_at": datetime.now(timezone.utc).isoformat(),
            "storage_root": str(design_root),
            "registered_agents": [],
            "total_tasks_delegated": 0,
            "total_documents_sent": 0,
            "total_documents_received": 0,
        }
        metadata_path.write_text(json.dumps(metadata, indent=2))
        created.append(str(metadata_path.relative_to(project_root)))

    # Update .gitignore if needed
    gitignore_path = project_root / ".gitignore"
    design_pattern = "design/"

    if gitignore_path.exists():
        content = gitignore_path.read_text()
        if design_pattern not in content:
            with gitignore_path.open("a") as f:
                f.write(f"\n# EOA Document Storage (local, not committed)\n{design_pattern}\n")
    else:
        gitignore_path.write_text(f"# EOA Document Storage (local, not committed)\n{design_pattern}\n")

    # Initialize empty category indexes
    category_indexes = ["tasks", "reports", "acks", "blockers", "sync"]
    for category in category_indexes:
        index_path = design_root / "index" / "by-category" / f"{category}.json"
        if not index_path.exists():
            index_path.write_text("[]")

    return {
        "success": True,
        "storage_root": str(design_root),
        "directories_created": created,
        "role": "orchestrator",
    }


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Initialize EOA orchestrator storage"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Project root directory (default: current directory)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )

    args = parser.parse_args()

    project_root = args.project_root or get_project_root()

    try:
        result = init_orchestrator_storage(project_root)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"EOA orchestrator storage initialized at: {result['storage_root']}")
            if result["directories_created"]:
                print(f"Created {len(result['directories_created'])} directories")
            else:
                print("Storage already exists")

        sys.exit(0)
    except Exception as e:
        error = {"success": False, "error": str(e)}
        if args.json:
            print(json.dumps(error, indent=2))
        else:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
