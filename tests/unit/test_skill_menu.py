#!/usr/bin/env python3
"""The main agent's skill menu must list every shipped skill, and only those.

RP-SKILL-MENU-01 (role-plugins-spec 1.1.0, ai-maestro `governance-rules`): "the
main agent carries a compact skill menu -- one line per shipped skill, name +
when-to-reach-for-it, updated in the same change that touches any skill."

WHY A TEST AND NOT A CONVENTION. Before this, the menu listed 5 of 23 skills. It
had been correct when written; skills were added afterwards and nobody updated it.
That is the failure mode a convention cannot prevent, because a stale menu has NO
LOCAL SYMPTOM -- nothing errors, no output changes, and the agent cannot miss what
it was never told exists. It just quietly stops reaching for 18 skills. The same
shape as the @mention defect in test_no_github_mentions.py: invisible from inside,
so the only detector that will ever exist is a mechanical one.

BOTH DIRECTIONS MATTER, for different reasons:
  - A skill missing FROM the menu is dead weight -- shipped, documented, never
    loaded, because the agent has no way to learn it is there.
  - A menu row with no skill behind it is worse: the agent tries to load it, the
    Skill tool fails, and the failure surfaces mid-task in whatever the agent was
    actually doing rather than here.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO / "skills"
MAIN_AGENT = REPO / "agents" / "ai-maestro-orchestrator-agent-main-agent.md"

# A menu row: `| \`skill-name\` | when to reach for it |`. Anchored on the leading
# pipe + backticked name so ordinary prose that merely mentions a skill in running
# text is not mistaken for a menu entry.
MENU_ROW = re.compile(r"^\|\s*`([a-z0-9-]+)`\s*\|\s*(.+?)\s*\|\s*$")

MENU_HEADING = "## Skill Menu"


def _menu_section(text: str) -> list[str]:
    """The lines of the `## Skill Menu` section, up to the next `## ` heading.

    Scoping matters: the file carries OTHER two-column tables of backticked
    identifiers (the LLM-Externalizer tool list, for one). A whole-file scan reads
    `| \\`chat\\` | Summarize files ... |` as a menu row and reports a dangling
    skill that was never claimed to be one — a false failure pointing at innocent
    documentation, which is how a check gets disabled instead of heeded.
    """
    lines = text.splitlines()
    try:
        start = next(i for i, ln in enumerate(lines) if ln.startswith(MENU_HEADING))
    except StopIteration:
        raise AssertionError(
            f"{MAIN_AGENT.name} has no '{MENU_HEADING}' section — RP-SKILL-MENU-01 "
            "requires the main agent to carry one"
        ) from None
    out: list[str] = []
    for ln in lines[start + 1 :]:
        if ln.startswith("## "):
            break
        out.append(ln)
    return out


def shipped_skills() -> set[str]:
    """Every skill this plugin ships, by directory name.

    Directory name rather than the frontmatter `name:` because the directory is
    what `Skill(plugin:<name>)` resolves against — so a menu row that matches the
    frontmatter but not the directory would still fail to load at runtime.
    """
    return {p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md")}


def menu_entries() -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in _menu_section(MAIN_AGENT.read_text(encoding="utf-8")):
        m = MENU_ROW.match(line.strip())
        if m and m.group(1) != "Skill":  # skip the header row
            entries[m.group(1)] = m.group(2)
    return entries


def test_menu_lists_every_shipped_skill():
    """No skill ships without a menu row telling the agent it exists."""
    missing = sorted(shipped_skills() - set(menu_entries()))
    assert not missing, (
        f"{len(missing)} shipped skill(s) absent from the main agent's menu — the "
        "agent has no way to discover them, so they are dead weight:\n  "
        + "\n  ".join(missing)
    )


def test_menu_has_no_row_without_a_skill():
    """No menu row points at a skill that is not shipped."""
    dangling = sorted(set(menu_entries()) - shipped_skills())
    assert not dangling, (
        f"{len(dangling)} menu row(s) name a skill that does not exist — loading one "
        "fails at runtime, mid-task, far from this file:\n  " + "\n  ".join(dangling)
    )


def test_every_row_says_when_to_reach_for_it():
    """A name alone is not a menu — the row must carry usable guidance.

    The spec's wording is "name + when-to-reach-for-it". A row that restates the
    name, or gives a two-word gesture, leaves the agent exactly as unable to choose
    as no row at all, while looking like the requirement was met.
    """
    thin = sorted(
        name
        for name, guidance in menu_entries().items()
        if len(guidance) < 20 or guidance.strip("`* ").lower() == name.replace("-", " ")
    )
    assert not thin, "menu row(s) with no usable when-to-reach-for-it: " + ", ".join(thin)


def test_main_agent_does_not_pin_a_model():
    """RP-MODEL-01 (ai-maestro#136): a main agent must OMIT `model:`.

    ROLE is orthogonal to MODEL. A pin spends the operator's budget on the
    plugin author's behalf and degrades silently where an org restricts models —
    the agent does not fail, it just runs as something the operator did not choose
    and cannot see. Omitting the key inherits the session model, which is the
    operator's actual decision.
    """
    assert not _model_pins([MAIN_AGENT]), (
        "main agent pins a model; RP-MODEL-01 requires the key be omitted so the "
        "operator's session model is inherited"
    )


def test_no_subagent_pins_a_model():
    """The same rule for subagents — where AMOA was actually drifting.

    role-plugins-spec 1.1.0 states as settled fact that "subagents already omit
    `model:` everywhere". That was FALSE here: all five AMOA subagents pinned
    `opus`, including `amoa-task-summarizer`, whose entire job is condensing
    verbose output into a minimal report — a bounded mechanical task carrying the
    fleet's most expensive per-token rate.

    RP-MODEL-01 is written about MAIN agents, so this test extends it rather than
    quoting it. The rationale transfers without modification (a pin spends the
    operator's budget and degrades silently under an org model restriction), and
    it matches CPV's CA-04 cache-warmth invariant: an agent inherits the session
    model, and the DISPATCH SITE overrides when a task genuinely needs a different
    tier. Encoding the tier in the persona puts that decision in the wrong place —
    the author's, permanently, instead of the caller's, per call.
    """
    pinned = _model_pins(sorted((REPO / "agents").glob("*.md")))
    assert not pinned, "agent(s) pin a model: " + ", ".join(pinned)


def _model_pins(paths: list[Path]) -> list[str]:
    """Names of agent files carrying a top-level `model:` key in frontmatter."""
    out: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        block = text[3 : end if end != -1 else len(text)]
        for line in block.splitlines():
            if line.startswith("model:"):
                out.append(f"{path.name} ({line.strip()})")
    return out


if __name__ == "__main__":
    entries, shipped = menu_entries(), shipped_skills()
    print(f"menu rows: {len(entries)}   shipped skills: {len(shipped)}")
    print(f"missing from menu: {sorted(shipped - set(entries)) or 'none'}")
    print(f"dangling rows:     {sorted(set(entries) - shipped) or 'none'}")
    sys.exit(0 if entries.keys() == shipped else 1)
