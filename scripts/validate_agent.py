#!/usr/bin/env python3
"""
Claude Plugins Validation - Agent Validator

Validates individual agent markdown files according to Claude Code agent spec.
Based on: https://code.claude.com/docs/en/agents.md

Usage:
    uv run python scripts/validate_agent.py path/to/agent.md
    uv run python scripts/validate_agent.py path/to/agents/  # validate all agents in dir
    uv run python scripts/validate_agent.py path/to/agent.md --verbose
    uv run python scripts/validate_agent.py path/to/agent.md --json

Exit codes:
    0 - All checks passed
    1 - CRITICAL issues found (agent will not work)
    2 - MAJOR issues found (significant problems)
    3 - MINOR issues found (may affect UX)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from cpv_validation_common import (
    COLORS,
    MAX_BODY_WORDS,
    MAX_DESCRIPTION_LENGTH,
    MAX_NAME_LENGTH,
    MIN_BODY_CHARS,
    NAME_PATTERN,
    SECRET_PATTERNS,
    USER_PATH_PATTERNS,
    VALID_CONTEXT_VALUES,
    VALID_MODELS,
    VALID_TOOLS,
    ValidationReport,
    check_utf8_encoding,
)

# Known frontmatter fields per official docs (agent-specific)
# Based on: https://code.claude.com/docs/en/sub-agents.md
KNOWN_FRONTMATTER_FIELDS = {
    # Required fields
    "name",
    "description",
    # Optional fields
    "tools",
    "disallowedTools",
    "model",
    "permissionMode",
    "skills",
    "hooks",
    "color",
    "capabilities",
    "maxTurns",
    "mcpServers",
    "memory",
    "background",
    "isolation",
    # Claude Code-specific fields (legacy/extended)
    "context",
    "agent",
    "user-invocable",
    "system-prompt",
}

# Valid values for the 'permissionMode' field
VALID_PERMISSION_MODES = {
    "default",  # Standard permission checking with prompts
    "acceptEdits",  # Auto-accept file edits
    "dontAsk",  # Auto-deny permission prompts (explicitly allowed tools still work)
    "bypassPermissions",  # Skip all permission checks (use with caution!)
    "plan",  # Plan mode (read-only exploration)
}

# Built-in agent types per official docs — custom agent names are also valid
VALID_AGENT_VALUES = {"Explore", "Plan", "general-purpose"}

# Valid values for the 'memory' field (persistent memory scope)
VALID_MEMORY_SCOPES = {"user", "project", "local"}

# Valid values for the 'isolation' field
VALID_ISOLATION_VALUES = {"worktree"}

# Minimum required example blocks for agent documentation
MIN_EXAMPLE_BLOCKS = 2

# Placeholder text patterns that indicate incomplete system prompts
PLACEHOLDER_PATTERNS = [
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\bPLACEHOLDER\b", re.IGNORECASE),
    re.compile(r"\bFIXME\b", re.IGNORECASE),
    re.compile(r"\bXXX\b"),
    re.compile(r"\[.*INSERT.*\]", re.IGNORECASE),
    re.compile(r"\[.*FILL.*\]", re.IGNORECASE),
]


@dataclass
class AgentValidationReport(ValidationReport):
    """Validation report for an agent file, extends base ValidationReport with agent_path."""

    agent_path: str = ""

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary for JSON serialization."""
        base = super().to_dict()
        base["agent_path"] = self.agent_path
        return base


def parse_frontmatter(content: str) -> tuple[dict[str, Any] | None, str, int]:
    """Parse YAML frontmatter from agent content.

    Returns:
        Tuple of (frontmatter_dict, body_content, frontmatter_end_line)
        Returns (None, content, 0) if no frontmatter found
    """
    if not content.startswith("---"):
        return None, content, 0

    # Find closing ---
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, content, 0

    try:
        frontmatter = yaml.safe_load(parts[1])
        if frontmatter is None:
            frontmatter = {}
        body = parts[2]
        # Count lines to find frontmatter end
        fm_end_line = parts[0].count("\n") + parts[1].count("\n") + 2
        return frontmatter, body, fm_end_line
    except yaml.YAMLError:
        return None, content, 0


def validate_frontmatter_exists(content: str, report: AgentValidationReport, filename: str) -> dict[str, Any] | None:
    """Validate YAML frontmatter exists and is valid."""
    if not content.startswith("---"):
        report.critical("No YAML frontmatter found (required)", filename)
        return None

    frontmatter, *_ = parse_frontmatter(content)

    if frontmatter is None and content.startswith("---"):
        report.critical(
            "Malformed YAML frontmatter (missing closing --- or invalid YAML)",
            filename,
        )
        return None

    if frontmatter is None:
        return None

    report.passed("Valid YAML frontmatter", filename)

    # Check for unknown fields
    for key in frontmatter.keys():
        if key not in KNOWN_FRONTMATTER_FIELDS:
            report.warning(
                f"Unknown frontmatter field '{key}' (may be ignored by CLI)",
                filename,
            )

    return frontmatter


def validate_name_field(frontmatter: dict[str, Any], filename: str, report: AgentValidationReport) -> None:
    """Validate the 'name' frontmatter field."""
    if "name" not in frontmatter:
        # Use filename as fallback name
        expected_name = Path(filename).stem
        report.info(
            f"No 'name' field (will use filename: {expected_name})",
            filename,
        )
        name = expected_name
    else:
        name = frontmatter["name"]
        report.passed(f"'name' field present: {name}", filename)

    if not isinstance(name, str):
        report.critical(f"'name' must be a string, got {type(name).__name__}", filename)
        return

    # Length check
    if len(name) > MAX_NAME_LENGTH:
        report.major(
            f"Name exceeds {MAX_NAME_LENGTH} chars ({len(name)} chars): {name}",
            filename,
        )

    # Lowercase check
    if name != name.lower():
        report.major(f"Name must be lowercase: {name}", filename)

    # Kebab-case pattern check
    if not NAME_PATTERN.match(name):
        report.major(
            f"Name must be kebab-case (lowercase letters, numbers, hyphens): {name}",
            filename,
        )

    # Consecutive hyphens check
    if "--" in name:
        report.major(f"Name cannot contain consecutive hyphens: {name}", filename)

    # Start/end hyphen check
    if name.startswith("-") or name.endswith("-"):
        report.major(f"Name cannot start/end with hyphen: {name}", filename)


def validate_description_field(frontmatter: dict[str, Any], filename: str, report: AgentValidationReport) -> None:
    """Validate the 'description' frontmatter field."""
    if "description" not in frontmatter:
        report.major("Missing 'description' field (required)", filename)
        return

    desc = frontmatter["description"]

    if not isinstance(desc, str):
        report.critical(f"'description' must be a string, got {type(desc).__name__}", filename)
        return

    if not desc.strip():
        report.major("'description' cannot be empty", filename)
        return

    # Length checks
    if len(desc) < 10:
        report.minor(
            f"Description is very short ({len(desc)} chars) - may not help Claude decide when to use",
            filename,
        )

    if len(desc) > MAX_DESCRIPTION_LENGTH:
        report.major(
            f"Description exceeds {MAX_DESCRIPTION_LENGTH} chars ({len(desc)} chars)",
            filename,
        )

    # Angle brackets check (breaks XML in prompts)
    if "<" in desc or ">" in desc:
        report.major(
            "Description contains angle brackets (< or >) - can break agent prompts",
            filename,
        )

    # Check for actionable description (should indicate WHEN to use)
    action_words = ["use when", "invoke", "call", "trigger", "run", "execute", "specialized in", "expert in"]
    has_action_hint = any(word in desc.lower() for word in action_words)
    if not has_action_hint:
        report.info(
            "Description should indicate WHEN to invoke the agent (e.g., 'Use when...')",
            filename,
        )

    # Check for proactive delegation hint (best practice from sub-agents docs)
    if "proactively" in desc.lower() or "use proactively" in desc.lower():
        report.passed("Description includes proactive delegation hint", filename)
    else:
        report.info(
            "Consider adding 'use proactively' to encourage Claude to delegate automatically",
            filename,
        )

    report.passed("'description' field valid", filename)


def validate_tools_field(frontmatter: dict[str, Any], filename: str, report: AgentValidationReport) -> None:
    """Validate the 'tools' frontmatter field."""
    if "tools" not in frontmatter:
        report.info("No 'tools' field (agent will inherit default tools)", filename)
        return

    tools = frontmatter["tools"]

    # Can be string (comma-separated) or list
    if isinstance(tools, str):
        tool_list = [t.strip() for t in tools.split(",") if t.strip()]
    elif isinstance(tools, list):
        tool_list = [str(t).strip() for t in tools if str(t).strip()]
    else:
        report.major(
            f"'tools' must be string or list, got {type(tools).__name__}",
            filename,
        )
        return

    if not tool_list:
        report.minor("'tools' field is empty", filename)
        return

    # Validate each tool name
    invalid_tools = []
    for tool in tool_list:
        # Handle tool with pattern like "Bash(git *)"
        base_tool = tool.split("(")[0].strip()
        if base_tool not in VALID_TOOLS and not base_tool.startswith("mcp__"):
            invalid_tools.append(tool)

    if invalid_tools:
        report.info(
            f"Unknown tools (may be custom): {', '.join(invalid_tools)}",
            filename,
        )

    report.passed(f"'tools' field valid: {len(tool_list)} tool(s)", filename)


def validate_model_field(frontmatter: dict[str, Any], filename: str, report: AgentValidationReport) -> None:
    """Validate the 'model' frontmatter field."""
    if "model" not in frontmatter:
        report.info("No 'model' field (agent will inherit parent model)", filename)
        return

    model = frontmatter["model"]

    if not isinstance(model, str):
        report.major(f"'model' must be a string, got {type(model).__name__}", filename)
        return

    model_lower = model.lower()
    if model_lower not in VALID_MODELS:
        report.major(
            f"Invalid 'model' value: {model}. Valid values: {VALID_MODELS}",
            filename,
        )
        return

    report.passed(f"'model' field valid: {model}", filename)


def validate_color_field(frontmatter: dict[str, Any], filename: str, report: AgentValidationReport) -> None:
    """Validate the 'color' frontmatter field."""
    if "color" not in frontmatter:
        return

    color = frontmatter["color"]

    if not isinstance(color, str):
        report.major(f"'color' must be a string, got {type(color).__name__}", filename)
        return

    # Hex color pattern
    hex_pattern = re.compile(r"^#[0-9A-Fa-f]{6}$")
    if not hex_pattern.match(color):
        report.major(
            f"'color' must be hex format (#RRGGBB): {color}",
            filename,
        )
        return

    report.passed(f"'color' field valid: {color}", filename)


def validate_capabilities_field(frontmatter: dict[str, Any], filename: str, report: AgentValidationReport) -> None:
    """Validate the 'capabilities' frontmatter field."""
    if "capabilities" not in frontmatter:
        return

    caps = frontmatter["capabilities"]

    if not isinstance(caps, list):
        report.major(
            f"'capabilities' must be an array, got {type(caps).__name__}",
            filename,
        )
        return

    for i, cap in enumerate(caps):
        if not isinstance(cap, str):
            report.major(
                f"'capabilities[{i}]' must be a string, got {type(cap).__name__}",
                filename,
            )

    report.passed(f"'capabilities' field valid: {len(caps)} capability(ies)", filename)


def validate_context_field(frontmatter: dict[str, Any], filename: str, report: AgentValidationReport) -> None:
    """Validate the 'context' frontmatter field.

    Valid values: 'fork' (or empty/missing).
    The 'fork' context indicates this agent runs in a separate process.
    """
    if "context" not in frontmatter:
        # context is optional - missing is fine
        return

    context = frontmatter["context"]

    if not isinstance(context, str):
        report.major(f"'context' must be a string, got {type(context).__name__}", filename)
        return

    if context not in VALID_CONTEXT_VALUES:
        report.major(
            f"Invalid 'context' value: '{context}'. Valid values: {sorted(VALID_CONTEXT_VALUES)}",
            filename,
        )
        return

    report.passed(f"'context' field valid: {context}", filename)


def validate_agent_field(frontmatter: dict[str, Any], filename: str, report: AgentValidationReport) -> None:
    """Validate the 'agent' frontmatter field.

    This field specifies specialized agent types.
    Standard values: api-coordinator, test-engineer, deploy-agent, debug-specialist, code-reviewer.
    Non-standard values are allowed but reported as INFO.
    """
    if "agent" not in frontmatter:
        # agent field is optional
        return

    agent = frontmatter["agent"]

    if not isinstance(agent, str):
        report.major(f"'agent' must be a string, got {type(agent).__name__}", filename)
        return

    if agent not in VALID_AGENT_VALUES:
        report.info(
            f"Non-standard 'agent' value: '{agent}'. Standard values: {sorted(VALID_AGENT_VALUES)}",
            filename,
        )
    else:
        report.passed(f"'agent' field valid: {agent}", filename)


def validate_user_invocable_field(frontmatter: dict[str, Any], filename: str, report: AgentValidationReport) -> None:
    """Validate the 'user-invocable' frontmatter field.

    Must be a boolean (true or false), not a string.
    """
    if "user-invocable" not in frontmatter:
        # user-invocable is optional
        return

    value = frontmatter["user-invocable"]

    if isinstance(value, bool):
        report.passed(f"'user-invocable' field valid: {value}", filename)
    elif isinstance(value, str) and value.lower() in ("true", "false"):
        report.minor(
            f"'user-invocable' should be boolean, not string: {value!r} -> use {value.lower() == 'true'}",
            filename,
        )
    else:
        report.major(
            f"'user-invocable' must be boolean (true/false), got: {type(value).__name__} = {value!r}",
            filename,
        )


def validate_system_prompt_field(frontmatter: dict[str, Any], filename: str, report: AgentValidationReport) -> None:
    """Validate the 'system-prompt' frontmatter field.

    Checks for placeholder text like TODO, PLACEHOLDER, FIXME, etc.
    """
    if "system-prompt" not in frontmatter:
        # system-prompt is optional
        return

    prompt = frontmatter["system-prompt"]

    if not isinstance(prompt, str):
        report.major(f"'system-prompt' must be a string, got {type(prompt).__name__}", filename)
        return

    if not prompt.strip():
        report.major("'system-prompt' cannot be empty", filename)
        return

    # Check for placeholder text
    for pattern in PLACEHOLDER_PATTERNS:
        match = pattern.search(prompt)
        if match:
            report.major(
                f"'system-prompt' contains placeholder text: '{match.group()}'",
                filename,
            )
            return

    report.passed("'system-prompt' field valid", filename)


def validate_skills_field(frontmatter: dict[str, Any], filename: str, report: AgentValidationReport) -> None:
    """Validate the 'skills' frontmatter field.

    The skills field specifies which skills the agent has access to.
    Must be a list of skill names (strings).
    """
    if "skills" not in frontmatter:
        # skills is optional
        return

    skills = frontmatter["skills"]

    if not isinstance(skills, list):
        report.major(f"'skills' must be a list, got {type(skills).__name__}", filename)
        return

    if not skills:
        report.minor("'skills' list is empty - consider removing if no skills needed", filename)
        return

    invalid_items = []
    valid_skills = []
    for i, skill in enumerate(skills):
        if not isinstance(skill, str):
            invalid_items.append(f"index {i}: {type(skill).__name__}")
        elif not skill.strip():
            invalid_items.append(f"index {i}: empty string")
        else:
            valid_skills.append(skill)

    if invalid_items:
        report.major(f"'skills' contains invalid items: {', '.join(invalid_items)}", filename)
        return

    report.passed(f"'skills' field valid: {valid_skills}", filename)


def validate_permission_mode_field(frontmatter: dict[str, Any], filename: str, report: AgentValidationReport) -> None:
    """Validate the 'permissionMode' frontmatter field.

    Valid values per sub-agents docs:
    - default: Standard permission checking with prompts
    - acceptEdits: Auto-accept file edits
    - dontAsk: Auto-deny permission prompts (explicitly allowed tools still work)
    - bypassPermissions: Skip all permission checks (use with caution!)
    - plan: Plan mode (read-only exploration)
    """
    if "permissionMode" not in frontmatter:
        # permissionMode is optional - defaults to 'default'
        return

    mode = frontmatter["permissionMode"]

    if not isinstance(mode, str):
        report.major(f"'permissionMode' must be a string, got {type(mode).__name__}", filename)
        return

    if mode not in VALID_PERMISSION_MODES:
        report.major(
            f"Invalid 'permissionMode' value: '{mode}'. Valid values: {sorted(VALID_PERMISSION_MODES)}",
            filename,
        )
        return

    # Warn about dangerous permission modes
    if mode == "bypassPermissions":
        report.minor(
            "'permissionMode: bypassPermissions' skips ALL permission checks - use with caution!",
            filename,
        )

    report.passed(f"'permissionMode' field valid: {mode}", filename)


def validate_memory_field(frontmatter: dict[str, Any], filename: str, report: AgentValidationReport) -> None:
    """Validate the 'memory' frontmatter field."""
    if "memory" not in frontmatter:
        return

    rel_path = filename
    memory_val = frontmatter["memory"]
    if not isinstance(memory_val, str):
        report.major(f"'memory' must be a string, got {type(memory_val).__name__}", rel_path)
    elif memory_val not in VALID_MEMORY_SCOPES:
        report.major(
            f"Invalid 'memory' value: '{memory_val}'. Must be one of: {sorted(VALID_MEMORY_SCOPES)}",
            rel_path,
        )
    else:
        report.passed(f"Valid memory scope: {memory_val}", rel_path)


def validate_isolation_field(frontmatter: dict[str, Any], filename: str, report: AgentValidationReport) -> None:
    """Validate the 'isolation' frontmatter field."""
    if "isolation" not in frontmatter:
        return

    rel_path = filename
    isolation_val = frontmatter["isolation"]
    if not isinstance(isolation_val, str):
        report.major(f"'isolation' must be a string, got {type(isolation_val).__name__}", rel_path)
    elif isolation_val not in VALID_ISOLATION_VALUES:
        report.major(
            f"Invalid 'isolation' value: '{isolation_val}'. Must be one of: {sorted(VALID_ISOLATION_VALUES)}",
            rel_path,
        )
    else:
        report.passed(f"Valid isolation mode: {isolation_val}", rel_path)


def validate_max_turns_field(frontmatter: dict[str, Any], filename: str, report: AgentValidationReport) -> None:
    """Validate the 'maxTurns' frontmatter field."""
    if "maxTurns" not in frontmatter:
        return

    rel_path = filename
    max_turns = frontmatter["maxTurns"]
    if not isinstance(max_turns, int) or max_turns < 1:
        report.major(f"'maxTurns' must be a positive integer, got {max_turns!r}", rel_path)
    else:
        report.passed(f"Valid maxTurns: {max_turns}", rel_path)


def validate_background_field(frontmatter: dict[str, Any], filename: str, report: AgentValidationReport) -> None:
    """Validate the 'background' frontmatter field."""
    if "background" not in frontmatter:
        return

    rel_path = filename
    bg_val = frontmatter["background"]
    if not isinstance(bg_val, bool):
        report.major(f"'background' must be a boolean, got {type(bg_val).__name__}", rel_path)
    else:
        report.passed(f"Valid background: {bg_val}", rel_path)


def validate_disallowed_tools_field(frontmatter: dict[str, Any], filename: str, report: AgentValidationReport) -> None:
    """Validate the 'disallowedTools' frontmatter field.

    Tools to deny, removed from inherited or specified tools list.
    Must be a comma-separated string or list of tool names.
    """
    if "disallowedTools" not in frontmatter:
        # disallowedTools is optional
        return

    tools = frontmatter["disallowedTools"]

    # Can be string (comma-separated) or list
    if isinstance(tools, str):
        tool_list = [t.strip() for t in tools.split(",") if t.strip()]
    elif isinstance(tools, list):
        tool_list = [str(t).strip() for t in tools if str(t).strip()]
    else:
        report.major(
            f"'disallowedTools' must be string or list, got {type(tools).__name__}",
            filename,
        )
        return

    if not tool_list:
        report.minor("'disallowedTools' field is empty - consider removing", filename)
        return

    # Validate each tool name
    invalid_tools = []
    for tool in tool_list:
        base_tool = tool.split("(")[0].strip()
        if base_tool not in VALID_TOOLS and not base_tool.startswith("mcp__"):
            invalid_tools.append(tool)

    if invalid_tools:
        report.info(
            f"Unknown tools in disallowedTools (may be custom): {', '.join(invalid_tools)}",
            filename,
        )

    report.passed(f"'disallowedTools' field valid: {len(tool_list)} tool(s)", filename)


def validate_hooks_field(frontmatter: dict[str, Any], filename: str, report: AgentValidationReport) -> None:
    """Validate the 'hooks' frontmatter field.

    Hooks scoped to this subagent. Valid event types for agents:
    - PreToolUse: Before the subagent uses a tool (supports matcher)
    - PostToolUse: After the subagent uses a tool (supports matcher)
    - Stop: When the subagent finishes (no matcher)
    """
    if "hooks" not in frontmatter:
        # hooks is optional
        return

    hooks = frontmatter["hooks"]

    if not isinstance(hooks, dict):
        report.major(f"'hooks' must be an object, got {type(hooks).__name__}", filename)
        return

    valid_agent_hook_events = {"PreToolUse", "PostToolUse", "Stop"}

    for event_name, event_config in hooks.items():
        if event_name not in valid_agent_hook_events:
            report.major(
                f"Invalid hook event for agent: '{event_name}'. Valid events: {sorted(valid_agent_hook_events)}",
                filename,
            )
            continue

        if not isinstance(event_config, list):
            report.major(
                f"Hook event '{event_name}' must be an array of matcher blocks",
                filename,
            )
            continue

        for i, matcher_block in enumerate(event_config):
            if not isinstance(matcher_block, dict):
                report.major(
                    f"Hook '{event_name}[{i}]' must be an object",
                    filename,
                )
                continue

            # Check for required 'hooks' array in matcher block
            if "hooks" not in matcher_block:
                report.major(
                    f"Hook '{event_name}[{i}]' missing required 'hooks' array",
                    filename,
                )
                continue

            inner_hooks = matcher_block["hooks"]
            if not isinstance(inner_hooks, list):
                report.major(
                    f"Hook '{event_name}[{i}].hooks' must be an array",
                    filename,
                )
                continue

            # Validate each hook in the array
            for j, hook in enumerate(inner_hooks):
                if not isinstance(hook, dict):
                    report.major(
                        f"Hook '{event_name}[{i}].hooks[{j}]' must be an object",
                        filename,
                    )
                    continue

                # Check for required 'type' field
                if "type" not in hook:
                    report.major(
                        f"Hook '{event_name}[{i}].hooks[{j}]' missing required 'type' field",
                        filename,
                    )
                    continue

                hook_type = hook["type"]
                if hook_type not in {"command", "prompt"}:
                    report.major(
                        f"Invalid hook type '{hook_type}' in '{event_name}[{i}].hooks[{j}]'. "
                        "Valid types: command, prompt",
                        filename,
                    )

    report.passed("'hooks' field structure valid", filename)


def validate_task_tool_prohibition(frontmatter: dict[str, Any], filename: str, report: AgentValidationReport) -> None:
    """Validate that subagents (context: fork) do not have Task tool.

    If an agent has context: fork (meaning it's meant to be spawned as a subagent),
    it should NOT have Task in its allowed tools to prevent infinite recursion.
    """
    context = frontmatter.get("context")
    if context != "fork":
        # Not a subagent, no restriction needed
        return

    tools = frontmatter.get("tools")
    if tools is None:
        return

    # Parse tools field (can be string or list)
    if isinstance(tools, str):
        tool_list = [t.strip() for t in tools.split(",") if t.strip()]
    elif isinstance(tools, list):
        tool_list = [str(t).strip() for t in tools if str(t).strip()]
    else:
        return

    # Check for Task tool (handle patterns like "Task" or "Task(pattern)")
    for tool in tool_list:
        base_tool = tool.split("(")[0].strip()
        if base_tool == "Task":
            report.major(
                "Subagent (context: fork) has Task tool - may cause infinite recursion",
                filename,
            )
            return


def validate_example_blocks(content: str, filename: str, report: AgentValidationReport) -> None:
    """Validate that agent has sufficient example blocks.

    Agent documentation should have 2-3+ <example> blocks with proper structure:
    - <example> opening tag
    - Context line (optional but recommended)
    - user: line with user message
    - assistant: line with assistant response
    - <commentary> block (recommended)
    - </example> closing tag
    """
    _, body, _ = parse_frontmatter(content)

    if not body.strip():
        # No body content - already flagged elsewhere
        return

    # Find all example blocks
    example_pattern = re.compile(r"<example>(.*?)</example>", re.DOTALL)
    examples = example_pattern.findall(body)

    example_count = len(examples)

    if example_count == 0:
        report.major(
            f"No <example> blocks found (need at least {MIN_EXAMPLE_BLOCKS})",
            filename,
        )
        return

    if example_count < MIN_EXAMPLE_BLOCKS:
        report.major(
            f"Only {example_count} <example> block(s) found (need at least {MIN_EXAMPLE_BLOCKS})",
            filename,
        )
    else:
        report.passed(f"Has {example_count} <example> block(s)", filename)

    # Validate each example block structure
    for i, example in enumerate(examples, 1):
        has_user = re.search(r"^\s*user:", example, re.MULTILINE | re.IGNORECASE) is not None
        has_assistant = re.search(r"^\s*assistant:", example, re.MULTILINE | re.IGNORECASE) is not None
        has_commentary = "<commentary>" in example and "</commentary>" in example

        if not has_user:
            report.minor(
                f"Example {i} missing 'user:' line",
                filename,
            )

        if not has_assistant:
            report.minor(
                f"Example {i} missing 'assistant:' line",
                filename,
            )

        if not has_commentary:
            report.info(
                f"Example {i} has no <commentary> block (recommended for clarity)",
                filename,
            )


def validate_body_content(content: str, filename: str, report: AgentValidationReport) -> None:
    """Validate agent body content (after frontmatter)."""
    _, body, _ = parse_frontmatter(content)

    if not body.strip():
        report.major("Agent has no content after frontmatter", filename)
        return

    body_text = body.strip()

    # Minimum content check
    if len(body_text) < MIN_BODY_CHARS:
        report.minor(
            f"Agent body is very short ({len(body_text)} chars, recommended: >{MIN_BODY_CHARS})",
            filename,
        )

    # Word count check
    word_count = len(body_text.split())
    if word_count > MAX_BODY_WORDS:
        report.minor(
            f"Agent body is very long ({word_count} words, recommended: <{MAX_BODY_WORDS})",
            filename,
        )

    # Role definition check (should have "You are" statement)
    if "you are" not in body_text.lower():
        report.minor(
            "Agent body should include a role definition ('You are...' statement)",
            filename,
        )
    else:
        report.passed("Role definition present ('You are...')", filename)

    # Check for common sections
    sections_found = []

    if re.search(r"##\s*capabilities", body_text, re.IGNORECASE):
        sections_found.append("Capabilities")
        report.passed("Has '## Capabilities' section", filename)

    if re.search(r"##\s*workflow", body_text, re.IGNORECASE):
        sections_found.append("Workflow")
        report.passed("Has '## Workflow' section", filename)

    if re.search(r"##\s*(approach|guidelines|instructions)", body_text, re.IGNORECASE):
        sections_found.append("Approach/Guidelines")
        report.passed("Has approach/guidelines section", filename)

    if not sections_found:
        report.info(
            "Consider adding structured sections (## Capabilities, ## Workflow, etc.)",
            filename,
        )


def validate_security(content: str, filename: str, report: AgentValidationReport) -> None:
    """Check for security issues in agent content."""
    # Check for hardcoded secrets
    for pattern, description in SECRET_PATTERNS:
        if pattern.search(content):
            report.critical(f"SECURITY: Contains {description}", filename)

    # Check for hardcoded user paths
    for pattern in USER_PATH_PATTERNS:
        match = pattern.search(content)
        if match:
            report.major(
                f"Contains hardcoded user path: {match.group()}",
                filename,
            )

    # Check for ${CLAUDE_PLUGIN_ROOT} usage (good practice)
    if "/scripts/" in content or "\\scripts\\" in content:
        if "${CLAUDE_PLUGIN_ROOT}" not in content and "$CLAUDE_PLUGIN_ROOT" not in content:
            report.info(
                "Consider using ${CLAUDE_PLUGIN_ROOT} for plugin-relative paths",
                filename,
            )


def validate_agent(agent_path: Path) -> AgentValidationReport:
    """Validate a complete agent file.

    Args:
        agent_path: Path to the agent .md file

    Returns:
        AgentValidationReport with all results
    """
    report = AgentValidationReport(agent_path=str(agent_path))
    filename = agent_path.name

    # Check file exists
    if not agent_path.exists():
        report.critical(f"Agent file not found: {agent_path}")
        return report

    if not agent_path.is_file():
        report.critical(f"Agent path is not a file: {agent_path}")
        return report

    # Check file extension
    if agent_path.suffix.lower() != ".md":
        report.major(f"Agent file should have .md extension, got: {agent_path.suffix}", filename)

    # Read file content (binary first for encoding check)
    content_bytes = agent_path.read_bytes()

    # Check encoding using shared function
    if not check_utf8_encoding(content_bytes, report, filename):
        return report

    report.passed("File is valid UTF-8", filename)

    content = content_bytes.decode("utf-8")

    # Validate frontmatter
    frontmatter = validate_frontmatter_exists(content, report, filename)

    if frontmatter is not None:
        # Validate individual frontmatter fields
        validate_name_field(frontmatter, filename, report)
        validate_description_field(frontmatter, filename, report)
        validate_tools_field(frontmatter, filename, report)
        validate_model_field(frontmatter, filename, report)
        validate_color_field(frontmatter, filename, report)
        validate_capabilities_field(frontmatter, filename, report)

        # Validate Claude Code-specific fields
        validate_context_field(frontmatter, filename, report)
        validate_agent_field(frontmatter, filename, report)
        validate_user_invocable_field(frontmatter, filename, report)
        validate_system_prompt_field(frontmatter, filename, report)
        validate_skills_field(frontmatter, filename, report)

        # Validate sub-agent specific fields (from sub-agents.md spec)
        validate_permission_mode_field(frontmatter, filename, report)
        validate_disallowed_tools_field(frontmatter, filename, report)
        validate_hooks_field(frontmatter, filename, report)

        # Validate new official fields
        validate_memory_field(frontmatter, filename, report)
        validate_isolation_field(frontmatter, filename, report)
        validate_max_turns_field(frontmatter, filename, report)
        validate_background_field(frontmatter, filename, report)

        # Cross-field validations
        validate_task_tool_prohibition(frontmatter, filename, report)

    # Validate body content
    validate_body_content(content, filename, report)

    # Validate example blocks
    validate_example_blocks(content, filename, report)

    # Security checks
    validate_security(content, filename, report)

    return report


def validate_agents_directory(agents_dir: Path) -> list[AgentValidationReport]:
    """Validate all agent files in a directory.

    Args:
        agents_dir: Path to the agents/ directory

    Returns:
        List of AgentValidationReport for each agent
    """
    reports = []

    if not agents_dir.is_dir():
        report = AgentValidationReport(agent_path=str(agents_dir))
        report.critical(f"Not a directory: {agents_dir}")
        return [report]

    agent_files = list(agents_dir.glob("*.md"))

    if not agent_files:
        report = AgentValidationReport(agent_path=str(agents_dir))
        report.info("No agent files (*.md) found in directory")
        return [report]

    for agent_file in sorted(agent_files):
        reports.append(validate_agent(agent_file))

    return reports


def print_results(report: AgentValidationReport, verbose: bool = False) -> None:
    """Print validation results in human-readable format."""
    # Count by level
    counts = {"CRITICAL": 0, "MAJOR": 0, "MINOR": 0, "NIT": 0, "WARNING": 0, "INFO": 0, "PASSED": 0}
    for r in report.results:
        counts[r.level] += 1

    # Print header
    print("\n" + "=" * 60)
    print(f"Agent Validation: {report.agent_path}")
    print("=" * 60)

    # Print summary
    print("\nSummary:")
    print(f"  {COLORS['CRITICAL']}CRITICAL: {counts['CRITICAL']}{COLORS['RESET']}")
    print(f"  {COLORS['MAJOR']}MAJOR:    {counts['MAJOR']}{COLORS['RESET']}")
    print(f"  {COLORS['MINOR']}MINOR:    {counts['MINOR']}{COLORS['RESET']}")
    print(f"  {COLORS['NIT']}NIT:      {counts['NIT']}{COLORS['RESET']}")
    print(f"  {COLORS['WARNING']}WARNING:  {counts['WARNING']}{COLORS['RESET']}")
    if verbose:
        print(f"  {COLORS['INFO']}INFO:     {counts['INFO']}{COLORS['RESET']}")
        print(f"  {COLORS['PASSED']}PASSED:   {counts['PASSED']}{COLORS['RESET']}")

    # Print score
    score = report.score
    score_color = COLORS["PASSED"] if score >= 80 else COLORS["MAJOR"] if score >= 60 else COLORS["CRITICAL"]
    print(f"\n  Score: {score_color}{score}/100{COLORS['RESET']}")

    # Print details
    print("\nDetails:")
    for r in report.results:
        if r.level == "PASSED" and not verbose:
            continue
        if r.level == "INFO" and not verbose:
            continue

        color = COLORS[r.level]
        reset = COLORS["RESET"]
        file_info = f" ({r.file})" if r.file else ""
        line_info = f":{r.line}" if r.line else ""
        print(f"  {color}[{r.level}]{reset} {r.message}{file_info}{line_info}")

    # Print final status
    print("\n" + "-" * 60)
    if report.exit_code == 0:
        print(f"{COLORS['PASSED']}PASSED: Agent validation passed{COLORS['RESET']}")
    elif report.exit_code == 1:
        print(f"{COLORS['CRITICAL']}FAILED: CRITICAL issues - agent will not work{COLORS['RESET']}")
    elif report.exit_code == 2:
        print(f"{COLORS['MAJOR']}WARNING: MAJOR issues - significant problems{COLORS['RESET']}")
    else:
        print(f"{COLORS['MINOR']}INFO: MINOR issues - may affect UX{COLORS['RESET']}")

    print()


def print_json(report: AgentValidationReport) -> None:
    """Print validation results as JSON."""
    output = {
        "agent_path": report.agent_path,
        "exit_code": report.exit_code,
        "score": report.score,
        "counts": {
            "critical": sum(1 for r in report.results if r.level == "CRITICAL"),
            "major": sum(1 for r in report.results if r.level == "MAJOR"),
            "minor": sum(1 for r in report.results if r.level == "MINOR"),
            "info": sum(1 for r in report.results if r.level == "INFO"),
            "passed": sum(1 for r in report.results if r.level == "PASSED"),
        },
        "results": [{"level": r.level, "message": r.message, "file": r.file, "line": r.line} for r in report.results],
    }
    print(json.dumps(output, indent=2))


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate a Claude Code agent file or directory")
    parser.add_argument("path", help="Path to agent .md file or agents/ directory")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show all results including passed checks",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--strict", action="store_true", help="Strict mode — NIT issues also block validation")
    args = parser.parse_args()

    path = Path(args.path).resolve()

    if not path.exists():
        print(f"Error: {path} does not exist", file=sys.stderr)
        return 1

    # Verify content type — must be .md file or directory containing .md files
    if path.is_file() and path.suffix != ".md":
        print(f"Error: {path} is not a Markdown (.md) agent file", file=sys.stderr)
        return 1
    if path.is_dir() and not list(path.glob("*.md")):
        print(f"Error: No agent definition files (.md) found in {path}", file=sys.stderr)
        return 1

    # Handle directory vs file
    if path.is_dir():
        reports = validate_agents_directory(path)
    else:
        reports = [validate_agent(path)]

    # Output
    if args.json:
        if len(reports) == 1:
            print_json(reports[0])
        else:
            combined = {
                "agents": [
                    {
                        "agent_path": r.agent_path,
                        "exit_code": r.exit_code,
                        "score": r.score,
                        "counts": {
                            "critical": sum(1 for x in r.results if x.level == "CRITICAL"),
                            "major": sum(1 for x in r.results if x.level == "MAJOR"),
                            "minor": sum(1 for x in r.results if x.level == "MINOR"),
                            "info": sum(1 for x in r.results if x.level == "INFO"),
                            "passed": sum(1 for x in r.results if x.level == "PASSED"),
                        },
                        "results": [
                            {"level": x.level, "message": x.message, "file": x.file, "line": x.line} for x in r.results
                        ],
                    }
                    for r in reports
                ],
                "overall_exit_code": max(r.exit_code for r in reports),
            }
            print(json.dumps(combined, indent=2))
    else:
        for report in reports:
            print_results(report, args.verbose)

    # Return worst exit code — in strict mode, NIT issues also block validation
    if args.strict:
        return max(r.exit_code_strict() for r in reports)
    return max(r.exit_code for r in reports)


if __name__ == "__main__":
    sys.exit(main())
