#!/usr/bin/env python3
"""No shipped template or prompt may contain a GitHub @mention.

WHY THIS EXISTS (orch#31). Our templates said `@maintainer` meaning our
governance ROLE. GitHub read it as a mention of the USER `maintainer` — Anton,
an account since 2009 with no connection to this project. The same held for
`manager` (Wolf Alexanyan, 2018), `orchestrator`, `integrator`, `architect`,
`reporter`, `developer-a`, `devops-team`, `backend-lead`, `sre-team` and more:
short role-shaped nouns are exactly the usernames claimed a decade ago. Our
governance vocabulary and GitHub's username namespace collide BY CONSTRUCTION.

THE DEFECT CLASS HAS NO LOCAL SYMPTOM. The damage lands entirely outside the
system — a stranger's notification inbox. Nothing observable from inside this
repo reports it, no test failed, no log recorded it. It ran for weeks and the
only detector was a courteous stranger asking us to stop. That is precisely why
this check has to be mechanical: there is no feedback signal to notice.

BACKTICKS DO NOT MAKE A TEMPLATE SAFE. GitHub does not linkify inside a code
span, so `@maintainer` in prose is inert. But a TEMPLATE is copied OUT of its
fence and pasted into a real comment, where the backticks are gone. The whole
point of these files is that an agent copies them, so a fenced template is the
MOST dangerous place for an `@`, not the safest.

WHAT IS AND IS NOT SCANNED. Only text that gets PUBLISHED: markdown prose plus
fenced blocks that are untagged or tagged markdown/text. A fence tagged with a
programming language is a CODE EXAMPLE — `@staticmethod`, `@NotNull`, `@main`
(Swift), `@rpath` (macOS linker), `@types/node` — where an `@` is correct and
means nothing to GitHub. Flagging those would make this check redden on correct
writing, and a check that cries wolf gets deleted, taking the real protection
with it.

THE FIX WHEN THIS FAILS is never to add a name to ALLOWED. Drop the `@`:
- naming a ROLE      -> `[maintainer]`, or bold/caps MAINTAINER. No sigil.
- a person PLACEHOLDER -> `@<username>`. A username may not begin with `<`, so
  the placeholder is provably inert until a real handle replaces it.
An `@` in published content should be a deliberate act of addressing a person,
never a side effect of naming a role.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Where an agent-copyable template or prompt can live.
#
# `design/requirements` was ADDED after this guard missed a real one. The PRRD's
# G1.1 rule carries the byline template every agent pastes into GitHub, and it
# shipped `@owner` — a real organization, registered 2021 — so the rule that exists
# to attribute authorship was paging a live org from every issue it produced. The
# guard was green throughout, because governance lived outside the tree it scanned.
#
# The lesson generalizes past this file: a template's DANGER follows where its text
# gets pasted, not which directory it happens to live in. Scoping a guard by
# directory silently assumes those coincide.
#
# NOT the whole of `design/`, deliberately. TRDDs legitimately write `@main` and
# `@v2.147.1` when recording a git-ref re-pin, and discuss `@mentions` by name;
# scanning them produced 13 false positives against 1 real finding, and a guard
# with a 13:1 noise ratio gets muted, taking the real finding with it.
SHIPPED_DIRS = ("skills", "commands", "agents", "docs", "design/requirements")
SHIPPED_FILES = ("README.md",)

# GitHub's real mention rule, as measured with `gh api markdown` and recorded in
# ~/.claude/rules/github-mentions.md — not as guessed:
#   `@janitor.` `(@janitor)` `@foo-bar`  -> PAGE (word boundary before @)
#   `x@janitor` `user@gmail.com`         -> plain (preceded by alphanumeric)
#   `@types/node` `actions/checkout@v4`  -> plain (a `/` follows, or @ is mid-word)
# The lookbehind encodes the word boundary; the `/` case is handled at the call
# site because a lookahead cannot express "not followed by / OR end-of-name".
MENTION = re.compile(r"(?<![A-Za-z0-9])@([A-Za-z0-9][A-Za-z0-9-]*)(?![A-Za-z0-9-])")

# A fence with one of these infostrings (or none at all) is PUBLISHED TEXT: the
# body is prose an agent pastes into an issue, PR, or comment. Anything else is
# a code example and is skipped — see the module docstring.
PUBLISHED_FENCES = {"", "markdown", "md", "text", "txt", "plaintext", "gfm", "none"}

# An inline code span, which GitHub does not linkify: `@rpath`, `@types`, `@main`.
# Stripped from PROSE only — never from inside a template fence. The asymmetry is
# deliberate and is the core of the threat model: in prose a backtick genuinely
# neutralizes the mention (this is the documented fix), but a TEMPLATE is written
# to be filled in and pasted, so it must carry no `@` at all regardless of how it
# is quoted here.
INLINE_CODE = re.compile(r"`+[^`]*`+")

# The ONLY permitted mention, and it is not a person: `@claude` is the documented
# trigger phrase for the Claude Code GitHub Action — a user types it in a comment
# to invoke the bot, so the sigil is load-bearing and the docs must show it.
# Do NOT extend this set to silence a failure; fix the text instead.
ALLOWED = frozenset({"claude"})


def _shipped_markdown() -> list[Path]:
    out: list[Path] = []
    for d in SHIPPED_DIRS:
        root = REPO / d
        if root.is_dir():
            out.extend(root.rglob("*.md"))
    out.extend(REPO / f for f in SHIPPED_FILES if (REPO / f).is_file())
    # `.trashcan/` holds safe-deleted history and worktrees hold branch copies;
    # neither ships, and scanning them would fail this test for text that was
    # already retired.
    return sorted(p for p in out if not any(x in p.parts for x in (".trashcan", "worktrees")))


def _published_lines(path: Path) -> list[tuple[int, str]]:
    """Lines of `path` that end up in published text, with their 1-based numbers.

    Tracks fenced blocks so a code example can be skipped by its infostring. The
    fence marker is matched at any indentation because templates routinely nest a
    fence inside a list item. Prose lines come back with inline code spans blanked
    out; template lines come back verbatim (see INLINE_CODE for why).
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[tuple[int, str]] = []
    fence: str | None = None  # the OPEN fence's infostring, or None outside one
    for n, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("```"):
            info = stripped[3:].strip().lower()
            if fence is None:
                fence = info.split()[0] if info else ""
            else:
                fence = None  # a closing fence carries no infostring
            continue
        if fence is None:
            out.append((n, INLINE_CODE.sub(" ", line)))
        elif fence in PUBLISHED_FENCES:
            out.append((n, line))
    return out


def _violations() -> list[str]:
    found: list[str] = []
    for path in _shipped_markdown():
        for n, line in _published_lines(path):
            for m in MENTION.finditer(line):
                if line[m.end() : m.end() + 1] == "/":
                    continue  # `@types/node` — a scoped package, not a mention
                if m.group(1).lower() in ALLOWED:
                    continue
                rel = path.relative_to(REPO)
                found.append(f"{rel}:{n}  @{m.group(1)}  |  {line.strip()[:88]}")
    return found


def test_no_at_mentions_in_shipped_text():
    """Every published template and prompt is free of GitHub @mentions."""
    found = _violations()
    assert not found, (
        f"{len(found)} @mention(s) in shipped text — each one notifies whoever owns "
        "that GitHub username:\n  " + "\n  ".join(found) + "\n\n"
        "Fix by DROPPING the @ (role -> [maintainer]; person -> @<username>). "
        "Never by adding the name to ALLOWED."
    )


def test_detector_matches_githubs_documented_behaviour():
    """The regex must agree with what GitHub actually linkifies.

    Pinned because the whole check rests on this one pattern: too loose and it
    reddens on `@staticmethod`, too tight and a real mention ships. Every row is
    a measured behaviour from ~/.claude/rules/github-mentions.md.
    """
    def pages(text: str) -> bool:
        for m in MENTION.finditer(text):
            if text[m.end() : m.end() + 1] == "/":
                continue
            return True
        return False

    assert pages("@janitor.")           # trailing punctuation still pages
    assert pages("(@janitor)")          # parenthesised still pages
    assert pages("@foo-bar")            # hyphens are legal in usernames
    assert pages("ping @maintainer -")  # mid-sentence

    assert not pages("x@janitor")            # preceded by alphanumeric
    assert not pages("user@gmail.com")       # an address does not page its domain
    assert not pages("actions/checkout@v4")  # version pin, @ is mid-word
    assert not pages("@types/node")          # scoped package
    assert not pages("@<username>")          # the inert placeholder this repo uses
    assert not pages("no sigil here")


def test_code_fences_are_excluded_but_template_fences_are_not(tmp_path):
    """A ```java example is skipped; an untagged template block is scanned.

    This asymmetry IS the design: the fenced template is the dangerous case
    (it gets pasted into a real comment), while the fenced code example is the
    safe one. A detector that treated all fences alike would be useless in one
    direction and intolerable in the other.
    """
    doc = tmp_path / "sample.md"
    doc.write_text(
        "```java\n@NotNull String s;\n```\n"
        "```\n@maintainer please review\n```\n",
        encoding="utf-8",
    )
    published = " ".join(line for _, line in _published_lines(doc))
    assert "@NotNull" not in published
    assert "@maintainer" in published


def test_backticks_neutralize_in_prose_but_not_inside_a_template(tmp_path):
    """`@rpath` in prose is inert; the same token inside a template is not.

    Prose is read where it sits, so a code span really does stop GitHub
    linkifying it — that is the documented fix, and flagging it would make this
    check redden on correct writing. A template is written to be COPIED into a
    comment, so it must carry no `@` at all: the check stays strict there
    precisely because that is the case that reached a stranger's inbox.
    """
    doc = tmp_path / "sample.md"
    doc.write_text(
        "Use `@rpath` and set the install name.\n"
        "```\nPing `@maintainer` for review\n```\n",
        encoding="utf-8",
    )
    lines = dict(_published_lines(doc))
    assert "@rpath" not in lines[1]      # prose: the code span disarms it
    assert "@maintainer" in lines[3]     # template: still flagged despite backticks


if __name__ == "__main__":
    bad = _violations()
    for line in bad:
        print(line)
    print(f"\n{len(bad)} violation(s)")
    sys.exit(1 if bad else 0)
