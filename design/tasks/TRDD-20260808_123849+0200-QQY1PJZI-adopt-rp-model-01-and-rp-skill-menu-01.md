---
trdd-id: QQY1PJZI
title: Adopt RP-MODEL-01 (drop the model pin) and RP-SKILL-MENU-01 (full skill menu) from role-plugins-spec 1.1.0
column: ai_review
created: 2026-08-08T12:38:49+0200
updated: 2026-08-08T15:00:41+0200
current-owner: ai-maestro-orchestrator-agent
assignee: ai-maestro-orchestrator-agent
task-type: refactor
scope: project
project-id: ai-maestro-orchestrator-agent
min-approval-requirement: none
severity: medium
blocked-by: []
relevant-rules: []
external-refs: [ai-maestro#136, TRDD-TYB3Q1NJ, TRDD-0FCR6KOW]
release-via: publish
---

# Adopt RP-MODEL-01 and RP-SKILL-MENU-01

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative) — 2026-08-08

**Both clauses implemented and guarded; folded into the same release as the kanban
write-through work, as the hub asked (not shipped twice).**

**Artifact adopted against:** `Emasoft/ai-maestro`, branch `governance-rules`,
`design/specs/role-plugins-spec.md` **spec-version 1.1.0**, **blob `bb99e877`**
(18,832 bytes), read 2026-08-08T12:35+0200.

**Why the blob sha and not the branch tip.** The hub's message named tip
`eaf609ad`. Measured minutes apart, the branch was `20b5f792` (10:33Z) and then
`46cf3ace` — the tip is a moving target on an actively-developed branch, and none
of the three matched. The BLOB sha pins the exact bytes I read and stays valid
across every later commit that does not touch this file, so it is the checkable
citation. Recorded rather than silently substituted: a citation nobody can verify
is worse than a mismatch somebody can.

## The two clauses, verified first-hand

- **`RP-MODEL-01`** (RULED 2026-08-08, ai-maestro#136, closes `TRDD-TYB3Q1NJ`):
  role-plugin **MAIN agents OMIT `model:`**, same as subagents. ROLE is orthogonal
  to model: the pin lets the role author spend the **operator's** budget, is the
  only spelling that **silently degrades** under an org model restriction, and
  conflicts with CPV's CA-04 cache-warmth default. Migration is on-next-release.
- **`RP-SKILL-MENU-01`** (added 2026-08-08, `TRDD-0FCR6KOW`): every main agent whose
  plugin ships skills carries a **compact skill menu** — one line per shipped skill,
  name + when to reach for it. Subagents exempt. **A stale menu is worse than none**;
  it must be updated in the same change that adds, renames, or removes a skill, and
  a publish gate SHOULD compare menu entries against shipped `SKILL.md` count.

## What was actually wrong here — one correction back to the spec

**RP-MODEL-01: the spec's premise was false for AMOA.** The clause reasons from
"subagents already omit `model:` everywhere (that half of the old clause was true
and stands)". Measured in this tree: **all five AMOA subagents pinned `model: opus`**
— `amoa-team-orchestrator`, `amoa-checklist-compiler`, `amoa-experimenter`,
`amoa-task-summarizer`, `amoa-docker-container-expert`. So the fleet-wide claim does
not hold, and the drift the ruling targets was **6 files here, not 1**.

`amoa-task-summarizer` is the sharpest case: an agent whose entire job is condensing
verbose output into a minimal report, pinned to the most expensive per-token rate in
the fleet. That is the exact anti-pattern the ruling's own rationale describes.

The ruling is written about MAIN agents, so dropping the five subagent pins **extends**
it rather than quoting it. Done deliberately, because the rationale transfers without
modification and because CA-04 says the same thing: an agent inherits the session
model and the **dispatch site** overrides per call. Encoding the tier in the persona
puts that decision in the author's hands permanently instead of the caller's, per call.

**RP-SKILL-MENU-01: "partial" was accurate.** The main agent listed **5 of 23** skills
under "Then read the relevant skill documentation". The list had been correct when
written; 18 skills were added afterwards and nobody updated it.

## Implementation

- `agents/ai-maestro-orchestrator-agent-main-agent.md` — `model: opus` dropped; the
  5-item partial list replaced by a **23-row menu** (`| skill | reach for it when |`),
  with an explicit note that the two communication skills are the pair most often
  confused (`amoa-developer-communication` when a **person** reads it,
  `amoa-remote-agent-coordinator` when an **agent** does).
- Five subagent personas — `model: opus` dropped.
- `tests/unit/test_skill_menu.py` — the publish gate the clause asks for, plus the
  model-pin guard.

## The guard, and why it is a test rather than a convention

A stale menu has **no local symptom**: nothing errors, no output changes, and the
agent cannot miss what it was never told exists — it just quietly stops reaching for
18 skills. Same defect class as the `@mention` bug closed today in `TRDD-7MGYSHMN`:
invisible from inside the system, so the only detector that will ever exist is a
mechanical one.

Both directions are checked, for different reasons: a skill **missing from** the menu
is dead weight (shipped, documented, never loaded); a menu row with **no skill behind
it** is worse, because the load fails mid-task, far from this file.

`_menu_section()` scopes the parse to the `## Skill Menu` heading. That is not
tidiness — the first version scanned the whole file and read the LLM-Externalizer
tool table's `` | `chat` | Summarize files… | `` as a menu row, reporting a dangling
skill nobody had claimed. A check that fails on innocent documentation gets disabled
rather than heeded.

## Verification

- Suite **191 passed** (was 186 before this card, 182 before today).
- `grep -rn '^model:' agents/` → no matches.
- Menu: 23 rows, 23 shipped skills, 0 missing, 0 dangling.
- **Mutation-verified**: deleting the `amoa-module-sync` row fails
  `test_menu_lists_every_shipped_skill`; restoring it passes.
- ruff + mypy clean.

## Acceptance criteria

- [x] `model:` absent from the main agent (RP-MODEL-01)
- [x] `model:` absent from all five subagents (extension, with the reason recorded)
- [x] Menu lists all 23 shipped skills with when-to-reach-for-it guidance
- [x] Publish gate compares menu entries against shipped `SKILL.md` count
- [x] Mutation-verified that both guards guard rather than decorate
- [x] Released — closure record below
- [x] Correction reported to the hub (subagents were NOT omitting; 6 files, not 1)

## Closure record — as the hub asked (release tag + sha + pasted timestamps)

| item | value |
|---|---|
| Release tag | `v1.11.0` |
| Release created | 2026-08-08T10:53:18Z (**12:53:18+0200** local) |
| Merge commit on `main` | `c58e501` (PR #32) |
| `main` tip at publish | `9a72807` |
| Spec adopted | role-plugins-spec **1.1.0**, blob `bb99e877` (18,832 bytes) |
| Spec read at | 2026-08-08T12:35+0200 |
| Adoption commit | `ebe3202` |

**Verified AT THE TAG**, not in the working tree: `git grep '^model:' v1.11.0 --
agents/` → **0 matches**; the menu in `v1.11.0:agents/…-main-agent.md` carries
**23 rows** against 23 shipped skills; both guards present in the published tree.

**Column stopped at `ai_review`.** `transition_authority("testing", "complete")`
returns `manager` — the gate this plugin ships (F3 of TRDD-704ZBCR8) refuses to let
an ORCHESTRATOR mark its own card complete. Awaiting a MANAGER stamp rather than
routing around the gate I built.

## Approval log

- 2026-08-08T12:38:49+0200 — Tier 0 (`min-approval-requirement: none`): adoption of a
  ratified spec clause inside this plugin's own tree, no baseline deviation. Requested
  by the ai-maestro hub via AMP, citing role-plugins-spec 1.1.0.
