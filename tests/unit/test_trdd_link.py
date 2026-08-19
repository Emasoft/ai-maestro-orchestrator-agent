#!/usr/bin/env python3
"""Issue↔TRDD linkage and the gated TRDD write-through.

Closes F2/F4 of TRDD-704ZBCR8: the alignment contract requires every board
mutation to land in the TRDD file AND its folder, not only in a mirror.

No mocks — these operate on real TRDD files written to tmp_path, so the
frontmatter handling is exercised against the actual on-disk shape.
"""

import os
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared"))

from amoa_trdd_link import (  # noqa: E402
    add_external_ref,
    crosses_zone,
    extract_trdd_id,
    find_trdd,
    read_column,
    set_column,
    zone_for_column,
)

FRONTMATTER = """---
trdd-id: {id}
title: A card
column: {column}
created: 2026-08-01T10:00:00+0200
updated: 2026-08-01T10:00:00+0200
external-refs: [{refs}]
---

# A card

Body text that must survive every write untouched.
"""


def _write(tmp: Path, zone: str, tid: str, column: str, refs: str = "") -> Path:
    folder = tmp / "design" / zone
    folder.mkdir(parents=True, exist_ok=True)
    p = folder / f"TRDD-20260801_100000+0200-{tid}-a-card.md"
    p.write_text(FRONTMATTER.format(id=tid, column=column, refs=refs), encoding="utf-8")
    return p


# ── id extraction ──

@pytest.mark.parametrize("text,want", [
    ("TRDD-M7BZ4X1Q", "M7BZ4X1Q"),
    ("Fix the thing (TRDD-M7BZ4X1Q)", "M7BZ4X1Q"),
    ("**TRDD:** TRDD-M7BZ4X1Q\n\nbody", "M7BZ4X1Q"),
    ("trdd-m7bz4x1q lowercase legacy", "M7BZ4X1Q"),  # canonicalized on read
    ("no id here", None),
    ("", None),
])
def test_extract_trdd_id(text, want):
    assert extract_trdd_id(text) == want


def test_extract_rejects_a_longer_run_rather_than_truncating():
    """`TRDD-ABCD1234EXTRA` must not silently resolve to `ABCD1234`.

    A truncating match would link the board to the WRONG card — the failure
    would be a successful-looking write to someone else's TRDD.
    """
    assert extract_trdd_id("TRDD-ABCD1234EXTRA") is None


# ── zones ──

def test_zone_mapping_and_crossing():
    assert zone_for_column("dev") == "tasks"
    assert zone_for_column("proposal") == "proposals"
    assert zone_for_column("completed") == "archived"
    assert zone_for_column("refused") == "refused"
    assert crosses_zone("dev", "testing") is False
    assert crosses_zone("dev", "completed") is True
    assert crosses_zone(None, "completed") is False  # unknown origin: no move claimed


def test_failed_stays_on_the_board():
    """`failed` is retryable, not terminal — archiving it would hide live work."""
    assert zone_for_column("failed") == "tasks"
    assert crosses_zone("dev", "failed") is False


# ── lookup ──
#
# find_trdd shells to `trddgrep show --porcelain` (TRDD-8DH44UXH F1), so the
# happy-path tests need the real CLI and SKIP where it is not installed (CI
# runners). That is the trichotomy's legitimate-deferral shape, not a hole:
# the missing-binary RAISE branch below runs EVERYWHERE, so an environment
# without the CLI still proves the failure mode it will actually exhibit.

_HAVE_TRDDGREP = shutil.which("trddgrep") is not None
needs_trddgrep = pytest.mark.skipif(not _HAVE_TRDDGREP, reason="trddgrep not installed")


def test_find_trdd_missing_binary_raises_not_none(tmp_path, monkeypatch):
    """No trddgrep on PATH must RAISE, never return None.

    Collapsing could-not-run into not-found would make a broken lookup report
    every card as missing — the exact conflation the exit trichotomy forbids.
    """
    _write(tmp_path, "tasks", "AAAA1111", "dev")
    monkeypatch.setitem(os.environ, "PATH", str(tmp_path / "empty-bin"))
    with pytest.raises(RuntimeError, match="COULD NOT RUN"):
        find_trdd("AAAA1111", tmp_path / "design")


@needs_trddgrep
def test_find_trdd_across_zones_and_case(tmp_path):
    _write(tmp_path, "tasks", "AAAA1111", "dev")
    arch = _write(tmp_path, "archived", "BBBB2222", "completed")
    root = tmp_path / "design"
    assert find_trdd("BBBB2222", root) == arch
    assert find_trdd("bbbb2222", root) == arch  # case-insensitive, per the -iname rule
    assert find_trdd("CCCC3333", root) is None


@needs_trddgrep
def test_find_trdd_does_not_mistake_the_timestamp_for_the_id(tmp_path):
    """The filename's first 8-char run is the DATE, not the id.

    A lookup built on the prose-citation regex returns `20260801` here and
    resolves every card to the wrong file — a write-through would then edit
    somebody else's TRDD and report success.
    """
    p = _write(tmp_path, "tasks", "AAAA1111", "dev")
    root = tmp_path / "design"
    assert find_trdd("AAAA1111", root) == p
    assert find_trdd("20260801", root) is None


@needs_trddgrep
def test_find_trdd_survives_a_negative_utc_offset(tmp_path):
    """A host west of Greenwich puts a dash INSIDE the timestamp.

    `TRDD-20260801_100000-0500-AAAA1111-...` — any implementation that splits
    the filename on "-" shifts a field here and fails only for those hosts,
    which is the kind of bug that reaches production because the author's
    machine is east of Greenwich.
    """
    folder = tmp_path / "design" / "tasks"
    folder.mkdir(parents=True)
    p = folder / "TRDD-20260801_100000-0500-AAAA1111-a-card.md"
    p.write_text(FRONTMATTER.format(id="AAAA1111", column="dev", refs=""), encoding="utf-8")
    assert find_trdd("AAAA1111", tmp_path / "design") == p


# ── write-through ──

def test_set_column_writes_and_bumps_updated(tmp_path):
    p = _write(tmp_path, "tasks", "AAAA1111", "dev")
    assert set_column(p, "testing", "2026-08-08T12:00:00+0200") is True
    assert read_column(p) == "testing"
    text = p.read_text()
    assert "updated: 2026-08-08T12:00:00+0200" in text
    assert "created: 2026-08-01T10:00:00+0200" in text  # created must NOT move


def test_set_column_preserves_the_body_and_other_fields(tmp_path):
    p = _write(tmp_path, "tasks", "AAAA1111", "dev")
    before = p.read_text()
    set_column(p, "testing", "2026-08-08T12:00:00+0200")
    after = p.read_text()
    assert "Body text that must survive every write untouched." in after
    assert "trdd-id: AAAA1111" in after
    assert "title: A card" in after
    # exactly two lines differ: column and updated
    diff = [(a, b) for a, b in zip(before.splitlines(), after.splitlines()) if a != b]
    assert len(diff) == 2, diff


def test_set_column_is_idempotent(tmp_path):
    p = _write(tmp_path, "tasks", "AAAA1111", "dev")
    set_column(p, "testing", "2026-08-08T12:00:00+0200")
    assert set_column(p, "testing", "2026-08-08T12:00:00+0200") is False


def test_set_column_refuses_a_malformed_trdd(tmp_path):
    """A TRDD with no `column:` is malformed — surface it, don't invent the field."""
    p = tmp_path / "broken.md"
    p.write_text("---\ntrdd-id: X\n---\nbody\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no `column:` field"):
        set_column(p, "dev", "2026-08-08T12:00:00+0200")

    p2 = tmp_path / "nofm.md"
    p2.write_text("no frontmatter at all\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no frontmatter"):
        set_column(p2, "dev", "2026-08-08T12:00:00+0200")


# ── the back-link ──

def test_add_external_ref_is_idempotent(tmp_path):
    p = _write(tmp_path, "tasks", "AAAA1111", "dev")
    url = "https://github.com/o/r/issues/7"
    assert add_external_ref(p, url) is True
    assert url in p.read_text()
    # A write-through runs on EVERY board move; a non-idempotent link would
    # accumulate one duplicate per move and become unreadable within a day.
    assert add_external_ref(p, url) is False
    assert p.read_text().count(url) == 1


def test_add_external_ref_keeps_existing_entries(tmp_path):
    p = _write(tmp_path, "tasks", "AAAA1111", "dev", refs="ai-maestro#1")
    add_external_ref(p, "https://github.com/o/r/issues/7")
    line = [x for x in p.read_text().splitlines() if x.startswith("external-refs:")][0]
    assert "ai-maestro#1" in line
    assert "issues/7" in line


# ── the issue side of the link ──

@needs_trddgrep
def test_issue_title_citation_round_trips(tmp_path):
    """The id written into a title must be the id read back out of it.

    This is the whole linkage in one assertion: create_task_issue appends
    `(TRDD-<id8>)` to the title, and the write-through resolves the card by
    parsing that same title. If the two ever disagree the board silently stops
    updating the SSOT, which is the failure F2 exists to close.
    """
    title = "Wire the retry backoff (TRDD-M7BZ4X1Q)"
    assert extract_trdd_id(title) == "M7BZ4X1Q"

    p = _write(tmp_path, "tasks", "M7BZ4X1Q", "dev")
    assert find_trdd(extract_trdd_id(title), tmp_path / "design") == p


def test_complete_zones_by_release_via():
    """3P-ZON-05 amended: complete archives AS ITSELF only for release-via none."""
    from amoa_trdd_link import zone_for_column
    assert zone_for_column("complete", "none") == "archived"
    assert zone_for_column("complete", "publish") == "tasks"
    assert zone_for_column("complete", "deploy") == "tasks"
    assert zone_for_column("complete", None) == "tasks"  # unknown = conservative
