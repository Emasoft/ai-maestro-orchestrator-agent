#!/usr/bin/env python3
"""
amoa_kanban_vocab.py — the SINGLE source of truth for this plugin's kanban vocabulary.

Per the USER-ratified 3-pillars kanban-supremacy rule (ai-maestro
TRDD-…-YUGDER9D, 2026-07-07) and GOVERNANCE-RULES R25 (Three-Pillars Task
System), the TRDD `column:` state machine IS the universal kanban vocabulary for
every surface — 1:1 with the ai-maestro server TaskStatus default (types/task.ts,
redeployed 2026-06-20, ai-maestro#43). Every consumer in this plugin (the GitHub
Project sync, the kanban manager, the aimaestro sync, the module-management
github_sync) aligns TO this vocabulary and imports it from here; none defines its
own status→column map. (issue #27)

Before the fix, each consumer carried its own pre-2026-06-20 5-status map
(`backlog/todo/assigned/in-progress/... → "Backlog"/"In Progress"/...`) and fell
back silently to `"Todo"` on any unknown status, splitting the kanban pillar into
two incompatible vocabularies. Keeping the vocabulary in ONE module makes that
drift structurally impossible.
"""

# The 17 ratified columns == TRDD `column:` states == ai-maestro server
# TaskStatus values. Tuple order is the lifecycle order (the 3 exception states
# follow the 14 lifecycle states), so iterating this reproduces the board order.
KANBAN_COLUMNS: tuple[str, ...] = (
    # 14 lifecycle states
    "backburner",
    "todo",
    "design",
    "dispatch",
    "dev",
    "testing",
    "ai_review",
    "human_review",
    "complete",
    "publish",
    "published",
    "deploy",
    "live",
    "live_auditing",
    # 3 exception states
    "blocked",
    "failed",
    "superseded",
)

# Fast membership set for resolve_column (defined before the function so it is
# resolvable at call time regardless of import order).
_COLUMN_SET: frozenset[str] = frozenset(KANBAN_COLUMNS)

# Explicit migration from every legacy status value this plugin ever emitted
# (the pre-2026-06-20 5-status vocab + its punctuation variants) to the ratified
# column. This REPLACES the old silent `.get(status, "Todo")` fallback (issue
# #27, suggested fix 2): a legacy value maps deterministically; a genuinely
# unknown value is surfaced by resolve_column, never quietly bucketed into a
# default column.
#
# Mapping notes (maintainer's call — issue #27 flags "low confidence on exact
# shape … re-verify against amp-kanban before publishing"):
#   - assigned → dispatch: "assignee set" is the dispatch state (a TRDD is
#     dispatched to an assignee); active implementation is `dev`. The old vocab
#     conflated both as "In Progress".
#   - merge-release → publish: the old generic "Merge/Release" column maps to
#     the tool-release lane `publish` (services use `deploy`); AMOA-orchestrated
#     work is overwhelmingly publish-lane.
LEGACY_STATUS_MIGRATION: dict[str, str] = {
    "backlog": "backburner",
    "pending": "todo",
    "assigned": "dispatch",
    "in-progress": "dev",
    "in_progress": "dev",
    "review": "ai_review",
    "ai-review": "ai_review",
    "human-review": "human_review",
    "merge-release": "publish",
    "done": "complete",
    "completed": "complete",
}


def resolve_column(status: str) -> str:
    """Resolve a module/task status to its ratified kanban column.

    Accepts either a ratified column value (returned unchanged) or a known
    legacy value (migrated via LEGACY_STATUS_MIGRATION). Raises ValueError on an
    unknown status so the caller surfaces the data error instead of silently
    mis-placing the item in a default column (issue #27 — no silent "Todo"
    fallback).

    Args:
        status: the raw status string read from orchestration state.

    Returns:
        One of KANBAN_COLUMNS.

    Raises:
        ValueError: status is neither a ratified column nor a known legacy value.
    """
    if status in _COLUMN_SET:
        return status
    migrated = LEGACY_STATUS_MIGRATION.get(status)
    if migrated is not None:
        return migrated
    raise ValueError(
        f"unknown kanban status {status!r}: not a ratified column "
        f"({', '.join(KANBAN_COLUMNS)}) nor a known legacy value "
        f"({', '.join(sorted(LEGACY_STATUS_MIGRATION))})"
    )
