#!/usr/bin/env python3
"""
Universal Comparison Analyzer - Comparative Gap Analysis Tool

WHY: Enables systematic comparison of any entity against a baseline to identify gaps,
strengths, weaknesses, and generate improvement recommendations. Adapted from ASO
competitor analysis for universal use cases.

Use cases:
- Competitive analysis (comparing products/services)
- Feature comparison (comparing implementations)
- Quality benchmarking (comparing metrics)
- Performance analysis (comparing systems)
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# WHY: Import cross-platform utilities for consistency
SKILLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_DIR / "shared"))
from cross_platform import atomic_write_json  # type: ignore[import-not-found]  # noqa: E402


class ComparisonAnalyzer:
    """
    Universal comparison analyzer for gap analysis.

    WHY: Provides a standardized way to compare entities across multiple dimensions,
    calculate gaps, identify patterns, and generate actionable recommendations.
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize the comparison analyzer.

        WHY: Verbose mode allows detailed logging during analysis without cluttering
        default output.
        """
        self.verbose = verbose
        self.baseline: Optional[Dict[str, Any]] = (
            None  # WHY: Reference entity for comparisons
        )
        self.comparisons: List[Dict[str, Any]] = []  # WHY: Store all comparison results

    def _log(self, message: str) -> None:
        """
        Log message if verbose mode is enabled.

        WHY: Conditional logging prevents output pollution in automated pipelines
        while still providing debug information when needed.
        """
        if self.verbose:
            print(f"[ComparisonAnalyzer] {message}", file=sys.stderr)

    def _extract_metrics(self, entity: Dict[str, Any]) -> Dict[str, Union[int, float]]:
        """
        Extract numeric metrics from entity data.

        WHY: Comparisons require numeric values. This method normalizes entity data
        to extract comparable metrics, handling nested structures and mixed types.
        """
        metrics = {}

        def extract_recursive(data: Any, prefix: str = "") -> None:
            """
            WHY: Recursively traverse nested structures to find all numeric values,
            creating flat dot-notation keys for comparison.
            """
            if isinstance(data, dict):
                for key, value in data.items():
                    new_prefix = f"{prefix}.{key}" if prefix else key
                    extract_recursive(value, new_prefix)
            elif isinstance(data, (int, float)):
                metrics[prefix] = data
            elif isinstance(data, list):
                # WHY: Handle lists by extracting metrics from each item and aggregating
                for idx, item in enumerate(data):
                    extract_recursive(item, f"{prefix}[{idx}]")

        extract_recursive(entity)
        return metrics

    def set_baseline(self, entity: Dict[str, Any]) -> None:
        """
        Set the baseline entity for comparison.

        WHY: All gap calculations are relative to a baseline. This method establishes
        the reference point for all subsequent comparisons.

        Args:
            entity: Baseline entity data (must include 'name' or 'id' field)
        """
        # WHY: Validate baseline has identifier for tracking
        if "name" not in entity and "id" not in entity:
            raise ValueError("Baseline entity must have 'name' or 'id' field")

        self.baseline = entity
        self._log(f"Baseline set: {entity.get('name', entity.get('id'))}")

    def compare(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare an entity against the baseline.

        WHY: Single entity comparison is the core operation. This method calculates
        gaps, identifies strengths/weaknesses, and generates recommendations.

        Args:
            entity: Entity to compare against baseline

        Returns:
            Comparison result with gaps, strengths, weaknesses, and recommendations
        """
        # WHY: Fail fast if baseline not set
        if self.baseline is None:
            raise ValueError("Baseline must be set before comparison")

        # WHY: Validate entity has identifier
        if "name" not in entity and "id" not in entity:
            raise ValueError("Entity must have 'name' or 'id' field")

        # WHY: Extract entity and baseline names, asserting they are strings for type safety
        entity_name_raw = entity.get("name", entity.get("id"))
        baseline_name_raw = self.baseline.get("name", self.baseline.get("id"))

        # WHY: Type assertion - we validated above that name or id exists
        assert isinstance(entity_name_raw, str), "Entity name must be a string"
        assert isinstance(baseline_name_raw, str), "Baseline name must be a string"

        entity_name: str = entity_name_raw
        baseline_name: str = baseline_name_raw

        self._log(f"Comparing '{entity_name}' against baseline '{baseline_name}'")

        # WHY: Extract numeric metrics for quantitative comparison
        baseline_metrics = self._extract_metrics(self.baseline)
        entity_metrics = self._extract_metrics(entity)

        # WHY: Calculate gaps (positive = entity better, negative = baseline better)
        gaps: Dict[str, Union[int, float]] = {}
        for key in set(baseline_metrics.keys()) | set(entity_metrics.keys()):
            baseline_val = baseline_metrics.get(key, 0)
            entity_val = entity_metrics.get(key, 0)
            gap = entity_val - baseline_val
            gaps[key] = gap

        # WHY: Identify strengths (positive gaps) and weaknesses (negative gaps)
        strengths = {k: v for k, v in gaps.items() if v > 0}
        weaknesses = {k: v for k, v in gaps.items() if v < 0}

        # WHY: Generate recommendations based on largest gaps
        recommendations = self._generate_recommendations(weaknesses, entity_name)

        comparison_result: Dict[str, Any] = {
            "entity": entity_name,
            "baseline": baseline_name,
            "gaps": gaps,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "summary": {
                "total_metrics": len(gaps),
                "strengths_count": len(strengths),
                "weaknesses_count": len(weaknesses),
                "net_score": sum(gaps.values()),  # WHY: Aggregate performance indicator
            },
        }

        self.comparisons.append(comparison_result)
        return comparison_result

    def compare_all(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Compare multiple entities against the baseline.

        WHY: Batch comparison enables ranking and relative performance analysis
        across multiple competitors/alternatives.

        Args:
            entities: List of entities to compare

        Returns:
            List of comparison results, sorted by net_score (descending)
        """
        results = []
        for entity in entities:
            try:
                result = self.compare(entity)
                results.append(result)
            except Exception as e:
                # WHY: Fail fast on errors, no silent failures
                raise RuntimeError(
                    f"Failed to compare entity {entity.get('name', entity.get('id'))}: {e}"
                ) from e

        # WHY: Sort by net score to rank entities from best to worst
        results.sort(key=lambda x: x["summary"]["net_score"], reverse=True)
        return results

    def _generate_recommendations(
        self, weaknesses: Dict[str, float], entity_name: str
    ) -> List[str]:
        """
        Generate improvement recommendations based on weaknesses.

        WHY: Recommendations convert raw gap data into actionable insights,
        prioritized by magnitude of weakness.
        """
        if not weaknesses:
            return [f"{entity_name} has no weaknesses compared to baseline"]

        # WHY: Sort weaknesses by magnitude (most negative first) to prioritize
        sorted_weaknesses = sorted(weaknesses.items(), key=lambda x: x[1])

        recommendations = []
        for metric, gap in sorted_weaknesses[:5]:  # WHY: Limit to top 5 to focus effort
            recommendations.append(
                f"Improve '{metric}' by {abs(gap):.2f} to match baseline"
            )

        return recommendations

    def get_gaps(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all gaps across all comparisons.

        WHY: Aggregated gap view enables cross-entity pattern analysis and
        identification of common weaknesses/strengths.

        Returns:
            Dictionary mapping metric names to list of gaps across entities
        """
        # WHY: Aggregate gaps by metric for pattern analysis
        gaps_by_metric: Dict[str, List[Dict[str, Any]]] = {}

        for comparison in self.comparisons:
            entity = comparison["entity"]
            for metric, gap in comparison["gaps"].items():
                if metric not in gaps_by_metric:
                    gaps_by_metric[metric] = []
                gaps_by_metric[metric].append({"entity": entity, "gap": gap})

        return gaps_by_metric

    def get_recommendations(self) -> Dict[str, List[str]]:
        """
        Get all recommendations across all comparisons.

        WHY: Consolidated recommendations enable strategic planning and
        prioritization of improvements across all entities.

        Returns:
            Dictionary mapping entity names to their recommendations
        """
        return {
            comparison["entity"]: comparison["recommendations"]
            for comparison in self.comparisons
        }

    def export(self, filepath: Union[str, Path]) -> None:
        """
        Export analysis results to JSON file.

        WHY: Persistent storage enables sharing, archiving, and further processing
        of comparison results.

        Args:
            filepath: Output file path
        """
        filepath = Path(filepath)

        output_data = {
            "baseline": self.baseline.get("name", self.baseline.get("id"))
            if self.baseline
            else None,
            "comparisons": self.comparisons,
            "aggregated_gaps": self.get_gaps(),
            "aggregated_recommendations": self.get_recommendations(),
            "metadata": {
                "total_comparisons": len(self.comparisons),
                "total_entities": len(self.comparisons) + (1 if self.baseline else 0),
            },
        }

        # WHY: Use atomic write for safe file operations
        atomic_write_json(output_data, filepath, indent=2)

        self._log(f"Analysis exported to {filepath}")


def load_json(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    Load JSON data from file.

    WHY: Centralized JSON loading with error handling ensures consistent
    failure behavior across the tool.
    """
    filepath = Path(filepath)

    # WHY: Fail fast if file doesn't exist
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    with filepath.open("r") as f:
        data: Dict[str, Any] = json.load(f)
        return data


def main() -> int:
    """
    CLI entry point.

    WHY: Command-line interface enables integration with scripts, pipelines,
    and manual analysis workflows.
    """
    parser = argparse.ArgumentParser(
        description="Universal Comparison Analyzer - Comparative Gap Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare single competitor
  %(prog)s --baseline our_project.json --comparisons competitor.json --output gaps.json

  # Compare multiple competitors with verbose output
  %(prog)s --baseline our_app.json --comparisons all_competitors.json --output analysis.json --verbose

  # Feature comparison
  %(prog)s --baseline current_version.json --comparisons next_version.json --output feature_gaps.json
        """,
    )

    # WHY: Required args ensure minimum viable input for analysis
    parser.add_argument(
        "--baseline", required=True, help="Path to baseline entity JSON file"
    )
    parser.add_argument(
        "--comparisons",
        required=True,
        help="Path to JSON file with entities to compare (single dict or list of dicts)",
    )
    parser.add_argument(
        "--output", required=True, help="Path to output gap analysis JSON file"
    )

    # WHY: Optional verbose mode for debugging
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    try:
        # WHY: Load baseline entity
        baseline = load_json(args.baseline)

        # WHY: Load comparison entities (handle both single dict and list)
        comparisons_data = load_json(args.comparisons)
        if isinstance(comparisons_data, dict):
            comparisons = [comparisons_data]  # WHY: Normalize to list
        elif isinstance(comparisons_data, list):
            comparisons = comparisons_data
        else:
            raise ValueError("Comparisons file must contain a dict or list of dicts")

        # WHY: Create analyzer and run comparison
        analyzer = ComparisonAnalyzer(verbose=args.verbose)
        analyzer.set_baseline(baseline)
        analyzer.compare_all(comparisons)

        # WHY: Export results
        analyzer.export(args.output)

        if not args.verbose:
            # WHY: Minimal output for orchestrator integration
            print(f"DONE comparison_analyzer.py - {len(comparisons)} entities analyzed")

        return 0

    except Exception as e:
        # WHY: Fail fast with clear error message
        print(f"FAILED comparison_analyzer.py - {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
