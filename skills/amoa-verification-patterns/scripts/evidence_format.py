#!/usr/bin/env python3
"""Evidence format enforcement for verification-patterns.

Defines required format for all verification evidence and provides
validation functions to ensure compliance.
"""

import sys
import json
import re
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

SKILLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_DIR / "shared"))
from thresholds import VERIFICATION  # type: ignore[import-not-found]  # noqa: E402


class EvidenceType(Enum):
    """Types of verification evidence."""

    EXIT_CODE = "exit_code"
    FILE_CONTENT = "file_content"
    COMMAND_OUTPUT = "command_output"
    SCREENSHOT = "screenshot"
    LOG_EXCERPT = "log_excerpt"
    TEST_RESULT = "test_result"
    API_RESPONSE = "api_response"
    METRIC = "metric"
    APPROVAL = "approval"


class VerificationStatus(Enum):
    """Verification outcome status."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class Evidence:
    """Single piece of verification evidence.

    This is the REQUIRED format for all evidence collected.
    """

    # Required fields
    evidence_id: str
    evidence_type: EvidenceType
    timestamp: str  # ISO-8601 format
    description: str

    # Type-specific data
    value: Any  # The actual evidence value

    # Optional context
    source: Optional[str] = None  # Where this came from (file, command, etc.)
    related_task: Optional[str] = None  # Task ID this relates to
    collector: Optional[str] = None  # Agent/tool that collected this

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "evidence_id": self.evidence_id,
            "evidence_type": self.evidence_type.value,
            "timestamp": self.timestamp,
            "description": self.description,
            "value": self.value,
            "source": self.source,
            "related_task": self.related_task,
            "collector": self.collector,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Evidence":
        """Create from dictionary."""
        return cls(
            evidence_id=data["evidence_id"],
            evidence_type=EvidenceType(data["evidence_type"]),
            timestamp=data["timestamp"],
            description=data["description"],
            value=data["value"],
            source=data.get("source"),
            related_task=data.get("related_task"),
            collector=data.get("collector"),
        )


@dataclass
class VerificationRecord:
    """Complete verification record with evidence.

    This is the REQUIRED format for verification reports.
    """

    # Required fields
    verification_id: str
    task_id: str
    verification_type: str  # exit_code, evidence_based, integration, e2e
    timestamp: str
    status: VerificationStatus

    # Evidence collection
    evidence: list[Evidence] = field(default_factory=list)

    # Execution details
    command_executed: Optional[str] = None
    exit_code: Optional[int] = None
    duration_ms: Optional[int] = None

    # Results
    summary: Optional[str] = None
    details: Optional[str] = None

    # Metadata
    agent_id: Optional[str] = None
    environment: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "verification_id": self.verification_id,
            "task_id": self.task_id,
            "verification_type": self.verification_type,
            "timestamp": self.timestamp,
            "status": self.status.value,
            "evidence": [e.to_dict() for e in self.evidence],
            "command_executed": self.command_executed,
            "exit_code": self.exit_code,
            "duration_ms": self.duration_ms,
            "summary": self.summary,
            "details": self.details,
            "agent_id": self.agent_id,
            "environment": self.environment,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VerificationRecord":
        """Create from dictionary."""
        return cls(
            verification_id=data["verification_id"],
            task_id=data["task_id"],
            verification_type=data["verification_type"],
            timestamp=data["timestamp"],
            status=VerificationStatus(data["status"]),
            evidence=[Evidence.from_dict(e) for e in data.get("evidence", [])],
            command_executed=data.get("command_executed"),
            exit_code=data.get("exit_code"),
            duration_ms=data.get("duration_ms"),
            summary=data.get("summary"),
            details=data.get("details"),
            agent_id=data.get("agent_id"),
            environment=data.get("environment"),
        )


# ============================================================
# VALIDATION FUNCTIONS
# ============================================================


def validate_evidence(evidence: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate evidence meets format requirements."""
    errors = []

    # Required fields
    required = ["evidence_id", "evidence_type", "timestamp", "description", "value"]
    for field_name in required:
        if field_name not in evidence:
            errors.append(f"Missing required field: {field_name}")

    # Validate evidence_type
    if "evidence_type" in evidence:
        valid_types = [t.value for t in EvidenceType]
        if evidence["evidence_type"] not in valid_types:
            errors.append(
                f"Invalid evidence_type: {evidence['evidence_type']}. Valid: {valid_types}"
            )

    # Validate timestamp format (ISO-8601)
    if "timestamp" in evidence:
        try:
            datetime.fromisoformat(evidence["timestamp"].replace("Z", "+00:00"))
        except ValueError:
            errors.append(
                f"Invalid timestamp format: {evidence['timestamp']}. Use ISO-8601."
            )

    # Validate evidence_id format
    if "evidence_id" in evidence:
        if not re.match(r"^[a-zA-Z0-9_-]+$", evidence["evidence_id"]):
            errors.append(f"Invalid evidence_id format: {evidence['evidence_id']}")

    return len(errors) == 0, errors


def validate_verification_record(record: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate verification record meets format requirements."""
    errors = []

    # Required fields
    required = [
        "verification_id",
        "task_id",
        "verification_type",
        "timestamp",
        "status",
    ]
    for field_name in required:
        if field_name not in record:
            errors.append(f"Missing required field: {field_name}")

    # Validate status
    if "status" in record:
        valid_statuses = [s.value for s in VerificationStatus]
        if record["status"] not in valid_statuses:
            errors.append(
                f"Invalid status: {record['status']}. Valid: {valid_statuses}"
            )

    # Validate verification_type
    valid_types = ["exit_code", "evidence_based", "integration", "e2e"]
    if "verification_type" in record and record["verification_type"] not in valid_types:
        errors.append(
            f"Invalid verification_type: {record['verification_type']}. Valid: {valid_types}"
        )

    # Validate evidence items
    if "evidence" in record:
        if not isinstance(record["evidence"], list):
            errors.append("'evidence' must be a list")
        else:
            for i, ev in enumerate(record["evidence"]):
                valid, ev_errors = validate_evidence(ev)
                if not valid:
                    errors.extend([f"evidence[{i}]: {e}" for e in ev_errors])

    # Check minimum evidence requirement
    if (
        "evidence" in record
        and len(record.get("evidence", [])) < VERIFICATION.MIN_EVIDENCE_ITEMS
    ):
        errors.append(
            f"Insufficient evidence: {len(record['evidence'])} items "
            f"(minimum: {VERIFICATION.MIN_EVIDENCE_ITEMS})"
        )

    # Validate exit_code for exit_code type
    if record.get("verification_type") == "exit_code":
        if "exit_code" not in record:
            errors.append("exit_code verification requires 'exit_code' field")

    return len(errors) == 0, errors


def validate_evidence_file(file_path: Path) -> tuple[bool, list[str]]:
    """Validate a JSON evidence file."""
    errors = []

    if not file_path.exists():
        return False, [f"File not found: {file_path}"]

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]

    # Determine if it's a single record or a list
    if isinstance(data, list):
        for i, record in enumerate(data):
            valid, record_errors = validate_verification_record(record)
            if not valid:
                errors.extend([f"record[{i}]: {e}" for e in record_errors])
    else:
        valid, record_errors = validate_verification_record(data)
        errors.extend(record_errors)

    return len(errors) == 0, errors


# ============================================================
# EVIDENCE CREATION HELPERS
# ============================================================


def create_exit_code_evidence(
    exit_code: int, command: str, stdout: str = "", stderr: str = ""
) -> Evidence:
    """Create evidence from command exit code."""
    import uuid

    return Evidence(
        evidence_id=f"exit-{uuid.uuid4().hex[:8]}",
        evidence_type=EvidenceType.EXIT_CODE,
        timestamp=datetime.utcnow().isoformat(),
        description=f"Exit code from: {command}",
        value={
            "exit_code": exit_code,
            "command": command,
            "stdout_excerpt": stdout[:500] if stdout else None,
            "stderr_excerpt": stderr[:500] if stderr else None,
        },
        source="command_execution",
    )


def create_test_result_evidence(
    test_name: str, passed: bool, duration_ms: int, output: str = ""
) -> Evidence:
    """Create evidence from test result."""
    import uuid

    return Evidence(
        evidence_id=f"test-{uuid.uuid4().hex[:8]}",
        evidence_type=EvidenceType.TEST_RESULT,
        timestamp=datetime.utcnow().isoformat(),
        description=f"Test result: {test_name}",
        value={
            "test_name": test_name,
            "passed": passed,
            "duration_ms": duration_ms,
            "output_excerpt": output[:500] if output else None,
        },
        source="test_execution",
    )


def create_approval_evidence(
    approver: str, approval_type: str, reference: str
) -> Evidence:
    """Create evidence of approval (review, sign-off, etc.)."""
    import uuid

    return Evidence(
        evidence_id=f"approval-{uuid.uuid4().hex[:8]}",
        evidence_type=EvidenceType.APPROVAL,
        timestamp=datetime.utcnow().isoformat(),
        description=f"{approval_type} by {approver}",
        value={
            "approver": approver,
            "approval_type": approval_type,
            "reference": reference,
        },
        source="manual_approval",
    )


# CLI
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evidence format enforcement")
    parser.add_argument("--validate", type=Path, help="Validate evidence file")
    parser.add_argument(
        "--schema", action="store_true", help="Print schema documentation"
    )

    args = parser.parse_args()

    if args.validate:
        valid, errors = validate_evidence_file(args.validate)
        if valid:
            print(f"✓ {args.validate} is valid")
            sys.exit(0)
        else:
            print(f"✗ {args.validate} validation failed:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)

    elif args.schema:
        print("Evidence Format Schema")
        print("=" * 50)
        print("\nEvidence Types:", [t.value for t in EvidenceType])
        print("\nVerification Statuses:", [s.value for s in VerificationStatus])
        print("\nRequired Evidence Fields:")
        print("  - evidence_id: str (alphanumeric with - and _)")
        print("  - evidence_type: EvidenceType")
        print("  - timestamp: str (ISO-8601)")
        print("  - description: str")
        print("  - value: any (type-specific)")
        print("\nRequired Verification Record Fields:")
        print("  - verification_id: str")
        print("  - task_id: str")
        print("  - verification_type: exit_code|evidence_based|integration|e2e")
        print("  - timestamp: str (ISO-8601)")
        print("  - status: passed|failed|skipped|error")
        print(f"\nMinimum evidence items: {VERIFICATION.MIN_EVIDENCE_ITEMS}")
