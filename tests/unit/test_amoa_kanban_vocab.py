#!/usr/bin/env python3
"""Unit tests for the shared kanban vocabulary (scripts/amoa_kanban_vocab.py).

Guards issue #27: the plugin must speak the ratified 22-column 3-pillars 3.0.0
vocabulary (3P-KAN) from ONE source of truth, migrate every legacy status
explicitly, and refuse (not silently bucket) an unknown status.
"""

import sys
from pathlib import Path

import pytest

# The vocabulary lives in shared/ (not scripts/) so the skill-bundled sync
# scripts, which sit at a different path depth, import the same module.
SHARED_DIR = Path(__file__).resolve().parents[2] / "shared"
if str(SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(SHARED_DIR))

from amoa_kanban_vocab import (  # noqa: E402
    BRACKET_COLUMNS,
    KANBAN_COLUMNS,
    LEGACY_STATUS_MIGRATION,
    LEGAL_COLUMNS,
    resolve_column,
)

# The ratified set, spelled out independently of the module so a drift in
# either direction fails this test. `@spec:kanban-columns v2` (3P-KAN).
EXPECTED_COLUMNS = {
    "backburner", "approval", "design", "design_ai_review", "design_human_review",
    "todo", "verify_assumptions", "plan", "dispatch", "dev", "testing",
    "ai_review", "human_review", "complete", "publish", "published",
    "deploy", "live", "live_auditing",
    "blocked", "failed", "superseded",
}

# The 5 BRACKET values (3P-KAN-20): legal `column:` values, not board columns.
EXPECTED_BRACKET_COLUMNS = {"proposal", "planned", "refused", "completed", "cancelled"}


def test_exactly_the_22_ratified_columns():
    """KANBAN_COLUMNS is exactly the 22 ratified 3-pillars 3.0.0 board columns, no more, no fewer."""
    assert len(KANBAN_COLUMNS) == 22
    assert set(KANBAN_COLUMNS) == EXPECTED_COLUMNS
    assert len(set(KANBAN_COLUMNS)) == 22  # no duplicates


def test_bracket_columns_are_legal_but_not_board_columns():
    """3P-KAN-20: the 5 bracket values are legal `column:` values outside the board."""
    assert set(BRACKET_COLUMNS) == EXPECTED_BRACKET_COLUMNS
    assert set(BRACKET_COLUMNS).isdisjoint(KANBAN_COLUMNS)


def test_legal_columns_is_board_plus_bracket_27_total():
    """3P-KAN-20: the LEGAL SET for a `column:` field is 22 board + 5 bracket = 27."""
    assert len(LEGAL_COLUMNS) == 27
    assert LEGAL_COLUMNS == frozenset(KANBAN_COLUMNS) | frozenset(BRACKET_COLUMNS)


def test_every_ratified_column_resolves_to_itself():
    """A ratified column value passes through resolve_column unchanged (identity)."""
    for column in KANBAN_COLUMNS:
        assert resolve_column(column) == column


@pytest.mark.parametrize(
    ("legacy", "expected"),
    [
        ("backlog", "backburner"),
        ("pending", "todo"),
        ("assigned", "dispatch"),
        ("in-progress", "dev"),
        ("in_progress", "dev"),
        ("review", "ai_review"),
        ("ai-review", "ai_review"),
        ("human-review", "human_review"),
        ("merge-release", "publish"),
        ("done", "complete"),
        ("completed", "complete"),
    ],
)
def test_legacy_status_migrates_to_ratified_column(legacy, expected):
    """Each legacy status maps deterministically to its ratified column."""
    assert resolve_column(legacy) == expected
    # And every migration target is itself a ratified column (no dangling map).
    assert expected in KANBAN_COLUMNS


def test_every_migration_target_is_ratified():
    """No entry in LEGACY_STATUS_MIGRATION points outside the ratified column set."""
    for src, dst in LEGACY_STATUS_MIGRATION.items():
        assert dst in KANBAN_COLUMNS, f"legacy {src!r} maps to non-ratified {dst!r}"


def test_unknown_status_raises_not_silent_fallback():
    """An unknown status raises ValueError instead of silently bucketing to a default (issue #27)."""
    with pytest.raises(ValueError, match="unknown kanban status"):
        resolve_column("totally-not-a-status")
