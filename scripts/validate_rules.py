#!/usr/bin/env python3
"""
Claude Plugins Validation - Rules Validator

Validates rule files (.md) in a plugin's rules/ directory.
Rules are plain markdown files loaded alongside CLAUDE.md into the model context.
They support optional YAML frontmatter with a `paths` field for path-specific rules.

Based on: https://docs.anthropic.com/en/docs/claude-code/memory

Usage:
    uv run python scripts/validate_rules.py path/to/rules/
    uv run python scripts/validate_rules.py path/to/rules/ --verbose
    uv run python scripts/validate_rules.py path/to/rules/ --json

Exit codes:
    0 - All checks passed
    1 - CRITICAL issues found
    2 - MAJOR issues found
    3 - MINOR issues found
    4 - NIT issues found (only in --strict mode)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

import yaml
from cpv_validation_common import (
    SECRET_PATTERNS,
    USER_PATH_PATTERNS,
    ValidationReport,
    check_utf8_encoding,
)

# =============================================================================
# Constants
# =============================================================================

# Token budget for all rules combined (loaded into context alongside CLAUDE.md)
MAX_RULES_TOKENS = 10_000

# Known frontmatter fields for rules files
KNOWN_RULES_FRONTMATTER_FIELDS = {"paths"}

# Character-to-token conversion ratios by script category.
# Based on Claude's BPE tokenizer behavior:
# - Latin/ASCII text: ~4 characters per token (0.25 tokens/char)
# - CJK ideographs (Chinese, Japanese kanji, Korean hanja): ~1 char per token
# - Japanese kana (hiragana, katakana): ~1.5 chars per token
# - Korean hangul syllables: ~1 char per token
# - Cyrillic, Greek, Arabic, Hebrew, Thai, Devanagari: ~2 chars per token
# Conservative estimates (slightly overcount tokens) to warn early.
TOKEN_RATIO_LATIN = 0.25  # 1 token per ~4 chars
TOKEN_RATIO_CJK = 1.0  # 1 token per ~1 char
TOKEN_RATIO_KANA = 0.7  # 1 token per ~1.5 chars
TOKEN_RATIO_OTHER_SCRIPTS = 0.5  # 1 token per ~2 chars


# =============================================================================
# Token Estimation
# =============================================================================


def _classify_char(ch: str) -> str:
    """Classify a character into a script category for token estimation.

    Returns one of: 'cjk', 'kana', 'other_script', 'latin'
    """
    cp = ord(ch)

    # CJK Unified Ideographs and extensions (Chinese, Japanese kanji, Korean hanja)
    if (
        0x4E00 <= cp <= 0x9FFF  # CJK Unified Ideographs
        or 0x3400 <= cp <= 0x4DBF  # CJK Extension A
        or 0x20000 <= cp <= 0x2A6DF  # CJK Extension B
        or 0x2A700 <= cp <= 0x2B73F  # CJK Extension C
        or 0x2B740 <= cp <= 0x2B81F  # CJK Extension D
        or 0xF900 <= cp <= 0xFAFF  # CJK Compatibility Ideographs
    ):
        return "cjk"

    # Japanese Kana
    if (
        0x3040 <= cp <= 0x309F  # Hiragana
        or 0x30A0 <= cp <= 0x30FF  # Katakana
        or 0x31F0 <= cp <= 0x31FF  # Katakana Phonetic Extensions
    ):
        return "kana"

    # Korean Hangul syllables
    if 0xAC00 <= cp <= 0xD7AF:
        return "cjk"  # Hangul syllables tokenize similarly to CJK

    # Korean Jamo
    if 0x1100 <= cp <= 0x11FF or 0x3130 <= cp <= 0x318F:
        return "cjk"

    # Other non-Latin scripts (Cyrillic, Arabic, Hebrew, Thai, Devanagari, etc.)
    cat = unicodedata.category(ch)
    if cat.startswith("L"):  # Letter category
        # Check if it's outside basic Latin + Latin Extended
        if cp > 0x024F:  # Beyond Latin Extended-B
            return "other_script"

    return "latin"


def estimate_tokens(text: str) -> tuple[int, dict[str, int]]:
    """Estimate token count for text using language-aware character ratios.

    Returns:
        (estimated_tokens, char_counts_by_category)
    """
    counts: dict[str, int] = {"cjk": 0, "kana": 0, "other_script": 0, "latin": 0}

    for ch in text:
        if ch.isspace():
            # Whitespace is part of Latin tokenization
            counts["latin"] += 1
            continue
        category = _classify_char(ch)
        counts[category] += 1

    estimated = (
        counts["cjk"] * TOKEN_RATIO_CJK
        + counts["kana"] * TOKEN_RATIO_KANA
        + counts["other_script"] * TOKEN_RATIO_OTHER_SCRIPTS
        + counts["latin"] * TOKEN_RATIO_LATIN
    )

    return int(estimated), counts


def _dominant_language(char_counts: dict[str, int]) -> str:
    """Return the dominant language category for reporting."""
    total = sum(char_counts.values())
    if total == 0:
        return "empty"

    cjk_total = char_counts.get("cjk", 0) + char_counts.get("kana", 0)
    other = char_counts.get("other_script", 0)

    if cjk_total > total * 0.3:
        return "CJK-heavy"
    elif other > total * 0.3:
        return "non-Latin"
    return "Latin"


# =============================================================================
# Validation Functions
# =============================================================================


def validate_rule_file(rule_path: Path, report: ValidationReport, rel_path: str) -> str:
    """Validate a single rule file.

    Returns:
        The text content of the rule (for token counting).
    """
    # Read raw bytes for encoding check
    try:
        raw = rule_path.read_bytes()
    except Exception as e:
        report.major(f"Cannot read rule file: {e}", rel_path)
        return ""

    # UTF-8 encoding check
    check_utf8_encoding(raw, report, rel_path)

    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        report.major("Rule file is not valid UTF-8", rel_path)
        return ""

    # Empty file check
    stripped = content.strip()
    if not stripped:
        report.minor("Rule file is empty", rel_path)
        return ""

    # Frontmatter validation (optional for rules)
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3 and parts[1].strip():
            try:
                frontmatter = yaml.safe_load(parts[1])
                if isinstance(frontmatter, dict):
                    _validate_frontmatter(frontmatter, report, rel_path)
                else:
                    report.minor("Frontmatter is not a YAML mapping", rel_path)
            except yaml.YAMLError as e:
                report.major(f"Invalid YAML frontmatter: {e}", rel_path)
        # Body is the part after frontmatter
        body = parts[2] if len(parts) >= 3 else ""
    else:
        body = content

    # Check body is not just whitespace after frontmatter
    if not body.strip():
        report.minor("Rule file has frontmatter but no content body", rel_path)

    # Scan for secrets
    for pattern, description in SECRET_PATTERNS:
        if re.search(pattern, content):
            report.critical(f"Potential secret found: {description}", rel_path)

    # Scan for private paths
    for pattern in USER_PATH_PATTERNS:
        match = re.search(pattern, content)
        if match:
            report.major(f"Private path found: {match.group()}", rel_path)

    report.passed(f"Rule file validated: {rel_path}", rel_path)
    return content


def _validate_frontmatter(frontmatter: dict[str, Any], report: ValidationReport, rel_path: str) -> None:
    """Validate rule frontmatter fields."""
    # Check for unknown fields
    for key in frontmatter:
        if key not in KNOWN_RULES_FRONTMATTER_FIELDS:
            report.warning(
                f"Unknown frontmatter field '{key}' in rule file — only 'paths' is recognized by Claude Code.",
                rel_path,
            )

    # Validate 'paths' field
    if "paths" in frontmatter:
        paths = frontmatter["paths"]
        if not isinstance(paths, list):
            report.major("'paths' must be an array of glob patterns", rel_path)
        else:
            for i, p in enumerate(paths):
                if not isinstance(p, str):
                    report.major(f"paths[{i}] must be a string, got {type(p).__name__}", rel_path)
                elif not p.strip():
                    report.minor(f"paths[{i}] is empty", rel_path)


def validate_rules_directory(
    rules_dir: Path,
    report: ValidationReport | None = None,
    plugin_root: Path | None = None,
) -> ValidationReport:
    """Validate all rule files in a rules/ directory.

    Args:
        rules_dir: Path to the rules/ directory
        report: Optional existing report to merge into
        plugin_root: Optional plugin root for relative path display

    Returns:
        ValidationReport with all results
    """
    if report is None:
        report = ValidationReport()

    if not rules_dir.is_dir():
        report.info("No rules/ directory found")
        return report

    # Find all .md files recursively
    rule_files = sorted(rules_dir.rglob("*.md"))

    if not rule_files:
        report.info("No rule files (*.md) found in rules/")
        return report

    report.info(f"Found {len(rule_files)} rule file(s)")

    # Validate each rule file and collect content for token counting
    all_content: list[str] = []
    for rule_path in rule_files:
        if plugin_root:
            rel_path = str(rule_path.relative_to(plugin_root))
        else:
            rel_path = str(rule_path.relative_to(rules_dir.parent))
        content = validate_rule_file(rule_path, report, rel_path)
        all_content.append(content)

    # Token size check across ALL rule files combined
    combined_text = "\n".join(all_content)
    estimated_tokens, char_counts = estimate_tokens(combined_text)
    lang = _dominant_language(char_counts)
    total_chars = sum(char_counts.values())

    if estimated_tokens > MAX_RULES_TOKENS:
        report.warning(
            f"Total rules content is ~{estimated_tokens:,} estimated tokens "
            f"({total_chars:,} chars, {lang} content) — exceeds {MAX_RULES_TOKENS:,} token budget. "
            f"Large rules consume model context and may degrade performance. "
            f"Consider splitting into path-specific rules or reducing content.",
        )
    elif estimated_tokens > MAX_RULES_TOKENS * 0.8:
        report.warning(
            f"Total rules content is ~{estimated_tokens:,} estimated tokens "
            f"({total_chars:,} chars, {lang} content) — approaching {MAX_RULES_TOKENS:,} token budget. "
            f"Consider reviewing for redundancy.",
        )
    else:
        report.passed(
            f"Total rules content: ~{estimated_tokens:,} estimated tokens "
            f"({total_chars:,} chars, {lang} content) — within budget"
        )

    return report


# =============================================================================
# Output Functions
# =============================================================================


def print_results(report: ValidationReport, verbose: bool = False) -> None:
    """Print validation results in human-readable format."""
    colors = {
        "CRITICAL": "\033[91m",
        "MAJOR": "\033[93m",
        "MINOR": "\033[94m",
        "NIT": "\033[96m",
        "WARNING": "\033[95m",
        "INFO": "\033[90m",
        "PASSED": "\033[92m",
        "RESET": "\033[0m",
    }

    counts: dict[str, int] = {"CRITICAL": 0, "MAJOR": 0, "MINOR": 0, "NIT": 0, "WARNING": 0, "INFO": 0, "PASSED": 0}
    for r in report.results:
        counts[r.level] += 1

    print("\n" + "=" * 60)
    print("Rules Validation Report")
    print("=" * 60)

    print("\nSummary:")
    print(f"  {colors['CRITICAL']}CRITICAL: {counts['CRITICAL']}{colors['RESET']}")
    print(f"  {colors['MAJOR']}MAJOR:    {counts['MAJOR']}{colors['RESET']}")
    print(f"  {colors['MINOR']}MINOR:    {counts['MINOR']}{colors['RESET']}")
    print(f"  {colors['NIT']}NIT:      {counts['NIT']}{colors['RESET']}")
    print(f"  {colors['WARNING']}WARNING:  {counts['WARNING']}{colors['RESET']}")
    if verbose:
        print(f"  {colors['INFO']}INFO:     {counts['INFO']}{colors['RESET']}")
        print(f"  {colors['PASSED']}PASSED:   {counts['PASSED']}{colors['RESET']}")

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

    print("\n" + "-" * 60)
    if report.exit_code == 0:
        print(f"{colors['PASSED']}✓ All rules checks passed{colors['RESET']}")
    elif report.exit_code == 1:
        print(f"{colors['CRITICAL']}✗ CRITICAL issues — rules will not load{colors['RESET']}")
    elif report.exit_code == 2:
        print(f"{colors['MAJOR']}✗ MAJOR issues found{colors['RESET']}")
    else:
        print(f"{colors['MINOR']}! MINOR issues found{colors['RESET']}")

    print()


def print_json(report: ValidationReport) -> None:
    """Print validation results as JSON."""
    output = {
        "exit_code": report.exit_code,
        "counts": {
            "critical": sum(1 for r in report.results if r.level == "CRITICAL"),
            "major": sum(1 for r in report.results if r.level == "MAJOR"),
            "minor": sum(1 for r in report.results if r.level == "MINOR"),
            "nit": sum(1 for r in report.results if r.level == "NIT"),
            "warning": sum(1 for r in report.results if r.level == "WARNING"),
            "info": sum(1 for r in report.results if r.level == "INFO"),
            "passed": sum(1 for r in report.results if r.level == "PASSED"),
        },
        "results": [{"level": r.level, "message": r.message, "file": r.file, "line": r.line} for r in report.results],
    }
    print(json.dumps(output, indent=2))


# =============================================================================
# Main
# =============================================================================


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate Claude Code rule files")
    parser.add_argument("path", help="Path to rules/ directory or plugin root")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all results")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--strict", action="store_true", help="Strict mode — NIT issues also block validation")
    args = parser.parse_args()

    path = Path(args.path).resolve()
    if not path.exists():
        print(f"Error: {path} does not exist", file=sys.stderr)
        return 1

    # If path is a plugin root, look for rules/ subdir
    if path.is_dir() and (path / "rules").is_dir():
        rules_dir = path / "rules"
        plugin_root = path
    elif path.is_dir():
        rules_dir = path
        plugin_root = path.parent
    else:
        print(f"Error: {path} is not a directory", file=sys.stderr)
        return 1

    # Verify content type — rules directory must contain .md rule files
    if not list(rules_dir.glob("*.md")):
        print(f"Error: No rule files (.md) found in {rules_dir}", file=sys.stderr)
        return 1

    report = validate_rules_directory(rules_dir, plugin_root=plugin_root)

    if args.json:
        print_json(report)
    else:
        print_results(report, args.verbose)

    if args.strict:
        return report.exit_code_strict()
    return report.exit_code


if __name__ == "__main__":
    sys.exit(main())
