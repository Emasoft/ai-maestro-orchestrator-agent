---
trdd-id: 66ea1bb1-0982-4d6b-b680-5b15ed1388ad
title: Canonical-pipeline migration to CPV 2.136.1 standard — publish v1.9.2
column: dev
created: 2026-06-22T02:43:17+0200
updated: 2026-06-22T02:43:17+0200
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
external-refs: ["github.com/Emasoft/ai-maestro/issues/44", "github.com/Emasoft/ai-maestro-orchestrator-agent/issues/22", "github.com/Emasoft/ai-maestro-orchestrator-agent/issues/23"]
---

# Canonical-pipeline migration to CPV 2.136.1 standard — publish v1.9.2

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-06-22

**Goal:** bring `ai-maestro-orchestrator-agent` publish pipeline to the current CPV
canonical standard (CPV 2.136.1), preserving the by-design **remote-validation**
profile, then publish v1.9.2 with CI green. USER-APPROVED (fleet #44).

**Pipeline profile:** `remote-validation` (de-vendored validators; `publish.py` drives
the remote `cpv-remote-validate` gate). The canon publish.py template must NOT replace it.

**Baseline (HEAD 6b91c0f, v1.9.1, clean tree):**
- `CLAUDE_PRIVATE_USERNAMES=runner uvx ...@v2.136.1 cpv-remote-validate plugin . --strict`
  → CRITICAL=0 MAJOR=0 MINOR=0 NIT=0 WARNING=25 (exit 0). All 25 WARNINGs are
  `RC-PIPELINE-DRIFT-001` (canon-pipeline drift).
- Plugin LACKS canon `ci.yml`; still has old `validate.yml` + `release.yml` + `notify-marketplace.yml`.
- `pyproject.toml` uses `[dependency-groups].dev`, NOT `[project.optional-dependencies].dev`.
- `publish.py` (remote-validation profile) has NO idempotency helpers AND calls the
  RETIRED `cpv-remote-validate lint` at Step 4 (a real publish would FAIL there — `lint`
  is gone from the launcher in v2.136.1; CHECK-23 BLOCKER).
- `ci-preflight` is NOT in the v2.136.1 remote launcher → CI parity proved by the real
  publish + `gh run watch`, not a local preflight.

**NEXT ACTION:** STEP 1 — run `standardize --fix --force-templates`.

**Plan (ordered):**
1. STEP 1 — `standardize --fix --force-templates` (installs canon ci.yml, updates release.yml/cliff.toml/etc; overwrites publish.py).
2. STEP 2a — `git checkout HEAD -- scripts/publish.py` (restore remote-validation publish.py).
3. STEP 2b — `pyproject.toml`: `[project.optional-dependencies].dev = ["pytest","ruff","mypy"]` + `uv lock`.
4. STEP 2c — `CLAUDE_PRIVATE_USERNAMES: runner` in ci.yml AND release.yml.
5. STEP 2d — `git rm .github/workflows/validate.yml`.
6. STEP 3 — fold idempotency into kept publish.py (remote-version baseline, skip-bump/commit/tag guards, push always) + fix retired `lint` Step 4 → drop it (Step 5 already does `plugin --strict`).
7. STEP 4 — verify with exact CI command (0 CRITICAL/MAJOR/MINOR + dry-run + interrupted-publish sim).
8. STEP 5 — `publish.py --patch` → v1.9.2; `gh run watch` all runs green; roll forward on failure (no re-tag).
9. STEP 6 — post from→to on ai-maestro#44; update orchestrator#22 (done) + #23 (idempotency folded).

**Load-bearing facts / gotchas:**
- Pre-push hook (process-ancestry) BLOCKS direct `git push` — push ONLY via publish.py.
- This plugin publishes directly on `main` (roll-forward, no PR). Roll forward on CI failure — never re-tag (AMAMA went 2.12.1→2.12.5).
- KNOWN FLAKE: Release post-hoc CPV gate can transiently hang ~15min then pass on `gh run rerun` — transient GitHub-integrity stall, NOT a failure; re-run, do NOT bump timeout-minutes.
- Stage files BY NAME; record WHY in commit msg + code comments.
- The 4 MANAGER fixes (2a-2d) ARE the hand-applied static remediation of §6 CIP-1..5.

**SUPERSEDED — do NOT carry forward:** (none yet)

**Durable artifacts to read before acting:**
- reports/cpv-canon-migration/20260622_024110+0200-canon-migration.md (this run's full report)
- CPV pipeline-migration.md §4 (idempotency) + §6 (CI-parity defects)
- canonical-pipeline-migration-checklist.md (87-check exit gate)

## Background

Fleet umbrella Emasoft/ai-maestro#44. AMAMA (MANAGER, v2.12.5) is the exemplar and
already paid ~5 publishes to find the canon-template defects; this migration pre-empts
all of them. orchestrator#22 tracks this migration; orchestrator#23 tracks the publish.py
idempotency fix (folded in here).
