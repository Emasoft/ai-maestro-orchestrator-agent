#!/usr/bin/env python3
"""
Enforce Document Delivery Protocol for Remote Agent Coordination

This script validates and enforces the document delivery protocol:
- Rejects messages with embedded markdown content (>500 chars)
- Tracks ACK responses for document deliveries
- Uploads documents to GitHub issue comments and returns URLs
"""

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Tuple


ACK_TRACKING_FILE = Path.home() / ".emasoft-orchestrator" / "ack-tracking.json"


@dataclass
class AckRecord:
    """Record of a document delivery awaiting acknowledgment"""

    task_id: str
    document_name: str
    sent_timestamp: float
    timeout_seconds: int
    github_url: Optional[str] = None
    recipient_agent: Optional[str] = None
    ack_received: bool = False
    ack_timestamp: Optional[float] = None

    def is_expired(self) -> bool:
        """Check if ACK timeout has expired"""
        if self.ack_received:
            return False
        elapsed = time.time() - self.sent_timestamp
        return elapsed > self.timeout_seconds

    def time_remaining(self) -> int:
        """Get remaining time before timeout (seconds)"""
        if self.ack_received:
            return 0
        elapsed = time.time() - self.sent_timestamp
        remaining = self.timeout_seconds - elapsed
        return max(0, int(remaining))


class DocumentDeliveryEnforcer:
    """Enforce document delivery protocol"""

    # Markdown patterns that indicate embedded document content
    MARKDOWN_PATTERNS = [
        r"#{1,6}\s+\w+",  # Headers (# Title)
        r"^\s*-\s+\[[ x]\]",  # Task lists (- [ ] item)
        r"```[\w]*\n",  # Code blocks (```language)
        r"^\s*\|\s*\w+\s*\|",  # Tables (| col |)
        r"^\s*>\s+\w+",  # Blockquotes (> quote)
        r"^\s*\d+\.\s+\w+",  # Numbered lists (1. item)
        r"^\s*[-*+]\s+\w+",  # Bullet lists (- item)
    ]

    def __init__(self):
        """Initialize enforcer and ensure ACK tracking directory exists"""
        ACK_TRACKING_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not ACK_TRACKING_FILE.exists():
            ACK_TRACKING_FILE.write_text("[]")

    def validate_message(self, message: str) -> Tuple[bool, str]:
        """
        Validate that message does not contain embedded document content.

        Returns:
            (is_valid, reason) - True if valid (no embedded docs), False otherwise
        """
        # Check message length - short messages are always OK
        if len(message) < 500:
            return True, "Message is short enough to not contain embedded documents"

        # Check for markdown patterns
        markdown_indicators = 0
        found_patterns = []

        for pattern in self.MARKDOWN_PATTERNS:
            if re.search(pattern, message, re.MULTILINE):
                markdown_indicators += 1
                found_patterns.append(pattern)

        # If multiple markdown patterns found, likely an embedded document
        if markdown_indicators >= 3:
            return (
                False,
                f"Message contains embedded markdown document (found {markdown_indicators} patterns: {', '.join(found_patterns[:3])}...)",
            )

        # Check for very long paragraphs (typical of embedded documents)
        lines = message.split("\n")
        long_paragraphs = sum(1 for line in lines if len(line) > 200)
        if long_paragraphs >= 3:
            return (
                False,
                f"Message contains {long_paragraphs} very long paragraphs, suggesting embedded document content",
            )

        # Check markdown density (ratio of markdown to text)
        markdown_chars = sum(len(re.findall(r"[#*`|>\-\[\]]", line)) for line in lines)
        if len(message) > 1000 and markdown_chars / len(message) > 0.1:
            return (
                False,
                f"High markdown density ({markdown_chars}/{len(message)} = {markdown_chars / len(message):.2%}) suggests embedded document",
            )

        return True, "Message appears to be a plain message without embedded documents"

    def upload_to_github(
        self, file_path: Path, issue_number: int, repo: str
    ) -> Optional[str]:
        """
        Upload markdown file to GitHub issue comment and return comment URL.

        Args:
            file_path: Path to .md file to upload
            issue_number: GitHub issue number
            repo: Repository in format 'owner/repo'

        Returns:
            Comment URL if successful, None otherwise
        """
        if not file_path.exists():
            print(
                json.dumps({"error": f"File not found: {file_path}"}), file=sys.stderr
            )
            return None

        # Read file content
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            print(json.dumps({"error": f"Failed to read file: {e}"}), file=sys.stderr)
            return None

        # Create GitHub comment with file content
        comment_body = f"## Document Delivery: {file_path.name}\n\n{content}"

        try:
            # Use gh CLI to create comment
            result = subprocess.run(
                [
                    "gh",
                    "issue",
                    "comment",
                    str(issue_number),
                    "--repo",
                    repo,
                    "--body",
                    comment_body,
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            # Get the comment URL - gh returns the URL in stdout
            comment_url = result.stdout.strip()

            # If gh didn't return URL directly, construct it
            if not comment_url.startswith("http"):
                comment_url = f"https://github.com/{repo}/issues/{issue_number}#issuecomment-latest"

            return comment_url

        except subprocess.CalledProcessError as e:
            print(
                json.dumps(
                    {
                        "error": f"Failed to create GitHub comment: {e.stderr}",
                        "command": e.cmd,
                    }
                ),
                file=sys.stderr,
            )
            return None

    def track_ack(
        self,
        task_id: str,
        document_name: str,
        timeout: int,
        github_url: Optional[str] = None,
        recipient: Optional[str] = None,
    ) -> None:
        """
        Start tracking acknowledgment for a sent document.

        Args:
            task_id: Unique task identifier (e.g., "GH-42")
            document_name: Name of the document sent
            timeout: Timeout in seconds to wait for ACK
            github_url: Optional GitHub URL where document was posted
            recipient: Optional recipient agent name
        """
        records = self._load_ack_records()

        # Create new ACK record
        record = AckRecord(
            task_id=task_id,
            document_name=document_name,
            sent_timestamp=time.time(),
            timeout_seconds=timeout,
            github_url=github_url,
            recipient_agent=recipient,
        )

        records.append(record)
        self._save_ack_records(records)

        print(
            json.dumps(
                {
                    "status": "tracking_started",
                    "task_id": task_id,
                    "document": document_name,
                    "timeout_seconds": timeout,
                    "expires_at": datetime.fromtimestamp(
                        record.sent_timestamp + timeout
                    ).isoformat(),
                }
            )
        )

    def mark_ack_received(self, task_id: str) -> bool:
        """
        Mark that acknowledgment was received for a task.

        Args:
            task_id: Task identifier

        Returns:
            True if record found and updated, False otherwise
        """
        records = self._load_ack_records()

        for record in records:
            if record.task_id == task_id and not record.ack_received:
                record.ack_received = True
                record.ack_timestamp = time.time()
                self._save_ack_records(records)
                return True

        return False

    def get_pending_acks(self) -> List[AckRecord]:
        """
        Get all pending (not yet acknowledged) ACK records.

        Returns:
            List of pending ACK records
        """
        records = self._load_ack_records()
        return [r for r in records if not r.ack_received]

    def get_expired_acks(self) -> List[AckRecord]:
        """
        Get all expired (timed out) ACK records.

        Returns:
            List of expired ACK records
        """
        records = self._load_ack_records()
        return [r for r in records if not r.ack_received and r.is_expired()]

    def cleanup_old_records(self, days: int = 7) -> int:
        """
        Remove ACK records older than specified days.

        Args:
            days: Remove records older than this many days

        Returns:
            Number of records removed
        """
        records = self._load_ack_records()
        cutoff_time = time.time() - (days * 86400)

        original_count = len(records)
        records = [r for r in records if r.sent_timestamp > cutoff_time]

        self._save_ack_records(records)
        return original_count - len(records)

    def _load_ack_records(self) -> List[AckRecord]:
        """Load ACK records from JSON file"""
        try:
            data = json.loads(ACK_TRACKING_FILE.read_text())
            return [AckRecord(**record) for record in data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_ack_records(self, records: List[AckRecord]) -> None:
        """Save ACK records to JSON file"""
        data = [asdict(record) for record in records]
        ACK_TRACKING_FILE.write_text(json.dumps(data, indent=2))


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate a message for embedded documents"""
    enforcer = DocumentDeliveryEnforcer()
    is_valid, reason = enforcer.validate_message(args.message)

    result = {"valid": is_valid, "reason": reason, "message_length": len(args.message)}

    print(json.dumps(result, indent=2))
    return 0 if is_valid else 1


def cmd_upload(args: argparse.Namespace) -> int:
    """Upload document to GitHub issue comment"""
    enforcer = DocumentDeliveryEnforcer()
    file_path = Path(args.file)

    if not file_path.exists():
        print(json.dumps({"error": f"File not found: {file_path}"}), file=sys.stderr)
        return 1

    url = enforcer.upload_to_github(file_path, args.issue, args.repo)

    if url:
        result = {
            "status": "success",
            "url": url,
            "file": str(file_path),
            "issue": args.issue,
            "repo": args.repo,
        }
        print(json.dumps(result, indent=2))
        return 0
    else:
        return 1


def cmd_track_ack(args: argparse.Namespace) -> int:
    """Start tracking acknowledgment for a sent document"""
    enforcer = DocumentDeliveryEnforcer()

    # Extract document name from task_id if not provided
    document_name = args.document or f"Document for {args.task_id}"

    enforcer.track_ack(
        task_id=args.task_id,
        document_name=document_name,
        timeout=args.timeout,
        github_url=args.url,
        recipient=args.recipient,
    )
    return 0


def cmd_mark_ack(args: argparse.Namespace) -> int:
    """Mark acknowledgment as received"""
    enforcer = DocumentDeliveryEnforcer()

    if enforcer.mark_ack_received(args.task_id):
        print(
            json.dumps(
                {
                    "status": "success",
                    "task_id": args.task_id,
                    "ack_received_at": datetime.now().isoformat(),
                }
            )
        )
        return 0
    else:
        print(
            json.dumps(
                {
                    "status": "not_found",
                    "task_id": args.task_id,
                    "error": "No pending ACK record found for this task_id",
                }
            ),
            file=sys.stderr,
        )
        return 1


def cmd_pending_acks(_args: argparse.Namespace) -> int:
    """Check pending acknowledgments"""
    enforcer = DocumentDeliveryEnforcer()
    pending = enforcer.get_pending_acks()

    if not pending:
        print(json.dumps({"status": "no_pending_acks", "count": 0}))
        return 0

    records: list[dict[str, Any]] = []
    result: dict[str, Any] = {
        "status": "pending_acks_found",
        "count": len(pending),
        "records": records,
    }

    for record in pending:
        records.append(
            {
                "task_id": record.task_id,
                "document": record.document_name,
                "sent_at": datetime.fromtimestamp(record.sent_timestamp).isoformat(),
                "time_remaining_seconds": record.time_remaining(),
                "expired": record.is_expired(),
                "recipient": record.recipient_agent,
                "github_url": record.github_url,
            }
        )

    print(json.dumps(result, indent=2))

    # Return exit code 1 if any expired ACKs
    has_expired = any(r.is_expired() for r in pending)
    return 1 if has_expired else 0


def cmd_cleanup(args: argparse.Namespace) -> int:
    """Cleanup old ACK records"""
    enforcer = DocumentDeliveryEnforcer()
    removed = enforcer.cleanup_old_records(args.days)

    result = {"status": "cleanup_complete", "records_removed": removed}

    print(json.dumps(result, indent=2))
    return 0


def main() -> int:
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Enforce Document Delivery Protocol for Remote Agent Coordination",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate message for embedded documents"
    )
    validate_parser.add_argument(
        "--message", required=True, help="Message content to validate"
    )
    validate_parser.set_defaults(func=cmd_validate)

    # Upload command
    upload_parser = subparsers.add_parser(
        "upload", help="Upload document to GitHub issue comment"
    )
    upload_parser.add_argument(
        "--file", required=True, help="Path to .md file to upload"
    )
    upload_parser.add_argument(
        "--issue", type=int, required=True, help="GitHub issue number"
    )
    upload_parser.add_argument(
        "--repo", required=True, help="Repository (owner/repo format)"
    )
    upload_parser.set_defaults(func=cmd_upload)

    # Track ACK command
    track_parser = subparsers.add_parser(
        "track-ack", help="Start tracking acknowledgment for sent document"
    )
    track_parser.add_argument(
        "--task-id", required=True, help="Task identifier (e.g., GH-42)"
    )
    track_parser.add_argument(
        "--document", help="Document name (optional, derived from task-id if omitted)"
    )
    track_parser.add_argument(
        "--timeout", type=int, default=300, help="Timeout in seconds (default: 300)"
    )
    track_parser.add_argument(
        "--url", help="GitHub URL where document was posted (optional)"
    )
    track_parser.add_argument("--recipient", help="Recipient agent name (optional)")
    track_parser.set_defaults(func=cmd_track_ack)

    # Mark ACK command
    mark_parser = subparsers.add_parser(
        "mark-ack", help="Mark acknowledgment as received"
    )
    mark_parser.add_argument("--task-id", required=True, help="Task identifier")
    mark_parser.set_defaults(func=cmd_mark_ack)

    # Pending ACKs command
    pending_parser = subparsers.add_parser(
        "pending-acks", help="Check pending acknowledgments"
    )
    pending_parser.set_defaults(func=cmd_pending_acks)

    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Cleanup old ACK records")
    cleanup_parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Remove records older than N days (default: 7)",
    )
    cleanup_parser.set_defaults(func=cmd_cleanup)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
