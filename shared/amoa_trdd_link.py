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
import subprocess
from pathlib import Path

# A CITATION in prose: `TRDD-<id8>`, 8 chars of base36. Case-INSENSITIVE because
# legacy lowercase ids stay permanently valid (the spec mandates `find -iname`),
# while the canonical WRITTEN form is uppercase. The trailing boundary stops
# `TRDD-ABCD1234EXTRA` matching a truncated prefix and resolving to another card.
TRDD_ID_RE = re.compile(r"TRDD-([A-Za-z0-9]{8})(?![A-Za-z0-9])", re.IGNORECASE)

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

# 3P-ZON-05 (amended 2026-08-18): ONLY these terminal values may enter
# design/archived/, and every one archives AS ITSELF — no rewrite on the way in.
ARCHIVE_ELIGIBLE_COLUMNS: frozenset[str] = frozenset(
    {"complete", "completed", "cancelled", "superseded", "published", "live"}
)


def extract_trdd_id(text: str) -> str | None:
    """Pull the canonical `TRDD-<id8>` out of an issue title or body.

    Returns the id UPPERCASED (the canonical written form) so callers compare
    and write one spelling regardless of how it was typed. Returns None when the
    text carries no id — a card with no TRDD behind it is legitimate, and the
    caller decides whether that is acceptable for its operation.
    """
    m = TRDD_ID_RE.search(text or "")
    return m.group(1).upper() if m else None


def zone_for_column(column: str, release_via: str | None = None) -> str:
    """The `design/<zone>/` folder a card in `column` belongs in.

    `complete` is release-via-DEPENDENT (3P-ZON-05 as amended 2026-08-18): with
    `release-via: none` it is the card's terminal column and archives AS ITSELF,
    while a publish/deploy card still has the release lane ahead of it
    (complete -> publish|deploy, Part B2) and must stay in tasks/. An unknown
    release_via (None) is treated as NOT-terminal — the conservative answer,
    because un-archiving is one `git mv` while a card wrongly pulled out of the
    release lane stalls the whole publish.
    """
    if column == "complete":
        return "archived" if release_via == "none" else DEFAULT_ZONE
    return _ZONE_BY_COLUMN.get(column, DEFAULT_ZONE)


def crosses_zone(
    from_column: str | None, to_column: str, release_via: str | None = None
) -> bool:
    """True when this transition moves the file between design/ folders."""
    if from_column is None:
        return False
    return zone_for_column(from_column, release_via) != zone_for_column(to_column, release_via)


def read_release_via(trdd_path: Path) -> str:
    """Read the card's `release-via:` (absent defaults to `none` per the TRDD spec)."""
    m = re.search(
        r"^release-via:\s*(\S+)", trdd_path.read_text(encoding="utf-8"), re.MULTILINE
    )
    return m.group(1) if m else "none"


def mark_archived(trdd_path: Path, outcome_line: str) -> bool:
    """The 3P-ZON-12 archival writes set_column does not do.

    Adds `archived: true` beside the terminal `column:` (idempotent) and appends
    the OUTCOME/WHY line to the body — the spec requires all three archival
    writes (column+updated via set_column, this flag, and the body record), and
    the pre-2026-08-19 path performed only the first (TRDD-8DH44UXH AC5).
    """
    text = trdd_path.read_text(encoding="utf-8")
    changed = False
    if re.search(r"^archived:\s*true\s*$", text, re.MULTILINE) is None:
        new_text, n = re.subn(
            r"(?m)^(column:[^\n]*)$", r"\1\narchived: true", text, count=1
        )
        if n:
            text, changed = new_text, True
    if outcome_line and outcome_line not in text:
        text = text.rstrip("\n") + f"\n\n{outcome_line}\n"
        changed = True
    if changed:
        trdd_path.write_text(text, encoding="utf-8")
    return changed


def find_trdd(trdd_id: str, design_root: Path) -> Path | None:
    """Locate a TRDD by id via `trddgrep show --porcelain` (TRDD-8DH44UXH F1).

    Porcelain contract (ai-maestro TRDD-IPSNDKGM, additive-only field order):
    one TAB-separated record per line, ABSOLUTE PATH first, title last. The
    lookup is case-insensitive in trddgrep itself, matching the `find -iname`
    rule the TRDD spec mandates.

    Exit trichotomy, preserved on purpose: 0 found -> the path; 1 no such id ->
    None (a missing card is a legitimate answer the caller decides about);
    2 / missing binary / timeout -> RAISE. Collapsing could-not-run into
    not-found is the exact conflation the trichotomy exists to prevent — a
    broken lookup would silently report every card as missing, and the
    write-through would then declare board and SSOT "out of step" forever.
    """
    try:
        result = subprocess.run(
            ["trddgrep", "show", trdd_id, "--porcelain", "--design-dir", str(design_root)],
            capture_output=True, text=True, timeout=60,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "trddgrep not on PATH — TRDD lookup COULD NOT RUN (exit-2 class)"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            "trddgrep show timed out — TRDD lookup COULD NOT RUN (exit-2 class)"
        ) from exc
    if result.returncode == 0:
        first_record = result.stdout.splitlines()[0]
        return Path(first_record.split("\t", 1)[0])
    if result.returncode == 1:
        return None
    raise RuntimeError(
        f"trddgrep show {trdd_id} could not run (exit {result.returncode}): "
        f"{result.stderr.strip() or result.stdout.strip()}"
    )


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
