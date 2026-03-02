#!/usr/bin/env python3
"""
Claude Plugins Validation - Common Module

Shared validation infrastructure for all Claude Code plugin validators.
This module contains:
- Type definitions (Level, ValidationResult, ValidationReport)
- Common constants (tools, models, security patterns)
- Utility functions (scoring, formatting, exit codes)

All individual validators should import from this module to ensure consistency.
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal

# =============================================================================
# Tool Resolution: local install → remote runner fallback (via smart_exec)
# =============================================================================


def resolve_tool_command(tool_name: str) -> list[str] | None:
    """Resolve a linting tool to its executable command prefix.

    Uses smart_exec's tool database and executor detection to find
    the best way to run the tool: local install first, then remote
    execution via uvx, bunx, npx, pnpm dlx, yarn dlx, deno, docker, etc.

    Supports 25+ tools across Python, Node, Deno, native, and PowerShell
    ecosystems. See smart_exec.py for the full TOOL_DB and PRIORITY tables.

    Returns:
        Command prefix as list (e.g. ["uvx", "ruff@latest"]) or None if
        no suitable executor is available on this system.
    """
    from smart_exec import choose_best, detect_executors, resolve_tool

    spec = resolve_tool(tool_name)
    executors = detect_executors()
    try:
        argv, _executor = choose_best(spec, [], executors)
        return argv
    except RuntimeError:
        return None


# =============================================================================
# Type Definitions
# =============================================================================

# Validation result severity levels (uppercase for consistency)
# Hierarchy: CRITICAL > MAJOR > MINOR > NIT > WARNING > INFO > PASSED
# - CRITICAL/MAJOR/MINOR: always block validation (non-zero exit code)
# - NIT: blocks only in --strict mode
# - WARNING: never blocks, always reported (security advisories, best practices)
# - INFO: informational only, shown in verbose mode
# - PASSED: check passed, shown in verbose mode
Level = Literal["CRITICAL", "MAJOR", "MINOR", "NIT", "WARNING", "INFO", "PASSED"]

# =============================================================================
# Exit Codes
# =============================================================================

EXIT_OK = 0  # All checks passed (or only WARNING/INFO/PASSED)
EXIT_CRITICAL = 1  # CRITICAL issues found
EXIT_MAJOR = 2  # MAJOR issues found
EXIT_MINOR = 3  # MINOR issues found
EXIT_NIT = 4  # NIT issues found (only in --strict mode)

# =============================================================================
# Severity Level Constants (L1-L10 Alternative System)
# =============================================================================

# L1-L10 severity levels with confidence thresholds
# This alternative system maps numeric severity to confidence levels
SEVERITY_L1 = 1  # Low severity, confidence > 0.7
SEVERITY_L2 = 2  # Low severity, confidence > 0.7
SEVERITY_L3 = 3  # Low severity, confidence > 0.7
SEVERITY_L4 = 4  # Medium severity, confidence > 0.85
SEVERITY_L5 = 5  # Medium severity, confidence > 0.85
SEVERITY_L6 = 6  # Medium severity, confidence > 0.85
SEVERITY_L7 = 7  # High severity, confidence > 0.95
SEVERITY_L8 = 8  # High severity, confidence > 0.95
SEVERITY_L9 = 9  # High severity, confidence > 0.95
SEVERITY_L10 = 10  # Critical severity, confidence > 0.99


def severity_to_level(severity: int) -> Level:
    """Convert L1-L10 severity to standard Level.

    Args:
        severity: Numeric severity (1-10)

    Returns:
        Corresponding Level (CRITICAL, MAJOR, MINOR, NIT, WARNING, INFO)
    """
    if severity >= SEVERITY_L10:
        return "CRITICAL"
    elif severity >= SEVERITY_L7:
        return "MAJOR"
    elif severity >= SEVERITY_L4:
        return "MINOR"
    elif severity == SEVERITY_L3:
        return "NIT"
    elif severity == SEVERITY_L2:
        return "WARNING"
    else:
        return "INFO"


def level_to_severity(level: Level) -> int:
    """Convert standard Level to L1-L10 severity (midpoint of range).

    Args:
        level: Standard Level type

    Returns:
        Corresponding severity number (1-10)
    """
    mapping = {
        "CRITICAL": SEVERITY_L10,
        "MAJOR": SEVERITY_L8,
        "MINOR": SEVERITY_L5,
        "NIT": SEVERITY_L3,
        "WARNING": SEVERITY_L2,
        "INFO": SEVERITY_L1,
        "PASSED": SEVERITY_L1,
    }
    return mapping.get(level, SEVERITY_L1)


# =============================================================================
# Hook Event Types
# =============================================================================

# All valid hook event types in Claude Code
VALID_HOOK_EVENTS = {
    "PreToolUse",
    "PostToolUse",
    "PostToolUseFailure",
    "PermissionRequest",
    "UserPromptSubmit",
    "Notification",
    "Stop",
    "SubagentStop",
    "SubagentStart",
    "SessionStart",
    "SessionEnd",
    "PreCompact",
    "Setup",
    "TeammateIdle",
    "TaskCompleted",
    "ConfigChange",
    "WorktreeCreate",
    "WorktreeRemove",
}

# =============================================================================
# Common Constants
# =============================================================================

# Valid context values for agents and skills (only "fork" is documented)
VALID_CONTEXT_VALUES = {"fork"}

# Built-in agent types provided by Claude Code
BUILTIN_AGENT_TYPES = {"Explore", "Plan", "general-purpose"}

# Semantic version pattern for marketplace version fields
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$")

# Valid tool names for Claude Code agents
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

# Valid model values for agents
VALID_MODELS = {"haiku", "sonnet", "opus", "inherit"}

# Environment variables provided by Claude Code at plugin load time
# Plugins must use these instead of hardcoded absolute paths
VALID_PLUGIN_ENV_VARS = {
    "CLAUDE_PLUGIN_ROOT",  # Plugin's root directory (all plugin hooks)
    "CLAUDE_PROJECT_DIR",  # Project root directory (all hooks)
    "CLAUDE_ENV_FILE",  # SessionStart/Setup only — write export statements to persist env vars
    "CLAUDE_CODE_REMOTE",  # Set to "true" in remote web environments; not set in local CLI
}

# Directories to skip when scanning (cache dirs, hidden dirs, etc.)
SKIP_DIRS = {
    ".ruff_cache",
    ".mypy_cache",
    ".git",
    "__pycache__",
    ".venv",
    "node_modules",
    ".pytest_cache",
    ".tox",
    "dist",
    "build",
    "*.egg-info",
}

# =============================================================================
# Security Patterns
# =============================================================================

# Patterns that indicate potential secrets/credentials
# Note: Generic API Key pattern excludes env var placeholders like ${VAR} or $VAR
SECRET_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS Access Key"),
    (re.compile(r"-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----"), "Private Key"),
    (re.compile(r"ghp_[a-zA-Z0-9]{36}"), "GitHub Personal Access Token"),
    (re.compile(r"sk-[a-zA-Z0-9]{20,}"), "API Key (sk-... format)"),
    (re.compile(r"xox[baprs]-[0-9a-zA-Z-]+"), "Slack Token"),
    (re.compile(r"github_pat_[a-zA-Z0-9_]{22,}"), "GitHub Fine-Grained Personal Access Token"),
    (re.compile(r"AIza[0-9A-Za-z\-_]{35}"), "Google API Key"),
    (re.compile(r"sk_live_[a-zA-Z0-9]{24,}"), "Stripe Secret Key"),
    (re.compile(r"pk_live_[a-zA-Z0-9]{24,}"), "Stripe Publishable Key"),
    (re.compile(r"sk-ant-[a-zA-Z0-9\-_]{80,}"), "Anthropic API Key"),
    (re.compile(r"npm_[a-zA-Z0-9]{36}"), "npm Access Token"),
    (re.compile(r"://[^:\s]+:[^@\s]+@[^\s]+"), "Database Connection String with Credentials"),
    (re.compile(r"SG\.[a-zA-Z0-9\-_]{22}\.[a-zA-Z0-9\-_]{43}"), "SendGrid API Key"),
    # Generic API key pattern excludes environment variable placeholders (${VAR} or $VAR)
    (re.compile(r"api[_-]?key['\"]?\s*[:=]\s*['\"](?!\$[\{A-Z_])[^'\"]{20,}['\"]", re.I), "Generic API Key"),
    # JWT tokens (base64url-encoded header.payload, signature optional)
    (re.compile(r"eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}"), "JWT Token"),
    # AWS Secret Access Key (40-char base64 string)
    (re.compile(r"aws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{40}", re.I), "AWS Secret Access Key"),
]

# Generic example usernames that are acceptable in documentation
EXAMPLE_USERNAMES = {
    "username",
    "user",
    "dev",
    "developer",
    "runner",
    "admin",
    "root",
    "yourname",
    "your-name",
    "your_name",
    "yourusername",
    "your-username",
    "example",
    "test",
    "demo",
    "sample",
    "foo",
    "bar",
    "john",
    "jane",
    "me",
    "you",
    "name",
    "xxx",
    "myuser",
    "myname",
    "your",
    "my",
    "[^/\\s]+",  # Regex pattern in code
}

# Patterns for hardcoded user paths (should use ${CLAUDE_PLUGIN_ROOT} instead)
# Note: These are generic patterns that may produce false positives for example paths
USER_PATH_PATTERNS = [
    re.compile(r"/Users/[^/\s]+/"),
    re.compile(r"C:\\Users\\[^\\\s]+\\"),
    re.compile(r"/home/[^/\s]+/"),
]

# Patterns for ANY absolute path (stricter check for plugins)
# Plugins should use relative paths or ${CLAUDE_PLUGIN_ROOT} / ${HOME}
ABSOLUTE_PATH_PATTERNS = [
    # macOS/Linux home directory paths — CRITICAL portability issue
    (re.compile(r'(?<![#!])(/(?:Users|home)/[^/\s"\'`>\]})]+/[^\s"\'`>\]})]+)'), "home directory path"),
    # Windows home directory paths
    (re.compile(r'(?<!\$\{)(?<!\$)([A-Z]:[\\\/]Users[\\\/][^\s"\'`>\]})]+)', re.IGNORECASE), "Windows home path"),
    # Unix system paths — non-portable, use env vars or relative paths instead
    # The (?<![#!]) lookbehind skips shebangs like #!/usr/bin/env or #!/bin/bash
    (
        re.compile(
            r"(?<![#!])"
            r"(?<!\$\{CLAUDE_PLUGIN_ROOT\})(?<!\$\{CLAUDE_PROJECT_DIR\})(?<![\w$\{])"
            r'(/(?:usr|opt|etc|var|bin|sbin|lib|root)/[^\s"\'`>\]})]+)'
        ),
        "system absolute path",
    ),
]

# Allowed absolute path prefixes in documentation examples
# These are skipped in doc files (.md, .txt, .html) to reduce false positives
ALLOWED_DOC_PATH_PREFIXES = {
    "/tmp/",
    "/var/tmp/",
    "/var/lib/",  # Docker volumes, app data (e.g. /var/lib/postgresql/data)
    "/var/log/",  # Log path examples (e.g. /var/log/myapp/)
    "/var/run/",  # PID/socket files
    "/dev/",
    "/proc/",
    "/sys/",
    "/etc/",  # Common in config examples
    "/bin/",  # Shell references (e.g. /bin/sh, /bin/bash)
    "/sbin/",  # System binaries
    "/usr/bin/",  # Common in shebang/doc examples
    "/usr/sbin/",  # System admin binaries
    "/usr/lib/",  # Shared libraries
    "/usr/lib64/",  # 64-bit shared libraries (RHEL/Fedora)
    "/usr/libexec/",  # Helper binaries (e.g. macOS ApplicationFirewall)
    "/usr/share/",  # Shared data (e.g. /usr/share/dotnet)
    "/usr/local/",  # Common in installation examples
    "/usr/include/",  # Header files
    "/opt/",  # Common in deployment examples
    "/snap/",  # Snap packages
    "/run/",  # Runtime data
}

# Files that should never be in a plugin
DANGEROUS_FILES = {
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
    ".env.staging",
    ".env.test",
    "credentials.json",
    "secrets.json",
    "config.secret.json",
    "private.key",
    "id_rsa",
    "id_ed25519",
    "id_dsa",
    "id_ecdsa",
    ".npmrc",
    ".pypirc",
    ".netrc",
    "token.json",
    "auth.json",
    "service-account.json",
    "service_account_key.json",
    ".htpasswd",
    "kubeconfig",
    ".docker/config.json",
    "cert.pem",
    "key.pem",
    "server.pem",
    "client.pem",
    "ca.pem",
}

# =============================================================================
# Private Information Detection Patterns
# =============================================================================


# Private usernames to detect - automatically detected from system
# These should never appear in published code
def _get_private_usernames() -> set[str]:
    """Auto-detect private usernames from the current system.

    Detection sources (in order):
    1. CLAUDE_PRIVATE_USERNAMES env var (comma-separated, set by agent)
    2. getpass.getuser() - current login name
    3. Path.home().name - home directory name
    4. USER, USERNAME, LOGNAME env vars
    """
    usernames: set[str] = set()

    # First check if explicitly provided via env var (from agent)
    explicit = os.environ.get("CLAUDE_PRIVATE_USERNAMES", "").strip()
    if explicit:
        for u in explicit.split(","):
            u = u.strip().lower()
            if u and u not in EXAMPLE_USERNAMES:
                usernames.add(u)

    # Get current user's login name
    try:
        import getpass

        username = getpass.getuser().lower()
        if username and username not in EXAMPLE_USERNAMES:
            usernames.add(username)
    except Exception:
        pass

    # Get username from home directory path
    try:
        home = Path.home()
        if home.name and home.name.lower() not in EXAMPLE_USERNAMES:
            usernames.add(home.name.lower())
    except Exception:
        pass

    # Also check environment variables
    for var in ("USER", "USERNAME", "LOGNAME"):
        val = os.environ.get(var, "").strip().lower()
        if val and val not in EXAMPLE_USERNAMES:
            usernames.add(val)

    return usernames


# Auto-detect at import time
PRIVATE_USERNAMES: set[str] = _get_private_usernames()


# Patterns for detecting private paths with actual usernames
# More specific than USER_PATH_PATTERNS - these flag as CRITICAL
def build_private_path_patterns(usernames: set[str]) -> list[tuple[re.Pattern[str], str]]:
    """Build regex patterns for detecting private usernames in paths.

    Args:
        usernames: Set of private usernames to detect

    Returns:
        List of (pattern, description) tuples
    """
    patterns: list[tuple[re.Pattern[str], str]] = []
    for username in usernames:
        # Case-insensitive match for username in paths
        escaped = re.escape(username)
        patterns.extend(
            [
                (
                    re.compile(rf"/Users/{escaped}(/|$)", re.IGNORECASE),
                    f"macOS private path with username '{username}'",
                ),
                (re.compile(rf"/home/{escaped}(/|$)", re.IGNORECASE), f"Linux private path with username '{username}'"),
                (
                    re.compile(rf"C:\\Users\\{escaped}(\\|$)", re.IGNORECASE),
                    f"Windows private path with username '{username}'",
                ),
                (
                    re.compile(rf"C:/Users/{escaped}(/|$)", re.IGNORECASE),
                    f"Windows private path with username '{username}'",
                ),
                # Also catch username alone in suspicious contexts
                (re.compile(rf"(?<=/){escaped}(?=/)", re.IGNORECASE), f"username '{username}' in path"),
            ]
        )
    return patterns


# Pre-built patterns for default usernames
PRIVATE_PATH_PATTERNS = build_private_path_patterns(PRIVATE_USERNAMES)

# File extensions to check for private info
SCANNABLE_EXTENSIONS = {
    ".json",
    ".yml",
    ".yaml",
    ".md",
    ".py",
    ".sh",
    ".txt",
    ".toml",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".html",
    ".css",
    ".xml",
    ".ini",
    ".cfg",
    ".conf",
    ".env",
    ".gitignore",
    ".gitmodules",
}

# Directories to skip when scanning for private info
PRIVATE_INFO_SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    ".pytest_cache",
    ".tox",
    "dist",
    "build",
    "target",
    ".eggs",
    "*.egg-info",
    # Also skip dev folders that aren't published
    "docs_dev",
    "scripts_dev",
    "tests_dev",
    "examples_dev",
    "samples_dev",
    "downloads_dev",
    "libs_dev",
    "builds_dev",
}


# =============================================================================
# Gitignore Support
# =============================================================================


def get_gitignored_files(root_path: Path) -> set[str]:
    """Get set of files/directories that are gitignored.

    Uses git check-ignore to accurately determine what's ignored,
    falling back to parsing .gitignore directly if git is not available.

    Args:
        root_path: Root directory to check for .gitignore

    Returns:
        Set of relative paths that are gitignored
    """
    ignored: set[str] = set()

    # Try using git check-ignore for accuracy (respects .gitignore hierarchy)
    try:
        result = subprocess.run(
            ["git", "ls-files", "--ignored", "--exclude-standard", "--others", "--directory"],
            cwd=root_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line:
                    ignored.add(line.rstrip("/"))
            return ignored
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    # Fallback: Parse .gitignore directly
    gitignore_path = root_path / ".gitignore"
    if gitignore_path.exists():
        try:
            patterns = parse_gitignore(gitignore_path)
            # Scan directory and match patterns
            for dirpath, dirnames, filenames in os.walk(root_path):
                rel_dir = Path(dirpath).relative_to(root_path)
                for name in dirnames + filenames:
                    rel_path = str(rel_dir / name) if str(rel_dir) != "." else name
                    if is_path_gitignored(rel_path, patterns):
                        ignored.add(rel_path)
        except Exception:
            pass

    return ignored


def parse_gitignore(gitignore_path: Path) -> list[str]:
    """Parse a .gitignore file and return list of patterns.

    Args:
        gitignore_path: Path to .gitignore file

    Returns:
        List of gitignore patterns (comments and empty lines stripped)
    """
    patterns: list[str] = []
    try:
        with open(gitignore_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                patterns.append(line)
    except (OSError, UnicodeDecodeError):
        pass
    return patterns


def is_path_gitignored(rel_path: str, patterns: list[str]) -> bool:
    """Check if a relative path matches any gitignore pattern.

    Args:
        rel_path: Relative path to check
        patterns: List of gitignore patterns

    Returns:
        True if path matches any pattern
    """
    # Normalize path separators
    rel_path = rel_path.replace("\\", "/")
    path_parts = rel_path.split("/")

    for pattern in patterns:
        # Handle negation (!) - un-ignore previously matched paths
        if pattern.startswith("!"):
            neg_pattern = pattern[1:]
            # If the path matches the negation pattern, it should NOT be ignored
            if fnmatch.fnmatch(rel_path, neg_pattern) or fnmatch.fnmatch(str(Path(rel_path).name), neg_pattern):
                return False
            continue

        # Handle directory-only patterns (ending with /)
        is_dir_pattern = pattern.endswith("/")
        if is_dir_pattern:
            pattern = pattern[:-1]

        # Handle patterns starting with /
        is_anchored = pattern.startswith("/")
        if is_anchored:
            pattern = pattern[1:]

        # Handle ** patterns properly for recursive directory matching
        if "**" in pattern:
            if pattern.startswith("**/"):
                # **/foo matches foo at any depth
                suffix = pattern[3:]  # e.g., "dist" from "**/dist"
                if (
                    fnmatch.fnmatch(rel_path, suffix)
                    or fnmatch.fnmatch(rel_path, f"*/{suffix}")
                    or f"/{suffix}" in f"/{rel_path}"
                ):
                    return True
                continue
            elif pattern.endswith("/**"):
                # build/** matches any file under the prefix directory
                prefix = pattern[:-3]  # e.g., "build" from "build/**"
                if rel_path.startswith(prefix + "/") or rel_path == prefix:
                    return True
                continue
            else:
                # General ** — replace with regex-like matching
                regex = pattern.replace(".", r"\.").replace("**", ".*").replace("*", "[^/]*").replace("?", "[^/]")
                if re.match(regex + "$", rel_path):
                    return True
                continue

        # Check if pattern matches any component or the full path
        if is_anchored:
            # Anchored patterns only match from root
            if fnmatch.fnmatch(rel_path, pattern):
                return True
        else:
            # Non-anchored patterns can match any component
            if fnmatch.fnmatch(rel_path, pattern):
                return True
            # Also check if any path component matches
            for part in path_parts:
                if fnmatch.fnmatch(part, pattern):
                    return True

    return False


def get_skip_dirs_with_gitignore(root_path: Path, additional_skip: set[str] | None = None) -> set[str]:
    """Get combined set of directories to skip (built-in + gitignored).

    Args:
        root_path: Root directory to check for .gitignore
        additional_skip: Additional directories to skip

    Returns:
        Combined set of directory names to skip
    """
    dirs_to_skip = set(PRIVATE_INFO_SKIP_DIRS)
    if additional_skip:
        dirs_to_skip.update(additional_skip)

    # Add gitignored directories
    gitignored = get_gitignored_files(root_path)
    for path in gitignored:
        # Add both the full path and just the directory name
        dirs_to_skip.add(path)
        if "/" in path:
            dirs_to_skip.add(path.split("/")[-1])

    return dirs_to_skip


# =============================================================================
# Validation Name Patterns
# =============================================================================

# Name validation pattern (kebab-case)
NAME_PATTERN = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

# Maximum recommended values for names and descriptions
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MIN_BODY_CHARS = 100
MAX_BODY_WORDS = 2000

# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class ValidationResult:
    """Single validation check result.

    Attributes:
        level: Severity level (CRITICAL, MAJOR, MINOR, INFO, PASSED)
        message: Human-readable description of the result
        file: Optional file path related to the result
        line: Optional line number in the file
        phase: Optional validation phase (structure, semantic, security, cross-reference)
        fixable: Whether this issue can be auto-fixed
        fix_id: Identifier for the fix function (if fixable)
    """

    level: Level
    message: str
    file: str | None = None
    line: int | None = None
    phase: str | None = None
    fixable: bool = False
    fix_id: str | None = None

    def to_dict(self) -> dict[str, str | int | bool | None]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, str | int | bool | None] = {"level": self.level, "message": self.message}
        if self.file is not None:
            result["file"] = self.file
        if self.line is not None:
            result["line"] = self.line
        if self.phase is not None:
            result["phase"] = self.phase
        if self.fixable:
            result["fixable"] = self.fixable
            if self.fix_id:
                result["fix_id"] = self.fix_id
        return result


# Type alias for fix functions
FixFunction = Callable[[str, int | None], bool]  # (file_path, line) -> success


@dataclass
class FixableIssue:
    """Represents an issue that can be automatically fixed.

    Attributes:
        result: The validation result describing the issue
        fix_func: Function that can fix this issue
        fix_description: Human-readable description of what the fix does
    """

    result: ValidationResult
    fix_func: FixFunction
    fix_description: str

    def apply(self) -> bool:
        """Apply the fix and return success status.

        Returns:
            True if fix was successfully applied, False otherwise
        """
        if not self.result.file:
            return False
        return self.fix_func(self.result.file, self.result.line)


@dataclass
class ValidationReport:
    """Complete validation report with results collection and scoring.

    This is the base class that all validators should use (or extend).
    Provides consistent methods for adding results and computing scores.

    Supports:
    - Error accumulation (collect all errors before reporting)
    - Fixable issues registration and auto-fix application
    - Multi-phase validation tracking
    - Partial validation (return valid items even when some fail)
    """

    results: list[ValidationResult] = field(default_factory=list)
    fixable_issues: list[FixableIssue] = field(default_factory=list)
    valid_items: list[Any] = field(default_factory=list)
    failed_items: list[Any] = field(default_factory=list)

    def add(
        self,
        level: Level,
        message: str,
        file: str | None = None,
        line: int | None = None,
        phase: str | None = None,
        fixable: bool = False,
        fix_id: str | None = None,
    ) -> None:
        """Add a validation result."""
        self.results.append(ValidationResult(level, message, file, line, phase, fixable, fix_id))

    def passed(self, message: str, file: str | None = None) -> None:
        """Add a passed check."""
        self.add("PASSED", message, file)

    def info(self, message: str, file: str | None = None) -> None:
        """Add an info message."""
        self.add("INFO", message, file)

    def warning(self, message: str, file: str | None = None, line: int | None = None) -> None:
        """Add a warning — always reported, never blocks validation (even in --strict)."""
        self.add("WARNING", message, file, line)

    def nit(self, message: str, file: str | None = None, line: int | None = None) -> None:
        """Add a nit — blocks validation only in --strict mode."""
        self.add("NIT", message, file, line)

    def minor(self, message: str, file: str | None = None, line: int | None = None) -> None:
        """Add a minor issue."""
        self.add("MINOR", message, file, line)

    def major(self, message: str, file: str | None = None, line: int | None = None) -> None:
        """Add a major issue."""
        self.add("MAJOR", message, file, line)

    def critical(self, message: str, file: str | None = None, line: int | None = None) -> None:
        """Add a critical issue."""
        self.add("CRITICAL", message, file, line)

    @property
    def has_critical(self) -> bool:
        """Check if any CRITICAL issues exist."""
        return any(r.level == "CRITICAL" for r in self.results)

    @property
    def has_major(self) -> bool:
        """Check if any MAJOR issues exist."""
        return any(r.level == "MAJOR" for r in self.results)

    @property
    def has_minor(self) -> bool:
        """Check if any MINOR issues exist."""
        return any(r.level == "MINOR" for r in self.results)

    @property
    def has_nit(self) -> bool:
        """Check if any NIT issues exist."""
        return any(r.level == "NIT" for r in self.results)

    @property
    def has_warning(self) -> bool:
        """Check if any WARNING issues exist."""
        return any(r.level == "WARNING" for r in self.results)

    @property
    def exit_code(self) -> int:
        """Get appropriate exit code based on highest severity issue.

        NIT and WARNING never affect exit code here.
        NIT blocking is handled by --strict flag in each validator's main().
        WARNING never blocks validation.
        """
        if self.has_critical:
            return EXIT_CRITICAL
        if self.has_major:
            return EXIT_MAJOR
        if self.has_minor:
            return EXIT_MINOR
        return EXIT_OK

    def exit_code_strict(self) -> int:
        """Get exit code for --strict mode (NIT issues also block).

        WARNING still does not block even in strict mode.
        """
        code = self.exit_code
        if code != EXIT_OK:
            return code
        if self.has_nit:
            return EXIT_NIT
        return EXIT_OK

    @property
    def score(self) -> int:
        """Calculate health score (0-100) based on validation results.

        Scoring:
        - Start at 100
        - Deduct 25 for each CRITICAL
        - Deduct 10 for each MAJOR
        - Deduct 3 for each MINOR
        - Deduct 1 for each NIT
        - WARNING, INFO, and PASSED don't affect score
        """
        score = 100
        for r in self.results:
            if r.level == "CRITICAL":
                score -= 25
            elif r.level == "MAJOR":
                score -= 10
            elif r.level == "MINOR":
                score -= 3
            elif r.level == "NIT":
                score -= 1
        return max(0, score)

    def count_by_level(self) -> dict[str, int]:
        """Get count of results by level."""
        counts: dict[str, int] = {"CRITICAL": 0, "MAJOR": 0, "MINOR": 0, "NIT": 0, "WARNING": 0, "INFO": 0, "PASSED": 0}
        for r in self.results:
            counts[r.level] = counts.get(r.level, 0) + 1
        return counts

    def merge(self, other: "ValidationReport") -> None:
        """Merge results from another report into this one."""
        self.results.extend(other.results)

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary for JSON serialization."""
        counts = self.count_by_level()
        return {
            "score": self.score,
            "grade": calculate_letter_grade(self.score),
            "exit_code": self.exit_code,
            "counts": counts,
            "results": [r.to_dict() for r in self.results],
            "fixable_count": len(self.fixable_issues),
            "valid_items_count": len(self.valid_items),
            "failed_items_count": len(self.failed_items),
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert report to JSON string.

        Args:
            indent: JSON indentation level (default 2)

        Returns:
            JSON string representation of the report
        """
        return json.dumps(self.to_dict(), indent=indent)

    # =========================================================================
    # Error Accumulation Pattern Methods
    # =========================================================================

    def get_all_errors(self) -> list[ValidationResult]:
        """Get all error results (CRITICAL, MAJOR, MINOR).

        Returns:
            List of all error-level results, excluding INFO and PASSED
        """
        return [r for r in self.results if r.level in ("CRITICAL", "MAJOR", "MINOR")]

    def get_errors_by_level(self, level: Level) -> list[ValidationResult]:
        """Get all results of a specific level.

        Args:
            level: The severity level to filter by

        Returns:
            List of results matching the specified level
        """
        return [r for r in self.results if r.level == level]

    def get_errors_by_phase(self, phase: str) -> list[ValidationResult]:
        """Get all errors from a specific validation phase.

        Args:
            phase: The validation phase to filter by

        Returns:
            List of error results from the specified phase
        """
        return [r for r in self.results if r.phase == phase and r.level in ("CRITICAL", "MAJOR", "MINOR")]

    # =========================================================================
    # Partial Validation Support Methods
    # =========================================================================

    def add_valid_item(self, item: Any) -> None:
        """Add an item that passed validation.

        Args:
            item: The validated item (can be any type)
        """
        self.valid_items.append(item)

    def add_failed_item(self, item: Any) -> None:
        """Add an item that failed validation.

        Args:
            item: The failed item (can be any type)
        """
        self.failed_items.append(item)

    def get_valid_items(self) -> list[Any]:
        """Get list of items that passed validation.

        Returns:
            List of valid items (even if some items failed)
        """
        return self.valid_items

    def get_failed_items(self) -> list[Any]:
        """Get list of items that failed validation.

        Returns:
            List of failed items
        """
        return self.failed_items

    # =========================================================================
    # Fixable Issues Support Methods
    # =========================================================================

    def add_fixable(
        self,
        level: Level,
        message: str,
        fix_func: FixFunction,
        fix_description: str,
        file: str | None = None,
        line: int | None = None,
        phase: str | None = None,
    ) -> None:
        """Add a validation result that can be auto-fixed.

        Args:
            level: Severity level
            message: Human-readable description
            fix_func: Function that fixes this issue
            fix_description: Description of what the fix does
            file: Optional file path
            line: Optional line number
            phase: Optional validation phase
        """
        # Generate a unique fix_id
        fix_id = f"fix_{len(self.fixable_issues)}"

        # Add the result with fixable flag
        result = ValidationResult(
            level=level,
            message=message,
            file=file,
            line=line,
            phase=phase,
            fixable=True,
            fix_id=fix_id,
        )
        self.results.append(result)

        # Register the fixable issue
        fixable = FixableIssue(
            result=result,
            fix_func=fix_func,
            fix_description=fix_description,
        )
        self.fixable_issues.append(fixable)

    def get_fixable_issues(self) -> list[FixableIssue]:
        """Get list of all fixable issues.

        Returns:
            List of FixableIssue objects that can be auto-fixed
        """
        return self.fixable_issues

    def apply_fixes(self, dry_run: bool = False) -> dict[str, int]:
        """Apply all registered auto-fixes.

        Args:
            dry_run: If True, don't actually apply fixes, just count them

        Returns:
            Dictionary with counts: {"applied": N, "failed": M, "skipped": K}
        """
        stats = {"applied": 0, "failed": 0, "skipped": 0}

        for fixable in self.fixable_issues:
            if dry_run:
                stats["skipped"] += 1
                continue

            try:
                success = fixable.apply()
                if success:
                    stats["applied"] += 1
                    # Update the result to PASSED if fix succeeded
                    fixable.result.level = "PASSED"
                    fixable.result.message = f"[FIXED] {fixable.result.message}"
                else:
                    stats["failed"] += 1
            except Exception:
                stats["failed"] += 1

        return stats


@dataclass
class ValidationContext:
    """Context for collecting validation errors without failing fast.

    This class implements the Error Accumulation Pattern, allowing validators
    to collect ALL errors before reporting rather than stopping at the first error.

    Usage:
        ctx = ValidationContext("my-validation")
        ctx.check(condition1, "MAJOR", "Error message 1")
        ctx.check(condition2, "MINOR", "Error message 2")
        report = ctx.finalize()
    """

    name: str
    report: ValidationReport = field(default_factory=ValidationReport)
    current_phase: str | None = None

    def set_phase(self, phase: str) -> None:
        """Set the current validation phase.

        Args:
            phase: Phase name (use PHASE_* constants)
        """
        self.current_phase = phase

    def check(
        self,
        condition: bool,
        level: Level,
        message: str,
        file: str | None = None,
        line: int | None = None,
    ) -> bool:
        """Check a condition and record result.

        Args:
            condition: If True, check passes; if False, adds error
            level: Severity level if check fails
            message: Error message if check fails
            file: Optional file path
            line: Optional line number

        Returns:
            The condition value (True if passed, False if failed)
        """
        if condition:
            self.report.passed(f"[{self.name}] {message}", file)
        else:
            self.report.add(level, f"[{self.name}] {message}", file, line, self.current_phase)
        return condition

    def require(
        self,
        condition: bool,
        message: str,
        file: str | None = None,
        line: int | None = None,
    ) -> bool:
        """Check a required condition (CRITICAL if fails).

        Args:
            condition: If True, check passes; if False, adds CRITICAL error
            message: Error message if check fails
            file: Optional file path
            line: Optional line number

        Returns:
            The condition value
        """
        return self.check(condition, "CRITICAL", message, file, line)

    def validate_item(
        self,
        item: Any,
        validator_func: Callable[[Any], bool],
        item_name: str,
    ) -> bool:
        """Validate an item and track it for partial validation.

        Args:
            item: The item to validate
            validator_func: Function that returns True if valid
            item_name: Name for error messages

        Returns:
            True if item is valid, False otherwise
        """
        try:
            is_valid = validator_func(item)
            if is_valid:
                self.report.add_valid_item(item)
            else:
                self.report.add_failed_item(item)
                self.report.add("MAJOR", f"Validation failed for {item_name}", phase=self.current_phase)
            return is_valid
        except Exception as e:
            self.report.add_failed_item(item)
            self.report.add("CRITICAL", f"Validation error for {item_name}: {e}", phase=self.current_phase)
            return False

    def add_error(
        self,
        level: Level,
        message: str,
        file: str | None = None,
        line: int | None = None,
    ) -> None:
        """Add an error without a condition check.

        Args:
            level: Severity level
            message: Error message
            file: Optional file path
            line: Optional line number
        """
        self.report.add(level, f"[{self.name}] {message}", file, line, self.current_phase)

    def add_fixable(
        self,
        level: Level,
        message: str,
        fix_func: FixFunction,
        fix_description: str,
        file: str | None = None,
        line: int | None = None,
    ) -> None:
        """Add a fixable error.

        Args:
            level: Severity level
            message: Error message
            fix_func: Function to fix this issue
            fix_description: Description of the fix
            file: Optional file path
            line: Optional line number
        """
        self.report.add_fixable(
            level=level,
            message=f"[{self.name}] {message}",
            fix_func=fix_func,
            fix_description=fix_description,
            file=file,
            line=line,
            phase=self.current_phase,
        )

    def finalize(self) -> ValidationReport:
        """Finalize the validation context and return the report.

        Returns:
            The collected ValidationReport with all results
        """
        return self.report

    @property
    def has_errors(self) -> bool:
        """Check if any errors were recorded.

        Returns:
            True if any CRITICAL, MAJOR, or MINOR issues exist
        """
        return bool(self.report.get_all_errors())

    @property
    def error_count(self) -> int:
        """Get total number of errors.

        Returns:
            Count of all error-level results
        """
        return len(self.report.get_all_errors())


# =============================================================================
# Utility Functions
# =============================================================================


def get_plugin_root() -> Path:
    """Get the plugin root directory (parent of scripts/).

    Returns:
        Path to the plugin root, assuming this module lives in scripts/.
    """
    return Path(__file__).resolve().parent.parent


def calculate_letter_grade(score: int) -> str:
    """Convert numeric score (0-100) to letter grade.

    Grade scale:
    - A+ : 97-100
    - A  : 93-96
    - A- : 90-92
    - B+ : 87-89
    - B  : 83-86
    - B- : 80-82
    - C+ : 77-79
    - C  : 73-76
    - C- : 70-72
    - D  : 60-69
    - F  : 0-59
    """
    if score >= 97:
        return "A+"
    elif score >= 93:
        return "A"
    elif score >= 90:
        return "A-"
    elif score >= 87:
        return "B+"
    elif score >= 83:
        return "B"
    elif score >= 80:
        return "B-"
    elif score >= 77:
        return "C+"
    elif score >= 73:
        return "C"
    elif score >= 70:
        return "C-"
    elif score >= 60:
        return "D"
    else:
        return "F"


def is_valid_kebab_case(name: str) -> bool:
    """Check if name follows kebab-case convention."""
    return bool(NAME_PATTERN.match(name))


# =============================================================================
# Color Formatting (for terminal output)
# =============================================================================

# ANSI color codes
COLORS = {
    "CRITICAL": "\033[91m",  # Red
    "MAJOR": "\033[93m",  # Yellow
    "MAJOR_DARK": "\033[33m",  # Dark Yellow
    "MINOR": "\033[94m",  # Blue
    "NIT": "\033[96m",  # Cyan — blocks only in --strict
    "WARNING": "\033[95m",  # Magenta — never blocks, always reported
    "INFO": "\033[90m",  # Gray
    "PASSED": "\033[92m",  # Green
    "RESET": "\033[0m",  # Reset
    "BOLD": "\033[1m",  # Bold
    "DIM": "\033[2m",  # Dim
}


def colorize(text: str, level: str) -> str:
    """Apply color to text based on level."""
    color = COLORS.get(level, "")
    return f"{color}{text}{COLORS['RESET']}"


def format_result(result: ValidationResult, show_file: bool = True) -> str:
    """Format a single validation result for terminal output."""
    color = COLORS.get(result.level, "")
    reset = COLORS["RESET"]

    parts = [f"{color}[{result.level}]{reset} {result.message}"]

    if show_file and result.file:
        location = result.file
        if result.line:
            location += f":{result.line}"
        parts.append(f" ({location})")

    return "".join(parts)


def print_report_summary(report: ValidationReport, title: str = "Validation Report") -> None:
    """Print a formatted summary of a validation report."""
    counts = report.count_by_level()
    score = report.score
    grade = calculate_letter_grade(score)

    print(f"\n{'=' * 60}")
    print(f"{COLORS['BOLD']}{title}{COLORS['RESET']}")
    print(f"{'=' * 60}")

    # Print counts by level
    print(f"\n{COLORS['CRITICAL']}CRITICAL: {counts['CRITICAL']}{COLORS['RESET']}")
    print(f"{COLORS['MAJOR']}MAJOR:    {counts['MAJOR']}{COLORS['RESET']}")
    print(f"{COLORS['MINOR']}MINOR:    {counts['MINOR']}{COLORS['RESET']}")
    print(f"{COLORS['NIT']}NIT:      {counts.get('NIT', 0)}{COLORS['RESET']}")
    print(f"{COLORS['WARNING']}WARNING:  {counts.get('WARNING', 0)}{COLORS['RESET']}")
    print(f"{COLORS['INFO']}INFO:     {counts['INFO']}{COLORS['RESET']}")
    print(f"{COLORS['PASSED']}PASSED:   {counts['PASSED']}{COLORS['RESET']}")

    # Print score and grade
    grade_color = COLORS["PASSED"] if score >= 80 else COLORS["MAJOR"] if score >= 60 else COLORS["CRITICAL"]
    print(
        f"\n{COLORS['BOLD']}Health Score:{COLORS['RESET']} {grade_color}{score}/100 (Grade: {grade}){COLORS['RESET']}"
    )

    # Print exit code interpretation
    exit_code = report.exit_code
    if exit_code == EXIT_OK:
        print(f"\n{COLORS['PASSED']}✓ All checks passed{COLORS['RESET']}")
    elif exit_code == EXIT_CRITICAL:
        print(f"\n{COLORS['CRITICAL']}✗ Critical issues found - must fix before use{COLORS['RESET']}")
    elif exit_code == EXIT_MAJOR:
        print(f"\n{COLORS['MAJOR']}! Major issues found - should fix{COLORS['RESET']}")
    else:
        print(f"\n{COLORS['MINOR']}~ Minor issues found - recommended to fix{COLORS['RESET']}")


def print_results_by_level(report: ValidationReport, verbose: bool = False) -> None:
    """Print validation results grouped by severity level."""
    # Group results by level
    by_level: dict[str, list[ValidationResult]] = {
        "CRITICAL": [],
        "MAJOR": [],
        "MINOR": [],
        "NIT": [],
        "WARNING": [],
        "INFO": [],
        "PASSED": [],
    }

    for result in report.results:
        by_level[result.level].append(result)

    # Always print blocking levels (CRITICAL, MAJOR, MINOR)
    for level in ["CRITICAL", "MAJOR", "MINOR"]:
        results = by_level[level]
        if results:
            print(f"\n{COLORS[level]}--- {level} ISSUES ({len(results)}) ---{COLORS['RESET']}")
            for result in results:
                print(f"  {format_result(result)}")

    # Always print NIT (blocks in --strict mode)
    if by_level["NIT"]:
        print(f"\n{COLORS['NIT']}--- NIT ISSUES ({len(by_level['NIT'])}) [blocks in --strict] ---{COLORS['RESET']}")
        for result in by_level["NIT"]:
            print(f"  {format_result(result)}")

    # Always print WARNING (never blocks, but always visible)
    if by_level["WARNING"]:
        print(f"\n{COLORS['WARNING']}--- WARNINGS ({len(by_level['WARNING'])}) [non-blocking] ---{COLORS['RESET']}")
        for result in by_level["WARNING"]:
            print(f"  {format_result(result)}")

    # Only print INFO and PASSED in verbose mode
    if verbose:
        for level in ["INFO", "PASSED"]:
            results = by_level[level]
            if results:
                print(f"\n{COLORS[level]}--- {level} ({len(results)}) ---{COLORS['RESET']}")
                for result in results:
                    print(f"  {format_result(result)}")


# =============================================================================
# File Encoding Utilities
# =============================================================================


def check_utf8_encoding(content: bytes, report: ValidationReport, filename: str) -> bool:
    """Check file is UTF-8 encoded without BOM.

    Args:
        content: Raw file bytes
        report: ValidationReport to add results to
        filename: Name of file for error messages

    Returns:
        True if encoding is valid, False otherwise
    """
    # Check for UTF-8 BOM (should not be present)
    if content.startswith(b"\xef\xbb\xbf"):
        report.major("File has UTF-8 BOM (should be UTF-8 without BOM)", filename)
        return False

    # Try to decode as UTF-8
    try:
        content.decode("utf-8")
        return True
    except UnicodeDecodeError as e:
        report.major(f"File is not valid UTF-8: {e}", filename)
        return False


def normalize_level(level: str) -> Level:
    """Normalize level string to uppercase Level type.

    Args:
        level: Level string (can be any case)

    Returns:
        Normalized Level literal
    """
    upper = level.upper()
    if upper in ("CRITICAL", "MAJOR", "MINOR", "NIT", "WARNING", "INFO", "PASSED"):
        return upper  # type: ignore
    # Default to INFO for unknown levels
    return "INFO"


# =============================================================================
# Private Information Scanning Functions
# =============================================================================


def scan_file_for_private_info(
    filepath: Path,
    report: ValidationReport,
    rel_path: str,
    additional_usernames: set[str] | None = None,
) -> int:
    """Scan a single file for private information (usernames, home paths).

    Args:
        filepath: Absolute path to the file
        report: ValidationReport to add results to
        rel_path: Relative path for error messages
        additional_usernames: Extra usernames to check beyond defaults

    Returns:
        Number of issues found
    """
    issues_found = 0

    # Build patterns including any additional usernames
    patterns = list(PRIVATE_PATH_PATTERNS)
    if additional_usernames:
        patterns.extend(build_private_path_patterns(additional_usernames))

    try:
        content = filepath.read_text(errors="ignore")
    except Exception:
        return 0

    for pattern, desc in patterns:
        for match in pattern.finditer(content):
            matched_text = match.group(0)
            line_num = content[: match.start()].count("\n") + 1
            issues_found += 1
            report.critical(
                f"Private info leaked: {desc} - found '{matched_text}' "
                "(replace with relative path or ${CLAUDE_PLUGIN_ROOT})",
                rel_path,
                line_num,
            )

    # Also check for generic home path patterns (MAJOR, not CRITICAL)
    # But only if no specific username was found
    if issues_found == 0:
        for pattern in USER_PATH_PATTERNS:
            for match in pattern.finditer(content):
                matched_text = match.group(0)

                # Skip if this looks like a regex pattern (contains metacharacters)
                if any(c in matched_text for c in r"[]\^$.*+?{}|()"):
                    continue

                # Extract the username from the path
                username_match = re.search(r"/Users/([^/\s]+)/", matched_text)
                if not username_match:
                    username_match = re.search(r"/home/([^/\s]+)/", matched_text)
                if not username_match:
                    username_match = re.search(r"\\Users\\([^\\\s]+)\\", matched_text)

                if username_match:
                    extracted_username = username_match.group(1).lower()
                    # Skip if it's a generic example username
                    if extracted_username in EXAMPLE_USERNAMES:
                        continue

                line_num = content[: match.start()].count("\n") + 1
                issues_found += 1
                report.major(
                    f"Hardcoded user path found: '{matched_text}...' (use relative paths or ${{CLAUDE_PLUGIN_ROOT}})",
                    rel_path,
                    line_num,
                )

    return issues_found


def scan_directory_for_private_info(
    root_path: Path,
    report: ValidationReport,
    additional_usernames: set[str] | None = None,
    skip_dirs: set[str] | None = None,
    respect_gitignore: bool = True,
) -> tuple[int, int]:
    """Scan a directory tree for private information.

    Args:
        root_path: Root directory to scan
        report: ValidationReport to add results to
        additional_usernames: Extra usernames to check beyond defaults
        skip_dirs: Additional directories to skip
        respect_gitignore: If True, skip files/dirs listed in .gitignore

    Returns:
        Tuple of (files_checked, issues_found)
    """
    files_checked = 0
    total_issues = 0

    # Combine skip dirs (includes gitignored dirs if respect_gitignore=True)
    if respect_gitignore:
        dirs_to_skip = get_skip_dirs_with_gitignore(root_path, skip_dirs)
        gitignore_patterns = parse_gitignore(root_path / ".gitignore") if (root_path / ".gitignore").exists() else []
    else:
        dirs_to_skip = set(PRIVATE_INFO_SKIP_DIRS)
        if skip_dirs:
            dirs_to_skip.update(skip_dirs)
        gitignore_patterns = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in dirs_to_skip]

        rel_dir = Path(dirpath).relative_to(root_path)

        for filename in filenames:
            filepath = Path(dirpath) / filename
            rel_path = str(rel_dir / filename) if str(rel_dir) != "." else filename

            # Skip gitignored files
            if respect_gitignore and gitignore_patterns and is_path_gitignored(rel_path, gitignore_patterns):
                continue

            # Check only relevant file types
            if filepath.suffix.lower() not in SCANNABLE_EXTENSIONS:
                continue

            files_checked += 1

            issues = scan_file_for_private_info(filepath, report, rel_path, additional_usernames)
            total_issues += issues

    return files_checked, total_issues


def validate_no_private_info(
    root_path: Path,
    report: ValidationReport,
    additional_usernames: set[str] | None = None,
) -> None:
    """Validate that a directory contains no private information.

    This is the main entry point for private info scanning.
    Checks for:
    - Private usernames in paths (CRITICAL)
    - Generic home directory paths (MAJOR)
    - Hardcoded absolute paths (MAJOR)

    Args:
        root_path: Root directory to scan
        report: ValidationReport to add results to
        additional_usernames: Extra usernames to check beyond PRIVATE_USERNAMES
    """
    files_checked, issues_found = scan_directory_for_private_info(root_path, report, additional_usernames)

    if issues_found == 0:
        report.passed(f"No private info found ({files_checked} files checked)")
    else:
        report.info(f"Found {issues_found} private info issue(s) in {files_checked} files")


def scan_file_for_absolute_paths(
    filepath: Path,
    report: ValidationReport,
    rel_path: str,
) -> int:
    """Scan a file for ANY absolute paths (stricter plugin validation).

    In plugins, ALL paths should be relative to ${CLAUDE_PLUGIN_ROOT} or use
    environment variables like ${HOME}. Absolute paths break portability.

    Args:
        filepath: Absolute path to the file
        report: ValidationReport to add results to
        rel_path: Relative path for error messages

    Returns:
        Number of issues found
    """
    issues_found = 0

    try:
        content = filepath.read_text(errors="ignore")
    except Exception:
        return 0

    # First check for private usernames (CRITICAL)
    private_patterns = build_private_path_patterns(PRIVATE_USERNAMES)
    for pattern, desc in private_patterns:
        for match in pattern.finditer(content):
            matched_text = match.group(0)
            line_num = content[: match.start()].count("\n") + 1
            issues_found += 1
            report.critical(
                f"Private path leaked: {desc} - '{matched_text}' (use relative path or ${{CLAUDE_PLUGIN_ROOT}})",
                rel_path,
                line_num,
            )

    # Determine if this is a documentation file (more lenient) or code file (strict)
    doc_extensions = {".md", ".txt", ".html", ".rst", ".adoc"}
    is_doc_file = filepath.suffix.lower() in doc_extensions

    # Then check for ALL absolute paths (MAJOR)
    for pattern, desc in ABSOLUTE_PATH_PATTERNS:
        for match in pattern.finditer(content):
            matched_text = match.group(1) if match.lastindex else match.group(0)

            # Skip if this looks like a regex pattern
            if any(c in matched_text for c in r"[]\^$.*+?{}|()"):
                continue

            # Skip allowed documentation paths — only in doc files, not in code/scripts
            if is_doc_file and any(matched_text.startswith(prefix) for prefix in ALLOWED_DOC_PATH_PREFIXES):
                continue

            # Skip if it's an environment variable reference
            if "${" in matched_text or matched_text.startswith("$"):
                continue

            # Extract username if it's a home path
            username_match = re.search(r"/(?:Users|home)/([^/\s]+)/", matched_text)
            if username_match:
                extracted_username = username_match.group(1).lower()
                # Skip example usernames in documentation
                if extracted_username in EXAMPLE_USERNAMES:
                    continue

            line_num = content[: match.start()].count("\n") + 1
            issues_found += 1
            # Use MINOR for system paths in scripts (may be intentional), MAJOR for home paths
            severity = "minor" if desc == "system absolute path" and not is_doc_file else "major"
            getattr(report, severity)(
                f"Absolute path found: '{matched_text[:60]}...' - "
                "use relative path, ${CLAUDE_PLUGIN_ROOT}, or ${CLAUDE_PROJECT_DIR}",
                rel_path,
                line_num,
            )

    return issues_found


def validate_no_absolute_paths(
    root_path: Path,
    report: ValidationReport,
    skip_dirs: set[str] | None = None,
    respect_gitignore: bool = True,
) -> None:
    """Validate that a plugin contains no absolute paths.

    This is a STRICT check for plugins. All paths should be:
    - Relative to plugin root (e.g., ./scripts/foo.py)
    - Using ${CLAUDE_PLUGIN_ROOT} for runtime resolution
    - Using ${HOME} or ~ for user home directory

    Args:
        root_path: Root directory to scan
        report: ValidationReport to add results to
        skip_dirs: Additional directories to skip
        respect_gitignore: If True, skip files/dirs listed in .gitignore
    """
    files_checked = 0
    total_issues = 0

    # Combine skip dirs (includes gitignored dirs if respect_gitignore=True)
    if respect_gitignore:
        dirs_to_skip = get_skip_dirs_with_gitignore(root_path, skip_dirs)
        gitignore_patterns = parse_gitignore(root_path / ".gitignore") if (root_path / ".gitignore").exists() else []
    else:
        dirs_to_skip = set(PRIVATE_INFO_SKIP_DIRS)
        if skip_dirs:
            dirs_to_skip.update(skip_dirs)
        gitignore_patterns = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Skip excluded directories (including gitignored)
        dirnames[:] = [d for d in dirnames if d not in dirs_to_skip]

        rel_dir = Path(dirpath).relative_to(root_path)

        for filename in filenames:
            filepath = Path(dirpath) / filename
            rel_path = str(rel_dir / filename) if str(rel_dir) != "." else filename

            # Skip gitignored files
            if respect_gitignore and gitignore_patterns and is_path_gitignored(rel_path, gitignore_patterns):
                continue

            # Check only relevant file types
            if filepath.suffix.lower() not in SCANNABLE_EXTENSIONS:
                continue

            # Skip CPV's own validation infrastructure — it contains path
            # patterns and allowlists as data constants, not hardcoded paths
            if filename == "cpv_validation_common.py":
                continue

            files_checked += 1

            issues = scan_file_for_absolute_paths(filepath, report, rel_path)
            total_issues += issues

    if total_issues == 0:
        report.passed(f"No absolute paths found ({files_checked} files checked)")
    else:
        report.info(f"Found {total_issues} absolute path(s) in {files_checked} files")


# =============================================================================
# TOC Embedding Validation — ensures .md files embed TOCs from referenced files
# =============================================================================

# Regex to extract TOC entries from a reference file's "## Table of Contents" section
_TOC_SECTION_RE = re.compile(
    r"(?im)^##\s*(table\s+of\s+contents|contents|toc|index)\s*\n(.*?)(?=\n##\s|\Z)",
    re.DOTALL,
)

# Regex to extract individual TOC heading titles (strip numbering, links, bullets)
_TOC_ENTRY_RE = re.compile(r"(?m)^[\s]*[-*]?\s*(?:\d+\.?\s*)?(?:\[([^\]]+)\]\([^)]*\)|(.+))")

# Regex to find markdown links pointing to .md files in references/
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(((?:references/)?[^\s)]+\.md)\)")


def extract_toc_headings(md_content: str) -> list[str]:
    """Extract TOC heading titles from a markdown file's Table of Contents section.

    Returns a list of heading title strings (stripped of numbering/links/bullets).
    Returns empty list if no TOC section is found.
    """
    m = _TOC_SECTION_RE.search(md_content)
    if not m:
        return []

    toc_block = m.group(2)
    headings: list[str] = []

    for entry_match in _TOC_ENTRY_RE.finditer(toc_block):
        # Group 1 = link text [Title](#anchor), Group 2 = plain text
        title = (entry_match.group(1) or entry_match.group(2) or "").strip()
        if not title or title.startswith("---"):
            continue
        # Strip leading numbering like "1. " or "3a. "
        title_clean = re.sub(r"^\d+[a-z]?\.\s*", "", title).strip()
        if title_clean:
            headings.append(title_clean)

    return headings


# Files exempt from the TOC requirement — these file types serve
# structural roles and do not need a Table of Contents section.
_TOC_EXEMPT_NAMES = {"SKILL.md", "CLAUDE.md"}
_TOC_EXEMPT_DIRS = {"agents", "commands", "rules"}

# Regex to detect list items (bulleted or numbered)
_LIST_ITEM_RE = re.compile(r"\s*(?:[-*+]|\d+\.)\s")


def _is_toc_exempt(file_path: Path) -> bool:
    """Check if a file is exempt from the TOC requirement.

    Exempt: SKILL.md, CLAUDE.md, agent files under agents/,
    command files under commands/, rule files under rules/.
    """
    if file_path.name in _TOC_EXEMPT_NAMES:
        return True
    for part in file_path.parts:
        if part in _TOC_EXEMPT_DIRS:
            return True
    return False


def validate_toc_embedding(
    md_content: str,
    md_file_path: Path,
    base_dir: Path,
    report: ValidationReport,
) -> None:
    """Validate that .md files embed TOCs from referenced .md files.

    When a markdown file links to another .md file, the link should include
    the referenced file's Table of Contents inline, so agents can see what
    content is available before navigating.

    Links can appear anywhere — in paragraphs, headings, or list items.
    Referenced files can be anywhere inside the plugin directory.

    When a link appears inside a list item (bullet or numbered), it may be
    an embedded TOC entry rather than a standalone reference. In that case:
    - If the target has a TOC and the TOC IS embedded after the link: PASSED
    - If the target has a TOC but no TOC copy follows: WARNING (ambiguous)
    - If the target has no TOC and is not exempt: NIT (file should have TOC)

    When a link is NOT in a list item (clear standalone reference):
    - If the target has a TOC and the TOC IS embedded: PASSED
    - If the target has a TOC but not embedded: MINOR (should embed it)
    - If the target has no TOC: skip (separate validation handles it)

    Args:
        md_content: The content of the markdown file being validated
        md_file_path: Path to the markdown file being validated
        base_dir: Base directory for resolving relative references
        report: ValidationReport to add results to
    """
    lines = md_content.split("\n")
    rel_file = md_file_path.name
    refs_checked = 0
    refs_with_toc = 0

    for link_match in _MD_LINK_RE.finditer(md_content):
        link_target = link_match.group(2)

        # Resolve the referenced file path
        ref_path = base_dir / link_target
        if not ref_path.is_file():
            ref_path = md_file_path.parent / link_target
            if not ref_path.is_file():
                continue

        # Only validate .md files
        if ref_path.suffix.lower() != ".md":
            continue

        # Determine if this link is inside a list item (bullet/numbered)
        link_start = link_match.start()
        link_line_num = md_content[:link_start].count("\n")
        line_text = lines[link_line_num] if link_line_num < len(lines) else ""
        is_list_item = bool(_LIST_ITEM_RE.match(line_text))

        # Read the referenced file and extract its TOC
        try:
            ref_content = ref_path.read_text()
        except Exception:
            continue

        toc_headings = extract_toc_headings(ref_content)

        if not toc_headings:
            # Target file has no TOC
            if is_list_item and not _is_toc_exempt(ref_path):
                # The link is in a list item pointing to a file without a TOC.
                # We can't require TOC embedding, but the file itself should
                # have a TOC for progressive discovery.
                report.nit(
                    f"Referenced file '{ref_path.name}' (linked from a list in "
                    f"{rel_file}) has no Table of Contents section. All .md "
                    f"reference files should include a TOC for progressive "
                    f"discovery.",
                    rel_file,
                )
            # For non-list links or exempt files: skip (no TOC to embed)
            continue

        refs_checked += 1

        # Check if TOC headings appear within ~50 lines after the link
        search_start = max(0, link_line_num)
        search_end = min(len(lines), link_line_num + 50)
        nearby_text = "\n".join(lines[search_start:search_end])

        embedded_count = sum(1 for heading in toc_headings if heading.lower() in nearby_text.lower())

        min_required = min(2, len(toc_headings))
        if embedded_count >= min_required:
            refs_with_toc += 1
        elif is_list_item:
            # Ambiguous: link in a list item could be a TOC title that
            # happens to link to a .md file, or a genuine reference.
            # Report as WARNING since we cannot tell which it is.
            report.warning(
                f"Link to '{ref_path.name}' in a list entry of {rel_file} "
                f"points to a file with a TOC ({len(toc_headings)} sections) "
                f"but the TOC is not embedded after the link. If this is a "
                f"reference, embed the TOC so agents know what it contains. "
                f"If this is an embedded TOC title, avoid using markdown "
                f"links in TOC entries to prevent this ambiguity.",
                rel_file,
            )
        else:
            # Clear standalone reference — TOC must be embedded
            report.minor(
                f"Reference to '{ref_path.name}' in {rel_file} does not "
                f"include the file's Table of Contents ({len(toc_headings)} "
                f"sections). Embed the TOC inline so agents can see what "
                f"content is available before navigating to it.",
                rel_file,
            )

    if refs_checked > 0 and refs_with_toc == refs_checked:
        report.passed(
            f"All {refs_checked} referenced .md files have TOC embedded in {rel_file}",
            rel_file,
        )
