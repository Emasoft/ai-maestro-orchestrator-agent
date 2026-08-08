---
trdd-id: 704ZBCR8
title: Governance-readiness conformance delta for the ORCHESTRATOR role-plugin against the ai-maestro SSOT
column: live_auditing
created: 2026-08-08T10:32:57+0200
updated: 2026-08-08T10:58:47+0200
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

**Artifact audited against:** `ai-maestro@governance-rules` (**LOCAL** tree `~/ai-maestro`) —
F1–F6/F8 at commit `0329558c`, v5.3.2; **F7 (R52) re-read at `2d5060ec`, v5.3.3**, because the tip
moved mid-audit. Named explicitly, with the version per finding, because the published remote tip
`2ca29e43` is v5.2.0 and **243 commits behind**: the newer text is the unpublished one, so "the
artifact" is ambiguous right now and a citation that does not say which is not checkable. Under the
**v4.8.0 authority inversion**, `design/specs/*.md` governs `docs/GOVERNANCE-RULES.md` where they
differ — so a catalog citation is a citation of the emanation, not the source.

**NEXT ACTION:** none outstanding — all eight findings are closed. Remaining follow-ups are for
whoever picks this up next: migrate the ONE card still carrying legacy `approval-tier` when it is
next touched (never a mass rewrite), and read `amoa_reassign_kanban_tasks.py` /
`amoa_sync_github_issues.py` line-by-line if their mirror-writer classification is ever doubted.

**How F2/F4 were closed (`e02922d`).** The
ai-maestro server **confirmed the orch#27 reconciliation on 2026-08-08**: "GATE THE PATH" is a
build-condition, not a standing prohibition, and building the gate first (landed `e237dfe`) IS the
lift condition. Three constraints bind the implementation: (a) the write flows BACKWARDS into the
TRDD's `column:` plus the folder `git mv` when the move crosses a lifecycle zone — never the mirror
alone; (b) the Part B2 authority table still binds, so an ORCHESTRATOR never performs a
USER/MANAGER-gated transition even through its own gate; (c) `resolve_column` stays mirror-only, and
every ORIGINATING write routes through the gated path.

**Linkage shape — ratified, do NOT invent one.** The issue carries the greppable `TRDD-<id8>` (in
the TITLE by preference, since it survives body edits; a `**TRDD:** TRDD-<id8>` body marker is the
alternative), and the TRDD frontmatter carries `external-refs:` with the issue URL. Project-scoped
cards also carry `project-id:`. `create_task_issue` should take the TRDD id as a required input for
TRDD-backed cards.

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
- **F2 — TRDD corpus as SSOT: WAS NOT CONFORMANT, FIXED `e02922d`.** There was no issue↔TRDD link at all — `create_task_issue` recorded assignee/priority/dependencies and no TRDD id, so no board move could reach a card. Now bidirectional: the issue title carries `TRDD-<id8>` (ratified shape, appended idempotently) and the TRDD carries the issue URL in `external-refs:`. `update_task_status` writes the column through to the TRDD, positioned AFTER the authority gate so it is gated by construction.
- **F3 — editor authority: WAS NOT CONFORMANT, FIXED `e237dfe`.** `update_task_status` validated column vocabulary but not the authority to enter it, so an ORCHESTRATOR could move a card to `published`/`deploy`/`failed`/`superseded` with no approver in the record. Now gated, with an `approved_by` mirror path that writes the approver to the issue.
- **F4 — round-trip to TRDDs: WAS NOT CONFORMANT, FIXED `e02922d`.** A move now flows backwards into the TRDD's `column:` and, when it crosses a lifecycle zone, into its FOLDER via `git mv` — the folder is part of the state, so a frontmatter-only edit would leave a completed card in `tasks/` where every board query still counts it as open. `failed` deliberately does not move: it is retryable, and archiving it would take live work off the board.
- **F5 — dispatch precondition: WAS NOT CONFORMANT, FIXED `e237dfe`.** `check_dependencies_resolved` tested only that the dependency issue was CLOSED — true while the satisfying code sits in an unmerged PR, which is the SCEN-031 deadlock. `check_dispatch_precondition` now requires a closing PR merged into the base the worker branches from, and fails CLOSED on a query error.
- **F6 — `min-approval-requirement` supersedes `approval-tier`: PARTIALLY MIGRATED.** Applied to TRDD-NSWPM93D on its next touch (`6f42ae3`); **one** other card still carries the legacy field and is deliberately left for its own next touch, since the rule forbids a mass rewrite.
- **F7 — R52 THE WRITE BOUNDARY (5.1.0): CONFORMANT.** `sync_task` upserts through `_run_task_command` → `aimaestro-task.sh`, the frozen CLI, satisfying **R52.4** ("mutate it BY ASKING THAT CLI, never by hand-editing"). Every write target in `scripts/` and `shared/` is project-relative — no absolute paths, no `expanduser` writes, nothing into `~/.aimaestro/` — so **R52.1** holds via the "agent working directories, including an adopted project folder" clause. **R52.2** (installer, not runtime) and **R52.3** (user-scoped exception) do not bind AMOA's runtime surface.
- **F8 — `context: fork` skill backgrounding: CONFORMANT.** All 21 forked skills declare `background: false` (`0ad4599`), independently verified by the ai-maestro server at `9c1c7b8` (23 SKILL.md / 21 forked / 0 unpinned). Guarded by `tests/unit/test_skill_frontmatter.py`, which also excludes `.trashcan/` and worktree copies from the population.

## Conformant — with what was checked

A zero-findings claim is worthless without its coverage, so:

- **F1** — read `shared/amoa_kanban_vocab.py` in full; confirmed `KANBAN_COLUMNS` is the ratified 17 in lifecycle order, `resolve_column` raises `ValueError` on unknown input, and grepped every consumer for a competing status→column map (none).
- **F8** — parsed the delimited frontmatter block of all 23 `skills/*/SKILL.md` (not a line grep: a line grep counts fenced ```yaml doc examples as config, which was measured to over-count by exactly the documentation). Mutation-verified both directions.
- **F3/F5** — the fixes carry 32 new tests; each was checked to FAIL against the pre-fix behaviour, so they guard rather than decorate.
- **F7** — read R52.0–R52.4 in full at `2d5060ec`; read `sync_task` and `get_aimaestro_tasks` to their transport call; enumerated every write site in `scripts/` and `shared/` and checked each for an absolute or `$HOME`-relative target.

## Not checked (stated so the coverage is honest)

`amoa_reassign_kanban_tasks.py` and `amoa_sync_github_issues.py` were classified by their mutation
surface but not read line-by-line; they are mirror-writers and so are governed by the same F2/F4
work. The GitHub-Project field mapping in `amoa_sync_kanban.py` was read for direction of sync only.
`scripts/publish.py` and `scripts/smart_exec.py` were excluded from the R52 write-site sweep: they
are developer tooling, not the agent runtime R52.1 binds — an exclusion by argument, which someone
may disagree with, rather than an oversight.

## Acceptance criteria

- [x] Four-point alignment contract assessed, each point with its evidence
- [x] Dispatch precondition implemented and tested, not merely acknowledged
- [x] Editor-authority gate implemented and tested
- [x] F7 (R52 write boundary) audited — conformant
- [x] F2/F4 implemented (`e02922d`) — write-through + round-trip, gated by construction

## Approval log

- 2026-08-08T10:32:57+0200 — Self-mandated Tier 0 (`min-approval-requirement: none`), per the ai-maestro server's instruction that the conformance-delta audit is self-authored. Format modelled on TRDD-92LA26H1 (`ee08c2e7`, ai-maestro-assistant-role-agent).
