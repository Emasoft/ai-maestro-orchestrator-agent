#!/usr/bin/env python3
"""Every `PRRD <id>` citation in prose must resolve to a rule that exists.

THE DEFECT THIS CATCHES (reported 2026-08-11 by the Claude developing
ai-maestro-programmer-agent, from their own G1.1→G1.2 bump). A pinned citation
`PRRD G1.1` dangles the moment the rule's text is revised, because a text edit
bumps the version. Their bump left **14** citations across skills, docs and tests
pointing at a version that no longer existed — and the full suite stayed green
through it, because no lint, no test and no plugin validator checks citation
integrity.

THIS REPO HAD THE MIRROR-IMAGE BUG, WHICH IS WORSE. On 2026-08-08 I edited G1.1's
text (removing a live `@owner` handle from the byline template) and did NOT bump
the version. Theirs dangles loudly — you look up G1.1 and find nothing. Mine
resolved perfectly, to text that had changed underneath every existing citation.
A stale pointer announces itself on the first lookup; a pointer to silently-mutated
content never does. Both are the same root cause: the version is a claim about the
text, and nothing was checking that the claim stayed true.

THE FIX SHAPE, which is why this test is small. The citation grammar already
defines a FLOATING form — `PRRD G1`, meaning "whatever rule 1 says now" — that
cannot dangle by construction. Living prose (a persona section, a skill template)
is a claim about the rule as it currently stands, so it floats. A PINNED version
is reserved for a claim genuinely about one revision. So the fix was mostly
deleting version numbers that were never load-bearing, not maintaining them.

TERMINAL TRDDs ARE EXEMPT, and the exemption is derived from `column:` rather than
a path list (their second finding, and it is the better half). A frozen card
records the rule AS IT STOOD when the work was done; renumbering its citations
makes the card lie about its own history. Keying on `column:` keeps the exemption
correct automatically as cards close — there is no list to maintain and no way for
a newly-closed card to be missed.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PRRD = REPO / "design" / "requirements" / "PRRD.md"

# A rule DEFINITION in the PRRD: `- **G1.2** — ...`. The letter is the current
# authority (G/S) and flips on promote/demote; the NUMBER is the identity and is
# never reused. So resolution is by number, and the letter is for human readers.
RULE_DEF = re.compile(r"^-\s+\*\*([GS])(\d+)\.(\d+)\*\*", re.MULTILINE)

# A CITATION in prose: `PRRD G1` (floating) or `PRRD G1.2` (pinned). The space is
# what makes it greppable and is required by the grammar.
CITATION = re.compile(r"\bPRRD\s+([GS])(\d+)(?:\.(\d+))?\b")

# Columns a card can hold and be FROZEN — its citations are a historical record.
TERMINAL_COLUMNS = frozenset(
    {"complete", "completed", "cancelled", "superseded", "published", "live", "refused"}
)


def current_rules() -> dict[str, int]:
    """Map rule NUMBER (as str) -> current version, from the PRRD definitions."""
    return {n: int(v) for _, n, v in RULE_DEF.findall(PRRD.read_text(encoding="utf-8"))}


def _is_frozen_card(path: Path) -> bool:
    """True for a TRDD whose `column:` is terminal — exempt, by state not by path."""
    if "design" not in path.parts or not path.name.startswith("TRDD-"):
        return False
    for line in path.read_text(encoding="utf-8").splitlines()[:40]:
        if line.startswith("column:"):
            return line.split(":", 1)[1].strip() in TERMINAL_COLUMNS
    return False


def _cited_files() -> list[Path]:
    """Every file whose prose could carry a citation — except this one.

    THIS FILE EXCLUDES ITSELF, and the reason generalizes: a detector that
    explains a rule must quote that rule's trigger text, and its fixtures must
    deliberately contain the very defect it detects — the exemption test below
    writes a card citing a stale `PRRD G1.1` precisely to prove the exemption
    fires. Scanning itself, this detector reports its own documentation and its
    own positive controls as findings. That is a permanent false positive, not an
    incidental one: it can never be fixed by editing the prose, because the prose
    has to say those words to do its job.

    The narrow self-exclusion is therefore correct, but it IS a hole — a genuine
    citation in this file goes unchecked. It is bounded to one file whose entire
    content is about citations, which is the smallest exclusion that resolves the
    self-reference.
    """
    out = [p for p in REPO.rglob("*.md") if p != PRRD]
    out += [p for p in REPO.rglob("*.py") if p != Path(__file__).resolve()]
    skip = (".trashcan", "worktrees", ".venv", "node_modules", ".git", "reports")
    return sorted(p for p in out if not any(s in p.parts for s in skip))


def dangling_citations() -> list[str]:
    rules = current_rules()
    bad: list[str] = []
    for path in _cited_files():
        if _is_frozen_card(path):
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for letter, num, ver in CITATION.findall(line):
                rel = f"{path.relative_to(REPO)}:{n}"
                if num not in rules:
                    bad.append(f"{rel}  PRRD {letter}{num} — NO SUCH RULE NUMBER")
                # `findall` yields '' — not None — for a non-participating optional
                # group, so a FLOATING `PRRD G1` arrives here as ver=''. Testing
                # `is not None` sent every floating citation into int('') and
                # crashed; truthiness is the correct test, and it is also the
                # semantically right one: no version means nothing to compare.
                elif ver and int(ver) != rules[num]:
                    bad.append(
                        f"{rel}  PRRD {letter}{num}.{ver} — rule {num} is now at "
                        f".{rules[num]}; pin is stale (or float it to `PRRD {letter}{num}`)"
                    )
    return bad


def test_prrd_has_parseable_rule_definitions():
    """Guards the guard: a PRRD this cannot parse would pass everything vacuously."""
    rules = current_rules()
    assert rules, (
        "parsed ZERO rule definitions out of the PRRD — every citation check below "
        "would then pass by having nothing to compare against"
    )


def test_no_dangling_prrd_citations():
    """Every cited rule number exists, and every pinned version is current."""
    bad = dangling_citations()
    assert not bad, (
        f"{len(bad)} dangling PRRD citation(s) — a reader following these looks up "
        "nothing, or worse, looks up text that changed underneath them:\n  "
        + "\n  ".join(bad)
        + "\n\nPrefer the FLOATING form `PRRD G<n>` for living prose; it cannot "
        "dangle. Pin a version only when the claim is about that revision."
    )


def test_terminal_cards_are_exempt_by_column_not_by_path(tmp_path):
    """A frozen card keeps its historical pin; a live card does not.

    Pinned by its own test because the exemption is the subtle half: derived from
    `column:`, it stays correct as cards close with nothing to maintain. Derived
    from a path list, it silently stops covering the next card that closes.
    """
    d = tmp_path / "design" / "tasks"
    d.mkdir(parents=True)
    frozen = d / "TRDD-20260101_000000+0000-AAAA1111-done.md"
    frozen.write_text("---\ncolumn: complete\n---\nPer PRRD G1.1 we did the thing.\n", encoding="utf-8")
    live = d / "TRDD-20260101_000000+0000-BBBB2222-open.md"
    live.write_text("---\ncolumn: dev\n---\nPer PRRD G1.1 we will do the thing.\n", encoding="utf-8")

    assert _is_frozen_card(frozen), "a `complete` card must be exempt"
    assert not _is_frozen_card(live), "a `dev` card must still be checked"


if __name__ == "__main__":
    print(f"rules: {current_rules()}")
    bad = dangling_citations()
    for b in bad:
        print("  " + b)
    print(f"\n{len(bad)} dangling citation(s)")
    sys.exit(1 if bad else 0)
