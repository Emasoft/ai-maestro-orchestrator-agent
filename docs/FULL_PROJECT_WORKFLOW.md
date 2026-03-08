# Full Project Workflow: From Requirements to Delivery

**Version**: 1.5.3
**Last Updated**: 2026-03-08

This document describes the complete workflow for how the AI Maestro agent system handles a project from initial requirements to delivery. All agents must understand this workflow to coordinate effectively.

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
AMAMA ─────────────────────────────────────────────────────►  │
  │                                                          │
  │ 6. Sends requirements to AMAA                             │
  ▼                                                          │
AMAA (Architect)                                              │
  │                                                          │
  │ 7. Creates design document                               │
  │ 8. Sends design to AMAMA                                  │
  ▼                                                          │
AMAMA ◄──── USER APPROVAL ─────────────────────────────────►  │
  │                                                          │
  │ 9. Sends approved design to AMOA                          │
  ▼                                                          │
AMOA (Orchestrator)                                           │
  │                                                          │
  │ 10. Splits design into tasks                             │
  │ 11. Creates task-requirements-documents                  │
  │ 12. Adds tasks to kanban                                 │
  │ 13. Assigns tasks to agents                              │
  ▼                                                          │
IMPLEMENTER AGENTS ◄───────────────────────────────────────► │
  │                                                          │
  │ 14. Work on tasks                                        │
  │ 15. Submit PRs                                           │
  ▼                                                          │
AMIA (Integrator)                                             │
  │                                                          │
  │ 16. Reviews PRs                                          │
  │ 17. Merges or rejects                                    │
  ▼                                                          │
AMOA ◄─────────────────────────────────────────────────────►  │
  │                                                          │
  │ 18. Reports to AMAMA                                      │
  │ 19. Assigns next tasks                                   │
  └──────────────────────────────────────────────────────────┘
```

---

## Kanban Column System

All projects use an **8-column kanban system** on GitHub Projects. Every agent must understand these columns and use the canonical code format consistently.

### Canonical Columns

| # | Column | Code Format | Label | Description |
|---|--------|-------------|-------|-------------|
| 1 | Backlog | `backlog` | `status:backlog` | Entry point for all new issues |
| 2 | Todo | `todo` | `status:todo` | Ready to start, prioritized |
| 3 | In Progress | `in-progress` | `status:in-progress` | Active work by assigned agent |
| 4 | AI Review | `ai-review` | `status:ai-review` | Integrator (AMIA) reviews the PR |
| 5 | Human Review | `human-review` | `status:human-review` | User reviews (big tasks only) |
| 6 | Merge/Release | `merge-release` | `status:merge-release` | Approved and ready to merge |
| 7 | Done | `done` | `status:done` | Completed and merged |
| 8 | Blocked | `blocked` | `status:blocked` | Blocked at any stage |

### Task Routing

- **Small tasks**: In Progress → AI Review → Merge/Release → Done
- **Big tasks**: In Progress → AI Review → Human Review → Merge/Release → Done
- **Human Review** is requested via AMAMA (Assistant Manager asks the user to test/review)
- **Blocked** can be set from any column; task returns to its previous column when unblocked

### Code Format Rules

- **Always use dashes**: `in-progress`, `ai-review`, `merge-release` (NOT underscores)
- **Labels use `status:` prefix**: `status:in-progress`, `status:ai-review`
- **Display names use title case**: "In Progress", "AI Review", "Merge/Release"

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

#### Step 6: Requirements to Architect
**Actor**: AMAMA (Manager)
**Action**:
- Send the requirements to the Architect agent (AMAA)
- Expand the requirements with more details
- Include the list of team member names in the requirements
- Assign to the Architect the task of developing the design document

**Communication**:
- GitHub: Create issue with requirements, assign label for AMAA
- AI Maestro: Message to AMAA with full requirements and team roster

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

#### Step 8: Design Submission
**Actor**: AMAA (Architect)
**Action**:
- Send the completed design document back to the Manager

**Communication**:
- GitHub: Attach design document to issue, mark ready for review
- AI Maestro: Notification to AMAMA that design is ready

#### Step 9: Design Approval
**Actor**: AMAMA (Manager) + USER
**Action**:
- Manager examines the design document
- Manager asks for approval from the User
- If User approves: design is sent to the Orchestrator
- If User rejects: design goes back to Architect with feedback

**Communication**:
- GitHub: Issue comments with design and approval status
- AI Maestro: Message to AMOA with approved design

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

#### Step 19: Task Completion
**Actor**: IMPLEMENTER AGENTS → AMOA
**Action**:
- When an implementer agent finishes a task, notify the Orchestrator
- Orchestrator discusses and asks questions to ensure truly completed
- If OK: Orchestrator gives approval to do the pull-request
- Implementer creates PR

**Communication**:
- AI Maestro: Completion notification from agent to AMOA
- AI Maestro: Approval to PR from AMOA to agent
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

#### Step 21: PR Evaluation
**Actor**: AMIA (Integrator)
**Action**:
- Examine the PR of each task
- Verify compliance with design requirements
- Run tests and linting
- If everything OK: merge to main
- If not OK: refuse PR, report issues to Orchestrator

**Communication**:
- GitHub: PR review comments, approval/rejection
- AI Maestro: Report to AMOA with pass/fail details

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

#### Step 23: Successful PR Handling
**Actor**: AMOA (Orchestrator)
**Action**:
- When Integrator reports successful PR merge, move task to `ai-review` column
  - If AI review passes for small tasks: move to `merge-release`, then `done`
  - If AI review passes for big tasks: move to `human-review` first, then `merge-release`, then `done`
  - Report to Manager (AMAMA) for approval
  - If Manager approves: assign new task to the agent that finished
  - Keep implementer agents always working, never idle

**Communication**:
- GitHub: Update project item status through kanban columns
- AI Maestro: Completion report to AMAMA
- AI Maestro: New task assignment to agent

#### Step 24: Iteration
**Action**:
- This cycle iterates until all tasks are complete
- Each successful merge triggers:
  - Report to Manager
  - New task assignment to available agent

---

## Communication Matrix

| From | To | Channel | Purpose |
|------|-----|---------|---------|
| AMAMA | AMCOS | AI Maestro | Requirements, team requests |
| AMCOS | AMAMA | AI Maestro | Team proposals, status updates |
| AMAMA | AMAA | GitHub + AI Maestro | Requirements, design requests |
| AMAA | AMAMA | GitHub + AI Maestro | Design documents |
| AMAMA | AMOA | GitHub + AI Maestro | Approved designs |
| AMOA | Agents | GitHub + AI Maestro | Task assignments |
| Agents | AMOA | AI Maestro | Status updates, questions |
| AMOA | AMAA | AI Maestro | Design change requests |
| AMOA | AMIA | AI Maestro | PR review requests |
| AMIA | AMOA | AI Maestro | PR review results |
| AMOA | AMAMA | AI Maestro | Completion reports |

---

## Role Boundaries Summary

| Role | Creates | Manages | Cannot Do |
|------|---------|---------|-----------|
| **AMAMA** | Projects | Approvals, user communication | Task assignment |
| **AMCOS** | Agents, teams | Agent lifecycle | Task assignment, projects |
| **AMAA** | Designs | Architecture | Task assignment |
| **AMOA** | Tasks, plans | Kanban, agent coordination | Agents, projects |
| **AMIA** | Nothing | PR reviews, merges | Task assignment |
| **Agents** | Code, PRs | Their assigned tasks | Everything else |

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
| 19 | Create PR | Agent |
| 21 | Review and merge/reject PR | AMIA |
| 23 | Move to "Done" column | AMOA |

---

## Document References

- **Requirements Document**: Created by AMAMA, sent to AMAA
- **Design Document**: Created by AMAA, approved by AMAMA/User
- **Task-Requirements-Document**: Created by AMOA for each task
- **Design-Change-Request**: Created by AMOA when agents suggest improvements
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

**This workflow must be followed by all agents. Deviations require Manager approval.**
