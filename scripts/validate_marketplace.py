#!/usr/bin/env python3
"""
Marketplace Validator for Claude Code Plugins.

Validates marketplace configuration files (marketplace.json) according to
Claude Code marketplace specifications.

A marketplace is a collection of plugins that can be installed via:
  claude plugin install <plugin-name>@<marketplace-name>

Exit Codes:
  0 - All checks passed
  1 - Critical issues found (marketplace unusable)
  2 - Major issues found (some plugins may fail)
  3 - Minor issues only (warnings)
"""

from __future__ import annotations

import argparse
import configparser
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from cpv_validation_common import (
    SEMVER_PATTERN,
    Level,
)
from cpv_validation_common import (
    ValidationReport as BaseValidationReport,
)
from cpv_validation_common import (
    ValidationResult as BaseValidationResult,
)

# =============================================================================
# Data Classes — extend canonical cpv_validation_common types
# =============================================================================


@dataclass
class MarketplaceValidationResult(BaseValidationResult):
    """Extended validation result with marketplace-specific fields."""

    category: str = ""
    suggestion: str | None = None

    @property
    def file_path(self) -> str | None:
        """Alias for backward compatibility — maps to canonical 'file' field."""
        return self.file

    @property
    def line_number(self) -> int | None:
        """Alias for backward compatibility — maps to canonical 'line' field."""
        return self.line


@dataclass
class MarketplaceValidationReport(BaseValidationReport):
    """Extended marketplace validation report with marketplace-specific fields."""

    marketplace_path: Path = field(default_factory=lambda: Path("."))
    marketplace_name: str | None = None
    plugins_found: list[str] = field(default_factory=list)
    plugins_validated: int = 0
    plugins_failed: int = 0

    def add_marketplace_result(
        self,
        level: Level,
        message: str,
        file: str | None = None,
        line: int | None = None,
        category: str = "",
        suggestion: str | None = None,
    ) -> None:
        """Add a marketplace-specific validation result with category/suggestion."""
        result = MarketplaceValidationResult(
            level=level,
            message=message,
            file=file,
            line=line,
            category=category,
            suggestion=suggestion,
        )
        self.results.append(result)


# Backward-compatibility aliases — existing code can still use these names
ValidationResult = MarketplaceValidationResult
ValidationReport = MarketplaceValidationReport


# =============================================================================
# Constants
# =============================================================================

# Valid source types for plugins in a marketplace
VALID_SOURCE_TYPES = {"github", "url", "npm", "pip"}

# Required fields in marketplace.json
REQUIRED_MARKETPLACE_FIELDS = {"name", "owner", "plugins"}

# Required fields for each plugin entry
REQUIRED_PLUGIN_FIELDS = {"name", "source"}

# Optional plugin fields
OPTIONAL_PLUGIN_FIELDS = {
    "version",
    "description",
    "source",
    "path",
    "repository",
    "author",
    "tags",
    "keywords",
    "license",
    "category",
    "dependencies",
    "enabled",
    "strict",
    "homepage",
    "commands",
    "agents",
    "skills",
    "hooks",
    "mcpServers",
    "lspServers",
    "outputStyles",
}

# Source-specific required fields
SOURCE_REQUIRED_FIELDS = {
    "github": {"repo"},
    "url": {"url"},
    "npm": {"package"},
    "pip": {"package"},
}

# Reserved marketplace names that cannot be used
RESERVED_MARKETPLACE_NAMES = {
    "claude-code-marketplace",
    "claude-code-plugins",
    "claude-plugins-official",
    "anthropic-marketplace",
    "anthropic-plugins",
    "agent-skills",
    "life-sciences",
}

# Name validation pattern (kebab-case)
NAME_PATTERN = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

# VERSION_PATTERN imported from cpv_validation_common as SEMVER_PATTERN

# Required README sections for GitHub deployment
# These patterns match common section header formats (# Section, ## Section, ### Section)
REQUIRED_README_SECTIONS = {
    "installation": re.compile(r"^#{1,3}\s*installation", re.IGNORECASE | re.MULTILINE),
    "update": re.compile(r"^#{1,3}\s*(update|updating)", re.IGNORECASE | re.MULTILINE),
    "uninstall": re.compile(r"^#{1,3}\s*(uninstall|remove|removal)", re.IGNORECASE | re.MULTILINE),
    "troubleshooting": re.compile(r"^#{1,3}\s*troubleshooting", re.IGNORECASE | re.MULTILINE),
}

# Required troubleshooting topics that should be documented
REQUIRED_TROUBLESHOOTING_TOPICS = {
    "hook_path_not_found": re.compile(
        r"(hook.*path.*not\s*found|can't\s*open\s*file.*hook|hook.*no\s*such\s*file)",
        re.IGNORECASE,
    ),
    "version_after_update": re.compile(
        r"(old\s*version.*after\s*update|version.*still.*showing|stale.*version)",
        re.IGNORECASE,
    ),
    "restart_required": re.compile(
        r"(restart.*claude\s*code|reload.*required|restart.*after.*update)",
        re.IGNORECASE,
    ),
}

# Required installation sub-steps (should be present in Installation section)
REQUIRED_INSTALLATION_STEPS = {
    "add_marketplace": re.compile(
        r"(marketplace\s+add|add\s+.*marketplace|claude\s+plugin\s+marketplace\s+add)",
        re.IGNORECASE,
    ),
    "install_plugin": re.compile(
        r"(plugin\s+install|install\s+.*plugin|claude\s+plugin\s+install)",
        re.IGNORECASE,
    ),
    "verify": re.compile(r"(verify|check|confirm|list)", re.IGNORECASE),
    "restart": re.compile(r"(restart|reload|relaunch)", re.IGNORECASE),
}


# =============================================================================
# Validation Functions
# =============================================================================


def validate_marketplace_file(
    marketplace_path: Path,
) -> tuple[dict[str, Any] | None, list[ValidationResult]]:
    """
    Validate and load a marketplace.json file.

    Args:
        marketplace_path: Path to marketplace directory or marketplace.json file

    Returns:
        Tuple of (parsed JSON data or None, list of validation results)
    """
    results: list[ValidationResult] = []

    # Determine the marketplace.json location
    # Can be at root (marketplace.json) or in .claude-plugin/ subdirectory
    if marketplace_path.is_file():
        json_path = marketplace_path
        marketplace_dir = marketplace_path.parent
    else:
        # Try root first
        json_path = marketplace_path / "marketplace.json"
        marketplace_dir = marketplace_path
        # If not found, try .claude-plugin/ subdirectory
        if not json_path.exists():
            json_path = marketplace_path / ".claude-plugin" / "marketplace.json"

    # Check file exists
    if not json_path.exists():
        results.append(
            ValidationResult(
                level="CRITICAL",
                category="structure",
                message=f"Marketplace configuration not found: {json_path}",
                file=str(json_path),
                suggestion="Create a marketplace.json file with name and plugins fields",
            )
        )
        return None, results

    # Parse JSON
    try:
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        results.append(
            ValidationResult(
                level="CRITICAL",
                category="manifest",
                message=f"Invalid JSON in marketplace.json: {e}",
                file=str(json_path),
                line=e.lineno,
                suggestion="Fix JSON syntax error",
            )
        )
        return None, results
    except Exception as e:
        results.append(
            ValidationResult(
                level="CRITICAL",
                category="manifest",
                message=f"Error reading marketplace.json: {e}",
                file=str(json_path),
            )
        )
        return None, results

    # Check it's a dict
    if not isinstance(data, dict):
        results.append(
            ValidationResult(
                level="CRITICAL",
                category="manifest",
                message="marketplace.json must be a JSON object",
                file=str(json_path),
                suggestion="Root element should be a JSON object with name and plugins fields",
            )
        )
        return None, results

    # Store the directory for later use
    data["_marketplace_dir"] = str(marketplace_dir)
    data["_json_path"] = str(json_path)

    return data, results


def validate_marketplace_name(name: Any, json_path: str) -> list[ValidationResult]:
    """Validate the marketplace name field."""
    results: list[ValidationResult] = []

    if not isinstance(name, str):
        results.append(
            ValidationResult(
                level="CRITICAL",
                category="manifest",
                message=f"Marketplace name must be a string, got {type(name).__name__}",
                file=json_path,
            )
        )
        return results

    if not name:
        results.append(
            ValidationResult(
                level="CRITICAL",
                category="manifest",
                message="Marketplace name cannot be empty",
                file=json_path,
            )
        )
        return results

    # Warn if not kebab-case
    if not NAME_PATTERN.match(name):
        results.append(
            ValidationResult(
                level="MINOR",
                category="manifest",
                message=f"Marketplace name '{name}' should use kebab-case (lowercase with hyphens)",
                file=json_path,
                suggestion="Use format: my-marketplace-name",
            )
        )

    # Check reserved marketplace names
    if name in RESERVED_MARKETPLACE_NAMES:
        results.append(
            ValidationResult(
                level="CRITICAL",
                category="marketplace",
                message=f"Marketplace name '{name}' is reserved and cannot be used",
                file=json_path,
            )
        )

    return results


def validate_plugin_entry(
    plugin: dict[str, Any],
    index: int,
    marketplace_dir: Path,
    json_path: str,
) -> list[ValidationResult]:
    """Validate a single plugin entry in the marketplace."""
    results: list[ValidationResult] = []
    plugin_id = plugin.get("name", f"plugins[{index}]")

    # Check required fields
    for field_name in REQUIRED_PLUGIN_FIELDS:
        if field_name not in plugin:
            results.append(
                ValidationResult(
                    level="CRITICAL",
                    category="plugin",
                    message=f"Plugin '{plugin_id}' missing required field: {field_name}",
                    file=json_path,
                )
            )

    # Validate name format
    name = plugin.get("name")
    if isinstance(name, str) and name:
        if not NAME_PATTERN.match(name):
            results.append(
                ValidationResult(
                    level="MINOR",
                    category="plugin",
                    message=f"Plugin name '{name}' should use kebab-case",
                    file=json_path,
                    suggestion="Use format: my-plugin-name",
                )
            )

    # Validate version if present
    version = plugin.get("version")
    if version is not None:
        if not isinstance(version, str):
            results.append(
                ValidationResult(
                    level="MAJOR",
                    category="plugin",
                    message=f"Plugin '{plugin_id}' version must be a string",
                    file=json_path,
                )
            )
        elif not SEMVER_PATTERN.match(version):
            results.append(
                ValidationResult(
                    level="MINOR",
                    category="plugin",
                    message=f"Plugin '{plugin_id}' version '{version}' should follow semver format",
                    file=json_path,
                    suggestion="Use format: X.Y.Z (e.g., 1.0.0)",
                )
            )

    # Validate source configuration
    source = plugin.get("source")
    if source is not None:
        results.extend(validate_plugin_source(plugin, plugin_id, marketplace_dir, json_path))

    # Validate local path if present
    local_path = plugin.get("path")
    if local_path is not None:
        results.extend(validate_local_path(local_path, plugin_id, marketplace_dir, json_path))

    # Validate repository URL if present
    repository = plugin.get("repository")
    if repository is not None:
        results.extend(validate_repository_url(repository, plugin_id, json_path))

    # Check for unknown fields
    known_fields = REQUIRED_PLUGIN_FIELDS | OPTIONAL_PLUGIN_FIELDS
    for field_name in plugin:
        if field_name not in known_fields:
            results.append(
                ValidationResult(
                    level="INFO",
                    category="plugin",
                    message=f"Plugin '{plugin_id}' has unknown field: {field_name}",
                    file=json_path,
                )
            )

    # Validate tags if present
    tags = plugin.get("tags")
    if tags is not None:
        if not isinstance(tags, list):
            results.append(
                ValidationResult(
                    level="MINOR",
                    category="plugin",
                    message=f"Plugin '{plugin_id}' tags must be an array",
                    file=json_path,
                )
            )
        elif not all(isinstance(t, str) for t in tags):
            results.append(
                ValidationResult(
                    level="MINOR",
                    category="plugin",
                    message=f"Plugin '{plugin_id}' tags must be strings",
                    file=json_path,
                )
            )

    # Validate dependencies if present
    deps = plugin.get("dependencies")
    if deps is not None:
        if not isinstance(deps, list):
            results.append(
                ValidationResult(
                    level="MAJOR",
                    category="plugin",
                    message=f"Plugin '{plugin_id}' dependencies must be an array",
                    file=json_path,
                )
            )
        elif not all(isinstance(d, str) for d in deps):
            results.append(
                ValidationResult(
                    level="MAJOR",
                    category="plugin",
                    message=f"Plugin '{plugin_id}' dependencies must be strings",
                    file=json_path,
                )
            )

    return results


def validate_plugin_source(
    plugin: dict[str, Any],
    plugin_id: str,
    marketplace_dir: Path,
    json_path: str,
) -> list[ValidationResult]:
    """Validate the source configuration for a plugin."""
    results: list[ValidationResult] = []
    source = plugin.get("source")

    if not isinstance(source, dict):
        # Source can also be a string shorthand
        if isinstance(source, str):
            # Accept relative paths (./path or ../path) as local source
            if source.startswith("./") or source.startswith("../"):
                # Validate that the local path exists
                resolved = marketplace_dir / source.lstrip("./")
                if not resolved.exists():
                    results.append(
                        ValidationResult(
                            level="MAJOR",
                            category="plugin",
                            message=f"Plugin '{plugin_id}' source path does not exist: {resolved}",
                            file=json_path,
                            suggestion="Ensure the plugin directory exists at the specified path",
                        )
                    )
            elif source not in VALID_SOURCE_TYPES:
                results.append(
                    ValidationResult(
                        level="MAJOR",
                        category="plugin",
                        message=f"Plugin '{plugin_id}' has invalid source type: {source}",
                        file=json_path,
                        suggestion=(
                            f"Valid source types: {', '.join(sorted(VALID_SOURCE_TYPES))} or relative path (./path)"
                        ),
                    )
                )
        else:
            results.append(
                ValidationResult(
                    level="MAJOR",
                    category="plugin",
                    message=f"Plugin '{plugin_id}' source must be a string or object",
                    file=json_path,
                )
            )
        return results

    # Source is a dict - validate source type (Anthropic schema uses "source" key inside the object)
    source_type = source.get("source")
    if source_type is None:
        results.append(
            ValidationResult(
                level="MAJOR",
                category="plugin",
                message=f"Plugin '{plugin_id}' source missing 'source' field",
                file=json_path,
                suggestion=f"Add source: {', '.join(sorted(VALID_SOURCE_TYPES))}",
            )
        )
    elif source_type not in VALID_SOURCE_TYPES:
        results.append(
            ValidationResult(
                level="MAJOR",
                category="plugin",
                message=f"Plugin '{plugin_id}' has invalid source type: {source_type}",
                file=json_path,
                suggestion=f"Valid source types: {', '.join(sorted(VALID_SOURCE_TYPES))}",
            )
        )
    else:
        # Check source-specific required fields
        required = SOURCE_REQUIRED_FIELDS.get(source_type, set())
        for field_name in required:
            if field_name not in source and field_name not in plugin:
                results.append(
                    ValidationResult(
                        level="MAJOR",
                        category="plugin",
                        message=f"Plugin '{plugin_id}' with source type '{source_type}' requires '{field_name}'",
                        file=json_path,
                    )
                )

        # Validate SHA format for GitHub sources
        if "sha" in source:
            sha = source["sha"]
            if not isinstance(sha, str) or not re.match(r"^[0-9a-f]{40}$", sha):
                results.append(
                    ValidationResult(
                        level="MINOR",
                        category="source",
                        message=f"Plugin '{plugin_id}' source 'sha' must be a 40-character hex string",
                        file=json_path,
                    )
                )

        # Check if using remote source type but plugin exists locally as submodule
        if source_type in ("github", "url"):
            plugin_name = plugin.get("name", plugin_id)
            local_plugin_path = marketplace_dir / plugin_name
            # Only warn if it exists as a git submodule (has .git file), not just a directory
            git_marker = local_plugin_path / ".git"
            if local_plugin_path.exists() and local_plugin_path.is_dir() and git_marker.exists():
                results.append(
                    ValidationResult(
                        level="MAJOR",
                        category="plugin",
                        message=f"Plugin '{plugin_id}' uses remote source but exists as local submodule",
                        file=json_path,
                        suggestion=(
                            f"Remove the local submodule checkout at './{plugin_name}' "
                            f"or change source to a relative path string"
                        ),
                    )
                )

    return results


def validate_local_path(
    local_path: Any,
    plugin_id: str,
    marketplace_dir: Path,
    json_path: str,
) -> list[ValidationResult]:
    """Validate a local file path for a plugin."""
    results: list[ValidationResult] = []

    if not isinstance(local_path, str):
        results.append(
            ValidationResult(
                level="MAJOR",
                category="plugin",
                message=f"Plugin '{plugin_id}' path must be a string",
                file=json_path,
            )
        )
        return results

    # Resolve the path
    if local_path.startswith("/"):
        # Absolute path - this is a CRITICAL issue for published marketplaces
        # as it exposes local filesystem structure and may contain usernames
        resolved = Path(local_path)
        results.append(
            ValidationResult(
                level="CRITICAL",
                category="plugin",
                message=f"Plugin '{plugin_id}' uses absolute path: {local_path}",
                file=json_path,
                suggestion=(
                    "Absolute paths expose local filesystem structure and may contain usernames. "
                    "Use relative paths (starting with ./) for local plugin references. "
                    f"Example: './{Path(local_path).name}' instead of '{local_path}'"
                ),
            )
        )
    else:
        # Relative to marketplace directory
        resolved = marketplace_dir / local_path

    # Check path exists
    if not resolved.exists():
        results.append(
            ValidationResult(
                level="MAJOR",
                category="plugin",
                message=f"Plugin '{plugin_id}' local path does not exist: {resolved}",
                file=json_path,
                suggestion="Ensure the path is relative to the marketplace directory or use absolute path",
            )
        )
    elif not resolved.is_dir():
        results.append(
            ValidationResult(
                level="MAJOR",
                category="plugin",
                message=f"Plugin '{plugin_id}' local path is not a directory: {resolved}",
                file=json_path,
            )
        )
    else:
        # Check for plugin.json in the plugin directory
        plugin_json = resolved / ".claude-plugin" / "plugin.json"
        if not plugin_json.exists():
            # Also check root plugin.json (legacy)
            alt_plugin_json = resolved / "plugin.json"
            if not alt_plugin_json.exists():
                results.append(
                    ValidationResult(
                        level="MAJOR",
                        category="plugin",
                        message=f"Plugin '{plugin_id}' directory missing plugin.json",
                        file=str(resolved),
                        suggestion="Add .claude-plugin/plugin.json to the plugin directory",
                    )
                )

    # Check for path traversal
    if ".." in local_path:
        results.append(
            ValidationResult(
                level="MINOR",
                category="plugin",
                message=f"Plugin '{plugin_id}' path contains '..' (path traversal)",
                file=json_path,
                suggestion="Use absolute paths or paths without parent directory references",
            )
        )

    return results


def validate_repository_url(
    repository: Any,
    plugin_id: str,
    json_path: str,
) -> list[ValidationResult]:
    """Validate a repository URL."""
    results: list[ValidationResult] = []

    if not isinstance(repository, str):
        results.append(
            ValidationResult(
                level="MINOR",
                category="plugin",
                message=f"Plugin '{plugin_id}' repository must be a string",
                file=json_path,
            )
        )
        return results

    # Try to parse as URL
    try:
        parsed = urlparse(repository)
        if not parsed.scheme:
            # Could be a GitHub shorthand (owner/repo)
            if "/" in repository and not repository.startswith("."):
                pass  # Valid shorthand
            else:
                results.append(
                    ValidationResult(
                        level="MINOR",
                        category="plugin",
                        message=f"Plugin '{plugin_id}' repository URL may be invalid: {repository}",
                        file=json_path,
                        suggestion="Use full URL or GitHub shorthand (owner/repo)",
                    )
                )
        elif parsed.scheme not in ("http", "https", "git", "ssh"):
            results.append(
                ValidationResult(
                    level="MINOR",
                    category="plugin",
                    message=f"Plugin '{plugin_id}' repository has unusual scheme: {parsed.scheme}",
                    file=json_path,
                )
            )
    except Exception:
        results.append(
            ValidationResult(
                level="MINOR",
                category="plugin",
                message=f"Plugin '{plugin_id}' repository URL could not be parsed",
                file=json_path,
            )
        )

    return results


def validate_plugins_array(
    plugins: Any,
    marketplace_dir: Path,
    json_path: str,
) -> tuple[list[str], list[ValidationResult]]:
    """Validate the plugins array in marketplace.json."""
    results: list[ValidationResult] = []
    plugin_names: list[str] = []

    if not isinstance(plugins, list):
        results.append(
            ValidationResult(
                level="CRITICAL",
                category="manifest",
                message="plugins field must be an array",
                file=json_path,
                suggestion="plugins: [{name: 'plugin-a'}, {name: 'plugin-b'}]",
            )
        )
        return plugin_names, results

    if len(plugins) == 0:
        results.append(
            ValidationResult(
                level="MINOR",
                category="manifest",
                message="plugins array is empty",
                file=json_path,
            )
        )
        return plugin_names, results

    # Validate each plugin
    seen_names: set[str] = set()
    for i, plugin in enumerate(plugins):
        if not isinstance(plugin, dict):
            results.append(
                ValidationResult(
                    level="CRITICAL",
                    category="plugin",
                    message=f"plugins[{i}] must be an object, got {type(plugin).__name__}",
                    file=json_path,
                )
            )
            continue

        # Track plugin name
        name = plugin.get("name")
        if isinstance(name, str):
            plugin_names.append(name)

            # Check for duplicates
            if name in seen_names:
                results.append(
                    ValidationResult(
                        level="MAJOR",
                        category="plugin",
                        message=f"Duplicate plugin name: {name}",
                        file=json_path,
                        suggestion="Each plugin must have a unique name",
                    )
                )
            seen_names.add(name)

        # Validate the plugin entry
        results.extend(validate_plugin_entry(plugin, i, marketplace_dir, json_path))

    return plugin_names, results


def validate_github_deployment(
    marketplace_dir: Path,
    plugins: list[dict[str, Any]],
) -> list[ValidationResult]:
    """
    Validate GitHub deployment structure for a marketplace.

    Checks:
    - Main README.md exists at marketplace root
    - README.md has required sections (Installation, Update, Uninstall, Troubleshooting)
    - Installation section has all required steps
    - Each plugin subfolder has its own README.md

    Args:
        marketplace_dir: Path to marketplace directory
        plugins: List of plugin entries from marketplace.json

    Returns:
        List of validation results
    """
    results: list[ValidationResult] = []

    # Check main README.md exists
    readme_path = marketplace_dir / "README.md"
    if not readme_path.exists():
        # Also check lowercase
        readme_path = marketplace_dir / "readme.md"

    if not readme_path.exists():
        results.append(
            ValidationResult(
                level="MAJOR",
                category="deployment",
                message="Missing README.md at marketplace root",
                file=str(marketplace_dir),
                suggestion="Create a README.md with installation instructions for users",
            )
        )
    else:
        # Validate README content
        results.extend(validate_readme_content(readme_path))

    # Check each plugin subfolder has README.md
    for plugin in plugins:
        source = plugin.get("source")
        plugin_name = plugin.get("name", "unknown")

        # Determine plugin path
        plugin_path: Path | None = None
        if isinstance(source, str) and source.startswith("./"):
            plugin_path = marketplace_dir / source[2:]
        elif isinstance(source, str) and not source.startswith(("http", "git@")):
            plugin_path = marketplace_dir / source
        elif "path" in plugin:
            path_val = plugin["path"]
            if isinstance(path_val, str):
                if path_val.startswith("./"):
                    plugin_path = marketplace_dir / path_val[2:]
                elif not path_val.startswith("/"):
                    plugin_path = marketplace_dir / path_val

        if plugin_path and plugin_path.exists() and plugin_path.is_dir():
            plugin_readme = plugin_path / "README.md"
            if not plugin_readme.exists():
                plugin_readme = plugin_path / "readme.md"

            if not plugin_readme.exists():
                results.append(
                    ValidationResult(
                        level="MINOR",
                        category="deployment",
                        message=f"Plugin '{plugin_name}' subfolder missing README.md",
                        file=str(plugin_path),
                        suggestion="Add README.md to plugin subfolder describing the plugin",
                    )
                )

    return results


def validate_readme_content(readme_path: Path) -> list[ValidationResult]:
    """
    Validate README.md has required sections for marketplace deployment.

    Args:
        readme_path: Path to README.md file

    Returns:
        List of validation results
    """
    results: list[ValidationResult] = []

    try:
        content = readme_path.read_text(encoding="utf-8")
    except Exception as e:
        results.append(
            ValidationResult(
                level="MAJOR",
                category="deployment",
                message=f"Could not read README.md: {e}",
                file=str(readme_path),
            )
        )
        return results

    # Check for required sections
    missing_sections: list[str] = []
    for section_name, pattern in REQUIRED_README_SECTIONS.items():
        if not pattern.search(content):
            missing_sections.append(section_name)

    if missing_sections:
        results.append(
            ValidationResult(
                level="MAJOR",
                category="deployment",
                message=f"README.md missing required sections: {', '.join(missing_sections)}",
                file=str(readme_path),
                suggestion="Add sections: ## Installation, ## Update, ## Uninstall, ## Troubleshooting",
            )
        )

    # Check installation section has required steps
    if "installation" not in missing_sections:
        missing_steps: list[str] = []
        for step_name, pattern in REQUIRED_INSTALLATION_STEPS.items():
            if not pattern.search(content):
                missing_steps.append(step_name.replace("_", " "))

        if missing_steps:
            results.append(
                ValidationResult(
                    level="MINOR",
                    category="deployment",
                    message=(f"README.md Installation section may be incomplete. Missing: {', '.join(missing_steps)}"),
                    file=str(readme_path),
                    suggestion=(
                        "Include steps for: add marketplace, install plugin, verify installation, restart Claude Code"
                    ),
                )
            )

    # Check for placeholder content
    placeholder_patterns = [
        r"\[TODO\]",
        r"\[INSERT",
        r"<your-",
        r"PLACEHOLDER",
        r"TBD",
    ]
    for placeholder_pattern in placeholder_patterns:
        if re.search(placeholder_pattern, content, re.IGNORECASE):
            results.append(
                ValidationResult(
                    level="MINOR",
                    category="deployment",
                    message="README.md contains placeholder content",
                    file=str(readme_path),
                    suggestion="Replace all placeholders with actual content before publishing",
                )
            )
            break

    # Check troubleshooting section has required topics
    if "troubleshooting" not in missing_sections:
        missing_topics: list[str] = []
        for topic_name, pattern in REQUIRED_TROUBLESHOOTING_TOPICS.items():
            if not pattern.search(content):
                missing_topics.append(topic_name.replace("_", " "))

        if missing_topics:
            results.append(
                ValidationResult(
                    level="MINOR",
                    category="deployment",
                    message=f"README.md Troubleshooting section missing important topics: {', '.join(missing_topics)}",
                    file=str(readme_path),
                    suggestion=(
                        "Document common issues: hook path not found after update, "
                        "old version after update, restart required after install/update"
                    ),
                )
            )

    return results


def validate_git_submodules(
    marketplace_dir: Path,
    plugins: list[dict[str, Any]],
) -> list[ValidationResult]:
    """
    Validate that all plugins are git submodules.

    For GitHub marketplace deployment, all plugins should be developed as git
    submodules of the main marketplace repository. This enables:
    - Independent version control for each plugin
    - Proper versioning and tagging
    - Clean separation of concerns

    Args:
        marketplace_dir: Path to marketplace directory
        plugins: List of plugin entries from marketplace.json

    Returns:
        List of validation results
    """
    results: list[ValidationResult] = []

    # Check if this is a git repository
    git_dir = marketplace_dir / ".git"
    if not git_dir.exists():
        results.append(
            ValidationResult(
                level="INFO",
                category="submodule",
                message="Marketplace is not a git repository, skipping submodule validation",
                file=str(marketplace_dir),
            )
        )
        return results

    # Check if .gitmodules file exists
    gitmodules_path = marketplace_dir / ".gitmodules"
    if not gitmodules_path.exists():
        # Check if all plugins use URL-based git sources (no submodules needed)
        all_url_based = True
        has_local_dirs = False
        for plugin in plugins:
            plugin_name = plugin.get("name", "")
            source = plugin.get("source", {})
            is_url_source = isinstance(source, dict) and source.get("source") in ("github", "url")
            if not is_url_source:
                all_url_based = False
            plugin_path = marketplace_dir / plugin_name
            if plugin_path.exists() and plugin_path.is_dir():
                has_local_dirs = True

        if all_url_based:
            # All plugins use URL-based git sources, submodules are not needed
            results.append(
                ValidationResult(
                    level="INFO",
                    category="submodule",
                    message="All plugins use URL-based git sources, no submodules required",
                    file=str(marketplace_dir),
                )
            )
        elif has_local_dirs:
            # Some plugins have local directories but no .gitmodules - likely misconfigured
            results.append(
                ValidationResult(
                    level="MAJOR",
                    category="submodule",
                    message="Missing .gitmodules file - local plugin directories exist but are not git submodules",
                    file=str(marketplace_dir),
                    suggestion=(
                        "Either convert local directories to git submodules with "
                        "'git submodule add <repo-url> <plugin-name>', "
                        "or switch all plugins to URL-based sources in marketplace.json"
                    ),
                )
            )
        return results

    # Parse .gitmodules file
    gitmodules_config = configparser.ConfigParser()
    try:
        gitmodules_config.read(str(gitmodules_path))
    except Exception as e:
        results.append(
            ValidationResult(
                level="MAJOR",
                category="submodule",
                message=f"Could not parse .gitmodules file: {e}",
                file=str(gitmodules_path),
            )
        )
        return results

    # Build a map of submodule paths to URLs
    submodules: dict[str, str] = {}
    for section in gitmodules_config.sections():
        if section.startswith('submodule "'):
            path = gitmodules_config.get(section, "path", fallback=None)
            url = gitmodules_config.get(section, "url", fallback=None)
            if path and url:
                submodules[path] = url

    # Check each plugin
    for plugin in plugins:
        plugin_name = plugin.get("name", "unknown")
        plugin_path = marketplace_dir / plugin_name
        source = plugin.get("source", {})

        # Get the expected repository URL from plugin source
        expected_repo: str | None = None
        if isinstance(source, dict):
            source_type = source.get("source")
            if source_type == "github":
                expected_repo = f"https://github.com/{source.get('repo', '')}"
            elif source_type == "url":
                expected_repo = source.get("url")
        elif isinstance(source, str) and (source.startswith("http") or source.startswith("git@")):
            expected_repo = source

        # Check if plugin directory exists
        if not plugin_path.exists():
            # Plugin is defined with git source but directory doesn't exist locally
            # This is acceptable for pure git-based marketplaces
            if expected_repo:
                results.append(
                    ValidationResult(
                        level="INFO",
                        category="submodule",
                        message=(
                            f"Plugin '{plugin_name}' has git source but no local directory (acceptable for remote-only)"
                        ),
                        file=str(plugin_path),
                    )
                )
            continue

        # Check if plugin is a submodule
        if plugin_name not in submodules and plugin_name not in [p.split("/")[-1] for p in submodules]:
            # Check if it's in a subdirectory
            found = False
            for submod_path in submodules:
                if submod_path.endswith(f"/{plugin_name}") or submod_path == plugin_name:
                    found = True
                    break

            if not found:
                results.append(
                    ValidationResult(
                        level="MAJOR",
                        category="submodule",
                        message=f"Plugin '{plugin_name}' directory exists but is not a git submodule",
                        file=str(plugin_path),
                        suggestion=(
                            f"Convert to submodule: 'git rm -r {plugin_name} && "
                            f"git submodule add <repo-url> {plugin_name}'"
                        ),
                    )
                )
                continue

        # Verify submodule URL matches plugin source
        submod_url = submodules.get(plugin_name)
        if submod_url and expected_repo:
            # Normalize URLs for comparison (remove .git suffix, normalize case)
            norm_submod = submod_url.rstrip("/").removesuffix(".git").lower()
            norm_expected = expected_repo.rstrip("/").removesuffix(".git").lower()

            if norm_submod != norm_expected:
                results.append(
                    ValidationResult(
                        level="MINOR",
                        category="submodule",
                        message=f"Plugin '{plugin_name}' submodule URL differs from source repository",
                        file=str(gitmodules_path),
                        suggestion=f"Submodule: {submod_url}, Source: {expected_repo}",
                    )
                )

        # Check submodule is initialized (has content)
        submod_git = plugin_path / ".git"
        if not submod_git.exists():
            # For submodules, .git is a file pointing to the git directory
            # Check if it's an uninitialized submodule
            try:
                result = subprocess.run(
                    ["git", "submodule", "status", plugin_name],
                    cwd=str(marketplace_dir),
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.stdout.startswith("-"):
                    results.append(
                        ValidationResult(
                            level="MINOR",
                            category="submodule",
                            message=f"Plugin '{plugin_name}' submodule is not initialized",
                            file=str(plugin_path),
                            suggestion="Run 'git submodule update --init --recursive' to initialize",
                        )
                    )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass  # Git command failed, skip this check

    # Info message if all checks passed
    if not any(r.level in ("CRITICAL", "MAJOR") for r in results):
        submod_count = len([p for p in plugins if p.get("name") in submodules])
        if submod_count > 0:
            results.append(
                ValidationResult(
                    level="INFO",
                    category="submodule",
                    message=f"Found {submod_count} plugin(s) configured as git submodules",
                    file=str(gitmodules_path),
                )
            )

    return results


def validate_marketplace_private_info(
    marketplace_dir: Path,
    plugins: list[dict[str, Any]],
) -> list[ValidationResult]:
    """
    Scan marketplace and all plugin subfolders for private information.

    Checks for:
    - Current user's home path (CRITICAL) - auto-detected from system
    - Generic home directory paths (MAJOR) - e.g., /Users/anyname/
    - Hardcoded absolute paths (MAJOR)

    This prevents accidental leaking of private home folder paths when
    publishing the marketplace to GitHub.

    Args:
        marketplace_dir: Path to marketplace directory
        plugins: List of plugin entries from marketplace.json

    Returns:
        List of validation results
    """
    results: list[ValidationResult] = []

    # Import the shared scanning functions
    try:
        from cpv_validation_common import (
            ABSOLUTE_PATH_PATTERNS,
            ALLOWED_DOC_PATH_PREFIXES,
            EXAMPLE_USERNAMES,
            PRIVATE_INFO_SKIP_DIRS,
            PRIVATE_USERNAMES,
            SCANNABLE_EXTENSIONS,
            build_private_path_patterns,
        )
    except ImportError:
        # Fallback if cpv_validation_common is not available
        results.append(
            ValidationResult(
                level="INFO",
                category="private-info",
                message="Could not import cpv_validation_common, skipping private info scan",
                file=str(marketplace_dir),
            )
        )
        return results

    # Build patterns for private usernames
    private_patterns = build_private_path_patterns(PRIVATE_USERNAMES)
    # Store in local scope for nested function
    example_usernames = EXAMPLE_USERNAMES
    absolute_patterns = ABSOLUTE_PATH_PATTERNS
    allowed_prefixes = ALLOWED_DOC_PATH_PREFIXES

    def scan_file(filepath: Path, rel_path: str) -> None:
        """Scan a single file for private info and absolute paths."""
        try:
            content = filepath.read_text(errors="ignore")
        except Exception:
            return

        # Check for private username patterns (CRITICAL)
        for pattern, desc in private_patterns:
            for match in pattern.finditer(content):
                matched_text = match.group(0)
                line_num = content[: match.start()].count("\n") + 1
                results.append(
                    ValidationResult(
                        level="CRITICAL",
                        category="private-info",
                        message=f"Private path leaked: {desc} - '{matched_text}' "
                        "(use relative path or ${CLAUDE_PLUGIN_ROOT})",
                        file=rel_path,
                        line=line_num,
                    )
                )

        # Check for ANY absolute paths (MAJOR) - stricter check
        for pattern, desc in absolute_patterns:
            for match in pattern.finditer(content):
                matched_text = match.group(1) if match.lastindex else match.group(0)

                # Skip if this looks like a regex pattern
                if any(c in matched_text for c in r"[]\^$.*+?{}|()"):
                    continue

                # Skip allowed documentation paths
                if any(matched_text.startswith(prefix) for prefix in allowed_prefixes):
                    continue

                # Skip environment variable references
                if "${" in matched_text or matched_text.startswith("$"):
                    continue

                # Extract username if it's a home path
                username_match = re.search(r"/(?:Users|home)/([^/\s]+)/", matched_text)
                if username_match:
                    extracted_username = username_match.group(1).lower()
                    # Skip example usernames in documentation
                    if extracted_username in example_usernames:
                        continue

                line_num = content[: match.start()].count("\n") + 1
                results.append(
                    ValidationResult(
                        level="MAJOR",
                        category="private-info",
                        message=f"Absolute path found: '{matched_text[:60]}...' "
                        "(use relative path, ${CLAUDE_PLUGIN_ROOT}, or ${HOME})",
                        file=rel_path,
                        line=line_num,
                    )
                )

    def scan_directory(root_dir: Path, base_rel: str = "") -> int:
        """Recursively scan a directory for private info."""
        files_scanned = 0
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Skip excluded directories
            dirnames[:] = [d for d in dirnames if d not in PRIVATE_INFO_SKIP_DIRS]

            for filename in filenames:
                filepath = Path(dirpath) / filename
                if filepath.suffix.lower() not in SCANNABLE_EXTENSIONS:
                    continue

                rel_dir = Path(dirpath).relative_to(root_dir)
                rel_path = f"{base_rel}/{rel_dir}/{filename}" if base_rel else f"{rel_dir}/{filename}"
                rel_path = rel_path.replace("./", "").lstrip("/")

                scan_file(filepath, rel_path)
                files_scanned += 1
        return files_scanned

    total_files = 0

    # Scan marketplace infrastructure dirs only (NOT the full root).
    # Plugin subdirs are scanned individually below.
    # Using scan_directory on the full marketplace_dir would recurse into
    # the entire workspace (166K+ files) when the marketplace is at repo root.
    MARKETPLACE_INFRA_DIRS = {".claude-plugin", ".github", "scripts"}
    for infra_dir_name in MARKETPLACE_INFRA_DIRS:
        infra_dir = marketplace_dir / infra_dir_name
        if infra_dir.is_dir():
            total_files += scan_directory(infra_dir, infra_dir_name)
    # Also scan known marketplace root files (README, LICENSE, CHANGELOG)
    MARKETPLACE_ROOT_FILES = {"README.md", "LICENSE", "CHANGELOG.md"}
    for root_file_name in MARKETPLACE_ROOT_FILES:
        root_file = marketplace_dir / root_file_name
        if root_file.is_file() and root_file.suffix.lower() in SCANNABLE_EXTENSIONS:
            scan_file(root_file, root_file_name)
            total_files += 1

    # Scan each plugin subfolder
    for plugin in plugins:
        source = plugin.get("source")
        plugin_name = plugin.get("name", "unknown")

        # Determine plugin path
        plugin_path: Path | None = None
        if isinstance(source, str) and source.startswith("./"):
            plugin_path = marketplace_dir / source[2:]
        elif isinstance(source, str) and not source.startswith(("http", "git@")):
            plugin_path = marketplace_dir / source

        if plugin_path and plugin_path.exists() and plugin_path.is_dir():
            total_files += scan_directory(plugin_path, plugin_name)

    # Summary
    critical_count = sum(1 for r in results if r.level == "CRITICAL")
    major_count = sum(1 for r in results if r.level == "MAJOR")

    if critical_count == 0 and major_count == 0:
        results.append(
            ValidationResult(
                level="INFO",
                category="private-info",
                message=f"No private info found in marketplace ({total_files} files scanned)",
                file=str(marketplace_dir),
            )
        )

    return results


def validate_github_source_required(
    plugins: list[dict[str, Any]],
    json_path: str,
) -> list[ValidationResult]:
    """
    Validate that plugins have GitHub repository URLs for publishing.

    For a marketplace to be publishable to GitHub and installable by users,
    each plugin should have a 'repository' field pointing to its GitHub repo.
    The 'source' field can be a local relative path (for submodules) but
    'repository' should always be the canonical GitHub URL.

    Args:
        plugins: List of plugin entries from marketplace.json
        json_path: Path to marketplace.json for error messages

    Returns:
        List of validation results
    """
    results: list[ValidationResult] = []

    for plugin in plugins:
        plugin_name = plugin.get("name", "unknown")
        repository = plugin.get("repository")
        source = plugin.get("source")

        # Check if repository field exists
        if not repository:
            results.append(
                ValidationResult(
                    level="MAJOR",
                    category="github-source",
                    message=f"Plugin '{plugin_name}' missing 'repository' field - "
                    "required for GitHub marketplace publishing",
                    file=json_path,
                    suggestion=f'Add: "repository": "https://github.com/OWNER/{plugin_name}"',
                )
            )
            continue

        # Check repository is a valid GitHub URL
        if not isinstance(repository, str):
            results.append(
                ValidationResult(
                    level="MAJOR",
                    category="github-source",
                    message=f"Plugin '{plugin_name}' repository must be a string URL",
                    file=json_path,
                )
            )
            continue

        # Validate it looks like a GitHub URL
        if not (
            repository.startswith("https://github.com/")
            or repository.startswith("git@github.com:")
            or "/" in repository
        ):  # Allow shorthand owner/repo
            results.append(
                ValidationResult(
                    level="MINOR",
                    category="github-source",
                    message=f"Plugin '{plugin_name}' repository doesn't look like a GitHub URL: {repository}",
                    file=json_path,
                    suggestion="Use format: https://github.com/OWNER/REPO",
                )
            )

        # Warn if source is NOT a relative path (local submodule)
        # For published marketplaces using submodules, source should be ./plugin-name
        if isinstance(source, str) and not source.startswith("./"):
            if source.startswith(("http", "git@")):
                # Remote source - this is OK but submodule is preferred
                results.append(
                    ValidationResult(
                        level="INFO",
                        category="github-source",
                        message=f"Plugin '{plugin_name}' uses remote source instead of local submodule",
                        file=json_path,
                        suggestion="Consider using git submodules with source: './{plugin_name}'",
                    )
                )

    if not any(r.level in ("CRITICAL", "MAJOR") for r in results):
        results.append(
            ValidationResult(
                level="INFO",
                category="github-source",
                message=f"All {len(plugins)} plugins have valid repository URLs",
                file=json_path,
            )
        )

    return results


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


def validate_workflow_inline_python(
    marketplace_dir: Path,
) -> list[ValidationResult]:
    """
    Scan GitHub Actions workflow files for dangerous inline Python patterns.

    When a YAML workflow uses `python3 -c "..."` (double-quoted shell string),
    dict bracket access like source["repo"] inside f-strings will fail at
    runtime because the shell strips the inner double quotes before Python
    sees the code. Python then interprets the bare word as an undefined
    variable name, causing NameError.

    This validator catches that pattern and reports it as a major issue.

    Args:
        marketplace_dir: Path to marketplace (or plugin) directory

    Returns:
        List of validation results
    """
    results: list[ValidationResult] = []

    # Find all YAML workflow files
    workflows_dir = marketplace_dir / ".github" / "workflows"
    if not workflows_dir.is_dir():
        return results

    yaml_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    if not yaml_files:
        return results

    for yaml_path in yaml_files:
        try:
            content = yaml_path.read_text(encoding="utf-8")
        except Exception:
            continue

        rel_path = str(yaml_path.relative_to(marketplace_dir))

        # Find all inline Python blocks
        for match in _YAML_INLINE_PYTHON_RE.finditer(content):
            python_code = match.group(1)
            block_start_offset = match.start()

            # Search for f-strings with dict bracket access
            for bad_match in _FSTRING_DICT_BRACKET_RE.finditer(python_code):
                # Calculate line number in the YAML file
                abs_offset = block_start_offset + bad_match.start()
                line_num = content[:abs_offset].count("\n") + 1
                snippet = bad_match.group(0)

                results.append(
                    ValidationResult(
                        level="MAJOR",
                        category="workflow",
                        message=(
                            f"Inline Python uses dict bracket access in f-string: {snippet} "
                            "-- shell quoting will strip inner quotes causing NameError at runtime"
                        ),
                        file=rel_path,
                        line=line_num,
                        suggestion=(
                            "Extract dict value into a local variable before using it in an f-string. "
                            "Example: val = mydict.get('key', ''); print(f'value: {val}')"
                        ),
                    )
                )

    if not results:
        results.append(
            ValidationResult(
                level="INFO",
                category="workflow",
                message=f"No dangerous inline Python patterns found in {len(yaml_files)} workflow file(s)",
                file=str(workflows_dir),
            )
        )

    return results


def validate_marketplace(marketplace_path: Path) -> ValidationReport:
    """
    Validate a complete marketplace configuration.

    Args:
        marketplace_path: Path to marketplace directory or marketplace.json

    Returns:
        ValidationReport with all findings
    """
    report = ValidationReport(marketplace_path=marketplace_path)

    # Load and validate the marketplace.json file
    data, load_results = validate_marketplace_file(marketplace_path)
    report.results.extend(load_results)

    if data is None:
        return report

    json_path = data.get("_json_path", str(marketplace_path))
    marketplace_dir = Path(data.get("_marketplace_dir", marketplace_path))

    # Check required fields
    for field_name in REQUIRED_MARKETPLACE_FIELDS:
        if field_name not in data:
            report.add_marketplace_result(
                level="CRITICAL",
                category="manifest",
                message=f"Missing required field: {field_name}",
                file=json_path,
            )

    # Validate owner field structure
    owner = data.get("owner")
    if isinstance(owner, dict):
        if "name" not in owner:
            report.add_marketplace_result(
                level="MAJOR",
                category="marketplace",
                message="'owner' object missing required 'name' field",
                file=json_path,
            )
    elif owner is not None:
        report.add_marketplace_result(
            level="MAJOR",
            category="marketplace",
            message=f"'owner' must be an object with a 'name' field, got {type(owner).__name__}",
            file=json_path,
        )

    # Validate name
    name = data.get("name")
    if name is not None:
        report.marketplace_name = name if isinstance(name, str) else None
        report.results.extend(validate_marketplace_name(name, json_path))

    # Validate plugins
    plugins = data.get("plugins")
    if plugins is not None:
        plugin_names, plugin_results = validate_plugins_array(plugins, marketplace_dir, json_path)
        report.plugins_found = plugin_names
        report.results.extend(plugin_results)

        # Validate GitHub deployment structure
        if isinstance(plugins, list):
            deployment_results = validate_github_deployment(marketplace_dir, plugins)
            report.results.extend(deployment_results)

            # Validate git submodules
            submodule_results = validate_git_submodules(marketplace_dir, plugins)
            report.results.extend(submodule_results)

            # Validate GitHub repository URLs for publishing
            github_source_results = validate_github_source_required(plugins, json_path)
            report.results.extend(github_source_results)

            # Scan for private info leaks (usernames, home paths)
            private_info_results = validate_marketplace_private_info(marketplace_dir, plugins)
            report.results.extend(private_info_results)

            # Scan GitHub Actions workflows for dangerous inline Python patterns
            # (dict bracket access in f-strings inside shell-quoted python3 -c blocks)
            workflow_results = validate_workflow_inline_python(marketplace_dir)
            report.results.extend(workflow_results)

    # Validate optional fields
    if "description" in data and not isinstance(data["description"], str):
        report.add_marketplace_result(
            level="MINOR",
            category="manifest",
            message="description field must be a string",
            file=json_path,
        )

    if "version" in data:
        version = data["version"]
        if not isinstance(version, str):
            report.add_marketplace_result(
                level="MINOR",
                category="manifest",
                message="version field must be a string",
                file=json_path,
            )
        elif not SEMVER_PATTERN.match(version):
            report.add_marketplace_result(
                level="MINOR",
                category="manifest",
                message=f"Marketplace version '{version}' should follow semver format",
                file=json_path,
            )

    return report


# =============================================================================
# CLI Interface
# =============================================================================


def format_report(report: ValidationReport, verbose: bool = False) -> str:
    """Format the validation report for display."""
    lines: list[str] = []

    # Header
    lines.append("=" * 60)
    lines.append("Marketplace Validation Report")
    lines.append("=" * 60)
    lines.append(f"Path: {report.marketplace_path}")
    if report.marketplace_name:
        lines.append(f"Name: {report.marketplace_name}")
    lines.append(f"Plugins Found: {len(report.plugins_found)}")
    if report.plugins_found:
        lines.append(f"  - {', '.join(report.plugins_found)}")
    lines.append("")

    # Group results by level
    critical = [r for r in report.results if r.level == "CRITICAL"]
    major = [r for r in report.results if r.level == "MAJOR"]
    minor = [r for r in report.results if r.level == "MINOR"]
    info = [r for r in report.results if r.level == "INFO"]

    # Summary
    lines.append(f"Critical Issues: {len(critical)}")
    lines.append(f"Major Issues: {len(major)}")
    lines.append(f"Minor Issues: {len(minor)}")
    if verbose:
        lines.append(f"Info: {len(info)}")
    lines.append("")

    # Details
    def format_result(r: BaseValidationResult) -> list[str]:
        category = getattr(r, "category", "")
        category_str = f" [{category}]" if category else ""
        result_lines = [f"  [{r.level}]{category_str} {r.message}"]
        file_val = getattr(r, "file", None) or getattr(r, "file_path", None)
        line_val = getattr(r, "line", None) or getattr(r, "line_number", None)
        if file_val:
            loc = str(file_val)
            if line_val:
                loc += f":{line_val}"
            result_lines.append(f"    Location: {loc}")
        suggestion = getattr(r, "suggestion", None)
        if suggestion:
            result_lines.append(f"    Suggestion: {suggestion}")
        return result_lines

    if critical:
        lines.append("--- CRITICAL ISSUES ---")
        for r in critical:
            lines.extend(format_result(r))
        lines.append("")

    if major:
        lines.append("--- MAJOR ISSUES ---")
        for r in major:
            lines.extend(format_result(r))
        lines.append("")

    if minor:
        lines.append("--- MINOR ISSUES ---")
        for r in minor:
            lines.extend(format_result(r))
        lines.append("")

    if verbose and info:
        lines.append("--- INFO ---")
        for r in info:
            lines.extend(format_result(r))
        lines.append("")

    # Final status
    lines.append("=" * 60)
    if report.has_critical:
        lines.append("RESULT: FAILED (critical issues found)")
    elif report.has_major:
        lines.append("RESULT: FAILED (major issues found)")
    elif report.has_minor:
        lines.append("RESULT: PASSED with warnings")
    else:
        lines.append("RESULT: PASSED")
    lines.append("=" * 60)

    return "\n".join(lines)


def main() -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Validate Claude Code plugin marketplace configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exit codes:
  0 - All checks passed
  1 - Critical issues found
  2 - Major issues found
  3 - Minor issues only

Examples:
  %(prog)s ./my-marketplace
  %(prog)s ./my-marketplace/marketplace.json --verbose
  %(prog)s ./my-marketplace --json
        """,
    )
    parser.add_argument(
        "marketplace_path",
        type=Path,
        help="Path to marketplace directory or marketplace.json file",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show all issues including info level",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument("--strict", action="store_true", help="Strict mode — NIT issues also block validation")

    args = parser.parse_args()

    # Resolve to absolute path so relative_to() works correctly
    marketplace_path = args.marketplace_path.resolve()

    # Verify path exists and contains marketplace content
    if not marketplace_path.exists():
        print(f"Error: {marketplace_path} does not exist", file=sys.stderr)
        return 1
    if marketplace_path.is_dir() and not (marketplace_path / "marketplace.json").exists():
        print(
            f"Error: No marketplace.json found at {marketplace_path}\n"
            f"Expected a marketplace directory with marketplace.json.",
            file=sys.stderr,
        )
        return 1
    if marketplace_path.is_file() and marketplace_path.name != "marketplace.json":
        print(f"Error: {marketplace_path} is not a marketplace.json file", file=sys.stderr)
        return 1

    # Run validation
    report = validate_marketplace(marketplace_path)

    # Output results
    if args.json:
        output = {
            "marketplace_path": str(report.marketplace_path),
            "marketplace_name": report.marketplace_name,
            "plugins_found": report.plugins_found,
            "results": [
                {
                    "level": r.level,
                    "category": r.category,
                    "message": r.message,
                    "file_path": r.file_path,
                    "line_number": r.line_number,
                    "suggestion": r.suggestion,
                }
                for r in report.results
                if isinstance(r, MarketplaceValidationResult)
            ],
            "summary": {
                "critical": sum(1 for r in report.results if r.level == "CRITICAL"),
                "major": sum(1 for r in report.results if r.level == "MAJOR"),
                "minor": sum(1 for r in report.results if r.level == "MINOR"),
                "info": sum(1 for r in report.results if r.level == "INFO"),
            },
            "exit_code": report.exit_code_strict() if args.strict else report.exit_code,
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_report(report, args.verbose))

    return report.exit_code_strict() if args.strict else report.exit_code


if __name__ == "__main__":
    sys.exit(main())
