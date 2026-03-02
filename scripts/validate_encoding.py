#!/usr/bin/env python3
"""
Claude Plugins Validation - Encoding Module

Validates file encoding and format across the entire plugin.
This module ensures consistent text encoding for cross-platform compatibility.

Encoding Checks Implemented:
1. UTF-8 encoding required (all text files)
2. No BOM (Byte Order Mark) detection
3. Proper Unicode handling in JSON
4. Special characters properly escaped
5. Line endings: LF for source files (.py, .sh, .md, .json)
6. Shell scripts: LF endings required (not CRLF)
7. Batch scripts (.bat, .cmd): CRLF allowed
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

from cpv_validation_common import (
    SKIP_DIRS,
    ValidationReport,
    print_report_summary,
    print_results_by_level,
)

# =============================================================================
# File Extension Categories
# =============================================================================

# Text files that must use UTF-8 encoding
TEXT_EXTENSIONS = {
    ".py",
    ".sh",
    ".bash",
    ".zsh",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".txt",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".html",
    ".htm",
    ".css",
    ".xml",
    ".ini",
    ".cfg",
    ".conf",
    ".env.example",
    ".gitignore",
    ".gitattributes",
    ".editorconfig",
    ".prettierrc",
    ".eslintrc",
}

# Source files that MUST use LF line endings (Unix-style)
LF_REQUIRED_EXTENSIONS = {
    ".py",
    ".sh",
    ".bash",
    ".zsh",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".html",
    ".htm",
    ".css",
    ".xml",
}

# Shell scripts that MUST use LF (CRLF will break them)
SHELL_EXTENSIONS = {
    ".sh",
    ".bash",
    ".zsh",
    ".ksh",
}

# Windows batch scripts that MAY use CRLF
BATCH_EXTENSIONS = {
    ".bat",
    ".cmd",
    ".ps1",
}

# Binary file extensions to skip
BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".ico",
    ".webp",
    ".svg",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".zip",
    ".tar",
    ".gz",
    ".bz2",
    ".xz",
    ".7z",
    ".rar",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".a",
    ".o",
    ".obj",
    ".pyc",
    ".pyo",
    ".class",
    ".jar",
    ".war",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".eot",
    ".mp3",
    ".mp4",
    ".avi",
    ".mkv",
    ".mov",
    ".wav",
    ".flac",
    ".sqlite",
    ".db",
    ".sqlite3",
}

# =============================================================================
# Encoding Validation Report
# =============================================================================


class EncodingValidationReport(ValidationReport):
    """Extended validation report for encoding-specific statistics."""

    def __init__(self) -> None:
        super().__init__()
        self.stats: dict[str, int] = {
            "files_scanned": 0,
            "files_skipped": 0,
            "utf8_issues": 0,
            "bom_issues": 0,
            "unicode_issues": 0,
            "escape_issues": 0,
            "line_ending_issues": 0,
            "shell_crlf_issues": 0,
        }

    def to_dict(self) -> dict[str, object]:
        """Override to include encoding-specific statistics."""
        base = super().to_dict()
        base["encoding_stats"] = self.stats
        return base


# =============================================================================
# Encoding Detection Utilities
# =============================================================================


def is_binary_file(file_path: Path) -> bool:
    """Check if a file is binary based on extension or content."""
    # Check extension first (fast path)
    if file_path.suffix.lower() in BINARY_EXTENSIONS:
        return True

    # Check file content for null bytes (binary indicator)
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(8192)
            return b"\x00" in chunk
    except (OSError, PermissionError):
        return True  # Treat unreadable files as binary


def should_skip_directory(dir_name: str) -> bool:
    """Check if a directory should be skipped during scanning."""
    if dir_name in SKIP_DIRS:
        return True
    for skip_pattern in SKIP_DIRS:
        if "*" in skip_pattern:
            pattern = skip_pattern.replace("*", ".*")
            if re.match(pattern, dir_name):
                return True
    return False


def is_text_file(file_path: Path) -> bool:
    """Determine if file should be treated as text based on extension."""
    suffix = file_path.suffix.lower()
    # Explicit text extensions
    if suffix in TEXT_EXTENSIONS:
        return True
    # Shell scripts without extension (check shebang)
    if not suffix:
        try:
            with open(file_path, "rb") as f:
                first_line = f.readline(128)
                return first_line.startswith(b"#!")
        except (OSError, PermissionError):
            return False
    return False


# =============================================================================
# Encoding Validation Functions
# =============================================================================


def check_utf8_encoding(content: bytes, file_path: str, report: EncodingValidationReport) -> bool:
    """Check if file content is valid UTF-8.

    Rule 1: UTF-8 encoding required (all files)

    Args:
        content: Raw file bytes
        file_path: Relative path for error messages
        report: Report to add results to

    Returns:
        True if valid UTF-8, False otherwise
    """
    try:
        content.decode("utf-8")
        return True
    except UnicodeDecodeError as e:
        report.critical(f"File is not valid UTF-8: {file_path} (error at byte {e.start}: {e.reason})")
        report.stats["utf8_issues"] += 1
        return False


def check_bom(content: bytes, file_path: str, report: EncodingValidationReport) -> bool:
    """Check for Byte Order Mark (BOM) which should not be present.

    Rule 2: No BOM (Byte Order Mark) detection

    Args:
        content: Raw file bytes
        file_path: Relative path for error messages
        report: Report to add results to

    Returns:
        True if no BOM found, False otherwise
    """
    # UTF-8 BOM
    if content.startswith(b"\xef\xbb\xbf"):
        report.major(f"File has UTF-8 BOM (should be UTF-8 without BOM): {file_path}")
        report.stats["bom_issues"] += 1
        return False

    # UTF-16 LE BOM
    if content.startswith(b"\xff\xfe"):
        report.critical(f"File has UTF-16 LE BOM (must use UTF-8): {file_path}")
        report.stats["bom_issues"] += 1
        return False

    # UTF-16 BE BOM
    if content.startswith(b"\xfe\xff"):
        report.critical(f"File has UTF-16 BE BOM (must use UTF-8): {file_path}")
        report.stats["bom_issues"] += 1
        return False

    # UTF-32 LE BOM
    if content.startswith(b"\xff\xfe\x00\x00"):
        report.critical(f"File has UTF-32 LE BOM (must use UTF-8): {file_path}")
        report.stats["bom_issues"] += 1
        return False

    # UTF-32 BE BOM
    if content.startswith(b"\x00\x00\xfe\xff"):
        report.critical(f"File has UTF-32 BE BOM (must use UTF-8): {file_path}")
        report.stats["bom_issues"] += 1
        return False

    return True


def check_json_unicode(content: str, file_path: str, report: EncodingValidationReport) -> bool:
    """Validate proper Unicode handling in JSON files.

    Rule 3: Proper Unicode handling in JSON

    Args:
        content: File content as string
        file_path: Relative path for error messages
        report: Report to add results to

    Returns:
        True if JSON Unicode is valid, False otherwise
    """
    if not file_path.endswith(".json"):
        return True

    try:
        # Parse JSON to verify Unicode handling
        json.loads(content)
        return True
    except json.JSONDecodeError as e:
        # Check if it's specifically a Unicode issue
        if "unicode" in str(e).lower() or "utf" in str(e).lower():
            report.major(f"JSON Unicode error in {file_path}: {e}")
            report.stats["unicode_issues"] += 1
            return False
        # Other JSON errors handled by JSON validator
        return True


def check_escape_sequences(content: str, file_path: str, report: EncodingValidationReport) -> bool:
    """Check for improperly escaped special characters.

    Rule 4: Special characters properly escaped

    Args:
        content: File content as string
        file_path: Relative path for error messages
        report: Report to add results to

    Returns:
        True if escaping is valid, False otherwise
    """
    issues_found = False

    # Check for raw control characters (except newlines and tabs)
    # These should be escaped in most contexts
    control_chars = re.findall(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", content)
    if control_chars:
        unique_chars = set(control_chars)
        char_codes = ", ".join(f"0x{ord(c):02x}" for c in unique_chars)
        report.minor(f"File contains raw control characters ({char_codes}): {file_path}")
        report.stats["escape_issues"] += 1
        issues_found = True

    # For JSON files, check for unescaped characters that should be escaped
    if file_path.endswith(".json"):
        # Detect bare newlines inside string values (should be \n)
        # This is a heuristic - proper parsing would require JSON parsing
        lines = content.split("\n")
        for _line_num, line in enumerate(lines, 1):
            # Check for tabs that might need escaping in JSON strings
            if "\t" in line and '"' in line:
                # Very rough heuristic: tab between quotes might need escaping
                # Only report if it looks like unescaped tab in string
                pass  # JSON parser handles this - skip false positives

    return not issues_found


def check_line_endings(content: bytes, file_path: str, suffix: str, report: EncodingValidationReport) -> bool:
    """Check line endings match requirements for file type.

    Rule 5: Line endings: LF for source files (.py, .sh, .md, .json)
    Rule 6: Shell scripts: LF endings required (not CRLF)
    Rule 7: Batch scripts (.bat, .cmd): CRLF allowed

    Args:
        content: Raw file bytes
        file_path: Relative path for error messages
        suffix: File extension
        report: Report to add results to

    Returns:
        True if line endings are valid, False otherwise
    """
    has_crlf = b"\r\n" in content
    _has_lf = b"\n" in content and not has_crlf
    has_cr_only = b"\r" in content and b"\n" not in content
    has_mixed = has_crlf and (content.replace(b"\r\n", b"").count(b"\n") > 0)

    # Rule 7: Batch scripts can use CRLF
    if suffix in BATCH_EXTENSIONS:
        if has_cr_only:
            report.minor(f"Batch script has old Mac-style CR line endings: {file_path}")
            report.stats["line_ending_issues"] += 1
            return False
        # CRLF is acceptable for batch files
        return True

    # Rule 6: Shell scripts MUST use LF (CRLF breaks them)
    if suffix in SHELL_EXTENSIONS:
        if has_crlf:
            report.critical(f"Shell script has CRLF line endings (will break execution): {file_path}")
            report.stats["shell_crlf_issues"] += 1
            return False
        if has_cr_only:
            report.critical(f"Shell script has CR-only line endings (will break execution): {file_path}")
            report.stats["shell_crlf_issues"] += 1
            return False
        if has_mixed:
            report.major(f"Shell script has mixed line endings: {file_path}")
            report.stats["shell_crlf_issues"] += 1
            return False
        return True

    # Rule 5: Source files should use LF
    if suffix in LF_REQUIRED_EXTENSIONS:
        if has_crlf:
            report.minor(f"Source file has CRLF line endings (should use LF): {file_path}")
            report.stats["line_ending_issues"] += 1
            return False
        if has_cr_only:
            report.minor(f"Source file has old Mac-style CR line endings: {file_path}")
            report.stats["line_ending_issues"] += 1
            return False
        if has_mixed:
            report.minor(f"Source file has mixed line endings: {file_path}")
            report.stats["line_ending_issues"] += 1
            return False

    return True


# =============================================================================
# Plugin-Wide Validation
# =============================================================================


def validate_file(file_path: Path, plugin_path: Path, report: EncodingValidationReport) -> None:
    """Run all encoding validations on a single file.

    Args:
        file_path: Absolute path to the file
        plugin_path: Root plugin path for relative path calculation
        report: Report to add results to
    """
    rel_path = str(file_path.relative_to(plugin_path))
    suffix = file_path.suffix.lower()

    try:
        # Read raw bytes for encoding checks
        with open(file_path, "rb") as f:
            content_bytes = f.read()

        report.stats["files_scanned"] += 1

        # Rule 1: UTF-8 encoding check
        is_utf8 = check_utf8_encoding(content_bytes, rel_path, report)

        # Rule 2: BOM check
        check_bom(content_bytes, rel_path, report)

        # Only proceed with text content checks if UTF-8 is valid
        if is_utf8:
            content_str = content_bytes.decode("utf-8")

            # Rule 3: JSON Unicode handling
            check_json_unicode(content_str, rel_path, report)

            # Rule 4: Escape sequences
            check_escape_sequences(content_str, rel_path, report)

        # Rules 5-7: Line endings (can check on raw bytes)
        check_line_endings(content_bytes, rel_path, suffix, report)

    except (OSError, PermissionError) as e:
        report.minor(f"Cannot read file: {rel_path} ({e})")
        report.stats["files_skipped"] += 1


def validate_encoding(plugin_path: Path) -> EncodingValidationReport:
    """Run all encoding validations on a plugin directory.

    Performs comprehensive encoding analysis including:
    1. UTF-8 encoding validation
    2. BOM detection
    3. JSON Unicode handling
    4. Escape sequence validation
    5. Line ending checks (LF vs CRLF)
    6. Shell script line ending enforcement
    7. Batch script CRLF allowance

    Args:
        plugin_path: Path to the plugin directory

    Returns:
        EncodingValidationReport with all encoding findings
    """
    report = EncodingValidationReport()

    # Verify plugin path exists
    if not plugin_path.exists():
        report.critical(f"Plugin path does not exist: {plugin_path}")
        return report

    if not plugin_path.is_dir():
        report.critical(f"Plugin path is not a directory: {plugin_path}")
        return report

    report.info(f"Starting encoding scan of: {plugin_path}")

    # Walk through all files
    for root, dirs, files in os.walk(plugin_path):
        # Filter out directories to skip
        dirs[:] = [d for d in dirs if not should_skip_directory(d)]

        for filename in files:
            file_path = Path(root) / filename

            # Skip binary files
            if is_binary_file(file_path):
                report.stats["files_skipped"] += 1
                continue

            # Only check text files
            if is_text_file(file_path) or file_path.suffix.lower() in TEXT_EXTENSIONS:
                validate_file(file_path, plugin_path, report)
            else:
                report.stats["files_skipped"] += 1

    # Report scan statistics
    report.info(
        f"Scanned {report.stats['files_scanned']} files, skipped {report.stats['files_skipped']} binary/other files"
    )

    # Add passed messages for clean categories
    if report.stats["utf8_issues"] == 0:
        report.passed("All files are valid UTF-8")
    if report.stats["bom_issues"] == 0:
        report.passed("No BOM detected in any file")
    if report.stats["unicode_issues"] == 0:
        report.passed("JSON Unicode handling is correct")
    if report.stats["escape_issues"] == 0:
        report.passed("No improper escape sequences detected")
    if report.stats["line_ending_issues"] == 0 and report.stats["shell_crlf_issues"] == 0:
        report.passed("All line endings are correct for file types")

    return report


# =============================================================================
# CLI Main
# =============================================================================


def main() -> int:
    """CLI entry point for standalone encoding validation."""
    parser = argparse.ArgumentParser(
        description="Encoding validation for Claude Code plugins",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Encoding Checks Performed:
  1. UTF-8 encoding required (all text files)
  2. No BOM (Byte Order Mark) detection
  3. Proper Unicode handling in JSON files
  4. Special characters properly escaped
  5. Line endings: LF for source files (.py, .sh, .md, .json)
  6. Shell scripts: LF endings required (CRLF breaks execution)
  7. Batch scripts (.bat, .cmd): CRLF allowed

Exit Codes:
  0 - All checks passed
  1 - CRITICAL issues found (must fix)
  2 - MAJOR issues found (should fix)
  3 - MINOR issues found (recommended to fix)
        """,
    )
    parser.add_argument("plugin_path", type=Path, help="Path to the plugin directory to validate")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show all results including INFO and PASSED")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--strict", action="store_true", help="Strict mode — NIT issues also block validation")

    args = parser.parse_args()

    # Resolve to absolute path so relative_to() works correctly
    plugin_path = args.plugin_path.resolve()

    # Verify this is a plugin directory
    if not plugin_path.is_dir():
        print(f"Error: {plugin_path} is not a directory", file=sys.stderr)
        return 1
    if not (plugin_path / ".claude-plugin").is_dir():
        print(
            f"Error: No Claude Code plugin found at {plugin_path}\nExpected a .claude-plugin/ directory.",
            file=sys.stderr,
        )
        return 1

    # Run validation
    report = validate_encoding(plugin_path)

    # Output results
    if args.json:
        output = report.to_dict()
        output["plugin_path"] = str(plugin_path)
        print(json.dumps(output, indent=2))
    else:
        print_results_by_level(report, verbose=args.verbose)
        print_report_summary(report, title=f"Encoding Validation: {plugin_path.name}")

    if args.strict:
        return report.exit_code_strict()
    return report.exit_code


if __name__ == "__main__":
    sys.exit(main())
