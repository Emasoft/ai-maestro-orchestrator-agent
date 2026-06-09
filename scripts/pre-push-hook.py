#!/usr/bin/env python3
"""pre-push-hook.py - Prevent pushing broken plugins to GitHub.

This hook runs validation before allowing git push.
If any CRITICAL issues are found, the push is blocked.

To install:
    cp scripts/pre-push-hook.py .git/hooks/pre-push
    chmod +x .git/hooks/pre-push

Exit codes:
    0 - All validations passed, push allowed
    1 - Validation failed, push blocked
"""

import codecs
import json
import re
import subprocess
import sys
from pathlib import Path

# ANSI Colors
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
BOLD = "\033[1m"
NC = "\033[0m"


def validate_json(file_path: Path) -> tuple[bool, str]:
    """Validate JSON file syntax."""
    try:
        with open(file_path, encoding="utf-8") as f:
            json.load(f)
        return True, ""
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except FileNotFoundError:
        return False, "File not found"


def validate_semver(version: str) -> bool:
    """Validate semver format."""
    pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$"
    return bool(re.match(pattern, version))


def validate_plugin_manifest(plugin_dir: Path) -> list[tuple[str, str]]:
    """Validate plugin manifest. Returns list of (severity, message) tuples."""
    issues: list[tuple[str, str]] = []
    plugin_json = plugin_dir / ".claude-plugin" / "plugin.json"

    if not plugin_json.exists():
        issues.append(("CRITICAL", "Missing .claude-plugin/plugin.json"))
        return issues

    valid, error = validate_json(plugin_json)
    if not valid:
        issues.append(("CRITICAL", f"Invalid plugin.json: {error}"))
        return issues

    with open(plugin_json, encoding="utf-8") as f:
        data = json.load(f)

    # Check required fields
    if not data.get("name"):
        issues.append(("CRITICAL", "Missing 'name' in plugin.json"))

    if not data.get("version"):
        issues.append(("CRITICAL", "Missing 'version' in plugin.json"))
    elif not validate_semver(data["version"]):
        issues.append(("MAJOR", f"Invalid semver '{data['version']}' in plugin.json"))

    if not data.get("description"):
        issues.append(("MAJOR", "Missing 'description' in plugin.json"))

    # Validate agents field if present
    agents = data.get("agents")
    if agents is not None:
        if not isinstance(agents, list):
            issues.append(("CRITICAL", "'agents' must be array in plugin.json"))
        else:
            for agent in agents:
                if not isinstance(agent, str):
                    issues.append(("CRITICAL", "Agent entry must be string path"))
                elif not agent.endswith(".md"):
                    issues.append(("MAJOR", f"Agent path should end with .md: {agent}"))
                else:
                    agent_path = plugin_dir / agent.lstrip("./")
                    if not agent_path.exists():
                        issues.append(("MAJOR", f"Agent file not found: {agent}"))

    return issues


def validate_hooks_config(plugin_dir: Path) -> list[tuple[str, str]]:
    """Validate hooks configuration."""
    issues: list[tuple[str, str]] = []
    hooks_json = plugin_dir / "hooks" / "hooks.json"

    if not hooks_json.exists():
        return issues  # Hooks are optional

    valid, error = validate_json(hooks_json)
    if not valid:
        issues.append(("CRITICAL", f"Invalid hooks.json: {error}"))
        return issues

    with open(hooks_json, encoding="utf-8") as f:
        data = json.load(f)

    hooks = data.get("hooks", {})
    valid_events = [
        "PreToolUse", "PostToolUse", "PostToolUseFailure",
        "Notification", "Stop", "SubagentStop", "SubagentStart",
        "UserPromptSubmit", "PermissionRequest",
        "SessionStart", "SessionEnd", "PreCompact", "Setup"
    ]

    for event_name, event_hooks in hooks.items():
        if event_name not in valid_events:
            issues.append(("MAJOR", f"Unknown hook event '{event_name}'"))

        if not isinstance(event_hooks, list):
            issues.append(("CRITICAL", f"Hook event '{event_name}' must be array"))
            continue

        for hook_entry in event_hooks:
            hook_list = hook_entry.get("hooks", [])
            for hook in hook_list:
                if hook.get("type") == "command":
                    cmd = hook.get("command", "")
                    if not cmd:
                        issues.append(("CRITICAL", f"Empty command in {event_name} hook"))
                    elif "${CLAUDE_PLUGIN_ROOT}" not in cmd and not cmd.startswith("/"):
                        issues.append(("MAJOR", f"Hook command should use ${{CLAUDE_PLUGIN_ROOT}}: {cmd}"))

    return issues


def lint_python_scripts(plugin_dir: Path) -> list[tuple[str, str]]:
    """Run ruff on Python scripts."""
    issues: list[tuple[str, str]] = []
    scripts_dir = plugin_dir / "scripts"

    if not scripts_dir.exists():
        return issues

    try:
        result = subprocess.run(
            ["ruff", "check", str(scripts_dir), "--select=E,F", "--quiet"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0 and result.stdout:
            # Count errors
            error_count = len(result.stdout.strip().split("\n"))
            if error_count > 0:
                issues.append(("MINOR", f"Python lint: {error_count} issues found"))
    except FileNotFoundError:
        pass  # ruff not installed
    except subprocess.TimeoutExpired:
        issues.append(("MINOR", "Python lint timed out"))

    return issues


def check_unicode_compliance(plugin_dir: Path) -> list[tuple[str, str]]:
    """Run Unicode compliance check on text files."""
    issues: list[tuple[str, str]] = []
    scripts_dir = plugin_dir / "scripts"
    skills_dir = plugin_dir / "skills"

    try:
        for check_dir in [scripts_dir, skills_dir]:
            if not check_dir.exists():
                continue
            for filepath in check_dir.rglob("*"):
                if not filepath.is_file():
                    continue
                if filepath.suffix not in (".py", ".md", ".json", ".yaml", ".yml", ".toml", ".sh"):
                    continue
                if any(p.startswith(".") or p == "__pycache__" for p in filepath.parts):
                    continue
                try:
                    raw = filepath.read_bytes()
                    if raw.startswith(codecs.BOM_UTF8) or raw.startswith((b"\xff\xfe", b"\xfe\xff")):
                        issues.append(("MAJOR", f"BOM detected in {filepath.relative_to(plugin_dir)}"))
                    if b"\r\n" in raw:
                        issues.append(("MINOR", f"CRLF line endings in {filepath.relative_to(plugin_dir)}"))
                except OSError:
                    pass
    except Exception:
        issues.append(("MINOR", "Unicode compliance check encountered an error"))

    return issues


def main() -> int:
    """Main pre-push validation."""
    # Get repo root
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True
    )
    repo_root = Path(result.stdout.strip())

    print(f"{BOLD}{'=' * 60}{NC}")
    print(f"{BOLD}Pre-Push Validation - Blocking broken plugins{NC}")
    print(f"{BOLD}{'=' * 60}{NC}")
    print()

    all_issues: list[tuple[str, str]] = []

    # 1. Validate plugin manifest
    print(f"{BLUE}Validating plugin manifest...{NC}")
    all_issues.extend(validate_plugin_manifest(repo_root))

    # 2. Validate hooks
    print(f"{BLUE}Validating hooks configuration...{NC}")
    all_issues.extend(validate_hooks_config(repo_root))

    # 3. Lint Python scripts
    print(f"{BLUE}Linting Python scripts...{NC}")
    all_issues.extend(lint_python_scripts(repo_root))

    # 4. Unicode compliance check
    print(f"{BLUE}Checking Unicode compliance...{NC}")
    all_issues.extend(check_unicode_compliance(repo_root))

    # Categorize issues
    critical = [msg for sev, msg in all_issues if sev == "CRITICAL"]
    major = [msg for sev, msg in all_issues if sev == "MAJOR"]
    minor = [msg for sev, msg in all_issues if sev == "MINOR"]

    # Report
    print()
    print(f"{BOLD}{'=' * 60}{NC}")
    print(f"{BOLD}Validation Results{NC}")
    print(f"{BOLD}{'=' * 60}{NC}")

    if critical:
        print(f"\n{RED}CRITICAL Issues (push blocked):{NC}")
        for msg in critical:
            print(f"  {RED}✘{NC} {msg}")

    if major:
        print(f"\n{YELLOW}MAJOR Issues (push blocked):{NC}")
        for msg in major:
            print(f"  {YELLOW}⚠{NC} {msg}")

    if minor:
        print(f"\n{BLUE}MINOR Issues (push blocked):{NC}")
        for msg in minor:
            print(f"  {BLUE}ℹ{NC} {msg}")

    print()
    print(f"Summary: {RED}{len(critical)} critical{NC}, {YELLOW}{len(major)} major{NC}, {BLUE}{len(minor)} minor{NC}")
    print()

    # Decision — strict mode: block on ALL issues including MINOR
    if critical or major or minor:
        print(f"{RED}{'=' * 60}{NC}")
        print(f"{RED}PUSH BLOCKED - Fix ALL issues (CRITICAL, MAJOR, and MINOR){NC}")
        print(f"{RED}{'=' * 60}{NC}")
        print()
        print("To bypass (NOT RECOMMENDED): git push --no-verify")
        return 1

    print(f"{GREEN}{'=' * 60}{NC}")
    print(f"{GREEN}VALIDATION PASSED - Push allowed{NC}")
    print(f"{GREEN}{'=' * 60}{NC}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
