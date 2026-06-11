# Full Project Workflow: From Requirements to Delivery

**Version**: 2.0.0
**Last Updated**: 2026-06-11

This document describes the complete workflow for how the AI Maestro agent system handles a project from initial requirements to delivery. All agents must understand this workflow to coordinate effectively.

> **R6 v3 routing (authoritative — see `docs/ROLE_BOUNDARIES.md` and the persona
> `agents/ai-maestro-orchestrator-agent-main-agent.md`):** AMCOS guards the team
> boundary. The MANAGER (AMAMA) reaches team-internal agents **only via AMCOS** —
> there is **no** AMAMA→AMOA or AMAMA→AMIA direct handoff. Inside the team, AMOA
> talks **directly** to AMAA, AMIA, and AMPA. This document was migrated to R6 v3
> in v2.0.0; any older text implying a direct manager→orchestrator handoff is
> superseded.

> **Column ownership (authoritative):** AMOA owns the **pre-PR green-light** only
> (clearing an implementer to open a PR). AMIA validates the **merged** PR against
> the task requirements and owns the flip to `done`/`completed`. **Nobody
> self-marks a task completed** — AMOA never moves its own team's task to `done`.

---

## Workflow Overview

```
USER
  │
  ▼
AMAMA (Manager) ◄────────────────────────────────────────────┐
  │                                                          │
  │ 1. Creates project                                       │
  │ 2. Sends requirements to AMCOS                            │
  ▼                                                          │
AMCOS (Chief of Staff)                                        │
  │                                                          │
  │ 3. Evaluates project, suggests team                      │
  │ 4. Creates/assigns agents                                │
  │ 5. Notifies AMAMA: team ready                             │
  ▼                                                          │
AMAMA ─── requirements to AMAA via AMCOS (team gateway) ────►  │
  │                                                          │
  │ 6. AMAMA → AMCOS → AMAA  (MANAGER never messages AMAA     │
  │    directly; AMCOS relays requirements into the team)     │
  ▼                                                          │
AMAA (Architect)                                              │
  │                                                          │
  │ 7. Creates design document                               │
  │ 8. Sends design back via AMCOS → AMAMA                    │
  ▼                                                          │
AMAMA ◄──── USER APPROVAL ─────────────────────────────────►  │
  │                                                          │
  │ 9. Sends approved design to AMCOS (team gateway)          │
  ▼                                                          │
AMCOS (Chief of Staff) ── relays approved design into team ── │
  │                                                          │
  │ 9b. AMCOS → AMOA (within-team DIRECT edge)                │
  ▼                                                          │
AMOA (Orchestrator)                                           │
  │                                                          │
  │ 10. Splits design into tasks                             │
  │ 11. Creates task-requirements-documents                  │
  │ 12. Adds tasks to kanban                                 │
  │ 13. Assigns tasks to agents (AMOA → AMPA DIRECT)          │
  ▼                                                          │
IMPLEMENTER AGENTS (AMPA) ◄────────────────────────────────► │
  │                                                          │
  │ 14. Work on tasks                                        │
  │ 15. AMOA gives pre-PR green-light → agent submits PR      │
  ▼                                                          │
AMIA (Integrator)                                             │
  │                                                          │
  │ 16. Reviews + validates the merged PR vs. requirements    │
  │ 17. Merges or rejects; AMIA flips `done`/`completed`      │
  ▼                                                          │
AMOA ◄──── AMIA reports merge/validation result (DIRECT) ───►  │
  │                                                          │
  │ 18. Reports up via AMCOS → AMAMA (route through AMCOS)     │
  │ 19. Assigns next tasks (AMOA → AMPA DIRECT)               │
  └──────────────────────────────────────────────────────────┘
```

---

## Kanban Column System

All projects use an **8-column kanban system** on GitHub Projects. Every agent must understand these columns and use the canonical code format consistently.

### Canonical Columns

| # | Column | Code Format | Label | Description | Flip owner |
|---|--------|-------------|-------|-------------|------------|
| 1 | Backlog | `backlog` | `status:backlog` | Entry point for all new issues | AMOA |
| 2 | Todo | `todo` | `status:todo` | Ready to start, prioritized | AMOA |
| 3 | In Progress | `in-progress` | `status:in-progress` | Active work by assigned agent | AMOA |
| 4 | AI Review | `ai-review` | `status:ai-review` | Integrator (AMIA) reviews the PR | AMIA |
| 5 | Human Review | `human-review` | `status:human-review` | User reviews (big tasks only) | AMIA (sets) / USER decides |
| 6 | Merge/Release | `merge-release` | `status:merge-release` | Approved and ready to merge | AMIA |
| 7 | Done | `done` | `status:done` | Completed and merged | **AMIA** (validates merged PR; AMOA never self-marks) |
| 8 | Blocked | `blocked` | `status:blocked` | Blocked at any stage | column owner at time of block |

### Task Routing

- **Small tasks**: In Progress → AI Review → Merge/Release → Done
- **Big tasks**: In Progress → AI Review → Human Review → Merge/Release → Done
- **Human Review** is requested up the chain via AMCOS → AMAMA (AMAMA asks the
  USER to test/review). No team-internal agent messages AMAMA directly (R6 v3).
- **Blocked** can be set from any column; task returns to its previous column when unblocked
- **Flip ownership**: AMOA owns Backlog → Todo → In Progress (the pre-PR
  green-light is the last AMOA-owned step); AMIA owns AI Review → Human Review →
  Merge/Release → Done. AMOA never flips a task to Done.

### Code Format Rules

- **Always use dashes**: `in-progress`, `ai-review`, `merge-release` (NOT underscores)
- **Labels use `status:` prefix**: `status:in-progress`, `status:ai-review`
- **Display names use title case**: "In Progress", "AI Review", "Merge/Release"

---

## Board Reconciliation: TRDD pipeline (authoritative) vs. GitHub board (projection)

There are two views of a task's state, and they are **not peers**:

1. **The TRDD `column:` pipeline is the AUTHORITATIVE lifecycle.** Each task is a
   TRDD file in `design/tasks/` whose `column:` field is the single source of
   truth for where the task is. The full pipeline is the v2 column set
   (`backburner`, `todo`, `design`, `dispatch`, `dev`, `testing`, `ai_review`,
   `human_review`, `complete`, `publish`, `published`, `deploy`, `live`,
   `live_auditing`, plus the exceptions `blocked`, `failed`, `superseded`). See
   `~/.claude/rules/trdd-design-tasks.md` for the definitive state machine.
2. **The 8-column GitHub Projects board is a VISUAL PROJECTION of that pipeline.**
   It exists for humans to see progress at a glance. It carries fewer columns, so
   several TRDD columns project onto one board column.

**Lossless rule.** The projection must never lose the authoritative state. The
board column **plus the `trdd-column:` custom field** (set to the exact TRDD
`column:` value) together reproduce the TRDD column exactly, so board → TRDD is
**lossless and bidirectional**. The board column alone is a lossy summary; the
`trdd-column:` field is what makes the round-trip exact. Never collapse two TRDD
columns onto one board column **without** also writing the precise value into
`trdd-column:`.

### Lossless column mapping (TRDD `column:` ↔ board)

| TRDD `column:` (authoritative) | Board column (projection) | `trdd-column:` field (exact, lossless) |
|---|---|---|
| `backburner` | Backlog | `backburner` |
| `todo` | Todo | `todo` |
| `design` | Todo | `design` |
| `dispatch` | Todo | `dispatch` |
| `dev` | In Progress | `dev` |
| `testing` | In Progress | `testing` |
| `ai_review` | AI Review | `ai_review` |
| `human_review` | Human Review | `human_review` |
| `complete` | Merge/Release | `complete` |
| `publish` | Merge/Release | `publish` |
| `deploy` | Merge/Release | `deploy` |
| `published` | Done | `published` |
| `live` | Done | `live` |
| `live_auditing` | Done | `live_auditing` |
| `blocked` | Blocked | `blocked` (`pre-block-column:` records where to restore) |
| `failed` | Blocked | `failed` |
| `superseded` | Done | `superseded` |

> Reverse direction (board → TRDD) is unambiguous: read `trdd-column:`. Two tasks
> in the same board column (e.g. both in "Todo") are distinguished by their
> `trdd-column:` (`design` vs `dispatch`). The board column is derived from
> `trdd-column:` by the table above — never set independently.

### Sync rules and tie-break

- **TRDD is written first; the board is updated to match.** Whoever owns a TRDD
  transition (per "Detailed Procedure Steps" and the *Flip owner* column above)
  edits the TRDD `column:` first, then projects it onto the board (board column +
  `trdd-column:` field) via `scripts/amoa_kanban_manager.py` / the sync script.
- **Tie-break: the TRDD wins.** If the board and the TRDD ever disagree, the TRDD
  `column:` is authoritative. Reconcile by re-deriving the board column from the
  TRDD's `column:` using the mapping table — never by editing the TRDD to match a
  stale board.
- **Ownership is preserved across the projection.** The board's *Flip owner*
  must match who owns the corresponding TRDD transition: AMOA owns up to the
  pre-PR green-light (`dev`/`testing`); AMIA owns `ai_review` → `complete` →
  `published`/`live` (the Done projection). AMOA never moves a task into the Done
  projection on its own.

---

## Detailed Procedure Steps

### Phase 1: Project Creation and Team Setup

#### Step 1: Manager Creates Project
**Actor**: AMAMA (Manager)
**Action**:
- Create a new project in a new GitHub repository (or in an existing repository)
- Send the requirements to the Chief of Staff (AMCOS)

**Communication**:
- GitHub: Create repository, create initial issue with requirements
- AI Maestro: Message to AMCOS with project details and requirements

#### Step 2: Chief of Staff Evaluates Project
**Actor**: AMCOS (Chief of Staff)
**Action**:
- Evaluate the project requirements
- Analyze complexity, technologies involved, timeline
- Suggest an optimal team of agents to the Manager

**Communication**:
- AI Maestro: Send team proposal to AMAMA with justification

#### Step 3: Team Discussion and Approval
**Actor**: AMAMA (Manager) + AMCOS (Chief of Staff)
**Action**:
- Manager discusses the team proposal with Chief of Staff
- Negotiate team composition if needed
- Manager ultimately approves a team proposal

**Communication**:
- AI Maestro: Back-and-forth messages until agreement

#### Step 4: Team Creation
**Actor**: AMCOS (Chief of Staff)
**Action**:
- Create the agents needed for the project team
- OR move agents from other projects to the new project team
- Configure each agent with appropriate skills and plugins for their role
- Assign agents to the project team

**Communication**:
- AI Maestro: Coordination messages during agent creation
- AI Maestro: Onboarding messages to each new agent

#### Step 5: Team Ready Notification
**Actor**: AMCOS (Chief of Staff)
**Action**:
- Notify the Manager that the team is set up and ready to follow instructions
- Provide team roster with agent names and roles

**Communication**:
- AI Maestro: Team ready notification to AMAMA

---

### Phase 2: Design and Planning

#### Step 6: Requirements to Architect (via AMCOS)
**Actor**: AMAMA (Manager) → AMCOS → AMAA
**Action**:
- Expand the requirements with more details, including the team member names
- Hand the requirements to **AMCOS** (the team gateway); AMCOS relays them to the
  Architect (AMAA) and assigns the design-document task — the MANAGER does **not**
  message AMAA directly (R6 v3)

**Communication**:
- GitHub: Create issue with requirements, assign label for AMAA
- AI Maestro: AMAMA → AMCOS (team-boundary edge); then AMCOS → AMAA (within-team
  DIRECT edge) with full requirements and team roster. No AMAMA→AMAA direct message.

#### Step 7: Design Document Creation
**Actor**: AMAA (Architect)
**Action**:
- Receive the task (on the kanban) to convert requirements into a full design document
- Create design document with:
  - System architecture
  - Module specifications
  - Detailed technical specs
  - Interface definitions
  - Data models

**Communication**:
- GitHub: Update issue with progress
- AI Maestro: Progress updates to AMAMA

#### Step 8: Design Submission (via AMCOS)
**Actor**: AMAA (Architect) → AMCOS → AMAMA
**Action**:
- Send the completed design document back toward the Manager **via AMCOS** — the
  Architect does not message AMAMA directly (R6 v3); AMCOS relays it up

**Communication**:
- GitHub: Attach design document to issue, mark ready for review
- AI Maestro: AMAA → AMCOS (within-team DIRECT edge); AMCOS → AMAMA (team-boundary
  edge) that design is ready

#### Step 9: Design Approval
**Actor**: AMAMA (Manager) + USER
**Action**:
- Manager examines the design document
- Manager asks for approval from the User
- If User approves: the approved design is handed to **AMCOS** (the team
  gateway), which relays it to the Orchestrator — the MANAGER does **not**
  message AMOA directly (R6 v3)
- If User rejects: design goes back to Architect with feedback (via AMCOS)

**Communication**:
- GitHub: Issue comments with design and approval status
- AI Maestro: AMAMA → AMCOS (team-boundary edge) with the approved design; then
  AMCOS → AMOA (within-team DIRECT edge). No AMAMA→AMOA direct message.

---

### Phase 3: Task Planning and Assignment

#### Step 10: Design Decomposition
**Actor**: AMOA (Orchestrator)
**Action**:
- Split the design into actionable small steps
- Split each step into actionable tasks
- Tailor tasks for the current team members and their capabilities

#### Step 11: Task Requirements Documents
**Actor**: AMOA (Orchestrator)
**Action**:
- Produce the task-requirements-document for each agent
- Include in each document:
  - Task description
  - Acceptance criteria
  - Related design sections
  - Dependencies
  - Expected deliverables

#### Step 12: Task Plan Creation
**Actor**: AMOA (Orchestrator)
**Action**:
- Create a plan where task-requirements-documents are ordered and parallelized
- Ensure tasks can be assigned to the right agent at the right time
- Define task dependencies
- Identify tasks that can run in parallel

#### Step 13: Kanban Population
**Actor**: AMOA (Orchestrator)
**Action**:
- Add tasks to the GitHub Project kanban `todo` column
- For each task:
  - Set the "Assigned Agent" custom field
  - Attach the task-requirements-document
  - Specify task order and dependencies
  - Ensure task executes only when required previous tasks are completed

**Communication**:
- GitHub: Create issues, add to project, set fields
- AI Maestro: Notification to each agent about their first assigned task

#### Step 14: Agent Clarification
**Actor**: AMOA (Orchestrator) + IMPLEMENTER AGENTS
**Action**:
- Send to each agent a notification using the `agent-messaging` skill that their first task has been assigned
- Ask each agent if they need clarifications
- The Orchestrator is the team lead with full project understanding (along with Architect)

**Communication**:
- AI Maestro: Task assignment messages with clarification request

#### Step 15: Feedback and Design Updates (if needed)
**Actor**: IMPLEMENTER AGENTS → AMOA → AMAA
**Action**:
- If agents reply presenting problems or improvement suggestions:
  - Orchestrator evaluates the feedback
  - If feasible: Orchestrator sends design-change-request to Architect
  - Architect creates new version of design document
  - Architect sends updated design to Orchestrator

**Communication**:
- AI Maestro: Feedback from agents to AMOA
- AI Maestro: Design change request from AMOA to AMAA
- AI Maestro: Updated design from AMAA to AMOA

#### Step 16: Task Updates from Design Changes
**Actor**: AMOA (Orchestrator)
**Action**:
- Evaluate the new version of the design document
- If approved:
  - Update all task-requirements-documents affected by changes
  - Update the attachments in project kanban tasks
  - Send updated documents to assigned agents
  - Explain the changes and motivations

**Communication**:
- GitHub: Update issue attachments
- AI Maestro: Change notifications to affected agents

---

### Phase 4: Implementation

#### Step 17: Task Execution
**Actor**: IMPLEMENTER AGENTS
**Action**:
- Start working on assigned tasks
- Report status of being "in development" to Orchestrator

**Communication**:
- AI Maestro: Status update to AMOA

#### Step 18: Kanban Status Update
**Actor**: AMOA (Orchestrator)
**Action**:
- Move tasks on project kanban from `todo` column to `in-progress` column

**Communication**:
- GitHub: Update project item status

#### Step 18.5: In-Dev Issue Dialog (MEMBER ⇄ AMOA) — the canonical in-development loop

> **CANONICAL DEFINITION (single source of truth).** This is the authoritative
> description of the second of the three dialog loops (the in-development loop).
> Every other document that touches it — the interview-protocol skill's
> `exception-handling.md` and `escalation-messages.md`, the `BLOCKER_REPORT_TEMPLATE`,
> the developer-communication blocker references — MUST link here rather than
> restate it. Do not fork a parallel copy.

**Actor**: IMPLEMENTER AGENTS (AMPA) ⇄ AMOA (Orchestrator); AMOA pulls in AMAA
(design) or AMIA (CI/merge) as the issue type requires.

**When it fires**: continuously, from the moment the agent starts coding (after
the pre-task handshake's PROCEED) until the pre-PR green-light (Step 19). The
moment an implementer hits ANY issue — ambiguity, blocker, a discovered design
flaw, a missing tool, a conflicting requirement — it raises it to AMOA
**immediately**, before writing any workaround.

**The iron rule**: an implementer **NEVER silently improvises around a design
flaw**. A design flaw is the Architect's to fix, not the implementer's to paper
over. Silent improvisation is the failure mode this loop exists to prevent: it
ships code that diverges from the approved design, and nobody notices until
review (or production).

**Routing (R6 v3 — all within-team DIRECT edges):**

| Issue type the implementer raises | AMOA's action | Who resolves it |
|---|---|---|
| **Design flaw / architectural incompatibility** | AMOA sends a **design-change-request** to AMAA (AMOA → AMAA, DIRECT) | AMAA revises the design or authors new TRDDs; AMOA re-interviews the implementer with the new design (see Steps 15–16) |
| **Ambiguous/contradictory MUTABLE requirement** | AMOA decides pragmatically and records the rationale in the task notes | AMOA (in-team authority) |
| **Ambiguous IMMUTABLE (user-specified) requirement** | AMOA escalates via AMCOS → AMAMA → USER | USER (relayed back down the chain) |
| **CI / merge / pipeline blocker** | AMOA pulls in AMIA (AMOA → AMIA, DIRECT) | AMIA |
| **Capability gap (missing tool/skill/access)** | AMOA escalates to AMCOS | AMCOS provides access / specialized agent / scope adjustment |
| **Environment / toolchain blocker** | Implementer files a Blocker Report; AMOA triages | AMOA + the relevant owner |

**Artifacts:**
- **Design-Change-Request** — created by AMOA when an implementer surfaces a
  design problem (see *Document References*); flows AMOA → AMAA, DIRECT.
- **Blocker Report** — the implementer-authored escalation document; the template
  lives in `skills/amoa-remote-agent-coordinator/templates/handoff/BLOCKER_REPORT_TEMPLATE.md`.

**Termination**: the loop ends only when the issue is resolved (design revised,
requirement clarified, blocker cleared) — then the implementer resumes, and the
cycle eventually reaches the pre-PR green-light (Step 19). An unresolved issue
**never** advances to a PR.

**Communication**:
- AI Maestro: implementer raises the issue to AMOA (AMPA → AMOA, DIRECT)
- AI Maestro: AMOA → AMAA design-change-request, or AMOA → AMIA CI escalation, or
  AMOA → AMCOS → AMAMA → USER for immutable-requirement questions
- AI Maestro: resolution relayed back to the implementer (AMOA → AMPA, DIRECT)

---

#### Step 19: Pre-PR Green-Light (NOT task completion)
**Actor**: IMPLEMENTER AGENTS (AMPA) → AMOA
**Action**:
- When an implementer agent finishes the code for a task, notify the Orchestrator
- Orchestrator discusses and asks questions to ensure the work is ready
- If OK: Orchestrator gives the **pre-PR green-light** — approval to open the
  pull request. **This is the ONLY completion-adjacent authority AMOA holds; it
  does NOT mark the task `completed`.** The task is *not* done yet — it is cleared
  to enter review.
- Implementer creates the PR

**Communication**:
- AI Maestro: "code ready" notification from agent to AMOA
- AI Maestro: pre-PR green-light from AMOA to agent (AMOA → AMPA, DIRECT)
- GitHub: PR created

---

### Phase 5: Integration and Review

#### Step 20: PR Review Request
**Actor**: AMOA (Orchestrator)
**Action**:
- Send message using the `agent-messaging` skill to Integrator agent (AMIA) to evaluate all PRs of completed tasks
- Request merge if they pass all checks

**Communication**:
- AI Maestro: PR review request to AMIA
- GitHub: PR ready for review

#### Step 21: PR Evaluation and Column Flips
**Actor**: AMIA (Integrator)
**Action**:
- Move the task into `ai-review` (board) / `ai_review` (TRDD) when review starts
- Examine the PR of each task
- Verify compliance with the task requirements / design
- Run tests and linting
- For big tasks: set `human-review` and route the USER decision via AMAMA (through
  AMCOS) before merge
- If everything OK: merge to main, then **AMIA owns the flips** through
  `merge-release` to `done` (TRDD `complete` → `published`/`live`) — see Step 23
- If not OK: refuse PR, report issues to Orchestrator (AMIA → AMOA, DIRECT)

**Communication**:
- GitHub: PR review comments, approval/rejection, column moves
- AI Maestro: Report to AMOA with pass/fail details (DIRECT edge)

#### Step 22: Handling Failed PRs
**Actor**: AMOA (Orchestrator) → IMPLEMENTER AGENTS
**Action**:
- Evaluate Integrator report about each task PR
- Communicate to agents the issues and shortcomings
- Instruct agents to fix or improve the code
- Provide extended/improved task-requirements-document if needed
- Move task back to `in-progress` column
- Ask agent if they need anything to complete the task
- If OK: implementer agent resumes work on task

**Communication**:
- AI Maestro: Feedback and instructions to agents
- GitHub: Update task status

---

### Phase 6: Completion and Continuation

#### Step 23: Successful PR Handling — INTEGRATOR owns `completed`
**Actors**: AMIA (Integrator) owns the completion flip; AMOA (Orchestrator)
re-fills the freed implementer.

**AMIA's part (owns the column flips to `done`/`completed`):**
- After merging, AMIA validates the **merged** PR satisfies the task
  requirements, then advances the columns it owns:
  - Small tasks: `ai-review` → `merge-release` → `done` (TRDD `ai_review` →
    `complete` → `published`/`live`)
  - Big tasks: `ai-review` → `human-review` (USER decides, via AMAMA through
    AMCOS) → `merge-release` → `done`
- **AMIA flips the task to `done`/`completed` — AMOA never self-marks its own
  team's task completed.** AMIA edits the TRDD `column:` first, then projects it
  onto the board (board column + `trdd-column:` field).
- AMIA reports the validated completion up the chain via AMCOS → AMAMA (AMIA does
  not message AMAMA directly).

**AMOA's part (keep implementers busy):**
- On AMIA's "task completed" report (AMIA → AMOA, DIRECT), AMOA assigns the freed
  implementer its next task (AMOA → AMPA, DIRECT) so agents never sit idle.
- Any MANAGER sign-off AMOA needs is requested via AMCOS → AMAMA, and the decision
  is relayed back down through AMCOS.

**Communication**:
- GitHub: AMIA moves project item status through the kanban columns to Done
- AI Maestro: AMIA → AMOA (DIRECT) completion report; AMIA → AMCOS → AMAMA for the
  governance-layer report; AMOA → AMPA (DIRECT) next-task assignment

#### Step 24: Iteration
**Action**:
- This cycle iterates until all tasks are complete
- Each successful merge triggers:
  - Report to Manager
  - New task assignment to available agent

---

## Communication Matrix (R6 v3)

Every edge below is either a **direct** `Y` edge or explicitly **via AMCOS**.
AMCOS is the team gateway; the MANAGER (AMAMA) never messages a team-internal
agent (AMOA/AMAA/AMIA/AMPA) directly.

| From | To | Edge | Channel | Purpose |
|------|-----|------|---------|---------|
| AMAMA | AMCOS | direct | AI Maestro | Requirements, approved designs, team requests |
| AMCOS | AMAMA | direct | AI Maestro | Team proposals, status/completion roll-ups |
| AMCOS | AMAA | direct | GitHub + AI Maestro | Relays requirements/design requests into team |
| AMAA | AMCOS | direct | GitHub + AI Maestro | Design documents back toward MANAGER |
| AMCOS | AMOA | direct | GitHub + AI Maestro | Relays the approved design to the Orchestrator |
| AMOA | AMPA (Agents) | direct | GitHub + AI Maestro | Task assignments, pre-PR green-light |
| AMPA (Agents) | AMOA | direct | AI Maestro | "code ready", status updates, questions |
| AMOA | AMAA | direct | AI Maestro | Design change requests (within team) |
| AMAA | AMOA | direct | AI Maestro | Updated designs (within team) |
| AMOA | AMIA | direct | AI Maestro | PR review requests |
| AMIA | AMOA | direct | AI Maestro | PR review results, "task completed" reports |
| AMOA | AMAMA | **via AMCOS** | AI Maestro | Any MANAGER sign-off request (route through AMCOS) |
| AMIA | AMAMA | **via AMCOS** | AI Maestro | Completion roll-up to governance (route through AMCOS) |
| any team role | MAINTAINER / AUTONOMOUS | **via AMCOS → AMAMA** | AI Maestro | Cross-layer governance requests (AMAMA is the sole bridge) |

**Forbidden direct edges (purged in v2.0.0):** AMAMA→AMOA, AMAMA→AMIA,
AMOA→AMAMA, AMIA→AMAMA, AMOA↔peer-AMOA. All of these route through AMCOS.

---

## Role Boundaries Summary

| Role | Creates | Manages | Cannot Do |
|------|---------|---------|-----------|
| **AMAMA** | Projects | Approvals, user communication | Task assignment; message team-internal agents except via AMCOS |
| **AMCOS** | Agents, teams | Agent lifecycle, team gateway | Task assignment, projects |
| **AMAA** | Designs | Architecture | Task assignment |
| **AMOA** | Tasks, plans | Kanban projection, agent coordination, **pre-PR green-light** | Agents, projects; flip a task to `done`/`completed`; self-approve; message AMAMA except via AMCOS |
| **AMIA** | Nothing | PR reviews, merges, **validates merged PR + owns `done`/`completed` flip** | Task assignment |
| **Agents (AMPA)** | Code, PRs | Their assigned tasks | Everything else |

---

## GitHub Integration Points

| Step | GitHub Action | Actor |
|------|---------------|-------|
| 1 | Create repository | AMAMA |
| 6 | Create requirements issue | AMAMA |
| 7 | Update issue with progress | AMAA |
| 8 | Attach design document | AMAA |
| 13 | Create task issues, add to project | AMOA |
| 13 | Set "Assigned Agent" field | AMOA |
| 18 | Move to "In Progress" column | AMOA |
| 19 | Create PR (after AMOA pre-PR green-light) | Agent |
| 21 | Move to "AI Review"; review and merge/reject PR | AMIA |
| 23 | Validate merged PR; move to "Done" column | **AMIA** |

---

## Document References

- **Requirements Document**: Created by AMAMA, relayed to AMAA via AMCOS
- **Design Document**: Created by AMAA, relayed back via AMCOS, approved by AMAMA/User
- **Task-Requirements-Document**: Created by AMOA for each task
- **Design-Change-Request**: Created by AMOA when agents suggest improvements or
  surface a design flaw — the in-development loop's design-escalation artifact
  (see *Step 18.5: In-Dev Issue Dialog*, the canonical definition)
- **PR Review Report**: Created by AMIA for each PR

---

## Skill Inventory (as of v1.5.3)

The AMOA plugin includes **16 skills**, **6 agents**, **15 commands**, and **4 hooks**.

### AMOA (Orchestrator) Skills (16 total)
- **amoa-agent-replacement**: Agent failure detection and replacement protocols
- **amoa-checklist-compilation-patterns**: Checklist compilation and tracking patterns
- **amoa-developer-communication**: Developer communication protocols and templates
- **amoa-github-action-integration**: GitHub Actions integration and CI/CD coordination
- **amoa-implementer-interview-protocol**: Interviewing implementer agents for task readiness
- **amoa-kanban-management**: Kanban column management and task routing
- **amoa-label-taxonomy**: GitHub label taxonomy and standardized labeling
- **amoa-messaging-templates**: Standardized AI Maestro message templates
- **amoa-module-management**: Module lifecycle and dependency tracking
- **amoa-orchestration-commands**: Orchestration command definitions and workflows
- **amoa-orchestration-patterns**: Task distribution, load balancing, dependency management
- **amoa-progress-monitoring**: Progress monitoring and reporting patterns
- **amoa-remote-agent-coordinator**: Remote agent coordination and multi-host management
- **amoa-task-distribution**: Task distribution strategies and parallel assignment
- **amoa-two-phase-mode**: Two-phase orchestration mode (planning then execution)
- **amoa-verification-patterns**: Task verification and acceptance criteria patterns

### Cross-Plugin Skills (AMIA Integrator)
The following skills belong to the AMIA plugin and integrate with AMOA workflows:
- **amia-ci-cd-pipeline**: CI/CD pipeline management, GitHub Actions workflows
- **amia-pr-review-workflow**: PR review automation, code quality checks
- **amia-release-management**: Version management, changelog generation, release automation
- **amia-quality-gates**: Code quality enforcement, linting, type checking
- **amia-github-projects-sync**: GitHub Projects kanban synchronization
- **amia-kanban-management**: Kanban column management and task routing

---

**This workflow must be followed by all agents. Deviations require Manager
approval (requested up the chain via AMCOS → AMAMA — never a direct
team-internal → MANAGER message; R6 v3).**

---

**Changelog (2.0.0, 2026-06-11)**: Migrated to R6 v3 — removed every direct
AMAMA↔AMOA and AMAMA↔AMIA handoff (the MANAGER reaches team-internal agents only
via AMCOS); added the Board Reconciliation section (TRDD `column:` pipeline is
authoritative, the 8-column GitHub board is its lossless projection via the
`trdd-column:` field, TRDD wins on tie-break); reassigned the `done`/`completed`
flip from AMOA to AMIA (AMOA owns only the pre-PR green-light; nobody self-marks
completed).
