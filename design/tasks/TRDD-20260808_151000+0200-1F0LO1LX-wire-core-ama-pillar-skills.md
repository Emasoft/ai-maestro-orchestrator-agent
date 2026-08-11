---
trdd-id: 1F0LO1LX
title: Wire the core granular ama-* pillar skills and retire the per-plugin script layer
column: testing
created: 2026-08-08T15:10:00+0200
updated: 2026-08-08T15:10:00+0200
current-owner: ai-maestro-orchestrator-agent
assignee: ai-maestro-orchestrator-agent
task-type: refactor
scope: project
project-id: ai-maestro-orchestrator-agent
min-approval-requirement: none
severity: high
blocked-by: []
relevant-rules: []
external-refs: [https://github.com/Emasoft/ai-maestro-orchestrator-agent/issues/25]
release-via: publish
---

# Wire the core granular `ama-*` pillar skills

## The finding (orch#25, A-CRITICAL)

Audited by MANAGER against v1.9.3: *"pillar ops run on a redundant per-plugin copy;
zero core `ama-*` wiring."* Re-measured at v1.11.0 — **still true**:

- `skills/amoa-prrd-trdd-kanban/SKILL.md` declared `allowed-tools` over the OLD
  script layer: `get-prrd.py`, `findprrd.py`, `findtrdd.py`, `kanban.py`.
- Its Overview and Resources deferred to a **monolithic `prrd-trdd-kanban` skill**
  that no longer exists — the operations were split into granular skills, so that
  reference resolved to nothing.
- Repo-wide grep for `ama-(prrd|trdd|kanban|proposal)`: **0 matches**.

Confirmed the granular skills are actually installed before wiring to them —
`ai-maestro-plugin` **3.1.5** ships all twelve: `ama-prrd-get`, `ama-prrd-find`,
`ama-prrd-edit`, `ama-prrd-propose`, `ama-trdd-write`, `ama-trdd-find`,
`ama-trdd-update`, `ama-trdd-transition`, `ama-trdd-server`, `ama-kanban-render`,
`ama-unblock`, `ama-proposal-approvals`.

## Why this was CRITICAL and not cosmetic

A second implementation of a governance operation **does not stay equivalent**. The
approval vocabulary moved under the MANAGER wave — `approval-tier: N` retired in
favour of `min-approval-requirement`, the approval record gained its
`approved:`/judge invariants, `orchestrator` became a first-class rung with no
legacy number. A private copy of the pillar ops keeps enforcing the retired shape
**while looking correct**, and nothing reports the divergence. The core skills are
the one implementation that moves with the rules.

## What changed

`skills/amoa-prrd-trdd-kanban/SKILL.md` → v2.0.0:

- `allowed-tools` now `Skill, Bash(amp-send:*), Bash(amp-kanban-*)…` — the whole
  `python3`/script surface removed.
- A **capability table** mapping each need to its core skill, called via
  `Skill(ai-maestro-plugin:<name>)`.
- Instructions rewritten onto the granular skills; the retired monolithic-skill
  references removed rather than repointed.
- **Capability-probe rule** recorded per the MANAGER wave: gate contract-dependent
  behaviour on the contract itself (`grep -q min-approval-requirement
  .claude/rules/aimaestro-trdd-approval.md`), **never** a plugin version or branch
  name — a version check answers a packaging question, not a behavioural one.
- Two additions that belong at the dispatch point: the **dispatch precondition**
  (step 4 — a dependency needs its closing PR *merged into the base the worker
  branches from*, not merely a closed issue; the SCEN-031 deadlock) and the
  **call-path gate** (step 7, from methodology §11).
- Step 8 now points at `transition_authority()` to answer exemption mechanically
  rather than from recall, noting it refuses ORCH's own completions by design.

The old script names survive in exactly one place: the paragraph explaining what was
removed and why. That is deliberate — the WHY is what stops a future contributor
restoring the copy. A first pass of my own verification flagged those two lines as
leftovers; they are the fix's documentation, not its residue.

Also on this card (orch#25, B-MED): **R24** cited at the Memory Protocol heading and
**R25** at the pillar wiring, both previously ungrepped.

## The rest of orch#25 — resolved after this card was written

- **Scenario coverage (B-MED): CLOSED in v1.13.0**, not outstanding as this card
  first said. SCEN-G12–G15 already existed on the stranded
  `feat/governance-readiness-25` branch and were salvaged by cherry-pick. Correcting
  the line rather than leaving it: a card that under-claims is as misleading as one
  that over-claims, and this one would have sent the next session to rewrite work
  that had already shipped.
- **Self-id (B-HIGH): CLOSED in v1.13.0** — the PRRD G1 line is embedded in the
  GH issue-body templates. Its salvaged form shipped `@Emasoft` inside the template,
  which the orch#31 mention guard caught on the cherry-pick; fixed to name the owner
  without the sigil.
- `approval-tier:` population (B-MED) is **superseded**, not outstanding: the field
  is RETIRED and `min-approval-requirement` replaces it. Every card authored today
  carries the new field; the one legacy card migrates on its next touch, never in a
  mass rewrite.

## Verification

- Suite **191 passed**; frontmatter parses; `allowed-tools` free of the script layer.
- All twelve `ama-*` skills confirmed present in the installed core plugin before
  being referenced — a wiring to a skill that does not exist would fail at load time,
  mid-task.

## Acceptance criteria

- [x] `allowed-tools` wired off the per-plugin script layer
- [x] Granular `ama-*` capability table, verified installed
- [x] Retired monolithic-skill references removed
- [x] Capability-probe rule recorded
- [x] R24 / R25 cited by number
- [x] Released — **v1.12.0** (rewire) + **v1.13.0** (salvaged #25 work)
- [ ] MANAGER stamp for the terminal transition

## Approval log

- 2026-08-08T15:10:00+0200 — Tier 0 (`min-approval-requirement: none`): rewiring this
  plugin's own skill onto already-ratified core skills, no baseline deviation, no
  cross-project write.
