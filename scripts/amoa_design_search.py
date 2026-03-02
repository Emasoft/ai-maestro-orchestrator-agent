#!/usr/bin/env python3
"""
EOA Design Search Script

Searches design documents by UUID, type, status, or keyword.
Supports all design/*/ subfolders.

Usage:
    python3 eoa_design_search.py --keyword "auth"
    python3 eoa_design_search.py --uuid abc12345
    python3 eoa_design_search.py --type requirements
    python3 eoa_design_search.py --type handoffs --agent implementer-1
    python3 eoa_design_search.py --recent 5
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

# Design folder default root
DEFAULT_ROOT = "design"

# Document types and their locations
DOC_TYPES = {
    "requirements": ["requirements/*/specs", "requirements/*/rdd", "requirements/*/templates"],
    "memory": ["memory"],
    "handoffs": ["handoffs"],
    "config": ["config"],
    "archive": ["archive"],
}


def read_yaml_file(path: Path) -> dict[str, Any]:
    """Read a YAML file and return its contents."""
    if not path.exists():
        return {}
    try:
        content = path.read_text(encoding="utf-8")
        return yaml.safe_load(content) or {}
    except yaml.YAMLError:
        return {}


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
    body = content[end_index + 3:].strip()

    try:
        data = yaml.safe_load(yaml_content) or {}
        return data, body
    except yaml.YAMLError:
        return {}, content


def extract_document_info(file_path: Path, root: Path) -> dict[str, Any]:
    """Extract information from a design document."""
    rel_path = file_path.relative_to(root)
    parts = list(rel_path.parts)

    # Determine document type
    doc_type = parts[0] if parts else "unknown"

    # Get file stats
    stat = file_path.stat()
    modified_time = datetime.fromtimestamp(stat.st_mtime).isoformat()

    # Read content
    content = file_path.read_text(encoding="utf-8")

    # Try to extract UUID/ID from content
    uuid_match = re.search(r'(?:ID|UUID|Handoff ID|Document ID|Decision ID):\s*([a-zA-Z0-9-]+)', content)
    doc_id = uuid_match.group(1) if uuid_match else None

    # Extract title (first heading)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else file_path.stem

    # Determine platform
    platform = None
    if len(parts) > 2 and doc_type == "requirements":
        platform = parts[1]

    # Determine agent (for handoffs)
    agent = None
    if doc_type == "handoffs" and len(parts) > 1 and parts[1] != "templates":
        agent = parts[1]

    return {
        "path": str(file_path),
        "relative_path": str(rel_path),
        "type": doc_type,
        "title": title,
        "id": doc_id,
        "platform": platform,
        "agent": agent,
        "modified": modified_time,
        "size": stat.st_size,
    }


def search_by_keyword(root: Path, keyword: str, doc_type: str | None = None) -> list[dict[str, Any]]:
    """Search documents by keyword in content or filename."""
    results = []
    keyword_lower = keyword.lower()

    # Determine search paths
    if doc_type and doc_type in DOC_TYPES:
        search_patterns = DOC_TYPES[doc_type]
    else:
        search_patterns = [p for patterns in DOC_TYPES.values() for p in patterns]

    for pattern in search_patterns:
        for md_file in root.glob(f"{pattern}/**/*.md"):
            if md_file.is_file():
                # Check filename
                if keyword_lower in md_file.name.lower():
                    results.append(extract_document_info(md_file, root))
                    continue

                # Check content
                try:
                    content = md_file.read_text(encoding="utf-8").lower()
                    if keyword_lower in content:
                        results.append(extract_document_info(md_file, root))
                except Exception:
                    continue

    return results


def search_by_uuid(root: Path, uuid: str) -> list[dict[str, Any]]:
    """Search documents by UUID/ID."""
    results = []

    for md_file in root.rglob("*.md"):
        if md_file.is_file():
            try:
                content = md_file.read_text(encoding="utf-8")
                if uuid in content:
                    results.append(extract_document_info(md_file, root))
            except Exception:
                continue

    return results


def search_by_type(root: Path, doc_type: str, agent: str | None = None, platform: str | None = None) -> list[dict[str, Any]]:
    """Search documents by type."""
    results: list[dict[str, Any]] = []

    if doc_type not in DOC_TYPES:
        return results

    for pattern in DOC_TYPES[doc_type]:
        for md_file in root.glob(f"{pattern}/**/*.md"):
            if md_file.is_file():
                info = extract_document_info(md_file, root)

                # Filter by agent
                if agent and info.get("agent") != agent:
                    continue

                # Filter by platform
                if platform and info.get("platform") != platform:
                    continue

                results.append(info)

    return results


def search_recent(root: Path, count: int = 10) -> list[dict[str, Any]]:
    """Get the most recently modified documents."""
    all_docs = []

    for md_file in root.rglob("*.md"):
        if md_file.is_file() and "templates" not in str(md_file):
            all_docs.append(extract_document_info(md_file, root))

    # Sort by modified time (descending)
    all_docs.sort(key=lambda x: x["modified"], reverse=True)

    return all_docs[:count]


def search_index(root: Path, doc_type: str | None = None) -> list[dict[str, Any]]:
    """Search using the index file if available."""
    index_file = root / "index.yaml"
    if not index_file.exists():
        return []

    index_data = read_yaml_file(index_file)
    documents = index_data.get("documents", {})

    results = []
    if doc_type:
        results = documents.get(doc_type, [])
    else:
        for doc_list in documents.values():
            results.extend(doc_list)

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Search design documents")
    parser.add_argument("--root", default=DEFAULT_ROOT, help="Design folder root")
    parser.add_argument("--keyword", "-k", help="Search by keyword in content/filename")
    parser.add_argument("--uuid", "-u", help="Search by UUID/ID")
    parser.add_argument(
        "--type",
        "-t",
        choices=list(DOC_TYPES.keys()),
        help="Filter by document type",
    )
    parser.add_argument("--agent", help="Filter handoffs by agent ID")
    parser.add_argument("--platform", help="Filter by platform")
    parser.add_argument("--recent", type=int, metavar="N", help="Show N most recent documents")
    parser.add_argument("--use-index", action="store_true", help="Search using index file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")

    args = parser.parse_args()

    root = Path(args.root)

    if not root.exists():
        if args.json:
            print(json.dumps({"success": False, "error": f"Design folder not found: {root}"}))
        else:
            print(f"ERROR: Design folder not found: {root}")
        return 1

    results: list[dict[str, Any]] = []

    # Determine search type
    if args.uuid:
        results = search_by_uuid(root, args.uuid)
    elif args.keyword:
        results = search_by_keyword(root, args.keyword, args.type)
    elif args.recent:
        results = search_recent(root, args.recent)
    elif args.use_index:
        results = search_index(root, args.type)
    elif args.type:
        results = search_by_type(root, args.type, args.agent, args.platform)
    else:
        # Default: show all documents
        results = search_recent(root, 100)

    # Output results
    output = {
        "success": True,
        "count": len(results),
        "results": results,
    }

    if args.json:
        print(json.dumps(output, indent=2))
    else:
        print(f"Found {len(results)} document(s)")
        print()

        if not results:
            print("No documents match the search criteria.")
            return 0

        for doc in results:
            print(f"  {doc['relative_path']}")
            if args.verbose:
                print(f"    Title: {doc['title']}")
                print(f"    Type: {doc['type']}")
                if doc.get('id'):
                    print(f"    ID: {doc['id']}")
                if doc.get('platform'):
                    print(f"    Platform: {doc['platform']}")
                if doc.get('agent'):
                    print(f"    Agent: {doc['agent']}")
                print(f"    Modified: {doc['modified']}")
                print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
