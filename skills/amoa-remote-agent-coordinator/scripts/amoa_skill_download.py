#!/usr/bin/env python3
"""
EOA Document Download and Storage Manager

Downloads .md files from GitHub issue comments and stores them in the
standardized design folder structure with read-only enforcement.

Usage:
    python eoa_skill_download.py download --url URL --task-id TASK_ID --category CATEGORY
    python eoa_skill_download.py init --project-root PATH
    python eoa_skill_download.py lookup --task-id TASK_ID
    python eoa_skill_download.py verify --project-root PATH
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

# Category definitions with folder structure
CATEGORIES: dict[str, dict[str, Any]] = {
    "tasks": {
        "path": "tasks/{task_id}",
        "subfolders": [],
        "retention": "permanent",
        "description": "Task delegations and assignments",
    },
    "reports": {
        "path": "reports/{task_id}",
        "subfolders": ["completion", "verification", "blockers", "status"],
        "retention": "permanent",
        "description": "Completion reports and status updates",
    },
    "acks": {
        "path": "acks/{task_id}",
        "subfolders": [],
        "retention": "90_days",
        "description": "Acknowledgment responses",
    },
    "specs": {
        "path": "specs",
        "subfolders": ["toolchains", "platforms", "configs"],
        "retention": "until_changed",
        "description": "Toolchain and platform specifications",
    },
    "plans": {
        "path": "plans/{task_id}",
        "subfolders": ["design", "implementation", "reviews"],
        "retention": "permanent",
        "description": "Design documents and plans",
    },
    "sync": {
        "path": "sync",
        "subfolders": [],
        "retention": "30_days",
        "description": "Cross-agent synchronization reports",
    },
}

# Document type to category mapping
DOCUMENT_TYPE_MAP: dict[str, tuple[str, str | None]] = {
    "delegation": ("tasks", None),
    "toolchain-spec": ("tasks", None),
    "checklist": ("tasks", None),
    "completion": ("reports", "completion"),
    "verification": ("reports", "verification"),
    "blocker": ("reports", "blockers"),
    "status": ("reports", "status"),
    "ack": ("acks", None),
    "toolchain": ("specs", "toolchains"),
    "platform": ("specs", "platforms"),
    "config": ("specs", "configs"),
    "design": ("plans", "design"),
    "implementation": ("plans", "implementation"),
    "review": ("plans", "reviews"),
    "project_sync": ("sync", None),
    "kanban_sync": ("sync", None),
}


def get_storage_root(project_root: Path | None = None) -> Path:
    """Get the design storage root directory."""
    if project_root:
        return project_root / "design" / "received"

    env_root = os.environ.get("EOA_STORAGE_ROOT")
    if env_root:
        return Path(env_root)

    cwd = Path.cwd()
    return cwd / "design" / "received"


def init_storage(project_root: Path) -> None:
    """Initialize the EOA design storage directory structure."""
    storage_root = get_storage_root(project_root)

    print(f"Initializing EOA design storage at: {storage_root}")

    # Create root
    storage_root.mkdir(parents=True, exist_ok=True)

    # Create category folders
    for category, config in CATEGORIES.items():
        cat_path = storage_root / category
        cat_path.mkdir(exist_ok=True)

        for subfolder in config["subfolders"]:
            (cat_path / subfolder).mkdir(exist_ok=True)

    # Create archive folder
    (storage_root.parent / "archive").mkdir(exist_ok=True)

    # Create .gitkeep
    gitkeep = storage_root.parent / ".gitkeep"
    gitkeep.write_text("# EOA design document storage - do not delete this folder\n")

    # Update .gitignore if in git repo
    gitignore_path = project_root / ".gitignore"
    gitignore_entry = "\n# EOA Design Document Storage (local cache)\ndesign/\n!design/.gitkeep\n"

    if gitignore_path.exists():
        content = gitignore_path.read_text()
        if "design/" not in content:
            with gitignore_path.open("a") as f:
                f.write(gitignore_entry)
            print(f"Updated {gitignore_path}")
    else:
        gitignore_path.write_text(gitignore_entry)
        print(f"Created {gitignore_path}")

    print("EOA design storage initialized successfully")


def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with file_path.open("rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def set_readonly(path: Path, recursive: bool = False) -> None:
    """Set file or directory to read-only."""
    if path.is_file():
        # Remove write permissions: r--r--r--
        current = path.stat().st_mode
        path.chmod(current & ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH)
    elif path.is_dir():
        if recursive:
            for item in path.rglob("*"):
                set_readonly(item, recursive=False)
        # Directory: r-xr-xr-x
        current = path.stat().st_mode
        path.chmod(current & ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH)


def extract_attachment_url(comment_url: str) -> str | None:
    """Extract .md attachment URL from GitHub issue comment."""
    # Parse comment URL
    match = re.match(
        r"https://github\.com/([^/]+)/([^/]+)/issues/(\d+)#issuecomment-(\d+)",
        comment_url,
    )
    if not match:
        print(f"ERROR: Invalid comment URL format: {comment_url}")
        return None

    owner, repo, _, comment_id = match.groups()

    # Fetch comment body via gh CLI
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{owner}/{repo}/issues/comments/{comment_id}", "--jq", ".body"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        body = result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to fetch comment: {e}")
        return None
    except FileNotFoundError:
        print("ERROR: gh CLI not found")
        return None

    # Find .md file URL in body
    # Pattern for GitHub file attachments
    md_urls = re.findall(r"https://github\.com/[^\s)]+\.md", body)
    if md_urls:
        return md_urls[0]

    # Pattern for user-attachments
    attachment_urls = re.findall(
        r"https://github\.com/user-attachments/files/[^\s)]+", body
    )
    if attachment_urls:
        return attachment_urls[0]

    print("WARNING: No .md attachment found in comment")
    print(f"Comment body preview: {body[:200]}...")
    return None


def download_document(
    url: str,
    task_id: str,
    category: str,
    subcategory: str | None = None,
    doc_type: str | None = None,
    sender: str = "unknown",
    project_root: Path | None = None,
) -> Path | None:
    """Download a document and store it in the correct category folder."""
    storage_root = get_storage_root(project_root)

    # Validate category
    if category not in CATEGORIES:
        print(f"ERROR: Unknown category: {category}")
        print(f"Valid categories: {list(CATEGORIES.keys())}")
        return None

    # Determine target folder
    cat_config = CATEGORIES[category]
    folder_template = cat_config["path"]

    if "{task_id}" in folder_template:
        folder_path = storage_root / folder_template.format(task_id=task_id)
    else:
        folder_path = storage_root / folder_template

    if subcategory and subcategory in cat_config["subfolders"]:
        folder_path = folder_path / subcategory

    folder_path.mkdir(parents=True, exist_ok=True)

    # Determine filename
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    if doc_type:
        filename = f"{timestamp}_{doc_type}.md"
    else:
        # Extract from URL or use default
        url_filename = url.split("/")[-1]
        if url_filename.endswith(".md"):
            filename = f"{timestamp}_{url_filename}"
        else:
            filename = f"{timestamp}_document.md"

    file_path = folder_path / filename

    # Check if attachment URL needs extraction
    if "#issuecomment-" in url:
        attachment_url = extract_attachment_url(url)
        if not attachment_url:
            print("ERROR: Could not extract attachment URL from comment")
            return None
        download_url = attachment_url
    else:
        download_url = url

    # Download file
    print(f"Downloading: {download_url}")
    print(f"Target: {file_path}")

    try:
        subprocess.run(
            ["curl", "-fsSL", download_url, "-o", str(file_path)],
            capture_output=True,
            text=True,
            check=True,
            timeout=60,
        )
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Download failed: {e}")
        print(f"stderr: {e.stderr}")
        return None

    if not file_path.exists() or file_path.stat().st_size == 0:
        print("ERROR: Downloaded file is empty or missing")
        return None

    # Compute hash
    sha256 = compute_sha256(file_path)

    # Create metadata
    metadata = {
        "schema_version": "1.0.0",
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
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": os.environ.get("EOA_AGENT_NAME", "unknown"),
            "sha256": sha256,
            "file_size_bytes": file_path.stat().st_size,
        },
        "sender": {
            "agent": sender,
            "via": "ai_maestro",
        },
        "ack_sent": False,
        "ack_timestamp": None,
    }

    metadata_path = folder_path / f"{filename.replace('.md', '')}_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2))

    # Set read-only
    set_readonly(file_path)
    set_readonly(metadata_path)
    set_readonly(folder_path)

    print(f"Downloaded and locked: {file_path}")
    print(f"SHA256: {sha256}")

    return file_path


def lookup_documents(
    task_id: str,
    project_root: Path | None = None,
    category: str | None = None,
) -> list[dict[str, Any]]:
    """Find all documents for a task ID."""
    storage_root = get_storage_root(project_root)
    results: list[dict[str, Any]] = []

    search_categories = [category] if category else list(CATEGORIES.keys())

    for cat in search_categories:
        cat_path = storage_root / cat

        if not cat_path.exists():
            continue

        # Search for task_id folders
        for task_folder in cat_path.rglob(task_id):
            if task_folder.is_dir():
                for md_file in task_folder.glob("*.md"):
                    metadata_file = md_file.with_suffix("").with_name(
                        f"{md_file.stem}_metadata.json"
                    )
                    metadata = {}
                    if metadata_file.exists():
                        try:
                            metadata = json.loads(metadata_file.read_text())
                        except json.JSONDecodeError:
                            pass

                    results.append({
                        "path": str(md_file),
                        "category": cat,
                        "task_id": task_id,
                        "metadata": metadata,
                    })

    return results


def verify_storage(project_root: Path | None = None) -> dict[str, Any]:
    """Verify storage integrity and permissions."""
    storage_root = get_storage_root(project_root)
    report: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "storage_root": str(storage_root),
        "issues": [],
        "stats": {
            "total_files": 0,
            "total_size_bytes": 0,
            "by_category": {},
        },
    }

    if not storage_root.exists():
        report["issues"].append({
            "type": "missing_root",
            "message": f"Storage root does not exist: {storage_root}",
        })
        return report

    for category in CATEGORIES:
        cat_path = storage_root / category
        cat_stats = {"files": 0, "size_bytes": 0}

        if not cat_path.exists():
            continue

        for md_file in cat_path.rglob("*.md"):
            cat_stats["files"] += 1
            cat_stats["size_bytes"] += md_file.stat().st_size
            report["stats"]["total_files"] += 1
            report["stats"]["total_size_bytes"] += md_file.stat().st_size

            # Check read-only
            mode = md_file.stat().st_mode
            if mode & stat.S_IWUSR or mode & stat.S_IWGRP or mode & stat.S_IWOTH:
                report["issues"].append({
                    "type": "writable_file",
                    "path": str(md_file),
                    "message": "File is not read-only",
                })

            # Check metadata exists
            metadata_file = md_file.with_suffix("").with_name(
                f"{md_file.stem}_metadata.json"
            )
            if not metadata_file.exists():
                report["issues"].append({
                    "type": "missing_metadata",
                    "path": str(md_file),
                    "message": "Metadata file missing",
                })
            else:
                # Verify SHA256
                try:
                    metadata = json.loads(metadata_file.read_text())
                    stored_hash = metadata.get("download", {}).get("sha256")
                    if stored_hash:
                        current_hash = compute_sha256(md_file)
                        if stored_hash != current_hash:
                            report["issues"].append({
                                "type": "integrity_violation",
                                "path": str(md_file),
                                "message": f"SHA256 mismatch: stored={stored_hash[:16]}... current={current_hash[:16]}...",
                            })
                except json.JSONDecodeError:
                    report["issues"].append({
                        "type": "invalid_metadata",
                        "path": str(metadata_file),
                        "message": "Metadata JSON is invalid",
                    })

        report["stats"]["by_category"][category] = cat_stats

    return report


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="EOA Document Download and Storage Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize storage structure")
    init_parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory",
    )

    # download command
    dl_parser = subparsers.add_parser("download", help="Download a document")
    dl_parser.add_argument("--url", required=True, help="GitHub comment or file URL")
    dl_parser.add_argument("--task-id", required=True, help="Task ID (e.g., GH-42)")
    dl_parser.add_argument(
        "--category",
        required=True,
        choices=list(CATEGORIES.keys()),
        help="Document category",
    )
    dl_parser.add_argument("--subcategory", help="Subcategory within category")
    dl_parser.add_argument("--doc-type", help="Document type for filename")
    dl_parser.add_argument("--sender", default="unknown", help="Sender agent name")
    dl_parser.add_argument("--project-root", type=Path, help="Project root directory")

    # lookup command
    lookup_parser = subparsers.add_parser("lookup", help="Find documents by task ID")
    lookup_parser.add_argument("--task-id", required=True, help="Task ID to search")
    lookup_parser.add_argument("--category", help="Filter by category")
    lookup_parser.add_argument("--project-root", type=Path, help="Project root directory")

    # verify command
    verify_parser = subparsers.add_parser("verify", help="Verify storage integrity")
    verify_parser.add_argument("--project-root", type=Path, help="Project root directory")
    verify_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "init":
        init_storage(args.project_root)
        return 0

    elif args.command == "download":
        result = download_document(
            url=args.url,
            task_id=args.task_id,
            category=args.category,
            subcategory=args.subcategory,
            doc_type=args.doc_type,
            sender=args.sender,
            project_root=args.project_root,
        )
        return 0 if result else 1

    elif args.command == "lookup":
        results = lookup_documents(
            task_id=args.task_id,
            project_root=args.project_root,
            category=args.category,
        )
        if results:
            print(f"\nFound {len(results)} document(s) for {args.task_id}:\n")
            for doc in results:
                print(f"  [{doc['category']}] {doc['path']}")
                if doc["metadata"]:
                    ts = doc["metadata"].get("download", {}).get("timestamp", "?")
                    print(f"           Downloaded: {ts}")
        else:
            print(f"No documents found for task: {args.task_id}")
        return 0

    elif args.command == "verify":
        report = verify_storage(args.project_root)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("\n=== EOA Design Storage Verification Report ===\n")
            print(f"Storage Root: {report['storage_root']}")
            print(f"Total Files: {report['stats']['total_files']}")
            print(f"Total Size: {report['stats']['total_size_bytes']} bytes")
            print("\nBy Category:")
            for cat, stats in report["stats"]["by_category"].items():
                print(f"  {cat}: {stats['files']} files, {stats['size_bytes']} bytes")

            if report["issues"]:
                print(f"\nIssues Found: {len(report['issues'])}")
                for issue in report["issues"]:
                    print(f"  [{issue['type']}] {issue['message']}")
                    if "path" in issue:
                        print(f"    Path: {issue['path']}")
            else:
                print("\nNo issues found. Storage is healthy.")

        return 1 if report["issues"] else 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
