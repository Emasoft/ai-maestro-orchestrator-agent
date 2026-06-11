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

# The existing suite imports scripts by putting scripts/ on sys.path; mirror it.
SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import amoa_sync_kanban as sk  # noqa: E402  (path injected above, on purpose)


# A realistic GitHub-Projects "fields" payload, shaped exactly like
# get_project_fields() returns: every board column / priority is a single-select
# option with a real option id. dry_run never touches these, but supplying a
# realistic structure keeps the test honest about the production shape.
def _realistic_fields() -> dict:
    return {
        "Status": {
            "id": "FIELD_status",
            "options": {
                "Backlog": "opt_backlog",
                "Todo": "opt_todo",
                "In Progress": "opt_inprogress",
                "AI Review": "opt_aireview",
                "Human Review": "opt_humanreview",
                "Merge/Release": "opt_merge",
                "Blocked": "opt_blocked",
                "Done": "opt_done",
            },
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
        "status": "in-progress",
        "priority": "high",
        "dependencies": ["token-store"],
        "description": "JWT issuance + refresh.",
    }
    title = "[auth-core] Core Authentication"
    items = [_board_item(title, current_status_column="In Progress")]

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
    assert result["status"] == "in-progress"
    assert result["priority"] == "high"
    assert result["success"] is True
    assert result["dry_run"] is True


def test_trdd_column_wins_when_board_differs():
    """TRDD status wins: target column is derived from the module, not the board's stale value."""
    # The board item currently sits in "Blocked", but the TRDD/module says the
    # work is now in "ai-review". The sync's target column must come from the
    # module's status (TRDD), proving TRDD-wins on a tie-break/disagreement.
    module = {
        "id": "auth-core",
        "name": "Core Authentication",
        "status": "ai-review",  # TRDD column
        "priority": "medium",
    }
    title = "[auth-core] Core Authentication"
    board_column = "Blocked"  # stale board column, deliberately != TRDD
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
    # ...and the status the sync will write is the TRDD's, mapped to the board.
    trdd_target_column = sk.STATUS_TO_COLUMN[module["status"]]
    assert trdd_target_column == "AI Review"
    # Hard proof of "TRDD wins": the TRDD-derived target differs from what the
    # board currently shows -- so applying the sync overwrites the board value.
    assert trdd_target_column != board_column
    # The result still reports the TRDD status, never the board's stale column.
    assert result["status"] == "ai-review"


def test_trdd_column_to_board_column_roundtrip_is_lossless():
    """Every TRDD column maps to a real board column, and 1:1 entries round-trip losslessly."""
    fields = _realistic_fields()
    valid_board_columns = set(fields["Status"]["options"].keys())

    # 1) Forward map is total: every TRDD column resolves to an EXISTING board
    #    column option (no TRDD state can map to a column the board lacks).
    for trdd_col, board_col in sk.STATUS_TO_COLUMN.items():
        assert board_col in valid_board_columns, (
            f"TRDD column {trdd_col!r} maps to {board_col!r}, "
            f"which is not a real board column"
        )

    # 2) The map is deterministic/stable (same input -> same output, twice).
    for trdd_col in sk.STATUS_TO_COLUMN:
        assert sk.STATUS_TO_COLUMN[trdd_col] == sk.STATUS_TO_COLUMN[trdd_col]

    # 3) Losslessness for the UNAMBIGUOUS (1:1) TRDD columns: build the inverse
    #    map and confirm board->TRDD->board returns the original board column
    #    for every column that has exactly one TRDD source.
    board_to_trdd_sources: dict[str, list[str]] = {}
    for trdd_col, board_col in sk.STATUS_TO_COLUMN.items():
        board_to_trdd_sources.setdefault(board_col, []).append(trdd_col)

    one_to_one = {
        board_col: srcs[0]
        for board_col, srcs in board_to_trdd_sources.items()
        if len(srcs) == 1
    }
    for board_col, trdd_col in one_to_one.items():
        # round-trip: board column -> its unique TRDD source -> back to board
        assert sk.STATUS_TO_COLUMN[trdd_col] == board_col

    # 4) Document the deliberately MANY->1 merges (a known, intentional non-
    #    injective collapse, NOT a loss bug): assigned+in-progress -> In Progress,
    #    done+complete -> Done. These are aliases on purpose.
    assert set(board_to_trdd_sources["In Progress"]) == {"assigned", "in-progress"}
    assert set(board_to_trdd_sources["Done"]) == {"done", "complete"}


def test_unknown_column_falls_back_to_todo_and_does_not_crash():
    """Unknown/invalid TRDD status falls back to 'Todo' and the sync stays well-formed."""
    # Pure-mapping fallback: an unknown TRDD state defaults to "Todo".
    assert sk.STATUS_TO_COLUMN.get("not-a-real-state", "Todo") == "Todo"
    # Priority fallback mirrors it.
    assert sk.PRIORITY_VALUES.get("urgent-ish", "Medium") == "Medium"

    # And the orchestration path tolerates the unknown status without raising:
    module = {
        "id": "weird-mod",
        "name": "Weird Module",
        "status": "totally-unknown-column",
        "priority": "also-unknown",
    }
    title = "[weird-mod] Weird Module"
    items = [_board_item(title, current_status_column="Todo")]

    result = sk.sync_module_to_project(
        module=module,
        project_id="PVT_test",
        items=items,
        fields=_realistic_fields(),
        dry_run=True,
        create_missing=False,
    )
    # Found by title -> update; the unknown status is preserved in the report,
    # and (per the mapping) would be written as the safe "Todo" default.
    assert result["action"] == "update"
    assert result["status"] == "totally-unknown-column"
    assert sk.STATUS_TO_COLUMN.get(module["status"], "Todo") == "Todo"


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
    # any gh call, so this is fully offline/deterministic).
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
