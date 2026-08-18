---
trdd-id: EYOV4I0A
title: Absorb coordination-methodology sections 3, 6 and 11 into the ORCHESTRATOR persona
column: complete
created: 2026-08-08T15:10:00+0200
updated: 2026-08-16T16:31:21+0200
current-owner: ai-maestro-orchestrator-agent
assignee: ai-maestro-orchestrator-agent
task-type: docs
scope: project
project-id: ai-maestro-orchestrator-agent
min-approval-requirement: none
severity: medium
blocked-by: []
relevant-rules: []
external-refs: [https://github.com/Emasoft/ai-maestro-orchestrator-agent/issues/33]
release-via: publish
---

# Absorb coordination-methodology §3, §6, §11

## The work order

orch#33, USER-commissioned, from the Claude developing ai-maestro. Source:
`design/methodology/multi-agent-coordination-methodology.md` in `Emasoft/ai-maestro`
(`governance-rules`, commit `cfd568b8`; read via the contents API 2026-08-08).
The ORCHESTRATOR's share is §3 (work-order shape), §6 (parallel by default; the
orchestrator owns the clock), §11 (honest columns and honest completion).

The order's **second item** — review the 5 `opus`-pinned subagents — was already
satisfied by v1.11.0 under `TRDD-QQY1PJZI`, which dropped all five. The orderer has
said it will amend the issue. Nothing further owed on that half.

## What was absorbed, and where

A new `## Coordination Method` section in
`agents/ai-maestro-orchestrator-agent-main-agent.md`, ahead of `## Record-Keeping`.

**Inlined rather than cited, deliberately.** A persona that points at a document the
agent must go fetch is ignored exactly when load is highest — which is when
coordination discipline matters. The citation is kept for provenance; the content is
local.

- **§6 — parallel by default.** Background workers for bounded measurement,
  work-order messages for peer-owned changes, inline only for own-judgment work. The
  **clock rule**: a spawned worker never polls or sleeps on an external event (it
  cannot see the world change and burns context idling) — the orchestrator holds the
  wait and dispatches bursts whose preconditions are already true. The **worker
  contract**: explicit file scope, invariant checklist in the prompt, report to a
  path, 2-line return, and **full accounting — every input CITED or explicitly
  CLEAN**, because a truncated report is otherwise indistinguishable from a thorough
  one and reads as good news.
  Kept the source's blunt framing: *serialization is the default failure mode of a
  careful agent.*
- **§3 — the work-order shape.** Spec card in the orderer's repo + the peer's OWN
  Tier-0 card + a closure record (release tag + tip sha + pasted timestamps). The
  split keeps every card Tier-0-honest — nobody writes in another project's tree —
  and gives the orderer something to RE-MEASURE instead of a claim to believe. Plus
  the **fold-in rule**: add to an open work order rather than issuing a second.
- **§11 — honest columns.** A column is a claim someone acts on. The refinement
  worth keeping: gate on **"reachable along MY OWN call path"**, not "the dependency
  deployed" — a server capability whose CLI this plugin cannot express is not
  available to this plugin, however live it is upstream. Also added to
  `amoa-prrd-trdd-kanban` step 7, where dispatch decisions are actually made.

This card is itself the shape §3 describes: the order lives in orch#33, this Tier-0
card lives here, and the closure record below is re-measurable.

## Verification

- Suite **191 passed**; ruff clean.
- `## Coordination Method` present in the persona with all three subsections.
- The §11 call-path gate also lands in `amoa-prrd-trdd-kanban` step 7.

## Acceptance criteria

- [x] §3 absorbed (work-order shape + fold-in rule)
- [x] §6 absorbed (parallel by default, clock rule, worker contract)
- [x] §11 absorbed (honest columns, call-path gate)
- [x] Second item (5 opus subagent pins) — satisfied by v1.11.0 / TRDD-QQY1PJZI
- [x] Released — **v1.12.0**, created 2026-08-08T13:12:53Z; source commit `cfd568b8`
- [x] MANAGER stamp for the terminal transition (ORCH cannot self-complete)

## Approval log

- 2026-08-08T15:10:00+0200 — Tier 0 (`min-approval-requirement: none`): documentation
  of this plugin's own persona, no baseline deviation, no cross-project write.
- 2026-08-16T16:31:21+0200 — APPROVED by ai-maestro hub session (fleet coordination, USER-granted 2026-08-16). testing -> complete. Evidence: agents/ai-maestro-orchestrator-agent-main-agent.md:190 "## Coordination Method".
