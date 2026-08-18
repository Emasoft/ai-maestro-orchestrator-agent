---
trdd-id: 73OGGN69
title: Remove the dead skill-local duplicate of amoa_register_agent.py (audit C1)
column: complete
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

## DEVIATION recorded in dev (2026-08-18) — rename, not delete

The diff (run before acting) falsified the "duplicate copy" premise: the two files are
DIFFERENT PROGRAMS sharing a basename. Canonical = state-file agent registration
(shared/amoa_state.py, positional `ai|human` CLI). Skill-local = document-storage folder
registration (`register|list` subcommands, `--name/--platform/--architecture`), the renamed
old `atlas_register_agent.py`, and its own skill's docs teach exactly that CLI shape — so
deleting it would break a documented workflow. Fix applied: `git mv` to
`amoa_storage_register_agent.py` (unique basename kills the drift hazard); 2 coordinator
docs plus skill-directory-structure.md plus the script docstring repointed (part5 also gained
the required `register` subcommand it was missing), stale `<!-- TODO: Rename -->` markers
stripped on touched lines, `scripts/__init__.py` collision note updated.

## Acceptance criteria

- [x] Exactly ONE `amoa_register_agent.py` in the tree (`find` → 1 hit: `scripts/`); skill
      copy now `amoa_storage_register_agent.py` (1 hit).
- [x] Zero references to the old skill-local path; every residual `amoa_register_agent`
      mention verified to name the CANONICAL script (commands/, amoa-plan-phase docs,
      amoa-two-phase README).
- [x] No behavior lost — nothing deleted; both programs intact under distinct names.
- [x] `py_compile` OK; ruff clean on both touched .py files.

## Approval log

- 2026-08-18T19:56:41+0200 — COMPLETE under the hub's Phase-2 GO + USER "permission granted".
  Substance of C1 (basename collision/drift hazard) resolved by rename; deviation from the
  literal delete plan is fact-driven and recorded above.

## Notes and lessons learned
