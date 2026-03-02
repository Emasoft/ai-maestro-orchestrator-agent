---
operation: schedule-claude-tasks
procedure: proc-create-task-plan
workflow-instruction: Step 12 - Task Plan Creation
parent-skill: eoa-two-phase-mode
parent-plugin: emasoft-orchestrator-agent
version: 1.0.0
---

# Schedule Claude Tasks


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Identify Tasks to Create](#step-1-identify-tasks-to-create)
  - [Step 2: Create Tasks with TaskCreate](#step-2-create-tasks-with-taskcreate)
  - [Step 3: Set Task Dependencies](#step-3-set-task-dependencies)
  - [Step 4: Create Task Series](#step-4-create-task-series)
  - [Step 5: Track Task Status](#step-5-track-task-status)
- [Checklist](#checklist)
- [Examples](#examples)
  - [Example: Module Implementation Series](#example-module-implementation-series)
  - [Example: Multi-Module Orchestration](#example-multi-module-orchestration)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## When to Use

Trigger this operation when:
- You receive any instruction that requires tracking
- You are starting implementation of modules
- You need tasks to persist across context compacting

## Prerequisites

- Modules are defined with acceptance criteria
- Task dependencies are identified
- Understanding of Claude Code Tasks API

## Procedure

### Step 1: Identify Tasks to Create

For each module or work item, create a Claude Task:

| Work Item | Task Subject | Task Description |
|-----------|--------------|------------------|
| Module implementation | "Implement [module-name]" | Full module requirements + criteria |
| Bug fix | "Fix [issue-id]: [brief]" | Issue details + reproduction steps |
| Feature addition | "Add [feature]" | Feature requirements + acceptance criteria |
| Verification | "Verify [module-name]" | Verification checklist |

### Step 2: Create Tasks with TaskCreate

Use the Claude Tasks API:

```
TaskCreate(
  subject="Implement auth-core module",
  description="""
Requirements:
- User login with email/password
- JWT token generation and validation
- Session management

Acceptance Criteria:
- [FUNC-001] Users can login with valid credentials
- [FUNC-002] JWT token valid for 24h
- [FUNC-003] Session can be invalidated on logout

Dependencies: None (foundation module)
Priority: High
""",
  activeForm="Implementing auth-core module"
)
```

### Step 3: Set Task Dependencies

Use TaskUpdate to establish blocking relationships:

```
# Create all tasks first
task_1 = TaskCreate(subject="Implement auth-core", ...)
task_2 = TaskCreate(subject="Implement oauth-google", ...)
task_3 = TaskCreate(subject="Implement oauth-github", ...)
task_4 = TaskCreate(subject="Write auth tests", ...)

# Then set dependencies
TaskUpdate(taskId=task_2, addBlockedBy=[task_1])
TaskUpdate(taskId=task_3, addBlockedBy=[task_1])
TaskUpdate(taskId=task_4, addBlockedBy=[task_1, task_2, task_3])
```

### Step 4: Create Task Series

Every task series should include:

1. **Implementation Tasks** - The actual work
2. **Verification Task** - Verify completion criteria
3. **Archive Task** - Document completion
4. **Commit Task** - Commit with series-complete message

```
# Series for auth-core module
task_impl = TaskCreate(subject="Implement auth-core", ...)
task_verify = TaskCreate(subject="Verify auth-core completion", ...)
task_archive = TaskCreate(subject="Archive auth-core documentation", ...)
task_commit = TaskCreate(subject="Commit auth-core with SERIES-COMPLETE", ...)

# Set series dependencies
TaskUpdate(taskId=task_verify, addBlockedBy=[task_impl])
TaskUpdate(taskId=task_archive, addBlockedBy=[task_verify])
TaskUpdate(taskId=task_commit, addBlockedBy=[task_archive])
```

### Step 5: Track Task Status

As work progresses, update task status:

```
# Starting work
TaskUpdate(taskId=task_impl, status="in-progress")

# Completed work
TaskUpdate(taskId=task_impl, status="completed")

# Check all tasks
TaskList()  # Returns current state of all tasks
```

## Checklist

Copy this checklist and track your progress:
- [ ] Identify all work items requiring tasks
- [ ] Create tasks with clear subjects and descriptions
- [ ] Include acceptance criteria in task descriptions
- [ ] Set blocking dependencies between tasks
- [ ] Create verification task for each implementation task
- [ ] Create archive and commit tasks for series closure
- [ ] Update task status as work progresses
- [ ] Use TaskList to verify task state

## Examples

### Example: Module Implementation Series

**Module:** User Profile API

```
# Create implementation task
TaskCreate(
  subject="Implement user-profile module",
  description="""
Module: User Profile API

Acceptance Criteria:
- GET /api/profile returns user profile
- PATCH /api/profile updates profile fields
- Profile endpoint requires authentication
- Response time < 100ms

Files to create:
- src/api/profile.py
- tests/unit/test_profile.py
""",
  activeForm="Implementing user profile API"
)

# Create verification task
TaskCreate(
  subject="Verify user-profile completion",
  description="Run all tests, check acceptance criteria, review code",
  activeForm="Verifying user-profile module"
)

# Create commit task
TaskCreate(
  subject="Commit user-profile [SERIES-COMPLETE]",
  description="Commit with series-complete message format",
  activeForm="Committing user-profile series"
)
```

### Example: Multi-Module Orchestration

**Project:** Authentication System

```
# Phase 1: Foundation
auth_core = TaskCreate(subject="Implement auth-core", ...)

# Phase 2: OAuth providers (parallel)
oauth_google = TaskCreate(subject="Implement oauth-google", ...)
oauth_github = TaskCreate(subject="Implement oauth-github", ...)
TaskUpdate(taskId=oauth_google, addBlockedBy=[auth_core])
TaskUpdate(taskId=oauth_github, addBlockedBy=[auth_core])

# Phase 3: Integration tests (waits for all)
auth_tests = TaskCreate(subject="Write auth integration tests", ...)
TaskUpdate(taskId=auth_tests, addBlockedBy=[auth_core, oauth_google, oauth_github])

# Phase 4: Final verification
final_verify = TaskCreate(subject="Final auth system verification", ...)
TaskUpdate(taskId=final_verify, addBlockedBy=[auth_tests])
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Task not persisting | Context compacted | Use TaskList after compacting to recover state |
| Dependency cycle | Circular blocking | Redesign task dependencies, break cycle |
| Stale task status | Forgot to update | Always update to in-progress/completed |
| Missing task | Not created | Verify all modules have corresponding tasks |

## Related Operations

- [op-identify-task-dependencies.md](../eoa-orchestration-patterns/references/op-identify-task-dependencies.md) - Dependencies inform task blocking
- [op-create-github-issues.md](op-create-github-issues.md) - GitHub issues parallel Claude tasks
- [op-approve-plan-transition.md](op-approve-plan-transition.md) - Transition creates initial tasks
