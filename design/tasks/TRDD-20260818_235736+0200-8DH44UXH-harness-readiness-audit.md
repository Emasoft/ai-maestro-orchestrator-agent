---
trdd-id: 8DH44UXH
title: Harness-readiness audit — full plugin conformance for the ai-maestro harness
column: ai_review
scope: project
project-id: ai-maestro-orchestrator-agent
created: 2026-08-18T23:57:37+0200
updated: 2026-08-19T14:04:27+0200
current-owner: ai-maestro-orchestrator-agent
created-by: ai-maestro-orchestrator-agent
task-type: audit
approval-tier: 0
relevant-rules: [9]
external-refs: [ai-maestro TRDD-BRRJK57P]
npt: []
eht: []
blocked-by: []
release-via: publish
---

# Harness-readiness audit — full plugin conformance for the ai-maestro harness

USER goal (2026-08-18, verbatim intent): verify the whole plugin (architecture, scripts,
skills, subagents, hooks, docs, templates, checklists) for the ai-maestro harness, in
collaboration with the hub session. Workflow-never-stops: the team flow may pause ONLY on
MANAGER / CHIEF-OF-STAFF approval waits.

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-08-19

S Fix phase largely LANDED. Commits: 2711d6d (G1-G6 oracle rewrite + AC1-AC5 archival path,
tests green), bd1ed0b (doc batch: G1/G7/G8/G9/G10/G11 + AC6 17-column table + F7 trichotomy
paragraph, 12 files), eb64ccc (F2 validate write-gate + F4/F5/F6 doc adoption + real-condition
tests; 204 tests pass). Hub ruling (BRRJK57P/63a2a0bb): 3-tools adoption VOLUNTARY NOW at the
ledgered sites — done except F1/F3, DECLINED with rationale (trddgrep show / specgrep have no
machine-readable path/porcelain output; parsing human-oriented ranked text from library code
is brittle — interface gap to file hub-side before migrating those two sites). The new F2 gate
immediately surfaced 5 real board defects; 4 repaired (6B3K7S69/NSWPM93D/704ZBCR8 archived as
`complete` per release-via none + 3P-ZON-12 three-writes; 03DYGXJW `derived: true` added).
Release CI v1.13.9 rerun = SUCCESS (run 32188563813).

### NEXT ACTION
D1-D8 all closed. v1.13.11 published (publish.py exit 0, CPV 0/0/0/0) and its Release CI
GREEN (run 32231241419 success, 2026-08-19 — one cancelled-flake rerun, timeouts untouched).
Card moved testing→ai_review in the test-runner capacity (CI green = the required tests).
REMAINING: ai_review pass, then ai_review→human_review escalation per B2 (non-exempt).
Prior v1.13.10 CI failure (find_trdd tests vs CLI-less runners) fixed in da1550f. Side event
ledgered: janitor cache-updater outage 09:45-10:02 tool-locked the session mid-release —
filed ai-maestro-janitor#281.

## Audit dimensions (checklist)

- [x] D1 No direct server calls — PASS (2026-08-18). `localhost:23000`/`curl 23000` refs = 0.
      All 33 `/api/` hits triaged one-by-one: generic example endpoints in teaching material
      (task templates, bug-report samples, changelog examples), project file paths
      (`src/api/`, `tests/api/`), or lines STATING the R23 rule. Zero instruct an ai-maestro
      server call. Full hit list preserved in the session log 2026-08-18.
- [x] D2 Script-call syntax current — PASS-with-note (2026-08-19, pre-clear session; see
      handoff ledger).
- [x] D3 Governance alignment — findings G10/G11 fixed in bd1ed0b (R49.4/R49.6 added to the
      persona); R50/R51 confirmed AIO-scoped, not applicable; R52 clean.
- [x] D4 3 pillars + 3 tools — tool is `specgrep` (not specsgrep; wrong-name zero). Adoption
      per hub ruling: F2/F4/F5/F6/F7 landed (eb64ccc, bd1ed0b); F1/F3 declined pending a
      machine-readable output mode (see STATE). Trichotomy taught at the F7 site.
- [x] D5 Frontmatter validity — verdicts ledgered below; class-C phantom fixed 387ac51.
- [x] D6 Integrator coordination — findings G1-G9 fixed across 2711d6d + bd1ed0b: oracle
      rewritten from Part B2, release lane to INTEGRATOR/RELEASER/DEPLOYER, assignee moves
      dev→testing only, test runner owns testing→ai_review|dev.
- [x] D7 Scenario walkthroughs — 4 findings (D7-1..D7-4, report
      reports/d7-walkthroughs/20260819_091934+0200-d7-scenarios.md), ALL FIXED: D7-1
      nonexistent agent-messaging skill (413 refs/105 files) swept to the amp-* CLI (8dd0855);
      D7-2 forbidden AMOA→AMAMA escalations rerouted via AMCOS with R6 v3 reason inline;
      D7-3 lifecycle-authority disambiguation added (TRDD authoritative, labels mirror) to the
      3 label-driving skills + main-agent menu; D7-4 AGENT_OPERATIONS.md refs qualified;
      D7-5 agent-replacement now writes the TRDD assignee:/current-owner: SSOT half (967836d).
- [x] D8 Cross-reference integrity — H1 label-taxonomy migration (d5d1588, 65 files), H2
      closed (a3b6b66), D7-1/D7-4 dead references fixed; scenario 4 clean; remaining known
      gap: none open on the ledger.

## Findings ledger

(append `F<n> — <file:line> — <class> — <one line>` as verified; every finding gets verified
first-hand before any fix card is authored)

### D4 sweep results (agent report, 2026-08-19 — VERIFY file:line first-hand before fixing)

SPEC PREMISE REFUTED: 3-pillars-spec.md 2.0.0 §3P-GREP is a reading protocol for the spec
itself, §3P-CHK assigns no check to role plugins; NO normative clause requires
trddgrep/prrdgrep/specgrep of a role plugin, and the exit-code trichotomy lives only in the
hub's CLAUDE.md:100-102. So D4 adoption is hub-COORDINATION work (agree the obligation with
the hub, or adopt voluntarily), not spec-compliance. USER mandate still asks for correct use
of the 3 tools → adopt at the F1-F7 sites below.

Migration candidates (tool would REPLACE a mechanism):
- F1 shared/amoa_trdd_link.py:93-106 find_trdd() raw glob → `trddgrep query`.
- F2 scripts/amoa_kanban_manager.py:680,698-711 set_column with no validate → `trddgrep
  validate` before write, honouring exit 2 ≠ 1.
- F3 scripts/amoa_compile_handoff.py:74-78 glob over design/requirements → specgrep/prrdgrep.
- F4 skills/amoa-prrd-trdd-kanban/SKILL.md:68,128,146 find-by-column via ama-trdd-find →
  name trddgrep as backing CLI.
- F5 SKILL.md:50-54 bare `grep -q` boolean collapses could-not-run into found — fix the
  2→1 collapse regardless of tool.
- F6 main-agent.md:526-536 inline 17-column list (6th copy) → specgrep @spec:kanban-columns.
- F7 main-agent.md:62-72 R25 block = the teaching site for the trichotomy paragraph.

ARCHIVAL DEFECTS (3P-ZON-05 amended 2026-08-18: every terminal column archives AS ITSELF;
`complete` archive-eligible; archival MUST NOT rename; 3P-ZON-12 three writes):
- AC1 shared/amoa_trdd_link.py:57-66 _ZONE_BY_COLUMN omits `complete` → falls to tasks zone.
- AC2 shared/amoa_kanban_vocab.py:86 alias `completed→complete` = rename of a terminal value
  AND (with AC1) makes the completion path NEVER reach archived/.
- AC3 tests/unit/test_trdd_link.py:79 pins the pre-amendment set green (asserts completed→
  archived, nothing for complete).
- AC4 `cancelled` archive-eligible per spec but absent from KANBAN_COLUMNS
  (amoa_kanban_vocab.py:23-42) → unreachable.
- AC5 scripts/amoa_kanban_manager.py:689-711 archival writes column+updated+git mv but never
  `archived: true` nor the body OUTCOME/WHY (2 of 3P-ZON-12's three writes missing).
- AC6 skills/amoa-kanban-management/references/kanban-column-system.md:1-17 ships an
  8-column "standard" contradicting 3P-KAN-01's 17 (and our own main-agent list).
Compliant for contrast: failed-stays-on-board (main-agent.md:535-536, 3P-ZON-06).

### D3+D6 sweep results (agent report, 2026-08-19 — VERIFY file:line first-hand before fixing)

TRANSITION-AUTHORITY DEFECTS vs Part B2 (~/ai-maestro/rules/aimaestro/aimaestro-trdd-approval.md):
- G1 main-agent.md:77 Key-Constraints table hands ALL column transitions to AMIA/integrator —
  strips ORCH of its own B2 rows (todo→design, dispatch→dev); contradicts our own SKILL.md:16-18.
- G2-G6 shared/amoa_kanban_vocab.py:195-203 `transition_authority()` claims for ORCH six
  transitions B2 assigns elsewhere: dev→testing (assignee), testing→ai_review + testing→dev
  (test runner), design→dispatch (ARCHITECT), backburner→todo (MANAGER), live→live_auditing
  (INTEGRATOR). amoa-prrd-trdd-kanban/SKILL.md:97-99 declares this oracle authoritative while
  its own prose at :19 is B2-correct — the file ships two answers and names the wrong one.
- G7 release lane: amoa-orchestration-patterns/references/release-coordination-procedure.md
  assigns complete→publish|deploy→published|live to ORCH+implementer; INTEGRATOR/RELEASER/
  DEPLOYER appear NOWHERE in the procedure.
- G8 assignee-moves-to-ai_review taught in 7+ places: amoa-implementer-interview-protocol
  SKILL.md:41 (+3 restatements), remote-coordinator task templates (part1-core-template.md:374,
  part1-template.md:330, github-projects-guide.md:137, KANBAN_SYNC part2:36-42),
  verification-loops-protocol.md:383 — all pre-empt the test runner's transition.
- G9 main-agent.md:529-536 enumerates 17 columns but carries no transition-authority table
  nor a Part B2 pointer (nothing corrects G1).

GOVERNANCE GAPS (governance-spec.md, R49; R50/R51 live in all-in-one-spec.md not
governance-spec — none of our files calls an AIO pipeline, so no R50/R51 finding; R52 clean):
- G10 R49.6 record-where-actionable MUST absent: refusals + named defect must land in the
  governing GitHub issue and/or Approval log; main-agent :561-562 covers approvals only.
- G11 R49.4 second sentence: where no AMP thread exists (plugin session ↔ MANAGER) the
  cross-repo GitHub issue IS the channel — persona hard-codes inter-agent message only
  (and :375 says stop-and-surface); add the issue channel.

### D5 verdicts (triage agent, 2026-08-18)
Fields background(21)/type(5)/memory_requirements(5)/triggers(2)/hooks `_note`(1) = class B
plugin-private, harmless — keep, optionally report to CPV as known-benign. The 1 class-C
phantom `hide-from-slash-command-tool` (commands/amoa-cancel-orchestrator.md) FIXED same day
→ `disable-model-invocation: true`.

### D8 partial findings (2026-08-19, verified first-hand via grep)

- H1 STALE LABEL TAXONOMY — the old 8-column GitHub-label vocabulary
  (`status:backlog`/`status:done`/`status:merge-release`, plus direct
  `--add-label "status:ai-review"` moves) survives in ~20 files OUTSIDE the bd1ed0b batch:
  amoa-progress-monitoring (op-verify-task-completion.md:188, escalation-and-messaging.md:126,
  monitoring-examples.md:92), amoa-two-phase-mode/op-create-github-issues.md:75,
  amoa-module-management/op-sync-module-github-issue.md:287-293,
  amoa-developer-communication (op-respond-feature-request.md:145, op-respond-bug-report.md:151),
  amoa-remote-agent-coordinator (op-review-completion-report.md:137,
  scripts/generate_agent_skill.py:147, templates/github-projects-guide.md:81-88,
  KANBAN_SYNC_PROTOCOL.md:57-79 + part1 + part3, AGENT_SYNC_CHECKLIST*.md, ISSUE_TEMPLATE.md,
  PROJECT_SETUP.md:114-121, toolchain/BASE_TOOLCHAIN.md:78-84),
  amoa-kanban-management/kanban-examples.md:44, amoa-label-taxonomy
  (op-validate-label-cardinality.md:98, op-lifecycle-triage-labels.md — many hits).
  Fix = migrate to the 17-column `status:` labels from `shared/amoa_kanban_vocab.py`
  (STATUS_LABEL_COLORS is the SSOT list) + B2-correct movers.
- H2 66EA1BB1 TERMINAL-WITHOUT-CHECKLIST (trddgrep validate ERROR, still open): `complete`
  with no acceptance checklist. Tool prescribes move-back-to-dev + write checklist; the June
  migration it tracked demonstrably shipped, so a retroactive checklist may be honest — but
  it is a per-card judgment, deferred, NOT mass-repaired.
- Board hygiene repaired (2026-08-19): 6B3K7S69 / NSWPM93D / 704ZBCR8 ZONE-MISMATCH →
  archived as `complete` (release-via none) with 3P-ZON-12 three-writes; 03DYGXJW
  `derived: true` added (mechanical repair, `updated:` not bumped).
- Hub follow-through (2026-08-19): spec proposal ai-maestro TRDD-Z70X3LEW (3P-TOOL-01..04,
  incl. porcelain-mode MUST with legitimate deferral — our F1/F3 declination cited as the
  reference shape); porcelain implementation carded hub-side as Tier-0 TRDD-IPSNDKGM
  (`--porcelain` TAB path-first records, trichotomy unchanged).
- Porcelain SHIPPED (hub 5f10772e) and verified first-hand on all 3 exit branches. F1
  MIGRATED: find_trdd() now `trddgrep show <id> --porcelain --design-dir`; 1→None,
  2/missing-binary/timeout→raise (never collapsed into not-found); dead TRDD_FILENAME_RE
  removed; all 20 trdd_link tests pass against the REAL CLI (they are the acceptance tests).
  F3 RE-CLASSIFIED as corpus mismatch, not interface gap: specgrep env shows this repo's
  corpus = design/specs/, but compile_handoff searches design/requirements/**/specs/ module
  files — disjoint trees, so specgrep cannot serve that lookup; F3 stays glob-based
  legitimately unless the module-spec tree ever moves under the spec corpus. Adoption tally:
  6 of 7 migrated, 1 not-applicable-with-rationale.

## Approval log

## Notes and lessons learned
