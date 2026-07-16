"""
amoa_state.py - Shared orchestration-state helpers for Orchestrator Agent.

Extracted from ~23 near-identical copies across scripts/*.py and
skills/*/scripts/*.py (TRDD-03DYGXJW) to clear the jscpd copy-paste gate.

Each call site keeps its own thin `parse_frontmatter`/`load_state` wrapper
with its ORIGINAL signature and return-type contract, delegating the actual
parsing to the functions below. This means behavior is preserved exactly
per call site (including the one caller that prints on a YAML parse error,
and the one caller that defaults to {"updates": {}} instead of None) while
the duplicated bodies collapse to a couple of lines each.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, overload

import yaml

# Canonical exec-phase state file location. Was duplicated verbatim as a
# module-level constant in 14 scripts.
EXEC_STATE_FILE = Path(".claude/orchestrator-exec-phase.local.md")


def parse_frontmatter(
    file_path: Path,
    *,
    on_yaml_error: Callable[[yaml.YAMLError], None] | None = None,
) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter and return (data, body).

    `on_yaml_error`, if given, is invoked with the YAMLError before falling
    back to ({}, content) — preserves the one pre-existing call site
    (module_operations.py) that printed a diagnostic on a parse error;
    every other caller passes nothing and stays silent on that path,
    exactly as before.
    """
    if not file_path.exists():
        return {}, ""

    content = file_path.read_text(encoding="utf-8")

    if not content.startswith("---"):
        return {}, content

    end_index = content.find("---", 3)
    if end_index == -1:
        return {}, content

    yaml_content = content[3:end_index].strip()
    body = content[end_index + 3 :].strip()

    try:
        data: dict[str, Any] = yaml.safe_load(yaml_content) or {}
        return data, body
    except yaml.YAMLError as e:
        if on_yaml_error is not None:
            on_yaml_error(e)
        return {}, content


# Overloads so the return type tracks the sentinel: callers that omit
# `default` may get None back (the JSON-missing case); callers that pass a
# concrete dict default are guaranteed a dict, so they can index the result
# without a None-check. This mirrors typeshed's own dict.get typing and
# preserves the two pre-existing contracts exactly (most callers returned
# `dict | None`; amoa_update_verification returned a non-optional dict).
@overload
def load_json_state(state_path: Path) -> dict[str, Any] | None: ...
@overload
def load_json_state(state_path: Path, *, default: dict[str, Any]) -> dict[str, Any]: ...


def load_json_state(
    state_path: Path,
    *,
    default: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Load a JSON state file, returning `default` if it is missing, empty,
    unparsable, or not a JSON object.

    `default` is returned as-is (not copied) on every fallback path — a
    caller that needs the sentinel to be its own fresh mutable object
    passes a freshly-constructed literal at each call, which is what every
    existing call site already does.
    """
    if not state_path.exists():
        return default

    try:
        content = state_path.read_text(encoding="utf-8").strip()
        if not content:
            return default
        data = json.loads(content)
        if not isinstance(data, dict):
            return default
        return data
    except (json.JSONDecodeError, OSError):
        return default
