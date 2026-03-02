#!/usr/bin/env python3
"""
EOA Compile Handoff Script

Compiles a handoff document for an agent from module specification and context.
Reads requirements from design/requirements/ and context from design/memory/.
Generates compiled handoff in design/handoffs/{agent-id}/.

Usage:
    python3 eoa_compile_handoff.py MODULE_ID AGENT_ID
    python3 eoa_compile_handoff.py auth-core implementer-1 --platform web
    python3 eoa_compile_handoff.py auth-core implementer-1 --include-context decision-001
"""

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

import yaml

# State file location
EXEC_STATE_FILE = Path(".claude/orchestrator-exec-phase.local.md")

# Design folder default root
DEFAULT_ROOT = "design"


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


def read_yaml_file(path: Path) -> dict[str, Any]:
    """Read a YAML file and return its contents."""
    if not path.exists():
        return {}
    try:
        content = path.read_text(encoding="utf-8")
        return yaml.safe_load(content) or {}
    except yaml.YAMLError:
        return {}


def find_module_spec(
    root: Path, module_id: str, platform: str | None = None
) -> tuple[Path | None, str]:
    """Find the module specification file. Returns (path, content)."""
    search_paths = []

    if platform:
        # Search platform-specific first
        search_paths.append(
            root / "requirements" / platform / "specs" / f"{module_id}.md"
        )
        search_paths.append(
            root / "requirements" / platform / "specs" / f"{module_id}-spec.md"
        )

    # Search shared
    search_paths.append(root / "requirements" / "shared" / "specs" / f"{module_id}.md")
    search_paths.append(
        root / "requirements" / "shared" / "specs" / f"{module_id}-spec.md"
    )

    # Search all platforms if not found
    requirements_dir = root / "requirements"
    if requirements_dir.exists():
        for platform_dir in requirements_dir.iterdir():
            if platform_dir.is_dir():
                specs_dir = platform_dir / "specs"
                if specs_dir.exists():
                    for spec_file in specs_dir.glob(f"*{module_id}*.md"):
                        search_paths.append(spec_file)

    for path in search_paths:
        if path.exists():
            return path, path.read_text(encoding="utf-8")

    return None, ""


def find_rdd_file(
    root: Path, module_id: str, platform: str | None = None
) -> tuple[Path | None, str]:
    """Find the RDD file for a module. Returns (path, content)."""
    search_paths = []

    if platform:
        search_paths.append(
            root / "requirements" / platform / "rdd" / f"{module_id}.md"
        )
        search_paths.append(
            root / "requirements" / platform / "rdd" / f"{module_id}-rdd.md"
        )

    search_paths.append(root / "requirements" / "shared" / "rdd" / f"{module_id}.md")
    search_paths.append(
        root / "requirements" / "shared" / "rdd" / f"{module_id}-rdd.md"
    )

    for path in search_paths:
        if path.exists():
            return path, path.read_text(encoding="utf-8")

    return None, ""


def find_context_docs(root: Path, doc_ids: list[str]) -> list[tuple[str, str]]:
    """Find context documents by ID. Returns list of (id, content)."""
    results: list[tuple[str, str]] = []
    memory_dir = root / "memory"

    if not memory_dir.exists():
        return results

    for doc_id in doc_ids:
        # Search for files matching the ID
        for md_file in memory_dir.rglob("*.md"):
            if doc_id in md_file.stem:
                content = md_file.read_text(encoding="utf-8")
                results.append((doc_id, content))
                break

    return results


def get_module_from_state(module_id: str) -> dict[str, Any] | None:
    """Get module info from orchestration state file."""
    if not EXEC_STATE_FILE.exists():
        return None

    data, _ = parse_frontmatter(EXEC_STATE_FILE)
    modules = data.get("modules", [])

    for module in modules:
        if module.get("id") == module_id:
            return cast(dict[str, Any], module)

    return None


def compile_handoff(
    module_id: str,
    agent_id: str,
    root: Path,
    platform: str | None = None,
    context_ids: list[str] | None = None,
    config_files: list[str] | None = None,
) -> dict[str, Any]:
    """Compile a handoff document from available sources."""
    handoff_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now(timezone.utc).isoformat()

    # Find module specification
    spec_path, spec_content = find_module_spec(root, module_id, platform)

    # Find RDD
    rdd_path, rdd_content = find_rdd_file(root, module_id, platform)

    # Get module from state file (for additional info)
    module_state = get_module_from_state(module_id)

    # Find context documents
    context_docs = []
    if context_ids:
        context_docs = find_context_docs(root, context_ids)

    # Build handoff content
    handoff_lines = [
        "# Agent Handoff Document",
        "",
        f"## Handoff ID: {handoff_id}",
        f"**Generated:** {timestamp}",
        f"**Agent:** {agent_id}",
        f"**Module:** {module_id}",
    ]

    if platform:
        handoff_lines.append(f"**Platform:** {platform}")

    handoff_lines.extend(
        [
            "",
            "---",
            "",
            "## Context Summary",
            "",
        ]
    )

    # Add context from state file
    if module_state:
        handoff_lines.append(f"**Module Name:** {module_state.get('name', module_id)}")
        handoff_lines.append(f"**Priority:** {module_state.get('priority', 'medium')}")
        if module_state.get("dependencies"):
            handoff_lines.append(
                f"**Dependencies:** {', '.join(module_state['dependencies'])}"
            )
        handoff_lines.append("")

    # Add context documents
    if context_docs:
        handoff_lines.append("### Related Context Documents")
        handoff_lines.append("")
        for doc_id, doc_content in context_docs:
            handoff_lines.append(f"#### {doc_id}")
            handoff_lines.append("")
            handoff_lines.append(doc_content)
            handoff_lines.append("")

    # Add requirements/specification
    handoff_lines.extend(
        [
            "---",
            "",
            "## Requirements and Specification",
            "",
        ]
    )

    if spec_content:
        handoff_lines.append(f"*Source: {spec_path}*")
        handoff_lines.append("")
        handoff_lines.append(spec_content)
    else:
        handoff_lines.append("*No module specification found.*")

    handoff_lines.append("")

    # Add RDD
    if rdd_content:
        handoff_lines.extend(
            [
                "---",
                "",
                "## Requirements-Driven Design",
                "",
                f"*Source: {rdd_path}*",
                "",
                rdd_content,
                "",
            ]
        )

    # Add configuration section
    handoff_lines.extend(
        [
            "---",
            "",
            "## Configuration",
            "",
        ]
    )

    if config_files:
        handoff_lines.append("The following configuration files are provided:")
        handoff_lines.append("")
        for cf in config_files:
            handoff_lines.append(f"- `{cf}`")
        handoff_lines.append("")
    else:
        handoff_lines.append("*No additional configuration files specified.*")
        handoff_lines.append("")

    # Add acceptance criteria
    handoff_lines.extend(
        [
            "---",
            "",
            "## Acceptance Criteria",
            "",
        ]
    )

    if module_state and module_state.get("acceptance_criteria"):
        for criterion in module_state["acceptance_criteria"]:
            handoff_lines.append(f"- {criterion}")
        handoff_lines.append("")
    else:
        handoff_lines.append(
            "*Acceptance criteria should be extracted from the specification above.*"
        )
        handoff_lines.append("")

    # Add verification request
    handoff_lines.extend(
        [
            "---",
            "",
            "## Instructions for Agent",
            "",
            "**Before starting implementation:**",
            "",
            "1. Read this entire handoff document carefully",
            "2. Reply with your understanding of the module scope and requirements",
            "3. List any questions or clarifications needed",
            "4. Confirm when you are ready to begin implementation",
            "",
            "**Do not start implementation until you receive authorization.**",
            "",
        ]
    )

    handoff_content = "\n".join(handoff_lines)

    return {
        "handoff_id": handoff_id,
        "agent_id": agent_id,
        "module_id": module_id,
        "platform": platform,
        "generated_at": timestamp,
        "spec_found": spec_path is not None,
        "rdd_found": rdd_path is not None,
        "context_docs_count": len(context_docs),
        "content": handoff_content,
    }


def write_handoff(root: Path, agent_id: str, module_id: str, content: str) -> Path:
    """Write handoff document to the handoffs folder."""
    agent_folder = root / "handoffs" / agent_id
    agent_folder.mkdir(parents=True, exist_ok=True)

    handoff_file = agent_folder / f"{module_id}-handoff.md"
    handoff_file.write_text(content, encoding="utf-8")

    return handoff_file


def update_index(root: Path, handoff_info: dict[str, Any], handoff_path: Path) -> bool:
    """Update the design index with the new handoff."""
    index_file = root / "index.yaml"
    if not index_file.exists():
        return False

    try:
        index_data = read_yaml_file(index_file)

        # Add to handoffs list
        handoff_entry = {
            "id": handoff_info["handoff_id"],
            "agent_id": handoff_info["agent_id"],
            "module_id": handoff_info["module_id"],
            "platform": handoff_info["platform"],
            "path": str(handoff_path),
            "generated_at": handoff_info["generated_at"],
        }

        if "documents" not in index_data:
            index_data["documents"] = {}
        if "handoffs" not in index_data["documents"]:
            index_data["documents"]["handoffs"] = []

        index_data["documents"]["handoffs"].append(handoff_entry)

        # Update stats
        if "stats" not in index_data:
            index_data["stats"] = {"total_documents": 0, "by_type": {}}
        index_data["stats"]["total_documents"] = (
            index_data["stats"].get("total_documents", 0) + 1
        )
        if "by_type" not in index_data["stats"]:
            index_data["stats"]["by_type"] = {}
        index_data["stats"]["by_type"]["handoffs"] = (
            index_data["stats"]["by_type"].get("handoffs", 0) + 1
        )

        # Write updated index
        content = yaml.dump(
            index_data, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
        index_file.write_text(content, encoding="utf-8")
        return True

    except Exception as e:
        print(f"WARNING: Failed to update index: {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile handoff document for agent")
    parser.add_argument("module_id", help="Module ID to compile handoff for")
    parser.add_argument("agent_id", help="Agent ID receiving the handoff")
    parser.add_argument("--root", default=DEFAULT_ROOT, help="Design folder root")
    parser.add_argument("--platform", help="Target platform (e.g., web, ios, android)")
    parser.add_argument(
        "--include-context",
        nargs="+",
        dest="context_ids",
        help="Context document IDs to include",
    )
    parser.add_argument(
        "--config-files",
        nargs="+",
        help="Configuration files to reference",
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument(
        "--dry-run", action="store_true", help="Generate but don't write handoff"
    )

    args = parser.parse_args()

    root = Path(args.root)

    # Check design folder exists
    if not root.exists():
        if args.json:
            print(
                json.dumps(
                    {"success": False, "error": f"Design folder not found: {root}"}
                )
            )
        else:
            print(f"ERROR: Design folder not found: {root}")
            print("Run eoa_init_design_folders.py first")
        return 1

    # Compile handoff
    handoff_info = compile_handoff(
        module_id=args.module_id,
        agent_id=args.agent_id,
        root=root,
        platform=args.platform,
        context_ids=args.context_ids,
        config_files=args.config_files,
    )

    result = {
        "success": True,
        "handoff_id": handoff_info["handoff_id"],
        "agent_id": handoff_info["agent_id"],
        "module_id": handoff_info["module_id"],
        "platform": handoff_info["platform"],
        "generated_at": handoff_info["generated_at"],
        "spec_found": handoff_info["spec_found"],
        "rdd_found": handoff_info["rdd_found"],
        "context_docs_count": handoff_info["context_docs_count"],
    }

    if args.dry_run:
        result["dry_run"] = True
        if args.json:
            result["content_preview"] = handoff_info["content"][:500] + "..."
            print(json.dumps(result, indent=2))
        else:
            print("DRY RUN - Handoff not written")
            print(f"Handoff ID: {handoff_info['handoff_id']}")
            print(f"Agent: {handoff_info['agent_id']}")
            print(f"Module: {handoff_info['module_id']}")
            print(f"Spec found: {handoff_info['spec_found']}")
            print(f"RDD found: {handoff_info['rdd_found']}")
            print(f"Context docs: {handoff_info['context_docs_count']}")
            print()
            print("--- Content Preview ---")
            print(handoff_info["content"][:1000])
            if len(handoff_info["content"]) > 1000:
                print("...")
        return 0

    # Write handoff
    handoff_path = write_handoff(
        root, args.agent_id, args.module_id, handoff_info["content"]
    )
    result["path"] = str(handoff_path)

    # Update index
    index_updated = update_index(root, handoff_info, handoff_path)
    result["index_updated"] = index_updated

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("Handoff compiled successfully")
        print(f"  Handoff ID: {handoff_info['handoff_id']}")
        print(f"  Agent: {handoff_info['agent_id']}")
        print(f"  Module: {handoff_info['module_id']}")
        print(f"  Path: {handoff_path}")
        print()
        if not handoff_info["spec_found"]:
            print("WARNING: No module specification found")
        if not handoff_info["rdd_found"]:
            print("NOTE: No RDD file found")

    return 0


if __name__ == "__main__":
    sys.exit(main())
