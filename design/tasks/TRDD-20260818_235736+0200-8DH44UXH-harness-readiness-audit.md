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

- [ ] D1 No direct server calls: R22.6 bright-line grep + `/api/` triage of all 33 files;
      every server interaction routes via amp-*/aimaestro-* scripts only.
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

## Approval log

## Notes and lessons learned
