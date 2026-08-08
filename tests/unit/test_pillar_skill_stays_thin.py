#!/usr/bin/env python3
"""`amoa-prrd-trdd-kanban` must stay a POLICY layer, never a mechanics copy.

THE RULING THIS ENCODES (MANAGER, 2026-08-08, orch#25). The issue said "retire the
redundant per-plugin pillar skill". The skill was rewired instead of deleted, and
MANAGER ruled the rewire stands: *"'retire the redundant skill' was my word for
'kill the reimplementation', and I wrote the wrong one. The skill is no longer
redundant; it was made non-redundant by the change."*

R25.1 prohibits a per-plugin REIMPLEMENTATION of pillar mechanics. It has never
prohibited ORCH-specific POLICY — the priority ranking with oldest-breaks-ties, the
`backburner` promotion gate, which fields ORCH owns as single writer, the NPT/EHT
collision protocol. No other skill can hold that, and moving it into the persona
would bloat a document loaded on every turn with procedure needed only when ORCH is
actually scheduling.

WHY A TEST AND NOT A NOTE. A thin layer thickens. Each addition looks locally
reasonable — restate one field so the reader need not look it up, inline one enum
for convenience — and the reimplementation reassembles a line at a time, with no
single commit where it was wrong. MANAGER gave a bar precisely so this would be
checkable rather than a vibe, so it belongs in the build, not in a memory:

    "Re-retire if the layer thickens back — concretely, if the skill ever restates
     pillar MECHANICS rather than pointing at them. `trdd-id:` / `approval-tier` /
     the 17-column vocabulary listing must stay at 0 occurrences, and `ama-*`
     references must outnumber mechanics markers. Today: 23 vs 0."

If this test fails, the honest response is to DELETE the restated mechanics, not to
relax the threshold. A failure means the original "retire it" ask has become correct
again.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skills" / "amoa-prrd-trdd-kanban" / "SKILL.md"

# Restating any of these means the skill has started carrying the pillar SCHEMA or
# LIFECYCLE itself — the thing R25.1 forbids — rather than delegating to `ama-*`.
#
# `approval-tier` is doubly disqualifying: it is both a mechanics restatement AND a
# RETIRED vocabulary (superseded by `min-approval-requirement`), so a copy here
# would keep enforcing a shape the governance layer has already moved off.
MECHANICS_MARKERS = (
    r"\btrdd-id:",           # the TRDD frontmatter schema
    r"\bapproval-tier\b",    # retired approval vocabulary
    r"\bmin-approval-requirement:",  # the schema of the CURRENT one, equally not ours
    r"\bnpt:\s*\[",          # frontmatter list syntax = schema, not policy
    r"\beht:\s*\[",
)

# The 17-column vocabulary lives in `shared/amoa_kanban_vocab.py` and `ama-*`.
# Naming the two or three columns ORCH OWNS is policy and stays legal; ENUMERATING
# the vocabulary is a copy of it. The line-level threshold distinguishes the two.
KANBAN_COLUMNS_SAMPLE = (
    "backburner", "todo", "design", "dispatch", "dev", "testing", "ai_review",
    "human_review", "complete", "publish", "published", "deploy", "live",
    "live_auditing", "blocked", "failed", "superseded",
)
MAX_COLUMNS_ON_ONE_LINE = 6

AMA_REF = re.compile(r"\bama-(?:prrd|trdd|kanban|proposal|unblock)[a-z-]*")


def _text() -> str:
    return SKILL.read_text(encoding="utf-8")


def test_skill_restates_no_pillar_mechanics():
    """Zero occurrences of the pillar schema / retired approval vocabulary."""
    text = _text()
    hits: list[str] = []
    for pattern in MECHANICS_MARKERS:
        for n, line in enumerate(text.splitlines(), 1):
            if re.search(pattern, line):
                hits.append(f"{SKILL.name}:{n}  /{pattern}/  {line.strip()[:70]}")
    assert not hits, (
        "the pillar skill has started restating mechanics instead of delegating:\n  "
        + "\n  ".join(hits)
        + "\n\nDelete the restatement and point at the `ama-*` skill that owns it. "
        "Do NOT relax this check — a failure means orch#25's original "
        "'retire the redundant skill' has become the right ask again."
    )


def test_skill_does_not_enumerate_the_column_vocabulary():
    """Naming the columns ORCH owns is policy; listing the vocabulary is a copy."""
    offenders = []
    for n, line in enumerate(_text().splitlines(), 1):
        found = sum(1 for c in KANBAN_COLUMNS_SAMPLE if re.search(rf"\b{c}\b", line))
        if found > MAX_COLUMNS_ON_ONE_LINE:
            offenders.append(f"{SKILL.name}:{n}  {found} columns  {line.strip()[:60]}")
    assert not offenders, (
        "the 17-column vocabulary is being enumerated here; it belongs to "
        "shared/amoa_kanban_vocab.py and the ama-* skills:\n  " + "\n  ".join(offenders)
    )


def test_delegations_outnumber_mechanics():
    """`ama-*` references must dominate. MANAGER measured 23 vs 0 at the ruling.

    The ratio is the real signal: a skill can be free of the specific markers above
    and still have quietly become a procedure manual. If delegations stop dominating,
    the layer is thickening whether or not it tripped a named pattern.
    """
    text = _text()
    delegations = len(AMA_REF.findall(text))
    assert delegations >= 10, (
        f"only {delegations} ama-* delegations left in the pillar skill — it is "
        "supposed to be a thin layer that POINTS at the core skills. Too few "
        "delegations means the mechanics moved back in here."
    )


if __name__ == "__main__":
    t = _text()
    print(f"ama-* delegations: {len(AMA_REF.findall(t))}")
    print(f"mechanics markers: {sum(len(re.findall(p, t)) for p in MECHANICS_MARKERS)}")
    sys.exit(0)
