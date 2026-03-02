---
operation: identify-task-dependencies
procedure: proc-decompose-design
workflow-instruction: Step 10 - Design Decomposition
parent-skill: eoa-orchestration-patterns
parent-plugin: emasoft-orchestrator-agent
version: 1.0.0
---

# Identify Task Dependencies


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: List All Tasks](#step-1-list-all-tasks)
  - [Step 2: Identify Dependency Types](#step-2-identify-dependency-types)
  - [Step 3: Build Dependency Matrix](#step-3-build-dependency-matrix)
  - [Step 4: Identify Parallel Opportunities](#step-4-identify-parallel-opportunities)
  - [Step 5: Document with Claude Tasks Blocking](#step-5-document-with-claude-tasks-blocking)
- [Checklist](#checklist)
- [Examples](#examples)
  - [Example: API Feature Implementation](#example-api-feature-implementation)
  - [Example: Microservices Feature](#example-microservices-feature)
  - [Example: Circular Dependency Detection](#example-circular-dependency-detection)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## When to Use

Trigger this operation when:
- You have decomposed a goal into multiple tasks/modules
- You need to determine execution order
- You want to identify which tasks can run in parallel

## Prerequisites

- Tasks/modules have been defined
- Task scope boundaries are clear
- Understanding of technical requirements for each task

## Procedure

### Step 1: List All Tasks

Create a task inventory:

```markdown
| Task ID | Task Name | Description |
|---------|-----------|-------------|
| T1 | Core Auth | Base authentication logic |
| T2 | Google OAuth | Google sign-in integration |
| T3 | GitHub OAuth | GitHub sign-in integration |
| T4 | Session Mgmt | Session handling |
| T5 | Auth Tests | Comprehensive auth tests |
```

### Step 2: Identify Dependency Types

For each task, identify dependencies:

| Dependency Type | Description | Example |
|-----------------|-------------|---------|
| **Code Dependency** | Task needs code from another task | OAuth needs Core Auth functions |
| **Data Dependency** | Task needs data/schema from another | API needs DB schema |
| **Interface Dependency** | Task needs API/contract from another | Frontend needs API spec |
| **Resource Dependency** | Task needs shared resource | Both need test database |
| **Knowledge Dependency** | Task needs information from another | Docs need implementation details |

### Step 3: Build Dependency Matrix

Create a matrix showing dependencies:

| Task | Depends On | Blocks |
|------|------------|--------|
| T1 (Core Auth) | - | T2, T3, T4 |
| T2 (Google OAuth) | T1 | T5 |
| T3 (GitHub OAuth) | T1 | T5 |
| T4 (Session Mgmt) | T1 | T5 |
| T5 (Auth Tests) | T1, T2, T3, T4 | - |

### Step 4: Identify Parallel Opportunities

Tasks without shared dependencies can run in parallel:

```
Execution Order:
  Phase 1: T1 (sequential - foundation)
  Phase 2: T2, T3, T4 (parallel - all depend only on T1)
  Phase 3: T5 (sequential - depends on all above)
```

**Parallel-Safe Criteria:**
- No shared write access to files
- No data dependencies between them
- No sequential interface requirements
- No resource contention

### Step 5: Document with Claude Tasks Blocking

Use Claude Tasks API to enforce dependencies:

```
TaskCreate(subject="Core Auth", ...)  -> task_id_1
TaskCreate(subject="Google OAuth", ...)  -> task_id_2
TaskCreate(subject="GitHub OAuth", ...)  -> task_id_3

TaskUpdate(taskId=task_id_2, addBlockedBy=[task_id_1])
TaskUpdate(taskId=task_id_3, addBlockedBy=[task_id_1])
```

## Checklist

Copy this checklist and track your progress:
- [ ] List all tasks with IDs and descriptions
- [ ] For each task, identify dependency types
- [ ] Build dependency matrix (depends on / blocks)
- [ ] Identify parallel execution opportunities
- [ ] Verify no circular dependencies
- [ ] Document execution phases
- [ ] Use Claude Tasks to enforce blocking

## Examples

### Example: API Feature Implementation

**Tasks:**
1. DB Schema Changes
2. Backend API Endpoints
3. Frontend Components
4. Integration Tests

**Dependency Analysis:**
```
DB Schema (T1) -> Backend API (T2) -> Frontend (T3) -> Integration Tests (T4)
                                   |
                                   -> Integration Tests (T4)
```

**Execution Phases:**
- Phase 1: T1 (DB Schema) - sequential
- Phase 2: T2 (Backend API) - blocked by T1
- Phase 3: T3 (Frontend) - blocked by T2
- Phase 4: T4 (Integration) - blocked by T2, T3

### Example: Microservices Feature

**Tasks:**
1. User Service changes
2. Auth Service changes
3. API Gateway updates
4. Service tests

**Dependency Analysis:**
```
User Service (T1) --\
                     --> API Gateway (T3) --> Tests (T4)
Auth Service (T2) --/
```

**Execution Phases:**
- Phase 1: T1, T2 (parallel - independent services)
- Phase 2: T3 (blocked by T1, T2)
- Phase 3: T4 (blocked by T3)

### Example: Circular Dependency Detection

**Problem:**
```
T1 depends on T3
T2 depends on T1
T3 depends on T2
```

**Resolution:** Break the cycle by:
1. Extracting shared interface to new task T0
2. T1, T2, T3 all depend on T0
3. Remove inter-dependencies

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Circular dependency | Tasks depend on each other | Extract shared interface, break cycle |
| Missing dependency | Task fails due to unmet prereq | Re-analyze, add missing dependency |
| Over-constrained | Too many sequential dependencies | Look for parallel opportunities |
| Phantom dependency | Dependency doesn't actually exist | Remove, enable parallel execution |

## Related Operations

- [op-decompose-goals-to-modules.md](op-decompose-goals-to-modules.md) - Decomposition before dependency analysis
- [op-schedule-claude-tasks.md](op-schedule-claude-tasks.md) - Schedule with dependencies
- [op-define-scope-boundaries.md](op-define-scope-boundaries.md) - Scope affects dependencies
