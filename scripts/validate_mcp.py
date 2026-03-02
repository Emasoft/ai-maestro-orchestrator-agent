#!/usr/bin/env python3
"""
MCP Server Configuration Validator

Validates MCP server configurations in Claude Code plugins.
Checks .mcp.json files and inline mcpServers definitions.

Based on:
- https://modelcontextprotocol.io/specification/2025-11-25/
- https://code.claude.com/docs/en/mcp.md
- https://code.claude.com/docs/en/plugins-reference.md

Usage:
    from validate_mcp import validate_mcp_config, validate_mcp_server
    report = validate_mcp_config(config_path, plugin_root)
    report = validate_mcp_server(server_name, server_config, plugin_root)

Exit codes (when run directly):
    0 - All checks passed
    1 - CRITICAL issues found
    2 - MAJOR issues found
    3 - MINOR issues found
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any

from cpv_validation_common import ValidationReport

# Valid transport types
VALID_TRANSPORTS = {"stdio", "sse", "http"}

# Known MCP server configuration fields
KNOWN_SERVER_FIELDS = {
    "command",  # Required for stdio servers
    "args",  # Command-line arguments
    "env",  # Environment variables
    "cwd",  # Working directory
    "type",  # Transport type: stdio, sse, http
    "url",  # Required for http/sse servers
    "headers",  # HTTP headers for authentication
    "timeout",  # Connection timeout
    "oauth",  # OAuth config object with clientId and callbackPort
}

# Environment variable pattern: ${VAR} or ${VAR:-default}
ENV_VAR_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")

# Plugin-specific environment variables
PLUGIN_ENV_VARS = {"CLAUDE_PLUGIN_ROOT", "CLAUDE_PROJECT_DIR"}

# Absolute path patterns (platform-independent)
ABSOLUTE_PATH_PATTERNS = [
    re.compile(r"^/[^$]"),  # Unix absolute path (not starting with ${)
    re.compile(r"^[A-Za-z]:\\"),  # Windows absolute path
]


def is_absolute_path(path: str) -> bool:
    """Check if a path appears to be an absolute path (without env var substitution)."""
    for pattern in ABSOLUTE_PATH_PATTERNS:
        if pattern.match(path):
            return True
    return False


def extract_env_vars(value: str) -> list[tuple[str, str | None]]:
    """Extract environment variable references from a string.

    Returns list of (var_name, default_value) tuples.
    """
    return ENV_VAR_PATTERN.findall(value)


def validate_env_var_syntax(value: str, report: ValidationReport, context: str) -> None:
    """Validate environment variable syntax in a string value."""
    # Check for malformed env var references
    if "${" in value:
        # Look for unclosed braces
        open_count = value.count("${")
        close_count = value.count("}")
        if open_count != close_count:
            report.major(f"Malformed env var syntax (unclosed braces) in {context}")
            return

        # Extract and validate each reference
        for match in ENV_VAR_PATTERN.finditer(value):
            var_name = match.group(1)
            default = match.group(2)

            # Warn about required env vars without defaults (excluding plugin vars)
            if default is None and var_name not in PLUGIN_ENV_VARS:
                report.info(f"Env var ${{{var_name}}} has no default value in {context} - config will fail if not set")


def validate_path_value(value: str, report: ValidationReport, context: str, plugin_root: Path | None = None) -> None:
    """Validate a path value in MCP configuration."""
    # Check for absolute paths (without env var substitution)
    if is_absolute_path(value):
        report.major(f"Absolute path found in {context}: {value} - use ${{{{CLAUDE_PLUGIN_ROOT}}}} for portability")
        return

    # Check if path uses CLAUDE_PLUGIN_ROOT for plugin-relative paths
    if plugin_root and not value.startswith("${") and not value.startswith("npx"):
        # Could be a relative path or command name
        # Check if it looks like a file path
        if "/" in value or "\\" in value:
            report.minor(f"Path in {context} should use ${{CLAUDE_PLUGIN_ROOT}}: {value}")

    # Validate env var syntax in path
    validate_env_var_syntax(value, report, context)

    # If plugin_root provided and path uses CLAUDE_PLUGIN_ROOT, verify the file exists
    if plugin_root and "${CLAUDE_PLUGIN_ROOT}" in value:
        # Substitute to check existence
        resolved = value.replace("${CLAUDE_PLUGIN_ROOT}", str(plugin_root))
        resolved_path = Path(resolved)
        # Only check if it looks like a file (has extension) not a dir
        if "." in resolved_path.name or resolved_path.suffix:
            if not resolved_path.exists():
                report.info(f"Referenced file may not exist: {value} (resolved: {resolved_path})")


def validate_mcp_server(
    server_name: str,
    config: dict[str, Any],
    report: ValidationReport,
    plugin_root: Path | None = None,
    file_context: str = "mcp-config",
) -> None:
    """Validate a single MCP server configuration.

    Args:
        server_name: Name of the server being validated
        config: Server configuration dictionary
        report: ValidationReport to add results to
        plugin_root: Optional path to plugin root for path resolution
        file_context: File context for error messages
    """
    ctx = f"{file_context}:{server_name}"

    # Check for unknown fields
    for key in config.keys():
        if key not in KNOWN_SERVER_FIELDS:
            report.warning(f"Unknown field '{key}' in server {server_name}")

    # Determine transport type
    transport = config.get("type", "stdio")
    if transport not in VALID_TRANSPORTS:
        report.major(f"Invalid transport type '{transport}' for server {server_name}")
        transport = "stdio"  # Assume stdio for further validation

    # Validate based on transport type
    if transport == "stdio":
        # stdio servers require 'command'
        if "command" not in config:
            report.critical(f"Server {server_name} missing required 'command' field")
        else:
            command = config["command"]
            validate_path_value(command, report, f"{ctx}:command", plugin_root)

            # Check if command is executable (if resolvable)
            if plugin_root and "${CLAUDE_PLUGIN_ROOT}" in command:
                resolved = command.replace("${CLAUDE_PLUGIN_ROOT}", str(plugin_root))
                resolved_path = Path(resolved)
                if resolved_path.exists():
                    if not os.access(resolved_path, os.X_OK):
                        report.major(f"Server {server_name} command not executable: {resolved}")
                    else:
                        report.passed(f"Server {server_name} command is executable")
            elif shutil.which(command):
                report.passed(f"Server {server_name} command '{command}' found in PATH")
            else:
                report.info(f"Server {server_name} command '{command}' not found (may be resolved at runtime)")

            # Security warning for package executors running remote packages
            package_executors = {"npx", "bunx", "uvx", "pipx", "pnpx"}
            if command in package_executors:
                # Check args to see if it's running a non-local package
                cmd_args = config.get("args", [])
                pkg_name = cmd_args[0] if cmd_args and isinstance(cmd_args[0], str) else None
                if pkg_name and not pkg_name.startswith((".", "/", "${")):
                    report.warning(
                        f"Server {server_name} uses {command} to execute remote package "
                        f"'{pkg_name}' — this downloads and runs code from a registry. "
                        f"Verify the package is trusted and consider pinning a version."
                    )

        # Warn about url field ignored for stdio transport
        if "url" in config and transport == "stdio":
            report.info(f"Server {server_name} has 'url' but transport is stdio - url will be ignored")

    elif transport in ("http", "sse"):
        # HTTP/SSE servers require 'url'
        if "url" not in config:
            report.critical(f"Server {server_name} (type={transport}) missing 'url'")
        else:
            url = config["url"]
            validate_env_var_syntax(url, report, f"{ctx}:url")

            # Basic URL validation
            if not url.startswith("${") and not url.startswith(("http://", "https://")):
                report.major(f"Server {server_name} url should be http(s):// : {url}")

            # Security warning for remote MCP servers
            if not url.startswith("${"):
                is_localhost = any(
                    url.startswith(prefix)
                    for prefix in (
                        "http://localhost",
                        "https://localhost",
                        "http://127.0.0.1",
                        "https://127.0.0.1",
                        "http://[::1]",
                        "https://[::1]",
                        "http://0.0.0.0",
                        "https://0.0.0.0",
                    )
                )
                if not is_localhost:
                    report.warning(
                        f"Server {server_name} connects to remote URL '{url}' — "
                        f"remote MCP servers can access tool results and conversation data. "
                        f"Ensure the server is trusted and uses HTTPS."
                    )
                    if url.startswith("http://") and not is_localhost:
                        report.major(
                            f"Server {server_name} uses unencrypted HTTP for remote server — "
                            f"use HTTPS to protect data in transit."
                        )

        # SSE is deprecated
        if transport == "sse":
            report.minor(f"Server {server_name} uses deprecated 'sse' transport - consider migrating to 'http'")

        # Warn if command is set for http/sse
        if "command" in config:
            report.info(f"Server {server_name} has 'command' but transport is {transport} - command will be ignored")

    # Validate args array
    if "args" in config:
        args = config["args"]
        if not isinstance(args, list):
            report.major(f"Server {server_name} 'args' must be an array")
        else:
            for i, arg in enumerate(args):
                if not isinstance(arg, str):
                    report.major(f"Server {server_name} args[{i}] must be a string")
                else:
                    validate_env_var_syntax(arg, report, f"{ctx}:args[{i}]")
                    # Check for paths in args
                    if "/" in arg or "\\" in arg:
                        validate_path_value(arg, report, f"{ctx}:args[{i}]", plugin_root)

    # Validate env object
    if "env" in config:
        env = config["env"]
        if not isinstance(env, dict):
            report.major(f"Server {server_name} 'env' must be an object")
        else:
            for key, value in env.items():
                if not isinstance(key, str):
                    report.major(f"Server {server_name} env key must be a string")
                if not isinstance(value, str):
                    report.major(f"Server {server_name} env[{key}] must be a string")
                else:
                    validate_env_var_syntax(value, report, f"{ctx}:env[{key}]")

    # Validate cwd
    if "cwd" in config:
        cwd = config["cwd"]
        if not isinstance(cwd, str):
            report.major(f"Server {server_name} 'cwd' must be a string")
        else:
            validate_path_value(cwd, report, f"{ctx}:cwd", plugin_root)

    # Validate headers (for http transport)
    if "headers" in config:
        headers = config["headers"]
        if not isinstance(headers, dict):
            report.major(f"Server {server_name} 'headers' must be an object")
        else:
            for key, value in headers.items():
                if not isinstance(value, str):
                    report.major(f"Server {server_name} headers[{key}] must be a string")
                else:
                    validate_env_var_syntax(value, report, f"{ctx}:headers[{key}]")

                    # Warn about hardcoded credentials
                    if key.lower() in ("authorization", "x-api-key", "api-key"):
                        if "${" not in value:
                            report.major(
                                f"Server {server_name} has hardcoded credential in "
                                f"headers[{key}] - use environment variables"
                            )

    # Validate timeout field
    if "timeout" in config:
        timeout = config["timeout"]
        if not isinstance(timeout, (int, float)):
            report.major(f"Server {server_name} 'timeout' must be a number, got {type(timeout).__name__}")
        elif timeout <= 0:
            report.major(f"Server {server_name} 'timeout' must be positive")
        else:
            report.passed(f"Server {server_name} timeout: {timeout}")

    # Validate oauth field structure
    if "oauth" in config:
        oauth = config["oauth"]
        if not isinstance(oauth, dict):
            report.major(f"Server {server_name} 'oauth' must be an object, got {type(oauth).__name__}")
        else:
            # clientId is the key field for OAuth
            if "clientId" in oauth and not isinstance(oauth["clientId"], str):
                report.major(f"Server {server_name} 'oauth.clientId' must be a string")
            if "callbackPort" in oauth and not isinstance(oauth["callbackPort"], int):
                report.major(f"Server {server_name} 'oauth.callbackPort' must be an integer")
            report.passed(f"Server {server_name} has OAuth configuration")

    report.passed(f"Server {server_name} configuration validated")


def validate_mcp_config(
    config_path: Path,
    plugin_root: Path | None = None,
    report: ValidationReport | None = None,
) -> ValidationReport:
    """Validate an MCP configuration file (.mcp.json).

    Args:
        config_path: Path to the .mcp.json file
        plugin_root: Optional path to plugin root for path resolution
        report: Optional existing report to add to

    Returns:
        ValidationReport with all validation results
    """
    if report is None:
        report = ValidationReport()

    rel_path = config_path.name
    if plugin_root:
        try:
            rel_path = str(config_path.relative_to(plugin_root))
        except ValueError:
            pass

    if not config_path.exists():
        report.info(f"MCP config file not found: {rel_path}")
        return report

    # Parse JSON
    try:
        config = json.loads(config_path.read_text())
    except json.JSONDecodeError as e:
        report.critical(f"Invalid JSON in {rel_path}: {e}")
        return report

    report.passed(f"{rel_path} is valid JSON")

    # Check for mcpServers field
    if "mcpServers" not in config:
        report.info(f"No 'mcpServers' field in {rel_path}")
        return report

    servers = config["mcpServers"]

    if not isinstance(servers, dict):
        report.critical(f"'mcpServers' must be an object in {rel_path}")
        return report

    if not servers:
        report.info(f"No MCP servers defined in {rel_path}")
        return report

    report.info(f"Found {len(servers)} MCP server(s) in {rel_path}")

    # Validate each server
    server_names = set()
    for server_name, server_config in servers.items():
        # Check for duplicate names
        if server_name in server_names:
            report.major(f"Duplicate server name: {server_name}")
        server_names.add(server_name)

        # Validate server name format
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", server_name):
            report.minor(f"Server name '{server_name}' should be alphanumeric with hyphens/underscores")

        if not isinstance(server_config, dict):
            report.critical(f"Server '{server_name}' config must be an object")
            continue

        validate_mcp_server(server_name, server_config, report, plugin_root, rel_path)

    return report


def validate_plugin_mcp(plugin_root: Path, report: ValidationReport | None = None) -> ValidationReport:
    """Validate all MCP configurations in a plugin.

    Checks both .mcp.json and inline mcpServers in plugin.json.

    Args:
        plugin_root: Path to the plugin root directory
        report: Optional existing report to add to

    Returns:
        ValidationReport with all validation results
    """
    if report is None:
        report = ValidationReport()

    # Check for .mcp.json
    mcp_json = plugin_root / ".mcp.json"
    if mcp_json.exists():
        validate_mcp_config(mcp_json, plugin_root, report)

    # Check for inline mcpServers in plugin.json
    plugin_json = plugin_root / ".claude-plugin" / "plugin.json"
    if plugin_json.exists():
        try:
            manifest = json.loads(plugin_json.read_text())
            if "mcpServers" in manifest:
                mcp_servers = manifest["mcpServers"]

                # Could be a path reference or inline object
                if isinstance(mcp_servers, str):
                    # Path to external config
                    if mcp_servers.startswith("./"):
                        external_path = plugin_root / mcp_servers[2:]
                    else:
                        external_path = plugin_root / mcp_servers

                    if external_path.exists():
                        validate_mcp_config(external_path, plugin_root, report)
                    else:
                        report.major(
                            f"Referenced MCP config not found: {mcp_servers}",
                            ".claude-plugin/plugin.json",
                        )

                elif isinstance(mcp_servers, dict):
                    # Inline definition
                    report.info(f"Found inline mcpServers in plugin.json ({len(mcp_servers)} server(s))")
                    for server_name, server_config in mcp_servers.items():
                        if isinstance(server_config, dict):
                            validate_mcp_server(
                                server_name,
                                server_config,
                                report,
                                plugin_root,
                                "plugin.json:mcpServers",
                            )
                        else:
                            report.critical(
                                f"Server '{server_name}' config must be an object",
                                ".claude-plugin/plugin.json",
                            )
                else:
                    report.major(
                        "mcpServers must be a string (path) or object",
                        ".claude-plugin/plugin.json",
                    )

        except json.JSONDecodeError:
            # plugin.json validation is handled elsewhere
            pass

    return report


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
    print("MCP Configuration Validation Report")
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
        print(f"{colors['PASSED']}✓ All MCP checks passed{colors['RESET']}")
    else:
        status_color = colors[["PASSED", "CRITICAL", "MAJOR", "MINOR", "NIT"][min(report.exit_code, 4)]]
        print(f"{status_color}✗ Issues found{colors['RESET']}")

    print()


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate MCP configuration")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all results")
    parser.add_argument("--strict", action="store_true", help="Strict mode — NIT issues also block validation")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "path",
        nargs="?",
        help="Path to .mcp.json file or plugin directory",
    )
    args = parser.parse_args()

    # Determine path — always resolve to absolute so relative_to() works
    if args.path:
        path = Path(args.path).resolve()
    else:
        path = Path.cwd().resolve()

    if not path.exists():
        print(f"Error: {path} does not exist", file=sys.stderr)
        return 1

    # Verify content type — must be .mcp.json file or directory containing one
    if path.is_file() and not path.name.endswith(".mcp.json"):
        print(f"Error: {path} is not an MCP config file (expected .mcp.json)", file=sys.stderr)
        return 1
    if path.is_dir():
        has_mcp = (path / ".mcp.json").exists() or (path / ".claude-plugin").is_dir()
        if not has_mcp:
            print(
                f"Error: No MCP configuration found at {path}\n"
                f"Expected .mcp.json file or a plugin directory with .claude-plugin/.",
                file=sys.stderr,
            )
            return 1

    # Determine if it's a file or directory
    if path.is_file():
        report = validate_mcp_config(path, path.parent)
    else:
        report = validate_plugin_mcp(path)

    # Output
    if args.json:
        output = {
            "exit_code": report.exit_code,
            "counts": {
                "critical": sum(1 for r in report.results if r.level == "CRITICAL"),
                "major": sum(1 for r in report.results if r.level == "MAJOR"),
                "minor": sum(1 for r in report.results if r.level == "MINOR"),
                "info": sum(1 for r in report.results if r.level == "INFO"),
                "passed": sum(1 for r in report.results if r.level == "PASSED"),
                "nit": sum(1 for r in report.results if r.level == "NIT"),
                "warning": sum(1 for r in report.results if r.level == "WARNING"),
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
    else:
        print_results(report, args.verbose)

    if args.strict:
        return report.exit_code_strict()
    return report.exit_code


if __name__ == "__main__":
    sys.exit(main())
