#!/usr/bin/env python3
"""
Claude Plugins Validation - Comprehensive Skill Validator

Validates individual skill directories using 210+ validation techniques from:
- AgentSkills OpenSpec (skills-ref library) - 44 rules + i18n, NFKC normalization
- Nixtla Quality Standards (strict mode) - Required sections, description quality
- Meta-Skill Validation - 8+1 Pillars, token budgets, checklists
- Component Validators - Multi-scale scoring (0-3), letter grading (A-F)
- Official Anthropic Documentation - XML tags, vague names, gerund naming,
  reference file TOC, nesting depth, Windows path detection, MCP tool format,
  time-sensitive info detection, metadata validation, scripts shebang check
- Claude Code skills.md - String substitutions, dynamic context, model field,
  argument-hint, hooks field validation
- Best Practices - Checklist patterns, examples patterns, workflow steps,
  feedback loops, package dependency detection

Usage:
    uv run python scripts/validate_skill_comprehensive.py path/to/skill/
    uv run python scripts/validate_skill_comprehensive.py path/to/skill/ --verbose
    uv run python scripts/validate_skill_comprehensive.py path/to/skill/ --json
    uv run python scripts/validate_skill_comprehensive.py path/to/skill/ --strict  # Nixtla strict mode
    uv run python scripts/validate_skill_comprehensive.py path/to/skill/ --pillars # 8+1 Pillars validation

Exit codes:
    0 - All checks passed (Grade A/B)
    1 - CRITICAL issues found (Grade F)
    2 - MAJOR issues found (Grade D)
    3 - MINOR issues found (Grade C)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml
from cpv_validation_common import (
    BUILTIN_AGENT_TYPES,
    EXIT_CRITICAL,
    EXIT_MAJOR,
    EXIT_MINOR,
    EXIT_OK,
    VALID_CONTEXT_VALUES,
    Level,
    validate_toc_embedding,
)
from cpv_validation_common import (
    ValidationReport as BaseValidationReport,
)
from cpv_validation_common import (
    ValidationResult as BaseValidationResult,
)

# =============================================================================
# Constants from Multiple Validation Sources
# =============================================================================

# Level type imported from cpv_validation_common

# Multi-scale scoring (0-3) from agent-validator
Score = Literal[0, 1, 2, 3]

# --- AgentSkills OpenSpec Constants ---
MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_COMPATIBILITY_LENGTH = 500

# AgentSkills OpenSpec allowed fields (strict whitelist)
OPENSPEC_ALLOWED_FIELDS = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
}

# --- Claude Code Extended Fields ---
CLAUDE_CODE_FIELDS = {
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

# --- Nixtla/Enterprise Extended Fields ---
ENTERPRISE_REQUIRED_FIELDS = {"name", "description", "allowed-tools", "version", "author", "license"}
ENTERPRISE_OPTIONAL_FIELDS = {"model", "disable-model-invocation", "mode", "tags", "metadata"}
DEPRECATED_FIELDS = {"when_to_use"}

# Combine all known fields (includes OpenSpec, Claude Code, and Enterprise fields)
ALL_KNOWN_FIELDS = (
    OPENSPEC_ALLOWED_FIELDS | CLAUDE_CODE_FIELDS | ENTERPRISE_REQUIRED_FIELDS | ENTERPRISE_OPTIONAL_FIELDS
)

# --- Token Budget Constants ---
MAX_SKILL_LINES = 500  # Warning threshold
MAX_SKILL_LINES_ERROR = 800  # Error threshold
MAX_WORD_COUNT_WARN = 3500
MAX_WORD_COUNT_ERROR = 5000
MAX_DESCRIPTION_WARN = 200
MAX_FRONTMATTER_CHARS_WARN = 12000
MAX_FRONTMATTER_CHARS_ERROR = 15000

# --- Valid Values ---
# VALID_CONTEXT_VALUES and BUILTIN_AGENT_TYPES imported from cpv_validation_common
VALID_MODEL_VALUES = {"sonnet", "opus", "haiku", "inherit"}

# Valid Claude Code tools (2025)
VALID_TOOLS = {
    "Read",
    "Write",
    "Edit",
    "Bash",
    "Grep",
    "Glob",
    "WebFetch",
    "WebSearch",
    "Task",
    "NotebookEdit",
    "Skill",
    "AskUserQuestion",
    "EnterPlanMode",
    "ExitPlanMode",
    "EnterWorktree",
    "TaskCreate",
    "TaskUpdate",
    "TaskList",
    "TaskGet",
    "TaskStop",
    "ToolSearch",
}

# --- Nixtla Strict Mode Required Sections ---
REQUIRED_SECTIONS = [
    "## Overview",
    "## Prerequisites",
    "## Instructions",
    "## Output",
    "## Error Handling",
    "## Examples",
    "## Resources",
]

# --- Description Quality Patterns (Nixtla Strict Mode) ---
RE_DESCRIPTION_USE_WHEN = re.compile(r"[Uu]se\s+when\s+", re.IGNORECASE)
RE_DESCRIPTION_TRIGGER_WITH = re.compile(r"[Tt]rigger\s+with\s+", re.IGNORECASE)
RE_FIRST_PERSON = re.compile(r"\b(I\s+can|I\s+will|I\s+am|I\s+help)\b", re.IGNORECASE)
RE_SECOND_PERSON = re.compile(r"\b(You\s+can|You\s+should|You\s+will|You\s+need)\b", re.IGNORECASE)

# --- Path Validation Patterns ---
ABSOLUTE_PATH_PATTERNS = [
    (re.compile(r"/home/\w+/"), "/home/..."),
    (re.compile(r"/Users/\w+/"), "/Users/..."),
    (re.compile(r"[A-Za-z]:\\\\Users\\\\"), "C:\\Users\\..."),
]

# --- Reference Pattern ---
RE_BASEDIR_SCRIPTS = re.compile(r"\{baseDir\}/scripts/([^\s\}]+)")
RE_BASEDIR_REFERENCES = re.compile(r"\{baseDir\}/references/([^\s\}]+)")
RE_BASEDIR_ASSETS = re.compile(r"\{baseDir\}/assets/([^\s\}]+)")

# --- XML Tag Pattern (Anthropic docs forbid XML tags in name/description) ---
RE_XML_TAG = re.compile(r"<[a-zA-Z][^>]*>")

# --- Vague/Generic Name Words (Anthropic docs recommend against these) ---
VAGUE_NAME_WORDS = {
    "helper",
    "helpers",
    "util",
    "utils",
    "utility",
    "utilities",
    "tool",
    "tools",
    "document",
    "documents",
    "data",
    "file",
    "files",
    "misc",
    "general",
    "common",
    "shared",
    "base",
    "core",
}

# --- Gerund Pattern (verb + -ing, recommended by Anthropic docs) ---
RE_GERUND_NAME = re.compile(r"^[a-z]+-[a-z]*ing(-[a-z]+)*$")

# --- Reference File TOC Threshold (Anthropic docs: files > 100 lines need TOC) ---
REFERENCE_TOC_THRESHOLD = 100

# --- Windows Backslash Pattern (any backslash in path context) ---
RE_WINDOWS_PATH = re.compile(r"\\[a-zA-Z_]")

# --- MCP Tool Reference Pattern (Anthropic docs: must use ServerName:tool_name format) ---
# Detects unqualified MCP tool references like "use the read_file tool" instead of "serena:read_file"
RE_MCP_TOOL_UNQUALIFIED = re.compile(
    r"\b(use|call|invoke|run)\s+(the\s+)?([a-z_]+_[a-z_]+)\s+(tool|function)\b",
    re.IGNORECASE,
)

# --- Time-Sensitive Information Pattern (Anthropic docs: avoid dates/versions that will go stale) ---
RE_TIME_SENSITIVE = re.compile(
    r"\b(before|after|until|starting|ending|since|as of)\s+"
    r"(January|February|March|April|May|June|July|August|September|October|November|December|\d{4}|v?\d+\.\d+)",
    re.IGNORECASE,
)

# --- String Substitution Patterns (skills.md: $ARGUMENTS, $ARGUMENTS[N], $N, ${CLAUDE_SESSION_ID}) ---
RE_ARGUMENTS_VAR = re.compile(r"\$ARGUMENTS(?!\[)")  # $ARGUMENTS (not followed by [)
RE_ARGUMENTS_INDEX = re.compile(r"\$ARGUMENTS\[(\d+)\]")  # $ARGUMENTS[N]
RE_SHORTHAND_ARG = re.compile(r"\$(\d+)(?!\d)")  # $N shorthand (e.g., $1, $2)
RE_SESSION_ID_VAR = re.compile(r"\$\{CLAUDE_SESSION_ID\}")

# --- Dynamic Context Injection Pattern (skills.md: `!`command``) ---
RE_DYNAMIC_CONTEXT = re.compile(r"!\s*`[^`]+`")  # Matches `!`command``

# --- Ultrathink Keyword (skills.md: enables extended thinking) ---
RE_ULTRATHINK = re.compile(r"\bultrathink\b", re.IGNORECASE)

# --- Checklist Pattern (best practices: [ ] and [x] checkboxes) ---
RE_CHECKLIST = re.compile(r"^\s*[-*]\s+\[[x ]\]", re.IGNORECASE | re.MULTILINE)

# --- Examples Pattern (best practices: input/output examples) ---
RE_EXAMPLE_BLOCK = re.compile(r"```.*?\n.*?```", re.DOTALL)  # Code blocks
RE_INPUT_OUTPUT = re.compile(r"\b(input|output|example|result)[:：]\s*", re.IGNORECASE)

# --- Workflow Steps Pattern (best practices: numbered workflow steps) ---
RE_WORKFLOW_STEPS = re.compile(r"(?m)^\s*(\d+)\.\s+\S+")

# --- Feedback Loop Pattern (best practices: validate → fix → repeat) ---
RE_FEEDBACK_LOOP = re.compile(
    r"\b(validate|verify|check|test)\s*[→\->]+\s*(fix|correct|update|adjust)",
    re.IGNORECASE,
)

# --- Package Dependency Pattern (best practices: pip install, npm install, etc.) ---
RE_PACKAGE_INSTALL = re.compile(
    r"\b(pip\s+install|npm\s+install|yarn\s+add|cargo\s+add|go\s+get|brew\s+install)\s+\S+",
    re.IGNORECASE,
)

# --- Checklist Copy Pattern (best practices lines 410, 452: complex workflows need copyable checklists) ---
# Exact phrases from Anthropic docs:
#   "Copy this checklist and track your progress:"
#   "Copy this checklist and check off items as you complete them:"
RE_CHECKLIST_COPY_PHRASE = re.compile(
    r"copy\s+this\s+checklist\s+and\s+(track\s+your\s+progress|check\s+off\s+items)",
    re.IGNORECASE,
)

# --- Template Pattern (best practices lines 585-634: output templates) ---
RE_TEMPLATE_STRICT = re.compile(
    r"(ALWAYS\s+use\s+this\s+(exact\s+)?template|use\s+this\s+exact\s+template)",
    re.IGNORECASE,
)
RE_TEMPLATE_FLEXIBLE = re.compile(
    r"(sensible\s+default\s+format|use\s+your\s+(best\s+)?judgment|adjust\s+as\s+needed)",
    re.IGNORECASE,
)

# --- 8+1 Pillars for lang-* and convert-* skills ---
EIGHT_PILLARS = [
    ("Module", ["import", "export", "module", "use", "require", "package", "namespace"]),
    ("Error", ["Result", "Exception", "Error", "try", "catch", "?", "unwrap", "panic"]),
    ("Concurrency", ["async", "await", "thread", "channel", "spawn", "Actor", "mutex", "lock"]),
    ("Metaprogramming", ["macro", "decorator", "@", "derive", "annotation", "quote", "defmacro"]),
    ("Zero/Default", ["null", "None", "nil", "Option", "Maybe", "default", "?", "undefined"]),
    ("Serialization", ["JSON", "serde", "marshal", "encode", "decode", "parse", "serialize"]),
    ("Build", ["Cargo", "npm", "pip", "mix", "make", "package.json", "deps", "go mod"]),
    ("Testing", ["test", "describe", "it", "assert", "expect", "mock", "#[test]", "pytest"]),
]

NINTH_PILLAR = ("Dev Workflow/REPL", ["REPL", "iex", "ghci", "clj", "hot reload", "interactive"])

# Languages requiring 9th pillar
REPL_CENTRIC_LANGUAGES = {"clojure", "elixir", "erlang", "haskell", "fsharp", "f#", "lisp", "scheme", "racket"}

# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class ComprehensiveValidationResult(BaseValidationResult):
    """Extended validation result with category and scoring.

    Extends the canonical ValidationResult (which has level, message, file, line,
    phase, fixable, fix_id) with category grouping and multi-scale scoring.
    """

    category: str | None = None  # For grouping in reports
    score: int = 0  # 0-3 multi-scale score (0=missing, 1=inadequate, 2=adequate, 3=excellent)


@dataclass
class PillarScore:
    """Score for a single pillar (0.0, 0.5, or 1.0)."""

    name: str
    score: float  # 0.0 = missing, 0.5 = partial, 1.0 = full
    notes: str = ""


@dataclass
class ComprehensiveSkillReport(BaseValidationReport):
    """Extended validation report with comprehensive skill scoring.

    Extends the canonical ValidationReport (which has results, fixable_issues,
    valid_items, failed_items, and all base convenience methods) with skill-specific
    fields: skill_path, pillar_scores, category_scores, overall_score, grade.
    """

    skill_path: str = ""
    pillar_scores: list[PillarScore] = field(default_factory=list)
    category_scores: dict[str, float] = field(default_factory=dict)
    overall_score: float = 0.0
    grade: str = "F"

    def add(
        self,
        level: Level,
        message: str,
        file: str | None = None,
        line: int | None = None,
        phase: str | None = None,
        fixable: bool = False,
        fix_id: str | None = None,
        *,
        category: str | None = None,
        score: int = 0,
    ) -> None:
        """Add a validation result with optional category and score."""
        result = ComprehensiveValidationResult(
            level=level,
            message=message,
            file=file,
            line=line,
            phase=phase,
            fixable=fixable,
            fix_id=fix_id,
            category=category,
            score=score,
        )
        self.results.append(result)

    def passed(self, message: str, file: str | None = None, category: str | None = None) -> None:
        """Add a passed check with optional category."""
        self.add("PASSED", message, file, category=category, score=3)

    def info(self, message: str, file: str | None = None, category: str | None = None) -> None:
        """Add an info message with optional category."""
        self.add("INFO", message, file, category=category, score=2)

    def nit(self, message: str, file: str | None = None, line: int | None = None, category: str | None = None) -> None:
        """Add a nit issue -- blocks only in --strict mode."""
        self.add("NIT", message, file, line, category=category)

    def warning(
        self, message: str, file: str | None = None, line: int | None = None, category: str | None = None
    ) -> None:
        """Add a warning -- never blocks validation, always reported."""
        self.add("WARNING", message, file, line, category=category)

    def minor(
        self, message: str, file: str | None = None, line: int | None = None, category: str | None = None
    ) -> None:
        """Add a minor issue with optional category."""
        self.add("MINOR", message, file, line, category=category, score=1)

    def major(
        self, message: str, file: str | None = None, line: int | None = None, category: str | None = None
    ) -> None:
        """Add a major issue with optional category."""
        self.add("MAJOR", message, file, line, category=category, score=0)

    def critical(
        self, message: str, file: str | None = None, line: int | None = None, category: str | None = None
    ) -> None:
        """Add a critical issue with optional category."""
        self.add("CRITICAL", message, file, line, category=category, score=0)

    @property
    def exit_code(self) -> int:
        """Get appropriate exit code based on highest severity issue.

        Uses the canonical exit code constants from cpv_validation_common.
        """
        if self.has_critical:
            return EXIT_CRITICAL
        if self.has_major:
            return EXIT_MAJOR
        if self.has_minor:
            return EXIT_MINOR
        return EXIT_OK

    def calculate_grade(self) -> None:
        """Calculate letter grade based on overall score.

        Uses simplified A/B/C/D/F scale for comprehensive skill reports,
        matching the original grading thresholds used by this validator.
        """
        if self.overall_score >= 90:
            self.grade = "A"
        elif self.overall_score >= 80:
            self.grade = "B"
        elif self.overall_score >= 70:
            self.grade = "C"
        elif self.overall_score >= 60:
            self.grade = "D"
        else:
            self.grade = "F"


# Backward compatibility aliases for tests and internal usage
ValidationResult = ComprehensiveValidationResult
ValidationReport = ComprehensiveSkillReport


# =============================================================================
# Parsing Functions
# =============================================================================


def parse_frontmatter(content: str) -> tuple[dict[str, Any] | None, str, int]:
    """Parse YAML frontmatter from skill content.

    Returns:
        Tuple of (frontmatter_dict, body_content, frontmatter_end_line)
        Returns (None, content, 0) if no frontmatter found
    """
    if not content.startswith("---"):
        return None, content, 0

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, content, 0

    try:
        frontmatter = yaml.safe_load(parts[1])
        if frontmatter is None:
            frontmatter = {}
        body = parts[2]
        fm_end_line = parts[0].count("\n") + parts[1].count("\n") + 2
        return frontmatter, body, fm_end_line
    except yaml.YAMLError:
        return None, content, 0


def find_skill_md(skill_dir: Path) -> Path | None:
    """Find the SKILL.md file (uppercase preferred, lowercase accepted)."""
    for name in ("SKILL.md", "skill.md"):
        path = skill_dir / name
        if path.exists():
            return path
    return None


# =============================================================================
# Validation Functions
# =============================================================================


def validate_skill_md_exists(skill_path: Path, report: ValidationReport) -> bool:
    """Validate SKILL.md exists (required)."""
    skill_md = find_skill_md(skill_path)

    if skill_md is None:
        report.critical("SKILL.md not found (required)", "SKILL.md", category="Structure")
        return False

    if skill_md.name == "skill.md":
        report.minor("SKILL.md should be uppercase (found 'skill.md')", "skill.md", category="Structure")
    else:
        report.passed("SKILL.md exists", "SKILL.md", category="Structure")
    return True


def validate_frontmatter_structure(content: str, report: ValidationReport) -> dict[str, Any] | None:
    """Validate YAML frontmatter structure."""
    if not content.startswith("---"):
        report.info("No YAML frontmatter found (optional but recommended)", "SKILL.md", category="Frontmatter")
        return None

    frontmatter, _, _ = parse_frontmatter(content)

    if frontmatter is None and content.startswith("---"):
        report.critical(
            "Malformed YAML frontmatter (missing closing --- or invalid YAML)",
            "SKILL.md",
            category="Frontmatter",
        )
        return None

    if frontmatter is None:
        return None

    # Check frontmatter size (token budget)
    fm_str = content.split("---", 2)[1] if content.startswith("---") else ""
    fm_chars = len(fm_str)
    if fm_chars > MAX_FRONTMATTER_CHARS_ERROR:
        report.critical(
            f"Frontmatter exceeds {MAX_FRONTMATTER_CHARS_ERROR} characters ({fm_chars} chars)",
            "SKILL.md",
            category="Token Budget",
        )
    elif fm_chars > MAX_FRONTMATTER_CHARS_WARN:
        report.minor(
            f"Frontmatter exceeds {MAX_FRONTMATTER_CHARS_WARN} characters ({fm_chars} chars)",
            "SKILL.md",
            category="Token Budget",
        )

    report.passed("Valid YAML frontmatter", "SKILL.md", category="Frontmatter")
    return frontmatter


def validate_name_field(
    frontmatter: dict[str, Any],
    skill_dir_name: str,
    report: ValidationReport,
    strict_openspec: bool = False,
) -> None:
    """Validate the 'name' frontmatter field with AgentSkills OpenSpec rules."""
    if "name" not in frontmatter:
        if strict_openspec:
            report.critical("Missing required field: 'name'", "SKILL.md", category="Frontmatter")
        else:
            report.info(
                f"No 'name' field (will use directory name: {skill_dir_name})",
                "SKILL.md",
                category="Frontmatter",
            )
        name = skill_dir_name
    else:
        name = frontmatter["name"]
        report.passed(f"'name' field present: {name}", "SKILL.md", category="Frontmatter")

    if not isinstance(name, str):
        report.critical(f"'name' must be a string, got {type(name).__name__}", "SKILL.md", category="Frontmatter")
        return

    # Unicode NFKC normalization (AgentSkills OpenSpec)
    name = unicodedata.normalize("NFKC", name.strip())

    # Length check (max 64 chars)
    if len(name) > MAX_SKILL_NAME_LENGTH:
        report.major(
            f"Skill name exceeds {MAX_SKILL_NAME_LENGTH} characters ({len(name)} chars): {name}",
            "SKILL.md",
            category="Frontmatter",
        )

    # Lowercase check
    if name != name.lower():
        report.major(f"Skill name must be lowercase: {name}", "SKILL.md", category="Frontmatter")

    # Kebab-case format check
    if not re.match(r"^[a-z][a-z0-9-]*[a-z0-9]$", name) and len(name) > 1:
        # Allow Unicode characters for i18n support
        if not all(c.isalnum() or c == "-" for c in name):
            report.major(
                f"Skill name must use only letters, numbers, hyphens: {name}",
                "SKILL.md",
                category="Frontmatter",
            )

    # No leading/trailing hyphens
    if name.startswith("-") or name.endswith("-"):
        report.major("Skill name cannot start or end with a hyphen", "SKILL.md", category="Frontmatter")

    # No consecutive hyphens
    if "--" in name:
        report.major("Skill name cannot contain consecutive hyphens", "SKILL.md", category="Frontmatter")

    # Reserved words check
    name_lower = name.lower()
    if "anthropic" in name_lower or "claude" in name_lower:
        report.major(f"Skill name contains reserved word: {name}", "SKILL.md", category="Frontmatter")

    # XML tag check (Anthropic docs)
    if RE_XML_TAG.search(name):
        report.critical(
            f"Skill name contains XML tags (forbidden): {name}",
            "SKILL.md",
            category="Frontmatter",
        )

    # Vague/generic name check (Anthropic docs)
    name_parts = set(name.split("-"))
    vague_matches = name_parts & VAGUE_NAME_WORDS
    if vague_matches:
        report.minor(
            f"Skill name uses vague/generic word(s): {', '.join(sorted(vague_matches))} - "
            "consider more specific naming (e.g., 'processing-pdfs' instead of 'pdf-helper')",
            "SKILL.md",
            category="Frontmatter",
        )

    # Gerund naming recommendation (Anthropic docs: verb + -ing format preferred)
    if not RE_GERUND_NAME.match(name):
        # Only suggest if name has a reasonable structure already
        if "-" in name and len(name) > 5:
            report.info(
                f"Consider gerund naming pattern (verb + -ing) for skill: {name} "
                "(e.g., 'processing-pdfs', 'analyzing-data', 'building-apis')",
                "SKILL.md",
                category="Frontmatter",
            )

    # Directory name match check (AgentSkills OpenSpec requirement)
    dir_name = unicodedata.normalize("NFKC", skill_dir_name)
    if "name" in frontmatter and dir_name != name:
        if strict_openspec:
            report.major(
                f"Directory name '{skill_dir_name}' must match skill name '{name}'",
                "SKILL.md",
                category="Frontmatter",
            )
        else:
            report.info(
                f"Skill name '{name}' differs from directory name '{skill_dir_name}'",
                "SKILL.md",
                category="Frontmatter",
            )


def validate_description_field(
    frontmatter: dict[str, Any],
    body: str,
    report: ValidationReport,
    strict_mode: bool = False,
) -> None:
    """Validate the 'description' field with Nixtla quality standards."""
    if "description" not in frontmatter:
        if body.strip():
            report.info(
                "No 'description' field (will use first paragraph of content)",
                "SKILL.md",
                category="Frontmatter",
            )
        else:
            report.major(
                "No 'description' field and no body content for fallback",
                "SKILL.md",
                category="Frontmatter",
            )
        return

    desc = frontmatter["description"]
    if not isinstance(desc, str):
        report.major(
            f"'description' must be a string, got {type(desc).__name__}",
            "SKILL.md",
            category="Frontmatter",
        )
        return

    # XML tag check (Anthropic docs forbid XML tags in description)
    if RE_XML_TAG.search(desc):
        report.major(
            "Description contains XML tags (forbidden) - use plain text",
            "SKILL.md",
            category="Description Quality",
        )

    # Length checks
    if len(desc) < 20:
        report.minor("Description is very short (< 20 chars)", "SKILL.md", category="Description Quality")

    if len(desc) > MAX_DESCRIPTION_LENGTH:
        report.major(
            f"Description exceeds {MAX_DESCRIPTION_LENGTH} characters ({len(desc)} chars)",
            "SKILL.md",
            category="Description Quality",
        )
    elif len(desc) > MAX_DESCRIPTION_WARN:
        report.minor(
            f"Description is long ({len(desc)} chars), consider shortening to < {MAX_DESCRIPTION_WARN}",
            "SKILL.md",
            category="Description Quality",
        )

    # Nixtla strict mode quality checks
    if strict_mode:
        # Must include "Use when..." phrase
        if not RE_DESCRIPTION_USE_WHEN.search(desc):
            report.major(
                "Description must include 'Use when ...' phrase (Nixtla strict mode)",
                "SKILL.md",
                category="Description Quality",
            )

        # Must include "Trigger with..." phrase
        if not RE_DESCRIPTION_TRIGGER_WITH.search(desc):
            report.minor(
                "Description should include 'Trigger with ...' phrase (Nixtla strict mode)",
                "SKILL.md",
                category="Description Quality",
            )

        # No first person
        if RE_FIRST_PERSON.search(desc):
            report.major(
                "Description must NOT use first person (I can / I will)",
                "SKILL.md",
                category="Description Quality",
            )

        # No second person
        if RE_SECOND_PERSON.search(desc):
            report.major(
                "Description must NOT use second person (You can / You should)",
                "SKILL.md",
                category="Description Quality",
            )
    else:
        # Non-strict mode - just warn
        if not RE_DESCRIPTION_USE_WHEN.search(desc):
            report.info(
                "Description should include 'Use when ...' phrase for better discoverability",
                "SKILL.md",
                category="Description Quality",
            )

    report.passed("'description' field present", "SKILL.md", category="Frontmatter")


def validate_allowed_tools_field(
    frontmatter: dict[str, Any],
    report: ValidationReport,
    strict_mode: bool = False,
    strict_openspec: bool = False,
) -> None:
    """Validate the 'allowed-tools' field with Nixtla strict mode and OpenSpec support.

    OpenSpec uses space-delimited format: "Bash(jq:*) Bash(git:*)"
    Nixtla uses comma-separated format: "Read, Write, Edit"
    """
    if "allowed-tools" not in frontmatter:
        return

    tools = frontmatter["allowed-tools"]

    # Nixtla strict mode: must be CSV string, not YAML array
    if isinstance(tools, list):
        if strict_mode:
            report.major(
                "'allowed-tools' must be comma-separated string (CSV), not YAML array",
                "SKILL.md",
                category="Frontmatter",
            )
        tool_list = tools
    elif isinstance(tools, str):
        # OpenSpec uses space-delimited format for scoped tools like "Bash(jq:*) Bash(git:*)"
        # Nixtla uses comma-delimited format like "Read, Write, Edit"
        # Detect format by checking for parentheses (scoped tools)
        if "(" in tools and ")" in tools and "," not in tools:
            # OpenSpec space-delimited format with scoped tools
            tool_list = tools.split()
            if strict_openspec:
                report.passed(
                    "'allowed-tools' uses OpenSpec space-delimited format",
                    "SKILL.md",
                    category="Frontmatter",
                )
        elif "," in tools:
            # Comma-delimited format
            tool_list = [t.strip() for t in tools.split(",")]
        else:
            # Single tool or space-delimited simple tools
            tool_list = tools.split()
    else:
        report.major(
            f"'allowed-tools' must be string or list, got {type(tools).__name__}",
            "SKILL.md",
            category="Frontmatter",
        )
        return

    if not tool_list:
        report.minor("'allowed-tools' is empty", "SKILL.md", category="Frontmatter")
        return

    # Validate individual tools
    for tool in tool_list:
        # Handle scoped tools like Bash(git:*)
        base_tool = tool.split("(")[0].strip()
        if base_tool and base_tool not in VALID_TOOLS and not base_tool.startswith("mcp__"):
            report.info(
                f"Unknown tool '{base_tool}' (may be valid if custom MCP tool)",
                "SKILL.md",
                category="Frontmatter",
            )

    # Nixtla strict mode: forbid unscoped Bash
    if strict_mode and "Bash" in tool_list:
        report.major(
            "Unscoped 'Bash' forbidden in strict mode - use scoped Bash(git:*) or Bash(npm:*)",
            "SKILL.md",
            category="Frontmatter",
        )

    # Over-permissioning advisory — not blocking
    if len(tool_list) > 6:
        report.warning(
            f"Many tools permitted ({len(tool_list)}) - consider limiting",
            "SKILL.md",
            category="Frontmatter",
        )

    report.passed(f"'allowed-tools' field valid: {len(tool_list)} tool(s)", "SKILL.md", category="Frontmatter")


def validate_metadata_field(
    frontmatter: dict[str, Any],
    report: ValidationReport,
) -> None:
    """Validate the 'metadata' field (must be string key-value pairs per OpenSpec)."""
    if "metadata" not in frontmatter:
        return

    metadata = frontmatter["metadata"]

    if not isinstance(metadata, dict):
        report.major(
            f"'metadata' must be a key-value mapping (dict), got {type(metadata).__name__}",
            "SKILL.md",
            category="Frontmatter",
        )
        return

    # Validate all values are strings (OpenSpec requirement)
    for key, value in metadata.items():
        if not isinstance(key, str):
            report.major(
                f"'metadata' key must be string, got {type(key).__name__}: {key}",
                "SKILL.md",
                category="Frontmatter",
            )
        if not isinstance(value, str):
            report.minor(
                f"'metadata.{key}' value should be string for OpenSpec compliance, got {type(value).__name__}",
                "SKILL.md",
                category="Frontmatter",
            )

    report.passed(f"'metadata' field valid: {len(metadata)} entries", "SKILL.md", category="Frontmatter")


def validate_compatibility_field(
    frontmatter: dict[str, Any],
    report: ValidationReport,
) -> None:
    """Validate the 'compatibility' field (OpenSpec: string, max 500 chars)."""
    if "compatibility" not in frontmatter:
        return

    compatibility = frontmatter["compatibility"]

    if not isinstance(compatibility, str):
        report.major(
            f"'compatibility' must be a string, got {type(compatibility).__name__}",
            "SKILL.md",
            category="Frontmatter",
        )
        return

    if len(compatibility) > MAX_COMPATIBILITY_LENGTH:
        report.major(
            f"'compatibility' exceeds {MAX_COMPATIBILITY_LENGTH} characters ({len(compatibility)} chars)",
            "SKILL.md",
            category="Frontmatter",
        )
    else:
        report.passed(f"'compatibility' field valid ({len(compatibility)} chars)", "SKILL.md", category="Frontmatter")


def validate_license_field(
    frontmatter: dict[str, Any],
    report: ValidationReport,
) -> None:
    """Validate the 'license' field (OpenSpec: string type)."""
    if "license" not in frontmatter:
        return

    license_val = frontmatter["license"]

    if not isinstance(license_val, str):
        report.major(
            f"'license' must be a string, got {type(license_val).__name__}",
            "SKILL.md",
            category="Frontmatter",
        )
        return

    if not license_val.strip():
        report.minor("'license' field is empty", "SKILL.md", category="Frontmatter")
    else:
        report.passed(f"'license' field valid: {license_val}", "SKILL.md", category="Frontmatter")


def validate_argument_hint_field(
    frontmatter: dict[str, Any],
    report: ValidationReport,
) -> None:
    """Validate the 'argument-hint' field (skills.md: string, shown during autocomplete)."""
    if "argument-hint" not in frontmatter:
        return

    hint = frontmatter["argument-hint"]

    if not isinstance(hint, str):
        report.major(
            f"'argument-hint' must be a string, got {type(hint).__name__}",
            "SKILL.md",
            category="Frontmatter",
        )
        return

    if not hint.strip():
        report.minor("'argument-hint' field is empty", "SKILL.md", category="Frontmatter")
    else:
        report.passed("'argument-hint' field valid", "SKILL.md", category="Frontmatter")


def validate_model_field(
    frontmatter: dict[str, Any],
    report: ValidationReport,
) -> None:
    """Validate the 'model' field (skills.md: sonnet, opus, haiku, or inherit).

    Note: haiku receives a minor penalty as it is considered less reliable.
    """
    if "model" not in frontmatter:
        return

    model = frontmatter["model"]

    if not isinstance(model, str):
        report.major(
            f"'model' must be a string, got {type(model).__name__}",
            "SKILL.md",
            category="Frontmatter",
        )
        return

    if model not in VALID_MODEL_VALUES:
        report.major(
            f"Invalid 'model' value: '{model}'. Valid values: {sorted(VALID_MODEL_VALUES)}",
            "SKILL.md",
            category="Frontmatter",
        )
    elif model == "haiku":
        # Haiku penalty: haiku is less reliable for complex skills
        report.minor(
            "'model: haiku' specified - haiku is less reliable for complex tasks. "
            "Consider using 'sonnet' or 'inherit' for better accuracy.",
            "SKILL.md",
            category="Frontmatter",
        )
    else:
        report.passed(f"'model' field valid: {model}", "SKILL.md", category="Frontmatter")


def validate_hooks_field(
    frontmatter: dict[str, Any],
    report: ValidationReport,
) -> None:
    """Validate the 'hooks' field (skills.md: must be valid hook structure)."""
    if "hooks" not in frontmatter:
        return

    hooks = frontmatter["hooks"]

    # Hooks can be a string (path to hooks.json) or a dict (inline hooks)
    if isinstance(hooks, str):
        if not hooks.strip():
            report.minor("'hooks' field is empty string", "SKILL.md", category="Frontmatter")
        else:
            report.passed(f"'hooks' field references: {hooks}", "SKILL.md", category="Frontmatter")
        return

    if not isinstance(hooks, dict):
        report.major(
            f"'hooks' must be a string (path) or dict (inline config), got {type(hooks).__name__}",
            "SKILL.md",
            category="Frontmatter",
        )
        return

    # Validate hook structure (keys should be valid hook event names)
    valid_hook_events = {
        "PreToolUse",
        "PostToolUse",
        "PostToolUseFailure",
        "PermissionRequest",
        "UserPromptSubmit",
        "Notification",
        "Stop",
        "SubagentStart",
        "SubagentStop",
        "Setup",
        "SessionStart",
        "SessionEnd",
        "PreCompact",
        "TeammateIdle",
        "TaskCompleted",
        "ConfigChange",
        "WorktreeCreate",
        "WorktreeRemove",
    }

    for event_name in hooks.keys():
        if event_name not in valid_hook_events:
            report.minor(
                f"Unknown hook event '{event_name}'. Valid events: PreToolUse, PostToolUse, Stop, etc.",
                "SKILL.md",
                category="Frontmatter",
            )

    report.passed(f"'hooks' field valid: {len(hooks)} event(s) configured", "SKILL.md", category="Frontmatter")


def validate_context_field(frontmatter: dict[str, Any], report: ValidationReport) -> None:
    """Validate the 'context' frontmatter field."""
    if "context" not in frontmatter:
        return

    context = frontmatter["context"]

    if not isinstance(context, str):
        report.critical(
            f"'context' must be a string, got {type(context).__name__}",
            "SKILL.md",
            category="Frontmatter",
        )
        return

    if context not in VALID_CONTEXT_VALUES:
        report.critical(
            f"Invalid 'context' value: '{context}'. Valid values: {VALID_CONTEXT_VALUES}",
            "SKILL.md",
            category="Frontmatter",
        )
        return

    report.passed(f"'context' field valid: {context}", "SKILL.md", category="Frontmatter")


def validate_agent_field(frontmatter: dict[str, Any], report: ValidationReport) -> None:
    """Validate the 'agent' frontmatter field."""
    if "agent" not in frontmatter:
        if frontmatter.get("context") == "fork":
            report.info(
                "'agent' not specified with context: fork (defaults to general-purpose)",
                "SKILL.md",
                category="Frontmatter",
            )
        return

    agent = frontmatter["agent"]

    if not isinstance(agent, str):
        report.critical(
            f"'agent' must be a string, got {type(agent).__name__}",
            "SKILL.md",
            category="Frontmatter",
        )
        return

    if frontmatter.get("context") != "fork":
        report.major(
            "'agent' field has no effect without 'context: fork'",
            "SKILL.md",
            category="Frontmatter",
        )

    if agent in BUILTIN_AGENT_TYPES:
        report.passed(f"'agent' field valid (built-in): {agent}", "SKILL.md", category="Frontmatter")
    else:
        report.info(
            f"'agent' value '{agent}' is not a built-in type (may be custom from .claude/agents/)",
            "SKILL.md",
            category="Frontmatter",
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
            category="Frontmatter",
        )
        return

    report.passed(f"'{field_name}' field valid: {value}", "SKILL.md", category="Frontmatter")


def validate_field_whitelist(
    frontmatter: dict[str, Any],
    report: ValidationReport,
    strict_openspec: bool = False,
) -> None:
    """Validate frontmatter fields against whitelist."""
    allowed_fields = OPENSPEC_ALLOWED_FIELDS if strict_openspec else ALL_KNOWN_FIELDS

    for key in frontmatter.keys():
        if key in DEPRECATED_FIELDS:
            report.minor(
                f"Deprecated field '{key}' (may be ignored by CLI)",
                "SKILL.md",
                category="Frontmatter",
            )
        elif key not in allowed_fields:
            if strict_openspec:
                report.major(
                    f"Unexpected field '{key}' in frontmatter. OpenSpec allows: {sorted(OPENSPEC_ALLOWED_FIELDS)}",
                    "SKILL.md",
                    category="Frontmatter",
                )
            else:
                report.warning(
                    f"Unknown frontmatter field '{key}' (may be ignored by CLI)",
                    "SKILL.md",
                    category="Frontmatter",
                )


def validate_token_budget(content: str, body: str, report: ValidationReport) -> None:
    """Validate token budget (line count, word count)."""
    total_lines = content.count("\n") + 1
    word_count = len(body.split())

    # Line count check
    if total_lines > MAX_SKILL_LINES_ERROR:
        report.major(
            f"SKILL.md has {total_lines} lines (max {MAX_SKILL_LINES_ERROR}). Must use progressive disclosure.",
            "SKILL.md",
            category="Token Budget",
        )
    elif total_lines > MAX_SKILL_LINES:
        report.minor(
            f"SKILL.md has {total_lines} lines (recommended: under {MAX_SKILL_LINES}). "
            "Consider moving detailed content to supporting files.",
            "SKILL.md",
            category="Token Budget",
        )
    else:
        report.passed(f"SKILL.md line count OK ({total_lines} lines)", "SKILL.md", category="Token Budget")

    # Word count check
    if word_count > MAX_WORD_COUNT_ERROR:
        report.major(
            f"Content exceeds {MAX_WORD_COUNT_ERROR} words ({word_count})",
            "SKILL.md",
            category="Token Budget",
        )
    elif word_count > MAX_WORD_COUNT_WARN:
        report.minor(
            f"Content is lengthy ({word_count} words)",
            "SKILL.md",
            category="Token Budget",
        )


def validate_required_sections(body: str, report: ValidationReport, strict_mode: bool = False) -> None:
    """Validate required sections (Nixtla strict mode)."""
    if not strict_mode:
        return

    for section in REQUIRED_SECTIONS:
        # Use regex to match exact section headers at start of line
        # This prevents false positives like "### Research Output Files" matching "## Output"
        section_pattern = rf"(?m)^{re.escape(section)}\s*$"
        if not re.search(section_pattern, body):
            report.major(
                f"Required section missing: '{section}' (Nixtla strict mode)",
                "SKILL.md",
                category="Required Sections",
            )
        else:
            report.passed(f"Required section present: {section}", "SKILL.md", category="Required Sections")

    # Instructions must have numbered list (only if ## Instructions section actually exists)
    # Use regex to match exact section header, not substring like "## Instructions vs System Prompts"
    instructions_match = re.search(r"(?m)^## Instructions\s*$", body)
    if instructions_match:
        instructions_start = instructions_match.start()
        # Find next ## header (any level 2 header)
        next_section = re.search(r"(?m)^## ", body[instructions_match.end() :])
        if next_section:
            instructions_end = instructions_match.end() + next_section.start()
        else:
            instructions_end = len(body)
        instructions = body[instructions_start:instructions_end]

        has_numbered = bool(re.search(r"(?m)^\s*1\.\s+\S+", instructions))
        if not has_numbered:
            report.major(
                "'## Instructions' must include numbered step-by-step list",
                "SKILL.md",
                category="Required Sections",
            )


def validate_path_formats(body: str, report: ValidationReport, skip_platform_checks: list[str] | None = None) -> None:
    """Validate path formats (no absolute paths, forward slashes only).

    Args:
        body: The SKILL.md body content
        report: ValidationReport to add results to
        skip_platform_checks: List of platforms to skip checks for (e.g., ['windows'])
    """
    skip_windows = skip_platform_checks is not None and (
        "windows" in skip_platform_checks or len(skip_platform_checks) == 0
    )

    lines = body.split("\n")
    in_code_block = False
    for i, line in enumerate(lines, 1):
        # Track fenced code blocks (``` or ~~~)
        stripped_line = line.strip()
        if stripped_line.startswith("```") or stripped_line.startswith("~~~"):
            in_code_block = not in_code_block
            continue

        # Skip all path checks inside fenced code blocks
        if in_code_block:
            continue

        # Check for absolute paths
        for pattern, desc in ABSOLUTE_PATH_PATTERNS:
            if pattern.search(line):
                report.major(
                    f"Line {i}: contains absolute/OS-specific path ({desc}) - use '{{baseDir}}/...'",
                    "SKILL.md",
                    line=i,
                    category="Path Format",
                )

        # Skip Windows path checks if requested
        if skip_windows:
            continue

        # Check for backslashes (Windows-style paths - Anthropic docs require forward slashes)
        if "\\scripts\\" in line or "\\references\\" in line:
            report.major(
                f"Line {i}: uses backslashes in path - use forward slashes",
                "SKILL.md",
                line=i,
                category="Path Format",
            )
        # Generic Windows backslash detection (any backslash followed by letter)
        elif RE_WINDOWS_PATH.search(line):
            # Skip shell line continuations (backslash at end of line)
            # Skip common escape sequences (\n, \t, \r, etc.)
            stripped = line.rstrip()
            is_shell_continuation = stripped.endswith(" \\") or stripped.endswith("\t\\")
            has_escape_sequences = any(
                esc in line for esc in ["\\n", "\\t", "\\r", "\\\\", '\\"', "\\'", "\\0", "\\x", "\\u"]
            )
            if (
                not stripped_line.startswith(("```", "`", "#", "//"))
                and not is_shell_continuation
                and not has_escape_sequences
            ):
                report.minor(
                    f"Line {i}: possible Windows-style path (backslash) - use forward slashes for portability",
                    "SKILL.md",
                    line=i,
                    category="Path Format",
                )


def validate_mcp_tool_references(body: str, report: ValidationReport) -> None:
    """Validate MCP tool references use qualified format (Anthropic docs requirement).

    MCP tools should be referenced with ServerName:tool_name format,
    not just tool_name (e.g., "serena:read_file" not "read_file").
    """
    # Common MCP tool patterns that should be qualified
    mcp_tool_patterns = [
        "read_file",
        "write_file",
        "list_dir",
        "find_file",
        "search_for_pattern",
        "get_symbols_overview",
        "find_symbol",
        "find_referencing_symbols",
        "replace_symbol_body",
        "execute_shell_command",
    ]

    lines = body.split("\n")
    for i, line in enumerate(lines, 1):
        # Check for unqualified MCP tool references
        match = RE_MCP_TOOL_UNQUALIFIED.search(line)
        if match:
            tool_name = match.group(3)
            if tool_name in mcp_tool_patterns or "_" in tool_name:
                report.minor(
                    f"Line {i}: MCP tool reference may need qualification (ServerName:tool_name): '{tool_name}'",
                    "SKILL.md",
                    line=i,
                    category="MCP Tools",
                )


def validate_time_sensitive_info(body: str, report: ValidationReport) -> None:
    """Detect time-sensitive information that may become stale (Anthropic docs).

    Skills should avoid dates, version numbers, and temporal references
    that will become outdated over time.
    """
    lines = body.split("\n")
    time_sensitive_found = []

    for i, line in enumerate(lines, 1):
        # Skip code blocks
        if line.strip().startswith("```") or line.strip().startswith("`"):
            continue

        match = RE_TIME_SENSITIVE.search(line)
        if match:
            time_sensitive_found.append((i, match.group(0)))

    if time_sensitive_found:
        # Report first 3 occurrences
        for line_num, text in time_sensitive_found[:3]:
            report.minor(
                f"Line {line_num}: Time-sensitive information may become stale: '{text}'",
                "SKILL.md",
                line=line_num,
                category="Content Quality",
            )

        if len(time_sensitive_found) > 3:
            report.minor(
                f"Found {len(time_sensitive_found)} time-sensitive references total (showing first 3)",
                "SKILL.md",
                category="Content Quality",
            )


def validate_string_substitutions(body: str, report: ValidationReport) -> None:
    """Validate string substitution patterns (skills.md: $ARGUMENTS, $N, ${CLAUDE_SESSION_ID}).

    Detects and validates the usage of Claude Code's string substitution variables.
    """
    # Check for $ARGUMENTS usage
    arguments_matches = RE_ARGUMENTS_VAR.findall(body)
    if arguments_matches:
        report.info(
            f"Skill uses $ARGUMENTS variable ({len(arguments_matches)} occurrence(s))",
            "SKILL.md",
            category="String Substitutions",
        )

    # Check for $ARGUMENTS[N] usage
    indexed_matches = RE_ARGUMENTS_INDEX.findall(body)
    if indexed_matches:
        indices = set(indexed_matches)
        report.info(
            f"Skill uses indexed arguments: $ARGUMENTS[{', '.join(sorted(indices))}]",
            "SKILL.md",
            category="String Substitutions",
        )

    # Check for $N shorthand usage
    shorthand_matches = RE_SHORTHAND_ARG.findall(body)
    if shorthand_matches:
        shorthand_indices = sorted(set(shorthand_matches))
        report.info(
            f"Skill uses shorthand arguments: ${', $'.join(shorthand_indices)}",
            "SKILL.md",
            category="String Substitutions",
        )

    # Check for ${CLAUDE_SESSION_ID} usage
    session_id_matches = RE_SESSION_ID_VAR.findall(body)
    if session_id_matches:
        report.info(
            f"Skill uses ${{CLAUDE_SESSION_ID}} ({len(session_id_matches)} occurrence(s))",
            "SKILL.md",
            category="String Substitutions",
        )


def validate_dynamic_context(body: str, report: ValidationReport) -> None:
    """Validate dynamic context injection (skills.md: `!`command`` syntax).

    Detects usage of the dynamic context injection feature.
    """
    # Check for `!`command`` syntax
    dynamic_matches = RE_DYNAMIC_CONTEXT.findall(body)
    if dynamic_matches:
        report.info(
            f"Skill uses dynamic context injection (! syntax): {len(dynamic_matches)} occurrence(s)",
            "SKILL.md",
            category="Dynamic Context",
        )

    # Check for ultrathink keyword
    ultrathink_matches = RE_ULTRATHINK.findall(body)
    if ultrathink_matches:
        report.info(
            "Skill contains 'ultrathink' keyword (enables extended thinking)",
            "SKILL.md",
            category="Dynamic Context",
        )


def validate_content_patterns(body: str, report: ValidationReport, strict_mode: bool = False) -> None:
    """Validate content quality patterns (best practices: checklists, examples, workflows).

    Detects and validates the presence of recommended content patterns.
    """
    # Check for checklist patterns ([ ] and [x])
    checklist_matches = RE_CHECKLIST.findall(body)
    if checklist_matches:
        report.passed(
            f"Skill uses checklist pattern ({len(checklist_matches)} checkbox(es))",
            "SKILL.md",
            category="Content Patterns",
        )
    elif strict_mode:
        report.minor(
            "No checklist pattern found (best practice: use [ ] / [x] for complex workflows)",
            "SKILL.md",
            category="Content Patterns",
        )

    # Check for examples pattern (input/output blocks)
    example_matches = RE_INPUT_OUTPUT.findall(body)
    code_blocks = RE_EXAMPLE_BLOCK.findall(body)
    if example_matches or code_blocks:
        example_count = len(example_matches) + len(code_blocks)
        report.passed(
            f"Skill includes examples ({example_count} pattern(s) found)",
            "SKILL.md",
            category="Content Patterns",
        )
    elif strict_mode:
        report.minor(
            "No clear input/output examples found (best practice: include concrete examples)",
            "SKILL.md",
            category="Content Patterns",
        )

    # Check for workflow numbered steps
    workflow_matches = RE_WORKFLOW_STEPS.findall(body)
    if len(workflow_matches) >= 3:
        report.passed(
            f"Skill includes numbered workflow steps ({len(workflow_matches)} steps found)",
            "SKILL.md",
            category="Content Patterns",
        )
    elif strict_mode and "workflow" in body.lower() or "step" in body.lower():
        report.minor(
            "Workflow mentioned but few numbered steps found (best practice: use 1. 2. 3. format)",
            "SKILL.md",
            category="Content Patterns",
        )

    # Check for feedback loop pattern (validate → fix)
    feedback_matches = RE_FEEDBACK_LOOP.findall(body)
    if feedback_matches:
        report.passed(
            f"Skill includes feedback loop pattern ({len(feedback_matches)} occurrence(s))",
            "SKILL.md",
            category="Content Patterns",
        )

    # Check for "Copy this checklist" phrase for complex workflows (best practices lines 410, 452)
    has_checklist = bool(checklist_matches)
    has_copy_phrase = bool(RE_CHECKLIST_COPY_PHRASE.search(body))

    if has_checklist and has_copy_phrase:
        report.passed(
            "Skill includes copyable checklist with 'Copy this checklist' phrase",
            "SKILL.md",
            category="Content Patterns",
        )
    elif has_checklist and not has_copy_phrase and len(workflow_matches) >= 3:
        # Complex workflow with checklist but missing the copy phrase
        report.minor(
            "Checklist found but missing 'Copy this checklist and track your progress' phrase "
            "(best practice for complex workflows)",
            "SKILL.md",
            category="Content Patterns",
        )

    # Check for template patterns (best practices lines 585-634)
    has_strict_template = bool(RE_TEMPLATE_STRICT.search(body))
    has_flexible_template = bool(RE_TEMPLATE_FLEXIBLE.search(body))

    if has_strict_template:
        report.passed(
            "Skill includes strict output template ('ALWAYS use this template')",
            "SKILL.md",
            category="Content Patterns",
        )
    elif has_flexible_template:
        report.passed(
            "Skill includes flexible output template guidance",
            "SKILL.md",
            category="Content Patterns",
        )


def validate_package_dependencies(body: str, report: ValidationReport) -> None:
    """Validate package dependency listings (best practices: document pip install, npm install).

    Detects and validates the presence of package installation instructions.
    """
    package_matches = RE_PACKAGE_INSTALL.findall(body)
    if package_matches:
        report.passed(
            f"Skill documents package dependencies ({len(package_matches)} install command(s))",
            "SKILL.md",
            category="Dependencies",
        )

        # List unique package managers found
        managers = set()
        for match in package_matches:
            if "pip" in match.lower():
                managers.add("pip")
            elif "npm" in match.lower():
                managers.add("npm")
            elif "yarn" in match.lower():
                managers.add("yarn")
            elif "cargo" in match.lower():
                managers.add("cargo")
            elif "go" in match.lower():
                managers.add("go")
            elif "brew" in match.lower():
                managers.add("brew")

        if managers:
            report.info(
                f"Package managers referenced: {', '.join(sorted(managers))}",
                "SKILL.md",
                category="Dependencies",
            )


def validate_resource_references(skill_path: Path, body: str, report: ValidationReport) -> None:
    """Validate that referenced scripts/resources exist."""
    # Check {baseDir}/scripts/... references
    for match in RE_BASEDIR_SCRIPTS.finditer(body):
        rel_path = match.group(1)
        script_path = skill_path / "scripts" / rel_path
        if not script_path.exists():
            report.major(
                f"Referenced script not found: '{{baseDir}}/scripts/{rel_path}'",
                "SKILL.md",
                category="Resource References",
            )
        else:
            report.passed(f"Script exists: scripts/{rel_path}", category="Resource References")

    # Check {baseDir}/references/... references
    for match in RE_BASEDIR_REFERENCES.finditer(body):
        rel_path = match.group(1)
        ref_path = skill_path / "references" / rel_path
        if not ref_path.exists():
            report.major(
                f"Referenced file not found: '{{baseDir}}/references/{rel_path}'",
                "SKILL.md",
                category="Resource References",
            )
        else:
            report.passed(f"Reference exists: references/{rel_path}", category="Resource References")

    # Check markdown links to local files
    local_refs = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", body)
    checked_files: set[str] = set()  # Track files we've already validated
    for _, link_target in local_refs:
        if link_target.startswith(("http://", "https://", "mailto:", "#", "{")):
            continue
        # Handle anchor links (e.g., "references/file.md#section-name")
        file_path = link_target.split("#")[0] if "#" in link_target else link_target
        # Skip if we've already checked this file
        if file_path in checked_files:
            continue
        checked_files.add(file_path)

        # Check for parent directory traversal (../) which breaks portability
        if "../" in file_path:
            report.major(
                f"Reference uses parent traversal '../': {file_path} - skill should be self-contained",
                "SKILL.md",
                category="Resource References",
            )
            # Still check if file exists for completeness
            ref_path = skill_path / file_path
            if ref_path.exists():
                report.info(
                    f"External file exists but skill not portable: {file_path}",
                    "SKILL.md",
                    category="Resource References",
                )
            continue

        ref_path = skill_path / file_path
        if not ref_path.exists():
            report.major(
                f"Referenced file not found: {file_path}",
                "SKILL.md",
                category="Resource References",
            )
        else:
            report.passed(f"Referenced file exists: {file_path}", "SKILL.md", category="Resource References")


def validate_directory_structure(skill_path: Path, report: ValidationReport) -> None:
    """Validate skill directory structure."""
    optional_dirs = ["scripts", "examples", "references", "assets", "templates"]

    for dir_name in optional_dirs:
        dir_path = skill_path / dir_name
        if dir_path.is_dir():
            report.passed(f"Optional directory exists: {dir_name}/", category="Structure")

    # Validate scripts directory if it exists
    validate_scripts_directory(skill_path, report)


def validate_scripts_directory(skill_path: Path, report: ValidationReport) -> None:
    """Validate scripts directory (Anthropic docs requirements).

    Checks:
    1. Scripts should be executable
    2. Shell/Python scripts should have proper shebang
    3. Scripts should not have syntax errors (basic check)
    """
    scripts_dir = skill_path / "scripts"
    if not scripts_dir.is_dir():
        return

    for script in scripts_dir.iterdir():
        if not script.is_file():
            continue

        # Check executable scripts
        if script.suffix in {".sh", ".py", ".bash"}:
            # Check executable bit
            if not os.access(script, os.X_OK):
                report.major(
                    f"Script not executable: scripts/{script.name}",
                    f"scripts/{script.name}",
                    category="Scripts",
                )
            else:
                report.passed(
                    f"Script executable: scripts/{script.name}",
                    f"scripts/{script.name}",
                    category="Scripts",
                )

            # Check shebang line
            try:
                content = script.read_text()
                first_line = content.split("\n")[0] if content else ""

                if not first_line.startswith("#!"):
                    report.minor(
                        f"Script lacks shebang line (e.g., #!/usr/bin/env python3): scripts/{script.name}",
                        f"scripts/{script.name}",
                        category="Scripts",
                    )
                else:
                    # Validate shebang is appropriate for file type
                    if script.suffix == ".py" and "python" not in first_line:
                        report.minor(
                            f"Python script has non-Python shebang: {first_line}",
                            f"scripts/{script.name}",
                            category="Scripts",
                        )
                    elif script.suffix in {".sh", ".bash"} and "sh" not in first_line and "bash" not in first_line:
                        report.minor(
                            f"Shell script has non-shell shebang: {first_line}",
                            f"scripts/{script.name}",
                            category="Scripts",
                        )
                    else:
                        report.passed(
                            f"Script has valid shebang: scripts/{script.name}",
                            f"scripts/{script.name}",
                            category="Scripts",
                        )

                    # Check for Python docstring (best practices: scripts should have clear documentation)
                    if script.suffix == ".py":
                        # Look for module docstring (triple quotes near start of file)
                        has_docstring = (
                            '"""' in content[:500]
                            or "'''" in content[:500]
                            or "# " in first_line  # or shebang followed by comment
                        )
                        if not has_docstring:
                            report.minor(
                                f"Python script lacks module docstring: scripts/{script.name} "
                                "(best practice: add '''Description of what script does''')",
                                f"scripts/{script.name}",
                                category="Scripts",
                            )
                        else:
                            report.passed(
                                f"Python script has documentation: scripts/{script.name}",
                                f"scripts/{script.name}",
                                category="Scripts",
                            )
            except Exception:
                report.minor(
                    f"Could not read script: scripts/{script.name}",
                    f"scripts/{script.name}",
                    category="Scripts",
                )


def validate_reference_files(skill_path: Path, report: ValidationReport) -> None:
    """Validate reference files structure (Anthropic docs requirements).

    Checks:
    1. Reference files > 100 lines should have a table of contents
    2. References should be one level deep (no nested references/ directories)
    """
    refs_dir = skill_path / "references"
    if not refs_dir.is_dir():
        return

    # Check for nested directories (should be one level deep)
    for item in refs_dir.iterdir():
        if item.is_dir():
            # Check if nested dir contains .md files (actual nested references)
            nested_md_files = list(item.glob("*.md"))
            if nested_md_files:
                report.major(
                    f"Nested references directory found: references/{item.name}/ - references should be one level deep",
                    f"references/{item.name}/",
                    category="Structure",
                )
            else:
                # Just an organizational folder (e.g., images/), which is OK
                report.info(
                    f"Subdirectory in references: references/{item.name}/ (OK if for assets)",
                    f"references/{item.name}/",
                    category="Structure",
                )

    # Check for long reference files without TOC
    for ref_file in refs_dir.glob("*.md"):
        try:
            content = ref_file.read_text()
            line_count = content.count("\n") + 1

            if line_count > REFERENCE_TOC_THRESHOLD:
                # Check for presence of a table of contents
                # Common TOC indicators: "## Contents", "## Table of Contents", "## TOC", numbered list at top
                has_toc = bool(
                    re.search(r"(?im)^##\s*(contents|table\s+of\s+contents|toc|index)(\s|$)", content)
                    or re.search(r"(?m)^-\s*\[.*\]\(#", content[:2000])  # Markdown anchor links
                    or re.search(r"(?m)^1\.\s+\[.*\]\(#", content[:2000])  # Numbered TOC
                )

                if not has_toc:
                    report.minor(
                        f"Reference file has {line_count} lines but no table of contents "
                        f"(Anthropic docs: files > {REFERENCE_TOC_THRESHOLD} lines should have TOC)",
                        f"references/{ref_file.name}",
                        category="Reference Files",
                    )
                else:
                    report.passed(
                        f"Reference file has TOC ({line_count} lines): references/{ref_file.name}",
                        f"references/{ref_file.name}",
                        category="Reference Files",
                    )
        except Exception:
            report.minor(
                f"Could not read reference file: references/{ref_file.name}",
                f"references/{ref_file.name}",
                category="Reference Files",
            )


def validate_pillars(
    skill_path: Path,
    body: str,
    report: ValidationReport,
    include_ninth: bool = False,
) -> None:
    """Validate 8+1 Pillars coverage for lang-* and convert-* skills."""
    skill_name = skill_path.name.lower()

    # Only apply to lang-* and convert-* skills
    if not (skill_name.startswith("lang-") or skill_name.startswith("convert-")):
        report.info(
            "8+1 Pillars validation skipped (only for lang-* and convert-* skills)",
            category="Pillars Coverage",
        )
        return

    # Determine if 9th pillar should be included
    should_include_ninth = include_ninth
    if not should_include_ninth:
        for lang in REPL_CENTRIC_LANGUAGES:
            if lang in skill_name:
                should_include_ninth = True
                break

    pillars_to_check = list(EIGHT_PILLARS)
    if should_include_ninth:
        pillars_to_check.append(NINTH_PILLAR)

    total_score = 0.0
    max_score = len(pillars_to_check)

    for pillar_name, keywords in pillars_to_check:
        # Count keyword occurrences
        keyword_count = 0
        for keyword in keywords:
            keyword_count += len(re.findall(re.escape(keyword), body, re.IGNORECASE))

        # Check for dedicated section
        has_section = bool(re.search(rf"##\s*{re.escape(pillar_name)}", body, re.IGNORECASE))

        # Score: 1.0 = dedicated section with content, 0.5 = mentioned, 0.0 = missing
        if has_section and keyword_count >= 3:
            score = 1.0
            notes = "Full coverage with dedicated section"
        elif keyword_count >= 5:
            score = 1.0
            notes = f"Full coverage ({keyword_count} keyword occurrences)"
        elif keyword_count >= 2:
            score = 0.5
            notes = f"Partial coverage ({keyword_count} keyword occurrences)"
        else:
            score = 0.0
            notes = "Missing or minimal coverage"

        total_score += score
        report.pillar_scores.append(PillarScore(pillar_name, score, notes))

        if score == 0.0:
            report.minor(
                f"Pillar '{pillar_name}' has minimal coverage",
                "SKILL.md",
                category="Pillars Coverage",
            )
        elif score == 0.5:
            report.info(
                f"Pillar '{pillar_name}' has partial coverage",
                "SKILL.md",
                category="Pillars Coverage",
            )
        else:
            report.passed(
                f"Pillar '{pillar_name}' has full coverage",
                "SKILL.md",
                category="Pillars Coverage",
            )

    # Store pillar score in category scores
    pillar_percentage = (total_score / max_score) * 100 if max_score > 0 else 0
    report.category_scores["Pillars Coverage"] = pillar_percentage

    # Threshold checks
    if pillar_percentage < 50:
        report.major(
            f"Pillars coverage is incomplete ({total_score}/{max_score})",
            "SKILL.md",
            category="Pillars Coverage",
        )
    elif pillar_percentage < 75:
        report.minor(
            f"Pillars coverage needs improvement ({total_score}/{max_score})",
            "SKILL.md",
            category="Pillars Coverage",
        )
    else:
        report.passed(
            f"Pillars coverage is good ({total_score}/{max_score})",
            "SKILL.md",
            category="Pillars Coverage",
        )


def calculate_overall_score(report: ValidationReport) -> None:
    """Calculate overall score and grade."""
    # Count results by level
    critical_count = sum(1 for r in report.results if r.level == "CRITICAL")
    major_count = sum(1 for r in report.results if r.level == "MAJOR")
    minor_count = sum(1 for r in report.results if r.level == "MINOR")
    passed_count = sum(1 for r in report.results if r.level == "PASSED")
    total_checks = critical_count + major_count + minor_count + passed_count

    if total_checks == 0:
        report.overall_score = 0.0
        report.grade = "F"
        return

    # Weighted scoring:
    # CRITICAL = 0 points, MAJOR = 1 point, MINOR = 2 points, PASSED = 3 points
    weighted_score = critical_count * 0 + major_count * 1 + minor_count * 2 + passed_count * 3
    max_possible = total_checks * 3

    report.overall_score = (weighted_score / max_possible) * 100 if max_possible > 0 else 0.0
    report.calculate_grade()


# =============================================================================
# Main Validation Function
# =============================================================================


def validate_skill(
    skill_path: Path,
    strict_mode: bool = False,
    strict_openspec: bool = False,
    validate_pillars_flag: bool = False,
    skip_platform_checks: list[str] | None = None,
) -> ValidationReport:
    """Validate a complete skill directory.

    Args:
        skill_path: Path to the skill directory
        strict_mode: Enable Nixtla strict mode validation
        strict_openspec: Enable AgentSkills OpenSpec strict validation
        validate_pillars_flag: Enable 8+1 Pillars validation
        skip_platform_checks: List of platforms to skip checks for (e.g., ['windows'])

    Returns:
        ValidationReport with all results
    """
    report = ValidationReport(skill_path=str(skill_path))

    # Check skill directory exists
    if not skill_path.exists():
        report.critical(f"Skill path does not exist: {skill_path}", category="Structure")
        return report

    if not skill_path.is_dir():
        report.critical(f"Skill path is not a directory: {skill_path}", category="Structure")
        return report

    # Validate SKILL.md exists (required)
    if not validate_skill_md_exists(skill_path, report):
        return report

    # Read SKILL.md content
    skill_md = find_skill_md(skill_path)
    if skill_md is None:
        return report
    content = skill_md.read_text()

    # Parse frontmatter
    frontmatter = validate_frontmatter_structure(content, report)
    _, body, _ = parse_frontmatter(content)

    if frontmatter is not None:
        # Validate field whitelist
        validate_field_whitelist(frontmatter, report, strict_openspec)

        # Validate individual frontmatter fields
        validate_name_field(frontmatter, skill_path.name, report, strict_openspec)
        validate_description_field(frontmatter, body, report, strict_mode)
        validate_context_field(frontmatter, report)
        validate_agent_field(frontmatter, report)
        validate_boolean_field(frontmatter, "user-invocable", report)
        validate_boolean_field(frontmatter, "disable-model-invocation", report)
        validate_allowed_tools_field(frontmatter, report, strict_mode, strict_openspec)
        validate_metadata_field(frontmatter, report)

        # New frontmatter field validations (Phase 2)
        validate_compatibility_field(frontmatter, report)
        validate_license_field(frontmatter, report)
        validate_argument_hint_field(frontmatter, report)
        validate_model_field(frontmatter, report)
        validate_hooks_field(frontmatter, report)

    # Validate token budget
    validate_token_budget(content, body, report)

    # Validate required sections (Nixtla strict mode)
    validate_required_sections(body, report, strict_mode)

    # Validate path formats
    validate_path_formats(body, report, skip_platform_checks)

    # Validate MCP tool references (Anthropic docs: use qualified format)
    validate_mcp_tool_references(body, report)

    # Validate time-sensitive information (Anthropic docs: avoid stale dates/versions)
    validate_time_sensitive_info(body, report)

    # Validate string substitutions (skills.md: $ARGUMENTS, $N, ${CLAUDE_SESSION_ID})
    validate_string_substitutions(body, report)

    # Validate dynamic context injection (skills.md: `!`command`` syntax)
    validate_dynamic_context(body, report)

    # Validate content patterns (best practices: checklists, examples, workflows, feedback loops)
    validate_content_patterns(body, report, strict_mode)

    # Validate package dependencies (best practices: pip install, npm install)
    validate_package_dependencies(body, report)

    # Validate resource references
    validate_resource_references(skill_path, body, report)

    # Validate directory structure
    validate_directory_structure(skill_path, report)

    # Validate reference files (TOC and nesting depth - Anthropic docs)
    validate_reference_files(skill_path, report)

    # Validate TOC embedding — SKILL.md must embed TOCs from referenced .md files
    if skill_md is not None:
        validate_toc_embedding(content, skill_md, skill_path, report)

    # Validate 8+1 Pillars (optional)
    if validate_pillars_flag:
        validate_pillars(skill_path, body, report)

    # Calculate overall score and grade
    calculate_overall_score(report)

    return report


# =============================================================================
# Output Functions
# =============================================================================


def print_results(report: ValidationReport, verbose: bool = False) -> None:
    """Print validation results in human-readable format."""
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
    counts = {"CRITICAL": 0, "MAJOR": 0, "MINOR": 0, "INFO": 0, "PASSED": 0}
    for r in report.results:
        counts[r.level] += 1

    # Print header
    print("\n" + "=" * 70)
    print(f"Skill Validation: {report.skill_path}")
    print("=" * 70)

    # Print grade
    grade_colors = {"A": "\033[92m", "B": "\033[92m", "C": "\033[93m", "D": "\033[93m", "F": "\033[91m"}
    grade_color = grade_colors.get(report.grade, "")
    print(f"\n{colors['BOLD']}Grade: {grade_color}{report.grade}{colors['RESET']} ({report.overall_score:.1f}/100)")

    # Print summary
    print("\nSummary:")
    print(f"  {colors['CRITICAL']}CRITICAL: {counts['CRITICAL']}{colors['RESET']}")
    print(f"  {colors['MAJOR']}MAJOR:    {counts['MAJOR']}{colors['RESET']}")
    print(f"  {colors['MINOR']}MINOR:    {counts['MINOR']}{colors['RESET']}")
    if verbose:
        print(f"  {colors['INFO']}INFO:     {counts['INFO']}{colors['RESET']}")
        print(f"  {colors['PASSED']}PASSED:   {counts['PASSED']}{colors['RESET']}")

    # Print pillar scores if available
    if report.pillar_scores:
        print("\nPillars Coverage:")
        for ps in report.pillar_scores:
            score_color = (
                colors["PASSED"] if ps.score == 1.0 else (colors["MINOR"] if ps.score == 0.5 else colors["MAJOR"])
            )
            score_symbol = "✓" if ps.score == 1.0 else ("~" if ps.score == 0.5 else "✗")
            print(f"  {score_color}{score_symbol} {ps.name}: {ps.score}/1.0{colors['RESET']} - {ps.notes}")

    # Print details by category
    print("\nDetails:")
    categories_seen: set[str] = set()
    for r in report.results:
        if r.level == "PASSED" and not verbose:
            continue
        if r.level == "INFO" and not verbose:
            continue

        # Print category header if new (category only exists on ComprehensiveValidationResult)
        if isinstance(r, ComprehensiveValidationResult) and r.category and r.category not in categories_seen:
            categories_seen.add(r.category)
            print(f"\n  {colors['BOLD']}[{r.category}]{colors['RESET']}")

        color = colors[r.level]
        reset = colors["RESET"]
        file_info = f" ({r.file})" if r.file else ""
        line_info = f":{r.line}" if r.line else ""
        print(f"    {color}[{r.level}]{reset} {r.message}{file_info}{line_info}")

    # Print final status
    print("\n" + "-" * 70)
    if report.exit_code == 0:
        print(f"{colors['PASSED']}✓ Skill validation passed (Grade {report.grade}){colors['RESET']}")
    elif report.exit_code == 1:
        print(f"{colors['CRITICAL']}✗ CRITICAL issues - skill will not work (Grade {report.grade}){colors['RESET']}")
    elif report.exit_code == 2:
        print(f"{colors['MAJOR']}✗ MAJOR issues - significant problems (Grade {report.grade}){colors['RESET']}")
    else:
        print(f"{colors['MINOR']}! MINOR issues - may affect UX (Grade {report.grade}){colors['RESET']}")

    print()


def print_json(report: ValidationReport) -> None:
    """Print validation results as JSON."""
    output = {
        "skill_path": report.skill_path,
        "exit_code": report.exit_code,
        "overall_score": round(report.overall_score, 2),
        "grade": report.grade,
        "counts": {
            "critical": sum(1 for r in report.results if r.level == "CRITICAL"),
            "major": sum(1 for r in report.results if r.level == "MAJOR"),
            "minor": sum(1 for r in report.results if r.level == "MINOR"),
            "info": sum(1 for r in report.results if r.level == "INFO"),
            "passed": sum(1 for r in report.results if r.level == "PASSED"),
        },
        "pillar_scores": [{"name": ps.name, "score": ps.score, "notes": ps.notes} for ps in report.pillar_scores],
        "category_scores": report.category_scores,
        "results": [
            {
                "level": r.level,
                "message": r.message,
                "file": r.file,
                "line": r.line,
                "category": r.category if isinstance(r, ComprehensiveValidationResult) else None,
            }
            for r in report.results
        ],
    }
    print(json.dumps(output, indent=2))


# =============================================================================
# Main Entry Point
# =============================================================================


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Comprehensive skill validator with 190+ validation rules")
    parser.add_argument("skill_path", help="Path to the skill directory")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show all results including passed checks",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable Nixtla strict mode (required sections, description quality)",
    )
    parser.add_argument(
        "--openspec",
        action="store_true",
        help="Enable AgentSkills OpenSpec strict mode (field whitelist)",
    )
    parser.add_argument(
        "--pillars",
        action="store_true",
        help="Enable 8+1 Pillars validation (for lang-* and convert-* skills)",
    )
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

    report = validate_skill(
        skill_path,
        strict_mode=args.strict,
        strict_openspec=args.openspec,
        validate_pillars_flag=args.pillars,
    )

    if args.json:
        print_json(report)
    else:
        print_results(report, args.verbose)

    return report.exit_code


if __name__ == "__main__":
    sys.exit(main())
