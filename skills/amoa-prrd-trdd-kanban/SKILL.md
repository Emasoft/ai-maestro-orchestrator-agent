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
Kanban model. ORCH is the team's traffic controller and **owns the RED
(blocked) column** — TRDDs whose `blocked-by:` list is non-empty are
the fundamental source of project delays, and ORCH's central job is to
minimise the time TRDDs spend there. ORCH owns three columns: `todo`
(claims promoted TRDDs from AMAMA), `dispatch` (assigns designed TRDDs
to agents and moves to `dev`), and `blocked` 🔴. It reads but does not
own `dev`, `testing`, `ai_review`, `human_review` for upward status.
For the universal mechanics, see the `prrd-trdd-kanban` skill in
`ai-maestro-plugin`.

## Prerequisites

- The universal `prrd-trdd-kanban` skill (ai-maestro-plugin) for shared
  mechanics, transition numbers, and the exempt-operations matrix.
- A PRRD plus a populated `design/tasks/` tree of TRDD `.md` files —
  the TRDD files are the single source of truth.
- AI Maestro Plugin (AMP) installed for inter-agent messaging; ORCH
  routes every cross-team message through its CHIEF-OF-STAFF (COS).

## Instructions

1. Claim a todo: `findtrdd.py --column todo`, pick highest-priority
   (oldest breaks ties), read body + frontmatter for intent.
2. Delegate design to ARCHITECT: AMP-send via COS "delegate TRDD-<id>
   to ARCHITECT", then edit `column: design` and bump `updated:`.
3. On design→dispatch, ARCHITECT signals via AMP (a 1→N split leaves N
   child TRDDs in `dispatch`, parent `superseded`); verify each child's
   `task-type:`, `test-requirements:`, `review-requirements:`, `eht:`.
4. Assign each dispatch TRDD: set `assignee:` (skill matches
   `task-type:`, capacity via `kanban.py --group-by assignee`),
   `column: dev`, bump `updated:`, AMP-send the assignee via COS.
5. Run `kanban.py --red` every session. For each TRDD in the
   **🔓 BLOCK-CLEARING PRIORITY** ranking, raise `priority:` toward `1`
   in proportion to `unblocks_count`; assign unassigned blockers now;
   recurse into chained (transitively blocked) blockers first.
6. Escalate non-exempt actions via COS — cross-team reassignment,
   `human_review`, force-`failed`. Exempt (no approval): dispatch→dev
   assignment, red-column priority bumps, within-team reassignment.

## Output

- TRDD frontmatter edits: `column:`, `assignee:`, `priority:`,
  `pre-block-column:`, `updated:` — written to the `.md` files.
- AMP status messages to COS (and through COS to MANAGER for any
  non-exempt request or escalation).
- Red-column priority actions: bumped `priority:` on blockers plus
  priority-ping AMP messages to their assignees.

## Error Handling

- Blocker cannot clear within the team → escalate to the team's COS
  with the chain of `blocked-by:` refs.
- Cross-team dependency or reassignment → route to MANAGER via COS;
  never reassign across teams unilaterally.
- A stuck TRDD that needs force-`failed` or `human_review` → request
  MANAGER approval via COS (non-exempt).
- Unsure whether an action is exempt → treat as non-exempt and request
  approval. Conservative default.

## Examples

```bash
# Start every session by inspecting the RED column priority ranking
kanban.py --red
```

```bash
# See what is waiting to be assigned, then assign by capacity
findtrdd.py --column dispatch
kanban.py --group-by assignee
```

## Single-writer-per-domain and NPT/EHT collision avoidance

Every mutable surface in `design/` has exactly one owning instance at a
time (PRRD S5.1). A TRDD `.md` file is write-locked by the instance
named in its `current-owner:` frontmatter field; a non-owner may mutate
only the coordination fields (`column:`, `assignee:`) and must delegate
any body or requirement edit to the owner or take an explicit claim
(set `current-owner:` to itself) before writing. Never blind-write a
file another instance owns — concurrent writes corrupt the single source
of truth.

When authoring derived NPT/EHT child TRDDs, prevent cross-instance
collisions (PRRD S6.1): each child declares in its body the
files/domains it will touch, and before creating it, scan the open
TRDDs (`findtrdd.py --column dev` / `dispatch` / `testing`) for a domain
overlap. On collision, serialise the children — make one `blocked-by:`
the other so only one writes the shared domain at a time — or merge them
into a single TRDD, rather than letting two instances edit the same
files in parallel. The task-comprehension handshake (the
`amoa-implementer-interview-protocol` skill) surfaces these domains up
front by asking each MEMBER which files/domains it will touch.

## Resources

For shared mechanics, transition numbers, and the approval matrix, read
the universal `prrd-trdd-kanban` skill in `ai-maestro-plugin` — in
particular its `exempt-operations.md` (which transitions need MANAGER
approval) and `column-transitions.md` (the full numbered transition
list). The existing `amoa-kanban-management` skill manages an AI Maestro
server-backed board and coexists with this file-based flow: the
server board is a UI mirror, while the TRDD `.md` files remain the
source of truth and `kanban.py` drives in-session red-column decisions.
The ORCHESTRATOR persona lives in the agent's main-agent definition.
