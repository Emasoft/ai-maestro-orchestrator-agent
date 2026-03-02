#!/usr/bin/env python3
"""
Claude Plugins Validation - Enterprise Compliance Validator

Validates enterprise and compliance requirements for Claude Code plugins.
Checks skills and agents for required metadata, licensing, and authorship.

This validator implements 9 compliance rules:
1. Required skill metadata: name, description, author, license
2. Skills must have context: fork field (valid value)
3. Skills agent field validation: api-coordinator, test-engineer, deploy-agent, debug-specialist, code-reviewer
4. user-invocable: true/false must be boolean
5. Author field is REQUIRED for enterprise compliance
6. License field is REQUIRED for enterprise compliance (SPDX identifier)
7. Tags array is RECOMMENDED (warn if missing)
8. Mode field validation: read, write, read-write
9. Check all skills and agents for compliance metadata

Usage:
    uv run python scripts/validate_enterprise.py path/to/plugin/
    uv run python scripts/validate_enterprise.py path/to/plugin/ --verbose
    uv run python scripts/validate_enterprise.py path/to/plugin/ --json
    uv run python scripts/validate_enterprise.py path/to/plugin/ --strict

Exit codes:
    0 - All checks passed
    1 - CRITICAL issues found
    2 - MAJOR issues found
    3 - MINOR issues found
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from cpv_validation_common import (
    BUILTIN_AGENT_TYPES,
    EXIT_CRITICAL,
    EXIT_MAJOR,
    EXIT_OK,
    VALID_CONTEXT_VALUES,
    Level,
    ValidationReport,
    ValidationResult,
    calculate_letter_grade,
)

# =============================================================================
# Enterprise Compliance Constants
# =============================================================================

# Valid values for agent field in enterprise context
# These are the specialized agent types for enterprise workflows
VALID_ENTERPRISE_AGENT_TYPES = {
    "api-coordinator",
    "test-engineer",
    "deploy-agent",
    "debug-specialist",
    "code-reviewer",
}

# All valid agent types (enterprise + built-in)
ALL_VALID_AGENT_TYPES = VALID_ENTERPRISE_AGENT_TYPES | BUILTIN_AGENT_TYPES

# Valid values for mode field
VALID_MODE_VALUES = {"read", "write", "read-write"}

# Common SPDX license identifiers for validation
# Full list: https://spdx.org/licenses/
COMMON_SPDX_LICENSES = {
    "MIT",
    "Apache-2.0",
    "GPL-2.0",
    "GPL-2.0-only",
    "GPL-2.0-or-later",
    "GPL-3.0",
    "GPL-3.0-only",
    "GPL-3.0-or-later",
    "LGPL-2.1",
    "LGPL-2.1-only",
    "LGPL-2.1-or-later",
    "LGPL-3.0",
    "LGPL-3.0-only",
    "LGPL-3.0-or-later",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "ISC",
    "MPL-2.0",
    "AGPL-3.0",
    "AGPL-3.0-only",
    "AGPL-3.0-or-later",
    "Unlicense",
    "CC0-1.0",
    "CC-BY-4.0",
    "CC-BY-SA-4.0",
    "WTFPL",
    "Zlib",
    "BSL-1.0",
    "EPL-2.0",
    "EUPL-1.2",
    "Proprietary",
    "UNLICENSED",
}

# Required fields for enterprise compliance
ENTERPRISE_REQUIRED_FIELDS = {"name", "description", "author", "license"}

# Recommended fields for enterprise compliance
ENTERPRISE_RECOMMENDED_FIELDS = {"tags", "version"}

# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class SkillComplianceResult:
    """Result of compliance check for a single skill."""

    skill_path: str
    skill_name: str
    is_compliant: bool
    missing_required: list[str] = field(default_factory=list)
    missing_recommended: list[str] = field(default_factory=list)
    invalid_fields: list[str] = field(default_factory=list)
    results: list[ValidationResult] = field(default_factory=list)


@dataclass
class AgentComplianceResult:
    """Result of compliance check for a single agent."""

    agent_path: str
    agent_name: str
    is_compliant: bool
    missing_required: list[str] = field(default_factory=list)
    results: list[ValidationResult] = field(default_factory=list)


@dataclass
class EnterpriseComplianceReport(ValidationReport):
    """Complete enterprise compliance validation report.

    Extends ValidationReport with enterprise-specific tracking:
    - Plugin path being validated
    - Skill compliance results
    - Agent compliance results
    - Strict mode flag
    - Overall compliance status
    """

    plugin_path: str = ""
    strict_mode: bool = False
    skill_results: list[SkillComplianceResult] = field(default_factory=list)
    agent_results: list[AgentComplianceResult] = field(default_factory=list)
    total_skills: int = 0
    compliant_skills: int = 0
    total_agents: int = 0
    compliant_agents: int = 0

    @property
    def overall_compliance(self) -> bool:
        """Check if plugin is fully compliant."""
        return not self.has_critical and not self.has_major

    @property
    def compliance_percentage(self) -> float:
        """Calculate compliance percentage across skills and agents."""
        total = self.total_skills + self.total_agents
        if total == 0:
            return 100.0
        compliant = self.compliant_skills + self.compliant_agents
        return (compliant / total) * 100

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary for JSON serialization."""
        base = super().to_dict()
        base.update(
            {
                "plugin_path": self.plugin_path,
                "strict_mode": self.strict_mode,
                "overall_compliance": self.overall_compliance,
                "compliance_percentage": round(self.compliance_percentage, 1),
                "total_skills": self.total_skills,
                "compliant_skills": self.compliant_skills,
                "total_agents": self.total_agents,
                "compliant_agents": self.compliant_agents,
                "skill_results": [
                    {
                        "skill_path": sr.skill_path,
                        "skill_name": sr.skill_name,
                        "is_compliant": sr.is_compliant,
                        "missing_required": sr.missing_required,
                        "missing_recommended": sr.missing_recommended,
                        "invalid_fields": sr.invalid_fields,
                    }
                    for sr in self.skill_results
                ],
                "agent_results": [
                    {
                        "agent_path": ar.agent_path,
                        "agent_name": ar.agent_name,
                        "is_compliant": ar.is_compliant,
                        "missing_required": ar.missing_required,
                    }
                    for ar in self.agent_results
                ],
            }
        )
        return base


# =============================================================================
# Frontmatter Parsing
# =============================================================================


def parse_frontmatter(content: str) -> tuple[dict[str, Any] | None, str]:
    """Parse YAML frontmatter from markdown content.

    Returns:
        Tuple of (frontmatter_dict, body_content)
        Returns (None, content) if no frontmatter found
    """
    if not content.startswith("---"):
        return None, content

    # Find closing ---
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, content

    try:
        frontmatter = yaml.safe_load(parts[1])
        if frontmatter is None:
            frontmatter = {}
        body = parts[2]
        return frontmatter, body
    except yaml.YAMLError:
        return None, content


# =============================================================================
# Skill Compliance Validation
# =============================================================================


def validate_skill_compliance(
    skill_path: Path,
    report: EnterpriseComplianceReport,
) -> SkillComplianceResult:
    """Validate enterprise compliance for a single skill.

    Implements rules 1-8 for skill validation:
    1. Required skill metadata: name, description, author, license
    2. context: fork field validation
    3. agent field validation
    4. user-invocable boolean validation
    5. Author field requirement
    6. License field requirement (SPDX)
    7. Tags array recommendation
    8. Mode field validation
    """
    skill_name = skill_path.name
    skill_md = skill_path / "SKILL.md"
    location = f"skills/{skill_name}/SKILL.md"

    result = SkillComplianceResult(
        skill_path=str(skill_path),
        skill_name=skill_name,
        is_compliant=True,
    )

    # Check SKILL.md exists
    if not skill_md.exists():
        level: Level = "CRITICAL" if report.strict_mode else "MAJOR"
        report.add(level, "SKILL.md not found", location)
        result.is_compliant = False
        result.missing_required.append("SKILL.md")
        return result

    # Read and parse content
    try:
        content = skill_md.read_text(encoding="utf-8")
    except Exception as e:
        report.critical(f"Failed to read SKILL.md: {e}", location)
        result.is_compliant = False
        return result

    # Parse frontmatter
    frontmatter, _body = parse_frontmatter(content)

    if frontmatter is None:
        level = "CRITICAL" if report.strict_mode else "MAJOR"
        report.add(level, "No YAML frontmatter found (required for enterprise compliance)", location)
        result.is_compliant = False
        result.missing_required.extend(list(ENTERPRISE_REQUIRED_FIELDS))
        return result

    # Rule 1: Required skill metadata (name, description)
    validate_required_metadata(frontmatter, location, report, result)

    # Rule 5: Author field (REQUIRED for enterprise)
    validate_author_field(frontmatter, location, report, result)

    # Rule 6: License field (REQUIRED for enterprise, SPDX identifier)
    validate_license_field(frontmatter, location, report, result)

    # Rule 2: context: fork field validation
    validate_context_field(frontmatter, location, report, result)

    # Rule 3: agent field validation
    validate_agent_field(frontmatter, location, report, result)

    # Rule 4: user-invocable boolean validation
    validate_user_invocable_field(frontmatter, location, report, result)

    # Rule 7: Tags array (RECOMMENDED)
    validate_tags_field(frontmatter, location, report, result)

    # Rule 8: Mode field validation
    validate_mode_field(frontmatter, location, report, result)

    # Determine compliance status
    result.is_compliant = len(result.missing_required) == 0 and len(result.invalid_fields) == 0

    return result


def validate_required_metadata(
    frontmatter: dict[str, Any],
    location: str,
    report: EnterpriseComplianceReport,
    result: SkillComplianceResult,
) -> None:
    """Validate required metadata fields: name, description."""
    # Check name field
    if "name" not in frontmatter:
        level: Level = "CRITICAL" if report.strict_mode else "MAJOR"
        report.add(level, "Missing required field: 'name'", location)
        result.missing_required.append("name")
    elif not isinstance(frontmatter["name"], str):
        level = "CRITICAL" if report.strict_mode else "MAJOR"
        report.add(level, f"'name' must be a string, got {type(frontmatter['name']).__name__}", location)
        result.invalid_fields.append("name")
    elif not frontmatter["name"].strip():
        level = "CRITICAL" if report.strict_mode else "MAJOR"
        report.add(level, "'name' cannot be empty", location)
        result.invalid_fields.append("name")
    else:
        report.passed(f"'name' field present: {frontmatter['name']}", location)

    # Check description field
    if "description" not in frontmatter:
        level = "CRITICAL" if report.strict_mode else "MAJOR"
        report.add(level, "Missing required field: 'description'", location)
        result.missing_required.append("description")
    elif not isinstance(frontmatter["description"], str):
        level = "CRITICAL" if report.strict_mode else "MAJOR"
        report.add(level, f"'description' must be a string, got {type(frontmatter['description']).__name__}", location)
        result.invalid_fields.append("description")
    elif not frontmatter["description"].strip():
        level = "CRITICAL" if report.strict_mode else "MAJOR"
        report.add(level, "'description' cannot be empty", location)
        result.invalid_fields.append("description")
    else:
        report.passed("'description' field present", location)


def validate_author_field(
    frontmatter: dict[str, Any],
    location: str,
    report: EnterpriseComplianceReport,
    result: SkillComplianceResult,
) -> None:
    """Rule 5: Validate author field (REQUIRED for enterprise compliance)."""
    if "author" not in frontmatter:
        level: Level = "CRITICAL" if report.strict_mode else "MAJOR"
        report.add(level, "Missing required field: 'author' (enterprise compliance requirement)", location)
        result.missing_required.append("author")
        return

    author = frontmatter["author"]

    # Author can be a string or an object with name/email
    if isinstance(author, str):
        if not author.strip():
            level = "CRITICAL" if report.strict_mode else "MAJOR"
            report.add(level, "'author' cannot be empty", location)
            result.invalid_fields.append("author")
        else:
            report.passed(f"'author' field present: {author}", location)
    elif isinstance(author, dict):
        # Validate author object structure
        if "name" not in author:
            level = "CRITICAL" if report.strict_mode else "MAJOR"
            report.add(level, "'author' object must have 'name' field", location)
            result.invalid_fields.append("author")
        else:
            author_name = author.get("name", "")
            author_email = author.get("email", "")
            author_str = author_name
            if author_email:
                author_str += f" <{author_email}>"
            report.passed(f"'author' field present: {author_str}", location)
    else:
        level = "CRITICAL" if report.strict_mode else "MAJOR"
        report.add(level, f"'author' must be a string or object, got {type(author).__name__}", location)
        result.invalid_fields.append("author")


def validate_license_field(
    frontmatter: dict[str, Any],
    location: str,
    report: EnterpriseComplianceReport,
    result: SkillComplianceResult,
) -> None:
    """Rule 6: Validate license field (REQUIRED for enterprise, SPDX identifier)."""
    if "license" not in frontmatter:
        level: Level = "CRITICAL" if report.strict_mode else "MAJOR"
        report.add(level, "Missing required field: 'license' (enterprise compliance requirement)", location)
        result.missing_required.append("license")
        return

    license_value = frontmatter["license"]

    if not isinstance(license_value, str):
        level = "CRITICAL" if report.strict_mode else "MAJOR"
        report.add(level, f"'license' must be a string (SPDX identifier), got {type(license_value).__name__}", location)
        result.invalid_fields.append("license")
        return

    if not license_value.strip():
        level = "CRITICAL" if report.strict_mode else "MAJOR"
        report.add(level, "'license' cannot be empty", location)
        result.invalid_fields.append("license")
        return

    # Check if it's a known SPDX identifier
    if license_value in COMMON_SPDX_LICENSES:
        report.passed(f"'license' field present (valid SPDX): {license_value}", location)
    else:
        # Not a known SPDX identifier, but might be valid - just warn
        report.minor(
            f"'license' value '{license_value}' is not a common SPDX identifier. "
            "See https://spdx.org/licenses/ for valid identifiers.",
            location,
        )


def validate_context_field(
    frontmatter: dict[str, Any],
    location: str,
    report: EnterpriseComplianceReport,
    result: SkillComplianceResult,
) -> None:
    """Rule 2: Validate context: fork field."""
    if "context" not in frontmatter:
        # Context is optional
        report.info("No 'context' field (skill runs in main context)", location)
        return

    context = frontmatter["context"]

    if not isinstance(context, str):
        level: Level = "CRITICAL" if report.strict_mode else "MAJOR"
        report.add(level, f"'context' must be a string, got {type(context).__name__}", location)
        result.invalid_fields.append("context")
        return

    if context not in VALID_CONTEXT_VALUES:
        level = "CRITICAL" if report.strict_mode else "MAJOR"
        report.add(level, f"Invalid 'context' value: '{context}'. Valid values: {VALID_CONTEXT_VALUES}", location)
        result.invalid_fields.append("context")
        return

    report.passed(f"'context' field valid: {context}", location)


def validate_agent_field(
    frontmatter: dict[str, Any],
    location: str,
    report: EnterpriseComplianceReport,
    result: SkillComplianceResult,
) -> None:
    """Rule 3: Validate agent field for enterprise agent types."""
    if "agent" not in frontmatter:
        # Agent is only relevant if context: fork is set
        if frontmatter.get("context") == "fork":
            report.info("No 'agent' field with context: fork (defaults to general-purpose)", location)
        return

    agent = frontmatter["agent"]

    if not isinstance(agent, str):
        level: Level = "CRITICAL" if report.strict_mode else "MAJOR"
        report.add(level, f"'agent' must be a string, got {type(agent).__name__}", location)
        result.invalid_fields.append("agent")
        return

    # Check if context: fork is set (required for agent to have effect)
    if frontmatter.get("context") != "fork":
        report.major("'agent' field has no effect without 'context: fork'", location)

    # Validate against known types
    if agent in ALL_VALID_AGENT_TYPES:
        if agent in VALID_ENTERPRISE_AGENT_TYPES:
            report.passed(f"'agent' field valid (enterprise type): {agent}", location)
        else:
            report.passed(f"'agent' field valid (built-in type): {agent}", location)
    else:
        # Could be a custom agent - warn in strict mode
        if report.strict_mode:
            report.minor(
                f"'agent' value '{agent}' is not a known type. "
                f"Enterprise types: {VALID_ENTERPRISE_AGENT_TYPES}. "
                f"Built-in types: {BUILTIN_AGENT_TYPES}",
                location,
            )
        else:
            report.info(f"'agent' value '{agent}' may be a custom agent from .claude/agents/", location)


def validate_user_invocable_field(
    frontmatter: dict[str, Any],
    location: str,
    report: EnterpriseComplianceReport,
    result: SkillComplianceResult,
) -> None:
    """Rule 4: Validate user-invocable field is boolean."""
    if "user-invocable" not in frontmatter:
        return

    value = frontmatter["user-invocable"]

    if not isinstance(value, bool):
        level: Level = "CRITICAL" if report.strict_mode else "MAJOR"
        report.add(level, f"'user-invocable' must be a boolean (true/false), got {type(value).__name__}", location)
        result.invalid_fields.append("user-invocable")
        return

    report.passed(f"'user-invocable' field valid: {value}", location)


def validate_tags_field(
    frontmatter: dict[str, Any],
    location: str,
    report: EnterpriseComplianceReport,
    result: SkillComplianceResult,
) -> None:
    """Rule 7: Validate tags array (RECOMMENDED)."""
    if "tags" not in frontmatter:
        # Tags are recommended but not required
        report.minor("Missing recommended field: 'tags' (helps with skill discovery)", location)
        result.missing_recommended.append("tags")
        return

    tags = frontmatter["tags"]

    if not isinstance(tags, list):
        report.minor(f"'tags' should be an array, got {type(tags).__name__}", location)
        result.invalid_fields.append("tags")
        return

    if len(tags) == 0:
        report.minor("'tags' array is empty (add tags for better skill discovery)", location)
        return

    # Validate each tag is a string
    invalid_tags = [t for t in tags if not isinstance(t, str)]
    if invalid_tags:
        report.minor(f"'tags' array contains non-string values: {invalid_tags}", location)
        return

    report.passed(f"'tags' field valid: {len(tags)} tag(s)", location)


def validate_mode_field(
    frontmatter: dict[str, Any],
    location: str,
    report: EnterpriseComplianceReport,
    result: SkillComplianceResult,
) -> None:
    """Rule 8: Validate mode field."""
    if "mode" not in frontmatter:
        # Mode is optional
        return

    mode = frontmatter["mode"]

    if not isinstance(mode, str):
        level: Level = "CRITICAL" if report.strict_mode else "MAJOR"
        report.add(level, f"'mode' must be a string, got {type(mode).__name__}", location)
        result.invalid_fields.append("mode")
        return

    if mode not in VALID_MODE_VALUES:
        level = "CRITICAL" if report.strict_mode else "MAJOR"
        report.add(level, f"Invalid 'mode' value: '{mode}'. Valid values: {VALID_MODE_VALUES}", location)
        result.invalid_fields.append("mode")
        return

    report.passed(f"'mode' field valid: {mode}", location)


# =============================================================================
# Agent Compliance Validation
# =============================================================================


def validate_agent_compliance(
    agent_path: Path,
    report: EnterpriseComplianceReport,
) -> AgentComplianceResult:
    """Validate enterprise compliance for a single agent definition.

    Rule 9: Check agents for compliance metadata (name, description required).
    """
    agent_name = agent_path.stem
    location = f"agents/{agent_path.name}"

    result = AgentComplianceResult(
        agent_path=str(agent_path),
        agent_name=agent_name,
        is_compliant=True,
    )

    # Read agent file
    try:
        content = agent_path.read_text(encoding="utf-8")
    except Exception as e:
        report.critical(f"Failed to read agent file: {e}", location)
        result.is_compliant = False
        return result

    # Parse frontmatter
    frontmatter, _body = parse_frontmatter(content)

    if frontmatter is None:
        level: Level = "CRITICAL" if report.strict_mode else "MAJOR"
        report.add(level, "No YAML frontmatter found (required for agent compliance)", location)
        result.is_compliant = False
        result.missing_required.extend(["name", "description"])
        return result

    # Check required fields
    if "name" not in frontmatter:
        level = "CRITICAL" if report.strict_mode else "MAJOR"
        report.add(level, "Missing required field: 'name'", location)
        result.missing_required.append("name")
    else:
        report.passed(f"'name' field present: {frontmatter['name']}", location)

    if "description" not in frontmatter:
        level = "CRITICAL" if report.strict_mode else "MAJOR"
        report.add(level, "Missing required field: 'description'", location)
        result.missing_required.append("description")
    else:
        report.passed("'description' field present", location)

    # Determine compliance status
    result.is_compliant = len(result.missing_required) == 0

    return result


# =============================================================================
# Main Validation
# =============================================================================


def validate_enterprise_compliance(
    plugin_path: Path,
    strict: bool = False,
) -> EnterpriseComplianceReport:
    """Validate enterprise compliance for a Claude Code plugin.

    Scans all skills in skills/ directory and agents in agents/ directory,
    checking each for compliance with enterprise metadata requirements.

    Args:
        plugin_path: Path to the plugin directory
        strict: If True, all rules become CRITICAL instead of MAJOR

    Returns:
        EnterpriseComplianceReport with all validation results
    """
    report = EnterpriseComplianceReport(
        plugin_path=str(plugin_path),
        strict_mode=strict,
    )

    # Check plugin directory exists
    if not plugin_path.exists():
        report.critical(f"Plugin directory not found: {plugin_path}")
        return report

    if not plugin_path.is_dir():
        report.critical(f"Path is not a directory: {plugin_path}")
        return report

    # Find skills directory
    skills_dir = plugin_path / "skills"
    if skills_dir.exists() and skills_dir.is_dir():
        # Scan all skills
        skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
        report.total_skills = len(skill_dirs)

        for skill_dir in sorted(skill_dirs):
            skill_result = validate_skill_compliance(skill_dir, report)
            report.skill_results.append(skill_result)
            if skill_result.is_compliant:
                report.compliant_skills += 1

        if report.total_skills == 0:
            report.info("No skills found in skills/ directory")
        else:
            report.info(f"Found {report.total_skills} skill(s) in skills/ directory")
    else:
        report.info("No skills/ directory found")

    # Find agents directory
    agents_dir = plugin_path / "agents"
    if agents_dir.exists() and agents_dir.is_dir():
        # Scan all agents (*.md files)
        agent_files = list(agents_dir.glob("*.md"))
        report.total_agents = len(agent_files)

        for agent_file in sorted(agent_files):
            agent_result = validate_agent_compliance(agent_file, report)
            report.agent_results.append(agent_result)
            if agent_result.is_compliant:
                report.compliant_agents += 1

        if report.total_agents == 0:
            report.info("No agents found in agents/ directory")
        else:
            report.info(f"Found {report.total_agents} agent(s) in agents/ directory")
    else:
        report.info("No agents/ directory found")

    # Summary result
    if report.total_skills == 0 and report.total_agents == 0:
        report.minor("No skills or agents found to validate")

    return report


# =============================================================================
# Output Formatting
# =============================================================================


def print_results(report: EnterpriseComplianceReport, verbose: bool = False) -> None:
    """Print validation results in human-readable format."""
    # ANSI colors
    colors = {
        "CRITICAL": "\033[91m",  # Red
        "MAJOR": "\033[93m",  # Yellow
        "MINOR": "\033[94m",  # Blue
        "INFO": "\033[90m",  # Gray
        "PASSED": "\033[92m",  # Green
        "RESET": "\033[0m",
        "BOLD": "\033[1m",
    }

    # Count by level
    counts = report.count_by_level()

    # Print header
    print("\n" + "=" * 70)
    print(f"{colors['BOLD']}Enterprise Compliance Validation{colors['RESET']}")
    print(f"Plugin: {report.plugin_path}")
    if report.strict_mode:
        print(f"{colors['MAJOR']}Mode: STRICT (all rules are CRITICAL){colors['RESET']}")
    print("=" * 70)

    # Print compliance summary
    print(f"\n{colors['BOLD']}Compliance Summary:{colors['RESET']}")
    print(f"  Skills:  {report.compliant_skills}/{report.total_skills} compliant")
    print(f"  Agents:  {report.compliant_agents}/{report.total_agents} compliant")
    print(f"  Overall: {report.compliance_percentage:.1f}%")

    # Print issue counts
    print(f"\n{colors['BOLD']}Issue Summary:{colors['RESET']}")
    print(f"  {colors['CRITICAL']}CRITICAL: {counts['CRITICAL']}{colors['RESET']}")
    print(f"  {colors['MAJOR']}MAJOR:    {counts['MAJOR']}{colors['RESET']}")
    print(f"  {colors['MINOR']}MINOR:    {counts['MINOR']}{colors['RESET']}")
    if verbose:
        print(f"  {colors['INFO']}INFO:     {counts['INFO']}{colors['RESET']}")
        print(f"  {colors['PASSED']}PASSED:   {counts['PASSED']}{colors['RESET']}")

    # Print skill results summary
    if report.skill_results:
        print(f"\n{colors['BOLD']}Skill Compliance:{colors['RESET']}")
        for sr in report.skill_results:
            status_color = colors["PASSED"] if sr.is_compliant else colors["MAJOR"]
            status_icon = "OK" if sr.is_compliant else "X"
            print(f"  {status_color}[{status_icon}]{colors['RESET']} {sr.skill_name}")
            if not sr.is_compliant and (sr.missing_required or sr.invalid_fields):
                if sr.missing_required:
                    print(f"      Missing: {', '.join(sr.missing_required)}")
                if sr.invalid_fields:
                    print(f"      Invalid: {', '.join(sr.invalid_fields)}")

    # Print agent results summary
    if report.agent_results:
        print(f"\n{colors['BOLD']}Agent Compliance:{colors['RESET']}")
        for ar in report.agent_results:
            status_color = colors["PASSED"] if ar.is_compliant else colors["MAJOR"]
            status_icon = "OK" if ar.is_compliant else "X"
            print(f"  {status_color}[{status_icon}]{colors['RESET']} {ar.agent_name}")
            if not ar.is_compliant and ar.missing_required:
                print(f"      Missing: {', '.join(ar.missing_required)}")

    # Print detailed results
    if verbose:
        print(f"\n{colors['BOLD']}Detailed Results:{colors['RESET']}")
        for r in report.results:
            color = colors[r.level]
            reset = colors["RESET"]
            file_info = f" ({r.file})" if r.file else ""
            line_info = f":{r.line}" if r.line else ""
            print(f"  {color}[{r.level}]{reset} {r.message}{file_info}{line_info}")

    # Print final status
    print("\n" + "-" * 70)
    if report.exit_code == EXIT_OK:
        print(f"{colors['PASSED']}SUCCESS: All enterprise compliance checks passed{colors['RESET']}")
    elif report.exit_code == EXIT_CRITICAL:
        crit = colors["CRITICAL"]
        rst = colors["RESET"]
        print(f"{crit}FAILED: CRITICAL compliance issues found{rst}")
    elif report.exit_code == EXIT_MAJOR:
        maj = colors["MAJOR"]
        rst = colors["RESET"]
        print(f"{maj}WARNING: MAJOR compliance issues found{rst}")
    else:
        minor = colors["MINOR"]
        rst = colors["RESET"]
        print(f"{minor}NOTICE: Minor compliance issues found{rst}")

    print(f"\nScore: {report.score}/100 ({calculate_letter_grade(report.score)})")
    print()


def print_json(report: EnterpriseComplianceReport) -> None:
    """Print validation results as JSON."""
    print(json.dumps(report.to_dict(), indent=2))


# =============================================================================
# CLI Entry Point
# =============================================================================


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate enterprise compliance for Claude Code plugins",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Rules validated:
  1. Required skill metadata: name, description, author, license
  2. Skills must have context: fork field (valid value)
  3. Skills agent field: api-coordinator, test-engineer, deploy-agent, debug-specialist, code-reviewer
  4. user-invocable: true/false must be boolean
  5. Author field is REQUIRED for enterprise compliance
  6. License field is REQUIRED for enterprise compliance (SPDX identifier)
  7. Tags array is RECOMMENDED (warn if missing)
  8. Mode field validation: read, write, read-write
  9. Check all skills and agents for compliance metadata

Exit codes:
  0 - All checks passed
  1 - CRITICAL issues found
  2 - MAJOR issues found
  3 - MINOR issues found
""",
    )
    parser.add_argument("plugin_path", help="Path to the plugin directory")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show all results including passed checks and info messages",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enterprise mode: all rules become CRITICAL (fail-fast)",
    )
    args = parser.parse_args()

    plugin_path = Path(args.plugin_path).resolve()

    if not plugin_path.exists():
        print(f"Error: {plugin_path} does not exist", file=sys.stderr)
        return EXIT_CRITICAL

    if not plugin_path.is_dir():
        print(f"Error: {plugin_path} is not a directory", file=sys.stderr)
        return EXIT_CRITICAL

    # Verify this is a plugin directory
    if not (plugin_path / ".claude-plugin").is_dir():
        print(
            f"Error: No Claude Code plugin found at {plugin_path}\nExpected a .claude-plugin/ directory.",
            file=sys.stderr,
        )
        return EXIT_CRITICAL

    report = validate_enterprise_compliance(plugin_path, strict=args.strict)

    if args.json:
        print_json(report)
    else:
        print_results(report, args.verbose)

    return report.exit_code


if __name__ == "__main__":
    sys.exit(main())
