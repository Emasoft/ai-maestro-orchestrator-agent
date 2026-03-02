#!/usr/bin/env python3
"""
Claude Plugins Validation - Documentation Validator

Validates README.md and documentation files according to best practices.
Implements 13 documentation validation rules:

1. README.md should exist at plugin root
2. README should contain installation instructions
3. README should contain usage examples
4. README should contain description section
5. README should have proper markdown formatting
6. No broken internal links
7. CHANGELOG.md recommended
8. Heading hierarchy should have no skips
9. Code blocks should be closed
10. Code blocks should have language tags
11. List formatting should be proper
12. Table structure should be valid
13. Image references should be valid

Usage:
    uv run python scripts/validate_documentation.py path/to/plugin/
    uv run python scripts/validate_documentation.py path/to/plugin/ --verbose
    uv run python scripts/validate_documentation.py path/to/plugin/ --json

Exit codes:
    0 - All checks passed
    1 - CRITICAL issues found
    2 - MAJOR issues found
    3 - MINOR issues found
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from cpv_validation_common import ValidationReport

# =============================================================================
# Documentation Validation Report
# =============================================================================


@dataclass
class DocumentationValidationReport(ValidationReport):
    """Validation report for documentation files.

    Extends ValidationReport with plugin_path tracking.
    All validation methods and properties are inherited from ValidationReport.
    """

    plugin_path: str = ""


# =============================================================================
# Rule 1: README.md should exist at plugin root
# =============================================================================


def validate_readme_exists(plugin_path: Path, report: DocumentationValidationReport) -> bool:
    """Validate that README.md exists at plugin root.

    Args:
        plugin_path: Path to the plugin directory
        report: Validation report to add results to

    Returns:
        True if README.md exists, False otherwise
    """
    readme = plugin_path / "README.md"
    if readme.exists():
        report.passed("README.md exists at plugin root", "README.md")
        return True
    else:
        # Also check for lowercase variant
        readme_lower = plugin_path / "readme.md"
        if readme_lower.exists():
            report.minor(
                "README.md exists but uses lowercase (readme.md) - consider using README.md",
                "readme.md",
            )
            return True

        report.critical("README.md is missing at plugin root", "README.md")
        return False


# =============================================================================
# Rule 2: README should contain installation instructions
# =============================================================================


def validate_installation_section(plugin_path: Path, report: DocumentationValidationReport) -> None:
    """Validate that README contains installation instructions.

    Looks for sections named: Installation, Getting Started, Setup, Quick Start

    Args:
        plugin_path: Path to the plugin directory
        report: Validation report to add results to
    """
    readme = _find_readme(plugin_path)
    if readme is None:
        return  # Already reported in validate_readme_exists

    content = readme.read_text()

    # Pattern matches ## Installation, ## Getting Started, ## Setup, ## Quick Start
    installation_patterns = [
        r"^#+\s*installation",
        r"^#+\s*getting\s+started",
        r"^#+\s*setup",
        r"^#+\s*quick\s*start",
    ]

    for pattern in installation_patterns:
        if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
            report.passed("README contains installation instructions", "README.md")
            return

    report.major(
        "README missing installation section (## Installation, ## Getting Started, ## Setup, or ## Quick Start)",
        "README.md",
    )


# =============================================================================
# Rule 3: README should contain usage examples
# =============================================================================


def validate_usage_section(plugin_path: Path, report: DocumentationValidationReport) -> None:
    """Validate that README contains usage examples.

    Looks for sections named: Usage, Examples, How to Use

    Args:
        plugin_path: Path to the plugin directory
        report: Validation report to add results to
    """
    readme = _find_readme(plugin_path)
    if readme is None:
        return

    content = readme.read_text()

    usage_patterns = [
        r"^#+\s*usage",
        r"^#+\s*examples?",
        r"^#+\s*how\s+to\s+use",
    ]

    for pattern in usage_patterns:
        if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
            report.passed("README contains usage section", "README.md")
            return

    report.major(
        "README missing usage section (## Usage, ## Examples, or ## How to Use)",
        "README.md",
    )


# =============================================================================
# Rule 4: README should contain description section
# =============================================================================


def validate_description_section(plugin_path: Path, report: DocumentationValidationReport) -> None:
    """Validate that README contains a description.

    A description is considered present if there's content between the
    title (h1) and the first h2 section.

    Args:
        plugin_path: Path to the plugin directory
        report: Validation report to add results to
    """
    readme = _find_readme(plugin_path)
    if readme is None:
        return

    content = readme.read_text()
    lines = content.split("\n")

    # Find the first h1 and first h2
    h1_idx = None
    h2_idx = None

    for i, line in enumerate(lines):
        if line.startswith("# ") and h1_idx is None:
            h1_idx = i
        elif line.startswith("## ") and h2_idx is None:
            h2_idx = i
            break

    if h1_idx is None:
        report.major("README missing title (# heading)", "README.md")
        return

    # Check for content between h1 and h2 (or end of file)
    end_idx = h2_idx if h2_idx is not None else len(lines)
    description_lines = lines[h1_idx + 1 : end_idx]
    description_content = "\n".join(description_lines).strip()

    # Need at least 20 characters of description content
    if len(description_content) >= 20:
        report.passed("README contains description section", "README.md")
    else:
        report.major(
            "README missing description section after title (add content between # Title and first ## section)",
            "README.md",
        )


# =============================================================================
# Rule 5: README should have proper markdown formatting
# (Meta-rule - covered by rules 8-12)
# =============================================================================


# =============================================================================
# Rule 6: No broken internal links
# =============================================================================


def validate_broken_links(plugin_path: Path, report: DocumentationValidationReport) -> None:
    """Validate that all internal links point to existing files.

    Checks markdown links [text](path) where path is a local file reference.
    External URLs (http://, https://, mailto:) are skipped.
    Anchor links (#section) are skipped.

    Args:
        plugin_path: Path to the plugin directory
        report: Validation report to add results to
    """
    # Find all markdown files in the plugin
    md_files = list(plugin_path.rglob("*.md"))

    for md_file in md_files:
        try:
            content = md_file.read_text()
        except (OSError, UnicodeDecodeError):
            continue

        # Find all markdown links: [text](target)
        links = re.findall(r"\[([^\]]*)\]\(([^)]+)\)", content)

        for link_text, link_target in links:
            # Skip external URLs
            if link_target.startswith(("http://", "https://", "mailto:")):
                continue

            # Skip anchor links
            if link_target.startswith("#"):
                continue

            # Handle links with anchors (file.md#section)
            target_path = link_target.split("#")[0]
            if not target_path:
                continue

            # Resolve relative to the markdown file's directory
            resolved = md_file.parent / target_path
            if not resolved.exists():
                # Also try relative to plugin root
                resolved = plugin_path / target_path
                if not resolved.exists():
                    rel_md = md_file.relative_to(plugin_path)
                    report.major(
                        f"Broken internal link: [{link_text}]({link_target})",
                        str(rel_md),
                    )


# =============================================================================
# Rule 7: CHANGELOG.md recommended
# =============================================================================


def validate_changelog_exists(plugin_path: Path, report: DocumentationValidationReport) -> None:
    """Validate that CHANGELOG.md exists (recommended).

    Args:
        plugin_path: Path to the plugin directory
        report: Validation report to add results to
    """
    changelog = plugin_path / "CHANGELOG.md"
    if changelog.exists():
        report.passed("CHANGELOG.md exists", "CHANGELOG.md")
        return

    # Check for variations
    for variant in ["CHANGELOG.md", "changelog.md", "CHANGES.md", "HISTORY.md"]:
        if (plugin_path / variant).exists():
            report.passed(f"Changelog found ({variant})", variant)
            return

    report.minor(
        "CHANGELOG.md is recommended for tracking version history",
        "CHANGELOG.md",
    )


# =============================================================================
# Rule 8: Heading hierarchy should have no skips
# =============================================================================


def validate_heading_hierarchy(plugin_path: Path, report: DocumentationValidationReport) -> None:
    """Validate that heading levels don't skip (h1 -> h3 is bad).

    Args:
        plugin_path: Path to the plugin directory
        report: Validation report to add results to
    """
    readme = _find_readme(plugin_path)
    if readme is None:
        return

    content = readme.read_text()
    lines = content.split("\n")

    # Track current heading level
    current_level = 0
    issues_found = False

    for i, line in enumerate(lines):
        # Match ATX-style headings (# Heading)
        match = re.match(r"^(#{1,6})\s+", line)
        if match:
            level = len(match.group(1))

            # Check if we skipped a level
            if current_level > 0 and level > current_level + 1:
                report.minor(
                    f"Heading hierarchy skip: level {current_level} to level {level} (line {i + 1})",
                    "README.md",
                    i + 1,
                )
                issues_found = True

            current_level = level

    if not issues_found and current_level > 0:
        report.passed("Heading hierarchy is correct", "README.md")


# =============================================================================
# Rule 9: Code blocks should be closed
# =============================================================================


def validate_code_block_closed(plugin_path: Path, report: DocumentationValidationReport) -> None:
    """Validate that all code blocks are properly closed.

    Checks that ``` fences are balanced (even count).

    Args:
        plugin_path: Path to the plugin directory
        report: Validation report to add results to
    """
    readme = _find_readme(plugin_path)
    if readme is None:
        return

    content = readme.read_text()
    lines = content.split("\n")

    # Track code fence state
    in_code_block = False
    open_line = 0
    issues_found = False

    for i, line in enumerate(lines):
        # Check for code fence (``` with optional language)
        if line.strip().startswith("```"):
            if not in_code_block:
                in_code_block = True
                open_line = i + 1
            else:
                in_code_block = False

    if in_code_block:
        report.major(
            f"Unclosed code block starting at line {open_line}",
            "README.md",
            open_line,
        )
        issues_found = True

    if not issues_found:
        report.passed("All code blocks are properly closed", "README.md")


# =============================================================================
# Rule 10: Code blocks should have language tags
# =============================================================================


def validate_code_block_language_tags(plugin_path: Path, report: DocumentationValidationReport) -> None:
    """Validate that code blocks have language tags.

    Checks that code fences specify a language (```python not just ```).

    Args:
        plugin_path: Path to the plugin directory
        report: Validation report to add results to
    """
    readme = _find_readme(plugin_path)
    if readme is None:
        return

    content = readme.read_text()
    lines = content.split("\n")

    in_code_block = False
    issues_found = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped.startswith("```"):
            if not in_code_block:
                # Opening fence - check for language tag
                in_code_block = True
                # Extract what comes after ```
                lang_part = stripped[3:].strip()
                if not lang_part:
                    report.minor(
                        f"Code block at line {i + 1} missing language tag",
                        "README.md",
                        i + 1,
                    )
                    issues_found = True
            else:
                in_code_block = False

    if not issues_found:
        report.passed("All code blocks have language tags", "README.md")


# =============================================================================
# Rule 11: List formatting should be proper
# =============================================================================


def validate_list_formatting(plugin_path: Path, report: DocumentationValidationReport) -> None:
    """Validate that list formatting is consistent.

    Checks for mixed list markers (-, *, +) in the same document.

    Args:
        plugin_path: Path to the plugin directory
        report: Validation report to add results to
    """
    readme = _find_readme(plugin_path)
    if readme is None:
        return

    content = readme.read_text()
    lines = content.split("\n")

    # Track list markers used
    markers_used: set[str] = set()
    in_code_block = False

    for line in lines:
        stripped = line.strip()

        # Skip code blocks
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Check for unordered list items
        match = re.match(r"^([-*+])\s+", stripped)
        if match:
            markers_used.add(match.group(1))

    if len(markers_used) > 1:
        markers = ", ".join(sorted(markers_used))
        report.minor(
            f"Inconsistent list markers used: {markers} (prefer using one consistently)",
            "README.md",
        )
    elif markers_used:
        report.passed("List formatting is consistent", "README.md")


# =============================================================================
# Rule 12: Table structure should be valid
# =============================================================================


def validate_table_structure(plugin_path: Path, report: DocumentationValidationReport) -> None:
    """Validate that markdown tables have consistent structure.

    Checks that:
    - Separator row has correct number of columns
    - Data rows have same number of columns as header

    Args:
        plugin_path: Path to the plugin directory
        report: Validation report to add results to
    """
    readme = _find_readme(plugin_path)
    if readme is None:
        return

    content = readme.read_text()
    lines = content.split("\n")

    in_table = False
    header_cols = 0
    issues_found = False
    in_code_block = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip code blocks
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Check for table row
        if stripped.startswith("|") and stripped.endswith("|"):
            cols = len([c for c in stripped.split("|") if c.strip()])

            if not in_table:
                # Header row
                in_table = True
                header_cols = cols
            elif re.match(r"^\|[\s\-:|]+\|$", stripped):
                # Separator row
                sep_cols = len([c for c in stripped.split("|") if c.strip()])
                if sep_cols != header_cols:
                    report.minor(
                        f"Table separator row has {sep_cols} columns, header has {header_cols} (line {i + 1})",
                        "README.md",
                        i + 1,
                    )
                    issues_found = True
            else:
                # Data row
                if cols != header_cols:
                    report.minor(
                        f"Table row has {cols} columns, header has {header_cols} (line {i + 1})",
                        "README.md",
                        i + 1,
                    )
                    issues_found = True
        else:
            # Not a table row - reset table state
            in_table = False
            header_cols = 0

    if not issues_found and header_cols > 0:
        report.passed("Table structure is valid", "README.md")


# =============================================================================
# Rule 13: Image references should be valid
# =============================================================================


def validate_image_references(plugin_path: Path, report: DocumentationValidationReport) -> None:
    """Validate that image references point to existing files.

    Checks markdown images ![alt](path) where path is a local file.
    External URLs are skipped.

    Args:
        plugin_path: Path to the plugin directory
        report: Validation report to add results to
    """
    # Find all markdown files
    md_files = list(plugin_path.rglob("*.md"))

    for md_file in md_files:
        try:
            content = md_file.read_text()
        except (OSError, UnicodeDecodeError):
            continue

        # Find all image references: ![alt](path)
        images = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", content)

        for alt_text, img_path in images:
            # Skip external URLs
            if img_path.startswith(("http://", "https://", "data:")):
                continue

            # Resolve relative to the markdown file's directory
            resolved = md_file.parent / img_path
            if not resolved.exists():
                # Also try relative to plugin root
                resolved = plugin_path / img_path
                if not resolved.exists():
                    rel_md = md_file.relative_to(plugin_path)
                    report.major(
                        f"Missing image: ![{alt_text}]({img_path})",
                        str(rel_md),
                    )


# =============================================================================
# Helper Functions
# =============================================================================


def _find_readme(plugin_path: Path) -> Path | None:
    """Find README.md in plugin directory (case-insensitive).

    Args:
        plugin_path: Path to the plugin directory

    Returns:
        Path to README.md if found, None otherwise
    """
    for name in ["README.md", "readme.md", "Readme.md"]:
        readme = plugin_path / name
        if readme.exists():
            return readme
    return None


# =============================================================================
# Main Validation Function
# =============================================================================


def validate_documentation(plugin_path: Path) -> DocumentationValidationReport:
    """Validate all documentation in a plugin directory.

    Runs all 13 validation rules and returns a complete report.

    Args:
        plugin_path: Path to the plugin directory

    Returns:
        DocumentationValidationReport with all results
    """
    report = DocumentationValidationReport(plugin_path=str(plugin_path))

    # Check plugin directory exists
    if not plugin_path.is_dir():
        report.critical(f"Plugin path is not a directory: {plugin_path}")
        return report

    # Rule 1: README.md should exist
    if not validate_readme_exists(plugin_path, report):
        # Can't validate other rules without README
        return report

    # Rule 2: Installation section
    validate_installation_section(plugin_path, report)

    # Rule 3: Usage section
    validate_usage_section(plugin_path, report)

    # Rule 4: Description section
    validate_description_section(plugin_path, report)

    # Rule 5 is covered by rules 8-12

    # Rule 6: Broken links
    validate_broken_links(plugin_path, report)

    # Rule 7: CHANGELOG recommended
    validate_changelog_exists(plugin_path, report)

    # Rule 8: Heading hierarchy
    validate_heading_hierarchy(plugin_path, report)

    # Rule 9: Code blocks closed
    validate_code_block_closed(plugin_path, report)

    # Rule 10: Code block language tags
    validate_code_block_language_tags(plugin_path, report)

    # Rule 11: List formatting
    validate_list_formatting(plugin_path, report)

    # Rule 12: Table structure
    validate_table_structure(plugin_path, report)

    # Rule 13: Image references
    validate_image_references(plugin_path, report)

    return report


# =============================================================================
# Output Functions
# =============================================================================


def print_results(report: DocumentationValidationReport, verbose: bool = False) -> None:
    """Print validation results in human-readable format.

    Args:
        report: The validation report to print
        verbose: If True, also show INFO and PASSED results
    """
    # ANSI colors
    colors = {
        "CRITICAL": "\033[91m",  # Red
        "MAJOR": "\033[93m",  # Yellow
        "MINOR": "\033[94m",  # Blue
        "INFO": "\033[90m",  # Gray
        "PASSED": "\033[92m",  # Green
        "RESET": "\033[0m",
    }

    # Count by level
    counts = {"CRITICAL": 0, "MAJOR": 0, "MINOR": 0, "INFO": 0, "PASSED": 0}
    for r in report.results:
        counts[r.level] += 1

    # Print header
    print("\n" + "=" * 60)
    print(f"Documentation Validation: {report.plugin_path}")
    print("=" * 60)

    # Print summary
    print("\nSummary:")
    print(f"  {colors['CRITICAL']}CRITICAL: {counts['CRITICAL']}{colors['RESET']}")
    print(f"  {colors['MAJOR']}MAJOR:    {counts['MAJOR']}{colors['RESET']}")
    print(f"  {colors['MINOR']}MINOR:    {counts['MINOR']}{colors['RESET']}")
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
        print(f"{colors['PASSED']}Documentation validation passed{colors['RESET']}")
    elif report.exit_code == 1:
        crit = colors["CRITICAL"]
        rst = colors["RESET"]
        print(f"{crit}CRITICAL issues - documentation incomplete{rst}")
    elif report.exit_code == 2:
        maj = colors["MAJOR"]
        rst = colors["RESET"]
        print(f"{maj}MAJOR issues - significant documentation problems{rst}")
    else:
        minor = colors["MINOR"]
        rst = colors["RESET"]
        print(f"{minor}MINOR issues - documentation could be improved{rst}")

    print()


def print_json(report: DocumentationValidationReport) -> None:
    """Print validation results as JSON.

    Args:
        report: The validation report to print
    """
    output = {
        "plugin_path": report.plugin_path,
        "exit_code": report.exit_code,
        "counts": {
            "critical": sum(1 for r in report.results if r.level == "CRITICAL"),
            "major": sum(1 for r in report.results if r.level == "MAJOR"),
            "minor": sum(1 for r in report.results if r.level == "MINOR"),
            "info": sum(1 for r in report.results if r.level == "INFO"),
            "passed": sum(1 for r in report.results if r.level == "PASSED"),
        },
        "results": [
            {
                "level": r.level,
                "message": r.message,
                "file": r.file,
                "line": r.line,
            }
            for r in report.results
        ],
    }
    print(json.dumps(output, indent=2))


# =============================================================================
# CLI Entry Point
# =============================================================================


def main() -> int:
    """Main entry point for CLI.

    Returns:
        Exit code (0=ok, 1=critical, 2=major, 3=minor)
    """
    parser = argparse.ArgumentParser(description="Validate documentation files in a Claude Code plugin")
    parser.add_argument("plugin_path", help="Path to the plugin directory")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show all results including passed checks",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--strict", action="store_true", help="Strict mode — NIT issues also block validation")
    args = parser.parse_args()

    plugin_path = Path(args.plugin_path).resolve()

    if not plugin_path.exists():
        print(f"Error: {plugin_path} does not exist", file=sys.stderr)
        return 1

    if not plugin_path.is_dir():
        print(f"Error: {plugin_path} is not a directory", file=sys.stderr)
        return 1

    # Verify this is a plugin directory
    if not (plugin_path / ".claude-plugin").is_dir():
        print(
            f"Error: No Claude Code plugin found at {plugin_path}\nExpected a .claude-plugin/ directory.",
            file=sys.stderr,
        )
        return 1

    report = validate_documentation(plugin_path)

    if args.json:
        print_json(report)
    else:
        print_results(report, args.verbose)

    if args.strict:
        return report.exit_code_strict()
    return report.exit_code


if __name__ == "__main__":
    sys.exit(main())
