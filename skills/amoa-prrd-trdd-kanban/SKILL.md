---
name: amoa-prrd-trdd-kanban
description: "ORCHESTRATOR's role in the PRRD / TRDD / Kanban workflow. Use when ORCH claims TRDDs from todo, delegates design to ARCHITECT, assigns dev work to MEMBERs, manages the RED (blocked) column priority, or coordinates AMP messages with the team."
allowed-tools: "Bash(python3:*), Bash(get-prrd.py:*), Bash(findprrd.py:*), Bash(findtrdd.py:*), Bash(kanban.py:*), Bash(amp-send:*), Read, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

## Overview

This is the ORCHESTRATOR's role-specific layer of the PRRD / TRDD /
Kanban model. For the universal mechanics, see `prrd-trdd-kanban` in
`ai-maestro-plugin`.

## Approval discipline

Check the **prrd-trdd-kanban** universal skill's `exempt-operations.md`
reference (bundled in ai-maestro-plugin) BEFORE triggering any transition. ORCH's
**exempt** transitions (no MANAGER approval): `dispatch → dev`
(assignment), red-column priority bumps, within-team reassignment,
status broadcasts to COS/MANAGER. ORCH's **non-exempt** (request
MANAGER approval via COS): cross-team TRDD reassignment, escalating
to `human_review`, force-`failed` of stuck TRDDs. Conservative
default — when unsure, request approval.

ORCHESTRATOR is the team's traffic controller and **owns the red
column**. The red column — TRDDs whose `blocked-by:` list is non-empty
— is the fundamental source of project delays. ORCH's central
responsibility is to MINIMIZE the time TRDDs spend there by bumping
the priority of TRDDs that unblock the most others.

## Columns ORCH owns

| Column | Ownership detail |
|---|---|
| `todo` | ORCH claims promoted TRDDs from AMAMA; the next step is delegating to ARCHITECT for design. |
| `dispatch` | ORCH receives full TRDDs from ARCHITECT; assigns each to a specific agent (sets `assignee:`) and moves to `dev`. |
| `blocked` 🔴 | ORCH watches the RED column constantly. Bumps priority of blockers; pings owners of stuck TRDDs. |

ORCH also reads (but does not own) `dev`, `testing`, `ai_review`,
`human_review` — for status reporting upward.

## Transitions ORCH triggers

- **#3** `todo → design` — delegate to ARCHITECT (AMP-send via COS)
- **#6** `dispatch → dev` — set `assignee:`, AMP-send to assignee
- **#28** `<any working> → blocked` — when an owner reports a blocker
- **#29** `blocked → <pre-block-column>` — when blockers clear

## PRRD authority

ORCHESTRATOR cannot mutate the PRRD directly. To propose a change:

```bash
prrd-edit.py propose silver "<text>" \
            --target <N> \
            --proposed-by orchestrator-<team> \
            --routed-via cos-<team>
```

This files a proposal that COS forwards to MANAGER for decision.

## The red column workflow (PRIMARY responsibility)

Every work session, ORCH starts with:

```bash
kanban.py --red
```

The output shows the **🔓 BLOCK-CLEARING PRIORITY** at the top — TRDDs
that, if completed, would unblock the most others. ORCH's job:

- [ ] For each TRDD in the priority ranking, raise its `priority:`
      frontmatter to at least `1` (highest). Bump in proportion to
      `unblocks_count`.
- [ ] If a blocker has `assignee:` already, AMP-ping the assignee:
      "TRDD-<id> is blocking N tasks. Please prioritise."
- [ ] If a blocker is unassigned (in `dispatch`), assign it NOW.
- [ ] If a blocker is itself blocked (chained), recurse: address the
      transitive blocker first.

When `blocked-by:` empties for a TRDD, the OWNER restores its
`column:` from `pre-block-column:`. ORCH then re-claims if needed.

## Per-column checklists

### Claiming a todo (todo → design)

- [ ] `findtrdd.py --column todo` → see what's available
- [ ] Pick the highest-priority. If multiple tied, pick the oldest.
- [ ] Read the TRDD body + frontmatter; understand the user's intent
- [ ] Identify which team is appropriate (check `docs_dev/teams/team-registry.md`)
- [ ] AMP-send to the team's CHIEF-OF-STAFF: "Please delegate TRDD-<id>
      to ARCHITECT for design"
- [ ] Edit `column: design`, bump `updated:`, optionally set
      `assignee: <arch-session>`

### Receiving a designed TRDD (design → dispatch)

- [ ] ARCHITECT signals via AMP. If 1→N split: ARCHITECT created N
      child TRDDs in `dispatch`, marked parent `superseded`.
- [ ] Read each new TRDD's frontmatter; ensure `task-type:`,
      `test-requirements:`, `audit-requirements:`,
      `review-requirements:`, `release-via:` are all set
- [ ] Verify EHTs are listed in `eht:` and exist as separate TRDDs

### Assigning (dispatch → dev)

- [ ] `findtrdd.py --column dispatch` → see what needs assigning
- [ ] For each, pick an assignee whose skill matches `task-type:` and
      who has free capacity (check `kanban.py --group-by assignee`)
- [ ] Edit `assignee: <session>`, `column: dev`, bump `updated:`
- [ ] If `delivery: pull-request`, propose a feature branch name:
      `feature/TRDD-<id8>-<slug>` and set `feature-branch:`
- [ ] AMP-send to the assignee (via COS): "TRDD-<id> assigned; please
      implement"

### Managing a blocked TRDD

- [ ] Owner reports a blocker; sets `blocked-by: [<refs>]`, bumps
      `updated:`
- [ ] ORCH receives notification (or sees it in `kanban.py --red`)
- [ ] Edit the TRDD: `pre-block-column: <previous>`, `column: blocked`
- [ ] Update priority of the BLOCKING TRDDs (per the red-column flow)
- [ ] AMP-broadcast to assignees of blockers: "<id> blocking <N> tasks"

## Coordination with team-kanban (server-backed)

The existing `amoa-kanban-management` skill manages an AI Maestro
server-backed kanban. This new file-based kanban is COMPLEMENTARY:

- Use `team-kanban` (server) for UI-visible boards, GitHub Projects
  sync, cross-team metrics.
- Use `kanban.py` (file-based) for in-session decision-making, drift
  detection, and the red-column priority ranking.

When both are in use, sync rules:

- Truth lives in the TRDD `.md` files. Server-backed kanban is a mirror.
- After a column change in a TRDD, AMP-send a server-side
  `team-kanban` task update if a parallel mirror exists.
- Drift signals from `kanban.py --check-drift` take precedence over
  server-backed state.

## AMP message templates

```text
Subject: TRDD-<id> in red column — please prioritise
To: <assignee-session>
Via: cos-<team>
Type: priority_bump
Body:
  TRDD-<id> "<title>" is currently blocking <N> other TRDDs. ORCH has
  raised its priority to <new>. Please address.
```

## Resources

- Universal skill: `prrd-trdd-kanban`
- Existing AMOA kanban skill (server-backed): `amoa-kanban-management`
- ORCHESTRATOR persona: `agents/ai-maestro-orchestrator-agent-main-agent.md`
