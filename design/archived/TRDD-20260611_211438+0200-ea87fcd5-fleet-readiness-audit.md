---
trdd-id: ea87fcd5-755b-414d-8934-c859329de53a
title: Fleet-readiness audit — migrate ORCHESTRATOR to 3-pillars + memory, close 13 governance gaps
column: published
created: 2026-06-11T21:14:38+0200
updated: 2026-06-12T01:30:00+0200
current-owner: orchestrator
assignee: orchestrator
priority: 1
severity: HIGH
effort: XL
labels: [governance, fleet-readiness, 3-pillars, memory, r6v3]
task-type: refactor
parent-trdd: null
npt: []
eht: []
blocked-by: []
relevant-rules: [1]
release-via: publish
delivery: direct-push
target-branch: main
must-pass-tests-before-merge: true
publish-target: ai-maestro-plugins
publish-channel: stable
test-requirements: [unit, lint, typecheck]
audit-requirements: []
review-requirements: [human-review]
impacts: [config-schema, ci-pipeline]
attempts: 0
last-test-result: pass
implementation-commits: [ef9c564, 5353881, b4ff34f, 3a7691b, 43bdb66]
published-version: 1.8.0
published-at: 2026-06-12T01:30:00+0200
external-refs: ["github.com/Emasoft/ai-maestro-orchestrator-agent/issues/13"]
---

# TRDD-ea87fcd5 — Fleet-readiness audit (orch issue #13)

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-06-11

**What this is:** the MANAGER (`ai-maestro-assistant-manager-agent`) filed a 13-verdict
governance work order on `ai-maestro-orchestrator-agent#13`. USER authorized executing it
**fully**, phased, publish **gated on USER approval**. This TRDD is the spec + tracker.

**Current state:**
- CPV stream (separate): DONE — FP issues filed upstream (`claude-plugins-validation#100`, `#101`); CPV strict gate = `CRITICAL=0 MAJOR=0 MINOR=0 NIT=0`.
- Audit Phases 1–4 + memory-migration: DONE + verified. **All 13 verdicts M1–M13 closed.**
  - P1 (R6 v3 docs M11/M6/M7d/M4/M5), P2 (dialog loops M7a/b/c), P3 (PRRD project-id + 7 SILVER, plugin dep, M9/M10/M13), P4 (M12: 108 unit tests green; found+fixed a real tz crash in `amoa_check_polling_due.py`; verified the wired Stop hook works).
  - Memory: recall/write already on LOCAL scope (`~/.claude/projects/<slug>/memory/`); retired the `design/memory` scaffolding; init now scaffolds the 4-zone TRDD structure (ratified 3-scope convention).
  - Commits: `ef9c564` (governance+dialog), `5353881` (PRRD+manifest+skills), + the tests/bugfix/structure commit (this set).
- MANAGER (on #13) confirmed: kanban framing RATIFIED, unpinned `[ai-maestro-plugin]` dep OK, will verify the release.

**STATUS: DONE — published v1.8.0** (USER approved the minor bump). Full gate passed end-to-end (CPV strict 0/0/0/0, 108 tests, consistency OK); release commit `43bdb66`; release https://github.com/Emasoft/ai-maestro-orchestrator-agent/releases/tag/v1.8.0. Per-verdict resolution table posted on #13 (comment 4698153886) for MANAGER verification. No further action — monitoring #13 for the MANAGER's ack/close.

**Load-bearing facts / canonical models (the SPEC):**
- **R6 v3 comm graph:** COS guards the **team boundary** only. Within-team `ORCH ↔ ARCH/MEMBER/INT` are **DIRECT** edges. MANAGER reaches team-internal agents **only via COS**. The persona (`agents/ai-maestro-orchestrator-agent-main-agent.md`) holds the authoritative R6 v3 text (M6 = ✓ there) — doc edits MUST match it; the docs are the stale copies.
- **Column ownership (M7d):** ORCH owns the **pre-PR green-light** only; **INTEGRATOR owns the `column→completed` flip** after validating the merged PR satisfies the TRDD. Nobody self-marks completed.
- **Board reconciliation (M4):** the TRDD `column:` pipeline is the **authoritative lifecycle**; the GitHub Projects 8-column board is its **visual projection**. Define the lossless column mapping + sync rules + tie-break (**TRDD wins**). Mirrors the framing the COS adopted on `chief-of-staff#17`.
- **Three dialog loops (M7a/b/c):** (a) task-comprehension handshake — extend question set with *files/domains to be touched* (single-writer ownership check) + *anticipated NPT/EHT*; (b) in-dev MEMBER⇄ORCH loop — consolidate (currently fragmented across 3 files); (c) pre-PR gate — add the INT-token-protection rationale + close the "status-only pre-PR" backdoor.
- **Publish:** `publish.py --patch|--minor|--major`; runs full CPV strict gate; `--dry-run` stops before bump/commit/push. **NEVER publish without explicit USER OK.**
- **GitHub self-id:** every issue/comment/PR body leads with "I'm the Claude responsible for the ai-maestro-orchestrator-agent project."
- **No-exempt:** CPV findings → devitalize/remove or report as FP upstream; NEVER request an allowlist/exempt.

**Coordination (standing):** MANAGER owns the 3-pillars (TRDD/PRRD/kanban) → coordinate on `#13`. JANITOR (`ai-maestro-janitor`) owns the memory system → coordinate on `janitor#18` (path convention) + `#16` (memgrep). Monitor the fleet repos' open issues.

**SUPERSEDED — do NOT carry forward:** ✗ "ORCH moves task to `done`" (FULL_PROJECT_WORKFLOW Step ~19) → replaced by "INT flips `completed`". ✗ AMAMA↔AMOA direct edges (ROLE_BOUNDARIES v1.6.8) → replaced by R6 v3 (via COS).

**Durable artifacts to read before acting:**
- `ai-maestro-orchestrator-agent#13` — the work order (verdicts M1–M13, fix priority, acceptance).
- `ai-maestro-chief-of-staff#17` — the COS's completed equivalent (quality bar / reference).
- `reports/cpv-fp-reconstruction/20260611_205012+0200-cpv-false-positives.md` — CPV FP evidence.

---

## Verdicts (M1–M13) and resolution status

| # | Verdict (audit) | Phase | Status |
|---|---|---|---|
| M1 | no `dependencies:` in plugin.json; AMP dep prose-only | 4 | pending |
| M2 | PRRD: `project-id:` absent; SILVER empty | 4 | pending |
| M3 | `design/tasks/` absent; no TRDDs; choice undocumented | 0/4 | structure ✓; doc pending |
| M4 | TWO BOARDS, lossy STATUS_MAPPING | 2 | pending |
| M5 | add explicit "never self-approve" one-liner | 2 | pending |
| M6 | R6 v3 ✓ in main agent — but see M11 | 1 | pending |
| M7a | extend interview set (files/domains + NPT/EHT) | 3 | pending |
| M7b | consolidate in-dev/design-change loop (3 files) | 3 | pending |
| M7c | pre-PR gate: INT-token rationale + close status-only backdoor | 3 | pending |
| M7d | FULL_PROJECT_WORKFLOW gives final `done` to ORCH; INT owns `completed` | 1 | pending |
| M8 | clean | — | n/a |
| M9 | no TRDD file-locking / domain-claim; NPT/EHT collision | 4 | pending |
| M10 | minor AMCOS-name/title conflation in templates | 4 | pending |
| M11 | CRITICAL — ROLE_BOUNDARIES + FULL_PROJECT_WORKFLOW show AMAMA↔AMOA direct (bypass COS) | 1 | pending |
| M12 | PARTIAL — blocking hooks (Task PreToolUse on EVERY Task call) + 15 commands + sync untested | 5 | pending |
| M13 | move authoring-guideline orphans out or justify | 4 | pending |

## Phase plan (≤5 files/phase where practical; verify between phases; publish gated)

- **Phase 0 — setup:** 4-zone `design/` + this TRDD. ✓ DONE.
- **Phase 1 — R6 v3 governance docs (M11/M6, M7d, M4, M5):** rewrite `docs/ROLE_BOUNDARIES.md` to R6 v3; fix `docs/FULL_PROJECT_WORKFLOW.md` (R6 v3 + INT-owns-completed + board projection + never-self-approve); `docs/STATUS_MAPPING.md` lossless mapping.
- **Phase 2 — dialog loops (M7a/b/c):** `skills/amoa-implementer-interview-protocol` + interview-templates + verification-loops.
- **Phase 3 — PRRD + manifest + misc (M1/M2/M3-doc/M9/M10/M13):** PRRD `project-id:` + real SILVER rules; plugin.json `dependencies`; document no-local-TRDD; domain-claim protocol; orphan cleanup; AMCOS name fixes.
- **Phase 4 — tests (M12):** Task PreToolUse blocking hook FIRST, then 15 commands + `amoa_sync_kanban.py`. Delegate to python-test-writer (explicit counts), no mocks.
- **Phase 5 — verify + publish:** full CPV dry-run gate; run test suite; **ASK USER** → `publish.py`; reply on #13 with per-verdict resolution table + version.

## Coordination log
- 2026-06-11 — Acked the MANAGER on #13 (executing full work order; raised kanban-framing + dep-pinning deferral, aligned to COS #17).
