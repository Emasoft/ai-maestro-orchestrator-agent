#!/usr/bin/env python3
"""Validate skills against the Open Agent Skills Specification.

Uses the skills-ref package from https://github.com/agentskills/agentskills
for validation, with additional Claude Code-specific checks.

Requirements:
    pip install skills-ref

Usage:
    python validate_skill.py ./path/to/skill
    python validate_skill.py ./path/to/skill --strict
    python validate_skill.py ./path/to/skill --json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, TypedDict

# Check if skills-ref is installed
try:
    from skills_ref import validate, read_properties  # type: ignore[import-not-found]

    SKILLS_REF_AVAILABLE = True
except ImportError:
    SKILLS_REF_AVAILABLE = False


# Open Spec constraints
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_COMPATIBILITY_LENGTH = 500
MAX_BODY_LINES = 500

# Claude Code additional directories
CLAUDE_CODE_DIRS = {"commands", "agents", "hooks", "scripts", "references", "assets"}


class ValidationResult(TypedDict):
    """Result of skill validation."""

    valid: bool
    errors: list[str]
    warnings: list[str]
    properties: dict[str, Any] | None


def validate_name_format(name: str) -> list[str]:
    """Validate name follows Open Spec constraints."""
    errors = []

    if not name:
        errors.append("Name is required")
        return errors

    if len(name) > MAX_NAME_LENGTH:
        errors.append(f"Name exceeds {MAX_NAME_LENGTH} characters: {len(name)}")

    if name != name.lower():
        errors.append(f"Name must be lowercase: '{name}'")

    if name.startswith("-") or name.endswith("-"):
        errors.append(f"Name cannot start/end with hyphen: '{name}'")

    if "--" in name:
        errors.append(f"Name cannot contain consecutive hyphens: '{name}'")

    # Check for invalid characters
    for char in name:
        if not (char.isalnum() or char == "-"):
            errors.append(f"Name contains invalid character '{char}': '{name}'")
            break

    return errors


def validate_skill_md(skill_path: Path) -> tuple[list[str], list[str]]:
    """Validate SKILL.md content against Open Spec.

    Returns:
        Tuple of (errors, warnings)
    """
    errors: list[str] = []
    warnings: list[str] = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        errors.append("Missing required file: SKILL.md")
        return errors, warnings

    content = skill_md.read_text(encoding="utf-8")
    lines = content.split("\n")

    # Check for frontmatter
    if not content.startswith("---"):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return errors, warnings

    # Find frontmatter end
    frontmatter_end = content.find("---", 3)
    if frontmatter_end == -1:
        errors.append("SKILL.md frontmatter not closed (missing ---)")
        return errors, warnings

    # Count body lines (after frontmatter)
    body_start_line = content[: frontmatter_end + 3].count("\n") + 1
    body_lines = len(lines) - body_start_line

    # Body line count is a recommendation, not a hard requirement
    if body_lines > MAX_BODY_LINES:
        warnings.append(
            f"Body exceeds {MAX_BODY_LINES} lines recommendation: {body_lines} lines"
        )

    return errors, warnings


def validate_directory_name(skill_path: Path, skill_name: str) -> list[str]:
    """Validate directory name matches skill name."""
    errors = []
    dir_name = skill_path.name

    if dir_name != skill_name:
        errors.append(
            f"Directory name '{dir_name}' does not match skill name '{skill_name}'"
        )

    return errors


def validate_claude_code_extras(skill_path: Path) -> list[str]:
    """Check for Claude Code-specific issues (warnings, not errors)."""
    warnings = []

    # Check for plugin.json in parent (if this is part of a plugin)
    plugin_dir = skill_path.parent.parent / ".claude-plugin"
    if plugin_dir.exists() and not (plugin_dir / "plugin.json").exists():
        warnings.append("Plugin directory exists but missing plugin.json")

    # Check scripts are executable
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        for script in scripts_dir.iterdir():
            if script.is_file() and script.suffix in {".sh", ".py"}:
                # Check shebang
                first_line = script.read_text(encoding="utf-8").split("\n")[0]
                if not first_line.startswith("#!"):
                    warnings.append(f"Script missing shebang: {script.name}")

    return warnings


def validate_skill(skill_path: Path, strict: bool = False) -> ValidationResult:
    """Validate a skill directory.

    Returns:
        ValidationResult with 'valid', 'errors', 'warnings', and 'properties' keys
    """
    result: ValidationResult = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "properties": None,
    }

    # Check path exists
    if not skill_path.exists():
        result["errors"].append(f"Skill path does not exist: {skill_path}")
        result["valid"] = False
        return result

    if not skill_path.is_dir():
        result["errors"].append(f"Skill path is not a directory: {skill_path}")
        result["valid"] = False
        return result

    # Validate SKILL.md exists and format
    md_errors, md_warnings = validate_skill_md(skill_path)
    result["errors"].extend(md_errors)
    result["warnings"].extend(md_warnings)

    # Use skills-ref if available
    if SKILLS_REF_AVAILABLE:
        # Run skills-ref validation
        ref_errors = validate(str(skill_path))
        result["errors"].extend(ref_errors)

        # Get properties if valid so far
        if not result["errors"]:
            try:
                props = read_properties(str(skill_path))
                result["properties"] = {
                    "name": props.name,
                    "description": props.description,
                    "license": props.license,
                    "compatibility": props.compatibility,
                    "metadata": props.metadata,
                    "allowed_tools": props.allowed_tools,
                }

                # Additional checks on properties
                if (
                    props.description
                    and len(props.description) > MAX_DESCRIPTION_LENGTH
                ):
                    result["errors"].append(
                        f"Description exceeds {MAX_DESCRIPTION_LENGTH} chars: {len(props.description)}"
                    )

                if (
                    props.compatibility
                    and len(props.compatibility) > MAX_COMPATIBILITY_LENGTH
                ):
                    result["errors"].append(
                        f"Compatibility exceeds {MAX_COMPATIBILITY_LENGTH} chars: {len(props.compatibility)}"
                    )

                # Validate directory name matches
                result["errors"].extend(validate_directory_name(skill_path, props.name))

            except Exception as e:
                result["errors"].append(f"Failed to read properties: {e}")
    else:
        result["warnings"].append(
            "skills-ref not installed. Install with: pip install skills-ref"
        )

    # Claude Code-specific checks (as warnings)
    result["warnings"].extend(validate_claude_code_extras(skill_path))

    # Determine validity
    if result["errors"]:
        result["valid"] = False
    elif strict and result["warnings"]:
        result["valid"] = False
        result["errors"].extend([f"[strict] {w}" for w in result["warnings"]])

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate skills against Open Agent Skills Specification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python validate_skill.py ./my-skill
    python validate_skill.py ./my-skill --strict
    python validate_skill.py ./my-skill --json

Requirements:
    pip install skills-ref
        """,
    )
    parser.add_argument("skill_path", type=Path, help="Path to skill directory")
    parser.add_argument(
        "--strict", action="store_true", help="Treat warnings as errors"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    result = validate_skill(args.skill_path, args.strict)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        skill_name = args.skill_path.name

        if result["valid"]:
            print(f"[VALID] {skill_name}")
            if result["properties"]:
                print(f"  Name: {result['properties']['name']}")
                desc = result["properties"]["description"]
                if desc and len(desc) > 80:
                    desc = desc[:77] + "..."
                print(f"  Description: {desc}")
        else:
            print(f"[INVALID] {skill_name}")
            for error in result["errors"]:
                print(f"  ERROR: {error}")

        if result["warnings"]:
            for warning in result["warnings"]:
                print(f"  WARNING: {warning}")

    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
