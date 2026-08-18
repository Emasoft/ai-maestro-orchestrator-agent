---
trdd-id: 7I4OPLBA
title: Retire the dead stop-check entry point scripts/amoa_orchestrator_stop_check.py and repoint its docs (audit C5)
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

# Retire the dead stop-check entry point and repoint its docs (audit C5)

Hub-verified finding C5 of the fleet plugin audit (ai-maestro TRDD-BRRJK57P, orchestrator
section), re-verified first-hand 2026-08-18 in this tree.

## Finding

The live Stop hook (`hooks/hooks.json:12`) runs `python3 -m amoa_stop_check.main` (package
`scripts/amoa_stop_check/`). The pre-package entry point `scripts/amoa_orchestrator_stop_check.py`
STILL EXISTS and is still cited by at least 8 files: `tests/unit/test_amoa_orchestrator_stop_check.py`
and 6 skill docs (`amoa-two-phase-mode/README.md` + references, `amoa-orchestration-commands/README.md`
+ `references/python-scripts.md` + `references/op-stop-hook-enforcement.md`,
`amoa-orchestration-loop/references/stop-hook-behavior.md`). Docs teach a dead entry point;
two versions of the stop-check violate the one-version rule.

## Work

1. Confirm `amoa_stop_check/` (package) fully covers the old script's behavior — diff the
   logic; port anything the package lacks BEFORE deleting.
2. Delete `scripts/amoa_orchestrator_stop_check.py` and its dedicated unit test
   `tests/unit/test_amoa_orchestrator_stop_check.py` (its real coverage must exist in
   `test_amoa_stop_check_main.py` — extend that suite first if a case is unique).
3. Repoint every doc hit at `python3 -m amoa_stop_check.main` (full tree sweep per the
   breaking-change rule — prose references are invisible to tsc/lint/tests).
4. Run the plugin test suite; ruff + mypy on touched files.

## Acceptance criteria

- [ ] Old-script logic diffed against the package; unique behavior ported (recorded here).
- [ ] `scripts/amoa_orchestrator_stop_check.py` gone; unique test cases migrated to
      `test_amoa_stop_check_main.py` before its test file is removed.
- [ ] `grep -rn "amoa_orchestrator_stop_check"` → 0 hits tree-wide.
- [ ] hooks.json unchanged (already correct); tests green; ruff + mypy clean.

## Approval log

## Notes and lessons learned
