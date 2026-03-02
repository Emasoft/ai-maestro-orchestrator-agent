#!/usr/bin/env python3
"""
EOA Initialize Design Folders Script

Creates the standardized design folder structure for orchestration.
Includes design/memory/, design/handoffs/, design/requirements/ with templates.

Usage:
    python3 eoa_init_design_folders.py
    python3 eoa_init_design_folders.py --platforms web ios android
    python3 eoa_init_design_folders.py --root design --platforms web
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# Default root location
DEFAULT_ROOT = "design"

# Default platforms
DEFAULT_PLATFORMS = ["shared"]

# Template files to create
TEMPLATE_FILES = {
    "requirements": {
        "MODULE_SPEC_TEMPLATE.md": """# Module Specification Template

## Module ID
{{MODULE_ID}}

## Module Name
{{MODULE_NAME}}

## Description
{{DESCRIPTION}}

## Platform
{{PLATFORM}}

## Dependencies
{{DEPENDENCIES}}

## Acceptance Criteria
{{ACCEPTANCE_CRITERIA}}

## Technical Notes
{{TECHNICAL_NOTES}}
""",
        "RDD_TEMPLATE.md": """# Requirements-Driven Design Document

## Document ID
{{DOCUMENT_ID}}

## Module
{{MODULE_NAME}}

## Platform
{{PLATFORM}}

## Requirements

### Functional Requirements
{{FUNCTIONAL_REQUIREMENTS}}

### Non-Functional Requirements
{{NON_FUNCTIONAL_REQUIREMENTS}}

## Design Decisions
{{DESIGN_DECISIONS}}

## Trade-offs
{{TRADE_OFFS}}

## Open Questions
{{OPEN_QUESTIONS}}
""",
    },
    "memory": {
        "CONTEXT_TEMPLATE.md": """# Context Document

## Document ID
{{DOCUMENT_ID}}

## Created
{{CREATED_AT}}

## Type
{{CONTEXT_TYPE}}

## Summary
{{SUMMARY}}

## Details
{{DETAILS}}

## Related Documents
{{RELATED_DOCS}}
""",
        "DECISION_TEMPLATE.md": """# Decision Record

## Decision ID
{{DECISION_ID}}

## Date
{{DECISION_DATE}}

## Status
{{STATUS}}

## Context
{{CONTEXT}}

## Decision
{{DECISION}}

## Consequences
{{CONSEQUENCES}}

## Alternatives Considered
{{ALTERNATIVES}}
""",
    },
    "handoffs": {
        "HANDOFF_TEMPLATE.md": """# Agent Handoff Document

## Handoff ID
{{HANDOFF_ID}}

## Generated
{{GENERATED_AT}}

## Agent
{{AGENT_ID}}

## Module
{{MODULE_ID}}

---

## Context

{{CONTEXT_SUMMARY}}

---

## Requirements

{{REQUIREMENTS_CONTENT}}

---

## Technical Specifications

{{TECHNICAL_SPECS}}

---

## Configuration

{{CONFIG_DETAILS}}

---

## Acceptance Criteria

{{ACCEPTANCE_CRITERIA}}

---

## Questions to Clarify Before Starting

Please confirm your understanding of:
1. The module scope and boundaries
2. The acceptance criteria
3. Any blocking dependencies

Reply with your understanding and any questions.
""",
    },
}


def create_index_file(root: Path, platforms: list[str]) -> dict[str, Any]:
    """Create the design folder index file."""
    index_data = {
        "version": "1.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "platforms": platforms,
        "documents": {
            "requirements": [],
            "memory": [],
            "handoffs": [],
        },
        "stats": {
            "total_documents": 0,
            "by_type": {
                "requirements": 0,
                "memory": 0,
                "handoffs": 0,
            },
            "by_platform": {p: 0 for p in platforms},
        },
    }
    return index_data


def write_yaml_file(path: Path, data: dict[str, Any]) -> bool:
    """Write data to a YAML file."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        content = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
        path.write_text(content, encoding="utf-8")
        return True
    except Exception as e:
        print(f"ERROR: Failed to write {path}: {e}")
        return False


def write_json_file(path: Path, data: dict[str, Any]) -> bool:
    """Write data to a JSON file."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return True
    except Exception as e:
        print(f"ERROR: Failed to write {path}: {e}")
        return False


def create_folder_structure(root: Path, platforms: list[str]) -> list[Path]:
    """Create the design folder structure and return created paths."""
    created: list[Path] = []

    # Main folders
    main_folders = [
        root / "requirements",
        root / "memory",
        root / "handoffs",
        root / "config",
        root / "archive",
    ]

    for folder in main_folders:
        folder.mkdir(parents=True, exist_ok=True)
        created.append(folder)

    # Platform-specific folders under requirements
    for platform in platforms:
        platform_folders = [
            root / "requirements" / platform / "templates",
            root / "requirements" / platform / "specs",
            root / "requirements" / platform / "rdd",
        ]
        for folder in platform_folders:
            folder.mkdir(parents=True, exist_ok=True)
            created.append(folder)

    # Platform-specific config folders
    for platform in platforms:
        config_folder = root / "config" / platform
        config_folder.mkdir(parents=True, exist_ok=True)
        created.append(config_folder)

    return created


def create_template_files(root: Path, platforms: list[str]) -> list[Path]:
    """Create template files in appropriate locations."""
    created: list[Path] = []

    # Requirements templates (one per platform)
    for platform in platforms:
        templates_dir = root / "requirements" / platform / "templates"
        for filename, content in TEMPLATE_FILES["requirements"].items():
            file_path = templates_dir / filename
            if not file_path.exists():
                file_path.write_text(content, encoding="utf-8")
                created.append(file_path)

    # Memory templates (shared)
    memory_dir = root / "memory"
    templates_subdir = memory_dir / "templates"
    templates_subdir.mkdir(parents=True, exist_ok=True)
    for filename, content in TEMPLATE_FILES["memory"].items():
        file_path = templates_subdir / filename
        if not file_path.exists():
            file_path.write_text(content, encoding="utf-8")
            created.append(file_path)

    # Handoffs templates (shared)
    handoffs_dir = root / "handoffs"
    templates_subdir = handoffs_dir / "templates"
    templates_subdir.mkdir(parents=True, exist_ok=True)
    for filename, content in TEMPLATE_FILES["handoffs"].items():
        file_path = templates_subdir / filename
        if not file_path.exists():
            file_path.write_text(content, encoding="utf-8")
            created.append(file_path)

    return created


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize design folder structure")
    parser.add_argument("--root", default=DEFAULT_ROOT, help="Root folder for design documents")
    parser.add_argument(
        "--platforms",
        nargs="+",
        default=DEFAULT_PLATFORMS,
        help="Platforms to create folders for (default: shared)",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing index file")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    root = Path(args.root)
    platforms = args.platforms

    # Ensure 'shared' is always included
    if "shared" not in platforms:
        platforms = ["shared"] + platforms

    results = {
        "success": True,
        "root": str(root),
        "platforms": platforms,
        "folders_created": [],
        "templates_created": [],
        "index_created": False,
        "errors": [],
    }

    # Check if already initialized
    index_file = root / "index.yaml"
    if index_file.exists() and not args.force:
        if args.json:
            results["success"] = False
            results["errors"].append(f"Design folder already initialized at {root}. Use --force to reinitialize.")
            print(json.dumps(results, indent=2))
        else:
            print(f"Design folder already initialized at {root}")
            print("Use --force to reinitialize")
        return 1

    # Create folder structure
    try:
        folders = create_folder_structure(root, platforms)
        results["folders_created"] = [str(f) for f in folders]
    except Exception as e:
        results["success"] = False
        results["errors"].append(f"Failed to create folder structure: {e}")
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"ERROR: {e}")
        return 1

    # Create template files
    try:
        templates = create_template_files(root, platforms)
        results["templates_created"] = [str(f) for f in templates]
    except Exception as e:
        results["success"] = False
        results["errors"].append(f"Failed to create template files: {e}")
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"ERROR: {e}")
        return 1

    # Create index file
    index_data = create_index_file(root, platforms)
    if write_yaml_file(index_file, index_data):
        results["index_created"] = True
    else:
        results["success"] = False
        results["errors"].append("Failed to create index file")

    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"Design folder initialized at: {root}")
        print(f"Platforms: {', '.join(platforms)}")
        print(f"Folders created: {len(results['folders_created'])}")
        print(f"Templates created: {len(results['templates_created'])}")
        print()
        print("Structure:")
        print(f"  {root}/")
        print("    requirements/")
        for p in platforms:
            print(f"      {p}/")
            print("        templates/")
            print("        specs/")
            print("        rdd/")
        print("    memory/")
        print("      templates/")
        print("    handoffs/")
        print("      templates/")
        print("    config/")
        for p in platforms:
            print(f"      {p}/")
        print("    archive/")
        print("    index.yaml")

    return 0 if results["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
