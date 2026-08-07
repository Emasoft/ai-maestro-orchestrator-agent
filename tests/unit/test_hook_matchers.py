#!/usr/bin/env python3
"""Regression tests for the tool-name matchers in hooks/hooks.json.

A hook matcher that names a tool Claude Code no longer has fails SILENTLY: the
hook simply never fires, nothing errors, and a gate documented as MANDATORY
quietly stops gating. That is exactly what happened -- the verification gate
matched "Task" while the current build names the subagent tool `Agent`, and the
file tracker matched a MultiEdit tool that no longer exists.

These tests pin the two properties that make the repaired matchers correct, so
the failure mode is a red test instead of a gate that is merely absent:

  1. They fire on every spelling of the tool they target.
  2. They are ANCHORED, so they do not also fire on unrelated tools whose names
     merely CONTAIN the target ("ListAgents", "TaskCreate", "NotebookEdit").

Property 2 is not pedantry. Claude Code matchers are regular expressions, so the
obvious-looking `Task|Agent` matches `ListAgents`, `TaskCreate`, `TaskOutput`,
and `TaskStop` -- firing a blocking gate on routine peer discovery and task
bookkeeping. Anchoring also makes the pattern behave identically under
re.search, re.match, and re.fullmatch, so correctness does not depend on which
one the platform happens to use.
"""

import json
import re
from pathlib import Path

HOOKS_PATH = Path(__file__).resolve().parents[2] / "hooks" / "hooks.json"

# Tools this build actually exposes whose names embed "Task", "Agent", "Edit",
# or "Write". Every one of them is a false positive an unanchored matcher would
# catch, so they double as the guard list.
DECOY_TOOLS = [
    "ListAgents",
    "TaskCreate",
    "TaskGet",
    "TaskList",
    "TaskUpdate",
    "TaskOutput",
    "TaskStop",
    "NotebookEdit",
    "SendMessage",
]


def _matchers(event: str) -> list[str]:
    """Every matcher string registered under a given hook event.

    Raises rather than returning [] when the file shape is not what we expect.
    A helper that quietly returns nothing would make every assertion below pass
    vacuously -- the same silent-absence failure these tests exist to catch,
    reintroduced one layer up. (It bit exactly that way during authoring: the
    events live under a top-level "hooks" key, not at the document root.)
    """
    config = json.loads(HOOKS_PATH.read_text(encoding="utf-8"))
    events = config.get("hooks")
    assert isinstance(events, dict), (
        f"{HOOKS_PATH} has no top-level 'hooks' object; the shape changed and "
        "these matcher tests would silently pass on nothing"
    )
    return [
        entry["matcher"]
        for entry in events.get(event, [])
        if isinstance(entry, dict) and "matcher" in entry
    ]


def _fires(matcher: str, tool_name: str) -> bool:
    """True if `matcher` selects `tool_name` under ANY plausible match mode.

    Deliberately the union of search/match/fullmatch rather than one of them:
    the platform's choice is not contractual, so a matcher is only safe when the
    answer is the same for all three. Taking the union means a matcher that is
    loose under any mode counts as firing, which is what the decoy assertions
    need in order to be meaningful.
    """
    pattern = re.compile(matcher)
    return bool(
        pattern.search(tool_name)
        or pattern.match(tool_name)
        or pattern.fullmatch(tool_name)
    )


def test_subagent_gate_fires_on_both_tool_spellings():
    """The PreToolUse verification gate matches Agent (current) and Task (legacy)."""
    gates = [m for m in _matchers("PreToolUse") if "Agent" in m or "Task" in m]
    assert gates, "no PreToolUse matcher targets the subagent tool at all"
    for matcher in gates:
        assert _fires(matcher, "Agent"), f"{matcher!r} misses the current tool name"
        assert _fires(matcher, "Task"), f"{matcher!r} misses the legacy tool name"


def test_subagent_gate_does_not_fire_on_lookalike_tools():
    """The gate must not fire on ListAgents/TaskCreate/... -- the unanchored-regex trap."""
    gates = [m for m in _matchers("PreToolUse") if "Agent" in m or "Task" in m]
    for matcher in gates:
        for decoy in DECOY_TOOLS:
            assert not _fires(matcher, decoy), (
                f"{matcher!r} also fires on {decoy!r}; anchor it as ^(...)$"
            )


def test_file_tracker_matches_edit_and_write_only():
    """The PostToolUse tracker fires on Edit and Write, and on nothing that merely contains them."""
    trackers = [
        m for m in _matchers("PostToolUse") if "Edit" in m or "Write" in m
    ]
    assert trackers, "no PostToolUse matcher targets file-modifying tools"
    for matcher in trackers:
        assert _fires(matcher, "Edit")
        assert _fires(matcher, "Write")
        assert not _fires(matcher, "NotebookEdit"), (
            f"{matcher!r} fires on NotebookEdit, whose payload shape differs"
        )
        # MultiEdit is gone from Claude Code; matching it is dead weight that
        # implies a code path the tracker deliberately no longer has.
        assert not _fires(matcher, "MultiEdit"), (
            f"{matcher!r} still matches the removed MultiEdit tool"
        )


def test_every_matcher_is_anchored():
    """Anchoring is what makes match-mode irrelevant; an unanchored matcher is a latent bug."""
    for event in ("PreToolUse", "PostToolUse"):
        for matcher in _matchers(event):
            if matcher in ("*", ".*", ""):
                continue  # deliberate catch-alls are not accidents
            assert matcher.startswith("^") and matcher.endswith("$"), (
                f"{event} matcher {matcher!r} is unanchored: it will also select "
                "any tool whose name merely contains it"
            )
