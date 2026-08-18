---
trdd-id: 73OGGN69
title: Remove the dead skill-local duplicate of amoa_register_agent.py (audit C1)
column: todo
scope: project
project-id: ai-maestro-orchestrator-agent
created: 2026-08-18T19:56:41+0200
updated: 2026-08-18T19:56:41+0200
current-owner: ai-maestro-orchestrator-agent
created-by: ai-maestro-orchestrator-agent
task-type: refactor
approval-tier: 0
relevant-rules: []
external-refs: [ai-maestro TRDD-BRRJK57P]
npt: []
eht: []
blocked-by: []
release-via: publish
---

# Remove the dead skill-local duplicate of amoa_register_agent.py (audit C1)

Hub-verified finding C1 of the fleet plugin audit (ai-maestro TRDD-BRRJK57P, orchestrator
section), re-verified first-hand 2026-08-18 in this tree.

## Finding

`amoa_register_agent.py` exists at TWO paths:

- `scripts/amoa_register_agent.py` — the canonical copy; referenced by
  `commands/amoa-register-agent.md` and skill docs.
- `skills/amoa-remote-agent-coordinator/scripts/amoa_register_agent.py` — a skill-local copy
  invoked by nothing executable (grep for the skill-local path returns zero hits outside the
  file itself).

Two copies of the same basename drift silently: a fix lands in one and the other keeps the bug
while still looking authoritative (one-source-of-truth violation).

## Work

1. Diff the two copies; if the skill-local one carries any fix the canonical one lacks, port it
   to `scripts/amoa_register_agent.py` first.
2. Delete `skills/amoa-remote-agent-coordinator/scripts/amoa_register_agent.py` (git-tracked —
   commit before delete per RULE 0 is satisfied by history).
3. Sweep the whole tree for references to the deleted path (docs, skills, templates, tests) and
   repoint every hit at the canonical script — including the skill's own
   `references/document-storage-protocol.md` and `templates/protocols/*-part5-*` if they cite
   the local relative path.
4. Run the plugin test suite; ruff + mypy on touched files.

## Acceptance criteria

- [ ] Exactly ONE `amoa_register_agent.py` in the tree (`find . -name amoa_register_agent.py`
      → 1 hit).
- [ ] Zero references to the deleted path (`grep -rn "amoa-remote-agent-coordinator/scripts/amoa_register_agent"` → 0).
- [ ] Any unique fix from the deleted copy demonstrably ported (diff recorded in this card).
- [ ] Tests green; ruff + mypy clean.

## Approval log

## Notes and lessons learned
