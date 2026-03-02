#!/usr/bin/env python3
"""
Claude Code Plugin Validator

Comprehensive validation suite for Claude Code plugins.
Validates structure, manifest, hooks, skills, scripts, and MCP servers.

Usage:
    uv run python scripts/validate_plugin.py /path/to/plugin
    uv run python scripts/validate_plugin.py --verbose
    uv run python scripts/validate_plugin.py --json
    uv run python scripts/validate_plugin.py --marketplace-only
    uv run python scripts/validate_plugin.py --skip-platform-checks windows

Flags:
    --marketplace-only: Skip plugin.json requirement for marketplace-only
                        distribution (strict=false). When using strict=false,
                        plugin.json should NOT exist (causes CLI issues).

    --skip-platform-checks: Skip platform-specific checks.
                        Valid platforms: windows, macos, linux
                        Use without args to skip all platform checks.
                        Example: --skip-platform-checks windows
                        Example: --skip-platform-checks (skips all)

Exit codes:
    0 - All checks passed (or only INFO/PASSED/WARNING/NIT)
    1 - CRITICAL issues found
    2 - MAJOR issues found
    3 - MINOR issues found
    4 - NIT issues found (--strict mode only)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

import yaml
from cpv_validation_common import ValidationReport, resolve_tool_command, validate_toc_embedding
from gitignore_filter import GitignoreFilter
from validate_hook import validate_hooks as validate_hook_file
from validate_mcp import validate_plugin_mcp
from validate_rules import validate_rules_directory

# Import comprehensive skill validator (190+ rules from AgentSkills OpenSpec, Nixtla, Meta-Skills)
from validate_skill_comprehensive import validate_skill as validate_skill_comprehensive

# Module-level gitignore filter — initialized in main(), used by scan functions
_gi: GitignoreFilter | None = None


def validate_manifest(
    plugin_root: Path, report: ValidationReport, marketplace_only: bool = False
) -> dict[str, Any] | None:
    """Validate plugin.json manifest.

    Args:
        plugin_root: Path to the plugin directory
        report: ValidationReport to add results to
        marketplace_only: If True, skip plugin.json requirement

    Returns:
        The manifest dict if valid, None otherwise
    """
    manifest_path = plugin_root / ".claude-plugin" / "plugin.json"

    if not manifest_path.exists():
        if marketplace_only:
            msg = "plugin.json correctly absent (marketplace-only, strict=false)"
            report.passed(msg, ".claude-plugin/plugin.json")
            return None
        report.critical("plugin.json not found", ".claude-plugin/plugin.json")
        return None

    if marketplace_only:
        report.major(
            "plugin.json EXISTS but should NOT for marketplace-only (strict=false). "
            "Remove .claude-plugin/plugin.json to fix CLI uninstall issues.",
            ".claude-plugin/plugin.json",
        )
        return None

    try:
        manifest = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as e:
        report.critical(f"Invalid JSON in plugin.json: {e}", ".claude-plugin/plugin.json")
        return None

    report.passed("plugin.json is valid JSON", ".claude-plugin/plugin.json")

    # Required field: name (per Anthropic docs, ONLY 'name' is required)
    if "name" not in manifest:
        report.critical(
            "Missing required field 'name' in plugin.json",
            ".claude-plugin/plugin.json",
        )
    else:
        report.passed("Required field 'name' present", ".claude-plugin/plugin.json")

    # Recommended fields
    recommended_fields = ["version", "description"]
    for fld in recommended_fields:
        if fld not in manifest:
            report.minor(
                f"Missing recommended field '{fld}' in plugin.json",
                ".claude-plugin/plugin.json",
            )
        else:
            report.passed(
                f"Recommended field '{fld}' present",
                ".claude-plugin/plugin.json",
            )

    # Name validation
    if "name" in manifest:
        name = manifest["name"]
        if name != name.lower():
            report.major(f"Plugin name must be lowercase: {name}", ".claude-plugin/plugin.json")
        if " " in name:
            report.major(
                f"Plugin name cannot contain spaces: {name}",
                ".claude-plugin/plugin.json",
            )
        if not re.match(r"^[a-z][a-z0-9-]*$", name):
            report.major(f"Plugin name must be kebab-case: {name}", ".claude-plugin/plugin.json")

    # Version validation
    if "version" in manifest:
        version = manifest["version"]
        if not re.match(r"^\d+\.\d+\.\d+", version):
            report.major(
                f"Version must be semver format: {version}",
                ".claude-plugin/plugin.json",
            )

    # Check for unknown fields — warn but don't block, as custom fields
    # may be consumed by plugin scripts or external tooling
    known_fields = {
        "name",
        "version",
        "description",
        "author",
        "homepage",
        "repository",
        "license",
        "keywords",
        "commands",
        "agents",
        "skills",
        "hooks",
        "mcpServers",
        "outputStyles",
        "lspServers",
    }
    for key in manifest.keys():
        if key not in known_fields:
            report.warning(
                f"Unknown manifest field '{key}' — not part of the Claude Code plugin spec. "
                f"If used by plugin scripts, consider documenting it.",
                ".claude-plugin/plugin.json",
            )

    # Validate repository field type — Claude Code requires a string URL, not an object
    if "repository" in manifest:
        repo_val = manifest["repository"]
        if not isinstance(repo_val, str):
            report.major(
                f"Field 'repository' must be a string URL (e.g. "
                f'"https://github.com/user/repo"), not {type(repo_val).__name__}. '
                f'Claude Code rejects object format like {{"type":"git","url":"..."}}.',
                ".claude-plugin/plugin.json",
            )

    # Validate author field structure
    if "author" in manifest:
        author = manifest["author"]
        if isinstance(author, str):
            report.passed("Author is a string (acceptable)", ".claude-plugin/plugin.json")
        elif isinstance(author, dict):
            if "name" not in author:
                report.major(
                    "'author' object missing required 'name' field",
                    ".claude-plugin/plugin.json",
                )
            elif not isinstance(author["name"], str):
                report.major(
                    "'author.name' must be a string",
                    ".claude-plugin/plugin.json",
                )
            else:
                report.passed("Author object has valid 'name' field", ".claude-plugin/plugin.json")
        else:
            report.major(
                f"'author' must be a string or object, got {type(author).__name__}",
                ".claude-plugin/plugin.json",
            )

    # Validate keywords field
    if "keywords" in manifest:
        kw = manifest["keywords"]
        if not isinstance(kw, list):
            report.major("'keywords' must be an array", ".claude-plugin/plugin.json")
        elif not all(isinstance(k, str) for k in kw):
            report.major("'keywords' must contain only strings", ".claude-plugin/plugin.json")
        else:
            report.passed(f"Keywords: {len(kw)} keyword(s)", ".claude-plugin/plugin.json")

    # Validate homepage and license field types
    for string_field in ("homepage", "license"):
        if string_field in manifest:
            val = manifest[string_field]
            if not isinstance(val, str):
                report.major(
                    f"'{string_field}' must be a string, got {type(val).__name__}",
                    ".claude-plugin/plugin.json",
                )

    # Validate component path fields start with ./
    path_fields = [
        "commands",
        "agents",
        "skills",
        "hooks",
        "mcpServers",
        "outputStyles",
        "lspServers",
    ]
    for key in path_fields:
        if key in manifest:
            value = manifest[key]
            if isinstance(value, str) and not value.startswith("./"):
                report.major(
                    f"Field '{key}' path must start with './': {value}",
                    ".claude-plugin/plugin.json",
                )
            elif isinstance(value, list):
                for i, path in enumerate(value):
                    if isinstance(path, str) and not path.startswith("./"):
                        report.major(
                            f"Field '{key}[{i}]' path must start with './': {path}",
                            ".claude-plugin/plugin.json",
                        )
            elif isinstance(value, dict):
                # Inline configuration object - valid for hooks, mcpServers, lspServers
                if key in ("hooks", "mcpServers", "lspServers"):
                    report.passed(
                        f"Field '{key}' uses inline configuration object",
                        ".claude-plugin/plugin.json",
                    )
                else:
                    report.major(
                        f"Field '{key}' must be a string path or array, not an object",
                        ".claude-plugin/plugin.json",
                    )

    # Check for duplicate hooks.json - the standard hooks/hooks.json is auto-loaded
    # so specifying it in manifest.hooks causes a duplicate load error
    if "hooks" in manifest:
        hooks_value = manifest["hooks"]
        if isinstance(hooks_value, str):
            # Normalize the path to check if it points to the auto-loaded file
            normalized = hooks_value.replace("\\", "/").lstrip("./")
            if normalized == "hooks/hooks.json":
                report.major(
                    "manifest.hooks points to 'hooks/hooks.json' which is auto-loaded by "
                    "Claude Code. This causes a duplicate load error. Remove the 'hooks' "
                    "field from plugin.json to fix.",
                    ".claude-plugin/plugin.json",
                )

    return cast(dict[str, Any], manifest)


def validate_structure(plugin_root: Path, report: ValidationReport, marketplace_only: bool = False) -> None:
    """Validate plugin directory structure.

    Args:
        plugin_root: Path to the plugin directory
        report: ValidationReport to add results to
        marketplace_only: If True, .claude-plugin directory is optional
    """
    claude_plugin_dir = plugin_root / ".claude-plugin"
    if not claude_plugin_dir.is_dir():
        if marketplace_only:
            msg = ".claude-plugin absent (marketplace-only, uses marketplace.json)"
            report.passed(msg)
        else:
            report.critical(".claude-plugin directory not found")
            return
    else:
        report.passed(".claude-plugin directory exists")

    # Components must be at root, NOT in .claude-plugin
    for component in ["commands", "agents", "skills", "hooks", "schemas", "bin"]:
        wrong_path = plugin_root / ".claude-plugin" / component
        if wrong_path.exists():
            report.critical(f"{component}/ must be at plugin root, not in .claude-plugin/")

    # Common directories
    common_dirs = {
        "commands": "INFO",
        "agents": "INFO",
        "skills": "INFO",
        "hooks": "INFO",
        "scripts": "INFO",
        "docs": "INFO",
    }

    for d, level in common_dirs.items():
        if (plugin_root / d).is_dir():
            report.passed(f"{d}/ directory exists")
        else:
            if level == "INFO":
                report.info(f"Optional directory {d}/ not found")
            else:
                report.minor(f"Directory {d}/ not found")

    # Check for non-standard directories — warn but don't block, since users
    # may add folders like libs/, modules/, resources/ needed by scripts
    known_dirs = {
        ".claude-plugin",
        ".git",
        ".github",
        ".gitignore",
        "commands",
        "agents",
        "skills",
        "hooks",
        "scripts",
        "docs",
        "rules",
        "schemas",
        "bin",
        "templates",
        "tests",
        # Common non-standard but legitimate dirs
        "lib",
        "libs",
        "modules",
        "resources",
        "assets",
        "data",
        "config",
        "configs",
        "examples",
        "samples",
        "references",
    }
    # Also skip hidden dirs and _dev dirs
    for item in plugin_root.iterdir():
        if not item.is_dir():
            continue
        dirname = item.name
        if dirname.startswith(".") or dirname.endswith("_dev"):
            continue
        if dirname.lower() not in known_dirs:
            report.warning(
                f"Non-standard directory '{dirname}/' — not part of the plugin spec. "
                f"If needed by plugin scripts, consider documenting its purpose in README."
            )


def validate_commands(plugin_root: Path, report: ValidationReport) -> None:
    """Validate command definitions."""
    commands_dir = plugin_root / "commands"

    if not commands_dir.is_dir():
        report.info("No commands/ directory found")
        return

    # Find all command files
    cmd_files = list(commands_dir.glob("*.md"))
    if not cmd_files:
        report.info("No command files (*.md) found in commands/")
        return

    report.info(f"Found {len(cmd_files)} command file(s)")

    for cmd_path in cmd_files:
        validate_command_file(cmd_path, report)


def validate_command_file(cmd_path: Path, report: ValidationReport) -> None:
    """Validate a single command file."""
    rel_path = f"commands/{cmd_path.name}"
    content = cmd_path.read_text()

    # Check frontmatter
    if not content.startswith("---"):
        report.critical("No frontmatter in command file", rel_path)
        return

    try:
        parts = content.split("---", 2)
        if len(parts) < 3:
            report.critical("Malformed frontmatter (missing closing ---)", rel_path)
            return

        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        report.critical(f"Invalid YAML frontmatter: {e}", rel_path)
        return

    if not frontmatter:
        report.critical("Empty frontmatter", rel_path)
        return

    report.passed("Valid YAML frontmatter", rel_path)

    # Required fields
    if "name" not in frontmatter:
        report.critical("Missing 'name' in frontmatter", rel_path)
    else:
        expected_name = cmd_path.stem
        if frontmatter["name"] != expected_name:
            report.major(
                f"Command name '{frontmatter['name']}' doesn't match filename '{expected_name}'",
                rel_path,
            )

    if "description" not in frontmatter:
        report.major("Missing 'description' in frontmatter", rel_path)


def validate_agents(plugin_root: Path, report: ValidationReport) -> None:
    """Validate agent definitions."""
    agents_dir = plugin_root / "agents"

    if not agents_dir.is_dir():
        report.info("No agents/ directory found")
        return

    # Find all agent files
    agent_files = list(agents_dir.glob("*.md"))
    if not agent_files:
        report.info("No agent files (*.md) found in agents/")
        return

    report.info(f"Found {len(agent_files)} agent file(s)")

    for agent_path in agent_files:
        validate_agent_file(agent_path, report)


def validate_agent_file(agent_path: Path, report: ValidationReport) -> None:
    """Validate a single agent file."""
    rel_path = f"agents/{agent_path.name}"
    content = agent_path.read_text()

    # Check frontmatter
    if not content.startswith("---"):
        report.critical("No frontmatter in agent file", rel_path)
        return

    try:
        parts = content.split("---", 2)
        if len(parts) < 3:
            report.critical("Malformed frontmatter (missing closing ---)", rel_path)
            return

        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        report.critical(f"Invalid YAML frontmatter: {e}", rel_path)
        return

    if not frontmatter:
        report.critical("Empty frontmatter", rel_path)
        return

    report.passed("Valid YAML frontmatter", rel_path)

    # Required fields for agents
    if "name" not in frontmatter:
        report.critical("Missing 'name' in frontmatter", rel_path)

    if "description" not in frontmatter:
        report.major("Missing 'description' in frontmatter", rel_path)

    # Validate TOC embedding — agent files must embed TOCs from referenced .md files
    validate_toc_embedding(content, agent_path, agent_path.parent, report)


def validate_hooks(plugin_root: Path, report: ValidationReport) -> None:
    """Validate hook configuration using comprehensive hook validator."""
    hooks_dir = plugin_root / "hooks"

    if not hooks_dir.is_dir():
        report.info("No hooks/ directory found")
        return

    hooks_json = hooks_dir / "hooks.json"
    if not hooks_json.exists():
        report.info("No hooks.json found")
        return

    # Use comprehensive hook validator
    hook_report = validate_hook_file(hooks_json, plugin_root)

    # Transfer all results to main report
    for result in hook_report.results:
        file_path = result.file
        if file_path:
            if file_path.startswith(str(plugin_root)):
                file_path = file_path[len(str(plugin_root)) + 1 :]
            if not file_path.startswith("hooks/"):
                file_path = f"hooks/{file_path}"
        else:
            file_path = "hooks/hooks.json"

        report.add(result.level, result.message, file_path, result.line)


def validate_mcp(plugin_root: Path, report: ValidationReport) -> None:
    """Validate MCP server configurations."""
    # Use comprehensive MCP validator
    mcp_report = validate_plugin_mcp(plugin_root)

    # Transfer all results to main report
    for result in mcp_report.results:
        report.add(result.level, result.message, result.file, result.line)


def validate_scripts(plugin_root: Path, report: ValidationReport) -> None:
    """Validate Python and shell scripts."""
    scripts_dir = plugin_root / "scripts"

    if not scripts_dir.is_dir():
        report.info("No scripts/ directory found")
        return

    # Python scripts
    py_files = list(scripts_dir.glob("*.py"))
    if py_files:
        # Ruff check - exclude E501 (line length) as it's configurable per project
        ruff_cmd = resolve_tool_command("ruff")
        if ruff_cmd:
            ruff_args = ruff_cmd + ["check", "--select", "E,F,W", "--ignore", "E501"]
            # If pyproject.toml exists in plugin root, use it for config
            pyproject = plugin_root / "pyproject.toml"
            if pyproject.exists():
                ruff_args.extend(["--config", str(pyproject)])
            ruff_args.extend([str(f) for f in py_files])
            result = subprocess.run(
                ruff_args,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                report.passed(f"Ruff check passed for {len(py_files)} Python files")
            else:
                # Aggregate ruff errors per-file to avoid inflating MAJOR count
                # Ruff output format: "path/to/file.py:line:col: CODE message"
                errors_by_file: dict[str, int] = {}
                for ruff_line in result.stdout.strip().split("\n"):
                    if ruff_line and ":" in ruff_line:
                        # Extract file path (first colon-separated field)
                        file_part = ruff_line.split(":")[0].strip()
                        if file_part:
                            errors_by_file[file_part] = errors_by_file.get(file_part, 0) + 1
                total_errors = sum(errors_by_file.values())
                for file_path_str, count in sorted(errors_by_file.items()):
                    # Report ONE MAJOR per file, with total error count for that file
                    rel = file_path_str
                    try:
                        rel = str(Path(file_path_str).relative_to(plugin_root))
                    except ValueError:
                        pass
                    report.major(f"Ruff: {count} error(s) in {rel}", rel)
                if not errors_by_file and result.stdout.strip():
                    # Fallback: ruff output did not match expected format
                    report.major(f"Ruff: {total_errors} error(s) across script files")
        else:
            report.minor("ruff not available locally or via uvx, skipping Python lint check")

        # Mypy check
        mypy_cmd = resolve_tool_command("mypy")
        if mypy_cmd:
            mypy_args = mypy_cmd + ["--ignore-missing-imports"]
            # If pyproject.toml exists in plugin root, use it for config
            pyproject = plugin_root / "pyproject.toml"
            if pyproject.exists():
                mypy_args.extend(["--config-file", str(pyproject)])
            mypy_args.extend([str(f) for f in py_files])
            result = subprocess.run(
                mypy_args,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                report.passed(f"Mypy check passed for {len(py_files)} Python files")
            else:
                for line in result.stdout.strip().split("\n"):
                    if line and not line.startswith("Success"):
                        report.minor(f"Mypy: {line}")
        else:
            report.minor("mypy not available locally or via uvx, skipping type check")

    # Shell scripts
    sh_files = list(scripts_dir.glob("*.sh"))
    for sh_file in sh_files:
        if not os.access(sh_file, os.X_OK):
            report.major(
                f"Shell script not executable: {sh_file.name}",
                f"scripts/{sh_file.name}",
            )
        else:
            report.passed(f"Shell script executable: {sh_file.name}", f"scripts/{sh_file.name}")

        # Shellcheck
        shellcheck_cmd = resolve_tool_command("shellcheck")
        if shellcheck_cmd:
            result = subprocess.run(
                shellcheck_cmd + [str(sh_file)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                report.passed(f"Shellcheck passed: {sh_file.name}")
            else:
                report.minor(f"Shellcheck issues in {sh_file.name}", f"scripts/{sh_file.name}")
        else:
            report.minor("shellcheck not available locally or via bunx/npx, skipping shell lint")


# =============================================================================
# Cross-Platform Compatibility Validation
# =============================================================================

# Script extensions and their platform availability
# Each entry: extension -> (language_name, available_platforms, notes)
SCRIPT_PLATFORM_MAP: dict[str, tuple[str, set[str], str]] = {
    ".sh": ("Bash/Shell", {"macos", "linux"}, "Not natively available on Windows"),
    ".bash": ("Bash", {"macos", "linux"}, "Not natively available on Windows"),
    ".zsh": ("Zsh", {"macos"}, "Not standard on Linux or Windows"),
    ".fish": ("Fish shell", set(), "Requires separate installation on all platforms"),
    ".ps1": ("PowerShell", {"windows"}, "Requires pwsh installation on macOS/Linux"),
    ".bat": ("Windows Batch", {"windows"}, "Not available on macOS or Linux"),
    ".cmd": ("Windows Batch", {"windows"}, "Not available on macOS or Linux"),
    ".nix": ("Nix", {"linux"}, "Not standard on macOS or Windows"),
}

# Cross-platform script languages (available everywhere with standard install)
CROSSPLATFORM_EXTENSIONS = {
    ".py",  # Python — widely available
    ".js",  # Node.js — widely available
    ".ts",  # TypeScript (via tsx/ts-node) — widely available
    ".mjs",  # ES module JavaScript
    ".cjs",  # CommonJS JavaScript
    ".rb",  # Ruby — often pre-installed on macOS
}

# Compiled binary extensions by platform
BINARY_PLATFORM_SUFFIXES: dict[str, str] = {
    # macOS
    "-darwin-arm64": "macOS ARM64 (Apple Silicon)",
    "-darwin-amd64": "macOS x86_64 (Intel)",
    "-darwin-x86_64": "macOS x86_64 (Intel)",
    "-darwin-universal": "macOS Universal",
    "-macos-arm64": "macOS ARM64 (Apple Silicon)",
    "-macos-amd64": "macOS x86_64 (Intel)",
    "-macos-x86_64": "macOS x86_64 (Intel)",
    # Linux
    "-linux-arm64": "Linux ARM64",
    "-linux-amd64": "Linux x86_64",
    "-linux-x86_64": "Linux x86_64",
    # Windows
    "-windows-arm64.exe": "Windows ARM64",
    "-windows-amd64.exe": "Windows x86_64",
    "-windows-x86_64.exe": "Windows x86_64",
}

# Minimum recommended platform set for compiled binaries
RECOMMENDED_PLATFORMS = {
    "macOS ARM64 (Apple Silicon)",
    "macOS x86_64 (Intel)",
    "Linux x86_64",
}


def _is_python_venv(dirpath: Path) -> bool:
    """Detect Python virtual environments by structural markers, not name.

    A directory is a venv if it contains pyvenv.cfg (created by python -m venv
    and virtualenv). This catches venvs regardless of name (.venv, .windows_venv,
    .virtualenv, my_env, etc.).
    """
    # pyvenv.cfg is the canonical marker — always created by venv/virtualenv
    if (dirpath / "pyvenv.cfg").is_file():
        return True
    # Fallback: bin/activate (Unix) or Scripts/activate.bat (Windows)
    if (dirpath / "bin" / "activate").is_file():
        return True
    if (dirpath / "Scripts" / "activate.bat").is_file():
        return True
    return False


def validate_cross_platform(plugin_root: Path, report: ValidationReport) -> None:
    """Validate cross-platform compatibility of plugin scripts and binaries.

    Checks:
    1. Scripts using platform-specific languages get warnings
    2. Compiled source code without binaries or build script = MAJOR error
    3. Compiled binaries should cover all major platforms
    """
    # Collect all files across the entire plugin tree
    platform_specific_scripts: dict[str, list[str]] = {}  # ext -> [relative paths]
    compiled_source_files: dict[str, list[str]] = {}  # lang -> [relative paths]
    all_files: list[str] = []

    # Compiled language source extensions and their build system markers
    compiled_languages: dict[str, tuple[str, list[str]]] = {
        ".rs": ("Rust", ["Cargo.toml", "Cargo.lock"]),
        ".go": ("Go", ["go.mod", "go.sum"]),
        ".c": ("C", ["Makefile", "CMakeLists.txt", "meson.build"]),
        ".cpp": ("C++", ["Makefile", "CMakeLists.txt", "meson.build"]),
        ".cc": ("C++", ["Makefile", "CMakeLists.txt", "meson.build"]),
        ".cxx": ("C++", ["Makefile", "CMakeLists.txt", "meson.build"]),
        ".swift": ("Swift", ["Package.swift"]),
        ".zig": ("Zig", ["build.zig"]),
    }

    # Directories to always skip (build artifacts, caches)
    skip_dirs = {
        "__pycache__",
        "node_modules",
        "dist",
        "build",
        "target",
        ".eggs",
    }

    # Use gitignore-aware walk to skip ignored files and directories
    for dirpath, dirnames, filenames in _gi.walk(plugin_root, skip_dirs=skip_dirs) if _gi else os.walk(plugin_root):
        if not _gi:
            # Fallback filtering when gitignore filter not initialized
            dirnames[:] = [
                d
                for d in dirnames
                if not d.startswith(".") and d not in skip_dirs and not _is_python_venv(Path(dirpath) / d)
            ]
        rel_dir = Path(dirpath).relative_to(plugin_root)

        for filename in filenames:
            ext = Path(filename).suffix.lower()
            rel_path = str(rel_dir / filename) if str(rel_dir) != "." else filename
            all_files.append(rel_path)

            if ext in SCRIPT_PLATFORM_MAP:
                platform_specific_scripts.setdefault(ext, []).append(rel_path)

            if ext in compiled_languages:
                lang_name = compiled_languages[ext][0]
                compiled_source_files.setdefault(lang_name, []).append(rel_path)

    # --- 1. Report platform-specific interpreted scripts ---
    if platform_specific_scripts:
        for ext, paths in platform_specific_scripts.items():
            lang_name, platforms, note = SCRIPT_PLATFORM_MAP[ext]
            if platforms:
                platforms_str = ", ".join(sorted(platforms))
                report.warning(
                    f"Found {len(paths)} {lang_name} script(s) ({ext}) — "
                    f"only natively available on {platforms_str}. {note}. "
                    f"Consider providing cross-platform alternatives or documenting requirements.",
                )
            else:
                report.warning(
                    f"Found {len(paths)} {lang_name} script(s) ({ext}) — {note}. "
                    f"Consider providing cross-platform alternatives.",
                )
    else:
        has_scripts = any(
            any(f.endswith(ext) for ext in CROSSPLATFORM_EXTENSIONS)
            for _, _, files in (_gi.walk(plugin_root, skip_dirs=skip_dirs) if _gi else os.walk(plugin_root))
            for f in files
        )
        if has_scripts:
            report.passed("All scripts use cross-platform languages")

    # --- 2. Check compiled source code has binaries or build script ---
    if compiled_source_files:
        # Search for bin/ directories recursively, skip gitignored paths
        bin_dirs = list(_gi.rglob("bin") if _gi else plugin_root.rglob("bin"))
        has_bin = any(d.is_dir() and any(d.iterdir()) for d in bin_dirs)

        for lang_name, source_paths in compiled_source_files.items():
            # Find expected build system files for this language
            expected_build_files: set[str] = set()
            for ext, (ln, build_markers) in compiled_languages.items():
                if ln == lang_name:
                    expected_build_files.update(build_markers)

            # Check if build system files exist at plugin root
            has_build_system = any((plugin_root / bf).exists() for bf in expected_build_files)

            # Check for a generic build/install script
            has_build_script = any(
                (plugin_root / s).exists()
                for s in [
                    "build.sh",
                    "install.sh",
                    "setup.sh",
                    "compile.sh",
                    "build.py",
                    "install.py",
                    "setup.py",
                    "Makefile",
                    "justfile",
                    "Taskfile.yml",
                ]
            )

            if has_bin:
                report.info(f"Found {len(source_paths)} {lang_name} source file(s) with compiled binaries in bin/")
            elif has_build_system or has_build_script:
                report.warning(
                    f"Found {len(source_paths)} {lang_name} source file(s) "
                    f"with build system but no pre-compiled binaries in bin/. "
                    f"Users will need to compile before use."
                )
            else:
                report.major(
                    f"Found {len(source_paths)} {lang_name} source file(s) "
                    f"but no compiled binaries in bin/ and no build script "
                    f"(build.sh, install.sh, Makefile, etc.). "
                    f"Provide pre-compiled binaries or a build/install script."
                )

    # --- 3. Check compiled binaries platform coverage ---
    # Search for bin/ directories recursively, skip gitignored paths
    all_bin_dirs = []
    for d in _gi.rglob("bin") if _gi else plugin_root.rglob("bin"):
        if not d.is_dir():
            continue
        # Also skip venvs detected structurally
        rel_parts = d.relative_to(plugin_root).parts[:-1]
        if any(_is_python_venv(plugin_root / Path(*rel_parts[: i + 1])) for i in range(len(rel_parts))):
            continue
        all_bin_dirs.append(d)
    if not all_bin_dirs:
        return

    binary_files: list[str] = []
    detected_platforms: set[str] = set()
    base_names: set[str] = set()

    for bin_dir in all_bin_dirs:
        for item in bin_dir.rglob("*"):
            if not item.is_file():
                continue
            name = item.name
            rel_path = str(item.relative_to(plugin_root))

            for suffix, platform_name in BINARY_PLATFORM_SUFFIXES.items():
                if suffix in name.lower():
                    binary_files.append(rel_path)
                    detected_platforms.add(platform_name)
                    base = name[: name.lower().index(suffix.split("-")[0] + "-")]
                    if base.endswith("-"):
                        base = base[:-1]
                    base_names.add(base)
                    break
            else:
                if not item.suffix and os.access(item, os.X_OK):
                    binary_files.append(rel_path)
                    base_names.add(name)
                elif item.suffix == ".exe":
                    binary_files.append(rel_path)
                    detected_platforms.add("Windows")
                    base_names.add(item.stem)
                elif item.suffix in {".dylib", ".so"}:
                    binary_files.append(rel_path)
                    if item.suffix == ".dylib":
                        detected_platforms.add("macOS")
                    else:
                        detected_platforms.add("Linux")

    if not binary_files:
        return

    report.info(f"Found {len(binary_files)} compiled binary file(s) for {len(base_names)} tool(s)")

    if detected_platforms:
        missing = RECOMMENDED_PLATFORMS - detected_platforms
        if missing:
            missing_str = ", ".join(sorted(missing))
            report.warning(
                f"Compiled binaries missing for: {missing_str}. "
                f"Detected platforms: {', '.join(sorted(detected_platforms))}. "
                f"Consider providing binaries for all major platforms."
            )
        else:
            report.passed(f"Compiled binaries cover recommended platforms: {', '.join(sorted(detected_platforms))}")
    else:
        report.warning(
            f"Found {len(binary_files)} binary file(s) without platform identifiers "
            f"in filename. Use naming convention like 'tool-darwin-arm64', "
            f"'tool-linux-amd64', 'tool-windows-amd64.exe' for multi-platform support."
        )


def validate_skills(plugin_root: Path, report: ValidationReport, skip_platform_checks: list[str] | None = None) -> None:
    """Validate all skills in the plugin's skills/ directory.

    Args:
        plugin_root: Path to plugin root directory
        report: ValidationReport to add results to
        skip_platform_checks: List of platforms to skip checks for (e.g., ['windows'])
    """
    skills_dir = plugin_root / "skills"

    if not skills_dir.is_dir():
        report.info("No skills/ directory found")
        return

    # Find all skill directories
    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir()]

    if not skill_dirs:
        report.info("No skill directories found in skills/")
        return

    report.info(f"Found {len(skill_dirs)} skill(s) to validate")

    # Validate each skill using comprehensive validator (190+ rules)
    for skill_dir in sorted(skill_dirs):
        skill_name = skill_dir.name
        # Use comprehensive validator with all checks enabled
        skill_report = validate_skill_comprehensive(
            skill_dir,
            strict_mode=True,  # Enable Nixtla strict mode
            strict_openspec=False,  # Don't require OpenSpec 6-field whitelist for plugins
            validate_pillars_flag=skill_name.startswith(("lang-", "convert-")),  # Auto-enable for lang-*/convert-*
            skip_platform_checks=skip_platform_checks,
        )

        # Transfer results to main report with skill path prefix
        for result in skill_report.results:
            file_path = f"skills/{skill_name}/{result.file}" if result.file else f"skills/{skill_name}"
            report.add(result.level, result.message, file_path, result.line)


def validate_readme(plugin_root: Path, report: ValidationReport) -> None:
    """Validate README.md exists."""
    readme = plugin_root / "README.md"
    if readme.exists():
        report.passed("README.md found")
    else:
        report.minor("README.md not found")


def validate_license(plugin_root: Path, report: ValidationReport) -> None:
    """Validate LICENSE file exists."""
    for license_name in ["LICENSE", "LICENSE.md", "LICENSE.txt"]:
        if (plugin_root / license_name).exists():
            report.passed(f"{license_name} found")
            return

    report.minor("No LICENSE file found")


def validate_rules(plugin_root: Path, report: ValidationReport) -> None:
    """Validate rule files in the plugin's rules/ directory.

    Rules are plain markdown files loaded alongside CLAUDE.md into model context.
    Checks: UTF-8 encoding, optional frontmatter (paths field), token budget.
    """
    rules_dir = plugin_root / "rules"

    if not rules_dir.is_dir():
        report.info("No rules/ directory found")
        return

    # Use the dedicated rules validator
    rules_report = validate_rules_directory(rules_dir, plugin_root=plugin_root)

    # Transfer results to main report
    for result in rules_report.results:
        report.add(result.level, result.message, result.file, result.line)


def validate_no_local_paths(plugin_root: Path, report: ValidationReport) -> None:
    """Validate that plugin files don't contain hardcoded local or absolute paths.

    Uses the stricter absolute path validation from cpv_validation_common.py.

    In plugins, ALL paths should be:
    - Relative to plugin root (e.g., ./scripts/foo.py)
    - Using ${CLAUDE_PLUGIN_ROOT} for runtime resolution
    - Using ${HOME} or ~ for user home directory

    Checks for:
    - Current user's home path (CRITICAL) - auto-detected from system
    - Any absolute home directory paths (MAJOR)

    Excludes:
    - Cache directories (.mypy_cache, .ruff_cache, __pycache__)
    - Development folders (docs_dev/, scripts_dev/, etc.)
    - .git/ directory
    - Allowed system paths (/tmp/, /dev/, /proc/, /sys/)
    - Generic example usernames in documentation
    - Test directories (tests/) — contain intentional test fixture paths
    """
    # Import the stricter absolute path validation from cpv_validation_common
    from cpv_validation_common import validate_no_absolute_paths

    # Use the strict absolute path validator which checks for:
    # - Current user's username (auto-detected) - CRITICAL
    # - ANY absolute paths that don't use env vars - MAJOR
    # We pass our local report since both have compatible interfaces
    validate_no_absolute_paths(plugin_root, report, skip_dirs={"tests"})  # type: ignore[arg-type]


# =============================================================================
# .gitignore Validation
# =============================================================================

# Patterns that a well-formed plugin .gitignore should include
# Each tuple: (pattern_to_search_for, description, severity)
# We check if the gitignore content covers these categories
EXPECTED_GITIGNORE_CATEGORIES: list[tuple[list[str], str, str]] = [
    # Cache/build artifacts
    (["__pycache__", "*.pyc"], "Python cache files (__pycache__ or *.pyc)", "warning"),
    (["node_modules"], "Node modules (node_modules/)", "warning"),
    ([".mypy_cache", ".ruff_cache", ".pytest_cache"], "Linter/type checker caches", "warning"),
    (["dist", "build", "*.egg-info"], "Build artifacts (dist/, build/, *.egg-info)", "warning"),
    # Temp/editor files
    ([".DS_Store", "Thumbs.db"], "OS metadata files (.DS_Store, Thumbs.db)", "warning"),
    (["*.swp", "*.swo", "*~", ".idea", ".vscode"], "Editor temp files", "warning"),
    # Environment/secrets
    ([".env", "*.env"], "Environment files (.env)", "major"),
    # Virtual environments
    ([".venv", "venv"], "Virtual environment directories", "major"),
]


def validate_gitignore(plugin_root: Path, report: ValidationReport) -> None:
    """Validate that the plugin has a .gitignore with essential patterns.

    Checks that cache files, build artifacts, temp files, secrets,
    and virtual environments are properly ignored.
    """
    gitignore_path = plugin_root / ".gitignore"

    if not gitignore_path.exists():
        report.major(
            "No .gitignore file found — cache files, build artifacts, "
            "and secrets may be accidentally included in the plugin"
        )
        return

    try:
        content = gitignore_path.read_text(encoding="utf-8")
    except Exception as e:
        report.minor(f"Could not read .gitignore: {e}")
        return

    # Strip comments and empty lines for pattern matching
    lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]
    missing_categories: list[tuple[str, str]] = []

    for patterns, description, severity in EXPECTED_GITIGNORE_CATEGORIES:
        # Check if ANY of the patterns in this category appear in the gitignore
        found = any(any(p.lower() in line.lower() for line in lines) for p in patterns)
        if not found:
            missing_categories.append((description, severity))

    if not missing_categories:
        report.passed(".gitignore covers all expected categories")
    else:
        for description, severity in missing_categories:
            getattr(report, severity)(f".gitignore missing coverage for: {description}")

    # Check for common anti-patterns in .gitignore
    # Ignoring the entire plugin source is almost certainly wrong
    if "*.py" in lines or "*.js" in lines or "*.ts" in lines:
        report.major(
            ".gitignore ignores all source files (*.py, *.js, or *.ts) — "
            "this will exclude plugin code from distribution"
        )

    # Scan for actual venv directories by structure (any name, not just .venv/venv)
    for item in plugin_root.iterdir():
        if item.is_dir() and _is_python_venv(item):
            dirname = item.name
            # Check if this specific directory is covered by .gitignore
            covered = any(dirname.lower() in line.lower() for line in lines)
            if not covered:
                report.major(
                    f"Virtual environment '{dirname}/' detected (contains pyvenv.cfg) "
                    f"but not covered by .gitignore. Add '{dirname}/' to .gitignore."
                )

    # Check that non-plugin artifacts that may exist are ignored
    # Look for actual artifacts in the tree that should be gitignored
    artifact_patterns = {
        "*.pyc": "Compiled Python files",
        ".DS_Store": "macOS metadata",
        "Thumbs.db": "Windows metadata",
    }
    for pattern_glob, desc in artifact_patterns.items():
        # Use gitignore-aware rglob — only find artifacts NOT covered by .gitignore
        if _gi:
            matches = [p for p in _gi.rglob(pattern_glob)]
        else:
            matches = list(plugin_root.rglob(pattern_glob))
        if matches:
            sample = matches[0].relative_to(plugin_root)
            report.warning(f"Found {len(matches)} {desc} file(s) (e.g. {sample}) that are not gitignored")


# Regex to find inline Python blocks inside YAML: `python3 -c "..."`  or `python -c "..."`
# Captures the Python code string passed to -c.
_YAML_INLINE_PYTHON_RE = re.compile(
    r'python3?\s+-c\s+"([^"]*(?:"[^"]*"[^"]*)*)"',
    re.DOTALL,
)

# Dangerous pattern: dict["key"] or dict['key'] inside an f-string.
# In YAML inline Python the shell strips the inner quotes, causing NameError.
# Matches: {expr["key"]}, {expr['key']}, {expr.method()["key"]} etc.
_FSTRING_DICT_BRACKET_RE = re.compile(
    r"""\{[^}]*\[["'][^"']+["']\][^}]*\}""",
)


def validate_workflow_inline_python(plugin_root: Path, report: ValidationReport) -> None:
    """Scan GitHub Actions workflow files for dangerous inline Python patterns.

    When a YAML workflow uses ``python3 -c "..."`` (double-quoted shell string),
    dict bracket access like source["repo"] inside f-strings will fail at
    runtime because the shell strips the inner double quotes before Python
    sees the code.  Python then interprets the bare word as an undefined
    variable name, causing NameError.

    This validator catches that pattern and reports it as MAJOR.
    """
    workflows_dir = plugin_root / ".github" / "workflows"
    if not workflows_dir.is_dir():
        return

    yaml_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    if not yaml_files:
        return

    found_any = False
    for yaml_path in yaml_files:
        try:
            content = yaml_path.read_text(encoding="utf-8")
        except Exception:
            continue

        rel_path = str(yaml_path.relative_to(plugin_root))

        # Find all inline Python blocks
        for match in _YAML_INLINE_PYTHON_RE.finditer(content):
            python_code = match.group(1)
            block_start_offset = match.start()

            # Search for f-strings with dict bracket access
            for bad_match in _FSTRING_DICT_BRACKET_RE.finditer(python_code):
                abs_offset = block_start_offset + bad_match.start()
                line_num = content[:abs_offset].count("\n") + 1
                snippet = bad_match.group(0)
                found_any = True
                report.major(
                    f"Inline Python uses dict bracket access in f-string: {snippet} "
                    "-- shell quoting will strip inner quotes causing NameError. "
                    "Extract value into a local variable first.",
                    rel_path,
                    line_num,
                )

    if not found_any and yaml_files:
        report.passed(f"No inline Python quoting issues in {len(yaml_files)} workflow file(s)")


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

    counts = {"CRITICAL": 0, "MAJOR": 0, "MINOR": 0, "NIT": 0, "WARNING": 0, "INFO": 0, "PASSED": 0}
    for r in report.results:
        counts[r.level] += 1

    print("\n" + "=" * 60)
    print("Plugin Validation Report")
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
        print(f"{colors['PASSED']}✓ All checks passed{colors['RESET']}")
    elif report.exit_code == 1:
        print(f"{colors['CRITICAL']}✗ CRITICAL issues found - plugin will not work{colors['RESET']}")
    elif report.exit_code == 2:
        print(f"{colors['MAJOR']}✗ MAJOR issues found - significant problems{colors['RESET']}")
    else:
        print(f"{colors['MINOR']}! MINOR issues found - may affect UX{colors['RESET']}")

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


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate Claude Code plugin")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show all results including passed checks",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--marketplace-only",
        action="store_true",
        help="Skip plugin.json requirement (for strict=false marketplace distribution)",
    )
    parser.add_argument(
        "--skip-platform-checks",
        nargs="*",
        metavar="PLATFORM",
        help="Skip platform-specific checks (e.g., --skip-platform-checks windows). "
        "Valid platforms: windows, macos, linux. Use without args to skip all.",
    )
    parser.add_argument("--strict", action="store_true", help="Strict mode — NIT issues also block validation")
    parser.add_argument("path", nargs="?", help="Plugin root path (default: parent of scripts/)")
    args = parser.parse_args()

    # Determine plugin root — always resolve to absolute path so relative_to() works
    if args.path:
        plugin_root = Path(args.path).resolve()
    else:
        plugin_root = Path(__file__).resolve().parent.parent

    if not plugin_root.is_dir():
        print(f"Error: {plugin_root} is not a directory", file=sys.stderr)
        return 1

    # Auto-resolve plugin cache directories that contain version subdirectories
    # e.g. ~/.claude/plugins/cache/marketplace/plugin-name/{1.0.0, 1.1.7}
    if not (plugin_root / ".claude-plugin").is_dir():
        version_dirs = sorted(
            [d for d in plugin_root.iterdir() if d.is_dir() and re.match(r"\d+\.\d+", d.name)],
            key=lambda d: d.name,
            reverse=True,
        )
        if version_dirs and (version_dirs[0] / ".claude-plugin").is_dir():
            plugin_root = version_dirs[0]
            print(f"Auto-resolved to latest version: {plugin_root.name}", file=sys.stderr)
        elif not args.marketplace_only:
            # No .claude-plugin/ found and no version subdirs — not a plugin directory
            print(
                f"Error: No Claude Code plugin found at {plugin_root}\n"
                f"Expected a .claude-plugin/ directory. "
                f"Make sure you are running this from the plugin root directory.",
                file=sys.stderr,
            )
            return 1

    # Initialize gitignore filter — all scan functions use this to skip ignored files
    global _gi  # noqa: PLW0603
    _gi = GitignoreFilter(plugin_root)

    # Run validation
    report = ValidationReport()
    marketplace_only = args.marketplace_only
    skip_platform_checks = args.skip_platform_checks

    validate_manifest(plugin_root, report, marketplace_only)
    validate_structure(plugin_root, report, marketplace_only)
    validate_commands(plugin_root, report)
    validate_agents(plugin_root, report)
    validate_hooks(plugin_root, report)
    validate_mcp(plugin_root, report)
    validate_scripts(plugin_root, report)
    validate_skills(plugin_root, report, skip_platform_checks)
    validate_rules(plugin_root, report)
    validate_readme(plugin_root, report)
    validate_license(plugin_root, report)
    validate_no_local_paths(plugin_root, report)
    validate_gitignore(plugin_root, report)
    validate_cross_platform(plugin_root, report)
    validate_workflow_inline_python(plugin_root, report)

    # Output
    if args.json:
        print_json(report)
    else:
        print_results(report, args.verbose)

    if args.strict:
        return report.exit_code_strict()
    return report.exit_code


if __name__ == "__main__":
    sys.exit(main())
