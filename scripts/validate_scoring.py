#!/usr/bin/env python3
"""
Claude Plugins Validation - Quality Scoring Module

Aggregates validation results from all validators and computes quality scores.
Provides category scores (0-10 scale) and overall quality score (0-100).

Usage:
    uv run python scripts/validate_scoring.py /path/to/plugin
    uv run python scripts/validate_scoring.py /path/to/plugin --verbose
    uv run python scripts/validate_scoring.py /path/to/plugin --json

Exit codes (standard severity-based convention):
    0 - PASS: No issues found
    1 - CRITICAL: Critical issues found
    2 - MAJOR: Major issues found (no critical)
    3 - MINOR: Minor issues only
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Import shared validation infrastructure
from cpv_validation_common import (
    COLORS,
    ValidationReport,
    ValidationResult,
    calculate_letter_grade,
)

# Import all validators
from validate_agent import validate_agent
from validate_command import validate_command
from validate_hook import validate_hooks
from validate_mcp import validate_plugin_mcp
from validate_plugin import (
    validate_agents as plugin_validate_agents,
)
from validate_plugin import (
    validate_commands as plugin_validate_commands,
)
from validate_plugin import (
    validate_hooks as plugin_validate_hooks,
)
from validate_plugin import (
    validate_license,
    validate_manifest,
    validate_readme,
    validate_scripts,
    validate_structure,
)
from validate_plugin import (
    validate_mcp as plugin_validate_mcp,
)
from validate_plugin import (
    validate_skills as plugin_validate_skills,
)
from validate_security import validate_security
from validate_skill import validate_skill

# =============================================================================
# Scoring Constants
# =============================================================================

# Category minimum thresholds (0-10 scale)
CATEGORY_THRESHOLDS = {
    "schema_compliance": 8,  # Minimum 8/10 - Required for proper functioning
    "security": 8,  # Minimum 8/10 - CRITICAL security requirements
    "matcher_validity": 7,  # Minimum 7/10 - Hook matchers must work
    "script_existence": 7,  # Minimum 7/10 - Scripts must exist and be executable
    "hook_types": 9,  # Minimum 9/10 - Hook types must be valid
    "documentation": 5,  # Minimum 5/10 - Documentation is helpful but not critical
    "maintainability": 6,  # Minimum 6/10 - Code should be maintainable
}

# Category weights for overall score calculation
CATEGORY_WEIGHTS = {
    "schema_compliance": 0.20,  # 20% of overall score
    "security": 0.25,  # 25% - security is most important
    "matcher_validity": 0.15,  # 15%
    "script_existence": 0.15,  # 15%
    "hook_types": 0.10,  # 10%
    "documentation": 0.08,  # 8%
    "maintainability": 0.07,  # 7%
}

# Rating descriptors
RATING_DESCRIPTIONS = {
    "9-10": "Excellent - Ready for production",
    "7-8": "Good - Minor improvements recommended",
    "5-6": "Fair - Significant improvements needed",
    "0-4": "Poor - Major revision required",
}

# Exit codes - standard severity-based convention
EXIT_PASS = 0  # No issues found
EXIT_CRITICAL = 1  # Critical issues found
EXIT_MAJOR = 2  # Major issues found (no critical)
EXIT_MINOR = 3  # Minor issues only


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class CategoryScore:
    """Score for a single validation category.

    Attributes:
        name: Category name (e.g., "schema_compliance", "security")
        score: Numeric score (0-10 scale)
        threshold: Minimum required score
        passed: Whether the category meets its threshold
        issues_critical: Count of critical issues in this category
        issues_major: Count of major issues in this category
        issues_minor: Count of minor issues in this category
        issues_passed: Count of passed checks in this category
        rating: Rating descriptor ("Excellent", "Good", "Fair", "Poor")
        recommendations: List of improvement recommendations
    """

    name: str
    score: float
    threshold: int
    passed: bool
    issues_critical: int = 0
    issues_major: int = 0
    issues_minor: int = 0
    issues_passed: int = 0
    rating: str = ""
    recommendations: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Calculate rating based on score."""
        if self.score >= 9:
            self.rating = "Excellent"
        elif self.score >= 7:
            self.rating = "Good"
        elif self.score >= 5:
            self.rating = "Fair"
        else:
            self.rating = "Poor"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "score": round(self.score, 2),
            "threshold": self.threshold,
            "passed": self.passed,
            "rating": self.rating,
            "issues": {
                "critical": self.issues_critical,
                "major": self.issues_major,
                "minor": self.issues_minor,
                "passed": self.issues_passed,
            },
            "recommendations": self.recommendations,
        }


@dataclass
class QualityScoreReport:
    """Complete quality score report with category breakdown.

    Attributes:
        plugin_path: Path to the validated plugin
        overall_score: Overall quality score (0-100)
        letter_grade: Letter grade (A+, A, B, etc.)
        status: Overall status (PASS, CONDITIONAL_PASS, FAIL)
        category_scores: Individual category scores
        critical_failures: List of critical failures that cause automatic fail
        recommendations: Prioritized list of improvement recommendations
        validator_reports: Raw reports from each validator
    """

    plugin_path: str
    overall_score: float = 0.0
    letter_grade: str = "F"
    status: str = "FAIL"
    category_scores: dict[str, CategoryScore] = field(default_factory=dict)
    critical_failures: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    validator_reports: dict[str, ValidationReport] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "plugin_path": self.plugin_path,
            "overall_score": round(self.overall_score, 2),
            "letter_grade": self.letter_grade,
            "status": self.status,
            "category_scores": {name: cat.to_dict() for name, cat in self.category_scores.items()},
            "critical_failures": self.critical_failures,
            "recommendations": self.recommendations,
            "validator_summaries": {
                name: {
                    "score": report.score,
                    "critical": report.count_by_level().get("CRITICAL", 0),
                    "major": report.count_by_level().get("MAJOR", 0),
                    "minor": report.count_by_level().get("MINOR", 0),
                }
                for name, report in self.validator_reports.items()
            },
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


# =============================================================================
# Category Scoring Functions
# =============================================================================


def calculate_category_score(
    results: list[ValidationResult],
    max_score: float = 10.0,
) -> tuple[float, int, int, int, int]:
    """Calculate score for a category based on its validation results.

    Scoring formula:
    - Start at max_score (10)
    - Deduct 3 points for each CRITICAL issue
    - Deduct 1.5 points for each MAJOR issue
    - Deduct 0.5 points for each MINOR issue
    - Minimum score is 0

    Args:
        results: List of validation results for this category
        max_score: Maximum possible score (default 10)

    Returns:
        Tuple of (score, critical_count, major_count, minor_count, passed_count)
    """
    score = max_score
    critical_count = 0
    major_count = 0
    minor_count = 0
    passed_count = 0

    for result in results:
        if result.level == "CRITICAL":
            score -= 3.0
            critical_count += 1
        elif result.level == "MAJOR":
            score -= 1.5
            major_count += 1
        elif result.level == "MINOR":
            score -= 0.5
            minor_count += 1
        elif result.level == "PASSED":
            passed_count += 1

    return max(0.0, score), critical_count, major_count, minor_count, passed_count


def categorize_results(
    reports: dict[str, ValidationReport],
) -> dict[str, list[ValidationResult]]:
    """Categorize validation results into scoring categories.

    Maps validator results to scoring categories based on the nature of each check.

    Args:
        reports: Dictionary of validator name -> ValidationReport

    Returns:
        Dictionary of category name -> list of ValidationResults
    """
    categories: dict[str, list[ValidationResult]] = {
        "schema_compliance": [],
        "security": [],
        "matcher_validity": [],
        "script_existence": [],
        "hook_types": [],
        "documentation": [],
        "maintainability": [],
    }

    # Helper to categorize based on message content
    def categorize_result(result: ValidationResult, validator_name: str) -> None:
        msg_lower = result.message.lower()

        # Security category - from security validator or security-related messages
        if validator_name == "security" or any(
            keyword in msg_lower
            for keyword in ["security", "secret", "credential", "injection", "traversal", "dangerous", "unsafe"]
        ):
            categories["security"].append(result)

        # Schema compliance - manifest, JSON, required fields
        elif any(
            keyword in msg_lower
            for keyword in ["json", "manifest", "plugin.json", "required field", "schema", "kebab-case", "name must"]
        ):
            categories["schema_compliance"].append(result)

        # Matcher validity - hook matchers
        elif any(keyword in msg_lower for keyword in ["matcher", "regex", "pattern invalid", "tool name", "wildcard"]):
            categories["matcher_validity"].append(result)

        # Script existence - scripts, executables
        elif any(
            keyword in msg_lower
            for keyword in ["script", "executable", "shebang", "chmod", "file not found", "command not found"]
        ):
            categories["script_existence"].append(result)

        # Hook types - hook configuration
        elif any(
            keyword in msg_lower
            for keyword in ["hook type", "event type", "pretooluse", "posttooluse", "stop", "sessionstart"]
        ):
            categories["hook_types"].append(result)

        # Documentation - README, descriptions, comments
        elif any(keyword in msg_lower for keyword in ["readme", "description", "documentation", "missing docstring"]):
            categories["documentation"].append(result)

        # Maintainability - code quality, structure
        elif any(
            keyword in msg_lower
            for keyword in ["version", "structure", "duplicate", "unused", "deprecated", "lint", "format"]
        ):
            categories["maintainability"].append(result)

        # Default to schema_compliance if no specific category matches
        else:
            categories["schema_compliance"].append(result)

    # Process all results from all validators
    for validator_name, report in reports.items():
        for result in report.results:
            categorize_result(result, validator_name)

    return categories


def generate_recommendations(category_scores: dict[str, CategoryScore]) -> list[str]:
    """Generate prioritized recommendations based on category scores.

    Recommendations are ordered by:
    1. Critical failures (must fix)
    2. Categories below threshold
    3. Categories with room for improvement

    Args:
        category_scores: Dictionary of category name -> CategoryScore

    Returns:
        List of recommendation strings, ordered by priority
    """
    recommendations: list[str] = []

    # Priority 1: Categories with critical issues
    for name, cat in category_scores.items():
        if cat.issues_critical > 0:
            recommendations.append(
                f"[CRITICAL] {name.replace('_', ' ').title()}: Fix {cat.issues_critical} critical issue(s) immediately"
            )

    # Priority 2: Categories below threshold
    for name, cat in category_scores.items():
        if not cat.passed and cat.issues_critical == 0:
            gap = cat.threshold - cat.score
            recommendations.append(
                f"[REQUIRED] {name.replace('_', ' ').title()}: "
                f"Score {cat.score:.1f}/10 is below minimum {cat.threshold}/10 "
                f"(need +{gap:.1f} points)"
            )

    # Priority 3: Categories with major issues
    for name, cat in category_scores.items():
        if cat.issues_major > 0 and cat.passed:
            recommendations.append(
                f"[RECOMMENDED] {name.replace('_', ' ').title()}: "
                f"Address {cat.issues_major} major issue(s) to improve quality"
            )

    # Priority 4: Categories with minor issues
    for name, cat in category_scores.items():
        if cat.issues_minor > 0 and cat.passed and cat.issues_major == 0:
            recommendations.append(
                f"[OPTIONAL] {name.replace('_', ' ').title()}: Consider fixing {cat.issues_minor} minor issue(s)"
            )

    return recommendations


# =============================================================================
# Main Scoring Function
# =============================================================================


def run_all_validators(plugin_path: Path) -> dict[str, ValidationReport]:
    """Run all validators and collect their reports.

    Args:
        plugin_path: Path to the plugin directory

    Returns:
        Dictionary of validator name -> ValidationReport
    """
    reports: dict[str, ValidationReport] = {}

    # Run plugin validator (main manifest and structure)
    # Uses multiple functions from validate_plugin.py
    # Note: validate_plugin uses its own ValidationReport class with compatible interface
    try:
        plugin_report = ValidationReport()
        _ = validate_manifest(plugin_path, plugin_report)
        validate_structure(plugin_path, plugin_report)
        plugin_validate_commands(plugin_path, plugin_report)
        plugin_validate_agents(plugin_path, plugin_report)
        plugin_validate_hooks(plugin_path, plugin_report)
        plugin_validate_mcp(plugin_path, plugin_report)
        validate_scripts(plugin_path, plugin_report)
        plugin_validate_skills(plugin_path, plugin_report)
        validate_readme(plugin_path, plugin_report)
        validate_license(plugin_path, plugin_report)
        reports["plugin"] = plugin_report
    except Exception as e:
        error_report = ValidationReport()
        error_report.critical(f"Plugin validation failed: {e}")
        reports["plugin"] = error_report

    # Run security validator (comprehensive security scan)
    try:
        security_report = validate_security(plugin_path)
        reports["security"] = security_report
    except Exception as e:
        error_report = ValidationReport()
        error_report.critical(f"Security validation failed: {e}")
        reports["security"] = error_report

    # Run hook validator if hooks.json exists (detailed hook validation)
    # Note: validate_hooks returns its own ValidationReport with compatible interface
    hooks_path = plugin_path / "hooks" / "hooks.json"
    if hooks_path.exists():
        try:
            hook_report = validate_hooks(hooks_path, plugin_path)
            reports["hooks"] = hook_report
        except Exception as e:
            error_report = ValidationReport()
            error_report.critical(f"Hook validation failed: {e}")
            reports["hooks"] = error_report

    # Run MCP validator if .mcp.json exists
    # Note: validate_plugin_mcp returns its own ValidationReport with compatible interface
    mcp_path = plugin_path / ".mcp.json"
    if mcp_path.exists():
        try:
            mcp_report = validate_plugin_mcp(plugin_path)
            reports["mcp"] = mcp_report
        except Exception as e:
            error_report = ValidationReport()
            error_report.critical(f"MCP validation failed: {e}")
            reports["mcp"] = error_report

    # Run detailed agent validator for each agent file
    agents_dir = plugin_path / "agents"
    if agents_dir.exists():
        agent_report = ValidationReport()
        for agent_file in agents_dir.glob("*.md"):
            try:
                agent_single_report = validate_agent(agent_file)
                agent_report.merge(agent_single_report)
            except Exception as e:
                agent_report.critical(f"Agent validation failed for {agent_file.name}: {e}")
        reports["agents"] = agent_report

    # Run detailed skill validator for each skill directory
    # Note: validate_skill returns its own ValidationReport with compatible interface
    skills_dir = plugin_path / "skills"
    if skills_dir.exists():
        skill_report = ValidationReport()
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith("."):
                try:
                    skill_single_report = validate_skill(skill_dir)
                    skill_report.merge(skill_single_report)
                except Exception as e:
                    skill_report.critical(f"Skill validation failed for {skill_dir.name}: {e}")
        reports["skills"] = skill_report

    # Run detailed command validator for each command file
    commands_dir = plugin_path / "commands"
    if commands_dir.exists():
        command_report = ValidationReport()
        for cmd_file in commands_dir.glob("*.md"):
            try:
                cmd_single_report = validate_command(cmd_file)
                command_report.merge(cmd_single_report)
            except Exception as e:
                command_report.critical(f"Command validation failed for {cmd_file.name}: {e}")
        reports["commands"] = command_report

    return reports


def compute_quality_score(plugin_path: Path) -> QualityScoreReport:
    """Compute comprehensive quality score for a plugin.

    This function:
    1. Runs all validators
    2. Categorizes results
    3. Computes category scores
    4. Calculates overall weighted score
    5. Determines pass/fail status
    6. Generates recommendations

    Args:
        plugin_path: Path to the plugin directory

    Returns:
        QualityScoreReport with complete scoring breakdown
    """
    report = QualityScoreReport(plugin_path=str(plugin_path))

    # Run all validators
    validator_reports = run_all_validators(plugin_path)
    report.validator_reports = validator_reports

    # Categorize all results
    categorized = categorize_results(validator_reports)

    # Calculate category scores
    for category_name, results in categorized.items():
        threshold = CATEGORY_THRESHOLDS.get(category_name, 5)
        score, critical, major, minor, passed = calculate_category_score(results)

        cat_score = CategoryScore(
            name=category_name,
            score=score,
            threshold=threshold,
            passed=score >= threshold,
            issues_critical=critical,
            issues_major=major,
            issues_minor=minor,
            issues_passed=passed,
        )

        # Track critical failures
        if critical > 0:
            for result in results:
                if result.level == "CRITICAL":
                    report.critical_failures.append(f"[{category_name}] {result.message}")

        report.category_scores[category_name] = cat_score

    # Calculate weighted overall score (0-100)
    weighted_sum = 0.0
    total_weight = 0.0
    for category_name, cat_score in report.category_scores.items():
        weight = CATEGORY_WEIGHTS.get(category_name, 0.1)
        weighted_sum += (cat_score.score / 10.0) * weight * 100
        total_weight += weight

    # Normalize if weights don't sum to 1.0
    if total_weight > 0:
        report.overall_score = weighted_sum / total_weight
    else:
        report.overall_score = 0.0

    # Determine letter grade
    report.letter_grade = calculate_letter_grade(int(report.overall_score))

    # Determine pass/fail status
    has_critical = len(report.critical_failures) > 0
    all_categories_pass = all(cat.passed for cat in report.category_scores.values())

    if has_critical or report.overall_score < 60:
        report.status = "FAIL"
    elif report.overall_score >= 80 and all_categories_pass:
        report.status = "PASS"
    else:
        report.status = "CONDITIONAL_PASS"

    # Generate recommendations
    report.recommendations = generate_recommendations(report.category_scores)

    return report


# =============================================================================
# Output Formatting
# =============================================================================


def print_quality_report(report: QualityScoreReport, verbose: bool = False) -> None:
    """Print a formatted quality report to stdout.

    Args:
        report: QualityScoreReport to print
        verbose: If True, show detailed breakdown
    """
    print(f"\n{'=' * 70}")
    print(f"{COLORS['BOLD']}Plugin Quality Score Report{COLORS['RESET']}")
    print(f"{'=' * 70}")
    print(f"Plugin: {report.plugin_path}")

    # Overall score with color coding
    if report.status == "PASS":
        status_color = COLORS["PASSED"]
        status_symbol = "PASS"
    elif report.status == "CONDITIONAL_PASS":
        status_color = COLORS["MAJOR"]
        status_symbol = "CONDITIONAL PASS"
    else:
        status_color = COLORS["CRITICAL"]
        status_symbol = "FAIL"

    print(f"\n{COLORS['BOLD']}Overall Score:{COLORS['RESET']} ", end="")
    print(f"{status_color}{report.overall_score:.1f}/100 ({report.letter_grade}){COLORS['RESET']}")
    print(f"{COLORS['BOLD']}Status:{COLORS['RESET']} {status_color}{status_symbol}{COLORS['RESET']}")

    # Category breakdown
    print(f"\n{COLORS['BOLD']}Category Scores (0-10 scale):{COLORS['RESET']}")
    print("-" * 70)

    for name, cat in sorted(report.category_scores.items()):
        # Color based on pass/fail
        if cat.passed:
            score_color = COLORS["PASSED"]
        elif cat.score >= cat.threshold - 2:
            score_color = COLORS["MAJOR"]
        else:
            score_color = COLORS["CRITICAL"]

        # Format category name
        display_name = name.replace("_", " ").title()

        # Build status string
        status = "PASS" if cat.passed else "FAIL"
        status_indicator = f"[{status}]"

        print(f"  {display_name:25} {score_color}{cat.score:5.1f}/10{COLORS['RESET']} ", end="")
        print(f"(min: {cat.threshold}/10) ", end="")
        print(f"{score_color}{status_indicator:8}{COLORS['RESET']} ", end="")
        print(f"[{cat.rating}]")

        if verbose:
            if cat.issues_critical > 0:
                print(f"    {COLORS['CRITICAL']}- Critical: {cat.issues_critical}{COLORS['RESET']}")
            if cat.issues_major > 0:
                print(f"    {COLORS['MAJOR']}- Major: {cat.issues_major}{COLORS['RESET']}")
            if cat.issues_minor > 0:
                print(f"    {COLORS['MINOR']}- Minor: {cat.issues_minor}{COLORS['RESET']}")
            if cat.issues_passed > 0:
                print(f"    {COLORS['PASSED']}- Passed: {cat.issues_passed}{COLORS['RESET']}")

    # Critical failures (always show)
    if report.critical_failures:
        print(f"\n{COLORS['CRITICAL']}Critical Failures:{COLORS['RESET']}")
        print("-" * 70)
        for failure in report.critical_failures[:10]:  # Limit to 10
            print(f"  {COLORS['CRITICAL']}- {failure}{COLORS['RESET']}")
        if len(report.critical_failures) > 10:
            print(f"  ... and {len(report.critical_failures) - 10} more")

    # Recommendations
    if report.recommendations:
        print(f"\n{COLORS['BOLD']}Recommendations:{COLORS['RESET']}")
        print("-" * 70)
        for rec in report.recommendations[:10]:  # Limit to 10
            if "[CRITICAL]" in rec:
                print(f"  {COLORS['CRITICAL']}{rec}{COLORS['RESET']}")
            elif "[REQUIRED]" in rec:
                print(f"  {COLORS['MAJOR']}{rec}{COLORS['RESET']}")
            elif "[RECOMMENDED]" in rec:
                print(f"  {COLORS['MINOR']}{rec}{COLORS['RESET']}")
            else:
                print(f"  {COLORS['INFO']}{rec}{COLORS['RESET']}")
        if len(report.recommendations) > 10:
            print(f"  ... and {len(report.recommendations) - 10} more")

    # Rating guide
    print(f"\n{COLORS['BOLD']}Rating Guide:{COLORS['RESET']}")
    print("-" * 70)
    for score_range, description in RATING_DESCRIPTIONS.items():
        print(f"  {score_range}: {description}")

    print(f"\n{'=' * 70}")


# =============================================================================
# CLI Entry Point
# =============================================================================


def main() -> int:
    """CLI entry point for quality scoring.

    Returns:
        Exit code based on highest severity issue found:
        - 0: No issues (PASS)
        - 1: Critical issues found
        - 2: Major issues found (no critical)
        - 3: Minor issues only
    """
    parser = argparse.ArgumentParser(
        description="Compute quality score for Claude Code plugin",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exit codes (standard severity-based convention):
    0 - PASS: No issues found
    1 - CRITICAL: Critical issues found
    2 - MAJOR: Major issues found (no critical)
    3 - MINOR: Minor issues only

Rating scale (0-10 per category):
    9-10: Excellent - Ready for production
    7-8:  Good - Minor improvements recommended
    5-6:  Fair - Significant improvements needed
    0-4:  Poor - Major revision required
        """,
    )

    parser.add_argument(
        "plugin_path",
        type=Path,
        help="Path to the plugin directory to validate",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed breakdown including issue counts per category",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of formatted text",
    )
    parser.add_argument("--strict", action="store_true", help="Strict mode — NIT issues also block validation")

    args = parser.parse_args()

    # Resolve to absolute path so relative_to() works correctly
    plugin_path = args.plugin_path.resolve()

    # Validate plugin path exists
    if not plugin_path.exists():
        print(f"Error: Plugin path does not exist: {plugin_path}", file=sys.stderr)
        return EXIT_CRITICAL

    if not plugin_path.is_dir():
        print(f"Error: Plugin path is not a directory: {plugin_path}", file=sys.stderr)
        return EXIT_CRITICAL

    # Verify this is a plugin directory
    if not (plugin_path / ".claude-plugin").is_dir():
        print(
            f"Error: No Claude Code plugin found at {plugin_path}\nExpected a .claude-plugin/ directory.",
            file=sys.stderr,
        )
        return EXIT_CRITICAL

    # Compute quality score
    report = compute_quality_score(plugin_path)

    # Output results
    if args.json:
        print(report.to_json())
    else:
        print_quality_report(report, verbose=args.verbose)

    # Determine exit code based on highest severity issue found
    # Count issues across all category scores
    total_critical = sum(cat.issues_critical for cat in report.category_scores.values())
    total_major = sum(cat.issues_major for cat in report.category_scores.values())
    total_minor = sum(cat.issues_minor for cat in report.category_scores.values())

    if total_critical > 0:
        return EXIT_CRITICAL
    elif total_major > 0:
        return EXIT_MAJOR
    elif total_minor > 0:
        return EXIT_MINOR
    else:
        return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
