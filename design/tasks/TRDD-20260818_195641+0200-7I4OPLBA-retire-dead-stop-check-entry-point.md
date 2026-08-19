---
trdd-id: 7I4OPLBA
title: Retire the dead stop-check entry point scripts/amoa_orchestrator_stop_check.py and repoint its docs (audit C5)
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
implementation-commits: [c7a6dbe]
---

# Retire the dead stop-check entry point and repoint its docs (audit C5)

Hub-verified finding C5 of the fleet plugin audit (ai-maestro TRDD-BRRJK57P, orchestrator
section), re-verified first-hand 2026-08-18 in this tree.

## Finding

The live Stop hook (`hooks/hooks.json:12`) runs `python3 -m amoa_stop_check.main` (package
`scripts/amoa_stop_check/`). The pre-package entry point `scripts/amoa_orchestrator_stop_check.py`
STILL EXISTS and is still cited by at least 8 files: `tests/unit/test_amoa_orchestrator_stop_check.py`
and 6 skill docs (`amoa-two-phase-mode/README.md` with its references;
`amoa-orchestration-commands/README.md` with `references/python-scripts.md` and
`references/op-stop-hook-enforcement.md`;
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

- [x] Old-script logic diffed against the package. Discovery: the old script read
      `.ai-maestro/orchestration-state.json`; the package deliberately reads
      `.claude/orchestrator-{plan,exec}-phase.local.md` instead — a designed state-source
      migration, so the JSON-hook logic is SUPERSEDED, not missing (the JSON state file
      itself stays alive for 6 other scripts: amoa_orchestration_status, amoa_check_plan_phase,
      amoa_check_orchestration_phase, amoa_sync_github_issues, amoa_compile_replacement_context,
      amoa_confirm_replacement). Nothing to port to the hook.
- [x] Old script + its test file removed; the 4 phase-behavior cases worth keeping were ported
      FIRST to `test_amoa_stop_check_main.py` against the package's real state mechanism
      (plan-phase block, plan-phase allow, corrupt-state fail-safe, block-output shape) —
      assertions derived from phase.py source, not guessed.
- [x] Doc sweep: 18 lines across 10 skill files repointed to `python3 -m amoa_stop_check.main`;
      `grep -rn "amoa_orchestrator_stop_check"` → 0 hits outside deliberate historical notes
      (main.py provenance docstring, this card, the test-file header — each marked "removed").
- [x] hooks.json unchanged; suite 196 passed; ruff + mypy clean (also registered PRRD S9.1 in
      test_prrd_citation_integrity RULE_BODY_HASHES, caught by the suite).

## Approval log

- 2026-08-18T19:56:41+0200 — COMPLETE under the hub's Phase-2 GO + USER "permission granted".

## Notes and lessons learned
