---
trdd-id: 6B3K7S69
title: Read aimaestro_task_id from the architect design-handoff (orch #26 read-side, parse-half)
column: testing
scope: project
created: 2026-07-23T17:56:46+0200
updated: 2026-07-23T18:02:03+0200
current-owner: ai-maestro-orchestrator-agent
task-type: feature
approval-tier: 0
relevant-rules: []
external-refs: [orch#26, architect#7, ai-maestro#77]
blocked-by: []
implementation-commits: [45e409e]
---

# Read aimaestro_task_id from the architect design-handoff (orch #26 read-side, parse-half)

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-07-23

S Parse-half of orch#26. Architect (v2.11.0, architect#7) now stamps the AI-Maestro
epic id into the design-handoff AMP message as an **optional top-level `aimaestro_task_id`
key inside the message `content`** (sibling of `type`/`message`), in both the
`design_complete` and `handoff` message shapes. The orchestrator (AMOA) must READ it and
later attach its implementation child tasks under that epic via
`amp-kanban-create-task --parent "$EPIC"`, completing design→epic→child→issue traceability.

D This TRDD lands the READ/PARSE unit + the attach PROCEDURE doc. The live server round-trip
(children read back under the epic) is a DEPLOYMENT-time check that needs a live AI-Maestro
server + an AMCOS-spawned agent binding — it cannot run from a dev session, mirroring the
architect side's TRDD-364ccafc Phase 0. Not blocked by ai-maestro#46: the spec owner verified
(ai-maestro#77, 2026-07-23) that identity resolves via `AGENT_WORK_DIR/$PWD → name → uuid`;
the colliding address was display-only.

### NEXT ACTION
DONE for everything runnable from a dev session: helper + 11 unit tests (green), ruff+mypy
clean, and the read + `--parent` attach procedure documented (kanban-management PROCEDURE 5
+ design-handoff §2.9 receive note). The ONLY open item is the deployment-time live
round-trip (children read back under the epic), which needs a live AI-Maestro server + an
AMCOS-spawned agent binding — deferred, cannot run here.

### Load-bearing facts / contract (✓ verified against the architect's live templates)
- Key path: `content.aimaestro_task_id` (top-level of `content`, NOT under `content.data`).
  The shipped v2.11.0 template put it top-level of `content`; architect#7's original proposal
  showed `content.data` — the SHIPPED shape wins.
- Optional/additive: absent on older handoffs and whenever AI-Maestro is not in use →
  the orchestrator behaves exactly as today (unlinked breakdown). NO regression on absence.
- The id is an opaque string (architect example `PVTI_laDOABcd1234`, a GH-Projects-v2 item id).
  The parser must not assume a UUID shape.
- Attach mechanism (write-half): `amp-kanban-create-task "<child>" --parent "$EPIC" ...`
  (frozen verb; never a raw `/api/*` call — R23).

### SUPERSEDED — do NOT carry forward
- The earlier belief that #26's write-half is blocked by ai-maestro#46. The spec owner
  unblocked it (ai-maestro#77). The remaining gate on the write-half is a live-server
  round-trip, not #46.

## Scope

**In scope (this TRDD, parse-half + wiring doc):**
1. A single-responsibility, tested helper that extracts the optional `aimaestro_task_id`
   from a received design-handoff message `content`.
2. Documenting the read + `--parent` attach procedure in the orchestrator's kanban skill
   and the design-handoff receive template.

**Out of scope (deferred, deployment-time):**
- The live `amp-kanban-create-task --parent` round-trip verification (needs a live server +
  agent binding; parallels architect TRDD-364ccafc Phase 0). Recorded as a checklist item.

## Design

`extract_aimaestro_task_id(content)`:
- Accepts the message `content` as an already-parsed `dict` OR as its raw JSON `str`
  (AMP delivers `content` as a JSON string), parsing the str form once.
- Returns the `aimaestro_task_id` string (stripped) when present and non-empty.
- Returns `None` when the key is absent — the documented optional/additive semantics
  (NOT a silent-failure fallback; absence is a first-class valid state per orch#26).
- FAIL-FAST on genuine errors: content that is neither dict nor JSON-object → `TypeError`;
  the key present but not a non-empty string → `ValueError`. These are real data defects,
  not the optional-absent case, so they surface rather than mis-link a child task.

## Acceptance criteria
- [x] `extract_aimaestro_task_id` returns the id for both `design_complete` and `handoff`
      content shapes, given a dict and given a JSON string.
- [x] Absent key → `None` (no regression).
- [x] Present-but-empty / present-but-non-string → raises (fail-fast).
- [x] Non-object content → raises (fail-fast).
- [x] Unit tests cover every branch; pytest green (11 new, 122 total), ruff clean, mypy clean.
- [x] Kanban skill + design-handoff receive template document the read + `--parent` attach.
- [ ] (Deployment) children read back under the epic — deferred, live-server check.

## Notes and lessons learned
