#!/usr/bin/env python3
"""
EOA Orchestrator Download Manager

Downloads .md files from GitHub issue comments and stores them in the
orchestrator's agent-specific folder structure. Updates cross-agent indexes.

Usage:
    python eoa_orchestrator_download.py download --url URL --agent AGENT --task-id TASK_ID --category CATEGORY
    python eoa_orchestrator_download.py index-rebuild [--design-root PATH]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Categories for documents FROM agents (orchestrator receiving)
RECEIVED_CATEGORIES = {
    "reports": {
        "subfolders": ["completion", "verification", "blockers", "status"],
        "retention": "permanent",
    },
    "acks": {
        "subfolders": [],
        "retention": "90_days",
    },
    "sync": {
        "subfolders": [],
        "retention": "30_days",
    },
}


def get_design_root() -> Path:
    """Get Design storage root from environment or current directory."""
    if "ATLAS_STORAGE_ROOT" in os.environ:
        return Path(os.environ["ATLAS_STORAGE_ROOT"])
    if "PROJECT_ROOT" in os.environ:
        return Path(os.environ["PROJECT_ROOT"]) / "design"
    return Path.cwd() / "design"


def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with file_path.open("rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def set_readonly(path: Path) -> None:
    """Set file or directory to read-only."""
    if path.is_file():
        current = path.stat().st_mode
        path.chmod(current & ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH)
    elif path.is_dir():
        current = path.stat().st_mode
        path.chmod(current & ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH)


def extract_attachment_url(comment_url: str) -> str | None:
    """Extract .md attachment URL from GitHub issue comment."""
    match = re.match(
        r"https://github\.com/([^/]+)/([^/]+)/issues/(\d+)#issuecomment-(\d+)",
        comment_url,
    )
    if not match:
        return None

    owner, repo, _, comment_id = match.groups()

    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{owner}/{repo}/issues/comments/{comment_id}", "--jq", ".body"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        body = result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

    # Find .md file URL in body
    md_urls = re.findall(r"https://github\.com/[^\s)]+\.md", body)
    if md_urls:
        return md_urls[0]

    attachment_urls = re.findall(
        r"https://github\.com/user-attachments/files/[^\s)]+", body
    )
    if attachment_urls:
        return attachment_urls[0]

    return None


def ensure_agent_registered(agent_name: str, design_root: Path) -> Path:
    """Ensure agent folder exists, return agent directory path."""
    agent_dir = design_root / "agents" / agent_name

    if not agent_dir.exists():
        # Create minimal agent structure
        directories = [
            agent_dir,
            agent_dir / "received" / "reports",
            agent_dir / "received" / "acks",
            agent_dir / "received" / "sync",
        ]
        for d in directories:
            d.mkdir(parents=True, exist_ok=True)

        # Create minimal agent metadata
        metadata = {
            "schema_version": "2.0.0",
            "agent_name": agent_name,
            "agent_type": "remote",
            "first_seen": datetime.now(timezone.utc).isoformat(),
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "total_documents_received": 0,
        }
        (agent_dir / "agent.json").write_text(json.dumps(metadata, indent=2))

    return agent_dir


def update_agent_stats(agent_dir: Path) -> None:
    """Update agent metadata after receiving a document."""
    agent_json = agent_dir / "agent.json"
    if agent_json.exists():
        try:
            metadata = json.loads(agent_json.read_text())
            metadata["last_activity"] = datetime.now(timezone.utc).isoformat()
            metadata["total_documents_received"] = metadata.get("total_documents_received", 0) + 1
            agent_json.write_text(json.dumps(metadata, indent=2))
        except json.JSONDecodeError:
            pass


def update_index(
    design_root: Path,
    task_id: str,
    agent_name: str,
    category: str,
    doc_path: str,
    timestamp: str,
) -> None:
    """Update cross-agent search indexes."""
    index_dir = design_root / "index"

    # Update by-task index
    task_index_path = index_dir / "by-task" / f"{task_id}.json"
    task_index_path.parent.mkdir(parents=True, exist_ok=True)

    if task_index_path.exists():
        try:
            task_index = json.loads(task_index_path.read_text())
        except json.JSONDecodeError:
            task_index = {"task_id": task_id, "documents": [], "assigned_agents": []}
    else:
        task_index = {
            "task_id": task_id,
            "created": timestamp,
            "status": "in-progress",
            "assigned_agents": [],
            "documents": [],
        }

    # Add agent if not present
    agent_entry = next(
        (a for a in task_index["assigned_agents"] if a.get("agent") == agent_name),
        None
    )
    if not agent_entry:
        task_index["assigned_agents"].append({
            "agent": agent_name,
            "assigned_at": timestamp,
        })

    # Add document
    task_index["documents"].append({
        "type": category,
        "path": doc_path,
        "agent": agent_name,
        "timestamp": timestamp,
    })

    task_index_path.write_text(json.dumps(task_index, indent=2))

    # Update by-agent index
    agent_index_path = index_dir / "by-agent" / f"{agent_name}.json"
    agent_index_path.parent.mkdir(parents=True, exist_ok=True)

    if agent_index_path.exists():
        try:
            agent_index = json.loads(agent_index_path.read_text())
        except json.JSONDecodeError:
            agent_index = {"agent": agent_name, "tasks": [], "documents": []}
    else:
        agent_index = {"agent": agent_name, "tasks": [], "documents": []}

    if task_id not in agent_index["tasks"]:
        agent_index["tasks"].append(task_id)

    agent_index["documents"].append({
        "task_id": task_id,
        "category": category,
        "path": doc_path,
        "timestamp": timestamp,
    })

    agent_index_path.write_text(json.dumps(agent_index, indent=2))

    # Update by-category index
    cat_index_path = index_dir / "by-category" / f"{category}.json"
    cat_index_path.parent.mkdir(parents=True, exist_ok=True)

    if cat_index_path.exists():
        try:
            cat_index = json.loads(cat_index_path.read_text())
        except json.JSONDecodeError:
            cat_index = []
    else:
        cat_index = []

    cat_index.append({
        "task_id": task_id,
        "agent": agent_name,
        "path": doc_path,
        "timestamp": timestamp,
    })

    cat_index_path.write_text(json.dumps(cat_index, indent=2))

    # Update by-date index
    date_str = timestamp[:10]  # YYYY-MM-DD
    year_month = timestamp[:7]  # YYYY-MM
    date_index_dir = index_dir / "by-date" / year_month
    date_index_dir.mkdir(parents=True, exist_ok=True)
    date_index_path = date_index_dir / f"{date_str.split('-')[2]}.json"

    if date_index_path.exists():
        try:
            date_index = json.loads(date_index_path.read_text())
        except json.JSONDecodeError:
            date_index = []
    else:
        date_index = []

    date_index.append({
        "task_id": task_id,
        "agent": agent_name,
        "category": category,
        "path": doc_path,
        "timestamp": timestamp,
    })

    date_index_path.write_text(json.dumps(date_index, indent=2))


def download_to_agent_folder(
    url: str,
    agent_name: str,
    task_id: str,
    category: str,
    subcategory: str | None = None,
    doc_type: str | None = None,
    design_root: Path | None = None,
) -> dict[str, Any]:
    """Download document to agent-specific folder."""
    if design_root is None:
        design_root = get_design_root()

    if category not in RECEIVED_CATEGORIES:
        return {
            "success": False,
            "error": f"Invalid category: {category}. Valid: {list(RECEIVED_CATEGORIES.keys())}",
        }

    # Ensure agent is registered
    agent_dir = ensure_agent_registered(agent_name, design_root)

    # Determine target folder
    cat_config = RECEIVED_CATEGORIES[category]
    received_dir = agent_dir / "received" / category

    if category in ("reports", "acks"):
        folder_path = received_dir / task_id
    else:
        folder_path = received_dir

    if subcategory and subcategory in cat_config["subfolders"]:
        folder_path = folder_path / subcategory

    folder_path.mkdir(parents=True, exist_ok=True)

    # Generate filename
    timestamp = datetime.now(timezone.utc)
    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
    if doc_type:
        filename = f"{timestamp_str}_{doc_type}.md"
    else:
        filename = f"{timestamp_str}_document.md"

    file_path = folder_path / filename

    # Extract attachment URL if needed
    if "#issuecomment-" in url:
        download_url = extract_attachment_url(url)
        if not download_url:
            return {
                "success": False,
                "error": "Could not extract attachment URL from comment",
            }
    else:
        download_url = url

    # Download file
    try:
        subprocess.run(
            ["curl", "-fsSL", download_url, "-o", str(file_path)],
            capture_output=True,
            text=True,
            check=True,
            timeout=60,
        )
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": f"Download failed: {e.stderr}",
        }

    if not file_path.exists() or file_path.stat().st_size == 0:
        return {
            "success": False,
            "error": "Downloaded file is empty or missing",
        }

    # Compute hash
    sha256 = compute_sha256(file_path)

    # Create metadata
    metadata = {
        "schema_version": "2.0.0",
        "file_name": filename,
        "category": category,
        "subcategory": subcategory,
        "task_id": task_id,
        "document_type": doc_type,
        "source": {
            "type": "github_issue_comment" if "#issuecomment-" in url else "direct_url",
            "url": url,
            "download_url": download_url,
        },
        "download": {
            "timestamp": timestamp.isoformat(),
            "agent": "orchestrator",
            "sha256": sha256,
            "file_size_bytes": file_path.stat().st_size,
        },
        "sender": {
            "agent": agent_name,
            "role": "remote",
            "via": "ai_maestro",
        },
        "receiver": {
            "agent": "orchestrator",
            "role": "orchestrator",
        },
        "ack_sent": False,
        "ack_timestamp": None,
    }

    metadata_path = folder_path / f"{filename.replace('.md', '')}_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2))

    # Set read-only
    set_readonly(file_path)
    set_readonly(metadata_path)

    # Update agent stats
    update_agent_stats(agent_dir)

    # Update indexes
    update_index(
        design_root=design_root,
        task_id=task_id,
        agent_name=agent_name,
        category=category,
        doc_path=str(file_path.relative_to(design_root)),
        timestamp=timestamp.isoformat(),
    )

    # Update orchestrator stats
    orch_json = design_root / "orchestrator.json"
    if orch_json.exists():
        try:
            orch_meta = json.loads(orch_json.read_text())
            orch_meta["total_documents_received"] = orch_meta.get("total_documents_received", 0) + 1
            orch_json.write_text(json.dumps(orch_meta, indent=2))
        except json.JSONDecodeError:
            pass

    return {
        "success": True,
        "file_path": str(file_path),
        "agent": agent_name,
        "task_id": task_id,
        "category": category,
        "sha256": sha256,
        "size_bytes": file_path.stat().st_size,
    }


def rebuild_indexes(design_root: Path | None = None) -> dict[str, Any]:
    """Rebuild all cross-agent indexes from stored documents."""
    if design_root is None:
        design_root = get_design_root()

    index_dir = design_root / "index"

    # Clear existing indexes
    for index_type in ["by-task", "by-agent", "by-category", "by-date"]:
        type_dir = index_dir / index_type
        if type_dir.exists():
            for f in type_dir.rglob("*.json"):
                f.unlink()

    # Rebuild from all agent documents
    agents_dir = design_root / "agents"
    stats = {"agents_scanned": 0, "documents_indexed": 0, "errors": 0}

    if not agents_dir.exists():
        return {"success": True, **stats}

    for agent_dir in agents_dir.iterdir():
        if not agent_dir.is_dir() or agent_dir.name.startswith("."):
            continue

        stats["agents_scanned"] += 1
        received_dir = agent_dir / "received"

        if not received_dir.exists():
            continue

        for md_file in received_dir.rglob("*.md"):
            metadata_path = md_file.with_suffix("").with_name(f"{md_file.stem}_metadata.json")

            if not metadata_path.exists():
                stats["errors"] += 1
                continue

            try:
                metadata = json.loads(metadata_path.read_text())
                task_id = metadata.get("task_id", "unknown")
                category = metadata.get("category", "unknown")
                timestamp = metadata.get("download", {}).get("timestamp", datetime.now(timezone.utc).isoformat())

                update_index(
                    design_root=design_root,
                    task_id=task_id,
                    agent_name=agent_dir.name,
                    category=category,
                    doc_path=str(md_file.relative_to(design_root)),
                    timestamp=timestamp,
                )
                stats["documents_indexed"] += 1
            except (json.JSONDecodeError, KeyError):
                stats["errors"] += 1

    return {"success": True, **stats}


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="EOA Orchestrator Download Manager"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # download command
    dl_parser = subparsers.add_parser("download", help="Download document from agent")
    dl_parser.add_argument("--url", required=True, help="GitHub comment or file URL")
    dl_parser.add_argument("--agent", required=True, help="Sender agent name")
    dl_parser.add_argument("--task-id", required=True, help="Task ID (e.g., GH-42)")
    dl_parser.add_argument(
        "--category",
        required=True,
        choices=list(RECEIVED_CATEGORIES.keys()),
        help="Document category",
    )
    dl_parser.add_argument("--subcategory", help="Subcategory")
    dl_parser.add_argument("--doc-type", help="Document type for filename")
    dl_parser.add_argument("--design-root", type=Path, help="Design storage root")
    dl_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # index-rebuild command
    idx_parser = subparsers.add_parser("index-rebuild", help="Rebuild all indexes")
    idx_parser.add_argument("--design-root", type=Path, help="Design storage root")
    idx_parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "download":
        result = download_to_agent_folder(
            url=args.url,
            agent_name=args.agent,
            task_id=args.task_id,
            category=args.category,
            subcategory=args.subcategory,
            doc_type=args.doc_type,
            design_root=args.design_root,
        )

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result["success"]:
                print(f"Downloaded: {result['file_path']}")
                print(f"  Agent: {result['agent']}")
                print(f"  Task: {result['task_id']}")
                print(f"  SHA256: {result['sha256'][:16]}...")
            else:
                print(f"ERROR: {result['error']}")
                return 1

    elif args.command == "index-rebuild":
        result = rebuild_indexes(args.design_root)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("Index rebuild complete:")
            print(f"  Agents scanned: {result['agents_scanned']}")
            print(f"  Documents indexed: {result['documents_indexed']}")
            if result["errors"]:
                print(f"  Errors: {result['errors']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
