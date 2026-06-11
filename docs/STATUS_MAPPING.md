# AMOA Status Mapping: TRDD column ↔ 8-column GitHub board

> **Version**: 2.0.0 | **Last Updated**: 2026-06-11

## Overview

A task has two state views, and they are **not peers**:

1. **The TRDD `column:` pipeline is the AUTHORITATIVE lifecycle** — the single
   source of truth for where a task is (see `docs/FULL_PROJECT_WORKFLOW.md` §
   "Board Reconciliation" and `~/.claude/rules/trdd-design-tasks.md`).
2. **The 8-column GitHub Projects board is a lossless VISUAL PROJECTION** of that
   pipeline — fewer columns for human glance-ability, but no information is lost
   because the board carries a `trdd-column:` custom field holding the **exact**
   TRDD `column:` value.

This document defines the **lossless, bidirectional** mapping between the
authoritative TRDD `column:` and the board (board column + `trdd-column:` field).
It supersedes the old "AMOA ↔ AI Maestro 5-status" mapping, which collapsed
distinct lifecycle states onto one status (lossy). **Nothing collapses here.**

## Lossless mapping (authoritative TRDD `column:` ↔ board)

| TRDD `column:` (authoritative) | Board column (projection) | `trdd-column:` field (exact) | Flip owner |
|---|---|---|---|
| `backburner` | Backlog | `backburner` | AMOA |
| `todo` | Todo | `todo` | AMOA |
| `design` | Todo | `design` | AMOA (assigns AMAA) |
| `dispatch` | Todo | `dispatch` | AMOA |
| `dev` | In Progress | `dev` | AMOA |
| `testing` | In Progress | `testing` | AMOA |
| `ai_review` | AI Review | `ai_review` | AMIA |
| `human_review` | Human Review | `human_review` | AMIA sets / USER decides (via AMCOS → AMAMA) |
| `complete` | Merge/Release | `complete` | AMIA |
| `publish` | Merge/Release | `publish` | AMIA |
| `deploy` | Merge/Release | `deploy` | AMIA |
| `published` | Done | `published` | AMIA |
| `live` | Done | `live` | AMIA |
| `live_auditing` | Done | `live_auditing` | AMIA |
| `blocked` | Blocked | `blocked` | column owner at time of block |
| `failed` | Blocked | `failed` | column owner at time of block |
| `superseded` | Done | `superseded` | ARCHITECT (design split) |

> **Why lossless:** the board column alone is a lossy summary (e.g. three TRDD
> columns — `published`, `live`, `live_auditing` — share the "Done" board
> column), but the `trdd-column:` field on each board item preserves the exact
> authoritative value, so the round-trip is exact.

## Forward direction (TRDD `column:` → board)

Whoever owns a TRDD transition edits the TRDD `column:` **first**, then projects
it onto the board: set the board column **and** write the precise TRDD value into
the `trdd-column:` field, both derived from the mapping table above. The board
column is **never** set independently of `trdd-column:`.

## Reverse direction (board → TRDD `column:`) — unambiguous

Read the `trdd-column:` field; it **is** the authoritative `column:` value. The
board column is redundant (derivable from `trdd-column:`). Two tasks sharing one
board column are distinguished by their `trdd-column:`:

| Board column | Possible `trdd-column:` values (read the field to disambiguate) |
|---|---|
| Backlog | `backburner` |
| Todo | `todo`, `design`, `dispatch` |
| In Progress | `dev`, `testing` |
| AI Review | `ai_review` |
| Human Review | `human_review` |
| Merge/Release | `complete`, `publish`, `deploy` |
| Done | `published`, `live`, `live_auditing`, `superseded` |
| Blocked | `blocked`, `failed` (read `pre-block-column:` to know where `blocked` restores to) |

There is **no disambiguation guesswork** and **no metadata heuristic** — the
exact value is stored, not inferred.

## Sync rules and tie-break

- **TRDD is written first; the board is updated to match.** The TRDD `column:`
  edit precedes the board projection in every transition.
- **Tie-break: the TRDD wins.** If the board and the TRDD ever disagree (e.g. a
  stale board after a missed sync), the TRDD `column:` is authoritative.
  Reconcile by re-deriving the board column + `trdd-column:` from the TRDD's
  `column:` — never by editing the TRDD to match a stale board.
- **Ownership is preserved across the projection.** The *Flip owner* in the
  mapping table matches who owns the corresponding TRDD transition: AMOA owns
  through the pre-PR green-light (`backburner`…`testing`); AMIA owns
  `ai_review` → `complete`/`publish`/`deploy` → `published`/`live` (the
  Merge/Release and Done projections). **AMOA never moves a task into Done.**

## No lossy mappings (changed in 2.0.0)

The previous version (1.6.0) collapsed AI Review + Human Review → `review`,
Merge/Release + Done → `completed`, and Blocked → `in_progress` (lossy in 3
pairs). That collapse is **removed**. The `trdd-column:` field carries the exact
state, so every distinct TRDD column round-trips through the board without loss.
This aligns with `docs/FULL_PROJECT_WORKFLOW.md` § "Board Reconciliation".

---

**Changelog (2.0.0, 2026-06-11)**: Re-keyed the mapping on the authoritative TRDD
`column:` pipeline; made the board a lossless projection via the `trdd-column:`
custom field (no column collapses); removed the lossy 5-status AI Maestro
collapse; added sync rules + TRDD-wins tie-break; aligned with the
FULL_PROJECT_WORKFLOW Board Reconciliation section.
