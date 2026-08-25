---
trdd-id: V5SDTH14
title: Migrate kanban vocabulary consumers to 3-pillars 3.0.0 (22-column board, 27-value column set)
column: publish
implementation-commits: [2818ca8]
scope: project
project-id: ai-maestro-orchestrator-agent
created: 2026-08-25T14:09:46+0200
updated: 2026-08-25T18:45:00+0200
current-owner: ai-maestro-orchestrator-agent
created-by: ai-maestro-orchestrator-agent
task-type: refactor
relevant-rules: []
external-refs: [ai-maestro governance-rules c8b0e9cb]
npt: []
eht: []
blocked-by: []
release-via: publish
---

# Migrate kanban vocabulary consumers to 3-pillars 3.0.0 (22-column board, 27-value column set)

## Why this exists

HUB directive received 2026-08-25 (cross-session message from the ai-maestro session, during
TRDD-CNUDTR9F work): 3-pillars **3.0.0 is PUSHED** — Emasoft/ai-maestro governance-rules head
`c8b0e9cb`, spec at `design/specs/3-pillars-spec.md`, PRRD at `design/requirements/PRRD.md`.
The board vocabulary moved from 17 columns to a **22-column board / 27-value `column:` set**,
and `approval-tier:` is **retired** (`min-approval-requirement:` is live). Existing cards are
grandfathered per 3P-KAN-21 — **no sweeps** over old cards.

Measured consumer surface in THIS repo (grep for `17-column|17 columns|live_auditing`,
2026-08-25): **19+ files**, including code and tests, not just prose:

- `shared/amoa_kanban_vocab.py` — the code-level vocabulary module (single source of truth here)
- `tests/unit/test_amoa_kanban_vocab.py`, `tests/unit/test_transition_authority.py`,
  `tests/unit/test_pillar_skill_stays_thin.py`
- `agents/ai-maestro-orchestrator-agent-main-agent.md`
- `docs/AGENT_OPERATIONS.md`, `docs/STATUS_MAPPING.md`, `docs/TEAM_REGISTRY_SPECIFICATION.md`,
  `docs/FULL_PROJECT_WORKFLOW.md`
- skills: `amoa-kanban-management` (kanban-column-system reference), `amoa-prrd-trdd-kanban`,
  `amoa-label-taxonomy` (2 refs), `amoa-module-management`, `amoa-remote-agent-coordinator`
  (4 templates), `amoa-messaging-templates`

No governance-pin sites found in this repo (grep for pinned governance SHAs → 0 hits); if the
3.0.0 spec introduces a pin-stamp convention, adopt it as part of this card.

## Scope / acceptance

1. Read the 3.0.0 spec FIRST from the hub repo (`design/specs/3-pillars-spec.md` at or after
   `c8b0e9cb`) — do not migrate from this card's summary; the spec is the authority.
2. `shared/amoa_kanban_vocab.py` carries the 3.0.0 column set; its tests updated and green.
3. Every doc/skill/template consumer above renders the 3.0.0 vocabulary; zero remaining
   `17-column` claims outside `design/archived/` and grandfathered card bodies.
4. New TRDDs authored by this repo never write `approval-tier:`; any tooling that emits it is
   migrated to `min-approval-requirement:` per the spec's grammar.
5. Full-repo sweep after the rename (`check-all-files-after-breaking-change`): no stale
   references to the retired vocabulary in rules, skills, commands, agents, hooks, scripts,
   docs, README, configs, tests.
6. Ships via publish.py (release-via: publish).

## Notes

- Authored directly as `todo` — fleet-conformance to a ratified pushed spec is
  apply-the-baseline-as-is (exempt class); no approval field written (the retired
  `approval-tier:` must not be written; `min-approval-requirement:` grammar to be read from
  the 3.0.0 spec before first use).
- Grandfathering: existing cards keep their old fields/columns per 3P-KAN-21 — this card
  migrates VOCABULARY CONSUMERS (code, tests, docs, skills), never old cards.

## Approval log

- 2026-08-25T18:45:00+0200 — Executed todo→dev→testing→publish under the USER's standing
  directive ("complete all pending tasks and TRDDs") + hub relay of the same; fleet-conformance
  to a ratified pushed spec is apply-the-baseline-as-is. Commit 2818ca8 (19 files). Acceptance
  measured: spec read in full from c8b0e9cb (fetched via gh api, 48312 bytes, spec-version
  3.0.0); vocab module + tests on 3.0.0, pytest 212/212, ruff clean; repo-wide grep — zero
  17-column claims, zero approval-tier field writes (rule-filename references retained
  deliberately); no governance-pin sites exist in this repo (measured, 0 hits). Entering
  release pipeline.
