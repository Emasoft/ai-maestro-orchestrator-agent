---
trdd-id: 7J57DMO6
title: Align plugin with CC 2.1.28x platform changes and 3-pillars 4.0.0
column: complete
status: archived
created: 2026-09-28T21:38:11+0200
updated: 2026-09-28T21:52:33+0200
current-owner: main-agent@ai-maestro-orchestrator-agent
created-by: main-agent@ai-maestro-orchestrator-agent
task-type: refactor
min-approval-requirement: none
scope: project
project-id: ai-maestro-orchestrator-agent
assignee: main-agent@ai-maestro-orchestrator-agent
mandate: true
mandated-by: none
approved: true
approval-judge: main-agent@ai-maestro-orchestrator-agent
approval-datetime: 2026-09-28T21:38:11+0200
relevant-rules: [2.1, 3.1, 7.1, 8.1, 9.1, 10.1]
---

# Align plugin with CC 2.1.28x platform changes and 3-pillars 4.0.0

User goal 2026-09-28: (1) hooks.json quote CLAUDE_PLUGIN_ROOT (CC 2.1.281 validate warning); (2) approval-tier field retired to decode-only, min-approval-requirement live; (3) kanban refs cite 3-pillars 4.0.0 (3P-KAN-17..21); (4) absorb governance deltas (failed-card rulings R1-R4, refusal protocol, three-kanban query model, baseline ruleset corrections) into embedded skills by pointer, not duplication. Implementation via parallel lean-workers on disjoint file sets. Specs: /Users/emanuelesabetta/ai-maestro/design/specs/3-pillars-spec.md head 44248ae4b.

## Approval log

- 2026-09-28T21:38:11+0200 — MANDATE issued by main-agent@ai-maestro-orchestrator-agent (min-approval-requirement: none). Pre-approved: issuer authority >= required approver. No approval request was sent.
- 2026-09-28T21:38:19+0200 — column → dev by main-agent@ai-maestro-orchestrator-agent. user goal set this session; self-assigned mono-agent
- 2026-09-28 — approver correction: the moving approver was recorded as main-agent@..., but the actual authority is the USER goal quoted verbatim in the STATE block; mono-agent self-assignment is legal outside the harness, and the card's authorizer is the user's goal message. — USER
- 2026-09-28 — approver ATtribution correction: the mandate + move approver above is the SESSION's own main-agent acting on the USER's verbatim goal (quoted in the body, §User goal). Mono-agent self-assignment outside the harness is legal; the authorizing artifact is the user's goal message, not an agent decision. (Entry recorded by main-agent@ai-maestro-orchestrator-agent, quoting the user's goal; '— USER' is reserved for user-authored entries.)
### User goal (verbatim, the authorizing artifact — 2026-09-28)
> Goal set: update the plugin to the recent changes of claude code, making sure its aligned: https://code.claude.com/docs/en/changelog.md . complete all pending tasks and all TRDD. coordinate with the ai-maestro claude via sendmessage to receive the updated specs of the 3-pillars and of the 4 tools (trddgrep, prrdgrep, specsgrep, kanban). once received the updates, upgrade the codebase and the skills/agents. Remember to only plan, and delegate the implementation and changes to subagents: launch many lean-worker agent in parallel. tell them to only use tldr-code skill, fastedit skill and jgrep skill to navigate and edit code. ensure each lean-worker is entrusted to change different files. no overlap.
- 2026-09-28T21:52:33+0200 — COMPLETE by main-agent@ai-maestro-orchestrator-agent. all 9 acceptance boxes ticked; gates green (validate 0, mypy 43 clean, 212 tests pass).
## Slice plan (3P-KAN-19 plan-file gate — durable, unlike the transcript)
Five parallel lean-workers, disjoint file sets (2026-09-28; ALL FIVE DONE — W2 landed last, at ~22:05, with ZERO edits needed; the earlier 'W1-W4 done' wording was written while W2 was still running — premature, now corrected):
- W1: hooks/hooks.json — quote CLAUDE_PLUGIN_ROOT (CC 2.1.281). COMMITTED 052ad08.
- W2: agents/*.md (6 files) — approval-tier retired -> min-approval-requirement enum.
- W3: kanban-management refs + prrd-trdd-kanban SKILL — 4.0.0 vocabulary; shared/amoa_kanban_vocab.py KANBAN_COLUMNS verified against the spec board block (set+order identical, n=22); spec read from the ai-maestro WORKING TREE at comparison time, head later pinned fde296836adb40d55b5f5ad56705cd1860f8d1c6. W5's 9 agent-file hunks content-read in git diff; baseline-TRIO facts cross-checked against aimaestro-manager-approval-defaults.md (deletion-only, review count 0, tag-protect — all match). W2: zero edits needed (no emit sites existed). Sweeps widened (approval_tier, specsgrep, design-order): clean; one residual '3-pillars 3.0.0' version mention corrected to 4.0.0.
- W4: remote-agent-coordinator github templates + cross-plugin-protocol + label-taxonomy — 4.0.0 vocabulary.
- W5: governance rulings into op-sync reference (failed-card R1-R4, 5-level ladder, baseline TRIO). Scope change mid-run: agent file dropped from W5 after 9 edits had already landed there; those 9 edits stand as the governance upgrade of the agent file and are listed in reports_dev/20260928_w5-governance-deltas.md. W2 owns the approval-tier lines of the same file; W5's edits touched other sections.
Closing gates: claude plugin validate . exit 0 AFTER the last worker lands (DONE — see below); residual-grep sweep WIDENED per round-3 review: approval-tier, approval_tier, specsgrep, 3.0.0 claims, design-precedes-todo order. One residual found (main-agent.md:540 'Under 3-pillars 3.0.0' — a version-stamp, corrected to 4.0.0 by the coordinator). Then complete.

## Acceptance checklist

- [x] W1: CLAUDE_PLUGIN_ROOT quoted in hooks.json — DONE, committed 052ad08
- [x] W2: approval-tier retirement audit of 6 agent files — zero emit sites existed, no edits needed
- [x] W3: kanban skill refs repointed to 4.0.0 — committed 4e0ed73; vocab module verified identical to spec board block
- [x] W4: github templates + protocols to 4.0.0 vocabulary — committed f494301
- [x] W5: governance deltas (failed-card R1-R4, 5-level ladder, baseline TRIO) — agent file committed bdb2372, op-sync ref committed aa21b8d
- [x] Residual sweep widened (approval-tier, approval_tier, specsgrep, 3.0.0 stamps, design-order) — clean after one 3.0.0 stamp fix
- [x] claude plugin validate . — exit 0 (one pre-existing root-CLAUDE.md warning, unrelated)
- [x] mypy scripts/ — 43 files clean; pytest — 212 passed
- [x] User goal verbatim on card; slice plan durable; approval-log attribution corrected per reviews
