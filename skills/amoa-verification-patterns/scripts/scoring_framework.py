#!/usr/bin/env python3
"""
Universal Scoring Framework - Volume/Competition/Relevance Scoring

WHY: Provides a flexible, reusable scoring system adapted from ASO analytics.
Enables ranking and prioritization of any entities (keywords, features, risks, etc.)
based on weighted multi-dimensional metrics.

WHY stdlib only: Ensures portability and zero external dependencies for universal deployment.
WHY class-based: Encapsulates scoring logic for reusability across different scoring scenarios.
WHY normalization: Different metrics have different scales; normalization ensures fair comparison.
WHY weighted scoring: Different dimensions have different importance in different contexts.
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable, Optional
from pathlib import Path

# WHY: Import cross-platform utilities for consistency
# WHY: Dynamic path insertion is needed because shared module is in a sibling directory
SKILLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_DIR / "shared"))
from cross_platform import atomic_write_json  # type: ignore[import-not-found]  # noqa: E402


@dataclass
class ScoringMetric:
    """
    Defines a single scoring metric with normalization and weight.

    WHY dataclass: Clean, immutable structure for metric definitions.
    WHY normalize_fn: Each metric may need different normalization (linear, log, sigmoid, etc.).
    WHY weight: Allows flexible importance tuning across different use cases.
    """

    name: str
    weight: float
    normalize_fn: Callable[[float], float]
    description: str = ""

    def __post_init__(self) -> None:
        """WHY: Validate weight is between 0 and 1 to prevent scoring errors."""
        if not 0 <= self.weight <= 1:
            raise ValueError(
                f"Weight for {self.name} must be between 0 and 1, got {self.weight}"
            )


@dataclass
class ScoredEntity:
    """
    Represents an entity with its calculated score and ranking.

    WHY separate from input: Keeps input data immutable while adding computed fields.
    WHY rank: Enables quick identification of top/bottom performers.
    """

    name: str
    score: float
    rank: int
    metrics: Dict[str, Any]
    raw_metrics: Dict[str, Any] = field(default_factory=dict)
    normalized_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """WHY: Custom serialization to control output format."""
        return {
            "name": self.name,
            "score": round(self.score, 2),
            "rank": self.rank,
            "metrics": self.metrics,
            "raw_metrics": self.raw_metrics,
            "normalized_metrics": {
                k: round(v, 2) for k, v in self.normalized_metrics.items()
            },
        }


class ScoringFramework:
    """
    Universal scoring framework for ranking entities based on weighted multi-dimensional metrics.

    WHY: Provides a reusable, configurable system for scoring any type of entity
    across different domains (ASO keywords, features, risks, quality metrics, etc.).

    Example use cases:
    - Keyword ranking (volume, competition, relevance)
    - Feature prioritization (impact, effort, risk)
    - Risk scoring (probability, severity, exposure)
    - Quality assessment (coverage, accuracy, completeness)
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize the scoring framework.

        WHY verbose: Enables debugging and transparency in scoring calculations.
        """
        self.entities: List[Dict[str, Any]] = []
        self.metrics: List[ScoringMetric] = []
        self.scored_entities: List[ScoredEntity] = []
        self.verbose = verbose

    def load_entities(self, filepath: str) -> None:
        """
        Load entities to score from JSON file.

        WHY: Separates data loading from scoring logic for better testability.
        WHY validation: Ensures input data has required structure before processing.

        Expected format:
        [
            {"name": "entity1", "metrics": {"volume": 100, "quality": 0.8}},
            {"name": "entity2", "metrics": {"volume": 50, "quality": 0.9}}
        ]
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {filepath}")

        with open(path, "r", encoding="utf-8") as f:
            self.entities = json.load(f)

        # WHY validation: Fail fast if input format is incorrect
        for entity in self.entities:
            if "name" not in entity:
                raise ValueError(f"Entity missing 'name' field: {entity}")
            if "metrics" not in entity or not isinstance(entity["metrics"], dict):
                raise ValueError(f"Entity missing or invalid 'metrics' field: {entity}")

        if self.verbose:
            print(
                f"✓ Loaded {len(self.entities)} entities from {filepath}",
                file=sys.stderr,
            )

    def define_metric(
        self,
        name: str,
        weight: float,
        normalize_fn: Optional[Callable[[float], float]] = None,
        description: str = "",
    ) -> None:
        """
        Define a scoring metric with weight and normalization function.

        WHY: Allows flexible metric definition for different scoring scenarios.
        WHY default normalization: Provides sensible default (linear 0-100) if not specified.

        Args:
            name: Metric name (must match key in entity metrics)
            weight: Importance weight (0-1, will be normalized if sum != 1)
            normalize_fn: Function to normalize raw value to 0-100 scale
            description: Human-readable description of what this metric measures
        """
        if normalize_fn is None:
            # WHY default: Linear normalization assumes values are already in reasonable range
            def default_normalize(x: float) -> float:
                return min(100.0, max(0.0, x))

            normalize_fn = default_normalize

        metric = ScoringMetric(
            name=name, weight=weight, normalize_fn=normalize_fn, description=description
        )
        self.metrics.append(metric)

        if self.verbose:
            print(
                f"✓ Defined metric: {name} (weight={weight}, {description})",
                file=sys.stderr,
            )

    def load_weights(self, filepath: str) -> None:
        """
        Load metric definitions from JSON file.

        WHY: Enables configuration-driven scoring without code changes.

        Expected format:
        {
            "metrics": [
                {
                    "name": "volume",
                    "weight": 0.4,
                    "description": "Search volume",
                    "normalization": "linear"
                }
            ]
        }
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Weights file not found: {filepath}")

        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)

        if "metrics" not in config:
            raise ValueError("Weights file must contain 'metrics' array")

        for metric_config in config["metrics"]:
            name = metric_config.get("name")
            weight = metric_config.get("weight")
            description = metric_config.get("description", "")
            norm_type = metric_config.get("normalization", "linear")

            # WHY different normalizations: Different metrics have different distributions
            # WHY wrapper functions: Static methods have extra params with defaults,
            # but ScoringMetric expects Callable[[float], float]
            normalize_fn: Callable[[float], float]
            if norm_type == "linear":

                def linear_wrapper(x: float) -> float:
                    return self._linear_normalization(x)

                normalize_fn = linear_wrapper
            elif norm_type == "log":

                def log_wrapper(x: float) -> float:
                    return self._log_normalization(x)

                normalize_fn = log_wrapper
            elif norm_type == "sigmoid":

                def sigmoid_wrapper(x: float) -> float:
                    return self._sigmoid_normalization(x)

                normalize_fn = sigmoid_wrapper
            elif norm_type == "inverse":

                def inverse_wrapper(x: float) -> float:
                    return self._inverse_normalization(x)

                normalize_fn = inverse_wrapper
            else:

                def default_wrapper(x: float) -> float:
                    return self._linear_normalization(x)

                normalize_fn = default_wrapper

            self.define_metric(name, weight, normalize_fn, description)

        if self.verbose:
            print(
                f"✓ Loaded {len(config['metrics'])} metric definitions from {filepath}",
                file=sys.stderr,
            )

    @staticmethod
    def _linear_normalization(
        value: float, min_val: float = 0, max_val: float = 100
    ) -> float:
        """
        Linear normalization to 0-100 scale.

        WHY: Simplest normalization for metrics already in reasonable range.
        """
        if max_val == min_val:
            return 50.0  # WHY: Avoid division by zero
        normalized = ((value - min_val) / (max_val - min_val)) * 100
        return max(0, min(100, normalized))

    @staticmethod
    def _log_normalization(value: float, base: float = 10) -> float:
        """
        Logarithmic normalization for metrics with exponential growth.

        WHY: Search volume, traffic, and similar metrics often follow power laws.
        Log normalization prevents a few huge values from dominating the score.
        """
        import math

        if value <= 0:
            return 0
        # WHY log10: Maps orders of magnitude to linear scale
        normalized = (math.log10(value + 1) / math.log10(base)) * 100
        return min(100, normalized)

    @staticmethod
    def _sigmoid_normalization(
        value: float, midpoint: float = 50, steepness: float = 0.1
    ) -> float:
        """
        Sigmoid normalization for metrics with diminishing returns.

        WHY: Some metrics have optimal ranges - too low or too high is bad.
        Sigmoid creates an S-curve that rewards middle-range values.
        """
        import math

        # WHY sigmoid: Creates smooth transition between 0 and 100
        normalized = 100 / (1 + math.exp(-steepness * (value - midpoint)))
        return normalized

    @staticmethod
    def _inverse_normalization(value: float, max_val: float = 100) -> float:
        """
        Inverse normalization for metrics where lower is better.

        WHY: Competition, difficulty, cost - lower values should score higher.
        """
        if value <= 0:
            return 100
        normalized = max(0, 100 - (value / max_val) * 100)
        return normalized

    def _normalize_weights(self) -> None:
        """
        Normalize weights to sum to 1.0.

        WHY: Ensures weights are proportional even if user didn't normalize them.
        WHY in-place: Avoids creating new metric objects.
        """
        total_weight = sum(m.weight for m in self.metrics)
        if total_weight == 0:
            raise ValueError("Total weight cannot be zero")

        if abs(total_weight - 1.0) > 0.001:  # WHY tolerance: Floating point comparison
            for metric in self.metrics:
                metric.weight = metric.weight / total_weight

            if self.verbose:
                print(
                    f"✓ Normalized weights (sum was {total_weight:.3f})",
                    file=sys.stderr,
                )

    def score_entity(self, entity: Dict[str, Any]) -> ScoredEntity:
        """
        Calculate weighted score for a single entity.

        WHY: Separates single-entity scoring from batch processing for flexibility.
        WHY stores both raw and normalized: Enables debugging and transparency.

        Returns:
            ScoredEntity with calculated score and metric details
        """
        if not self.metrics:
            raise ValueError(
                "No metrics defined. Call define_metric() or load_weights() first."
            )

        name = entity["name"]
        raw_metrics = entity["metrics"]
        normalized_metrics = {}
        weighted_scores = {}

        # WHY separate loops: Clear separation of normalization and weighting
        for metric in self.metrics:
            if metric.name not in raw_metrics:
                if self.verbose:
                    print(
                        f"⚠ Entity '{name}' missing metric '{metric.name}', using 0",
                        file=sys.stderr,
                    )
                raw_value = 0
            else:
                raw_value = raw_metrics[metric.name]

            # WHY normalization: Brings all metrics to same scale (0-100)
            normalized_value = metric.normalize_fn(raw_value)
            normalized_metrics[metric.name] = normalized_value

            # WHY weighted: Applies importance to each metric
            weighted_scores[metric.name] = normalized_value * metric.weight

        # WHY sum: Composite score is weighted average of all metrics
        total_score = sum(weighted_scores.values()) * 100  # WHY * 100: Scale to 0-100

        return ScoredEntity(
            name=name,
            score=total_score,
            rank=0,  # WHY 0: Will be assigned in rank_all()
            metrics=raw_metrics,
            raw_metrics=raw_metrics,
            normalized_metrics=normalized_metrics,
        )

    def rank_all(self) -> List[ScoredEntity]:
        """
        Score and rank all loaded entities.

        WHY: Batch processing with ranking assignment.
        WHY descending: Higher scores should have lower rank numbers (1 = best).

        Returns:
            List of ScoredEntity sorted by score (highest first)
        """
        if not self.entities:
            raise ValueError("No entities loaded. Call load_entities() first.")

        # WHY normalize first: Ensures weights are correct before scoring
        self._normalize_weights()

        # WHY list comprehension: Efficient batch processing
        self.scored_entities = [self.score_entity(entity) for entity in self.entities]

        # WHY sort descending: Best scores first
        self.scored_entities.sort(key=lambda x: x.score, reverse=True)

        # WHY enumerate: Assign ranks based on sorted position
        for rank, entity in enumerate(self.scored_entities, start=1):
            entity.rank = rank

        if self.verbose:
            print(
                f"✓ Scored and ranked {len(self.scored_entities)} entities",
                file=sys.stderr,
            )
            print(
                f"  Top score: {self.scored_entities[0].score:.2f} ({self.scored_entities[0].name})",
                file=sys.stderr,
            )
            print(
                f"  Bottom score: {self.scored_entities[-1].score:.2f} ({self.scored_entities[-1].name})",
                file=sys.stderr,
            )

        return self.scored_entities

    def get_top(self, n: int) -> List[ScoredEntity]:
        """
        Get top N entities by score.

        WHY: Common use case - identifying best performers.
        WHY slice: Efficient for already-sorted list.

        Args:
            n: Number of top entities to return

        Returns:
            List of top N ScoredEntity objects
        """
        if not self.scored_entities:
            raise ValueError("No scored entities. Call rank_all() first.")

        return self.scored_entities[:n]

    def get_bottom(self, n: int) -> List[ScoredEntity]:
        """
        Get bottom N entities by score.

        WHY: Useful for identifying worst performers or deprioritization.
        """
        if not self.scored_entities:
            raise ValueError("No scored entities. Call rank_all() first.")

        return self.scored_entities[-n:]

    def get_by_rank(self, rank: int) -> Optional[ScoredEntity]:
        """
        Get entity by rank number.

        WHY: Direct access to specific rank position.
        """
        if not self.scored_entities:
            raise ValueError("No scored entities. Call rank_all() first.")

        if 1 <= rank <= len(self.scored_entities):
            return self.scored_entities[rank - 1]
        return None

    def export(self, filepath: str, include_details: bool = True) -> None:
        """
        Export scored and ranked entities to JSON file.

        WHY: Persists results for downstream processing or reporting.
        WHY include_details: Allows compact output when only scores/ranks needed.

        Args:
            filepath: Output file path
            include_details: If True, includes raw and normalized metrics
        """
        if not self.scored_entities:
            raise ValueError("No scored entities. Call rank_all() first.")

        output_data = []
        for entity in self.scored_entities:
            entity_dict = entity.to_dict()
            if not include_details:
                # WHY compact: Remove detailed metrics for smaller output
                entity_dict = {
                    "name": entity_dict["name"],
                    "score": entity_dict["score"],
                    "rank": entity_dict["rank"],
                }
            output_data.append(entity_dict)

        # WHY: Use atomic write for safe file operations
        atomic_write_json(output_data, Path(filepath), indent=2)

        if self.verbose:
            print(
                f"✓ Exported {len(output_data)} scored entities to {filepath}",
                file=sys.stderr,
            )

    def print_summary(self, top_n: int = 10) -> None:
        """
        Print human-readable summary of scoring results.

        WHY: Quick inspection of results without opening JSON files.
        """
        if not self.scored_entities:
            print(
                "No scored entities available. Call rank_all() first.", file=sys.stderr
            )
            return

        print("\n" + "=" * 80)
        print(f"SCORING SUMMARY - Top {top_n} Entities")
        print("=" * 80)
        print(f"{'Rank':<6} {'Score':<8} {'Entity Name':<40}")
        print("-" * 80)

        for entity in self.get_top(top_n):
            print(f"{entity.rank:<6} {entity.score:<8.2f} {entity.name:<40}")

        print("=" * 80)
        print(f"Total entities scored: {len(self.scored_entities)}")
        print()


def main() -> None:
    """
    CLI entry point for universal scoring framework.

    WHY: Provides command-line interface for standalone usage and scripting.
    """
    parser = argparse.ArgumentParser(
        description="Universal Scoring Framework - Rank entities using weighted multi-dimensional metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  # Score entities with predefined weights
  %(prog)s --input entities.json --weights weights.json --output scored.json

  # Verbose mode for debugging
  %(prog)s --input entities.json --weights weights.json --output scored.json --verbose

  # Show top 20 instead of default 10
  %(prog)s --input entities.json --weights weights.json --output scored.json --top 20

Use cases:
  - Keyword ranking (volume, competition, relevance)
  - Feature prioritization (impact, effort, risk)
  - Risk scoring (probability, severity, exposure)
  - Quality assessment (coverage, accuracy, completeness)
        """,
    )

    parser.add_argument(
        "--input", required=True, help="Input JSON file with entities to score"
    )

    parser.add_argument(
        "--weights", required=True, help="JSON file with metric definitions and weights"
    )

    parser.add_argument(
        "--output", required=True, help="Output JSON file for scored results"
    )

    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose output for debugging"
    )

    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of top entities to display in summary (default: 10)",
    )

    parser.add_argument(
        "--compact",
        action="store_true",
        help="Export compact output (scores/ranks only, no detailed metrics)",
    )

    args = parser.parse_args()

    try:
        # WHY: Clear workflow - load, configure, score, export
        framework = ScoringFramework(verbose=args.verbose)
        framework.load_entities(args.input)
        framework.load_weights(args.weights)
        framework.rank_all()
        framework.export(args.output, include_details=not args.compact)
        framework.print_summary(top_n=args.top)

        if args.verbose:
            print(
                f"\n✓ SUCCESS: Scored entities exported to {args.output}",
                file=sys.stderr,
            )

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
