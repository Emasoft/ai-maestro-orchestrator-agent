---
prrd-version: 1.1
updated: 2026-06-11T21:42:49+0200
project: ai-maestro-orchestrator-agent
project-id: ai-maestro-orchestrator-agent
canonical-source: design/requirements/PRRD.md
mirrors: []
---

# Project Requirements & Rules — ai-maestro-orchestrator-agent

ORCHESTRATOR role plugin (AMOA) — task distribution, kanban, red-column management.

## §0. Canonical source + copies

| Path | Role | Update strategy |
|---|---|---|
| `design/requirements/PRRD.md` | **CANONICAL** for this project | Edit first. Bump `prrd-version:`. Update `updated:`. |

## §I. How to read this document

Rule citation form: `PRRD G<n>.<v>` (golden, user-set) or `PRRD S<n>.<v>`
(silver, manager-mutable). Rule numbers are globally unique across G/S;
promote/demote flips the letter without changing the number. The
`get-prrd.py <n>` script returns a rule's text by bare number. Full
spec: `~/.claude/rules/prrd-design-rules.md`.

## §II. TRDD location and design folders

TRDDs for this project are git-tracked under `design/tasks/` (NOT in
`docs_dev/` or any gitignored path) on the v2 `column:` schema. The
project carries the full four-zone design layout — `design/proposals/`
(awaiting approval, `column: proposal`), `design/tasks/` (authorized
open work, `column: planned`→…), `design/refused/` (never-approved
proposals), and `design/archived/` (terminal `completed`/`cancelled`/
`superseded`). A TRDD moves between zones with `git mv` on every
approve / refuse / complete decision so each zone stays an accurate
index. Full lifecycle: `~/.claude/rules/trdd-approval-tiers.md`.

## 🥇 GOLDEN — set by the USER (immutable to MANAGER)

- **G1.1** — Every agent that writes to GitHub (issue, issue comment, PR, PR comment, PR review, discussion, release note) MUST begin the body with a one-line self-identification of which agent/role/plugin authored it, because all AI Maestro agents share the single human-owner GitHub identity (the owner's gh CLI auth). Recommended leading line: _Posted by the Claude developing **<plugin-or-role>** (via the shared @owner gh auth)._ Commit messages SHOULD carry an `Agent: <role>` trailer.

## 🥈 SILVER — MANAGER-mutable (agents propose via COS)

- **S2.1** — ORCHESTRATOR MUST run the RED (blocked) column priority sweep (`kanban.py --red`) at least once per orchestration session and again whenever a `blocked-by:` edge is added or cleared; for each blocked TRDD it raises `priority:` toward `1` in proportion to how many other TRDDs that blocker unblocks, assigns any unassigned blocker immediately, and recurses into transitively-blocked blockers first. Red-column priority bumps are exempt (no MANAGER approval) per the exempt-operations matrix.
- **S3.1** — Re-assigning a TRDD between MEMBERs of the SAME team is ORCHESTRATOR's to decide directly (exempt); the new `assignee:` MUST match the TRDD's `task-type:` skill requirement and respect the target MEMBER's current capacity (`kanban.py --group-by assignee`). Re-assigning a TRDD ACROSS teams is non-exempt and MUST be routed to MANAGER via the team's CHIEF-OF-STAFF — ORCHESTRATOR never reassigns across team boundaries unilaterally.
- **S4.1** — The TRDD `column:` pipeline in `design/tasks/` is the AUTHORITATIVE project lifecycle; the GitHub Projects board is its visual projection only. ORCHESTRATOR MUST keep the two in sync via the lossless column mapping in `docs/STATUS_MAPPING.md`, syncing after every column transition. When the board and the TRDD frontmatter disagree, **the TRDD wins** — the board is corrected to match the TRDD, never the reverse.
- **S5.1** — Single-writer-per-domain: every mutable surface in `design/` (each TRDD `.md` file, the PRRD, the kanban projection) has EXACTLY ONE owning instance at a time. An ORCHESTRATOR instance that needs to write a domain it does not own MUST either delegate the edit to the owner or take an explicit claim before writing; concurrent blind writes to the same file are forbidden. The TRDD's `current-owner:` field records the present write-lock holder, and the coordination fields (`column:`, `assignee:`) are the only fields a non-owner may mutate.
- **S6.1** — When ORCHESTRATOR (or an ARCHITECT it coordinates) authors derived NPT/EHT child TRDDs, each child MUST declare the files/domains it will touch in its body and MUST NOT overlap the write-domain of a sibling or parent TRDD that is concurrently in a working column. Before creating a derived TRDD, ORCHESTRATOR checks the open TRDDs in `design/tasks/` for a domain collision; on collision it serialises the children (one `blocked-by:` the other) or merges them rather than letting two instances write the same domain in parallel.
- **S7.1** — ORCHESTRATOR owns the PRE-PR GREEN-LIGHT only: the assigned MEMBER MUST clear "I believe it's done — PR now?" with ORCHESTRATOR before opening a PR or notifying the INTEGRATOR, and ORCHESTRATOR verifies the work substantively (not a status-flag-only check) to protect INTEGRATOR tokens from premature PRs. ORCHESTRATOR does NOT flip `column:` to `completed`; the INTEGRATOR owns the `→ completed` transition after validating the merged PR actually satisfies the TRDD. No agent self-marks its own work `completed`.
- **S8.1** — The three dialog loops are ORCHESTRATOR-owned and run on DIRECT within-team edges (R6 v3): (a) the task-comprehension handshake — the MEMBER MUST restate the task, name the files/domains it will touch (single-writer check) and the anticipated NPT/EHT, and resolve every ambiguity/risk before coding; (b) the in-dev MEMBER⇄ORCH issue loop — raised immediately on any blocker, with ORCHESTRATOR pulling in ARCHITECT (design) or INTEGRATOR (CI/merge) rather than improvising around a design flaw; (c) the pre-PR gate (S7.1). ORCHESTRATOR reaches ARCHITECT / MEMBER / INTEGRATOR directly; only cross-team and MANAGER-bound traffic routes through the CHIEF-OF-STAFF.
