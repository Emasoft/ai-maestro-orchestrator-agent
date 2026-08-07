#!/usr/bin/env python3
"""Every `context: fork` skill must declare `background: false`.

Claude Code v2.1.218 changed forked skills to run in the BACKGROUND by default.
The official docs are explicit on both halves:

  skills.md:271 -- "`background` ... Only applies with `context: fork`. Set to
    `false` to wait for the forked subagent's result in the turn that invoked the
    skill ... Default: `true`. Requires Claude Code v2.1.218 or later."
  skills.md:573 -- "Before v2.1.218, forked skills always blocked the turn until
    they finished."

So every AMOA procedure skill silently changed meaning without its file changing.
There are TWO distinct losses, and the second is the one that is easy to miss:

  1. RETURN VALUE. A backgrounded skill hands back an agent handle, not the
     procedure. The invoking agent proceeds having received none of the
     instructions it asked for -- and no error is raised, so the failure is
     invisible at the call site.
  2. TOOLS. skills.md:582 -- "A backgrounded fork also runs with the narrower
     tool set that applies to background subagents: the skill's subagent is a
     regular agent type, so the exemption for subagents that fork the
     conversation doesn't cover it. If your skill's steps depend on a tool
     outside that set, set `background: false` to keep the full tool set."

AMOA's 21 forked skills are in-turn reference material ("Use when X ... Loaded by
ai-maestro-orchestrator-agent-main-agent"), not deferred long-running work, so
all 21 opt out. `context: fork` is kept deliberately -- forking is what keeps a
multi-kilobyte reference out of the main agent's context; only the backgrounding
was wrong.

This test exists because the frontmatter line looks redundant. It is not: delete
it and the skill reverts to background, losing both its return value and part of
its tool set, with nothing anywhere reporting a problem.
"""

import re
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[2] / "skills"


def _frontmatter(skill_md: Path) -> dict[str, str]:
    """Parse the top-level scalar keys of a SKILL.md YAML frontmatter block.

    Deliberately a flat scalar scan rather than a YAML load: the only keys this
    test reasons about are top-level scalars, and a hand-rolled scan keeps the
    check dependency-free and immune to a nested block (`metadata:`) shifting
    parse behavior.
    """
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    out: dict[str, str] = {}
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*?)\s*$", line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def _skill_files() -> list[Path]:
    files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    assert files, f"no SKILL.md found under {SKILLS_DIR} -- this test would pass vacuously"
    return files


def test_every_forked_skill_opts_out_of_backgrounding():
    """A `context: fork` skill without `background: false` silently loses its result AND tools."""
    offenders = []
    for f in _skill_files():
        fm = _frontmatter(f)
        if fm.get("context") == "fork" and fm.get("background") != "false":
            offenders.append(f"{f.parent.name} (background={fm.get('background', '<absent>')})")
    assert not offenders, (
        "forked skills missing `background: false` -- since CC 2.1.218 these run in the "
        "background, returning an agent handle instead of the procedure and running with a "
        "narrower tool set, both silently:\n  " + "\n  ".join(offenders)
    )


def test_background_key_only_appears_with_context_fork():
    """`background` is meaningless without `context: fork` -- a stray one implies a fork that isn't there."""
    strays = [
        f.parent.name
        for f in _skill_files()
        if "background" in _frontmatter(f) and _frontmatter(f).get("context") != "fork"
    ]
    assert not strays, (
        "`background` set on a non-forked skill (the docs scope it to `context: fork` only); "
        "it does nothing and misleads the next reader: " + ", ".join(strays)
    )


def test_fork_skill_count_is_covered():
    """Guards the guard: if the parse breaks, the checks above must not pass on zero skills."""
    forked = [f for f in _skill_files() if _frontmatter(f).get("context") == "fork"]
    assert forked, (
        "parsed zero forked skills -- either the frontmatter parser broke or the skills "
        "changed shape; both make the assertions above vacuous"
    )
