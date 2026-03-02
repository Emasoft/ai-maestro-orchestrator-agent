#!/usr/bin/env python3
"""
Claude Plugins Validation - Cross-Reference Validator

Validates cross-references between plugin components:
1. Agent Task() calls must reference existing agents in agents/ directory
2. Subagent_type must match actual agent filenames
3. Version synchronization between plugin.json, marketplace entry, and README
4. Breaking references detection for commands calling non-existent agents
5. Skills referenced in code should exist in skills/ directory
6. Hook scripts referenced in hooks.json must exist

Usage:
    uv run python scripts/validate_xref.py /path/to/plugin
    uv run python scripts/validate_xref.py /path/to/plugin --verbose
    uv run python scripts/validate_xref.py /path/to/plugin --json

Exit codes:
    0 - All checks passed (or only INFO/PASSED)
    1 - CRITICAL issues found
    2 - MAJOR issues found
    3 - MINOR issues found
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from cpv_validation_common import (
    COLORS,
    SKIP_DIRS,
    ValidationReport,
    print_report_summary,
    print_results_by_level,
)

# =============================================================================
# Regex Patterns for Cross-Reference Detection
# =============================================================================

# Pattern to find Task tool invocations with subagent_type parameter
# Matches patterns like: subagent_type: "my-agent" or subagent_type="my-agent"
SUBAGENT_TYPE_PATTERN = re.compile(
    r'subagent_type\s*[=:]\s*["\']([^"\']+)["\']',
    re.IGNORECASE,
)

# Pattern to find agent references in markdown (e.g., "spawn agent-name agent")
AGENT_SPAWN_PATTERN = re.compile(
    r'(?:spawn|invoke|call|use)\s+(?:the\s+)?["\']?([a-z][a-z0-9-]*)["\']?\s+agent',
    re.IGNORECASE,
)

# Pattern to find skill references in code and markdown
SKILL_REF_PATTERN = re.compile(
    r"(?:skill|skills)/([a-z][a-z0-9-]*)",
    re.IGNORECASE,
)

# Pattern to extract version from files
VERSION_PATTERN = re.compile(
    r'(?:version|VERSION)\s*[=:]\s*["\']?(\d+\.\d+\.\d+)["\']?',
    re.IGNORECASE,
)

# Pattern to find hook script references in hooks.json
HOOK_SCRIPT_PATTERN = re.compile(
    r'\$\{CLAUDE_PLUGIN_ROOT\}/([^"\'}\s]+)',
)


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class CrossReferenceValidationReport(ValidationReport):
    """Validation report for cross-references, extends base ValidationReport.

    Attributes:
        plugin_path: Path to the plugin being validated
        agent_refs: Dict mapping source files to their agent references
        skill_refs: Dict mapping source files to their skill references
        version_sources: Dict mapping file names to versions found
        hook_script_refs: List of hook script paths referenced
    """

    plugin_path: str = ""
    agent_refs: dict[str, list[str]] = field(default_factory=dict)
    skill_refs: dict[str, list[str]] = field(default_factory=dict)
    version_sources: dict[str, str] = field(default_factory=dict)
    hook_script_refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary for JSON serialization."""
        base = super().to_dict()
        base["plugin_path"] = self.plugin_path
        base["agent_refs"] = self.agent_refs
        base["skill_refs"] = self.skill_refs
        base["version_sources"] = self.version_sources
        base["hook_script_refs"] = self.hook_script_refs
        return base


# =============================================================================
# Helper Functions
# =============================================================================


def get_available_agents(plugin_root: Path) -> set[str]:
    """Get set of available agent names from agents/ directory.

    Args:
        plugin_root: Root path of the plugin

    Returns:
        Set of agent names (without .md extension)
    """
    agents_dir = plugin_root / "agents"
    if not agents_dir.exists():
        return set()

    agents = set()
    for agent_file in agents_dir.glob("*.md"):
        # Extract agent name from filename (remove .md extension)
        agent_name = agent_file.stem
        agents.add(agent_name)
    return agents


def get_available_skills(plugin_root: Path) -> set[str]:
    """Get set of available skill names from skills/ directory.

    Args:
        plugin_root: Root path of the plugin

    Returns:
        Set of skill names (directory names in skills/)
    """
    skills_dir = plugin_root / "skills"
    if not skills_dir.exists():
        return set()

    skills = set()
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir() and not skill_dir.name.startswith("."):
            skills.add(skill_dir.name)
    return skills


def should_skip_dir(path: Path) -> bool:
    """Check if directory should be skipped during scanning.

    Args:
        path: Path to check

    Returns:
        True if directory should be skipped
    """
    return path.name in SKIP_DIRS or path.name.startswith(".")


def parse_yaml_frontmatter(content: str) -> dict[str, Any] | None:
    """Parse YAML frontmatter from markdown content.

    Args:
        content: Markdown file content

    Returns:
        Parsed frontmatter dict or None if not found/invalid
    """
    if not content.startswith("---"):
        return None

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None

    try:
        frontmatter = yaml.safe_load(parts[1])
        return frontmatter if isinstance(frontmatter, dict) else None
    except yaml.YAMLError:
        return None


# =============================================================================
# Rule 1: Agent Task() calls must reference existing agents
# =============================================================================


def validate_agent_task_refs(
    plugin_root: Path,
    report: CrossReferenceValidationReport,
    available_agents: set[str],
) -> None:
    """Validate that Task() calls reference existing agents.

    Parses agent .md files for Task tool references with subagent_type
    and verifies the referenced agents exist in agents/ directory.

    Args:
        plugin_root: Root path of the plugin
        report: Validation report to add results to
        available_agents: Set of available agent names
    """
    agents_dir = plugin_root / "agents"
    if not agents_dir.exists():
        report.info("No agents/ directory found - skipping Task() reference check")
        return

    for agent_file in agents_dir.glob("*.md"):
        try:
            content = agent_file.read_text(errors="ignore")
        except Exception as e:
            report.minor(f"Could not read agent file: {e}", str(agent_file.relative_to(plugin_root)))
            continue

        # Find all subagent_type references
        rel_path = str(agent_file.relative_to(plugin_root))
        matches = SUBAGENT_TYPE_PATTERN.findall(content)

        if matches:
            report.agent_refs[rel_path] = matches

        for ref_agent in matches:
            if ref_agent not in available_agents:
                report.major(
                    f"Task() references non-existent agent '{ref_agent}'",
                    rel_path,
                )
            else:
                report.passed(
                    f"Task() reference to '{ref_agent}' is valid",
                    rel_path,
                )


# =============================================================================
# Rule 2: Subagent_type must match actual agent filenames
# =============================================================================


def validate_subagent_type_matching(
    plugin_root: Path,
    report: CrossReferenceValidationReport,
    available_agents: set[str],
) -> None:
    """Validate subagent_type values match actual agent filenames.

    Scans all markdown files for subagent_type references and verifies
    that agents/NAME.md exists for each referenced NAME.

    Args:
        plugin_root: Root path of the plugin
        report: Validation report to add results to
        available_agents: Set of available agent names
    """
    # Scan all .md files in the plugin
    for md_file in plugin_root.rglob("*.md"):
        # Skip hidden directories and cache directories
        if any(should_skip_dir(p) for p in md_file.parents):
            continue

        try:
            content = md_file.read_text(errors="ignore")
        except Exception:
            continue

        rel_path = str(md_file.relative_to(plugin_root))
        matches = SUBAGENT_TYPE_PATTERN.findall(content)

        for ref_agent in matches:
            expected_file = plugin_root / "agents" / f"{ref_agent}.md"
            if not expected_file.exists():
                report.major(
                    f"subagent_type '{ref_agent}' has no matching agents/{ref_agent}.md",
                    rel_path,
                )


# =============================================================================
# Rule 3: Version synchronization
# =============================================================================


def validate_version_sync(
    plugin_root: Path,
    report: CrossReferenceValidationReport,
) -> None:
    """Validate version consistency across plugin files.

    Checks version in:
    - .claude-plugin/plugin.json (version field)
    - marketplace entry (if parent is a marketplace)
    - README.md (if version is mentioned)

    Args:
        plugin_root: Root path of the plugin
        report: Validation report to add results to
    """
    versions_found: dict[str, str] = {}

    # Check plugin.json
    plugin_json = plugin_root / ".claude-plugin" / "plugin.json"
    if plugin_json.exists():
        try:
            manifest = json.loads(plugin_json.read_text())
            if "version" in manifest:
                versions_found["plugin.json"] = manifest["version"]
        except (json.JSONDecodeError, Exception):
            pass

    # Check README.md for version mentions
    readme_path = plugin_root / "README.md"
    if readme_path.exists():
        try:
            content = readme_path.read_text(errors="ignore")
            # Look for version patterns like "Version: 1.0.0" or "version = 1.0.0"
            match = VERSION_PATTERN.search(content)
            if match:
                versions_found["README.md"] = match.group(1)
        except Exception:
            pass

    # Check marketplace.json in parent directory (if plugin is in a marketplace)
    marketplace_json = plugin_root.parent / "marketplace.json"
    if marketplace_json.exists():
        try:
            marketplace = json.loads(marketplace_json.read_text())
            plugins = marketplace.get("plugins", [])
            plugin_name = plugin_root.name
            for plugin_entry in plugins:
                if plugin_entry.get("name") == plugin_name:
                    if "version" in plugin_entry:
                        versions_found["marketplace.json"] = plugin_entry["version"]
                    break
        except (json.JSONDecodeError, Exception):
            pass

    # Check pyproject.toml for version (Python plugins)
    pyproject = plugin_root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            match = re.search(r'version\s*=\s*["\'](\d+\.\d+\.\d+)["\']', content)
            if match:
                versions_found["pyproject.toml"] = match.group(1)
        except Exception:
            pass

    report.version_sources = versions_found

    if len(versions_found) < 2:
        report.info(f"Only {len(versions_found)} version source(s) found - sync check skipped")
        return

    # Check for version mismatches
    unique_versions = set(versions_found.values())
    if len(unique_versions) == 1:
        version = list(unique_versions)[0]
        report.passed(f"All {len(versions_found)} version sources agree: {version}")
    else:
        version_list = ", ".join(f"{src}={ver}" for src, ver in versions_found.items())
        report.major(f"Version mismatch detected: {version_list}")


# =============================================================================
# Rule 4: Breaking references for commands calling non-existent agents
# =============================================================================


def validate_command_agent_refs(
    plugin_root: Path,
    report: CrossReferenceValidationReport,
    available_agents: set[str],
) -> None:
    """Validate that commands do not reference non-existent agents.

    Scans command .md files for agent references (spawn, invoke, etc.)
    and verifies the referenced agents exist.

    Args:
        plugin_root: Root path of the plugin
        report: Validation report to add results to
        available_agents: Set of available agent names
    """
    commands_dir = plugin_root / "commands"
    if not commands_dir.exists():
        report.info("No commands/ directory found - skipping command agent ref check")
        return

    for cmd_file in commands_dir.glob("*.md"):
        try:
            content = cmd_file.read_text(errors="ignore")
        except Exception as e:
            report.minor(f"Could not read command file: {e}", str(cmd_file.relative_to(plugin_root)))
            continue

        rel_path = str(cmd_file.relative_to(plugin_root))

        # Check for subagent_type references
        subagent_refs = SUBAGENT_TYPE_PATTERN.findall(content)
        for ref_agent in subagent_refs:
            if ref_agent not in available_agents:
                report.critical(
                    f"Command references non-existent agent '{ref_agent}' - BREAKING",
                    rel_path,
                )
            else:
                report.passed(
                    f"Command reference to agent '{ref_agent}' is valid",
                    rel_path,
                )

        # Check for spawn/invoke patterns
        spawn_refs = AGENT_SPAWN_PATTERN.findall(content)
        for ref_agent in spawn_refs:
            # Normalize the agent name (lowercase, trimmed)
            ref_agent_normalized = ref_agent.lower().strip()
            if ref_agent_normalized not in available_agents:
                # Check if it might be a built-in agent type
                builtin_types = {"basic", "task", "explore", "scout", "oracle", "haiku", "sonnet", "opus"}
                if ref_agent_normalized not in builtin_types:
                    report.major(
                        f"Command mentions unknown agent '{ref_agent}'",
                        rel_path,
                    )


# =============================================================================
# Rule 5: Skills referenced in code should exist
# =============================================================================


def validate_skill_refs(
    plugin_root: Path,
    report: CrossReferenceValidationReport,
    available_skills: set[str],
) -> None:
    """Validate that skill references point to existing skills.

    Scans code files for skill path references and verifies the
    referenced skills exist in skills/ directory.

    Args:
        plugin_root: Root path of the plugin
        report: Validation report to add results to
        available_skills: Set of available skill names
    """
    # File extensions to scan for skill references
    scan_extensions = {".py", ".sh", ".md", ".json", ".yaml", ".yml"}

    for ext in scan_extensions:
        for file_path in plugin_root.rglob(f"*{ext}"):
            # Skip hidden/cache directories
            if any(should_skip_dir(p) for p in file_path.parents):
                continue

            try:
                content = file_path.read_text(errors="ignore")
            except Exception:
                continue

            rel_path = str(file_path.relative_to(plugin_root))
            matches = SKILL_REF_PATTERN.findall(content)

            if matches:
                report.skill_refs[rel_path] = list(set(matches))

            for skill_name in set(matches):
                skill_name_lower = skill_name.lower()
                if skill_name_lower not in available_skills:
                    report.major(
                        f"Reference to non-existent skill '{skill_name}'",
                        rel_path,
                    )
                else:
                    report.passed(
                        f"Skill reference '{skill_name}' is valid",
                        rel_path,
                    )


# =============================================================================
# Rule 6: Hook scripts referenced in hooks.json must exist
# =============================================================================


def validate_hook_script_refs(
    plugin_root: Path,
    report: CrossReferenceValidationReport,
) -> None:
    """Validate that hook script references in hooks.json exist.

    Parses hooks/hooks.json (and any hooks referenced in plugin.json)
    and verifies that all script paths exist.

    Args:
        plugin_root: Root path of the plugin
        report: Validation report to add results to
    """
    hooks_files: list[Path] = []

    # Check default hooks/hooks.json
    default_hooks = plugin_root / "hooks" / "hooks.json"
    if default_hooks.exists():
        hooks_files.append(default_hooks)

    # Check for hooks referenced in plugin.json
    plugin_json = plugin_root / ".claude-plugin" / "plugin.json"
    if plugin_json.exists():
        try:
            manifest = json.loads(plugin_json.read_text())
            if "hooks" in manifest:
                hooks_val = manifest["hooks"]
                if isinstance(hooks_val, str):
                    # Path to hooks file
                    hooks_path = plugin_root / hooks_val.lstrip("./")
                    if hooks_path.exists() and hooks_path not in hooks_files:
                        hooks_files.append(hooks_path)
        except (json.JSONDecodeError, Exception):
            pass

    if not hooks_files:
        report.info("No hooks configuration found - skipping hook script check")
        return

    for hooks_file in hooks_files:
        try:
            hooks_content = hooks_file.read_text()
            hooks_config = json.loads(hooks_content)
        except (json.JSONDecodeError, Exception) as e:
            report.minor(f"Could not parse hooks file: {e}", str(hooks_file.relative_to(plugin_root)))
            continue

        rel_hooks_path = str(hooks_file.relative_to(plugin_root))

        # Extract all script paths from hooks config
        script_paths = extract_script_paths_from_hooks(hooks_config)
        report.hook_script_refs.extend(script_paths)

        for script_path in script_paths:
            # Resolve the path relative to plugin root
            # Scripts use ${CLAUDE_PLUGIN_ROOT} which maps to plugin_root
            resolved_path = plugin_root / script_path.lstrip("./")

            if not resolved_path.exists():
                report.critical(
                    f"Hook references non-existent script: {script_path}",
                    rel_hooks_path,
                )
            else:
                # Check if script is executable (for shell scripts)
                if resolved_path.suffix in {".sh", ".bash"}:
                    import os

                    if not os.access(resolved_path, os.X_OK):
                        report.minor(
                            f"Hook script is not executable: {script_path}",
                            rel_hooks_path,
                        )
                    else:
                        report.passed(
                            f"Hook script exists and is executable: {script_path}",
                            rel_hooks_path,
                        )
                else:
                    report.passed(
                        f"Hook script exists: {script_path}",
                        rel_hooks_path,
                    )


def extract_script_paths_from_hooks(hooks_config: dict[str, Any]) -> list[str]:
    """Extract all script paths from hooks configuration.

    Args:
        hooks_config: Parsed hooks.json content

    Returns:
        List of script paths referenced in the hooks
    """
    script_paths: list[str] = []

    def extract_from_value(value: Any) -> None:
        """Recursively extract script paths from a value."""
        if isinstance(value, str):
            # Check for ${CLAUDE_PLUGIN_ROOT} paths
            matches = HOOK_SCRIPT_PATTERN.findall(value)
            script_paths.extend(matches)
        elif isinstance(value, dict):
            # Check 'command' field specifically
            if "command" in value:
                cmd = value["command"]
                if isinstance(cmd, str):
                    matches = HOOK_SCRIPT_PATTERN.findall(cmd)
                    script_paths.extend(matches)
            # Recurse into nested dicts
            for v in value.values():
                extract_from_value(v)
        elif isinstance(value, list):
            for item in value:
                extract_from_value(item)

    extract_from_value(hooks_config)
    return list(set(script_paths))


# =============================================================================
# Main Validation Function
# =============================================================================


def validate_cross_references(plugin_path: str | Path) -> CrossReferenceValidationReport:
    """Validate all cross-references in a plugin.

    Args:
        plugin_path: Path to the plugin directory

    Returns:
        CrossReferenceValidationReport with all validation results
    """
    plugin_root = Path(plugin_path).resolve()
    report = CrossReferenceValidationReport()
    report.plugin_path = str(plugin_root)

    # Verify plugin directory exists
    if not plugin_root.exists():
        report.critical(f"Plugin directory does not exist: {plugin_root}")
        return report

    if not plugin_root.is_dir():
        report.critical(f"Plugin path is not a directory: {plugin_root}")
        return report

    # Get available components
    available_agents = get_available_agents(plugin_root)
    available_skills = get_available_skills(plugin_root)

    report.info(f"Found {len(available_agents)} agent(s) in agents/")
    report.info(f"Found {len(available_skills)} skill(s) in skills/")

    # Run all validation rules
    # Rule 1: Agent Task() calls
    validate_agent_task_refs(plugin_root, report, available_agents)

    # Rule 2: Subagent_type matching
    validate_subagent_type_matching(plugin_root, report, available_agents)

    # Rule 3: Version synchronization
    validate_version_sync(plugin_root, report)

    # Rule 4: Command agent references
    validate_command_agent_refs(plugin_root, report, available_agents)

    # Rule 5: Skill references
    validate_skill_refs(plugin_root, report, available_skills)

    # Rule 6: Hook script references
    validate_hook_script_refs(plugin_root, report)

    return report


# =============================================================================
# CLI Entry Point
# =============================================================================


def main() -> int:
    """CLI entry point for cross-reference validation.

    Returns:
        Exit code (0=OK, 1=CRITICAL, 2=MAJOR, 3=MINOR)
    """
    parser = argparse.ArgumentParser(
        description="Validate cross-references between Claude Code plugin components",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    uv run python scripts/validate_xref.py /path/to/plugin
    uv run python scripts/validate_xref.py /path/to/plugin --verbose
    uv run python scripts/validate_xref.py /path/to/plugin --json

Exit codes:
    0 - All checks passed
    1 - CRITICAL issues found
    2 - MAJOR issues found
    3 - MINOR issues found
        """,
    )
    parser.add_argument(
        "plugin_path",
        type=str,
        help="Path to the plugin directory to validate",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show all results including PASSED and INFO",
    )
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    # Resolve to absolute path so relative_to() works correctly
    plugin_path = Path(args.plugin_path).resolve()

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
    report = validate_cross_references(plugin_path)

    # Output results
    if args.json:
        print(report.to_json())
    else:
        print_report_summary(report, "Cross-Reference Validation Report")
        print_results_by_level(report, verbose=args.verbose)

        # Show cross-reference summary
        if args.verbose:
            print(f"\n{COLORS['BOLD']}Cross-Reference Summary:{COLORS['RESET']}")
            if report.agent_refs:
                print(f"  Agent references found in {len(report.agent_refs)} file(s)")
            if report.skill_refs:
                print(f"  Skill references found in {len(report.skill_refs)} file(s)")
            if report.version_sources:
                print(f"  Version sources: {', '.join(report.version_sources.keys())}")
            if report.hook_script_refs:
                print(f"  Hook scripts referenced: {len(report.hook_script_refs)}")

    return report.exit_code


if __name__ == "__main__":
    sys.exit(main())
