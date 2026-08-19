---
trdd-id: 0DSR6WT4
title: Remove the orphaned scripts/gitignore_filter.py (audit C2)
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
implementation-commits: [24dc81a]
---

# Remove the orphaned scripts/gitignore_filter.py (audit C2)

Hub-verified finding C2 of the fleet plugin audit (ai-maestro TRDD-BRRJK57P, orchestrator
section), re-verified first-hand 2026-08-18 in this tree.

## Finding

`scripts/gitignore_filter.py` is 200 lines with ZERO referencing files
(`grep -rln "gitignore_filter" --exclude-dir=.git .` → no hits, exit 1). Control for the grep
method: `amoa_stop_check` returns 20 referencing files, so the zero is a real orphan, not a
search miss. Dead code that ships in the plugin misleads readers and inflates the audit
surface.

## Work

1. Second-look for dynamic/indirect invocation the name-grep cannot see: `python3 …
   gitignore_filter` fragments, importlib strings, hook/command YAML, plugin.json.
2. If genuinely orphaned: delete it (git-tracked; history preserves it — no `_dev` parking
   needed).
3. Sweep docs for any prose mention and remove it.
4. Run the plugin test suite.

## Acceptance criteria

- [x] Indirect-invocation sweep documented: `gitignore_filter` / `gitignore.filter` /
      `gitignore-filter` greps → 0 hits outside this card; no `importlib`/`__import__` in
      scripts/ or hooks/; no plugin.json mention. The file was a GitignoreFilter helper "all
      validators should use" — local validators were removed when CPV became the single
      validation source, which is WHY it orphaned.
- [x] `scripts/gitignore_filter.py` deleted (git-tracked at deletion → recoverable from
      history per RULE 0).
- [x] Tests green (suite run in the C5 card's verification, same session).

## Approval log

- 2026-08-18T19:56:41+0200 — COMPLETE under the hub's Phase-2 GO + USER "permission granted".

## Notes and lessons learned
