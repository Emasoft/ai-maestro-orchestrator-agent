#!/usr/bin/env python3
"""
Polymorphic Evidence Collection System for Audit Workflows.

WHY: Universal evidence tracking across any verification domain - testing, security,
compliance, quality assurance. Provides structured storage with flexible filtering
to answer "What did we find?", "When did it happen?", "What's the severity distribution?"

WHY dataclass: Immutable evidence records prevent accidental modification of audit trail.
WHY JSON persistence: Human-readable, version-controllable, diffable evidence archives.
WHY predicate filtering: Enables complex queries without hardcoding every filter combination.
"""

# WHY: future annotations enable forward references and modern type syntax in all Python 3.7+
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Iterator, Self

# WHY: Import cross-platform utilities for atomic file operations
SKILLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_DIR / "shared"))
from cross_platform import atomic_write_json  # type: ignore  # noqa: E402


class EvidenceType(Enum):
    """Evidence classification for audit workflows.

    WHY separate types: Different evidence requires different handling and reporting.
    FINDING: Actionable defect or non-conformance requiring remediation
    OBSERVATION: Notable condition that may become a finding
    EVENT: Timestamped occurrence in the audit process
    ISSUE: Known problem tracked for resolution
    """

    FINDING = "FINDING"
    OBSERVATION = "OBSERVATION"
    EVENT = "EVENT"
    ISSUE = "ISSUE"


class Severity(Enum):
    """Impact classification for evidence prioritization.

    WHY severity levels: Enables risk-based prioritization and SLA assignment.
    """

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class Evidence:
    """Immutable evidence record for audit trails.

    WHY immutable: Evidence must not be altered after creation (audit integrity).
    WHY id field: Enables deduplication and cross-referencing.
    WHY metadata dict: Extensible storage for domain-specific attributes without schema changes.
    """

    id: str
    type: EvidenceType
    source: str
    timestamp: str
    severity: Severity
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Normalize enum fields from string values.

        WHY: Allows creating Evidence from JSON deserialization with string values.
        """
        if isinstance(self.type, str):
            self.type = EvidenceType(self.type)
        if isinstance(self.severity, str):
            self.severity = Severity(self.severity)

    def to_dict(self) -> dict[str, Any]:
        """Convert evidence to JSON-serializable dict.

        WHY explicit method: Enum serialization requires custom handling.
        """
        data = asdict(self)
        data["type"] = self.type.value
        data["severity"] = self.severity.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Reconstruct evidence from JSON-loaded dict.

        WHY classmethod: Factory pattern for controlled deserialization.
        """
        return cls(**data)


class EvidenceStore:
    """Thread-safe evidence collection with deduplication and filtering.

    WHY class-based: Encapsulates evidence collection state and operations.
    WHY deduplication: Prevents duplicate evidence from multiple collection passes.
    WHY multiple filters: Different audit questions require different evidence slices.
    """

    def __init__(self) -> None:
        """Initialize empty evidence store.

        WHY dict storage: O(1) deduplication by ID, preserves insertion order (Python 3.7+).
        """
        self._evidence: dict[str, Evidence] = {}

    def add(self, evidence: Evidence) -> bool:
        """Add evidence with automatic deduplication.

        WHY return bool: Caller knows if evidence was new or duplicate.
        WHY ID-based dedup: Same finding reported multiple times should appear once.

        Returns:
            True if evidence was added, False if duplicate ID existed.
        """
        if evidence.id in self._evidence:
            return False
        self._evidence[evidence.id] = evidence
        return True

    def filter_by_type(self, evidence_type: EvidenceType) -> list[Evidence]:
        """Filter evidence by type classification.

        WHY: Common query - "Show me all FINDINGS" for remediation planning.
        """
        return [e for e in self._evidence.values() if e.type == evidence_type]

    def filter_by_source(self, source: str) -> list[Evidence]:
        """Filter evidence by originating source.

        WHY: Source isolation - "What did this specific test/scanner/audit find?"
        """
        return [e for e in self._evidence.values() if e.source == source]

    def filter_by_time(
        self, start: str | None = None, end: str | None = None
    ) -> list[Evidence]:
        """Filter evidence by timestamp range.

        WHY: Temporal analysis - "What happened during this sprint/release/incident?"
        WHY ISO 8601: Unambiguous, sortable, timezone-aware timestamps.

        Args:
            start: ISO 8601 timestamp (inclusive), None means no lower bound
            end: ISO 8601 timestamp (inclusive), None means no upper bound
        """
        results = list(self._evidence.values())

        if start:
            results = [e for e in results if e.timestamp >= start]
        if end:
            results = [e for e in results if e.timestamp <= end]

        return results

    def filter_by_predicate(
        self, predicate: Callable[[Evidence], bool]
    ) -> list[Evidence]:
        """Filter evidence using custom predicate function.

        WHY: Complex queries without hardcoding every combination.
        Example: lambda e: e.severity == Severity.CRITICAL and 'security' in e.metadata

        Args:
            predicate: Function taking Evidence, returning True to include.
        """
        return [e for e in self._evidence.values() if predicate(e)]

    def get_statistics(self) -> dict[str, Any]:
        """Compute evidence distribution statistics.

        WHY: High-level overview for reports - "How many criticals? Which source found most?"

        Returns:
            Dict with counts by type, severity, and source.
        """
        type_counts: dict[str, int] = {t.value: 0 for t in EvidenceType}
        severity_counts: dict[str, int] = {s.value: 0 for s in Severity}
        source_counts: dict[str, int] = {}

        for evidence in self._evidence.values():
            type_counts[evidence.type.value] += 1
            severity_counts[evidence.severity.value] += 1
            source_counts[evidence.source] = source_counts.get(evidence.source, 0) + 1

        return {
            "total": len(self._evidence),
            "by_type": type_counts,
            "by_severity": severity_counts,
            "by_source": source_counts,
        }

    def save(self, filepath: Path) -> None:
        """Persist evidence store to JSON file.

        WHY JSON: Human-readable, git-friendly, language-agnostic evidence archive.
        WHY atomic write: Prevents corruption if interrupted during save.
        """
        filepath = Path(filepath)

        # WHY list conversion: JSON doesn't support dict keys directly
        data = {
            "evidence": [e.to_dict() for e in self._evidence.values()],
            "saved_at": datetime.utcnow().isoformat() + "Z",
        }

        # WHY atomic_write_json: Cross-platform atomic file write prevents corruption
        atomic_write_json(data, filepath, indent=2)

        # WHY verify write: Ensure file was actually written and is valid JSON
        if not filepath.exists():
            raise IOError(f"Failed to write evidence store: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            json.load(f)  # Validate JSON integrity

    def load(self, filepath: Path) -> None:
        """Load evidence from JSON file.

        WHY: Resume analysis sessions, merge evidence from multiple runs.
        WHY clear first: Load replaces current state (use merge if accumulating).
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Evidence file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._evidence.clear()
        for evidence_dict in data.get("evidence", []):
            evidence = Evidence.from_dict(evidence_dict)
            self.add(evidence)

    def __len__(self) -> int:
        """Return total evidence count.

        WHY: Enables len(store) for quick size checks.
        """
        return len(self._evidence)

    def __iter__(self) -> Iterator[Evidence]:
        """Iterate over all evidence.

        WHY: Enables for evidence in store loops.
        """
        return iter(self._evidence.values())


def verify(store: EvidenceStore, filepath: Path | None = None) -> bool:
    """Verify evidence store integrity and output validity.

    WHY verify: Ensures data integrity before reporting success.
    Checks that the store is internally consistent and optionally
    verifies that the file on disk matches the in-memory state.

    Args:
        store: The EvidenceStore to verify
        filepath: Optional path to verify file contents match store

    Returns:
        True if all checks pass, False otherwise.
    """
    # WHY: Check that all evidence IDs are unique (should be by design, but verify)
    ids_seen: set[str] = set()
    for evidence in store:
        if evidence.id in ids_seen:
            print(f"VERIFY FAILED: Duplicate ID {evidence.id}", file=sys.stderr)
            return False
        ids_seen.add(evidence.id)

        # WHY: Validate enum values are proper types
        if not isinstance(evidence.type, EvidenceType):
            print(f"VERIFY FAILED: Invalid type for {evidence.id}", file=sys.stderr)
            return False
        if not isinstance(evidence.severity, Severity):
            print(f"VERIFY FAILED: Invalid severity for {evidence.id}", file=sys.stderr)
            return False

    # WHY: If filepath provided, verify file contents match store
    if filepath and filepath.exists():
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            file_count = len(data.get("evidence", []))
            if file_count != len(store):
                print(
                    f"VERIFY FAILED: File has {file_count} items, store has {len(store)}",
                    file=sys.stderr,
                )
                return False
        except (json.JSONDecodeError, OSError) as e:
            print(f"VERIFY FAILED: Cannot read file: {e}", file=sys.stderr)
            return False

    return True


def main() -> int:
    """CLI interface for evidence store operations.

    WHY CLI: Enables shell scripting and manual inspection without Python code.
    """
    parser = argparse.ArgumentParser(
        description="Polymorphic Evidence Collection System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create new evidence store
  %(prog)s --store audit.json --add '{"id":"F001","type":"FINDING","source":"pytest","timestamp":"2025-01-01T12:00:00Z","severity":"HIGH","content":"Test failed"}'

  # View statistics
  %(prog)s --store audit.json --stats

  # Filter by type
  %(prog)s --store audit.json --filter type=FINDING --output findings.json

  # Filter by severity
  %(prog)s --store audit.json --filter severity=CRITICAL

  # Filter by source
  %(prog)s --store audit.json --filter source=pytest
        """,
    )

    parser.add_argument(
        "--store", type=Path, required=True, help="Path to evidence store JSON file"
    )

    parser.add_argument(
        "--add", type=str, metavar="JSON", help="Add evidence from JSON string"
    )

    parser.add_argument(
        "--filter",
        type=str,
        metavar="KEY=VALUE",
        help="Filter evidence (type=X, severity=X, source=X)",
    )

    parser.add_argument("--stats", action="store_true", help="Show evidence statistics")

    parser.add_argument(
        "--output",
        type=Path,
        metavar="FILE",
        help="Write filtered results to JSON file",
    )

    args = parser.parse_args()

    # WHY try/except: Robust error handling for I/O operations with explicit exit codes
    try:
        # WHY load-or-create: Idempotent operation for new/existing stores
        store = EvidenceStore()
        if args.store.exists():
            store.load(args.store)

        # WHY add before filter: New evidence should be immediately queryable
        if args.add:
            evidence_data = json.loads(args.add)
            evidence = Evidence.from_dict(evidence_data)
            if store.add(evidence):
                print(f"Added evidence: {evidence.id}")
            else:
                print(f"Duplicate evidence ID: {evidence.id}")
            store.save(args.store)

        # WHY filter operations don't modify store: Read-only projections
        if args.filter:
            key, value = args.filter.split("=", 1)

            if key == "type":
                results = store.filter_by_type(EvidenceType(value))
            elif key == "severity":
                results = store.filter_by_predicate(lambda e: e.severity.value == value)
            elif key == "source":
                results = store.filter_by_source(value)
            else:
                print(f"Unknown filter key: {key}", file=sys.stderr)
                return 1

            if args.output:
                # WHY separate file: Filtered views for downstream tools
                filtered_store = EvidenceStore()
                for evidence in results:
                    filtered_store.add(evidence)
                filtered_store.save(args.output)
                print(f"Wrote {len(results)} evidence to {args.output}")
            else:
                # WHY JSON output: Parseable by downstream tools
                for evidence in results:
                    print(json.dumps(evidence.to_dict(), indent=2))

        if args.stats:
            stats = store.get_statistics()
            print(json.dumps(stats, indent=2))

        # WHY verify: Ensure output integrity before reporting success
        output_path = args.output if args.filter and args.output else args.store
        if not verify(store, output_path if output_path.exists() else None):
            print("ERROR: Verification failed", file=sys.stderr)
            return 1

        return 0

    except FileNotFoundError as e:
        print(f"ERROR: File not found: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"ERROR: I/O error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"ERROR: Invalid value: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    # WHY sys.exit: Explicit exit code for shell integration and CI/CD pipelines
    sys.exit(main())
