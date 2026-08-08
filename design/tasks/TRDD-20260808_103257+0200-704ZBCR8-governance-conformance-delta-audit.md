---
trdd-id: 704ZBCR8
title: Governance-readiness conformance delta for the ORCHESTRATOR role-plugin against the ai-maestro SSOT
column: live_auditing
created: 2026-08-08T10:32:57+0200
updated: 2026-08-08T10:32:57+0200
current-owner: ai-maestro-orchestrator-agent
assignee: ai-maestro-orchestrator-agent
task-type: audit
scope: project
project-id: ai-maestro-orchestrator-agent
min-approval-requirement: none
mandate: true
mandated-by: self
severity: medium
blocked-by: []
relevant-rules: []
external-refs: [ai-maestro-plugin#61, ai-maestro-janitor#238, ai-maestro-janitor#190]
release-via: none
---

# Governance-readiness conformance delta for the ORCHESTRATOR role-plugin

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-08-08

**Artifact audited against:** `ai-maestro@governance-rules` commit `0329558c` (**LOCAL** tree
`~/ai-maestro`), `docs/GOVERNANCE-RULES.md` v5.3.2. Named explicitly because the published remote
tip `2ca29e43` is v5.2.0 and **243 commits behind** — the newer text is the unpublished one, so
"the artifact" is ambiguous right now and a citation that does not say which is not checkable.
Under the **v4.8.0 authority inversion**, `design/specs/*.md` governs `docs/GOVERNANCE-RULES.md`
where they differ.

**NEXT ACTION:** answer is pending from the ai-maestro server on whether MANAGER ruling orch#27
(resolve_column is mirror-only) permits AMOA to originate TRDD `column:` writes now that the path
is gated. Findings F2 and F4 are blocked on that answer and on **nothing else** — the gate they
require already exists.

**Load-bearing gotcha:** `shared/amoa_kanban_vocab.py` carries an invariant recording orch#27:
*"if resolve_column is ever wired into a path that ORIGINATES a TRDD column write, a legacy value
would land a card on a MANAGER-gated column with no MANAGER stamp. If you add such a path: GATE
THE PATH, not this map."* Wiring the write-through without the gate is the specific, predicted
failure. The gate landed first (`e237dfe`); the write-through has not.

## Scope of this audit — what was checked

The four-point **Orchestrator-plugin alignment** contract
(`rules/aimaestro/aimaestro-kanban-multiagent.md`, section at line 146), the **dispatch
precondition** (`aimaestro-trdd-approval.md` Part B2, TRDD-BYCN5PB7), and the TRDD schema deltas
since ~2026-07-21. Every finding below was reached by READING the implicated source, not by
grepping for its absence.

## Findings

- **F1 — 17-column vocabulary: CONFORMANT.** `shared/amoa_kanban_vocab.py` is the single source; `resolve_column()` raises on an unknown value instead of defaulting to a column (orch#27, suggested fix 2), and every consumer imports from it rather than carrying its own map.
- **F2 — TRDD corpus as SSOT: NOT CONFORMANT.** No kanban script writes a TRDD on a board mutation, and there is **no issue↔TRDD link at all** — `create_task_issue` records assignee/priority/dependencies and no TRDD id. The board is GitHub-issue-native. *Blocked on the orch#27 reconciliation (see STATE).*
- **F3 — editor authority: WAS NOT CONFORMANT, FIXED `e237dfe`.** `update_task_status` validated column vocabulary but not the authority to enter it, so an ORCHESTRATOR could move a card to `published`/`deploy`/`failed`/`superseded` with no approver in the record. Now gated, with an `approved_by` mirror path that writes the approver to the issue.
- **F4 — GitHub-Project round-trip to TRDDs: NOT CONFORMANT.** Nothing flows back. Same blocker as F2; the two land together or not at all.
- **F5 — dispatch precondition: WAS NOT CONFORMANT, FIXED `e237dfe`.** `check_dependencies_resolved` tested only that the dependency issue was CLOSED — true while the satisfying code sits in an unmerged PR, which is the SCEN-031 deadlock. `check_dispatch_precondition` now requires a closing PR merged into the base the worker branches from, and fails CLOSED on a query error.
- **F6 — `min-approval-requirement` supersedes `approval-tier`: PARTIALLY MIGRATED.** Applied to TRDD-NSWPM93D on its next touch (`6f42ae3`); **one** other card still carries the legacy field and is deliberately left for its own next touch, since the rule forbids a mass rewrite.
- **F7 — R52 THE WRITE BOUNDARY (5.1.0): NOT AUDITED.** AMOA ships `amoa_aimaestro_sync.py` and calls `sync_task(...)` into server-owned stores, so it is in scope. Recorded as unaudited rather than assumed clean — section requested from the server.
- **F8 — `context: fork` skill backgrounding: CONFORMANT.** All 21 forked skills declare `background: false` (`0ad4599`), independently verified by the ai-maestro server at `9c1c7b8` (23 SKILL.md / 21 forked / 0 unpinned). Guarded by `tests/unit/test_skill_frontmatter.py`, which also excludes `.trashcan/` and worktree copies from the population.

## Conformant — with what was checked

A zero-findings claim is worthless without its coverage, so:

- **F1** — read `shared/amoa_kanban_vocab.py` in full; confirmed `KANBAN_COLUMNS` is the ratified 17 in lifecycle order, `resolve_column` raises `ValueError` on unknown input, and grepped every consumer for a competing status→column map (none).
- **F8** — parsed the delimited frontmatter block of all 23 `skills/*/SKILL.md` (not a line grep: a line grep counts fenced ```yaml doc examples as config, which was measured to over-count by exactly the documentation). Mutation-verified both directions.
- **F3/F5** — the fixes carry 32 new tests; each was checked to FAIL against the pre-fix behaviour, so they guard rather than decorate.

## Not checked (stated so the coverage is honest)

`amoa_reassign_kanban_tasks.py`, `amoa_aimaestro_sync.py` and `amoa_sync_github_issues.py` were
classified by their mutation surface but not read line-by-line; they are mirror-writers and so are
governed by the same F2/F4 answer. R52 (F7) is unaudited. The GitHub-Project field mapping in
`amoa_sync_kanban.py` was read for direction of sync only.

## Acceptance criteria

- [x] Four-point alignment contract assessed, each point with its evidence
- [x] Dispatch precondition implemented and tested, not merely acknowledged
- [x] Editor-authority gate implemented and tested
- [ ] F2/F4 resolved once the orch#27 reconciliation lands
- [ ] F7 (R52 write boundary) audited

## Approval log

- 2026-08-08T10:32:57+0200 — Self-mandated Tier 0 (`min-approval-requirement: none`), per the ai-maestro server's instruction that the conformance-delta audit is self-authored. Format modelled on TRDD-92LA26H1 (`ee08c2e7`, ai-maestro-assistant-role-agent).
