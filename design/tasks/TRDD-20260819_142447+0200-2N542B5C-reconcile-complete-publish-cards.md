---
trdd-id: 2N542B5C
title: Reconcile the 8 complete/publish cards — backfill implementation-commits and run the publish lane
column: todo
scope: project
project-id: ai-maestro-orchestrator-agent
created: 2026-08-19T14:24:47+0200
updated: 2026-08-19T14:24:47+0200
current-owner: ai-maestro-orchestrator-agent
created-by: ai-maestro-orchestrator-agent
task-type: infra
approval-tier: 0
relevant-rules: []
npt: []
eht: []
blocked-by: []
release-via: none
---

# Reconcile the 8 complete/publish cards — backfill implementation-commits and run the publish lane

Board audit 2026-08-19 (during TRDD-8DH44UXH): 8 cards sit at `column: complete` with
`release-via: publish` — EKKIOYAO, 7MGYSHMN, 1F0LO1LX, QQY1PJZI, EYOV4I0A, 73OGGN69,
0DSR6WT4, 7I4OPLBA. Their work almost certainly shipped in already-published v1.13.x
releases, but NONE carries `implementation-commits:`, so tag-containment cannot be
checked mechanically (an empty SHA list makes `git merge-base --is-ancestor` vacuously
pass — measured, do not repeat that check without SHAs).

Task (atomic, per card ×8):
1. Backfill `implementation-commits:` — locate the landing commits via
   `git log --oneline -S`/commit-subject grep for the card id (commit-discipline puts
   the id in subjects).
2. Verify containment in the newest published tag (`git tag --list 'v1.13.*'` — beware
   lexical sort; v1.13.11 exists).
3. For contained cards: file ONE batch MANAGER approval request (§Y non-exempt) for
   `complete→publish→published` reconciliation, then archive as `published` with the
   3P-ZON-12 three writes.
4. Any card NOT contained in a published tag stays at `complete` and is reported.

Acceptance:
- [ ] all 8 cards carry non-empty `implementation-commits:`
- [ ] containment verdict recorded per card
- [ ] batch approval request filed (or the not-contained exceptions listed)
- [ ] approved cards archived as `published` via three-writes + `git mv`

## Approval log

## Notes and lessons learned
