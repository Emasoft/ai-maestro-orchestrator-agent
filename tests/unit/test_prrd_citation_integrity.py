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


# Each rule's BODY hash, keyed by its full citation. Reported 2026-08-11 by the
# Claude developing ai-maestro-programmer-agent, who found this hole in their own
# guard after checking my report against their implementation instead of filing it
# as already-handled.
#
# WHY THE CITATION CHECK ALONE IS NOT ENOUGH. That check binds CITATION -> version.
# Nothing bound TEXT -> version, which is precisely the direction this repo failed
# in: on 2026-08-08 I edited G1.1's text and left the version at .1, so every
# citation still resolved, to changed content, and pytest / ruff / CPV --strict all
# stayed green. A guard that only catches the loud direction leaves the silent one
# open, and the silent one is the one that actually happened here.
#
# ON A LEGITIMATE EDIT this fails and PRINTS the hash to paste, so the cost is one
# line on a rule the author is already editing to bump. Do NOT "fix" a failure by
# regenerating the whole fixture blindly — that is the one move that converts this
# guard back into decoration.
RULE_BODY = re.compile(
    r"^-\s+\*\*([GS])(\d+)\.(\d+)\*\*\s*(.*?)(?=^-\s+\*\*[GS]\d+\.\d+\*\*|^##|\Z)",
    re.MULTILINE | re.DOTALL,
)
RULE_BODY_HASHES = {
    "G1.2": "aa0bcd191bbe5282",
    "S2.1": "aa7a8a2c67d6aa31",
    "S3.1": "8e16a7756bb4076c",
    "S4.1": "7cf7183d222c7ea3",
    "S5.1": "1d53473bbb0e3953",
    "S6.1": "d8a1f7bd6aae76c0",
    "S7.1": "86d1ad67ee3545ba",
    "S8.1": "62b8df094293cdf7",
}


def _rule_body_hashes() -> dict[str, str]:
    import hashlib

    out: dict[str, str] = {}
    for letter, num, ver, body in RULE_BODY.findall(PRRD.read_text(encoding="utf-8")):
        # Whitespace-normalized: a reflow is not a revision, and failing on one
        # would train the author to regenerate the fixture without reading it.
        norm = " ".join(body.split())
        out[f"{letter}{num}.{ver}"] = hashlib.sha256(norm.encode()).hexdigest()[:16]
    return out


def test_rule_text_matches_its_version():
    """A rule's text may not change without its version moving.

    Reports new / removed / mutated distinctly, because each needs a different fix:
    a NEW rule needs a fixture entry, a REMOVED one needs its entry dropped, and a
    MUTATED one needs a version bump (or, if the edit was accidental, a revert).
    """
    actual, expected = _rule_body_hashes(), RULE_BODY_HASHES
    new = sorted(set(actual) - set(expected))
    gone = sorted(set(expected) - set(actual))
    moved = sorted(k for k in set(actual) & set(expected) if actual[k] != expected[k])

    problems: list[str] = []
    if moved:
        problems.append(
            "TEXT CHANGED WITHOUT A VERSION BUMP — bump the rule, then set the hash:\n    "
            + "\n    ".join(f'"{k}": "{actual[k]}",  (fixture has {expected[k]})' for k in moved)
        )
    if new:
        problems.append(
            "NEW rule id(s) — add to RULE_BODY_HASHES:\n    "
            + "\n    ".join(f'"{k}": "{actual[k]}",' for k in new)
        )
    if gone:
        problems.append(
            "rule id(s) no longer in the PRRD — drop from RULE_BODY_HASHES: " + ", ".join(gone)
        )
    assert not problems, "\n\n".join(problems)


def test_rule_capture_spans_continuation_lines_but_ignores_reflow():
    """The two controls pull OPPOSITE ways, so one alone hides the other.

    Reported 2026-08-11 by the Claude developing ai-maestro-programmer-agent, who
    found their own guard carrying the defect class it exists to catch: `(.*)$`
    under `re.M` stops at the first newline, so a rule wrapped across lines was
    truncated to its FIRST line and an edit to any continuation line hashed
    IDENTICALLY. The guard passed while the rule's meaning changed.

    That is silent UNDER-coverage, and it is worse than a false positive: a false
    alarm announces itself, a guard that quietly stopped covering never does.

    THIS IMPLEMENTATION IS ALREADY CORRECT — `(.*?)` with DOTALL plus a lookahead
    to the next bullet/heading/EOF captures the whole BLOCK. This test exists
    because it was correct and UNPROVEN: the only control shipped was a first-line
    edit, which passes under both the correct regex and the broken one. So the
    property was one well-meaning "simplification" to `(.*)$` away from silently
    vanishing, with every test still green.

    Both directions are pinned together deliberately. Fixing a false positive by
    normalizing whitespace, and fixing under-coverage by capturing the block, pull
    against each other — a single control in either direction hides a regression in
    the other, which is precisely how the original passed review.
    """
    import hashlib

    def hashes(text: str) -> dict[str, str]:
        return {
            f"{a}{b}.{c}": hashlib.sha256(" ".join(d.split()).encode()).hexdigest()[:16]
            for a, b, c, d in RULE_BODY.findall(text)
        }

    base = (
        "## GOLDEN\n\n"
        "- **G1.1** — first line here\n"
        "  second line zeta continues\n"
        "  third line\n\n"
        "- **S2.1** — a different rule\n"
    )
    # A: meaning changed on a CONTINUATION line -> must be detected.
    changed = base.replace("zeta", "OMEGA")
    assert hashes(changed)["G1.1"] != hashes(base)["G1.1"], (
        "a word changed on a continuation line hashed IDENTICALLY — the capture is "
        "truncating at the first newline, so multi-line rules are silently uncovered"
    )
    # B: pure reflow, no meaning change -> must NOT be detected.
    reflowed = base.replace("first line here\n  second line", "first line here second line")
    assert hashes(reflowed)["G1.1"] == hashes(base)["G1.1"], (
        "a pure reflow changed the hash — that trains the author to regenerate the "
        "fixture without reading it, which turns this guard into decoration"
    )
    # And the block must stop at the next rule, not swallow it.
    bodies = [groups[3] for groups in RULE_BODY.findall(base) if "zeta" in groups[3]]
    assert "different rule" not in " ".join(bodies), (
        "the capture ran past its own rule into the next one"
    )

    # C: the broken shape must actually be broken. Without this, the two asserts
    # above pass under a regex that never had the property — they only prove the
    # CURRENT pattern behaves, not that the pattern is what makes it behave.
    broken = re.compile(r"^-\s+\*\*([GS])(\d+)\.(\d+)\*\*\s*(.*)$", re.MULTILINE)
    assert hashes(base)["G1.1"] != {
        f"{a}{b}.{c}": hashlib.sha256(" ".join(d.split()).encode()).hexdigest()[:16]
        for a, b, c, d in broken.findall(base)
    }["G1.1"], (
        "the block-capture and the first-line-only capture produced the SAME hash, "
        "so this fixture no longer distinguishes them and the controls above are "
        "vacuous — give the synthetic rule a real continuation line"
    )


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
