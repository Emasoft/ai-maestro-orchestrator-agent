#!/usr/bin/env python3
"""
Marketplace Publishing Pipeline Validator for Claude Code Plugins.

Validates the complete marketplace publishing automation pipeline including:
- Marketplace structure (marketplace.json, .gitmodules)
- Git submodule health and configuration
- GitHub workflow automation (update-submodules, notify-marketplace)
- Sync scripts for version management
- Documentation completeness

This validator ensures your marketplace can:
1. Receive notifications when plugins update
2. Automatically sync submodule versions
3. Run validation CI on changes
4. Maintain version consistency

Exit Codes:
  0 - Score >= 90 (A grade) - Pipeline fully operational
  1 - Score >= 70 (B or C grade) - Minor gaps, mostly functional
  2 - Score >= 60 (D grade) - Manual updates required
  3 - Score < 60 (F grade) - Pipeline broken or not configured

Usage:
    uv run python scripts/validate_marketplace_pipeline.py /path/to/marketplace
    uv run python scripts/validate_marketplace_pipeline.py /path/to/marketplace --verbose
    uv run python scripts/validate_marketplace_pipeline.py /path/to/marketplace --json
"""

from __future__ import annotations

import argparse
import ast
import configparser
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from cpv_validation_common import (
    EXIT_CRITICAL,
    EXIT_MAJOR,
    EXIT_MINOR,
    EXIT_OK,
    Level,
)

# =============================================================================
# Constants
# =============================================================================

# Category weights (must sum to 100)
CATEGORY_WEIGHTS = {
    "marketplace_structure": 25,
    "submodule_health": 20,
    "marketplace_workflows": 20,
    "plugin_workflows": 15,
    "sync_scripts": 10,
    "documentation": 10,
}

# Required fields in marketplace.json
REQUIRED_MARKETPLACE_FIELDS = {"name", "version", "plugins"}

# GitHub repo HTTPS URL pattern
GITHUB_HTTPS_URL_PATTERN = re.compile(r"^https://github\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+(\.git)?$")


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class PipelineValidationResult:
    """Result of a single validation check with weighted scoring."""

    level: Level  # "CRITICAL", "MAJOR", "MINOR", "INFO", "PASSED"
    category: str  # Category name for grouping
    message: str
    file_path: str = ""
    suggestion: str = ""
    points_earned: float = 0.0
    points_possible: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "level": self.level,
            "category": self.category,
            "message": self.message,
            "file_path": self.file_path if self.file_path else None,
            "suggestion": self.suggestion if self.suggestion else None,
            "points_earned": self.points_earned,
            "points_possible": self.points_possible,
        }


@dataclass
class CategoryScore:
    """Score tracking for a validation category."""

    name: str
    weight: int
    points_earned: float = 0.0
    points_possible: float = 0.0
    results: list[PipelineValidationResult] = field(default_factory=list)

    @property
    def percentage(self) -> float:
        """Calculate percentage score for this category."""
        if self.points_possible == 0:
            return 100.0
        return (self.points_earned / self.points_possible) * 100.0

    @property
    def weighted_score(self) -> float:
        """Calculate weighted contribution to total score."""
        return (self.percentage / 100.0) * self.weight


@dataclass
class PipelineValidationReport:
    """Complete validation report for marketplace pipeline."""

    marketplace_path: Path
    marketplace_name: str | None = None
    categories: dict[str, CategoryScore] = field(default_factory=dict)
    plugins_found: list[str] = field(default_factory=list)
    submodules_found: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize category scores."""
        for name, weight in CATEGORY_WEIGHTS.items():
            self.categories[name] = CategoryScore(name=name, weight=weight)

    def add(
        self,
        level: Level,
        category: str,
        message: str,
        points_possible: float,
        points_earned: float | None = None,
        file_path: str = "",
        suggestion: str = "",
    ) -> None:
        """Add a validation result to the appropriate category."""
        # If level is PASSED, earn full points; otherwise earn specified or 0
        if points_earned is None:
            points_earned = points_possible if level == "PASSED" else 0.0

        result = PipelineValidationResult(
            level=level,
            category=category,
            message=message,
            file_path=file_path,
            suggestion=suggestion,
            points_earned=points_earned,
            points_possible=points_possible,
        )

        if category in self.categories:
            self.categories[category].results.append(result)
            self.categories[category].points_earned += points_earned
            self.categories[category].points_possible += points_possible

    def passed(
        self,
        category: str,
        message: str,
        points: float,
        file_path: str = "",
    ) -> None:
        """Add a passed check."""
        self.add("PASSED", category, message, points, points, file_path)

    def critical(
        self,
        category: str,
        message: str,
        points: float,
        file_path: str = "",
        suggestion: str = "",
    ) -> None:
        """Add a critical failure (0 points earned)."""
        self.add("CRITICAL", category, message, points, 0.0, file_path, suggestion)

    def major(
        self,
        category: str,
        message: str,
        points: float,
        file_path: str = "",
        suggestion: str = "",
    ) -> None:
        """Add a major failure (0 points earned)."""
        self.add("MAJOR", category, message, points, 0.0, file_path, suggestion)

    def minor(
        self,
        category: str,
        message: str,
        points: float,
        file_path: str = "",
        suggestion: str = "",
    ) -> None:
        """Add a minor failure (0 points earned)."""
        self.add("MINOR", category, message, points, 0.0, file_path, suggestion)

    def info(
        self,
        category: str,
        message: str,
        file_path: str = "",
    ) -> None:
        """Add an info message (no points)."""
        self.add("INFO", category, message, 0.0, 0.0, file_path)

    @property
    def total_score(self) -> float:
        """Calculate total weighted score (0-100)."""
        return sum(cat.weighted_score for cat in self.categories.values())

    @property
    def grade(self) -> str:
        """Calculate letter grade based on total score."""
        score = self.total_score
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    @property
    def grade_description(self) -> str:
        """Get description for the grade."""
        descriptions = {
            "A": "Pipeline fully operational",
            "B": "Minor gaps, mostly functional",
            "C": "Some automation missing",
            "D": "Manual updates required",
            "F": "Pipeline broken or not configured",
        }
        return descriptions.get(self.grade, "Unknown")

    def has_critical(self) -> bool:
        """Check if there are critical issues."""
        return any(r.level == "CRITICAL" for cat in self.categories.values() for r in cat.results)

    def has_major(self) -> bool:
        """Check if there are major issues."""
        return any(r.level == "MAJOR" for cat in self.categories.values() for r in cat.results)

    def has_minor(self) -> bool:
        """Check if there are minor issues."""
        return any(r.level == "MINOR" for cat in self.categories.values() for r in cat.results)

    def exit_code(self) -> int:
        """Return appropriate exit code based on score."""
        score = self.total_score
        if score >= 90:
            return EXIT_OK  # A grade
        elif score >= 70:
            return EXIT_CRITICAL  # B or C grade
        elif score >= 60:
            return EXIT_MAJOR  # D grade
        else:
            return EXIT_MINOR  # F grade (ironic but follows spec)

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary for JSON serialization."""
        return {
            "marketplace_path": str(self.marketplace_path),
            "marketplace_name": self.marketplace_name,
            "total_score": round(self.total_score, 2),
            "grade": self.grade,
            "grade_description": self.grade_description,
            "plugins_found": self.plugins_found,
            "submodules_found": self.submodules_found,
            "categories": {
                name: {
                    "weight": cat.weight,
                    "points_earned": round(cat.points_earned, 2),
                    "points_possible": round(cat.points_possible, 2),
                    "percentage": round(cat.percentage, 2),
                    "weighted_score": round(cat.weighted_score, 2),
                    "results": [r.to_dict() for r in cat.results],
                }
                for name, cat in self.categories.items()
            },
        }


# =============================================================================
# Helper Functions
# =============================================================================


def parse_gitmodules(gitmodules_path: Path) -> dict[str, dict[str, str]]:
    """Parse .gitmodules file and return submodule information.

    Args:
        gitmodules_path: Path to .gitmodules file

    Returns:
        Dictionary mapping submodule names to their config (path, url)
    """
    submodules: dict[str, dict[str, str]] = {}

    if not gitmodules_path.exists():
        return submodules

    # Use configparser with special handling for git config format
    config = configparser.ConfigParser()
    try:
        config.read(str(gitmodules_path))
        for section in config.sections():
            # Section format: submodule "name"
            if section.startswith('submodule "') and section.endswith('"'):
                name = section[11:-1]  # Extract name from quotes
                submodules[name] = {
                    "path": config.get(section, "path", fallback=""),
                    "url": config.get(section, "url", fallback=""),
                }
    except Exception:
        # Fallback to regex parsing if configparser fails
        content = gitmodules_path.read_text()
        submodule_pattern = re.compile(
            r'\[submodule\s+"([^"]+)"\]\s*'
            r"(?:path\s*=\s*([^\n]+)\s*)?"
            r"(?:url\s*=\s*([^\n]+)\s*)?",
            re.MULTILINE,
        )
        for match in submodule_pattern.finditer(content):
            name = match.group(1)
            submodules[name] = {
                "path": match.group(2).strip() if match.group(2) else "",
                "url": match.group(3).strip() if match.group(3) else "",
            }

    return submodules


def load_yaml_file(file_path: Path) -> dict[str, Any] | None:
    """Safely load a YAML file.

    Args:
        file_path: Path to YAML file

    Returns:
        Parsed YAML content or None if failed
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            result: dict[str, Any] | None = yaml.safe_load(f)
            return result
    except Exception:
        return None


def check_python_syntax(file_path: Path) -> bool:
    """Check if a Python file has valid syntax.

    Args:
        file_path: Path to Python file

    Returns:
        True if syntax is valid, False otherwise
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            ast.parse(f.read())
        return True
    except SyntaxError:
        return False


def run_git_command(cwd: Path, *args: str) -> tuple[bool, str]:
    """Run a git command and return success status and output.

    Args:
        cwd: Working directory for the command
        *args: Git command arguments

    Returns:
        Tuple of (success, output)
    """
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


# =============================================================================
# Category 1: Marketplace Structure Validation (25 points)
# =============================================================================


def validate_marketplace_structure(
    marketplace_path: Path,
    report: PipelineValidationReport,
) -> dict[str, Any] | None:
    """Validate marketplace structure and return parsed marketplace.json.

    Checks:
    - marketplace.json exists (5 pts, CRITICAL)
    - marketplace.json valid JSON (3 pts, CRITICAL)
    - marketplace.json has required fields (5 pts, CRITICAL)
    - .gitmodules exists (5 pts, CRITICAL)
    - .gitmodules has entries for all plugins (4 pts, MAJOR)
    - Plugin versions match (3 pts, MAJOR)

    Returns:
        Parsed marketplace.json data or None if critical failure
    """
    category = "marketplace_structure"
    # Check both possible locations for marketplace.json
    marketplace_json_path = marketplace_path / "marketplace.json"
    alt_marketplace_json_path = marketplace_path / ".claude-plugin" / "marketplace.json"
    gitmodules_path = marketplace_path / ".gitmodules"

    # Check 1: marketplace.json exists (5 pts, CRITICAL)
    # Check root first, then .claude-plugin/
    if marketplace_json_path.exists():
        actual_path = marketplace_json_path
    elif alt_marketplace_json_path.exists():
        actual_path = alt_marketplace_json_path
        marketplace_json_path = actual_path  # Use this path for subsequent checks
    else:
        actual_path = None

    if actual_path is None:
        report.critical(
            category,
            "marketplace.json not found",
            5.0,
            str(marketplace_json_path),
            "Create marketplace.json with name, version, and plugins fields in root or .claude-plugin/",
        )
        # Still check other things even if this fails
        marketplace_data = None
    else:
        report.passed(category, "marketplace.json exists", 5.0, str(actual_path))

        # Check 2: marketplace.json valid JSON (3 pts, CRITICAL)
        try:
            with open(marketplace_json_path, encoding="utf-8") as f:
                marketplace_data = json.load(f)
            report.passed(category, "marketplace.json is valid JSON", 3.0, str(marketplace_json_path))
        except json.JSONDecodeError as e:
            report.critical(
                category,
                f"marketplace.json has invalid JSON: {e}",
                3.0,
                str(marketplace_json_path),
                "Fix JSON syntax errors",
            )
            marketplace_data = None

        # Check 3: Required fields (5 pts, CRITICAL)
        if marketplace_data is not None:
            missing_fields = REQUIRED_MARKETPLACE_FIELDS - set(marketplace_data.keys())
            if missing_fields:
                report.critical(
                    category,
                    f"marketplace.json missing required fields: {', '.join(sorted(missing_fields))}",
                    5.0,
                    str(marketplace_json_path),
                    f"Add missing fields: {', '.join(sorted(missing_fields))}",
                )
            else:
                report.passed(
                    category,
                    "marketplace.json has all required fields (name, version, plugins)",
                    5.0,
                    str(marketplace_json_path),
                )
                report.marketplace_name = marketplace_data.get("name")
                # Extract plugin names
                plugins = marketplace_data.get("plugins", [])
                if isinstance(plugins, list):
                    for plugin in plugins:
                        if isinstance(plugin, dict) and "name" in plugin:
                            report.plugins_found.append(plugin["name"])
        else:
            # Can't check fields if JSON is invalid
            report.critical(
                category,
                "Cannot validate required fields - marketplace.json is invalid",
                5.0,
            )

    # Check 4: .gitmodules exists (5 pts, CRITICAL)
    if not gitmodules_path.exists():
        report.critical(
            category,
            ".gitmodules not found - plugins should be git submodules",
            5.0,
            str(gitmodules_path),
            "Initialize plugins as git submodules with: git submodule add <url> <path>",
        )
        submodules = {}
    else:
        report.passed(category, ".gitmodules exists", 5.0, str(gitmodules_path))
        submodules = parse_gitmodules(gitmodules_path)
        report.submodules_found = list(submodules.keys())

    # Check 5: .gitmodules has entries for all plugins (4 pts, MAJOR)
    if marketplace_data is not None and report.plugins_found:
        submodule_paths = {sm.get("path", "") for sm in submodules.values()}
        missing_submodules = []
        for plugin_name in report.plugins_found:
            # Check if plugin has a corresponding submodule (by name or path)
            # Common patterns: plugins/<name>, <name>
            possible_paths = [plugin_name, f"plugins/{plugin_name}"]
            if not any(p in submodule_paths for p in possible_paths) and plugin_name not in submodules:
                missing_submodules.append(plugin_name)

        if missing_submodules:
            report.major(
                category,
                f"Plugins missing from .gitmodules: {', '.join(missing_submodules)}",
                4.0,
                str(gitmodules_path),
                "Add missing plugins as submodules: git submodule add <url> plugins/<name>",
            )
        else:
            report.passed(
                category,
                "All plugins have corresponding submodule entries",
                4.0,
                str(gitmodules_path),
            )
    else:
        # Can't check submodule mapping if no plugins found
        if not report.plugins_found:
            report.major(
                category,
                "No plugins found in marketplace.json to validate submodules against",
                4.0,
            )
        else:
            report.passed(
                category,
                "Submodule entries present",
                4.0,
            )

    # Check 6: Plugin versions match (3 pts, MAJOR)
    if marketplace_data is not None and report.plugins_found:
        version_mismatches = []
        plugins = marketplace_data.get("plugins", [])

        for plugin in plugins:
            if not isinstance(plugin, dict):
                continue
            plugin_name = plugin.get("name", "")
            marketplace_version = plugin.get("version", "")
            if not marketplace_version:
                continue

            # Try to find plugin.json in submodule path
            plugin_json_search_paths: list[Path] = [
                marketplace_path / plugin_name / ".claude-plugin" / "plugin.json",
                marketplace_path / "plugins" / plugin_name / ".claude-plugin" / "plugin.json",
                marketplace_path / plugin_name / "plugin.json",
                marketplace_path / "plugins" / plugin_name / "plugin.json",
            ]

            for plugin_json_path in plugin_json_search_paths:
                if plugin_json_path.exists():
                    try:
                        with open(plugin_json_path, encoding="utf-8") as f:
                            plugin_data = json.load(f)
                        plugin_version = plugin_data.get("version", "")
                        if plugin_version and plugin_version != marketplace_version:
                            version_mismatches.append(
                                f"{plugin_name}: marketplace={marketplace_version}, plugin.json={plugin_version}"
                            )
                    except Exception:
                        pass
                    break

        if version_mismatches:
            report.major(
                category,
                f"Version mismatches: {'; '.join(version_mismatches)}",
                3.0,
                suggestion="Run sync script to update marketplace.json versions",
            )
        else:
            report.passed(
                category,
                "Plugin versions in marketplace.json match plugin.json files",
                3.0,
            )
    else:
        report.passed(
            category,
            "Version consistency check skipped (no plugins with versions)",
            3.0,
        )

    return marketplace_data if marketplace_data else None


# =============================================================================
# Category 2: Submodule Health Validation (20 points)
# =============================================================================


def validate_submodule_health(
    marketplace_path: Path,
    report: PipelineValidationReport,
) -> None:
    """Validate git submodule health.

    Checks:
    - All submodules initialized (5 pts, CRITICAL)
    - All submodules point to valid remote URLs (5 pts, CRITICAL)
    - Submodule paths exist as directories (4 pts, MAJOR)
    - Submodule remotes are HTTPS GitHub URLs (4 pts, MAJOR)
    - No detached HEAD warnings (2 pts, MINOR)
    """
    category = "submodule_health"
    gitmodules_path = marketplace_path / ".gitmodules"

    # Parse .gitmodules first
    if not gitmodules_path.exists():
        report.critical(
            category,
            "Cannot validate submodules - .gitmodules not found",
            20.0,  # All points for this category
        )
        return

    submodules = parse_gitmodules(gitmodules_path)
    if not submodules:
        report.info(category, "No submodules defined in .gitmodules")
        # Award all points since there's nothing to fail
        report.passed(category, "No submodules to validate", 5.0)
        report.passed(category, "No submodules to validate", 5.0)
        report.passed(category, "No submodules to validate", 4.0)
        report.passed(category, "No submodules to validate", 4.0)
        report.passed(category, "No submodules to validate", 2.0)
        return

    # Check 1: All submodules initialized (5 pts, CRITICAL)
    success, output = run_git_command(marketplace_path, "submodule", "status")
    if not success:
        report.critical(
            category,
            f"Failed to get submodule status: {output}",
            5.0,
            suggestion="Run 'git submodule init' and 'git submodule update'",
        )
        uninitialized = list(submodules.keys())
    else:
        # Parse submodule status - lines starting with '-' are uninitialized
        uninitialized = []
        for line in output.strip().split("\n"):
            if line.startswith("-"):
                # Format: -<sha> <path> (optional description)
                parts = line[1:].split()
                if len(parts) >= 2:
                    uninitialized.append(parts[1])

        if uninitialized:
            report.critical(
                category,
                f"Uninitialized submodules: {', '.join(uninitialized)}",
                5.0,
                suggestion="Run 'git submodule update --init --recursive'",
            )
        else:
            report.passed(category, "All submodules are initialized", 5.0)

    # Check 2: All submodules point to valid remote URLs (5 pts, CRITICAL)
    invalid_urls = []
    for name, config in submodules.items():
        url = config.get("url", "")
        if not url:
            invalid_urls.append(f"{name}: no URL specified")
        elif not url.startswith(("https://", "git@", "git://")):
            invalid_urls.append(f"{name}: invalid URL format")

    if invalid_urls:
        report.critical(
            category,
            f"Invalid submodule URLs: {'; '.join(invalid_urls)}",
            5.0,
            suggestion="Update .gitmodules with valid git URLs",
        )
    else:
        report.passed(category, "All submodule URLs are valid", 5.0)

    # Check 3: Submodule paths exist as directories (4 pts, MAJOR)
    missing_paths = []
    for name, config in submodules.items():
        path = config.get("path", name)
        full_path = marketplace_path / path
        if not full_path.is_dir():
            missing_paths.append(path)

    if missing_paths:
        report.major(
            category,
            f"Submodule directories not found: {', '.join(missing_paths)}",
            4.0,
            suggestion="Run 'git submodule update --init' to clone missing submodules",
        )
    else:
        report.passed(category, "All submodule directories exist", 4.0)

    # Check 4: Submodule remotes are HTTPS GitHub URLs (4 pts, MAJOR)
    non_github_https = []
    for name, config in submodules.items():
        url = config.get("url", "")
        if url and not GITHUB_HTTPS_URL_PATTERN.match(url):
            non_github_https.append(f"{name}: {url}")

    if non_github_https:
        report.major(
            category,
            f"Non-HTTPS GitHub URLs (may cause CI issues): {'; '.join(non_github_https)}",
            4.0,
            suggestion="Use HTTPS GitHub URLs (https://github.com/owner/repo.git) for better CI compatibility",
        )
    else:
        report.passed(category, "All submodules use HTTPS GitHub URLs", 4.0)

    # Check 5: No detached HEAD warnings (2 pts, MINOR)
    detached_heads = []
    if success and output:
        for line in output.strip().split("\n"):
            # Lines with '+' indicate the submodule HEAD doesn't match recorded commit
            if line.startswith("+"):
                parts = line[1:].split()
                if len(parts) >= 2:
                    detached_heads.append(parts[1])

    if detached_heads:
        report.minor(
            category,
            f"Submodules with modified HEAD (may be intentional): {', '.join(detached_heads)}",
            2.0,
            suggestion="Commit submodule updates or reset to recorded commit",
        )
    else:
        report.passed(category, "No detached HEAD warnings", 2.0)


# =============================================================================
# Category 3: Marketplace Workflows Validation (20 points)
# =============================================================================


def validate_marketplace_workflows(
    marketplace_path: Path,
    report: PipelineValidationReport,
) -> None:
    """Validate GitHub workflow automation for the marketplace.

    Checks:
    - .github/workflows/ directory exists (3 pts, MAJOR)
    - update-submodules.yml exists (5 pts, MAJOR)
    - update-submodules.yml has repository_dispatch trigger (4 pts, MAJOR)
    - update-submodules.yml has workflow_dispatch for manual trigger (2 pts, MINOR)
    - update-submodules.yml runs sync script (3 pts, MAJOR)
    - validate.yml exists for CI (3 pts, MINOR)
    """
    category = "marketplace_workflows"
    workflows_dir = marketplace_path / ".github" / "workflows"

    # Check 1: .github/workflows/ directory exists (3 pts, MAJOR)
    if not workflows_dir.is_dir():
        report.major(
            category,
            ".github/workflows/ directory not found",
            3.0,
            str(workflows_dir),
            "Create .github/workflows/ and add automation workflows",
        )
        # Can't check other workflow-related items
        report.major(category, "Cannot check update-submodules.yml - no workflows dir", 5.0)
        report.major(category, "Cannot check repository_dispatch trigger", 4.0)
        report.minor(category, "Cannot check workflow_dispatch trigger", 2.0)
        report.major(category, "Cannot check sync script execution", 3.0)
        report.minor(category, "Cannot check validate.yml", 3.0)
        return

    report.passed(category, ".github/workflows/ directory exists", 3.0, str(workflows_dir))

    # Check 2: update-submodules.yml exists (5 pts, MAJOR)
    update_workflow_path = workflows_dir / "update-submodules.yml"
    if not update_workflow_path.exists():
        # Try alternative names
        alternatives = ["update-plugins.yml", "sync-submodules.yml", "auto-update.yml"]
        found_alternative = None
        for alt in alternatives:
            alt_path = workflows_dir / alt
            if alt_path.exists():
                found_alternative = alt_path
                break

        if found_alternative:
            report.passed(
                category,
                f"Update workflow found: {found_alternative.name}",
                5.0,
                str(found_alternative),
            )
            update_workflow_path = found_alternative
        else:
            report.major(
                category,
                "update-submodules.yml not found",
                5.0,
                str(update_workflow_path),
                "Create workflow to handle plugin update notifications",
            )
            # Can't check workflow contents
            report.major(category, "Cannot check repository_dispatch - workflow missing", 4.0)
            report.minor(category, "Cannot check workflow_dispatch - workflow missing", 2.0)
            report.major(category, "Cannot check sync script - workflow missing", 3.0)
            # Still check validate.yml
            validate_workflow_path = workflows_dir / "validate.yml"
            if validate_workflow_path.exists() or (workflows_dir / "ci.yml").exists():
                report.passed(category, "CI validation workflow exists", 3.0)
            else:
                report.minor(
                    category,
                    "No CI validation workflow (validate.yml or ci.yml) found",
                    3.0,
                    suggestion="Create validate.yml to run validation on PRs",
                )
            return
    else:
        report.passed(category, "update-submodules.yml exists", 5.0, str(update_workflow_path))

    # Load and parse the workflow
    workflow_data = load_yaml_file(update_workflow_path)
    if workflow_data is None:
        report.major(
            category,
            "Failed to parse update-submodules.yml - invalid YAML",
            4.0 + 2.0 + 3.0,  # Points for remaining checks
            str(update_workflow_path),
            "Fix YAML syntax in workflow file",
        )
    else:
        # YAML 1.1 treats 'on' as boolean True, so we need to check for both string and bool keys
        triggers_value = workflow_data.get("on") or workflow_data.get(True, {})  # type: ignore[call-overload]
        triggers = triggers_value if isinstance(triggers_value, dict) else {}

        # Check 3: repository_dispatch trigger (4 pts, MAJOR)
        if "repository_dispatch" in triggers or (
            isinstance(triggers_value, list) and "repository_dispatch" in triggers_value
        ):
            report.passed(
                category,
                "update-submodules.yml has repository_dispatch trigger",
                4.0,
                str(update_workflow_path),
            )
        else:
            report.major(
                category,
                "update-submodules.yml missing repository_dispatch trigger",
                4.0,
                str(update_workflow_path),
                "Add 'repository_dispatch' to 'on:' section to receive plugin notifications",
            )

        # Check 4: workflow_dispatch for manual trigger (2 pts, MINOR)
        if "workflow_dispatch" in triggers or (
            isinstance(triggers_value, list) and "workflow_dispatch" in triggers_value
        ):
            report.passed(
                category,
                "update-submodules.yml has workflow_dispatch for manual trigger",
                2.0,
                str(update_workflow_path),
            )
        else:
            report.minor(
                category,
                "update-submodules.yml missing workflow_dispatch (manual trigger)",
                2.0,
                str(update_workflow_path),
                "Add 'workflow_dispatch' to allow manual workflow runs",
            )

        # Check 5: runs sync script (3 pts, MAJOR)
        workflow_content = update_workflow_path.read_text()
        sync_patterns = [
            r"sync.*script",
            r"python.*sync",
            r"sync.*version",
            r"update.*submodule",
            r"git\s+submodule\s+update",
        ]
        runs_sync = any(re.search(pattern, workflow_content, re.IGNORECASE) for pattern in sync_patterns)

        if runs_sync:
            report.passed(
                category,
                "update-submodules.yml runs sync/update operations",
                3.0,
                str(update_workflow_path),
            )
        else:
            report.major(
                category,
                "update-submodules.yml doesn't appear to run sync operations",
                3.0,
                str(update_workflow_path),
                "Add step to run sync script or git submodule update",
            )

    # Check 6: validate.yml exists for CI (3 pts, MINOR)
    validate_workflow = workflows_dir / "validate.yml"
    ci_workflow = workflows_dir / "ci.yml"
    if validate_workflow.exists() or ci_workflow.exists():
        found = validate_workflow if validate_workflow.exists() else ci_workflow
        report.passed(category, f"CI validation workflow exists ({found.name})", 3.0, str(found))
    else:
        report.minor(
            category,
            "No CI validation workflow (validate.yml or ci.yml) found",
            3.0,
            str(validate_workflow),
            "Create validate.yml to run validation checks on PRs and pushes",
        )


# =============================================================================
# Category 4: Plugin Workflows Validation (15 points)
# =============================================================================


def validate_plugin_workflows(
    marketplace_path: Path,
    report: PipelineValidationReport,
) -> None:
    """Validate GitHub workflows in each plugin for marketplace notification.

    Checks (per plugin with workflows found):
    - Each plugin has .github/workflows/ directory (3 pts, MAJOR)
    - Each plugin has notify-marketplace.yml (5 pts, MAJOR)
    - notify-marketplace.yml has correct push trigger (3 pts, MAJOR)
    - notify-marketplace.yml uses repository_dispatch (4 pts, MAJOR)

    Points are distributed across all plugins found.
    """
    category = "plugin_workflows"
    gitmodules_path = marketplace_path / ".gitmodules"

    # Parse .gitmodules to find plugin paths
    if not gitmodules_path.exists():
        report.major(
            category,
            "Cannot validate plugin workflows - .gitmodules not found",
            15.0,
        )
        return

    submodules = parse_gitmodules(gitmodules_path)
    if not submodules:
        report.info(category, "No plugin submodules to validate workflows for")
        # Award points since there's nothing to fail
        report.passed(category, "No plugins to validate", 15.0)
        return

    # Calculate points per plugin (distribute evenly)
    plugin_count = len(submodules)
    points_per_check = {
        "workflows_dir": 3.0 / plugin_count,
        "notify_workflow": 5.0 / plugin_count,
        "push_trigger": 3.0 / plugin_count,
        "repository_dispatch": 4.0 / plugin_count,
    }

    plugins_with_workflows = 0
    plugins_with_notify = 0
    plugins_with_push_trigger = 0
    plugins_with_dispatch = 0

    for name, config in submodules.items():
        path = config.get("path", name)
        plugin_path = marketplace_path / path

        if not plugin_path.is_dir():
            continue

        workflows_dir = plugin_path / ".github" / "workflows"

        # Check 1: .github/workflows/ exists
        if workflows_dir.is_dir():
            plugins_with_workflows += 1

            # Check 2: notify-marketplace.yml exists
            notify_workflow = workflows_dir / "notify-marketplace.yml"
            if not notify_workflow.exists():
                # Try alternatives
                alternatives = ["notify.yml", "marketplace-notify.yml", "update-marketplace.yml"]
                for alt in alternatives:
                    alt_path = workflows_dir / alt
                    if alt_path.exists():
                        notify_workflow = alt_path
                        break

            if notify_workflow.exists():
                plugins_with_notify += 1

                # Check 3 & 4: Workflow contents
                workflow_data = load_yaml_file(notify_workflow)
                if workflow_data:
                    # YAML 1.1 treats 'on' as boolean True, so check both keys
                    triggers_value = workflow_data.get("on") or workflow_data.get(True, {})  # type: ignore[call-overload]
                    triggers = triggers_value if isinstance(triggers_value, dict) else {}
                    # Check push trigger
                    if "push" in triggers:
                        plugins_with_push_trigger += 1

                    # Check for repository_dispatch action
                    workflow_content = notify_workflow.read_text()
                    if "repository_dispatch" in workflow_content or "repository-dispatch" in workflow_content:
                        plugins_with_dispatch += 1

    # Report results
    if plugins_with_workflows == plugin_count:
        report.passed(
            category,
            f"All {plugin_count} plugins have .github/workflows/ directory",
            3.0,
        )
    elif plugins_with_workflows > 0:
        report.add(
            "MAJOR",
            category,
            f"Only {plugins_with_workflows}/{plugin_count} plugins have .github/workflows/",
            3.0,
            points_per_check["workflows_dir"] * plugins_with_workflows,
            suggestion="Add .github/workflows/ to all plugins",
        )
    else:
        report.major(
            category,
            "No plugins have .github/workflows/ directory",
            3.0,
            suggestion="Create .github/workflows/ in each plugin with notify workflow",
        )

    if plugins_with_notify == plugin_count:
        report.passed(
            category,
            f"All {plugin_count} plugins have notify-marketplace workflow",
            5.0,
        )
    elif plugins_with_notify > 0:
        report.add(
            "MAJOR",
            category,
            f"Only {plugins_with_notify}/{plugin_count} plugins have notify workflow",
            5.0,
            points_per_check["notify_workflow"] * plugins_with_notify,
            suggestion="Add notify-marketplace.yml to remaining plugins",
        )
    else:
        report.major(
            category,
            "No plugins have notify-marketplace workflow",
            5.0,
            suggestion="Create notify-marketplace.yml in each plugin to notify marketplace of updates",
        )

    if plugins_with_push_trigger == plugins_with_notify and plugins_with_notify > 0:
        report.passed(
            category,
            "All notify workflows have push trigger",
            3.0,
        )
    elif plugins_with_push_trigger > 0:
        report.add(
            "MAJOR",
            category,
            f"Only {plugins_with_push_trigger}/{plugins_with_notify} notify workflows have push trigger",
            3.0,
            points_per_check["push_trigger"] * plugins_with_push_trigger,
            suggestion="Add 'on: push' trigger to notify workflows",
        )
    elif plugins_with_notify > 0:
        report.major(
            category,
            "No notify workflows have push trigger",
            3.0,
            suggestion="Add 'on: push' to trigger notification on commits",
        )
    else:
        report.major(category, "No notify workflows to check push trigger", 3.0)

    if plugins_with_dispatch == plugins_with_notify and plugins_with_notify > 0:
        report.passed(
            category,
            "All notify workflows use repository_dispatch",
            4.0,
        )
    elif plugins_with_dispatch > 0:
        report.add(
            "MAJOR",
            category,
            f"Only {plugins_with_dispatch}/{plugins_with_notify} notify workflows use repository_dispatch",
            4.0,
            points_per_check["repository_dispatch"] * plugins_with_dispatch,
            suggestion="Add repository_dispatch action to notify workflows",
        )
    elif plugins_with_notify > 0:
        report.major(
            category,
            "No notify workflows use repository_dispatch",
            4.0,
            suggestion="Use peter-evans/repository-dispatch action to notify marketplace",
        )
    else:
        report.major(category, "No notify workflows to check repository_dispatch", 4.0)


# =============================================================================
# Category 5: Sync Scripts Validation (10 points)
# =============================================================================


def validate_sync_scripts(
    marketplace_path: Path,
    report: PipelineValidationReport,
) -> None:
    """Validate sync scripts for version management.

    Checks:
    - scripts/ directory exists (2 pts, MINOR)
    - sync_marketplace_versions.py exists (4 pts, MAJOR)
    - sync_marketplace_versions.py is executable (2 pts, MINOR)
    - sync_marketplace_versions.py has valid Python syntax (2 pts, MINOR)
    """
    category = "sync_scripts"
    scripts_dir = marketplace_path / "scripts"

    # Check 1: scripts/ directory exists (2 pts, MINOR)
    if not scripts_dir.is_dir():
        report.minor(
            category,
            "scripts/ directory not found",
            2.0,
            str(scripts_dir),
            "Create scripts/ directory for automation scripts",
        )
        # Can't check other items
        report.major(category, "Cannot check sync script - no scripts/ dir", 4.0)
        report.minor(category, "Cannot check executable permission", 2.0)
        report.minor(category, "Cannot check Python syntax", 2.0)
        return

    report.passed(category, "scripts/ directory exists", 2.0, str(scripts_dir))

    # Check 2: sync_marketplace_versions.py exists (4 pts, MAJOR)
    sync_script = scripts_dir / "sync_marketplace_versions.py"
    if not sync_script.exists():
        # Try alternatives
        alternatives = [
            "sync_versions.py",
            "update_versions.py",
            "sync.py",
            "sync_marketplace.py",
        ]
        found_alternative = None
        for alt in alternatives:
            alt_path = scripts_dir / alt
            if alt_path.exists():
                found_alternative = alt_path
                break

        if found_alternative:
            report.passed(
                category,
                f"Sync script found: {found_alternative.name}",
                4.0,
                str(found_alternative),
            )
            sync_script = found_alternative
        else:
            report.major(
                category,
                "sync_marketplace_versions.py not found",
                4.0,
                str(sync_script),
                "Create script to sync versions from plugin.json to marketplace.json",
            )
            # Can't check other items
            report.minor(category, "Cannot check executable - script missing", 2.0)
            report.minor(category, "Cannot check syntax - script missing", 2.0)
            return
    else:
        report.passed(category, "sync_marketplace_versions.py exists", 4.0, str(sync_script))

    # Check 3: Script is executable (2 pts, MINOR)
    import os
    import stat

    file_stat = os.stat(sync_script)
    is_executable = bool(file_stat.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))

    if is_executable:
        report.passed(category, "Sync script is executable", 2.0, str(sync_script))
    else:
        report.minor(
            category,
            "Sync script is not executable",
            2.0,
            str(sync_script),
            f"Run: chmod +x {sync_script}",
        )

    # Check 4: Valid Python syntax (2 pts, MINOR)
    if check_python_syntax(sync_script):
        report.passed(category, "Sync script has valid Python syntax", 2.0, str(sync_script))
    else:
        report.minor(
            category,
            "Sync script has Python syntax errors",
            2.0,
            str(sync_script),
            "Fix Python syntax errors in the script",
        )


# =============================================================================
# Category 6: Documentation Validation (10 points)
# =============================================================================


def validate_documentation(
    marketplace_path: Path,
    report: PipelineValidationReport,
) -> None:
    """Validate documentation completeness.

    Checks:
    - README.md exists (3 pts, MINOR)
    - README.md contains architecture diagram (mermaid or code block) (4 pts, MINOR)
    - README.md has installation instructions (3 pts, MINOR)
    """
    category = "documentation"
    readme_path = marketplace_path / "README.md"

    # Check 1: README.md exists (3 pts, MINOR)
    if not readme_path.exists():
        report.minor(
            category,
            "README.md not found",
            3.0,
            str(readme_path),
            "Create README.md with marketplace documentation",
        )
        # Can't check other items
        report.minor(category, "Cannot check for architecture diagram - no README", 4.0)
        report.minor(category, "Cannot check installation instructions - no README", 3.0)
        return

    report.passed(category, "README.md exists", 3.0, str(readme_path))

    # Read README content
    readme_content = readme_path.read_text()

    # Check 2: Architecture diagram (4 pts, MINOR)
    has_mermaid = "```mermaid" in readme_content
    has_flowchart = re.search(
        r"```[^\n]*\n.*(?:graph|flowchart|sequenceDiagram)", readme_content, re.IGNORECASE | re.DOTALL
    )
    has_diagram_image = re.search(r"!\[.*(?:diagram|architecture|flow).*\]", readme_content, re.IGNORECASE)

    if has_mermaid or has_flowchart or has_diagram_image:
        report.passed(
            category,
            "README.md contains architecture/flow diagram",
            4.0,
            str(readme_path),
        )
    else:
        report.minor(
            category,
            "README.md missing architecture diagram",
            4.0,
            str(readme_path),
            "Add mermaid diagram showing plugin update flow",
        )

    # Check 3: Installation instructions (3 pts, MINOR)
    has_install_heading = re.search(r"^#{1,3}\s*installation", readme_content, re.IGNORECASE | re.MULTILINE)
    has_install_content = re.search(r"(?:claude\s+plugin|marketplace\s+add|install)", readme_content, re.IGNORECASE)

    if has_install_heading or has_install_content:
        report.passed(
            category,
            "README.md has installation instructions",
            3.0,
            str(readme_path),
        )
    else:
        report.minor(
            category,
            "README.md missing installation instructions",
            3.0,
            str(readme_path),
            "Add Installation section with 'claude plugin marketplace add' commands",
        )


# =============================================================================
# Main Validation
# =============================================================================


def validate_marketplace_pipeline(
    marketplace_path: Path,
    _verbose: bool = False,
) -> PipelineValidationReport:
    """Run all pipeline validation checks.

    Args:
        marketplace_path: Path to marketplace root directory
        _verbose: Reserved for future use (currently unused)

    Returns:
        Complete validation report
    """
    report = PipelineValidationReport(marketplace_path=marketplace_path)

    # Run all category validations
    validate_marketplace_structure(marketplace_path, report)
    validate_submodule_health(marketplace_path, report)
    validate_marketplace_workflows(marketplace_path, report)
    validate_plugin_workflows(marketplace_path, report)
    validate_sync_scripts(marketplace_path, report)
    validate_documentation(marketplace_path, report)

    return report


# =============================================================================
# Output Formatting
# =============================================================================


def format_text_report(report: PipelineValidationReport, verbose: bool = False) -> str:
    """Format the report as human-readable text.

    Args:
        report: Validation report
        verbose: Include all details including PASSED results

    Returns:
        Formatted text report
    """
    lines = []
    lines.append("=" * 70)
    lines.append("MARKETPLACE PIPELINE VALIDATION REPORT")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"Marketplace: {report.marketplace_name or 'Unknown'}")
    lines.append(f"Path: {report.marketplace_path}")
    lines.append(f"Plugins found: {len(report.plugins_found)}")
    lines.append(f"Submodules found: {len(report.submodules_found)}")
    lines.append("")

    # Overall score
    lines.append("-" * 70)
    lines.append(f"OVERALL SCORE: {report.total_score:.1f}/100 (Grade: {report.grade})")
    lines.append(f"Status: {report.grade_description}")
    lines.append("-" * 70)
    lines.append("")

    # Category breakdown
    lines.append("CATEGORY BREAKDOWN:")
    lines.append("")
    for name, cat in report.categories.items():
        status_icon = "[OK]" if cat.percentage >= 90 else "[!!]" if cat.percentage < 70 else "[!]"
        lines.append(
            f"  {status_icon} {name.replace('_', ' ').title()}: "
            f"{cat.points_earned:.1f}/{cat.points_possible:.1f} ({cat.percentage:.0f}%) "
            f"[weight: {cat.weight}%]"
        )
    lines.append("")

    # Detailed results by category
    for name, cat in report.categories.items():
        # Filter results based on verbosity
        issues = [r for r in cat.results if r.level not in ("PASSED", "INFO")]
        passed = [r for r in cat.results if r.level == "PASSED"]

        if not issues and not verbose:
            continue

        lines.append("-" * 70)
        lines.append(f"{name.replace('_', ' ').upper()}")
        lines.append("-" * 70)

        if issues:
            for result in issues:
                icon = {"CRITICAL": "[X]", "MAJOR": "[!]", "MINOR": "[~]"}.get(result.level, "[-]")
                lines.append(f"  {icon} {result.level}: {result.message}")
                if result.file_path:
                    lines.append(f"      File: {result.file_path}")
                if result.suggestion:
                    lines.append(f"      Fix: {result.suggestion}")

        if verbose and passed:
            for result in passed:
                lines.append(f"  [OK] {result.message}")

        lines.append("")

    # Summary
    lines.append("=" * 70)
    total_critical = sum(1 for cat in report.categories.values() for r in cat.results if r.level == "CRITICAL")
    total_major = sum(1 for cat in report.categories.values() for r in cat.results if r.level == "MAJOR")
    total_minor = sum(1 for cat in report.categories.values() for r in cat.results if r.level == "MINOR")
    total_passed = sum(1 for cat in report.categories.values() for r in cat.results if r.level == "PASSED")

    lines.append(f"SUMMARY: {total_critical} CRITICAL, {total_major} MAJOR, {total_minor} MINOR, {total_passed} PASSED")
    lines.append("=" * 70)

    return "\n".join(lines)


# =============================================================================
# CLI Entry Point
# =============================================================================


def main() -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Validate marketplace publishing pipeline automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/marketplace
  %(prog)s /path/to/marketplace --verbose
  %(prog)s /path/to/marketplace --json

Exit Codes:
  0 - Score >= 90 (A grade) - Pipeline fully operational
  1 - Score >= 70 (B/C grade) - Minor gaps, mostly functional
  2 - Score >= 60 (D grade) - Manual updates required
  3 - Score < 60 (F grade) - Pipeline broken
        """,
    )
    parser.add_argument(
        "marketplace_path",
        type=Path,
        help="Path to marketplace root directory",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show all results including passed checks",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument("--strict", action="store_true", help="Strict mode — NIT issues also block validation")

    args = parser.parse_args()

    # Resolve to absolute path so relative_to() works correctly
    marketplace_path = args.marketplace_path.resolve()

    # Validate path exists
    if not marketplace_path.exists():
        print(f"Error: Path does not exist: {marketplace_path}", file=sys.stderr)
        return EXIT_MINOR

    if not marketplace_path.is_dir():
        print(f"Error: Path is not a directory: {marketplace_path}", file=sys.stderr)
        return EXIT_MINOR

    # Verify content type — marketplace directory must contain marketplace.json
    if not (marketplace_path / "marketplace.json").exists():
        print(
            f"Error: No marketplace.json found at {marketplace_path}\n"
            f"Expected a marketplace directory with marketplace.json.",
            file=sys.stderr,
        )
        return EXIT_MINOR

    # Run validation
    report = validate_marketplace_pipeline(marketplace_path, _verbose=args.verbose)

    # Output results
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(format_text_report(report, verbose=args.verbose))

    return report.exit_code()


if __name__ == "__main__":
    sys.exit(main())
