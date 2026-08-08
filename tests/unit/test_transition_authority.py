#!/usr/bin/env python3
"""The editor-authority gate: an ORCHESTRATOR must not perform governed transitions.

The alignment contract (ai-maestro `rules/aimaestro/aimaestro-kanban-multiagent.md`,
"Orchestrator-plugin alignment") requires that an ORCHESTRATOR "moves and
re-assigns; it does not silently perform USER- or MANAGER-gated transitions".

`amoa_kanban_vocab.resolve_column` carries an invariant recording a MANAGER
ruling (orch#27): it is MIRROR-ONLY, and "if resolve_column is ever wired into a
path that ORIGINATES a TRDD `column:` write, a legacy value would land a card on
a MANAGER-gated column with no MANAGER stamp. If you add such a path: GATE THE
PATH, not this map." These tests pin that gate.

The gated sets come from `aimaestro-manager-approval-defaults.md` §Y (release
pipeline, abandonment, force-supersede) and §Z (the human's own verdict).
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared"))

from amoa_kanban_vocab import (  # noqa: E402
    KANBAN_COLUMNS,
    assert_orchestrator_may_transition,
    transition_authority,
)


@pytest.mark.parametrize(
    "frm,to",
    [
        ("dispatch", "dev"),
        ("dev", "testing"),
        ("testing", "ai_review"),
        ("testing", "dev"),
        ("ai_review", "dev"),
        ("live", "live_auditing"),
        ("live_auditing", "live"),
    ],
)
def test_mechanical_transitions_need_no_approval(frm, to):
    """Judgment-free moves are the orchestrator's own (approval-defaults section A)."""
    assert transition_authority(frm, to) == "orchestrator"
    assert_orchestrator_may_transition(frm, to)  # must not raise


@pytest.mark.parametrize(
    "frm,to",
    [
        ("complete", "publish"),
        ("complete", "deploy"),
        ("publish", "published"),
        ("deploy", "live"),
        ("ai_review", "human_review"),
        ("dev", "failed"),
        ("testing", "superseded"),
    ],
)
def test_release_and_abandonment_require_manager(frm, to):
    """Entering the release pipeline, abandoning, or escalating is MANAGER's call."""
    assert transition_authority(frm, to) == "manager"
    with pytest.raises(PermissionError, match="MANAGER"):
        assert_orchestrator_may_transition(frm, to)


@pytest.mark.parametrize("to", ["complete", "dev"])
def test_leaving_human_review_requires_user(to):
    """Leaving human_review IS the human's verdict — the orchestrator only relays it."""
    assert transition_authority("human_review", to) == "user"
    with pytest.raises(PermissionError, match="USER"):
        assert_orchestrator_may_transition("human_review", to)


def test_unknown_origin_resolves_to_the_stricter_answer():
    """A card with no readable current column must not become a licence to move it anywhere.

    An issue can carry no `status:` label at all. Treating that as "origin
    unknown, therefore probably fine" is how an ungated write reaches a governed
    column — the exact hazard the resolve_column invariant names.
    """
    assert transition_authority(None, "published") == "manager"
    with pytest.raises(PermissionError):
        assert_orchestrator_may_transition(None, "published")
    # ...while an ungoverned target stays permitted, so the strictness is
    # targeted rather than a blanket refusal that would block ordinary work.
    assert transition_authority(None, "todo") == "orchestrator"
    assert_orchestrator_may_transition(None, "todo")


def test_complete_is_never_the_orchestrators_call():
    """Declaring work finished is a verdict, from any origin."""
    for frm in ("testing", "ai_review", "dev", None):
        assert transition_authority(frm, "complete") in ("manager", "user")


def test_every_column_is_classifiable():
    """Guards the guard: a new column must not silently fall through to 'orchestrator'.

    If the ratified vocabulary grows, this fails loudly for any target whose
    authority nobody decided, rather than defaulting it to permitted.
    """
    unclassified = []
    for to in KANBAN_COLUMNS:
        authority = transition_authority(None, to)
        assert authority in ("orchestrator", "manager", "user")
        if to in ("publish", "published", "deploy", "live", "failed", "superseded",
                  "human_review", "complete") and authority == "orchestrator":
            unclassified.append(to)
    assert not unclassified, f"governed columns classified as permitted: {unclassified}"


def test_legacy_values_are_resolved_before_gating():
    """A legacy status must be migrated THEN gated — not gated as an unknown string.

    This is the concrete failure the invariant predicted: `verified` migrates to
    `complete`, a governed column. If the gate ran on the raw string it would not
    match any governed target and would wave the transition through.
    """
    assert transition_authority("testing", "verified") in ("manager", "user")
    with pytest.raises(PermissionError):
        assert_orchestrator_may_transition("testing", "verified")


def test_unknown_status_still_raises_valueerror():
    """The gate must not swallow the vocabulary error resolve_column exists to raise."""
    with pytest.raises(ValueError, match="unknown kanban status"):
        transition_authority("dev", "not-a-real-column")
