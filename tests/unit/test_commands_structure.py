#!/usr/bin/env python3
"""Structural tests for the 15 AMOA slash commands in commands/*.md.

REAL tests, NO mocks. Two parametrized checks run over EVERY command file:

  (a) Frontmatter is valid YAML with the required keys (`name`, `description`),
      and if an `argument-hint` is present it MUST be a quoted string. A bare
      `argument-hint: [foo] [bar]` is a real bug: YAML parses the leading `[`
      as a flow-sequence, silently turning the hint into a list (or raising),
      which corrupts the whole frontmatter block.

  (b) Every concrete `${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py` path the command
      body (or its allowed-tools) references actually EXISTS in the repo. A
      dangling script reference means the slash command is dead on arrival.

Scope note for (b): only the structured `${CLAUDE_PLUGIN_ROOT}/scripts/*.py`
references are checked -- those are concrete, in-repo, and verifiable. Prose
mentions of cross-plugin skills (e.g. "using the `agent-messaging` skill") are
NOT local to this repo and are intentionally out of scope; checking them would
produce false failures for references this plugin does not own.
"""

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
COMMANDS_DIR = REPO_ROOT / "commands"

# Dynamic discovery -- stays honest if commands are added/removed.
COMMAND_FILES = sorted(COMMANDS_DIR.glob("*.md"))

# Guard: the suite is meant to cover the 15 documented commands. If this count
# drifts, the test should be re-reviewed rather than silently covering more/less.
EXPECTED_COMMAND_COUNT = 15

# Matches a concrete script reference like ${CLAUDE_PLUGIN_ROOT}/scripts/foo.py
SCRIPT_REF_RE = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/scripts/([A-Za-z0-9_]+\.py)")

# Matches the raw `argument-hint:` line so we can inspect its UNPARSED value.
ARG_HINT_LINE_RE = re.compile(r"^argument-hint:(.*)$", re.MULTILINE)


def _split_frontmatter(text: str) -> tuple[str, str]:
    """Return (raw_frontmatter, body) for a `---`-delimited markdown file."""
    assert text.startswith("---"), "command file must begin with YAML frontmatter"
    end = text.find("---", 3)
    assert end != -1, "command frontmatter is not terminated by a closing '---'"
    return text[3:end].strip(), text[end + 3 :]


def test_commands_discovered():
    """Exactly the expected number of command files are present to parametrize over."""
    assert len(COMMAND_FILES) == EXPECTED_COMMAND_COUNT, (
        f"expected {EXPECTED_COMMAND_COUNT} command files, "
        f"found {len(COMMAND_FILES)}: {[p.name for p in COMMAND_FILES]}"
    )


@pytest.mark.parametrize("cmd_path", COMMAND_FILES, ids=lambda p: p.name)
def test_command_frontmatter_valid(cmd_path):
    """Each command has parseable frontmatter with name+description and a string argument-hint."""
    text = cmd_path.read_text(encoding="utf-8")
    raw_fm, _body = _split_frontmatter(text)

    # Frontmatter must parse as YAML and be a mapping.
    data = yaml.safe_load(raw_fm)
    assert isinstance(data, dict), f"{cmd_path.name}: frontmatter is not a YAML mapping"

    # Required keys, non-empty strings.
    for key in ("name", "description"):
        assert key in data, f"{cmd_path.name}: missing required key '{key}'"
        assert isinstance(data[key], str) and data[key].strip(), (
            f"{cmd_path.name}: '{key}' must be a non-empty string"
        )

    # name should match the filename stem (the slash-command identity).
    assert data["name"] == cmd_path.stem, (
        f"{cmd_path.name}: frontmatter name '{data['name']}' != filename stem"
    )

    # If argument-hint is present it MUST be a quoted string, not a bare
    # flow-sequence. Two independent checks:
    if "argument-hint" in data:
        # 1) After YAML parsing it must be a str (a bare `[...]` parses to list).
        assert isinstance(data["argument-hint"], str), (
            f"{cmd_path.name}: argument-hint parsed to {type(data['argument-hint']).__name__}, "
            f"not str -- it is a bare YAML flow-sequence and must be quoted"
        )
        # 2) The RAW line's value must be quoted, so the `[` is literal text and
        #    never interpreted by YAML as the start of a flow-sequence.
        m = ARG_HINT_LINE_RE.search(raw_fm)
        assert m is not None, f"{cmd_path.name}: argument-hint present in data but no raw line found"
        raw_value = m.group(1).strip()
        assert (raw_value.startswith('"') and raw_value.endswith('"')) or (
            raw_value.startswith("'") and raw_value.endswith("'")
        ), (
            f"{cmd_path.name}: argument-hint value {raw_value!r} is not quoted; "
            f"a bare '[...]' breaks the YAML block"
        )


@pytest.mark.parametrize("cmd_path", COMMAND_FILES, ids=lambda p: p.name)
def test_command_script_references_exist(cmd_path):
    """Every ${CLAUDE_PLUGIN_ROOT}/scripts/*.py the command references exists in the repo."""
    text = cmd_path.read_text(encoding="utf-8")
    referenced = set(SCRIPT_REF_RE.findall(text))

    # A command may legitimately reference no script (e.g. cancel-orchestrator
    # uses inline bash); that yields an empty set and trivially passes.
    missing = sorted(
        name for name in referenced if not (REPO_ROOT / "scripts" / name).is_file()
    )
    assert not missing, (
        f"{cmd_path.name}: references non-existent script(s): {missing} "
        f"(expected under {REPO_ROOT / 'scripts'})"
    )
