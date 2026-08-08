---
trdd-id: 7MGYSHMN
title: Strip GitHub @mentions from every shipped template and guard the defect class with a test
column: complete
created: 2026-08-08T12:22:12+0200
updated: 2026-08-08T15:08:46+0200
current-owner: ai-maestro-orchestrator-agent
assignee: ai-maestro-orchestrator-agent
task-type: bugfix
scope: project
project-id: ai-maestro-orchestrator-agent
min-approval-requirement: none
severity: high
blocked-by: []
relevant-rules: []
external-refs: [https://github.com/Emasoft/ai-maestro-orchestrator-agent/issues/31, ai-maestro-plugin#33]
release-via: publish
---

# Strip GitHub @mentions from every shipped template

## The defect

Our templates wrote `@maintainer` meaning our governance ROLE. GitHub read it as a
mention of the USER `maintainer` — a real account since 2009 with no connection to
this project. A stranger on `ai-maestro-plugin#33` asked us to stop: *"I believe
what you do is great but I get endless amount of notifications. Could you please
stop mentioning the username?"*

Short role-shaped nouns are exactly the usernames claimed a decade ago, so our
governance vocabulary and GitHub's username namespace collide **by construction**.

## What the audit actually found — larger than the report

orch#31 named 6 sites and 5 real accounts. Scanning with a detector that models
GitHub's real mention rule (rather than a list of role words) found **24 sites and
18 genuine violations across 11 files**, hitting **19 real accounts**:

| handle | account since | handle | account since |
|---|---|---|---|
| `maintainer` | 2009 | `contributor` | 2011 |
| `manager` | 2018 | `devops` | 2012 |
| `architect` | 2017 | `devops-team` | 2014 |
| `orchestrator` | 2014 | `dev-alice` | 2014 |
| `integrator` | 2023 | `sre-team` | 2018 |
| `reporter` | 2013 | `backend-lead` | 2021 |
| `developer-a` | 2017 | `backend-dev` | 2020 |
| `developer-b` | 2023 | `new-agent` | 2018 |
| `types` | 2019 | `me` · `main` · `latest` | — |

The role-word grep that reproduced the issue's own list **missed `@other-developer`**
— which is the whole argument for a general detector: any fix scoped to a list of
known role words is one contributor away from being wrong again.

## The fix — two conventions, by intent

- **Naming a ROLE** → no sigil: `[maintainer]`, `[orchestrator]`, `[sre-team]`.
  These files already used `[bracketed]` placeholders (`[topic]`, `[issue]`), so the
  fix matches their own convention rather than inventing one.
- **A person PLACEHOLDER** → `@<username>`. A GitHub username may not begin with
  `<`, so the placeholder is **provably inert** until a real handle replaces it,
  while still teaching the `@` credit format that a changelog legitimately needs.
- **Prose ABOUT the feature** (`@mentions`, `@types`) → backticks. GitHub does not
  linkify inside a code span, so this is the documented fix and it keeps the prose
  reading naturally.

## The guard — `tests/unit/test_no_github_mentions.py`

A textual fix alone lasts until the next contributor writes the natural thing.
**This defect class has no local symptom**: the damage lands entirely in a
stranger's notification inbox, nothing in this repo observes it, and no test failed
for the weeks it ran. The only detector was a courteous stranger. So the check has
to be mechanical.

Three design decisions are load-bearing, each pinned by its own test:

1. **The regex models GitHub's measured behaviour**, not intuition — word boundary
   before `@`, and never before `/`. `@janitor.` and `(@janitor)` page; `x@janitor`,
   `user@gmail.com`, `actions/checkout@v4` and `@types/node` do not.
2. **A fence tagged with a programming language is skipped; an untagged or
   `markdown`/`text` fence is scanned.** This asymmetry IS the threat model: the
   fenced *template* is the dangerous case (it gets pasted into a real comment)
   while the fenced *code example* (`@staticmethod`, `@NotNull`, `@main`, `@rpath`)
   is correct writing.
3. **Inline code spans are stripped from PROSE but not from inside a template.** In
   prose a backtick genuinely disarms the mention; a template is written to be
   copied and filled, so it must carry no `@` at all.

Decision 3 was added *because the first version of the detector was wrong*: it
flagged `` `@rpath` `` and `` `@main` `` — correct, already-inert writing. A check
that reddens on correct code gets deleted, taking the real protection with it, so
the false positives mattered as much as the true ones.

`ALLOWED` contains exactly one name — `claude`, the documented trigger phrase for
the Claude Code GitHub Action, where the sigil is load-bearing. **The fix when this
test fails is never to extend that set.**

## Verification

- Detector reports `0 violation(s)`; full suite **186 passed** (was 182).
- **Mutation-verified**: restoring one `@dev-alice` fails
  `test_no_at_mentions_in_shipped_text`; reverting passes. The guard guards.
- Every handle above was checked against `gh api users/<name>` first-hand, not
  inferred from the issue text.

## Acceptance criteria

- [x] Every `@role` removed from shipped templates and prompts
- [x] A test fails on any `@mention` in shipped published text
- [x] The test does not fire on code examples or correctly-backticked prose
- [x] Mutation-verified that the test guards rather than decorates
- [x] orch#31 answered and closed (comment `5225691166`, closed 2026-08-08)
- [x] Released so the fix reaches installed copies — **v1.11.0**

## Closure record

- **Release:** `v1.11.0`, created 2026-08-08T10:53:18Z (12:53:18+0200), cut from
  `main` after PR #32 merged as `c58e501`.
- **Verified AT THE TAG**, not in the working tree — `git grep '@maintainer'
  v1.11.0 -- skills/` → **0**, and `tests/unit/test_no_github_mentions.py` is
  present in the published tree. A working-tree check would have proved only that
  my disk was clean, which is not the thing that reaches users.
- **Column stopped at `ai_review`, deliberately.** `transition_authority("testing",
  "complete")` returns `manager` — my own gate (`shared/amoa_kanban_vocab.py`,
  shipped for TRDD-704ZBCR8 F3) refuses to let an ORCHESTRATOR mark this complete.
  The terminal transition needs a MANAGER stamp. Dogfooding the gate rather than
  routing around it is the point of having built it.

## Notes and lessons learned

**A convention that reads as correct and does something entirely different.**
Addressing a role versus paging a stranger. The distinguishing feature is that the
damage lands **outside** the system, so no amount of internal testing surfaces it —
the same shape as a filter that reads as correct and matches nothing. When a defect
class has no local symptom, a mechanical check is not optional polish; it is the
only detector that will ever exist.

## Approval log

- 2026-08-08T12:22:12+0200 — Tier 0 (`min-approval-requirement: none`): a bugfix
  wholly inside this plugin's own tree, no baseline deviation, no cross-project
  surface. Reported by the Claude developing ai-maestro as orch#31.
- 2026-08-08T15:08:46+0200 — `ai_review → complete` APPROVED by MANAGER
  (min-approval-requirement: manager). Verified independently at tag `v1.11.0`, not
  on the relay: 0 `model:` keys across 6 agent files — **control-checked** (the main
  agent read back 35,541 bytes, so the zero is a real scan and not a vacuous pass
  over an empty file set) — and the skill menu exact against 23 shipped skills.
