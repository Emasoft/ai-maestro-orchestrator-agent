---
trdd-id: PNIP18BY
title: Verify on a live server that implementation child tasks read back under the AI-Maestro epic
column: backburner
scope: project
project-id: ai-maestro-orchestrator-agent
created: 2026-08-16T16:30:31+0200
updated: 2026-08-18T19:53:09+0200
current-owner: ai-maestro-orchestrator-agent
task-type: feature
approval-tier: 0
created-by: ai-maestro-orchestrator-agent
relevant-rules: []
external-refs: [orch#26, architect#7, ai-maestro#77, TRDD-6B3K7S69]
npt: []
eht: []
blocked-by: []
release-via: none
review-after: 2026-09-15
---

# Verify on a live server that implementation child tasks read back under the AI-Maestro epic

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-08-16

S Split out of TRDD-6B3K7S69 on 2026-08-16. That card landed the READ/PARSE half of orch#26
(`extract_aimaestro_task_id`, `shared/amoa_design_handoff.py:25`, commit `45e409e`) plus the
attach PROCEDURE doc, and every dev-session-runnable acceptance box was checked. Its one
remaining box was a DEPLOYMENT-time check that cannot run from a dev checkout at all.

C Carrying that box on the parent left a completed card permanently one box short — the
completion gate would have had to be either violated (retro-ticked) or left standing forever
on work nobody can do here. Splitting is the honest third option: the parent closes on what it
actually delivered, and the live check stays tracked instead of quietly disappearing.

### NEXT ACTION
Nothing runnable from a dev session. When a live AI-Maestro server and an AMCOS-spawned agent
binding are available: send a design-handoff carrying `content.aimaestro_task_id`, create an
implementation child with `amp-kanban-create-task "<child>" --parent "$EPIC"`, then read the
epic back and assert the child appears under it.

### What proves this card
The child task, created with `--parent "$EPIC"` from an id parsed out of a real design-handoff,
is returned as a child of that epic when the epic is read back from the live server. Anything
short of a real server round-trip does not close this card — a mocked or replayed response
proves nothing about the traceability chain this exists to verify.

### Load-bearing facts inherited from 6B3K7S69 (do not re-derive)
- Key path is `content.aimaestro_task_id`, top-level of `content`, NOT under `content.data`.
  The SHIPPED v2.11.0 template wins over architect#7's original proposal.
- The id is an opaque string (e.g. `PVTI_laDOABcd1234`); do not assume a UUID shape.
- Attach only via the frozen verb `amp-kanban-create-task ... --parent` — never a raw
  `/api/*` call (R23, Plugin Abstraction Principle).
- Not blocked by ai-maestro#46: identity resolves via `AGENT_WORK_DIR/$PWD → name → uuid`;
  the colliding address was display-only (ai-maestro#77, 2026-07-23).

## Why this is a standalone card and NOT an `eht:` of 6B3K7S69

`~/.claude/rules/trdd-design-tasks.md` §9 defines an EHT as a post-condition whose parent
**cannot reach `complete` until every EHT is terminal**. Filing this as an EHT would therefore
reproduce the exact block the split exists to remove — the parent would stay open on a check
that needs infrastructure this repo does not have. It is filed as a derived standalone card
(`created-by: 6B3K7S69`) so the lineage is greppable while the parent closes on its own merits.

## Acceptance criteria
- [ ] A design-handoff carrying `content.aimaestro_task_id` is received from a live architect.
- [ ] An implementation child is created with `amp-kanban-create-task --parent "$EPIC"`.
- [ ] Reading the epic back from the live server returns that child under it.
- [ ] The absence case still behaves as today (no epic id → unlinked breakdown, no error).

## Notes and lessons learned
