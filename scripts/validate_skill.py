#!/usr/bin/env python3
"""
Claude Plugins Validation - Skill Validator

Validates individual skill directories according to Claude Code skill spec.
Based on: https://code.claude.com/docs/en/skills.md

Usage:
    uv run python scripts/validate_skill.py path/to/skill/
    uv run python scripts/validate_skill.py path/to/skill/ --verbose
    uv run python scripts/validate_skill.py path/to/skill/ --json

Exit codes:
    0 - All checks passed
    1 - CRITICAL issues found (skill will not work)
    2 - MAJOR issues found (significant problems)
    3 - MINOR issues found (may affect UX)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from cpv_validation_common import BUILTIN_AGENT_TYPES, VALID_CONTEXT_VALUES, ValidationReport

# Maximum recommended SKILL.md line count per Anthropic docs
MAX_SKILL_LINES = 500

# Known frontmatter fields per official docs
KNOWN_FRONTMATTER_FIELDS = {
    "name",
    "description",
    "argument-hint",
    "disable-model-invocation",
    "user-invocable",
    "allowed-tools",
    "model",
    "context",
    "agent",
    "hooks",
}


@dataclass
class SkillValidationReport(ValidationReport):
    """Skill validation report with skill-specific metadata."""

    skill_path: str = ""


def validate_skill_md_exists(skill_path: Path, report: ValidationReport) -> bool:
    """Validate SKILL.md exists (required)."""
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        report.critical("SKILL.md not found (required)", "SKILL.md")
        return False

    report.passed("SKILL.md exists", "SKILL.md")
    return True


def parse_frontmatter(content: str) -> tuple[dict[str, Any] | None, str, int]:
    """Parse YAML frontmatter from skill content.

    Returns:
        Tuple of (frontmatter_dict, body_content, frontmatter_end_line)
        Returns (None, content, 0) if no frontmatter found
    """
    if not content.startswith("---"):
        return None, content, 0

    # Find closing ---
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, content, 0

    try:
        frontmatter = yaml.safe_load(parts[1])
        if frontmatter is None:
            frontmatter = {}
        body = parts[2]
        # Count lines to find frontmatter end
        fm_end_line = parts[0].count("\n") + parts[1].count("\n") + 2
        return frontmatter, body, fm_end_line
    except yaml.YAMLError:
        return None, content, 0


def validate_frontmatter(skill_path: Path, content: str, report: ValidationReport) -> dict[str, Any] | None:
    """Validate YAML frontmatter structure and content."""
    # Check frontmatter exists
    if not content.startswith("---"):
        report.info("No YAML frontmatter found (optional but recommended)", "SKILL.md")
        return None

    # Parse frontmatter
    frontmatter, _body, _fm_end_line = parse_frontmatter(content)

    if frontmatter is None and content.startswith("---"):
        # Started with --- but failed to parse
        report.critical(
            "Malformed YAML frontmatter (missing closing --- or invalid YAML)",
            "SKILL.md",
        )
        return None

    if frontmatter is None:
        return None

    report.passed("Valid YAML frontmatter", "SKILL.md")

    # Validate known fields
    for key in frontmatter.keys():
        if key not in KNOWN_FRONTMATTER_FIELDS:
            report.warning(
                f"Unknown frontmatter field '{key}' (may be ignored by CLI)",
                "SKILL.md",
            )

    return frontmatter


def validate_name_field(frontmatter: dict[str, Any], skill_dir_name: str, report: ValidationReport) -> None:
    """Validate the 'name' frontmatter field."""
    if "name" not in frontmatter:
        report.info(
            f"No 'name' field (will use directory name: {skill_dir_name})",
            "SKILL.md",
        )
        # Validate directory name as implicit skill name
        name = skill_dir_name
    else:
        name = frontmatter["name"]
        report.passed(f"'name' field present: {name}", "SKILL.md")

    # Validate name format per docs:
    # "Lowercase letters, numbers, and hyphens only (max 64 characters)"
    if not isinstance(name, str):
        report.critical(f"'name' must be a string, got {type(name).__name__}", "SKILL.md")
        return

    if len(name) > 64:
        report.major(
            f"Skill name exceeds 64 characters ({len(name)} chars): {name}",
            "SKILL.md",
        )

    if name != name.lower():
        report.major(f"Skill name must be lowercase: {name}", "SKILL.md")

    if not re.match(r"^[a-z][a-z0-9-]*$", name):
        report.major(
            f"Skill name must use only lowercase letters, numbers, hyphens: {name}",
            "SKILL.md",
        )

    # Check name matches directory name (recommended)
    if "name" in frontmatter and name != skill_dir_name:
        report.info(
            f"Skill name '{name}' differs from directory name '{skill_dir_name}'",
            "SKILL.md",
        )


def validate_description_field(frontmatter: dict[str, Any], body: str, report: ValidationReport) -> None:
    """Validate the 'description' frontmatter field."""
    if "description" not in frontmatter:
        # Check if body has content that could serve as description
        if body.strip():
            report.info(
                "No 'description' field (will use first paragraph of content)",
                "SKILL.md",
            )
        else:
            report.major(
                "No 'description' field and no body content for fallback",
                "SKILL.md",
            )
        return

    desc = frontmatter["description"]
    if not isinstance(desc, str):
        report.major(
            f"'description' must be a string, got {type(desc).__name__}",
            "SKILL.md",
        )
        return

    if len(desc) < 10:
        report.minor(
            "Description is very short (may not help Claude decide when to use)",
            "SKILL.md",
        )

    if len(desc) > 500:
        report.minor(
            f"Description is long ({len(desc)} chars), consider shortening",
            "SKILL.md",
        )

    report.passed("'description' field present", "SKILL.md")


def validate_context_field(frontmatter: dict[str, Any], report: ValidationReport) -> None:
    """Validate the 'context' frontmatter field."""
    if "context" not in frontmatter:
        return

    context = frontmatter["context"]

    if not isinstance(context, str):
        report.critical(
            f"'context' must be a string, got {type(context).__name__}",
            "SKILL.md",
        )
        return

    if context not in VALID_CONTEXT_VALUES:
        report.critical(
            f"Invalid 'context' value: '{context}'. Valid values: {VALID_CONTEXT_VALUES}",
            "SKILL.md",
        )
        return

    report.passed(f"'context' field valid: {context}", "SKILL.md")


def validate_agent_field(frontmatter: dict[str, Any], report: ValidationReport) -> None:
    """Validate the 'agent' frontmatter field."""
    if "agent" not in frontmatter:
        # Agent is only relevant if context: fork is set
        if frontmatter.get("context") == "fork":
            report.info(
                "'agent' not specified with context: fork (defaults to general-purpose)",
                "SKILL.md",
            )
        return

    agent = frontmatter["agent"]

    if not isinstance(agent, str):
        report.critical(
            f"'agent' must be a string, got {type(agent).__name__}",
            "SKILL.md",
        )
        return

    # Check if context: fork is set (required for agent to have effect)
    if frontmatter.get("context") != "fork":
        report.major(
            "'agent' field has no effect without 'context: fork'",
            "SKILL.md",
        )

    # Validate against known built-in types
    if agent in BUILTIN_AGENT_TYPES:
        report.passed(f"'agent' field valid (built-in): {agent}", "SKILL.md")
    else:
        # Could be a custom agent from .claude/agents/
        report.info(
            f"'agent' value '{agent}' is not a built-in type (may be custom from .claude/agents/)",
            "SKILL.md",
        )


def validate_boolean_field(
    frontmatter: dict[str, Any],
    field_name: str,
    report: ValidationReport,
) -> None:
    """Validate a boolean frontmatter field."""
    if field_name not in frontmatter:
        return

    value = frontmatter[field_name]

    if not isinstance(value, bool):
        report.critical(
            f"'{field_name}' must be a boolean (true/false), got {type(value).__name__}",
            "SKILL.md",
        )
        return

    report.passed(f"'{field_name}' field valid: {value}", "SKILL.md")


def validate_allowed_tools_field(frontmatter: dict[str, Any], report: ValidationReport) -> None:
    """Validate the 'allowed-tools' frontmatter field."""
    if "allowed-tools" not in frontmatter:
        return

    tools = frontmatter["allowed-tools"]

    if isinstance(tools, str):
        # Single tool or comma-separated list
        tool_list = [t.strip() for t in tools.split(",")]
    elif isinstance(tools, list):
        tool_list = tools
    else:
        report.major(
            f"'allowed-tools' must be string or list, got {type(tools).__name__}",
            "SKILL.md",
        )
        return

    if not tool_list:
        report.minor("'allowed-tools' is empty", "SKILL.md")
        return

    report.passed(f"'allowed-tools' field valid: {len(tool_list)} tool(s)", "SKILL.md")


def validate_model_field(frontmatter: dict[str, Any], report: ValidationReport) -> None:
    """Validate the 'model' frontmatter field."""
    if "model" not in frontmatter:
        return

    model = frontmatter["model"]

    if not isinstance(model, str):
        report.major(
            f"'model' must be a string, got {type(model).__name__}",
            "SKILL.md",
        )
        return

    report.passed(f"'model' field present: {model}", "SKILL.md")


def validate_argument_hint_field(frontmatter: dict[str, Any], report: ValidationReport) -> None:
    """Validate the 'argument-hint' frontmatter field."""
    if "argument-hint" not in frontmatter:
        return

    hint = frontmatter["argument-hint"]

    if not isinstance(hint, str):
        report.major(
            f"'argument-hint' must be a string, got {type(hint).__name__}",
            "SKILL.md",
        )
        return

    report.passed(f"'argument-hint' field present: {hint}", "SKILL.md")


def validate_hooks_field(frontmatter: dict[str, Any], report: ValidationReport) -> None:
    """Validate the 'hooks' frontmatter field."""
    if "hooks" not in frontmatter:
        return

    hooks = frontmatter["hooks"]

    if not isinstance(hooks, dict):
        report.major(
            f"'hooks' must be an object, got {type(hooks).__name__}",
            "SKILL.md",
        )
        return

    report.passed("'hooks' field present", "SKILL.md")


def validate_skill_content(content: str, report: ValidationReport) -> None:
    """Validate SKILL.md content (body after frontmatter)."""
    _, body, _ = parse_frontmatter(content)

    # Check for empty body
    if not body.strip():
        report.major("SKILL.md has no content after frontmatter", "SKILL.md")
        return

    # Check line count (recommendation: under 500 lines)
    total_lines = content.count("\n") + 1
    if total_lines > MAX_SKILL_LINES:
        report.minor(
            f"SKILL.md has {total_lines} lines (recommended: under {MAX_SKILL_LINES}). "
            "Consider moving detailed content to supporting files.",
            "SKILL.md",
        )
    else:
        report.passed(f"SKILL.md line count OK ({total_lines} lines)", "SKILL.md")

    # Check for $ARGUMENTS placeholder if skill seems action-oriented
    # (contains numbered steps, commands, etc.)
    if re.search(r"^\d+\.", body, re.MULTILINE) or "```bash" in body.lower():
        if "$ARGUMENTS" not in content:
            report.info(
                "Task-oriented skill without $ARGUMENTS placeholder (arguments will be appended automatically)",
                "SKILL.md",
            )


def validate_directory_structure(skill_path: Path, report: ValidationReport) -> None:
    """Validate skill directory structure."""
    # Common optional directories per docs
    optional_dirs = ["scripts", "examples", "references", "assets", "templates"]

    for dir_name in optional_dirs:
        dir_path = skill_path / dir_name
        if dir_path.is_dir():
            report.passed(f"Optional directory exists: {dir_name}/")

    # Check for scripts that should be executable
    scripts_dir = skill_path / "scripts"
    if scripts_dir.is_dir():
        for script in scripts_dir.iterdir():
            if script.is_file() and script.suffix in {".sh", ".py", ".bash"}:
                if not os.access(script, os.X_OK):
                    report.major(
                        f"Script not executable: scripts/{script.name}",
                        f"scripts/{script.name}",
                    )
                else:
                    report.passed(
                        f"Script executable: scripts/{script.name}",
                        f"scripts/{script.name}",
                    )


def validate_supporting_files(skill_path: Path, report: ValidationReport) -> None:
    """Validate supporting files referenced in SKILL.md."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return

    content = skill_md.read_text()

    # Find markdown links to local files
    local_refs = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)

    for _, link_target in local_refs:
        # Skip external URLs
        if link_target.startswith(("http://", "https://", "mailto:")):
            continue

        # Skip anchors
        if link_target.startswith("#"):
            continue

        # Check if referenced file exists
        ref_path = skill_path / link_target
        if not ref_path.exists():
            report.major(
                f"Referenced file not found: {link_target}",
                "SKILL.md",
            )
        else:
            report.passed(f"Referenced file exists: {link_target}", "SKILL.md")


def validate_skill(skill_path: Path) -> SkillValidationReport:
    """Validate a complete skill directory.

    Args:
        skill_path: Path to the skill directory

    Returns:
        ValidationReport with all results
    """
    report = SkillValidationReport(skill_path=str(skill_path))

    # Check skill directory exists
    if not skill_path.is_dir():
        report.critical(f"Skill path is not a directory: {skill_path}")
        return report

    # Validate SKILL.md exists (required)
    if not validate_skill_md_exists(skill_path, report):
        return report

    # Read SKILL.md content
    skill_md = skill_path / "SKILL.md"
    content = skill_md.read_text()

    # Validate frontmatter
    frontmatter = validate_frontmatter(skill_path, content, report)

    if frontmatter is not None:
        # Validate individual frontmatter fields
        validate_name_field(frontmatter, skill_path.name, report)
        validate_description_field(frontmatter, content, report)
        validate_context_field(frontmatter, report)
        validate_agent_field(frontmatter, report)
        validate_boolean_field(frontmatter, "user-invocable", report)
        validate_boolean_field(frontmatter, "disable-model-invocation", report)
        validate_allowed_tools_field(frontmatter, report)
        validate_model_field(frontmatter, report)
        validate_argument_hint_field(frontmatter, report)
        validate_hooks_field(frontmatter, report)

    # Validate content
    validate_skill_content(content, report)

    # Validate directory structure
    validate_directory_structure(skill_path, report)

    # Validate supporting files
    validate_supporting_files(skill_path, report)

    return report


def print_results(report: SkillValidationReport, verbose: bool = False) -> None:
    """Print validation results in human-readable format."""
    # ANSI colors
    colors = {
        "CRITICAL": "\033[91m",  # Red
        "MAJOR": "\033[93m",  # Yellow
        "MINOR": "\033[94m",  # Blue
        "NIT": "\033[96m",  # Cyan — blocks only in --strict
        "WARNING": "\033[95m",  # Magenta — never blocks, always reported
        "INFO": "\033[90m",  # Gray
        "PASSED": "\033[92m",  # Green
        "RESET": "\033[0m",
    }

    # Count by level
    counts = {"CRITICAL": 0, "MAJOR": 0, "MINOR": 0, "NIT": 0, "WARNING": 0, "INFO": 0, "PASSED": 0}
    for r in report.results:
        counts[r.level] += 1

    # Print header
    print("\n" + "=" * 60)
    print(f"Skill Validation: {report.skill_path}")
    print("=" * 60)

    # Print summary
    print("\nSummary:")
    print(f"  {colors['CRITICAL']}CRITICAL: {counts['CRITICAL']}{colors['RESET']}")
    print(f"  {colors['MAJOR']}MAJOR:    {counts['MAJOR']}{colors['RESET']}")
    print(f"  {colors['MINOR']}MINOR:    {counts['MINOR']}{colors['RESET']}")
    print(f"  {colors['NIT']}NIT:      {counts['NIT']}{colors['RESET']}")
    print(f"  {colors['WARNING']}WARNING:  {counts['WARNING']}{colors['RESET']}")
    if verbose:
        print(f"  {colors['INFO']}INFO:     {counts['INFO']}{colors['RESET']}")
        print(f"  {colors['PASSED']}PASSED:   {counts['PASSED']}{colors['RESET']}")

    # Print details
    print("\nDetails:")
    for r in report.results:
        if r.level == "PASSED" and not verbose:
            continue
        if r.level == "INFO" and not verbose:
            continue

        color = colors[r.level]
        reset = colors["RESET"]
        file_info = f" ({r.file})" if r.file else ""
        line_info = f":{r.line}" if r.line else ""
        print(f"  {color}[{r.level}]{reset} {r.message}{file_info}{line_info}")

    # Print final status
    print("\n" + "-" * 60)
    if report.exit_code == 0:
        print(f"{colors['PASSED']}✓ Skill validation passed{colors['RESET']}")
    elif report.exit_code == 1:
        crit = colors["CRITICAL"]
        rst = colors["RESET"]
        print(f"{crit}✗ CRITICAL issues - skill will not work{rst}")
    elif report.exit_code == 2:
        maj = colors["MAJOR"]
        rst = colors["RESET"]
        print(f"{maj}✗ MAJOR issues - significant problems{rst}")
    else:
        minor = colors["MINOR"]
        rst = colors["RESET"]
        print(f"{minor}! MINOR issues - may affect UX{rst}")

    print()


def print_json(report: SkillValidationReport) -> None:
    """Print validation results as JSON."""
    output = {
        "skill_path": report.skill_path,
        "exit_code": report.exit_code,
        "counts": {
            "critical": sum(1 for r in report.results if r.level == "CRITICAL"),
            "major": sum(1 for r in report.results if r.level == "MAJOR"),
            "minor": sum(1 for r in report.results if r.level == "MINOR"),
            "warning": sum(1 for r in report.results if r.level == "WARNING"),
            "nit": sum(1 for r in report.results if r.level == "NIT"),
            "info": sum(1 for r in report.results if r.level == "INFO"),
            "passed": sum(1 for r in report.results if r.level == "PASSED"),
        },
        "results": [{"level": r.level, "message": r.message, "file": r.file, "line": r.line} for r in report.results],
    }
    print(json.dumps(output, indent=2))


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate a Claude Code skill directory")
    parser.add_argument("skill_path", help="Path to the skill directory")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show all results including passed checks",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--strict", action="store_true", help="Strict mode — NIT issues also block validation")
    args = parser.parse_args()

    skill_path = Path(args.skill_path).resolve()

    if not skill_path.exists():
        print(f"Error: {skill_path} does not exist", file=sys.stderr)
        return 1

    if not skill_path.is_dir():
        print(f"Error: {skill_path} is not a directory (expected a skill directory)", file=sys.stderr)
        return 1

    # Verify content type — skill directory must contain SKILL.md
    if not (skill_path / "SKILL.md").exists() and not (skill_path / "skill.md").exists():
        print(
            f"Error: No SKILL.md found in {skill_path}\nA valid skill directory must contain a SKILL.md file.",
            file=sys.stderr,
        )
        return 1

    report = validate_skill(skill_path)

    if args.json:
        print_json(report)
    else:
        print_results(report, args.verbose)

    if args.strict:
        return report.exit_code_strict()
    return report.exit_code


if __name__ == "__main__":
    sys.exit(main())
