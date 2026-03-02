#!/usr/bin/env python3
"""
Claude Plugins Validation - Command Validator

Validates individual command markdown files according to Claude Code command spec.
Based on: https://code.claude.com/docs/en/custom-slash-commands.md

Usage:
    uv run python scripts/validate_command.py path/to/command.md
    uv run python scripts/validate_command.py path/to/commands/  # validate all commands in dir
    uv run python scripts/validate_command.py path/to/command.md --verbose
    uv run python scripts/validate_command.py path/to/command.md --json

Exit codes:
    0 - All checks passed
    1 - CRITICAL issues found (command will not work)
    2 - MAJOR issues found (significant problems)
    3 - MINOR issues found (may affect UX)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from cpv_validation_common import (
    COLORS,
    EXIT_CRITICAL,
    EXIT_MAJOR,
    EXIT_OK,
    MAX_NAME_LENGTH,
    NAME_PATTERN,
    SECRET_PATTERNS,
    USER_PATH_PATTERNS,
    VALID_TOOLS,
    ValidationReport,
    check_utf8_encoding,
)

# =============================================================================
# Command-Specific Constants
# =============================================================================

# Maximum description length for commands (SHORTER than agents!)
MAX_COMMAND_DESCRIPTION_LENGTH = 60

# Minimum body content length (characters)
MIN_COMMAND_BODY_CHARS = 100

# Known frontmatter fields per official docs (command-specific)
KNOWN_FRONTMATTER_FIELDS = {
    "name",
    "description",
    "allowed-tools",
    "model",
    "argument-hint",
}

# Pattern for allowed-tools with optional pattern: ToolName or ToolName(pattern*)
TOOL_PATTERN_REGEX = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)(?:\(([^)]*)\))?$")


# =============================================================================
# Command-Specific Report Class
# =============================================================================


@dataclass
class CommandValidationReport(ValidationReport):
    """Validation report for a command file, extends base ValidationReport with command_path."""

    command_path: str = ""

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary for JSON serialization."""
        base = super().to_dict()
        base["command_path"] = self.command_path
        return base


# =============================================================================
# Parsing Functions
# =============================================================================


def parse_frontmatter(content: str) -> tuple[dict[str, Any] | None, str, int]:
    """Parse YAML frontmatter from command content.

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


def count_frontmatter_markers(content: str) -> int:
    """Count the number of --- markers in the file."""
    count = 0
    lines = content.split("\n")
    for line in lines:
        if line.strip() == "---":
            count += 1
    return count


# =============================================================================
# Validation Functions
# =============================================================================


def validate_file_format(content: str, report: CommandValidationReport, filename: str) -> bool:
    """Validate file format: must have exactly two --- markers for YAML frontmatter."""
    marker_count = count_frontmatter_markers(content)

    if marker_count < 2:
        report.critical(
            f"Missing YAML frontmatter markers (found {marker_count}, need 2). "
            "File must start with --- and end frontmatter with ---",
            filename,
        )
        return False

    if marker_count > 2:
        report.minor(
            f"Multiple --- markers found ({marker_count}). Only first two are used for frontmatter",
            filename,
        )

    return True


def validate_frontmatter_exists(content: str, report: CommandValidationReport, filename: str) -> dict[str, Any] | None:
    """Validate YAML frontmatter exists and is valid."""
    if not content.startswith("---"):
        report.critical("No YAML frontmatter found (required)", filename)
        return None

    frontmatter, *_ = parse_frontmatter(content)

    if frontmatter is None and content.startswith("---"):
        report.critical(
            "Malformed YAML frontmatter (missing closing --- or invalid YAML)",
            filename,
        )
        return None

    if frontmatter is None:
        return None

    report.passed("Valid YAML frontmatter", filename)

    # Check for unknown fields
    for key in frontmatter.keys():
        if key not in KNOWN_FRONTMATTER_FIELDS:
            report.warning(
                f"Unknown frontmatter field '{key}' (may be ignored by CLI)",
                filename,
            )

    return frontmatter


def validate_name_field(frontmatter: dict[str, Any], filename: str, report: CommandValidationReport) -> None:
    """Validate the 'name' frontmatter field."""
    if "name" not in frontmatter:
        # Use filename as fallback name (without .md extension)
        expected_name = Path(filename).stem
        report.info(
            f"No 'name' field (will use filename: {expected_name})",
            filename,
        )
        name = expected_name
    else:
        name = frontmatter["name"]
        report.passed(f"'name' field present: {name}", filename)

    if not isinstance(name, str):
        report.critical(f"'name' must be a string, got {type(name).__name__}", filename)
        return

    # Length check: 1-64 characters
    if len(name) < 1:
        report.critical("Name cannot be empty", filename)
        return

    if len(name) > MAX_NAME_LENGTH:
        report.major(
            f"Name exceeds {MAX_NAME_LENGTH} chars ({len(name)} chars): {name}",
            filename,
        )

    # Lowercase check
    if name != name.lower():
        report.major(f"Name must be lowercase: {name}", filename)

    # Kebab-case pattern check
    if not NAME_PATTERN.match(name):
        report.major(
            f"Name must be kebab-case (lowercase letters, numbers, hyphens): {name}",
            filename,
        )

    # Consecutive hyphens check
    if "--" in name:
        report.major(f"Name cannot contain consecutive hyphens: {name}", filename)

    # Start/end hyphen check
    if name.startswith("-") or name.endswith("-"):
        report.major(f"Name cannot start/end with hyphen: {name}", filename)


def validate_description_field(frontmatter: dict[str, Any], filename: str, report: CommandValidationReport) -> None:
    """Validate the 'description' frontmatter field (REQUIRED, max 60 chars)."""
    if "description" not in frontmatter:
        report.major("Missing 'description' field (required)", filename)
        return

    desc = frontmatter["description"]

    if not isinstance(desc, str):
        report.critical(f"'description' must be a string, got {type(desc).__name__}", filename)
        return

    if not desc.strip():
        report.major("'description' cannot be empty", filename)
        return

    # Length check - COMMANDS have shorter max (60 chars vs 1024 for agents)
    if len(desc) > MAX_COMMAND_DESCRIPTION_LENGTH:
        report.major(
            f"Description exceeds {MAX_COMMAND_DESCRIPTION_LENGTH} chars ({len(desc)} chars). "
            "Command descriptions must be brief for slash command menu.",
            filename,
        )

    # Angle brackets check (breaks XML in prompts)
    if "<" in desc or ">" in desc:
        report.major(
            "Description contains angle brackets (< or >) - can break prompts",
            filename,
        )

    # Check for actionable description
    if len(desc) < 10:
        report.minor(
            f"Description is very short ({len(desc)} chars) - may not help users understand the command",
            filename,
        )

    report.passed("'description' field valid", filename)


def validate_allowed_tools_field(frontmatter: dict[str, Any], filename: str, report: CommandValidationReport) -> None:
    """Validate the 'allowed-tools' frontmatter field."""
    if "allowed-tools" not in frontmatter:
        report.info("No 'allowed-tools' field (command will inherit default tools)", filename)
        return

    tools = frontmatter["allowed-tools"]

    # Can be string (comma-separated) or list
    if isinstance(tools, str):
        tool_list = [t.strip() for t in tools.split(",") if t.strip()]
    elif isinstance(tools, list):
        tool_list = [str(t).strip() for t in tools if str(t).strip()]
    else:
        report.major(
            f"'allowed-tools' must be string or list, got {type(tools).__name__}",
            filename,
        )
        return

    if not tool_list:
        report.minor("'allowed-tools' field is empty", filename)
        return

    # Validate each tool pattern
    invalid_tools = []
    for tool in tool_list:
        is_valid, error_msg = validate_tool_pattern(tool)
        if not is_valid:
            invalid_tools.append((tool, error_msg))

    if invalid_tools:
        for tool, error_msg in invalid_tools:
            report.major(f"Invalid tool pattern '{tool}': {error_msg}", filename)
    else:
        report.passed(f"'allowed-tools' field valid: {len(tool_list)} tool(s)", filename)


def validate_tool_pattern(tool: str) -> tuple[bool, str]:
    """Validate a single tool pattern.

    Valid formats:
    - "ToolName" (e.g., "Read", "Write", "Bash")
    - "ToolName(pattern*)" (e.g., "Bash(git*)", "Bash(command:*)")
    - "mcp__server__tool" (MCP tools)

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Handle MCP tools
    if tool.startswith("mcp__"):
        # MCP tools have format: mcp__<server>__<tool>
        parts = tool.split("__")
        if len(parts) >= 3:
            return True, ""
        return False, "MCP tool format should be mcp__<server>__<tool>"

    # Parse tool pattern
    match = TOOL_PATTERN_REGEX.match(tool)
    if not match:
        return False, "Invalid format. Use 'ToolName' or 'ToolName(pattern*)'"

    base_tool = match.group(1)
    pattern = match.group(2)  # May be None

    # Validate base tool name
    if base_tool not in VALID_TOOLS:
        return False, f"Unknown tool '{base_tool}'. Known tools: {sorted(VALID_TOOLS)}"

    # Validate pattern if present
    if pattern is not None:
        # Pattern can be:
        # - Simple glob: "git*", "*"
        # - Command prefix: "command:*"
        # - Empty string (matches nothing specific)
        if pattern and not pattern.strip():
            return False, "Pattern inside parentheses cannot be empty whitespace"

        # Check for common Bash patterns
        if base_tool == "Bash" and pattern:
            # Common patterns: "git *", "npm *", "command:*"
            # Just validate it's not obviously malformed
            if "(" in pattern or ")" in pattern:
                return False, "Pattern cannot contain nested parentheses"

    return True, ""


def validate_model_field(frontmatter: dict[str, Any], filename: str, report: CommandValidationReport) -> None:
    """Validate the 'model' frontmatter field."""
    if "model" not in frontmatter:
        report.info("No 'model' field (command will inherit current model)", filename)
        return

    model = frontmatter["model"]

    if not isinstance(model, str):
        report.major(f"'model' must be a string, got {type(model).__name__}", filename)
        return

    model_lower = model.lower()
    # Valid models for commands: sonnet, opus, haiku (not 'inherit')
    command_valid_models = {"sonnet", "opus", "haiku"}
    if model_lower not in command_valid_models:
        report.major(
            f"Invalid 'model' value: {model}. Valid values: {sorted(command_valid_models)}",
            filename,
        )
        return

    report.passed(f"'model' field valid: {model}", filename)


def validate_argument_hint_field(frontmatter: dict[str, Any], filename: str, report: CommandValidationReport) -> None:
    """Validate the 'argument-hint' frontmatter field."""
    if "argument-hint" not in frontmatter:
        return

    hint = frontmatter["argument-hint"]

    if not isinstance(hint, str):
        report.major(f"'argument-hint' must be a string, got {type(hint).__name__}", filename)
        return

    if not hint.strip():
        report.minor("'argument-hint' is empty (should describe expected arguments)", filename)
        return

    # Check for reasonable length
    if len(hint) > 100:
        report.minor(
            f"'argument-hint' is long ({len(hint)} chars) - may be truncated in UI",
            filename,
        )

    report.passed(f"'argument-hint' field valid: {hint}", filename)


def validate_body_content(content: str, filename: str, report: CommandValidationReport) -> None:
    """Validate command body content (after frontmatter)."""
    _, body, _ = parse_frontmatter(content)

    if not body.strip():
        report.major("Command has no content after frontmatter", filename)
        return

    body_text = body.strip()

    # Minimum content check
    if len(body_text) < MIN_COMMAND_BODY_CHARS:
        report.minor(
            f"Command body is very short ({len(body_text)} chars, recommended: >{MIN_COMMAND_BODY_CHARS})",
            filename,
        )
    else:
        report.passed(f"Command body has adequate content ({len(body_text)} chars)", filename)

    # Check for common command body patterns
    has_instructions = any(
        keyword in body_text.lower()
        for keyword in ["you", "will", "should", "must", "when", "if", "task", "do", "perform", "execute"]
    )
    if not has_instructions:
        report.info(
            "Command body should contain clear instructions for Claude",
            filename,
        )


def validate_security(content: str, filename: str, report: CommandValidationReport) -> None:
    """Check for security issues in command content."""
    # Check for hardcoded secrets
    for pattern, description in SECRET_PATTERNS:
        if pattern.search(content):
            report.critical(f"SECURITY: Contains {description}", filename)

    # Check for hardcoded user paths
    for pattern in USER_PATH_PATTERNS:
        match = pattern.search(content)
        if match:
            report.major(
                f"Contains hardcoded user path: {match.group()}. "
                "Use ${CLAUDE_PLUGIN_ROOT} or ${CLAUDE_PROJECT_DIR} instead",
                filename,
            )

    # Check for ${CLAUDE_PLUGIN_ROOT} usage (good practice for plugin commands)
    if "/scripts/" in content or "\\scripts\\" in content:
        if "${CLAUDE_PLUGIN_ROOT}" not in content and "$CLAUDE_PLUGIN_ROOT" not in content:
            report.info(
                "Consider using ${CLAUDE_PLUGIN_ROOT} for plugin-relative paths",
                filename,
            )


# =============================================================================
# Main Validation Function
# =============================================================================


def validate_command(command_path: Path) -> CommandValidationReport:
    """Validate a complete command file.

    Args:
        command_path: Path to the command .md file

    Returns:
        CommandValidationReport with all results
    """
    report = CommandValidationReport(command_path=str(command_path))
    filename = command_path.name

    # Check file exists
    if not command_path.exists():
        report.critical(f"Command file not found: {command_path}")
        return report

    if not command_path.is_file():
        report.critical(f"Command path is not a file: {command_path}")
        return report

    # Check file extension
    if command_path.suffix.lower() != ".md":
        report.major(f"Command file should have .md extension, got: {command_path.suffix}", filename)

    # Read file content (binary first for encoding check)
    content_bytes = command_path.read_bytes()

    # Check encoding using shared function
    if not check_utf8_encoding(content_bytes, report, filename):
        return report

    report.passed("File is valid UTF-8", filename)

    content = content_bytes.decode("utf-8")

    # Validate file format (two --- markers)
    if not validate_file_format(content, report, filename):
        return report

    # Validate frontmatter
    frontmatter = validate_frontmatter_exists(content, report, filename)

    if frontmatter is not None:
        # Validate individual frontmatter fields
        validate_name_field(frontmatter, filename, report)
        validate_description_field(frontmatter, filename, report)
        validate_allowed_tools_field(frontmatter, filename, report)
        validate_model_field(frontmatter, filename, report)
        validate_argument_hint_field(frontmatter, filename, report)

    # Validate body content
    validate_body_content(content, filename, report)

    # Security checks
    validate_security(content, filename, report)

    return report


def validate_commands_directory(commands_dir: Path) -> list[CommandValidationReport]:
    """Validate all command files in a directory.

    Args:
        commands_dir: Path to the commands/ directory

    Returns:
        List of CommandValidationReport for each command
    """
    reports = []

    if not commands_dir.is_dir():
        report = CommandValidationReport(command_path=str(commands_dir))
        report.critical(f"Not a directory: {commands_dir}")
        return [report]

    command_files = list(commands_dir.glob("*.md"))

    if not command_files:
        report = CommandValidationReport(command_path=str(commands_dir))
        report.info("No command files (*.md) found in directory")
        return [report]

    for command_file in sorted(command_files):
        reports.append(validate_command(command_file))

    return reports


# =============================================================================
# Output Functions
# =============================================================================


def print_results(report: CommandValidationReport, verbose: bool = False) -> None:
    """Print validation results in human-readable format."""
    # Count by level
    counts = report.count_by_level()

    # Print header
    print("\n" + "=" * 60)
    print(f"Command Validation: {report.command_path}")
    print("=" * 60)

    # Print summary
    print("\nSummary:")
    print(f"  {COLORS['CRITICAL']}CRITICAL: {counts['CRITICAL']}{COLORS['RESET']}")
    print(f"  {COLORS['MAJOR']}MAJOR:    {counts['MAJOR']}{COLORS['RESET']}")
    print(f"  {COLORS['MINOR']}MINOR:    {counts['MINOR']}{COLORS['RESET']}")
    if verbose:
        print(f"  {COLORS['INFO']}INFO:     {counts['INFO']}{COLORS['RESET']}")
        print(f"  {COLORS['PASSED']}PASSED:   {counts['PASSED']}{COLORS['RESET']}")

    # Print score
    score = report.score
    score_color = COLORS["PASSED"] if score >= 80 else COLORS["MAJOR"] if score >= 60 else COLORS["CRITICAL"]
    print(f"\n  Score: {score_color}{score}/100{COLORS['RESET']}")

    # Print details
    print("\nDetails:")
    for r in report.results:
        if r.level == "PASSED" and not verbose:
            continue
        if r.level == "INFO" and not verbose:
            continue

        color = COLORS[r.level]
        reset = COLORS["RESET"]
        file_info = f" ({r.file})" if r.file else ""
        line_info = f":{r.line}" if r.line else ""
        print(f"  {color}[{r.level}]{reset} {r.message}{file_info}{line_info}")

    # Print final status
    print("\n" + "-" * 60)
    if report.exit_code == EXIT_OK:
        print(f"{COLORS['PASSED']}[OK] Command validation passed{COLORS['RESET']}")
    elif report.exit_code == EXIT_CRITICAL:
        print(f"{COLORS['CRITICAL']}[CRITICAL] CRITICAL issues - command will not work{COLORS['RESET']}")
    elif report.exit_code == EXIT_MAJOR:
        print(f"{COLORS['MAJOR']}[MAJOR] MAJOR issues - significant problems{COLORS['RESET']}")
    else:
        print(f"{COLORS['MINOR']}[MINOR] MINOR issues - may affect UX{COLORS['RESET']}")

    print()


def print_json(report: CommandValidationReport) -> None:
    """Print validation results as JSON."""
    output = {
        "command_path": report.command_path,
        "exit_code": report.exit_code,
        "score": report.score,
        "counts": {
            "critical": sum(1 for r in report.results if r.level == "CRITICAL"),
            "major": sum(1 for r in report.results if r.level == "MAJOR"),
            "minor": sum(1 for r in report.results if r.level == "MINOR"),
            "info": sum(1 for r in report.results if r.level == "INFO"),
            "passed": sum(1 for r in report.results if r.level == "PASSED"),
        },
        "results": [{"level": r.level, "message": r.message, "file": r.file, "line": r.line} for r in report.results],
    }
    print(json.dumps(output, indent=2))


# =============================================================================
# Main Entry Point
# =============================================================================


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate a Claude Code command file or directory")
    parser.add_argument("path", help="Path to command .md file or commands/ directory")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show all results including passed checks",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--strict", action="store_true", help="Strict mode — NIT issues also block validation")
    args = parser.parse_args()

    path = Path(args.path).resolve()

    if not path.exists():
        print(f"Error: {path} does not exist", file=sys.stderr)
        return 1

    # Verify content type — must be .md file or directory containing .md files
    if path.is_file() and path.suffix != ".md":
        print(f"Error: {path} is not a Markdown (.md) command file", file=sys.stderr)
        return 1
    if path.is_dir() and not list(path.glob("*.md")):
        print(f"Error: No command definition files (.md) found in {path}", file=sys.stderr)
        return 1

    # Handle directory vs file
    if path.is_dir():
        reports = validate_commands_directory(path)
    else:
        reports = [validate_command(path)]

    # Output
    if args.json:
        if len(reports) == 1:
            print_json(reports[0])
        else:
            combined = {
                "commands": [
                    {
                        "command_path": r.command_path,
                        "exit_code": r.exit_code,
                        "score": r.score,
                        "counts": {
                            "critical": sum(1 for x in r.results if x.level == "CRITICAL"),
                            "major": sum(1 for x in r.results if x.level == "MAJOR"),
                            "minor": sum(1 for x in r.results if x.level == "MINOR"),
                            "info": sum(1 for x in r.results if x.level == "INFO"),
                            "passed": sum(1 for x in r.results if x.level == "PASSED"),
                        },
                        "results": [
                            {"level": x.level, "message": x.message, "file": x.file, "line": x.line} for x in r.results
                        ],
                    }
                    for r in reports
                ],
                "overall_exit_code": max(r.exit_code for r in reports),
            }
            print(json.dumps(combined, indent=2))
    else:
        for report in reports:
            print_results(report, args.verbose)

    # Return worst exit code — in strict mode NIT issues also block
    if args.strict:
        return max(r.exit_code_strict() for r in reports)
    return max(r.exit_code for r in reports)


if __name__ == "__main__":
    sys.exit(main())
