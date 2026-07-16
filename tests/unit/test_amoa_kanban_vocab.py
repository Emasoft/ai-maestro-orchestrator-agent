#!/usr/bin/env python3
"""Unit tests for the shared kanban vocabulary (scripts/amoa_kanban_vocab.py).

Guards issue #27: the plugin must speak the ratified 17-column 3-pillars
vocabulary from ONE source of truth, migrate every legacy status explicitly,
and refuse (not silently bucket) an unknown status.
"""

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from amoa_kanban_vocab import (  # noqa: E402
    KANBAN_COLUMNS,
    LEGACY_STATUS_MIGRATION,
    resolve_column,
)

# The ratified set, spelled out independently of the module so a drift in
# either direction fails this test.
EXPECTED_COLUMNS = {
    "backburner", "todo", "design", "dispatch", "dev", "testing",
    "ai_review", "human_review", "complete", "publish", "published",
    "deploy", "live", "live_auditing",
    "blocked", "failed", "superseded",
}


def test_exactly_the_17_ratified_columns():
    """KANBAN_COLUMNS is exactly the 17 ratified 3-pillars states, no more, no fewer."""
    assert len(KANBAN_COLUMNS) == 17
    assert set(KANBAN_COLUMNS) == EXPECTED_COLUMNS
    assert len(set(KANBAN_COLUMNS)) == 17  # no duplicates


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
