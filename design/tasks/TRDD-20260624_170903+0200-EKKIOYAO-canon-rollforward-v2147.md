---
trdd-id: EKKIOYAO
title: Canonical-pipeline roll-forward to CPV v2.147.1 — re-pin @main, fix mypy/markdownlint, publish v1.9.3+
column: dev
created: 2026-06-24T17:09:03+0200
updated: 2026-06-24T17:09:03+0200
current-owner: plugin-fixer
assignee: plugin-fixer
task-type: infra
priority: 2
relevant-rules: []
release-via: publish
delivery: direct-push
target-branch: main
publish-target: ai-maestro-plugins
test-requirements: [lint, typecheck]
impacts: [ci-pipeline]
npt: [TRDD-03DYGXJW]
external-refs: ["github.com/Emasoft/ai-maestro/issues/44", "github.com/Emasoft/ai-maestro-orchestrator-agent/issues/22", "github.com/Emasoft/ai-maestro-orchestrator-agent/issues/23"]
---

# Canonical-pipeline roll-forward to CPV v2.147.1 — publish v1.9.3+

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-06-24

**Goal:** roll the orchestrator-agent pipeline forward from the stale CPV v2.136.1 canon
(shipped in v1.9.2) to the current **CPV v2.147.1** canon, fixing v1.9.2's RED CI, then
publish v1.9.3+ with CI GREEN. USER-DIRECTED (fleet #44).

**Why v1.9.2 CI is RED:**
1. v2.136.1 canon `ci.yml`/`release.yml` pin `cpv-remote-validate@main`; the CI runner
   cannot `git fetch …@main` (`× Failed to resolve --with requirement … Git operation failed`).
   FIX: v2.147.1 canon pins `@v2.147.1` instead → `standardize --force-templates` re-pins.
2. CI Lint (MegaLinter/jscpd): 5.82% > 5% python duplication from `parse_frontmatter`/
   `EXEC_STATE_FILE`/`load_state` boilerplate copy-pasted across ~29 scripts. → NPT TRDD-03DYGXJW.

**Pipeline profile:** resolves to `standard` (no `cpv.pipeline_profile` override in manifest),
BUT the v2.147.1 canon `publish.py` template is profile-aware and **already carries** the
by-design remote-validation logic (`_read_remote_version` ×4, `cpv-remote-validate` +
`PLUGIN_SKIP_GITHUB_INTEGRITY` ×4) AND the issue-#143 jscpd gate (×19). So adopting the
canon template is a strict SUPERSET — it preserves #23 idempotency + retired-lint removal AND
adds the jscpd gate. VERIFIED on a throwaway copy (1859-line template vs 1649-line current).

**Baseline (HEAD 58e3575, v1.9.2, clean tree), `…@v2.147.1 cpv-remote-validate plugin . --strict`:**
- CRITICAL=0 MAJOR=0 MINOR=18 NIT=1 WARNING=27.
- 18 MINOR = mypy `no-any-return` (+1 `annotation-unchecked`) across ~10 scripts — these now
  BLOCK --strict (v2.147.1 surfaces them; v2.136.1 did not red-light them the same way).
- 1 NIT = markdownlint MD012 (CHANGELOG.md:11 multiple consecutive blank lines).
- 27 WARNING = CA-01..CA-06 cache (non-blocking) + RC-PIPELINE-DRIFT-001.
- Test suite: 91 passed (green baseline).

**CRITICAL canon delta vs v2.136.1 (issue #140):** the v2.147.1 canon CI **must NOT carry
`CLAUDE_PRIVATE_USERNAMES`** in any workflow step (a CI runner has no local username to
protect; seeding it with the public owner makes CPV flag every owner URL/email as a CRITICAL
leak). Instead validate steps set `PLUGIN_SKIP_GITHUB_INTEGRITY: "1"` + a `timeout-minutes`.
→ `--force-templates` rewrites the workflows to this shape, SUPERSEDING the prior
`CLAUDE_PRIVATE_USERNAMES: runner` fix. This is correct per the prompt ("unless the v2.147.1
canon supersedes them").

**NEXT ACTION:** run `standardize_plugin.py --fix --force-templates` (v2.147.1) → adopt canon
ci.yml/release.yml/notify-marketplace.yml/.mega-linter.yml/.jscpd.json/cliff.toml/pre-push/
publish.py/cpv_network_resilience.py + re-pin @main→@v2.147.1; then fix the 18 mypy + 1
markdownlint; verify --strict clean (modulo the jscpd dup deferred to TRDD-03DYGXJW); run the
87-check matrix; publish; watch CI to green.

**SUPERSEDED — do NOT carry forward:**
- ✗ "publish.py is the remote-validation profile and must NOT be replaced by the canon template"
  (from v2.136.1 TRDD-66ea1bb1). v2.147.1 canon template IS the remote-validation superset →
  ADOPT it, don't restore HEAD.
- ✗ "Keep `CLAUDE_PRIVATE_USERNAMES: runner` in CI." v2.147.1 canon issue-#140 forbids it → removed.

**Durable artifacts to read before acting:**
- Report: $MAIN_ROOT/reports/cpv-canon-migration/<ts>-upgrade-v2147.md
- 87-check matrix: CPV cache references/canonical-pipeline-migration-checklist.md
- NPT: design/tasks/TRDD-…-03DYGXJW-dedup-amoa-boilerplate.md

## Plan

1. `standardize_plugin.py --fix --force-templates` (v2.147.1) — adopt canon, re-pin CPV ref.
2. Restore/verify by-design preservation: confirm publish.py still has `_read_remote_version`,
   no standalone retired `cpv-remote-validate lint`, jscpd gate present; confirm 42 prior
   markdownlint NITs stay clean.
3. Fix 18 mypy `no-any-return` MINORs (add explicit casts/typed returns) + 1 markdownlint MD012.
4. `…@v2.147.1 cpv-remote-validate plugin . --strict` → 0 C/M/MINOR/NIT (jscpd dup deferred).
5. 87-check matrix BLOCKER+MAJOR pass.
6. `publish.py --patch` → v1.9.3; `gh run watch` all runs to GREEN; roll forward on red.
7. Update fleet #44 + orchestrator-agent #22/#23.

## Approval log
- 2026-06-24T17:09:03+0200 — USER-DIRECTED roll-forward (fleet #44). No approval gate.
