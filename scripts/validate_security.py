#!/usr/bin/env python3
"""
Claude Plugins Validation - Security Module

Performs comprehensive security validation across the entire plugin.
This module implements security checks that must run BEFORE any allowlists.

Security Checks Implemented:
1. Injection Detection (command substitution, variable expansion, eval patterns)
2. Path Traversal Blocking (../, absolute paths, Windows paths)
3. Secret Detection (AWS keys, private keys, API tokens)
4. Hardcoded User Path Detection (/Users/xxx/, /home/xxx/)
5. Dangerous File Detection (.env, credentials.json, etc.)
6. Script Permission Check (executable, shebang, world-writable)
7. Plugin-Wide Recursive Scan
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
from pathlib import Path

from cpv_validation_common import (
    DANGEROUS_FILES,
    SECRET_PATTERNS,
    SKIP_DIRS,
    USER_PATH_PATTERNS,
    ValidationReport,
    print_report_summary,
    print_results_by_level,
)

# =============================================================================
# Injection Detection Patterns
# =============================================================================

# Command substitution patterns - MUST be checked BEFORE any allowlist
COMMAND_SUBSTITUTION_PATTERNS = [
    # $(command) - POSIX command substitution
    (re.compile(r"\$\([^)]+\)"), "Command substitution $(...) detected"),
    # `command` - Legacy backtick command substitution
    (re.compile(r"`[^`]+`"), "Command substitution `...` detected"),
]

# Variable expansion in unsafe contexts (unquoted)
# This pattern detects $VAR without surrounding quotes that could be injection vectors
UNSAFE_VARIABLE_PATTERNS = [
    # Unquoted variable at start of command or after pipe/semicolon
    (
        re.compile(r"(?:^|[|;&])\s*\$[A-Za-z_][A-Za-z0-9_]*(?:\s|$|[|;&])"),
        "Unquoted variable expansion may be unsafe",
    ),
    # Variable in arithmetic context without braces
    (
        re.compile(r"\[\[\s*\$[A-Za-z_][A-Za-z0-9_]*\s*(?:==|!=|<|>|-eq|-ne|-lt|-gt)"),
        "Unquoted variable in comparison",
    ),
]

# Pipe to shell patterns - extremely dangerous
PIPE_TO_SHELL_PATTERNS = [
    (re.compile(r"\|\s*sh\b"), "Pipe to sh detected"),
    (re.compile(r"\|\s*bash\b"), "Pipe to bash detected"),
    (re.compile(r"\|\s*zsh\b"), "Pipe to zsh detected"),
    (re.compile(r"\|\s*ksh\b"), "Pipe to ksh detected"),
    (re.compile(r"\|\s*source\b"), "Pipe to source detected"),
    (re.compile(r"\|\s*\.\s"), "Pipe to dot (source) detected"),
]

# Eval patterns - code execution risks
EVAL_PATTERNS = [
    (re.compile(r"\beval\s+"), "eval command detected"),
    (re.compile(r"\bexec\s+"), "exec command detected"),
    # Python-specific
    (re.compile(r"\beval\s*\("), "Python eval() detected"),
    (re.compile(r"\bexec\s*\("), "Python exec() detected"),
    (re.compile(r"\bcompile\s*\([^)]*\bexec\b"), "Python compile() with exec mode"),
    # JavaScript-specific
    (re.compile(r"\bFunction\s*\("), "JavaScript Function constructor (eval-like)"),
    (re.compile(r"\bnew\s+Function\s*\("), "JavaScript new Function() (eval-like)"),
]

# =============================================================================
# Path Traversal Patterns
# =============================================================================

PATH_TRAVERSAL_PATTERNS = [
    # Directory traversal
    (re.compile(r"\.\./"), "Path traversal ../ detected"),
    (re.compile(r"\.\.\\"), "Path traversal ..\\ detected"),
    # Absolute paths (except environment variable placeholders)
    (
        re.compile(
            r"(?<!\$\{CLAUDE_PLUGIN_ROOT\})(?<!\$\{CLAUDE_PROJECT_DIR\})(?<![\w$\{])/(?:usr|etc|var|tmp|opt|bin|sbin|lib|root)/"
        ),
        "Absolute Unix system path detected",
    ),
    # Windows absolute paths
    (re.compile(r"[A-Za-z]:\\"), "Windows absolute path detected"),
]

# =============================================================================
# Binary File Detection
# =============================================================================

# File extensions that are typically binary
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
# Security Validation Functions
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
    # Direct match
    if dir_name in SKIP_DIRS:
        return True
    # Wildcard patterns (e.g., *.egg-info)
    for skip_pattern in SKIP_DIRS:
        if "*" in skip_pattern:
            # Convert glob pattern to regex
            pattern = skip_pattern.replace("*", ".*")
            if re.match(pattern, dir_name):
                return True
    return False


def is_validator_script(file_path: str) -> bool:
    """Check if file is a validator script that contains intentional pattern definitions.

    Validator scripts contain regex patterns, example shebangs, and documentation
    that would trigger false positives. These are safe to skip for certain checks.
    """
    file_lower = file_path.lower()
    # Validator scripts that contain intentional pattern definitions
    return ("validate_" in file_lower and file_lower.endswith(".py")) or "cpv_validation_common" in file_lower


def scan_for_injection(content: str, file_path: str, report: ValidationReport) -> int:
    """Scan content for injection patterns. Returns count of issues found.

    CRITICAL: This check runs BEFORE any allowlist processing.
    Note: Shell scripts (.sh, .bash) legitimately use command substitution,
    so we only flag command substitution in non-shell files where it's unexpected.
    """
    issues_found = 0
    lines = content.split("\n")

    file_lower = file_path.lower()

    # Determine if file is markdown - backticks are code formatting
    is_markdown = file_lower.endswith((".md", ".mdx", ".markdown"))

    # Determine if file is a shell script - command substitution is expected
    is_shell_script = file_lower.endswith((".sh", ".bash", ".zsh", ".ksh"))

    # Determine if file is a test file - test files often have mock/example content
    is_test_file = (
        "test_" in file_lower or "_test.py" in file_lower or "/tests/" in file_lower or "\\tests\\" in file_lower
    )

    # Determine if file is a validator script - they contain intentional patterns
    is_validator = is_validator_script(file_path)

    # Skip all injection checks for validator scripts (they define patterns)
    if is_validator:
        return 0

    # Skip command substitution checks for shell scripts (it's expected) and markdown/tests
    skip_command_sub = is_shell_script or is_markdown or is_test_file

    for line_num, line in enumerate(lines, start=1):
        # Skip comment-only lines in shell scripts
        stripped = line.strip()
        if stripped.startswith("#") and not stripped.startswith("#!"):
            continue

        # Check command substitution (CRITICAL) - but not in shell scripts where it's expected
        if not skip_command_sub:
            for pattern, msg in COMMAND_SUBSTITUTION_PATTERNS:
                if pattern.search(line):
                    report.critical(f"{msg}: {line.strip()[:80]}", file_path, line_num)
                    issues_found += 1

        # Check pipe to shell (CRITICAL) - dangerous in any context
        for pattern, msg in PIPE_TO_SHELL_PATTERNS:
            # Skip if line looks like documentation (markdown table)
            if "|" in line and line.count("|") >= 2 and ("object" in line.lower() or "string" in line.lower()):
                continue
            if pattern.search(line):
                report.critical(f"{msg}: {line.strip()[:80]}", file_path, line_num)
                issues_found += 1

        # Check eval patterns (CRITICAL)
        for pattern, msg in EVAL_PATTERNS:
            if pattern.search(line):
                report.critical(f"{msg}: {line.strip()[:80]}", file_path, line_num)
                issues_found += 1

        # Check unsafe variable expansion (MAJOR - context-dependent)
        for pattern, msg in UNSAFE_VARIABLE_PATTERNS:
            if pattern.search(line):
                report.major(f"{msg}: {line.strip()[:80]}", file_path, line_num)
                issues_found += 1

    return issues_found


def scan_for_path_traversal(content: str, file_path: str, report: ValidationReport) -> int:
    """Scan content for path traversal patterns. Returns count of issues found.

    Note: Documentation files (.md) often contain examples showing path syntax.
    We skip path checks for markdown documentation to avoid false positives.
    """
    issues_found = 0
    lines = content.split("\n")

    file_lower = file_path.lower()

    # Skip path checks for validator scripts - they contain intentional pattern definitions
    if is_validator_script(file_path):
        return 0

    # Skip path checks for markdown documentation - they contain examples
    if file_lower.endswith((".md", ".mdx", ".markdown")):
        return 0

    # Skip path checks for test files - they contain example data
    if "test_" in file_lower or "_test.py" in file_lower or "/tests/" in file_lower:
        return 0

    for line_num, line in enumerate(lines, start=1):
        # Skip comment-only lines
        stripped = line.strip()
        if stripped.startswith("#") and not stripped.startswith("#!"):
            continue

        # Skip shebang lines entirely - they legitimately reference system paths
        if stripped.startswith("#!"):
            continue

        for pattern, msg in PATH_TRAVERSAL_PATTERNS:
            if pattern.search(line):
                report.critical(f"{msg}: {line.strip()[:80]}", file_path, line_num)
                issues_found += 1

    return issues_found


def scan_for_secrets(content: str, file_path: str, report: ValidationReport) -> int:
    """Scan content for secret patterns. Returns count of issues found."""
    issues_found = 0
    lines = content.split("\n")

    for line_num, line in enumerate(lines, start=1):
        for pattern, secret_type in SECRET_PATTERNS:
            if pattern.search(line):
                # Mask the actual secret in the report
                masked_line = line.strip()[:40] + "..." if len(line.strip()) > 40 else line.strip()
                report.critical(f"{secret_type} detected: {masked_line}", file_path, line_num)
                issues_found += 1

    return issues_found


def scan_for_user_paths(content: str, file_path: str, report: ValidationReport) -> int:
    """Scan content for hardcoded user paths. Returns count of issues found.

    Note: Validator scripts and documentation contain pattern examples that would
    trigger false positives. We skip those files.
    """
    issues_found = 0
    lines = content.split("\n")

    file_lower = file_path.lower()

    # Skip validator scripts - they contain pattern definitions for detecting user paths
    if is_validator_script(file_path):
        return 0

    # Skip markdown documentation - they contain examples
    if file_lower.endswith((".md", ".mdx", ".markdown")):
        return 0

    # Skip test files - they contain example data
    if "test_" in file_lower or "_test.py" in file_lower or "/tests/" in file_lower:
        return 0

    for line_num, line in enumerate(lines, start=1):
        for pattern in USER_PATH_PATTERNS:
            match = pattern.search(line)
            if match:
                report.major(
                    f"Hardcoded user path detected (use ${{CLAUDE_PLUGIN_ROOT}} instead): {match.group()}",
                    file_path,
                    line_num,
                )
                issues_found += 1

    return issues_found


def check_dangerous_files(plugin_path: Path, report: ValidationReport) -> int:
    """Check for presence of dangerous files in the plugin. Returns count found."""
    issues_found = 0

    for root, dirs, files in os.walk(plugin_path):
        # Skip hidden and cache directories
        dirs[:] = [d for d in dirs if not should_skip_directory(d)]

        for filename in files:
            if filename in DANGEROUS_FILES:
                full_path = Path(root) / filename
                rel_path = full_path.relative_to(plugin_path)
                report.critical(f"Dangerous file detected: {rel_path}")
                issues_found += 1

    return issues_found


def check_script_permissions(plugin_path: Path, report: ValidationReport) -> int:
    """Check script files for proper permissions. Returns count of issues found."""
    issues_found = 0

    for root, dirs, files in os.walk(plugin_path):
        # Skip hidden and cache directories
        dirs[:] = [d for d in dirs if not should_skip_directory(d)]

        for filename in files:
            file_path = Path(root) / filename
            rel_path = file_path.relative_to(plugin_path)

            # Check shell scripts
            if filename.endswith(".sh"):
                try:
                    file_stat = file_path.stat()
                    mode = file_stat.st_mode

                    # Check if executable
                    if not (mode & stat.S_IXUSR):
                        report.minor(f"Shell script is not executable: {rel_path}")
                        issues_found += 1

                    # Check for world-writable (security risk)
                    if mode & stat.S_IWOTH:
                        report.critical(f"Script is world-writable: {rel_path}")
                        issues_found += 1

                    # Check for proper shebang
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        first_line = f.readline()
                        if not first_line.startswith("#!"):
                            report.minor(f"Shell script missing shebang: {rel_path}")
                            issues_found += 1
                        elif "bash" not in first_line and "sh" not in first_line:
                            report.info(f"Shell script has non-standard shebang: {first_line.strip()}", str(rel_path))

                except (OSError, PermissionError) as e:
                    report.major(f"Cannot check script permissions: {rel_path} ({e})")
                    issues_found += 1

            # Check Python scripts
            elif filename.endswith(".py"):
                try:
                    file_stat = file_path.stat()
                    mode = file_stat.st_mode

                    # Check for world-writable
                    if mode & stat.S_IWOTH:
                        report.critical(f"Python script is world-writable: {rel_path}")
                        issues_found += 1

                except (OSError, PermissionError) as e:
                    report.major(f"Cannot check script permissions: {rel_path} ({e})")
                    issues_found += 1

    return issues_found


def scan_all_files(plugin_path: Path, report: ValidationReport) -> dict[str, int]:
    """Recursively scan all text files in the plugin for security issues.

    Returns a dictionary with counts of issues found by category.
    """
    stats = {
        "files_scanned": 0,
        "files_skipped": 0,
        "injection_issues": 0,
        "path_traversal_issues": 0,
        "secret_issues": 0,
        "user_path_issues": 0,
    }

    for root, dirs, files in os.walk(plugin_path):
        # Filter out directories to skip
        dirs[:] = [d for d in dirs if not should_skip_directory(d)]

        for filename in files:
            file_path = Path(root) / filename
            rel_path = str(file_path.relative_to(plugin_path))

            # Skip binary files
            if is_binary_file(file_path):
                stats["files_skipped"] += 1
                continue

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                stats["files_scanned"] += 1

                # Run all content scans
                # CRITICAL: Injection detection runs FIRST, before any allowlisting
                stats["injection_issues"] += scan_for_injection(content, rel_path, report)
                stats["path_traversal_issues"] += scan_for_path_traversal(content, rel_path, report)
                stats["secret_issues"] += scan_for_secrets(content, rel_path, report)
                stats["user_path_issues"] += scan_for_user_paths(content, rel_path, report)

            except (OSError, PermissionError) as e:
                report.minor(f"Cannot read file: {rel_path} ({e})")
                stats["files_skipped"] += 1

    return stats


# =============================================================================
# Main Validation Function
# =============================================================================


def validate_security(plugin_path: Path) -> ValidationReport:
    """Run all security validations on a plugin directory.

    This function performs comprehensive security analysis including:
    1. Injection detection (BEFORE any allowlist)
    2. Path traversal blocking
    3. Secret detection
    4. Hardcoded user path detection
    5. Dangerous file detection
    6. Script permission checks
    7. Plugin-wide recursive scan

    Args:
        plugin_path: Path to the plugin directory

    Returns:
        ValidationReport with all security findings
    """
    report = ValidationReport()

    # Verify plugin path exists
    if not plugin_path.exists():
        report.critical(f"Plugin path does not exist: {plugin_path}")
        return report

    if not plugin_path.is_dir():
        report.critical(f"Plugin path is not a directory: {plugin_path}")
        return report

    report.info(f"Starting security scan of: {plugin_path}")

    # Check 1: Dangerous files (quick check first)
    dangerous_count = check_dangerous_files(plugin_path, report)
    if dangerous_count == 0:
        report.passed("No dangerous files detected")

    # Check 2: Script permissions
    permission_issues = check_script_permissions(plugin_path, report)
    if permission_issues == 0:
        report.passed("All scripts have proper permissions")

    # Check 3-6: Full content scan (injection, path traversal, secrets, user paths)
    scan_stats = scan_all_files(plugin_path, report)

    # Report scan statistics
    report.info(f"Scanned {scan_stats['files_scanned']} files, skipped {scan_stats['files_skipped']} binary files")

    # Add passed messages for clean categories
    if scan_stats["injection_issues"] == 0:
        report.passed("No injection patterns detected")
    if scan_stats["path_traversal_issues"] == 0:
        report.passed("No path traversal patterns detected")
    if scan_stats["secret_issues"] == 0:
        report.passed("No secrets detected")
    if scan_stats["user_path_issues"] == 0:
        report.passed("No hardcoded user paths detected")

    return report


# =============================================================================
# CLI Main
# =============================================================================


def main() -> int:
    """CLI entry point for standalone security validation."""
    parser = argparse.ArgumentParser(
        description="Security validation for Claude Code plugins",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Security Checks Performed:
  1. Injection detection (command substitution, eval, pipe to shell)
  2. Path traversal blocking (../, absolute paths)
  3. Secret detection (API keys, private keys, tokens)
  4. Hardcoded user path detection (/Users/xxx/, /home/xxx/)
  5. Dangerous file detection (.env, credentials.json)
  6. Script permission check (executable, shebang, world-writable)
  7. Plugin-wide recursive scan of all text files

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
    report = validate_security(plugin_path)

    # Output results
    if args.json:
        output = report.to_dict()
        output["plugin_path"] = str(plugin_path)
        print(json.dumps(output, indent=2))
    else:
        print_results_by_level(report, verbose=args.verbose)
        print_report_summary(report, title=f"Security Validation: {plugin_path.name}")

    if args.strict:
        return report.exit_code_strict()
    return report.exit_code


if __name__ == "__main__":
    sys.exit(main())
