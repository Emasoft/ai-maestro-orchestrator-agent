---
trdd-id: 8DH44UXH
title: Harness-readiness audit — full plugin conformance for the ai-maestro harness
column: dev
scope: project
project-id: ai-maestro-orchestrator-agent
created: 2026-08-18T23:57:37+0200
updated: 2026-08-18T23:57:37+0200
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

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-08-18

S Audit running. Facts so far: direct-server refs (localhost:23000) = 0. `/api/` strings in
33 files (triage pending: teach-a-call vs benign prose). trddgrep + prrdgrep on PATH at
`~/.local/bin`; **specsgrep MISSING**. CPV strict = 0 blocking, 45 advisory WARNINGs to mine
(unknown frontmatter fields, RC-PIPELINE-DRIFT on ci.yml/notify-marketplace.yml).
Authoritative refs requested from the hub (msg 3432e501): governance version, frozen-CLI verb
SSOT, specsgrep origin + 3-tools contract, integrator review-column contract, 3-pillars
role-plugin checklist.

### NEXT ACTION
Triage the 33 `/api/` files (classify each hit: (a) instructs an actual server call —
VIOLATION of R22/plugin-abstraction; (b) mentions an API in prose/examples unrelated to the
ai-maestro server — benign; (c) documents the frozen-CLI layer itself — benign). Then, on hub
reply: diff every amp-*/aimaestro-* call-site against the verb SSOT.

## Audit dimensions (checklist)

- [x] D1 No direct server calls — PASS (2026-08-18). `localhost:23000`/`curl 23000` refs = 0.
      All 33 `/api/` hits triaged one-by-one: generic example endpoints in teaching material
      (task templates, bug-report samples, changelog examples), project file paths
      (`src/api/`, `tests/api/`), or lines STATING the R23 rule. Zero instruct an ai-maestro
      server call. Full hit list preserved in the session log 2026-08-18.
- [ ] D2 Script-call syntax current: every amp-*/aimaestro-* invocation in skills/agents/
      commands/templates diffed against the frozen-CLI verb SSOT (need hub ref #2).
- [ ] D3 Governance alignment: rules added since the last delta audit (TRDD-704ZBCR8) that
      bind role plugins are reflected (need hub ref #1); PRRD S9.1 transport rule respected
      everywhere messaging is taught.
- [ ] D4 3 pillars + 3 tools: skills teach trddgrep/prrdgrep/specsgrep correctly; specsgrep
      availability resolved (missing on PATH — install path or upstream gap).
- [ ] D5 Frontmatter validity: mine CPV's 45 WARNINGs; fix malformed/unknown fields that are
      real (some may be CPV gaps to report upstream instead).
- [ ] D6 Integrator coordination: orchestrator handoffs at testing/ai_review columns match
      the integrator plugin's expected verbs/messages (need hub ref #4); S7.1 pre-PR gate text
      consistent across skills.
- [ ] D7 Scenario walkthroughs: simulate the team loop (dispatch → dev → testing → ai_review
      → complete) and the failure paths (blocked, failed, agent replacement); identify any
      point where an agent would STOP other than a MANAGER/COS approval wait; fix instructions
      that dead-end.
- [ ] D8 Inconsistencies/missing elements: cross-reference integrity (commands ↔ scripts ↔
      skills ↔ docs), dead references, duplicated guidance that drifted.

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

## Approval log

## Notes and lessons learned
