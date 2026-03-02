#!/usr/bin/env python3
"""
Hierarchical Checklist Compliance Validator

WHY: Complex workflows (releases, compliance audits, onboarding) require systematic
validation of dependencies, blocking conditions, and completion status. This tool
prevents missed steps and identifies bottlenecks in multi-stage processes.

Adapted from ASO launch checklist methodology for universal use.
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# WHY: Import cross-platform utilities for consistency
# NOTE: Dynamic path modification is required because shared modules are not installed packages
SKILLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_DIR / "shared"))
from cross_platform import atomic_write_json  # type: ignore[import-not-found]  # noqa: E402


@dataclass
class ChecklistItem:
    """
    Represents a single checklist item with dependencies and completion state.

    WHY: Dataclass provides type safety and clear structure for validation logic.
    Dependencies enable detection of blocked states and prerequisite chains.
    """

    id: str
    name: str
    required: bool = True
    depends_on: List[str] = field(default_factory=list)
    category: str = ""

    def __hash__(self) -> int:
        """WHY: Enable use in sets for efficient dependency tracking."""
        return hash(self.id)


class ChecklistValidator:
    """
    Validates hierarchical checklists against current completion status.

    WHY: Centralized validation prevents scattered logic and enables reusable
    compliance checking across different workflow types. Class-based design
    allows stateful operations like progress tracking and blocker analysis.
    """

    def __init__(self) -> None:
        """Initialize empty validator state."""
        self.items: Dict[str, ChecklistItem] = {}  # WHY: Fast lookup by item ID
        self.categories: List[str] = []  # WHY: Preserve category order
        self.completed: Set[str] = set()  # WHY: O(1) membership testing
        self.skipped: Set[str] = set()
        self.blocked: Set[str] = set()
        self.validation_errors: List[
            str
        ] = []  # WHY: Collect all errors for batch reporting

    def load_checklist(self, filepath: Path) -> None:
        """
        Load checklist definition from JSON file.

        WHY: Separating definition from status enables reusable templates and
        version control of compliance requirements independent of execution state.

        Args:
            filepath: Path to checklist definition JSON

        Raises:
            FileNotFoundError: If checklist file doesn't exist
            json.JSONDecodeError: If JSON is malformed
            KeyError: If required fields are missing
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # WHY: Validate structure before processing to fail fast on malformed input
        if "categories" not in data:
            raise KeyError("Checklist must contain 'categories' key")

        for category_data in data["categories"]:
            category_name = category_data.get("name", "Unnamed")
            self.categories.append(category_name)

            for item_data in category_data.get("items", []):
                # WHY: Explicit field extraction with defaults prevents runtime errors
                item = ChecklistItem(
                    id=item_data["id"],  # WHY: Required field, no default
                    name=item_data["name"],
                    required=item_data.get(
                        "required", True
                    ),  # WHY: Default to required for safety
                    depends_on=item_data.get("depends_on", []),
                    category=category_name,
                )
                self.items[item.id] = item

    def load_status(self, filepath: Path) -> None:
        """
        Load current completion status from JSON file.

        WHY: Status is separate from definition to enable incremental updates
        and multiple parallel execution tracks from same checklist template.

        Args:
            filepath: Path to status JSON

        Raises:
            FileNotFoundError: If status file doesn't exist
            json.JSONDecodeError: If JSON is malformed
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # WHY: Use sets for O(1) membership tests during validation
        self.completed = set(data.get("completed", []))
        self.skipped = set(data.get("skipped", []))
        self.blocked = set(data.get("blocked", []))

    def validate(self) -> bool:
        """
        Run validation checks on loaded checklist and status.

        WHY: Validation must be explicit method call to allow loading from multiple
        sources before running checks. Returns bool for easy scripting integration.

        Returns:
            True if validation passes, False if errors found
        """
        self.validation_errors = []

        # WHY: Check status references against defined items to catch typos early
        all_status_ids = self.completed | self.skipped | self.blocked
        undefined_ids = all_status_ids - set(self.items.keys())
        if undefined_ids:
            self.validation_errors.append(
                f"Status contains undefined item IDs: {sorted(undefined_ids)}"
            )

        # WHY: Validate dependency references to prevent circular deps and dangling refs
        for item in self.items.values():
            for dep_id in item.depends_on:
                if dep_id not in self.items:
                    self.validation_errors.append(
                        f"Item '{item.id}' depends on undefined item '{dep_id}'"
                    )

        # WHY: Detect circular dependencies that would create impossible completion states
        for item_id in self.items:
            if self._has_circular_dependency(item_id):
                self.validation_errors.append(
                    f"Circular dependency detected involving item '{item_id}'"
                )

        return len(self.validation_errors) == 0

    def _has_circular_dependency(
        self, item_id: str, visited: Optional[Set[str]] = None
    ) -> bool:
        """
        Detect circular dependencies via depth-first search.

        WHY: Circular dependencies create unresolvable blocking states. DFS is
        efficient for dependency graphs and detects cycles during traversal.

        Args:
            item_id: ID of item to check
            visited: Set of already-visited items in current path

        Returns:
            True if circular dependency found, False otherwise
        """
        if visited is None:
            visited = set()

        if item_id in visited:
            return True  # WHY: Revisiting an item in current path means cycle exists

        item = self.items.get(item_id)
        if not item:
            return False  # WHY: Undefined items handled elsewhere

        visited.add(item_id)

        # WHY: Recursively check all dependencies in current path
        for dep_id in item.depends_on:
            if self._has_circular_dependency(dep_id, visited.copy()):
                return True

        return False

    def get_progress(self) -> Dict[str, float]:
        """
        Calculate completion percentage overall and per category.

        WHY: Progress metrics enable reporting and decision-making about readiness.
        Category breakdown identifies which areas need attention.

        Returns:
            Dict with 'overall' and per-category completion percentages (0-100)
        """
        progress = {"overall": 0.0}

        if not self.items:
            return progress  # WHY: Avoid division by zero

        # WHY: Count completed required items as completion metric
        required_items = [item for item in self.items.values() if item.required]
        completed_required = sum(
            1 for item in required_items if item.id in self.completed
        )

        if required_items:
            progress["overall"] = (completed_required / len(required_items)) * 100

        # WHY: Per-category progress shows granular status for targeted improvements
        for category in self.categories:
            category_items = [
                item for item in required_items if item.category == category
            ]
            if category_items:
                category_completed = sum(
                    1 for item in category_items if item.id in self.completed
                )
                progress[category] = (category_completed / len(category_items)) * 100
            else:
                progress[category] = 0.0

        return progress

    def get_blockers(self) -> List[Dict[str, Any]]:
        """
        Identify items blocking completion due to unmet dependencies.

        WHY: Blockers are critical path items preventing forward progress.
        Surfacing them enables prioritized resolution and prevents stalls.

        Returns:
            List of dicts describing blocked items and their blocking dependencies
        """
        blockers = []

        for item in self.items.values():
            # WHY: Skip items already completed or explicitly skipped
            if item.id in self.completed or item.id in self.skipped:
                continue

            # WHY: Find uncompleted dependencies that block this item
            blocking_deps = [
                dep_id
                for dep_id in item.depends_on
                if dep_id not in self.completed and dep_id not in self.skipped
            ]

            if blocking_deps:
                blockers.append(
                    {
                        "item_id": item.id,
                        "item_name": item.name,
                        "category": item.category,
                        "required": item.required,
                        "blocked_by": blocking_deps,
                        "blocked_by_names": [
                            self.items[dep_id].name
                            for dep_id in blocking_deps
                            if dep_id in self.items
                        ],
                    }
                )

        # WHY: Sort by required status and category for readable reports
        return sorted(blockers, key=lambda x: (not x["required"], x["category"]))

    def get_next_actions(self) -> List[Dict[str, Any]]:
        """
        Recommend next items that can be completed now (no blocking dependencies).

        WHY: Next actions list enables workflow automation and prevents decision
        paralysis by showing exactly what's actionable right now.

        Returns:
            List of dicts describing immediately actionable items
        """
        next_actions = []

        for item in self.items.values():
            # WHY: Skip completed, skipped, or explicitly blocked items
            if (
                item.id in self.completed
                or item.id in self.skipped
                or item.id in self.blocked
            ):
                continue

            # WHY: Check if all dependencies are satisfied
            all_deps_met = all(
                dep_id in self.completed or dep_id in self.skipped
                for dep_id in item.depends_on
            )

            if all_deps_met:
                next_actions.append(
                    {
                        "item_id": item.id,
                        "item_name": item.name,
                        "category": item.category,
                        "required": item.required,
                    }
                )

        # WHY: Prioritize required items and group by category for organized execution
        return sorted(next_actions, key=lambda x: (not x["required"], x["category"]))

    def export(self, filepath: Path, verbose: bool = False) -> None:
        """
        Export validation report to JSON file.

        WHY: JSON output enables integration with other tools, CI/CD pipelines,
        and dashboard visualizations. Structured format beats console-only output.

        Args:
            filepath: Path to output JSON file
            verbose: If True, include full item details in report
        """
        report = {
            "validation": {
                "passed": len(self.validation_errors) == 0,
                "errors": self.validation_errors,
            },
            "progress": self.get_progress(),
            "status": {
                "total_items": len(self.items),
                "required_items": sum(
                    1 for item in self.items.values() if item.required
                ),
                "completed": len(self.completed),
                "skipped": len(self.skipped),
                "blocked": len(self.blocked),
                "remaining": len(self.items) - len(self.completed) - len(self.skipped),
            },
            "blockers": self.get_blockers(),
            "next_actions": self.get_next_actions(),
        }

        # WHY: Verbose mode includes full checklist for self-contained reports
        if verbose:
            report["checklist"] = {
                item.id: {
                    "name": item.name,
                    "category": item.category,
                    "required": item.required,
                    "depends_on": item.depends_on,
                }
                for item in self.items.values()
            }

        # WHY: Use atomic write for safe file operations
        atomic_write_json(report, Path(filepath), indent=2)


def main() -> int:
    """
    CLI entry point for checklist validation.

    WHY: Standalone script execution enables integration with build systems,
    CI/CD pipelines, and manual workflow tracking without Python API knowledge.

    Returns:
        0 on success, 1 on validation failure, 2 on error
    """
    parser = argparse.ArgumentParser(
        description="Validate hierarchical checklist completion status",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic validation
  %(prog)s --checklist release.json --status current.json --output report.json

  # Verbose report with full item details
  %(prog)s --checklist release.json --status current.json --output report.json --verbose

  # Print next actions to console
  %(prog)s --checklist release.json --status current.json --output report.json && \\
    jq -r '.next_actions[] | "- \\(.item_name) (\\(.category))"' report.json
        """,
    )

    parser.add_argument(
        "--checklist",
        type=Path,
        required=True,
        help="Path to checklist definition JSON file",
    )
    parser.add_argument(
        "--status", type=Path, required=True, help="Path to current status JSON file"
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to output validation report JSON file",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Include full checklist details in output report",
    )

    args = parser.parse_args()

    try:
        validator = ChecklistValidator()

        # WHY: Load operations separated for clear error attribution
        print(f"Loading checklist: {args.checklist}", file=sys.stderr)
        validator.load_checklist(args.checklist)

        print(f"Loading status: {args.status}", file=sys.stderr)
        validator.load_status(args.status)

        print("Running validation...", file=sys.stderr)
        validation_passed = validator.validate()

        print(f"Exporting report: {args.output}", file=sys.stderr)
        validator.export(args.output, verbose=args.verbose)

        # WHY: Print summary to stderr to keep stdout clean for piping
        progress = validator.get_progress()
        print("\n[OK] Validation report generated", file=sys.stderr)
        print(f"  Overall progress: {progress['overall']:.1f}%", file=sys.stderr)
        print(f"  Blockers: {len(validator.get_blockers())}", file=sys.stderr)
        print(f"  Next actions: {len(validator.get_next_actions())}", file=sys.stderr)

        if not validation_passed:
            print("\n[ERROR] Validation errors found:", file=sys.stderr)
            for error in validator.validation_errors:
                print(f"  - {error}", file=sys.stderr)
            return 1  # WHY: Non-zero exit for CI/CD integration

        return 0

    except FileNotFoundError as e:
        print(f"✗ Error: File not found - {e}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"✗ Error: Invalid JSON - {e}", file=sys.stderr)
        return 2
    except KeyError as e:
        print(f"✗ Error: Missing required field - {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
