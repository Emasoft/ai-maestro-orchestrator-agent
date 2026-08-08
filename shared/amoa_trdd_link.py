#!/usr/bin/env python3
"""Issue↔TRDD linkage and the TRDD write-through — the SSOT half of the board.

The alignment contract (ai-maestro `rules/aimaestro/aimaestro-kanban-multiagent.md`,
"Orchestrator-plugin alignment") requires the ORCHESTRATOR to "treat the TRDD
corpus as the SSOT — every board mutation lands in the TRDD file (and its
folder), not only in a mirror" and to "round-trip GitHub-Project mirror changes
back to the TRDDs".

WHY THIS MODULE EXISTS SEPARATELY FROM THE VOCABULARY. `amoa_kanban_vocab.py`
carries a MANAGER ruling (orch#27): `resolve_column` is MIRROR-ONLY, and *"if
resolve_column is ever wired into a path that ORIGINATES a TRDD column write, a
legacy value would land a card on a MANAGER-gated column with no MANAGER stamp.
If you add such a path: GATE THE PATH, not this map."* That is a build-condition,
not a prohibition — confirmed by the ai-maestro server 2026-08-08 — and the gate
(`assert_orchestrator_may_transition`) shipped first in `e237dfe`. This module is
the path it was gating. The map stays mirror-only; every ORIGINATING write goes
through the gate, then through here.

LINKAGE SHAPE — RATIFIED, NOT INVENTED. The issue carries the greppable
`TRDD-<id8>` in its TITLE (preferred: a title survives body edits), or a
`**TRDD:** TRDD-<id8>` body marker. The TRDD frontmatter carries `external-refs:`
with the issue URL. `<id8>` is 8 chars of UPPERCASE base36.
"""

from __future__ import annotations

import re
from pathlib import Path

# A CITATION in prose: `TRDD-<id8>`, 8 chars of base36. Case-INSENSITIVE because
# legacy lowercase ids stay permanently valid (the spec mandates `find -iname`),
# while the canonical WRITTEN form is uppercase. The trailing boundary stops
# `TRDD-ABCD1234EXTRA` matching a truncated prefix and resolving to another card.
TRDD_ID_RE = re.compile(r"TRDD-([A-Za-z0-9]{8})(?![A-Za-z0-9])", re.IGNORECASE)

# A FILENAME: `TRDD-<YYYYMMDD_HHMMSS±HHMM>-<id8>-<slug>.md`. This needs its own
# pattern and must NOT reuse TRDD_ID_RE: the citation regex matches the first
# 8-char run after `TRDD-`, which in a filename is the DATE (`20260801`), so a
# lookup built on it resolves every card to the wrong file.
#
# Splitting on "-" does not work either — a NEGATIVE UTC offset puts a dash
# inside the timestamp (`...+0200` vs `...-0500`), shifting the field positions
# for exactly the hosts west of Greenwich. Anchoring on the timestamp's shape is
# the only form that survives both.
TRDD_FILENAME_RE = re.compile(
    r"^TRDD-\d{8}_\d{6}[+-]\d{4}-([A-Za-z0-9]{8})(?:-|\.md$)", re.IGNORECASE
)

# Which lifecycle folder each column belongs in. A move that crosses these zones
# needs a `git mv`, not just a frontmatter edit — the folder IS part of the
# state, which is why the contract says "the TRDD file (and its folder)".
#
# `failed` is deliberately absent from the archived set: it is a RETRYABLE state
# that stays in design/tasks/, and archiving it would take a live card off the
# board while it still needs work.
_ZONE_BY_COLUMN: dict[str, str] = {
    "proposal": "proposals",
    "refused": "refused",
    "completed": "archived",
    "cancelled": "archived",
    "superseded": "archived",
    "published": "archived",
    "live": "archived",
}
DEFAULT_ZONE = "tasks"


def extract_trdd_id(text: str) -> str | None:
    """Pull the canonical `TRDD-<id8>` out of an issue title or body.

    Returns the id UPPERCASED (the canonical written form) so callers compare
    and write one spelling regardless of how it was typed. Returns None when the
    text carries no id — a card with no TRDD behind it is legitimate, and the
    caller decides whether that is acceptable for its operation.
    """
    m = TRDD_ID_RE.search(text or "")
    return m.group(1).upper() if m else None


def zone_for_column(column: str) -> str:
    """The `design/<zone>/` folder a card in `column` belongs in."""
    return _ZONE_BY_COLUMN.get(column, DEFAULT_ZONE)


def crosses_zone(from_column: str | None, to_column: str) -> bool:
    """True when this transition moves the file between design/ folders."""
    if from_column is None:
        return False
    return zone_for_column(from_column) != zone_for_column(to_column)


def find_trdd(trdd_id: str, design_root: Path) -> Path | None:
    """Locate a TRDD by id across every lifecycle folder.

    Case-INSENSITIVE on the id, matching the `find -iname` rule the TRDD spec
    mandates: legacy lowercase ids remain valid forever, so a case-sensitive
    lookup silently reports a real card as missing.
    """
    want = trdd_id.upper()
    for zone in ("tasks", "proposals", "archived", "refused"):
        folder = design_root / zone
        if not folder.is_dir():
            continue
        for path in folder.glob("TRDD-*.md"):
            m = TRDD_FILENAME_RE.match(path.name)
            if m and m.group(1).upper() == want:
                return path
    return None


def read_column(trdd_path: Path) -> str | None:
    """Read a TRDD's current `column:` without a YAML round-trip.

    Line-oriented on purpose: a parse-and-redump would reorder keys, restyle
    lists, and strip the comments the corpus relies on. The frontmatter is
    grep-first by design (one field per line), so a line read is both sufficient
    and lossless.
    """
    for line in _frontmatter_lines(trdd_path):
        if line.startswith("column:"):
            return line.split(":", 1)[1].strip()
    return None


def set_column(trdd_path: Path, column: str, updated_iso: str) -> bool:
    """Write `column:` and bump `updated:` in place. Returns False if unchanged.

    Rewrites only the two lines it owns and leaves every other byte alone, for
    the same reason read_column is line-oriented. Refuses rather than inventing
    a field: a TRDD with no `column:` is malformed, and adding one here would
    paper over that instead of surfacing it.
    """
    text = trdd_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{trdd_path} has no frontmatter block")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError(f"{trdd_path} has an unterminated frontmatter block")

    head, body = text[: end + 1], text[end + 1 :]
    lines = head.splitlines()
    saw_column = False
    out: list[str] = []
    for line in lines:
        if line.startswith("column:"):
            saw_column = True
            out.append(f"column: {column}")
        elif line.startswith("updated:"):
            out.append(f"updated: {updated_iso}")
        else:
            out.append(line)
    if not saw_column:
        raise ValueError(f"{trdd_path} frontmatter has no `column:` field")

    new_head = "\n".join(out) + "\n"
    if new_head == head:
        return False
    trdd_path.write_text(new_head + body, encoding="utf-8")
    return True


def add_external_ref(trdd_path: Path, url: str) -> bool:
    """Append `url` to the frontmatter `external-refs:` flow list, idempotently.

    This is the TRDD half of the bidirectional link. Idempotent because a
    write-through runs on every board move, and a link that accumulated a
    duplicate per move would make the field unreadable within a day.
    """
    text = trdd_path.read_text(encoding="utf-8")
    end = text.find("\n---", 3)
    if not text.startswith("---") or end == -1:
        raise ValueError(f"{trdd_path} has no usable frontmatter block")
    head, body = text[: end + 1], text[end + 1 :]

    out: list[str] = []
    changed = False
    for line in head.splitlines():
        if line.startswith("external-refs:"):
            if url in line:
                return False  # already linked
            inner = line.split(":", 1)[1].strip()
            items = [i for i in inner.strip("[]").split(",") if i.strip()]
            items.append(f" {url}")
            out.append("external-refs: [" + ",".join(i.strip() for i in items).replace(",", ", ") + "]")
            changed = True
        else:
            out.append(line)
    if not changed:
        return False
    trdd_path.write_text("\n".join(out) + "\n" + body, encoding="utf-8")
    return True


def _frontmatter_lines(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return []
    end = text.find("\n---", 3)
    return text[3 : end if end != -1 else len(text)].splitlines()
