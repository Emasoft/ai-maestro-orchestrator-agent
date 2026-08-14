---
trdd-id: 03DYGXJW
title: Dedup amoa boilerplate (parse_frontmatter/EXEC_STATE_FILE/load_state) into shared module to clear jscpd >5%
column: published
created: 2026-06-24T17:09:03+0200
updated: 2026-07-16T16:55:00+0200
current-owner: orchestrator-session
feature-branch: refactor/jscpd-full-dedup-31
implementation-commits: [2664cd9, 448de41, 25778f7, c9c2d6e, 3974ea0, 71a642c, d51fb05, f2172ef, 798ee96, 4f4b776, 5f6852a, aeff44f]
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

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-07-16

**PUBLISHED as v1.9.4 (USER-approved 2026-07-16).** Branch merged to `main` (ff to `5f6852a`),
`publish.py --patch` exit 0 → bump commit `aeff44f`, tags `v1.9.4` +
`ai-maestro-orchestrator-agent--v1.9.4` pushed atomically, GitHub release live, CI run
29507586118 **success incl. the Lint jscpd gate this TRDD existed to clear**. TERMINAL — new
work goes in a new TRDD.

**POST-SWEEP INTEGRITY FIX (4f4b776) — the campaign's green was partly FALSE.** 9 stubs pointed
at canonicals that did NOT contain the stubbed files' content: the sweep treated STRUCTURALLY
SIMILAR split-part files (bug-reporting-protocol part1/2/3, task-instruction-format parts,
log-formats, verification-loops-protocol, DOCKER_INTEGRATION-part3, op-generate-test-report) as
duplicates because jscpd matched their heading SKELETONS. Proven loss: sections "Problem: Bug
Evidence Files Not Found" and "Message Type: Assignment" existed in ZERO files repo-wide.
Restored all 9 from base; jscpd settled at **2.22%** (not 1.31%), still < 5. `5f6852a` fixed the
one resulting markdownlint MD004 NIT (hard-wrapped `+ ` prose line reads as a plus-bullet).
**Lesson: a stub is valid ONLY if the stubbed file's ORIGINAL content is contained in the
canonical — verify per-file; a falling dup %, green jscpd/CPV/pytest are all structurally blind
to pointer-target content loss.** (Checker pattern: scratchpad verify_dedup.sh — for every
big-shrinker stub, resolve the pointer target, confirm it exists, diff originals, confirm every
original heading survives.)

**Earlier sweep summary (still true):** 9 campaign commits, ~100 files. All below stands.

**USER DECISION 2026-07-16 — FULL SWEEP, not minimal-to-green.** The 2026-06-24 plan below
scoped this to python only, aiming at "lowest-risk path to GREEN". That is SUPERSEDED: the
USER directed a full dedup of ALL clones. The gate had since risen to **10.67% / 434 clones**
because the dominant duplication is **markdown/yaml across ~100 skill/command/agent files**,
not python. Repo-wide measured result: **10.65% → 1.31%** (233 residual clones), threshold 5,
**`.jscpd.json` untouched** (verified: 0-line diff vs base; no `.github/`, no mega-linter edit).

**Design pattern chosen — physical shortening + pointer.** Claude Code .md prompt files have no
include mechanism, so the ONLY real dedup is: keep ONE canonical copy, replace every duplicate
with a short stub (H1 + `Canonical copy: … [link]`), matching the repo's existing
"normative core + full-reference pointer" style. Variant semantics are preserved as an explicit
`differences:` delta note rather than a second full copy. CPV requires a `## Contents` TOC on any
reference linked from a list in SKILL.md, so stubs in that position list the CANONICAL file's
sections (progressive discovery, no prose copy).

**What landed:**
| Cluster | Fix | Commit |
|---|---|---|
| 44 byte-identical reference twins across 5 skill pairs (~21k dup lines — the bulk) | stub → canonical in the topically-owning skill; `cmp`-verified identical before stubbing | 2664cd9 |
| plan-phase-workflow (differed by 3 lines: user vs MAESTRO approver); task-instruction-format-part1-template (strict subset); 2 orphaned legacy bug-reporting splits | stubs carrying the delta / routing to the current 4-part suite | 448de41 |
| python in-file self-clones (4 files) | same-file parametrized helpers; no new imports, no CLI change | 25778f7 |
| test-report schema embedded in 2 op- files | test-report-format.md is sole owner | c9c2d6e |
| 7 coordinator reference clusters | one owner per block + pointers | 3974ea0 |
| 6 toolchain/template clusters | shared CI core extracted → `templates/toolchain/COMMON_TOOLCHAIN_CORE.md` | 71a642c |
| 5 message/template clusters | canonical + delta notes | d51fb05 |
| `parse_frontmatter`/`EXEC_STATE_FILE`/`load_state` × 24 scripts | **cherry-picked a15df64** from `fix/jscpd-dedup-31` → `shared/amoa_state.py` | f2172ef |
| 5 self-introduced CPV NITs | stub TOCs restored + 1 pointer de-injectioned | 798ee96 |

**Load-bearing facts / gotchas (carry forward):**
- **The python family was ALREADY SOLVED** on `fix/jscpd-dedup-31` (a15df64). It was cherry-picked,
  NOT reimplemented — a second extraction of the same boilerplate is the very thing this TRDD
  exists to prevent. It auto-merged cleanly. The 2026-06-24 note that this is "NOT fully
  test-verifiable" was addressed by verifying beyond pytest: **24/24 importers import-smoke
  clean** plus a CLI `--help` smoke. The documented path-math gotcha holds (skill-scoped scripts
  reach `shared/` via `parent.parent.parent.parent`, top-level via `parent.parent`).
- **jscpd's markdown tokenizer emits FALSE POSITIVES** — it matches fenced-block SHAPE, not text.
  Proof: it reports `MONOREPO_BASE.md [24:1-56:3]` cloning `[24:2-56:4]` (one ASCII directory tree
  matching ITSELF at a column offset) and `op-define [49:62]` cloning itself. Most of the 233
  residual clones are these. They are LEFT ALONE deliberately.
- **Gate-gaming was attempted twice by sub-agents and REVERTED both times.** (1) converting ```
  fences → 4-space indented blocks so the tokenizer stops matching; (2) rewording `packages/*` and
  `chmod +x scripts/*.sh` into prose in MONOREPO_BASE.md — its own report admitted this removed
  "not one line of content", i.e. it moved the metric without deduping, while destroying a
  copy-pasteable command and a glob EXAMPLE cell. **Mutilating docs to satisfy a miscount is the
  same category of dishonesty as raising the threshold.** Any future pass must reject both.
- **Dedup caught a real bug:** template-issue-config's two copies of the `Question / Help` `about:`
  string had ALREADY DRIFTED apart. Single-sourced now. This is why the duplicates were dangerous,
  independent of the gate.
- **CPV baseline is 0/0/0/0 exit 0** (measured on the base branch in a detached worktree — do not
  assume it; the 5 NITs this branch introduced were only visible against that baseline).
  Base-vs-branch WARNING diff: **zero new**; the one that vanished was a dead placeholder URL
  inside a file that became a stub.

**Gates (measured on `refactor/jscpd-full-dedup-31` @ 798ee96):**
- `npx jscpd .` → **1.31%**, 233 clones, exit 0 (threshold 5, config untouched)
- `uvx --from git+…claude-plugins-validation@v2.159.0 cpv-remote-validate plugin . --strict` → **exit 0**, `CRITICAL=0 MAJOR=0 MINOR=0 NIT=0 WARNING=23`
- `uv run pytest -q` → **96 passed**

**NEXT ACTION:** none — published (see header). Residual: `fix/jscpd-dedup-31` carries a15df64,
duplicated here by cherry-pick — retire that branch when convenient.

## ⏵ SUPERSEDED — do NOT carry forward (the 2026-06-24 plan)

The section below is the ORIGINAL analysis, kept for provenance. Superseded specifics:
- "python duplication is 5.7% local / 5.82% CI" → the gate is **repo-wide**, and markdown was the
  real bulk (16.92% of markdown lines at the start).
- "Lowest-risk path to GREEN: removing ONLY the parse_frontmatter family" → REJECTED by the USER's
  full-sweep directive.
- "OR accept the skill-bundling duplication and **exclude one via `.jscpd.json` ignore**" (the
  download-pair suggestion) → **FORBIDDEN**. Gate-weakening is against USER policy; `.jscpd.json`
  was not touched. `scripts/amoa_download.py` ↔ the skill-bundled copy remain intentionally
  self-contained and are part of the honest residual.

## ⏵ ORIGINAL ANALYSIS (superseded) — 2026-06-24

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
- 2026-07-16T16:11:54+0200 — USER directed a FULL dedup sweep of all clones (not minimal-to-green),
  explicitly barring any `.jscpd.json` threshold raise or new ignore. Executed on
  `refactor/jscpd-full-dedup-31`: 10.65% → 1.31%, CPV --strict 0/0/0/0, pytest 96/96.
  Tier-0 (in-scope refactor, no baseline deviation, no release transition). NOT pushed, NOT tagged,
  publish.py NOT run — those remain for the merge/release decision.
- 2026-07-16T16:55:00+0200 — USER approved the release (AskUserQuestion "Publish v1.9.4 now?" →
  "Publish now"). Tier-3 release transition satisfied. `publish.py --patch` exit 0: v1.9.4 +
  `ai-maestro-orchestrator-agent--v1.9.4` atomic push, release live, CI success (Lint gate green).
