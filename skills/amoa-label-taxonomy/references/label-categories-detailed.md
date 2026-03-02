# Label Categories (Detailed)

## Table of Contents

- [Assignment Labels (`assign:*`)](#assignment-labels-assign)
  - [Rules](#rules)
  - [Assignment Authority](#assignment-authority)
  - [Conflict Resolution](#conflict-resolution)
- [Status Labels (`status:*`)](#status-labels-status)
  - [Rules](#rules-1)
  - [Status Workflow](#status-workflow)
- [Priority Labels (`priority:*`)](#priority-labels-priority)
  - [Rules](#rules-2)
- [Type Labels (`type:*`)](#type-labels-type)
  - [Rules](#rules-3)
- [Component Labels (`component:*`)](#component-labels-component)
  - [Rules](#rules-4)
- [Effort Labels (`effort:*`)](#effort-labels-effort)
  - [Rules](#rules-5)
- [Platform Labels (`platform:*`)](#platform-labels-platform)
  - [Rules](#rules-6)
- [Toolchain Labels (`toolchain:*`)](#toolchain-labels-toolchain)
  - [Rules](#rules-7)
- [Review Labels (`review:*`)](#review-labels-review)
  - [Rules](#rules-8)

## Assignment Labels (`assign:*`)

**Purpose:** Track which agent is assigned to work on an issue.

**CRITICAL:** In single-account mode, `assign:*` labels REPLACE GitHub assignees for agent tracking.

| Label | Description | When to Use |
|-------|-------------|-------------|
| `assign:<agent-session-name>` | Specific agent assigned | When EOA assigns task to agent |
| `assign:implementer-1` | First implementer agent | For code implementation tasks |
| `assign:implementer-2` | Second implementer agent | For parallel implementation |
| `assign:code-reviewer` | Code review agent | For PR review tasks |
| `assign:orchestrator` | Orchestrator handling | When EOA handles directly |
| `assign:human` | Human developer | When human intervention needed |
| `assign:remote` | Remote agent (any) | For remote execution tasks |
| `assign:local` | Local agent | For local execution tasks |

**Rules:**
- An issue should have AT MOST ONE `assign:*` label at a time
- When reassigning, REMOVE old `assign:*` label BEFORE adding new one
- Use `gh issue edit --remove-label "assign:old" --add-label "assign:new"`

**Assignment Authority:**

| Agent | Authority | When to Use |
|-------|-----------|-------------|
| **EOA** | Primary | Normal task assignment during orchestration |
| **ECOS** | Override | Agent failure, termination, or replacement |
| **EIA** | Limited | Only for `assign:code-reviewer` on PRs |
| **EAMA** | Limited | Only for `assign:human` escalations |

**Conflict Resolution:**
1. If EOA and ECOS both try to assign, ECOS wins (lifecycle takes priority)
2. If assignment conflict detected, message the other agent before changing
3. Use AI Maestro to coordinate: `{"type": "request", "message": "Requesting assignment of #42 to implementer-2"}`

## Status Labels (`status:*`)

**Purpose:** Track the current workflow state of an issue.

| Label | Description | Who Sets It |
|-------|-------------|-------------|
| `status:backlog` | In backlog, needs triage or is deferred | Created automatically, by user, or EOA after triage |
| `status:todo` | Ready to be worked on | EOA when assigning |
| `status:in-progress` | Currently being worked on | Assigned agent when starting |
| `status:blocked` | Cannot proceed (includes waiting for info, intentionally paused) | Agent when blocked, EOA or ECOS |
| `status:ai-review` | Integrator reviews ALL tasks | Agent after completing work |
| `status:human-review` | User reviews BIG tasks only | EIA after AI review passes |
| `status:merge-release` | Ready to merge | EIA or user after review |
| `status:done` | Completed | EIA after merge |

**Rules:**
- An issue should have EXACTLY ONE `status:*` label
- Status transitions follow a defined workflow
- Always update status when issue state changes

**Status Workflow:**
```
backlog → todo → in-progress → ai-review → human-review → merge-release → done
                       ↓                        ↑ (BIG tasks only)
                    blocked → (resolved) → in-progress
```

## Priority Labels (`priority:*`)

| Label | Description | Meaning |
|-------|-------------|---------|
| `priority:critical` | Must fix immediately | Blocking production or other work |
| `priority:high` | Should complete soon | Important for current milestone |
| `priority:normal` | Standard priority | Regular backlog item |
| `priority:low` | Nice to have | Can be deferred |

**Rules:**
- An issue should have EXACTLY ONE `priority:*` label
- Priority is set during triage by EOA or ECOS
- Priority can be escalated by any agent when circumstances change

## Type Labels (`type:*`)

| Label | Description | Examples |
|-------|-------------|----------|
| `type:feature` | New functionality | Add user authentication |
| `type:bug` | Something isn't working | Login fails on Safari |
| `type:refactor` | Code improvement without behavior change | Extract service class |
| `type:docs` | Documentation only | Update API reference |
| `type:test` | Testing improvements | Add integration tests |
| `type:chore` | Maintenance tasks | Update dependencies |
| `type:security` | Security related | Fix XSS vulnerability |
| `type:performance` | Performance improvement | Optimize database queries |
| `type:epic` | Large multi-issue feature | User management system |
| `type:blocker` | Issue tracking a blocking problem that prevents another task from continuing | Missing API credentials needed for #42 |

**Rules:**
- An issue should have EXACTLY ONE `type:*` label
- Type is set when issue is created
- Type should not change after creation (create new issue if scope changes)
- `type:blocker` issues are special: they track the CAUSE (the blocking problem), not the blocked task itself. When the blocker is resolved, close the `type:blocker` issue and unblock the referenced task.

## Component Labels (`component:*`)

| Label | Description |
|-------|-------------|
| `component:api` | API endpoints and controllers |
| `component:ui` | User interface components |
| `component:database` | Database schemas, migrations, queries |
| `component:auth` | Authentication and authorization |
| `component:infra` | Infrastructure and DevOps |
| `component:core` | Core business logic |
| `component:tests` | Test infrastructure |
| `component:docs` | Documentation system |

**Rules:**
- An issue can have MULTIPLE `component:*` labels
- Add all components that will be touched
- Helps with code review assignment

## Effort Labels (`effort:*`)

| Label | Description | Typical Scope |
|-------|-------------|---------------|
| `effort:xs` | Trivial change | Single line fix |
| `effort:s` | Small task | Single function or file |
| `effort:m` | Medium task | Multiple files, one component |
| `effort:l` | Large task | Multiple components |
| `effort:xl` | Epic sized | System-wide changes |

**Rules:**
- An issue should have EXACTLY ONE `effort:*` label
- Effort is estimated during triage
- If effort changes significantly, update the label

## Platform Labels (`platform:*`)

| Label | Description |
|-------|-------------|
| `platform:linux` | Linux environments |
| `platform:macos` | macOS environments |
| `platform:windows` | Windows environments |
| `platform:docker` | Docker containers |
| `platform:cloud` | Cloud deployment (AWS, GCP, etc.) |

**Rules:**
- An issue can have MULTIPLE `platform:*` labels
- Used for routing to agents with correct environment
- Helps with test matrix planning

## Toolchain Labels (`toolchain:*`)

| Label | Description |
|-------|-------------|
| `toolchain:python` | Python development |
| `toolchain:node` | Node.js/JavaScript/TypeScript |
| `toolchain:rust` | Rust development |
| `toolchain:go` | Go development |
| `toolchain:docker` | Docker tooling |
| `toolchain:terraform` | Infrastructure as code |

**Rules:**
- An issue can have MULTIPLE `toolchain:*` labels
- Helps match tasks to agents with required skills
- Used for environment setup verification

## Review Labels (`review:*`)

| Label | Description | Who Sets It |
|-------|-------------|-------------|
| `review:needed` | Needs review | PR creator |
| `review:in-progress` | Review underway | Reviewer |
| `review:changes-requested` | Changes required | Reviewer |
| `review:approved` | Review passed | Reviewer |
| `review:blocked` | Cannot review (conflicts, etc.) | Reviewer |

**Rules:**
- Used primarily on PRs, not issues
- An PR should have AT MOST ONE `review:*` label
- Updated by EIA code-reviewer agent
