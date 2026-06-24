---
trdd-id: 03DYGXJW
title: Dedup amoa boilerplate (parse_frontmatter/EXEC_STATE_FILE/load_state) into shared module to clear jscpd >5%
column: backburner
created: 2026-06-24T17:09:03+0200
updated: 2026-06-24T17:09:03+0200
current-owner: plugin-fixer
task-type: refactor
priority: 2
relevant-rules: []
release-via: publish
delivery: direct-push
target-branch: main
test-requirements: [unit, lint, typecheck]
impacts: [ci-pipeline]
parent-trdd: TRDD-EKKIOYAO
external-refs: ["github.com/Emasoft/ai-maestro-orchestrator-agent/issues/23"]
---

# Dedup amoa boilerplate to clear the jscpd >5% CI Lint gate

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-06-24

**Why this is its own TRDD (deferred from the v2.147.1 migration TRDD-EKKIOYAO):**
The plugin's python duplication is **5.7% local / 5.82% CI**, over the canon jscpd threshold
of 5% (`.jscpd.json` minTokens=50, MegaLinter `COPYPASTE_JSCPD_ARGUMENTS: --threshold 5`).
The cause is boilerplate copy-pasted across ~29 orchestration scripts. The proper fix is
extracting it into ONE shared module and updating the importers — but that is a **risky
30-file refactor of the plugin's load-bearing orchestration scripts**, and the test suite
(10 files, 9 touching amoa scripts) covers only a fraction of the 29 importers, so the
extraction is **NOT fully test-verifiable**. Per the plugin-fixer dedup guardrail, this
balloons into a dedicated refactor — it must NOT be done inside the migration, and the gate
must NOT be muted / threshold-raised / `.mega-linter.yml`-edited (gaming).

**Measured duplication families (jscpd json report, python-only, canon config; dup-line
instances counting both sides; TOTAL = 1913):**
| Family | dup-line instances | % of dup | Recommended fix |
|---|---|---|---|
| `parse_frontmatter` + `EXEC_STATE_FILE = Path(".claude/orchestrator-exec-phase.local.md")` | 592 | 31% | Extract `parse_frontmatter()` + constant into `shared/amoa_state.py`; update the **29** scripts that `def parse_frontmatter` (12 also define `EXEC_STATE_FILE`). Note variants: `tuple[dict, str]` vs `tuple[dict[str, Any], str]`, some import yaml. Canonicalize to one signature. |
| `amoa_download.py` ↔ `skills/amoa-remote-agent-coordinator/scripts/amoa_skill_download.py` | 535 | 28% | Two near-identical ~445-line download/verify modules in DIFFERENT distribution scopes (top-level script vs skill-bundled, kept self-contained). Extract the shared body into `shared/amoa_download_core.py` with location-aware path math, OR accept the skill-bundling duplication and exclude one via `.jscpd.json` ignore IF the skill must stay self-contained (decide with owner). |
| `load_state`/`STATE_FILE_REL`/`COMPLETE_STATUSES` (orchestration-state) | 201 | 11% | Extract into `shared/amoa_state.py` alongside parse_frontmatter. `amoa_check_orchestration_phase.py` ↔ `amoa_orchestration_status.py` + a few more. |
| other | 585 | 30% | Smaller scattered clones (argparse blocks, sha256 helpers, report_writer-adjacent). Re-measure after the big three. |

**Lowest-risk path to GREEN:** removing ONLY the `parse_frontmatter` family (31%) drops 5.7%
→ ~3.9%, comfortably under 5%. So the minimal viable fix is `shared/amoa_state.py` plus
rewiring the 29 `parse_frontmatter` importers, **test-verified per file** — after each batch
of ~5 files run `pytest tests/`, `mypy`, and a smoke import of every touched script. The
download pair and load_state can follow for margin but are not strictly required for the gate.

**NEXT ACTION:** create `shared/amoa_state.py` exporting `EXEC_STATE_FILE` + a canonical
`parse_frontmatter(file_path) -> tuple[dict[str, Any], str]`; rewire the 29 importers in
batches of 5 with `pytest`+`mypy`+import-smoke between batches; re-run jscpd python-only to
confirm <5%; then re-run the full migration verify + publish a patch.

**Load-bearing facts / gotchas:**
- `shared/` is the existing home (`shared/report_writer.py`, `shared/thresholds.py`), imported
  via `sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shared"))` — works for
  `scripts/*.py` (parent.parent = plugin root) but NOT for `skills/.../scripts/*.py` (different
  depth) → the download-pair dedup needs different path math than the parse_frontmatter dedup.
- The 29 importers are NOT all test-covered → extraction needs import-smoke verification, not
  just the existing pytest suite.

## Approval log
- 2026-06-24T17:09:03+0200 — created as deferred NPT of the v2.147.1 migration (TRDD-EKKIOYAO);
  the migration leaves CI Lint RED on this gate until this lands. Tier-0 in-scope refactor.
