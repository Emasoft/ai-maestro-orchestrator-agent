#!/usr/bin/env python3
"""Test Quality Analyzer - Detect low-quality tests.

PURPOSE: Identifies tests that only verify build/exit codes without checking
actual behavior. Flags skeleton tests and stub implementations.

USAGE:
  python test_quality_analyzer.py <test_file_or_directory>
  python test_quality_analyzer.py --min-score 70 tests/

EXITS:
  0 = All tests meet quality threshold
  1 = Some tests below quality threshold
  2 = Error in analysis

QUALITY METRICS:
- Has behavioral assertions (not just exit code checks)
- Verifies output content (not just success status)
- No TODO/FIXME/stub markers
- No ignored/skipped tests
- Tests actual functionality (not just compilation)
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ==============================================================================
# LOW-QUALITY PATTERNS (indicate build-only or skeleton tests)
# ==============================================================================

LOW_QUALITY_PATTERNS_RUST = [
    (
        r"assert!\s*\(\s*.*\.success\(\s*\)\s*\)",
        "Build-only assertion (checks exit code only)",
    ),
    (r"assert!\s*\(\s*output\.status\.success", "Exit code only check"),
    (r"#\[ignore\]", "Ignored test"),
    (r"//\s*TODO", "Incomplete test (TODO marker)"),
    (r"//\s*FIXME", "Incomplete test (FIXME marker)"),
    (r"unimplemented!\(\)", "Unimplemented stub"),
    (r"todo!\(\)", "Todo stub"),
    (r"panic!\s*\(\s*\"not implemented", "Not implemented stub"),
]

LOW_QUALITY_PATTERNS_PYTHON = [
    (r"assert\s+.*\.returncode\s*==\s*0", "Exit code only check"),
    (r"@pytest\.mark\.skip", "Skipped test"),
    (r"@unittest\.skip", "Skipped test"),
    (r"#\s*TODO", "Incomplete test (TODO marker)"),
    (r"#\s*FIXME", "Incomplete test (FIXME marker)"),
    (r"pass\s*$", "Empty test body (pass only)"),
    (r"raise\s+NotImplementedError", "Not implemented stub"),
    (r"\.\.\.(?:\s*#.*)?$", "Ellipsis stub"),
]

LOW_QUALITY_PATTERNS_JS = [
    (r"expect\s*\(\s*true\s*\)\s*\.toBe\s*\(\s*true\s*\)", "Trivial assertion"),
    (r"\.skip\s*\(", "Skipped test"),
    (r"//\s*TODO", "Incomplete test (TODO marker)"),
    (r"//\s*FIXME", "Incomplete test (FIXME marker)"),
    (r"throw\s+new\s+Error\s*\(\s*['\"]not implemented", "Not implemented stub"),
    (r"pending\s*\(\s*\)", "Pending test marker"),
]

# ==============================================================================
# REQUIRED PATTERNS (indicate behavioral tests)
# ==============================================================================

REQUIRED_PATTERNS_RUST = [
    (r"assert_eq!\s*\(.*,.*\)", "Value comparison assertion"),
    (r"assert_ne!\s*\(.*,.*\)", "Value inequality assertion"),
    (r"assert!\s*\(.*\.contains\s*\(", "Content verification"),
    (r"\.expect\s*\(", "Result expectation"),
    (r"assert_matches!", "Pattern matching assertion"),
]

REQUIRED_PATTERNS_PYTHON = [
    (r"assert\s+.*==", "Value comparison assertion"),
    (r"assert\s+.*!=", "Value inequality assertion"),
    (r"assert\s+.*\s+in\s+", "Contains check"),
    (r"assertEqual", "Unittest equality check"),
    (r"assertIn", "Unittest contains check"),
    (r"pytest\.raises", "Exception assertion"),
]

REQUIRED_PATTERNS_JS = [
    (r"expect\s*\(.*\)\s*\.toBe\s*\(", "Value comparison"),
    (r"expect\s*\(.*\)\s*\.toEqual\s*\(", "Deep equality check"),
    (r"expect\s*\(.*\)\s*\.toContain\s*\(", "Contains check"),
    (r"expect\s*\(.*\)\s*\.toThrow", "Exception assertion"),
    (r"assert\.strictEqual", "Strict equality (Node assert)"),
]


# ==============================================================================
# DATA STRUCTURES
# ==============================================================================


@dataclass
class TestIssue:
    """A quality issue found in a test."""

    line_number: int
    issue_type: str
    description: str
    severity: str  # "low", "medium", "high"


@dataclass
class TestAnalysis:
    """Analysis result for a single test file."""

    file_path: str
    language: str
    test_count: int = 0
    low_quality_count: int = 0
    behavioral_count: int = 0
    issues: list[TestIssue] = field(default_factory=list)
    score: float = 0.0

    def calculate_score(self) -> float:
        """Calculate quality score (0-100)."""
        if self.test_count == 0:
            return 0.0

        # Base score from behavioral test ratio
        behavioral_ratio = (
            self.behavioral_count / self.test_count if self.test_count > 0 else 0
        )
        base_score = behavioral_ratio * 100

        # Penalty for low-quality patterns
        low_quality_penalty = (
            (self.low_quality_count / self.test_count) * 50
            if self.test_count > 0
            else 0
        )

        # Calculate final score
        self.score = max(0, min(100, base_score - low_quality_penalty))
        return self.score


# ==============================================================================
# ANALYZER
# ==============================================================================


def detect_language(file_path: Path) -> str:
    """Detect programming language from file extension."""
    suffix = file_path.suffix.lower()
    if suffix == ".rs":
        return "rust"
    elif suffix == ".py":
        return "python"
    elif suffix in (".js", ".ts", ".jsx", ".tsx"):
        return "javascript"
    else:
        return "unknown"


def get_patterns_for_language(
    language: str,
) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Get low-quality and required patterns for a language."""
    if language == "rust":
        return LOW_QUALITY_PATTERNS_RUST, REQUIRED_PATTERNS_RUST
    elif language == "python":
        return LOW_QUALITY_PATTERNS_PYTHON, REQUIRED_PATTERNS_PYTHON
    elif language == "javascript":
        return LOW_QUALITY_PATTERNS_JS, REQUIRED_PATTERNS_JS
    else:
        return [], []


def count_tests(content: str, language: str) -> int:
    """Count number of test functions in file."""
    if language == "rust":
        return len(re.findall(r"#\[test\]", content))
    elif language == "python":
        # Match def test_ or async def test_
        return len(re.findall(r"(?:async\s+)?def\s+test_", content))
    elif language == "javascript":
        # Match it(, test(, describe(
        return len(re.findall(r"\b(?:it|test)\s*\(", content))
    return 0


def analyze_test_file(file_path: Path) -> TestAnalysis:
    """Analyze a single test file for quality issues."""
    language = detect_language(file_path)
    analysis = TestAnalysis(file_path=str(file_path), language=language)

    if language == "unknown":
        return analysis

    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        analysis.issues.append(
            TestIssue(
                line_number=0,
                issue_type="read_error",
                description=str(e),
                severity="high",
            )
        )
        return analysis

    # Count tests
    analysis.test_count = count_tests(content, language)

    # Get patterns for language
    low_quality_patterns, required_patterns = get_patterns_for_language(language)

    # Check for low-quality patterns
    lines = content.split("\n")
    for line_num, line in enumerate(lines, 1):
        for pattern, description in low_quality_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                analysis.issues.append(
                    TestIssue(
                        line_number=line_num,
                        issue_type="low_quality",
                        description=description,
                        severity="medium",
                    )
                )
                analysis.low_quality_count += 1

    # Check for required behavioral patterns
    for pattern, description in required_patterns:
        if re.search(pattern, content, re.MULTILINE):
            analysis.behavioral_count += 1

    # Calculate score
    analysis.calculate_score()

    return analysis


def analyze_directory(directory: Path, recursive: bool = True) -> list[TestAnalysis]:
    """Analyze all test files in a directory."""
    results = []

    # Test file patterns
    test_patterns = [
        "**/test_*.py",
        "**/*_test.py",
        "**/tests/*.py",
        "**/test/*.rs",
        "**/*_test.rs",
        "**/*.test.js",
        "**/*.test.ts",
        "**/*.spec.js",
        "**/*.spec.ts",
    ]

    seen_files = set()
    for pattern in test_patterns:
        for file_path in directory.glob(pattern):
            if file_path.is_file() and file_path not in seen_files:
                seen_files.add(file_path)
                results.append(analyze_test_file(file_path))

    return results


def generate_report(
    analyses: list[TestAnalysis], min_score: int = 70
) -> dict[str, Any]:
    """Generate a summary report of all analyses."""
    total_tests = sum(a.test_count for a in analyses)
    total_low_quality = sum(a.low_quality_count for a in analyses)
    total_behavioral = sum(a.behavioral_count for a in analyses)

    passing = [a for a in analyses if a.score >= min_score]
    failing = [a for a in analyses if a.score < min_score and a.test_count > 0]

    avg_score = sum(a.score for a in analyses) / len(analyses) if analyses else 0

    return {
        "summary": {
            "total_files": len(analyses),
            "total_tests": total_tests,
            "total_low_quality_patterns": total_low_quality,
            "total_behavioral_patterns": total_behavioral,
            "average_score": round(avg_score, 1),
            "passing_files": len(passing),
            "failing_files": len(failing),
            "min_score_threshold": min_score,
        },
        "failing_files": [
            {
                "file": a.file_path,
                "score": round(a.score, 1),
                "tests": a.test_count,
                "issues": [
                    {
                        "line": i.line_number,
                        "type": i.issue_type,
                        "description": i.description,
                    }
                    for i in a.issues
                ],
            }
            for a in failing
        ],
        "all_files": [
            {
                "file": a.file_path,
                "score": round(a.score, 1),
                "tests": a.test_count,
                "language": a.language,
            }
            for a in analyses
        ],
    }


def print_report(report: dict[str, Any], verbose: bool = False) -> None:
    """Print human-readable report."""
    summary = report["summary"]

    print("\n" + "=" * 70)
    print("TEST QUALITY ANALYSIS REPORT")
    print("=" * 70)

    print(f"\nFiles analyzed:      {summary['total_files']}")
    print(f"Total tests:         {summary['total_tests']}")
    print(f"Behavioral patterns: {summary['total_behavioral_patterns']}")
    print(f"Low-quality issues:  {summary['total_low_quality_patterns']}")
    print(f"Average score:       {summary['average_score']}%")
    print(f"Threshold:           {summary['min_score_threshold']}%")
    print(f"Passing files:       {summary['passing_files']}")
    print(f"Failing files:       {summary['failing_files']}")

    if report["failing_files"]:
        print("\n" + "-" * 70)
        print("FAILING FILES (below threshold)")
        print("-" * 70)

        for file_info in report["failing_files"]:
            print(f"\n{file_info['file']}")
            print(f"  Score: {file_info['score']}% | Tests: {file_info['tests']}")
            if verbose and file_info["issues"]:
                for issue in file_info["issues"][:5]:  # Limit to 5 issues per file
                    print(f"  Line {issue['line']}: {issue['description']}")
                if len(file_info["issues"]) > 5:
                    print(f"  ... and {len(file_info['issues']) - 5} more issues")

    print("\n" + "=" * 70)

    if summary["failing_files"] > 0:
        print("RESULT: FAIL - Some test files below quality threshold")
    else:
        print("RESULT: PASS - All test files meet quality threshold")

    print("=" * 70 + "\n")


# ==============================================================================
# MAIN
# ==============================================================================


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze test quality and detect low-quality tests"
    )
    parser.add_argument(
        "path", nargs="?", default=".", help="Test file or directory to analyze"
    )
    parser.add_argument(
        "--min-score", type=int, default=70, help="Minimum quality score (0-100)"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output with issue details"
    )
    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        default=True,
        help="Search recursively (default: True)",
    )

    args = parser.parse_args()

    path = Path(args.path)

    if not path.exists():
        print(f"ERROR: Path does not exist: {path}", file=sys.stderr)
        return 2

    if path.is_file():
        analyses = [analyze_test_file(path)]
    else:
        analyses = analyze_directory(path, recursive=args.recursive)

    if not analyses:
        print("No test files found.", file=sys.stderr)
        return 0

    report = generate_report(analyses, min_score=args.min_score)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report, verbose=args.verbose)

    # Exit with failure if any files are below threshold
    if report["summary"]["failing_files"] > 0:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
