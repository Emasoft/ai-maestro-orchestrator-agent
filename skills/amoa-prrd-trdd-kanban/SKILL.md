---
name: amoa-prrd-trdd-kanban
description: "ORCHESTRATOR's role in the PRRD / TRDD / Kanban workflow. Use when ORCH claims TRDDs from todo, delegates design to ARCHITECT, assigns dev work to MEMBERs, manages the RED (blocked) column priority, or coordinates AMP messages with the team."
allowed-tools: "Skill, Bash(amp-send:*), Bash(amp-kanban-list:*), Bash(amp-kanban-move:*), Read, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "2.0.0"
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

## The pillar operations live in the CORE plugin — call them, do not reimplement

Every PRRD / TRDD / kanban operation is a **granular `ama-*` skill shipped by
`ai-maestro-plugin`**. Load one with `Skill(ai-maestro-plugin:<name>)`. This file
carries only what is ORCHESTRATOR-*specific* — which columns ORCH owns, and how it
ranks the red column. It deliberately carries no mechanics of its own.

| Need | Core skill |
|---|---|
| Read a PRRD rule by number | `ama-prrd-get` |
| Search the PRRD | `ama-prrd-find` |
| Edit a SILVER rule (authority-gated) | `ama-prrd-edit` |
| Propose a rule change | `ama-prrd-propose` |
| Find TRDDs by column / field | `ama-trdd-find` |
| Author a TRDD | `ama-trdd-write` |
| Update TRDD frontmatter | `ama-trdd-update` |
| Move a card between columns | `ama-trdd-transition` |
| Render the board | `ama-kanban-render` |
| Rank / clear the blocked column | `ama-unblock` |
| Approve or refuse a proposal | `ama-proposal-approvals` |

**Why this matters and is not mere tidiness.** This skill previously wired a
per-plugin copy of the old script layer (`get-prrd.py`, `findprrd.py`,
`findtrdd.py`, `kanban.py`). A second implementation of a governance operation does
not stay equivalent: the vocabulary, the authority table and the approval record
all moved under the MANAGER wave, and a private copy silently keeps enforcing the
retired shape while looking correct. The core skills are the one implementation
that moves with the rules.

**Probe capability, never a version.** When you depend on a contract that may not
be seeded yet, test for the contract itself —
`grep -q min-approval-requirement .claude/rules/aimaestro-trdd-approval.md` — never
a plugin version or branch name. A version check answers a question about
packaging; the behaviour you actually need is what the seeded rules say.
**Keep grep's exit trichotomy when probing:** `0` = contract present, `1` =
absent, `2` = THE PROBE COULD NOT RUN (unreadable path, bad pattern). Never
collapse `2` into `1` with a bare boolean (`if grep -q …; then … else <treat as
absent>`): a broken probe then silently reports the contract missing. Branch
three ways, or at minimum surface exit `2` as an error. The same trichotomy
governs `trddgrep`/`prrdgrep`/`specgrep` — never `trddgrep validate || fallback`.

## Prerequisites

- `ai-maestro-plugin` installed — it ships the `ama-*` skills above. This skill is
  a thin role layer over them and does nothing useful without it.
- A PRRD plus a populated `design/tasks/` tree of TRDD `.md` files. **The files are
  the SSOT for state**; the server board is a mirror, and the script verbs are
  correctness wrappers, not an authorization boundary.
- AI Maestro Plugin (AMP) installed for inter-agent messaging; ORCH
  routes every cross-team message through its CHIEF-OF-STAFF (COS).

## Instructions

1. Claim a todo: `Skill(ai-maestro-plugin:ama-trdd-find)` filtered to
   `column: todo`, pick highest-priority (oldest breaks ties), read body +
   frontmatter for intent.
2. Delegate design to ARCHITECT: AMP-send via COS "delegate TRDD-<id>
   to ARCHITECT", then transition to `design` with
   `Skill(ai-maestro-plugin:ama-trdd-transition)` (it bumps `updated:` for you —
   do not also hand-edit the field, or the board's sort order reflects two writes).
3. On design→dispatch, ARCHITECT signals via AMP (a 1→N split leaves N
   child TRDDs in `dispatch`, parent `superseded`); verify each child's
   `task-type:`, `test-requirements:`, `review-requirements:`, `eht:`.
4. **Before dispatching, check the DISPATCH PRECONDITION** — every dependency must
   have a closing PR **merged into the base this worker will branch from**, not
   merely a closed issue. `shared/amoa_dispatch_gate.py` evaluates it. A closed
   issue whose fix sits in an unmerged PR is the SCEN-031 deadlock: the worker
   branches off a base that lacks the dependency and cannot proceed.
5. Assign each dispatch TRDD: set `assignee:` (skill matches `task-type:`, capacity
   from `Skill(ai-maestro-plugin:ama-kanban-render)` grouped by assignee), move to
   `dev`, AMP-send the assignee via COS.
6. Work the blocked column every session with
   `Skill(ai-maestro-plugin:ama-unblock)`. Raise `priority:` toward `1` in
   proportion to `unblocks_count`; assign unassigned blockers now; recurse into
   chained (transitively blocked) blockers first.
7. **Gate on "reachable along MY OWN call path", not "the dependency shipped."** A
   server capability that this plugin's CLI cannot yet express is not available to
   this plugin, however deployed it is upstream. Promote a `backburner` card only
   when the trigger written on the card is reachable from here.
8. Escalate non-exempt actions via COS — cross-team reassignment,
   `human_review`, force-`failed`. Exempt (no approval): dispatch→dev
   assignment, red-column priority bumps, within-team reassignment.
   `shared/amoa_kanban_vocab.py::transition_authority()` mirrors the Part B2
   table (hub overlay rule *aimaestro-trdd-approval.md*) exactly — consult it
   rather than recalling the table. It returns the owning actor for every row
   ORCH must not originate (`assignee`, `test-runner`, `architect`,
   `ai-reviewer`, `reviewer`, `integrator`, `releaser`, `deployer`, `manager`);
   ORCH only originates `todo→design` and `dispatch→dev`. A non-`"orchestrator"`
   answer means route the transition to that actor and mirror the result
   afterward — never perform it directly.

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

```text
# Start every session on the blocked column — it is the delay source ORCH owns
Skill(ai-maestro-plugin:ama-unblock)

# See what is waiting to be assigned, then assign by capacity
Skill(ai-maestro-plugin:ama-trdd-find)      # filter: column = dispatch
Skill(ai-maestro-plugin:ama-kanban-render)  # group by assignee
```

The `trddgrep` CLI backs these lookups and is the direct query path when a
skill round-trip is overkill: `trddgrep` (the board), `trddgrep --column todo`
(one column), `trddgrep show <id>` (one card + STATE block), `trddgrep next`
(what is workable now), `trddgrep validate` (the write gate). Exit codes are
grep's trichotomy — `0` clean · `1` findings · `2` COULD NOT RUN — and `2`
must never be collapsed into `1`.

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
TRDDs (`ama-trdd-find` over `dev` / `dispatch` / `testing`) for a domain
overlap. On collision, serialise the children — make one `blocked-by:`
the other so only one writes the shared domain at a time — or merge them
into a single TRDD, rather than letting two instances edit the same
files in parallel. The task-comprehension handshake (the
`amoa-implementer-interview-protocol` skill) surfaces these domains up
front by asking each MEMBER which files/domains it will touch.

## Resources

Shared mechanics, the 17-column vocabulary, and the approval matrix live in the
granular `ama-*` skills listed above — `ama-trdd-transition` carries the transition
rules, `ama-proposal-approvals` the approval flow. There is no monolithic
`prrd-trdd-kanban` skill to defer to any more; that name was retired when the
operations were split, and a reference to it resolves to nothing.

The `amoa-kanban-management` skill manages the AI Maestro server-backed board and
coexists with this file-based flow: **the server board is a mirror; the TRDD `.md`
files are the SSOT.** When the two disagree, the files win and the mirror is
re-synced from them — never the reverse.

The ORCHESTRATOR persona lives in the agent's main-agent definition.
