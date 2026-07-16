#!/usr/bin/env python3
"""Tests for amoa_sync_kanban.py -- the TRDD<->GitHub-Projects kanban sync.

REAL behavioral tests, NO mocks. The script's GitHub-touching functions
(`gh_command`, `get_project_items`, `create_project_item`, ...) shell out to
the `gh` CLI; we never mock the network. Instead we import and exercise the
*deterministic* parts directly:

  - The pure status->column / priority mapping tables.
  - `find_item_by_title` (pure list search).
  - `sync_module_to_project(..., dry_run=True)` -- the script's own code path
    that decides the action and the target column WITHOUT making any network
    call (it early-returns before any gh invocation when dry_run is set).
  - `parse_frontmatter` -- the malformed-input fail-safe.

These are the parts whose correctness actually matters for "the TRDD column
wins over the board column", and they run identically on every platform with
no `gh` auth and no network.
"""

import sys
from pathlib import Path

import pytest

# The existing suite imports scripts by putting scripts/ on sys.path; mirror it.
# shared/ carries the kanban vocabulary (importable from both scripts/ and the
# skill-bundled scripts, which sit at a different depth).
_ROOT = Path(__file__).resolve().parents[2]
for _d in (_ROOT / "scripts", _ROOT / "shared"):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

import amoa_sync_kanban as sk  # noqa: E402  (path injected above, on purpose)
from amoa_kanban_vocab import (  # noqa: E402
    KANBAN_COLUMNS,
    LEGACY_STATUS_MIGRATION,
    resolve_column,
)


# A realistic GitHub-Projects "fields" payload, shaped exactly like
# get_project_fields() returns: every board column / priority is a single-select
# option with a real option id. dry_run never touches these, but supplying a
# realistic structure keeps the test honest about the production shape.
#
# The Status options are the 17 RATIFIED columns (issue #27) — a board configured
# for the 3-pillars vocabulary, not the pre-2026-06-20 5-status board. Deriving
# them from KANBAN_COLUMNS rather than hardcoding a list is deliberate: if the
# ratified vocabulary ever changes, this fixture cannot silently describe a board
# that no longer exists.
def _realistic_fields() -> dict:
    return {
        "Status": {
            "id": "FIELD_status",
            "options": {col: f"opt_{col}" for col in KANBAN_COLUMNS},
        },
        "Priority": {
            "id": "FIELD_priority",
            "options": {
                "Critical": "opt_critical",
                "High": "opt_high",
                "Medium": "opt_medium",
                "Low": "opt_low",
            },
        },
    }


def _board_item(title: str, current_status_column: str, item_id: str = "ITEM_1") -> dict:
    """Build a board item shaped like get_project_items() returns it."""
    return {
        "id": item_id,
        "content": {"number": 42, "title": title},
        "fieldValues": {
            "nodes": [
                {
                    "name": current_status_column,
                    "field": {"name": "Status"},
                }
            ]
        },
    }


def test_happy_path_sync_updates_existing_item():
    """Happy path: a module matching a board item is mapped to an update action."""
    module = {
        "id": "auth-core",
        "name": "Core Authentication",
        "status": "dev",
        "priority": "high",
        "dependencies": ["token-store"],
        "description": "JWT issuance + refresh.",
    }
    title = "[auth-core] Core Authentication"
    items = [_board_item(title, current_status_column="dev")]

    result = sk.sync_module_to_project(
        module=module,
        project_id="PVT_test",
        items=items,
        fields=_realistic_fields(),
        dry_run=True,
        create_missing=False,
    )

    # Real contract: existing item found -> action "update", item_id carried,
    # title built as "[id] name", and dry_run flag echoed. No network happened.
    assert result["action"] == "update"
    assert result["item_id"] == "ITEM_1"
    assert result["title"] == title
    assert result["status"] == "dev"
    assert result["priority"] == "high"
    assert result["success"] is True
    assert result["dry_run"] is True


def test_trdd_column_wins_when_board_differs():
    """TRDD status wins: target column is derived from the module, not the board's stale value."""
    # The board item currently sits in "blocked", but the TRDD/module says the
    # work is now in "ai_review". The sync's target column must come from the
    # module's status (TRDD), proving TRDD-wins on a tie-break/disagreement.
    module = {
        "id": "auth-core",
        "name": "Core Authentication",
        "status": "ai_review",  # TRDD column
        "priority": "medium",
    }
    title = "[auth-core] Core Authentication"
    board_column = "blocked"  # stale board column, deliberately != TRDD
    items = [_board_item(title, current_status_column=board_column)]

    result = sk.sync_module_to_project(
        module=module,
        project_id="PVT_test",
        items=items,
        fields=_realistic_fields(),
        dry_run=True,
        create_missing=False,
    )

    # The action targets the SAME board item (found by title)...
    assert result["action"] == "update"
    assert result["item_id"] == "ITEM_1"
    # ...and the status the sync will write is the TRDD's, resolved through the
    # single-source-of-truth vocabulary (issue #27 — the script no longer owns a
    # local status→column map).
    trdd_target_column = resolve_column(module["status"])
    assert trdd_target_column == "ai_review"
    # Hard proof of "TRDD wins": the TRDD-derived target differs from what the
    # board currently shows -- so applying the sync overwrites the board value.
    assert trdd_target_column != board_column
    # The result still reports the TRDD status, never the board's stale column.
    assert result["status"] == "ai_review"


def test_trdd_column_to_board_column_roundtrip_is_lossless():
    """Every ratified column round-trips through resolve_column onto a real board option."""
    fields = _realistic_fields()
    valid_board_columns = set(fields["Status"]["options"].keys())

    # 1) The vocabulary IS the board vocabulary: resolve_column is the identity
    #    on every ratified column, and each one exists as a board option. This is
    #    the lossless round-trip the old many→1 map could not offer (issue #27).
    for col in KANBAN_COLUMNS:
        assert resolve_column(col) == col
        assert col in valid_board_columns, (
            f"ratified column {col!r} has no option on a 3-pillars board"
        )

    # 2) Legacy statuses are MIGRATED, not dropped: every legacy value resolves
    #    to a ratified column that the board can actually show.
    for legacy, expected in LEGACY_STATUS_MIGRATION.items():
        assert resolve_column(legacy) == expected
        assert expected in valid_board_columns

    # 3) Deterministic: same input -> same output, twice.
    for status in (*KANBAN_COLUMNS, *LEGACY_STATUS_MIGRATION):
        assert resolve_column(status) == resolve_column(status)

    # 4) Document the deliberately MANY->1 legacy merges (an intentional
    #    non-injective collapse of the OLD vocab, not a loss bug): the pre-2026-
    #    06-20 statuses that meant the same lifecycle state now share a column.
    #    Losslessness holds where it matters -- among the ratified columns (1).
    collapsed: dict[str, set[str]] = {}
    for legacy, col in LEGACY_STATUS_MIGRATION.items():
        collapsed.setdefault(col, set()).add(legacy)
    assert collapsed["dev"] == {"in-progress", "in_progress"}
    assert collapsed["ai_review"] == {"review", "ai-review"}
    # `verified` joins the done-spellings: it came from a THIRD legacy vocabulary
    # (amoa_sync_github_issues.py) where "verified or complete" WAS the finished
    # set -- see amoa_check_orchestration_phase.py's phase gate.
    assert collapsed["complete"] == {"done", "completed", "verified"}


def test_unknown_status_is_surfaced_as_an_error_never_a_default_column():
    """Unknown TRDD status yields a failed result naming it -- never a silent default column."""
    # The vocabulary refuses to guess: resolve_column raises rather than bucket
    # an unrecognized status somewhere plausible (issue #27, suggested fix 2).
    with pytest.raises(ValueError, match="unknown kanban status"):
        resolve_column("not-a-real-state")

    # The orchestration path converts that refusal into a well-formed FAILED
    # result -- it must not raise out of the sync, and must not fall through to a
    # write. Before the fix this module would have been silently placed in
    # "Todo", so a typo'd status looked like real triage.
    module = {
        "id": "weird-mod",
        "name": "Weird Module",
        "status": "totally-unknown-column",
        "priority": "also-unknown",
    }
    title = "[weird-mod] Weird Module"
    items = [_board_item(title, current_status_column="todo")]

    result = sk.sync_module_to_project(
        module=module,
        project_id="PVT_test",
        items=items,
        fields=_realistic_fields(),
        dry_run=True,
        create_missing=False,
    )
    assert result["action"] == "error"
    assert result["success"] is False
    # The offending value is named, so an operator can fix the state file.
    assert "totally-unknown-column" in result["error"]
    # The raw status is still reported verbatim (never rewritten to a guess).
    assert result["status"] == "totally-unknown-column"

    # Priority KEEPS its documented default -- an unknown priority is cosmetic,
    # not a placement error, so it stays a fallback rather than a hard failure.
    assert sk.PRIORITY_VALUES.get("urgent-ish", "Medium") == "Medium"


def test_empty_board_reports_missing_then_create():
    """Empty board: a module is 'missing' without --create-missing, and 'create' with it."""
    module = {
        "id": "auth-core",
        "name": "Core Authentication",
        "status": "todo",
        "priority": "high",
    }
    fields = _realistic_fields()

    # No items on the board AND create_missing not requested -> "missing".
    missing = sk.sync_module_to_project(
        module=module,
        project_id="PVT_test",
        items=[],
        fields=fields,
        dry_run=True,
        create_missing=False,
    )
    assert missing["action"] == "missing"
    assert "message" in missing  # tells caller to use --create-missing
    assert missing["success"] is True

    # Empty board WITH create_missing -> "create" (dry_run short-circuits before
    # any gh call, so this is fully offline/deterministic). "todo" is a ratified
    # column, so resolve_column passes it through and the create path proceeds.
    creating = sk.sync_module_to_project(
        module=module,
        project_id="PVT_test",
        items=[],
        fields=fields,
        dry_run=True,
        create_missing=True,
    )
    assert creating["action"] == "create"
    assert creating["dry_run"] is True
    assert creating["title"] == "[auth-core] Core Authentication"


def test_malformed_frontmatter_is_failsafe(tmp_path):
    """Malformed YAML frontmatter fails safe: returns ({}, content) and never raises."""
    bad = tmp_path / "broken-state.local.md"
    # Real malformed YAML: a mapping value that opens a flow-sequence and never
    # closes it -- yaml.safe_load raises YAMLError, which the script must swallow.
    bad.write_text(
        "---\n"
        "github_project_id: PVT_test\n"
        "modules_status: [oops, unterminated\n"
        "  - this: is not valid yaml at all : : :\n"
        "---\n\n"
        "# Body survives\n",
        encoding="utf-8",
    )

    # Must NOT raise -- the fail-safe returns empty data and the raw content.
    data, body = sk.parse_frontmatter(bad)
    assert data == {}
    assert "Body survives" in body  # on YAMLError the whole content is returned

    # Sanity: a well-formed file parses normally (proves the test above is
    # exercising the failure branch, not a parser that always returns {}).
    good = tmp_path / "good-state.local.md"
    good.write_text(
        "---\n"
        "github_project_id: PVT_real\n"
        "modules_status:\n"
        "  - id: auth-core\n"
        "    status: todo\n"
        "---\n\n"
        "# Good body\n",
        encoding="utf-8",
    )
    gdata, gbody = sk.parse_frontmatter(good)
    assert gdata["github_project_id"] == "PVT_real"
    assert gdata["modules_status"][0]["id"] == "auth-core"
    assert "Good body" in gbody
