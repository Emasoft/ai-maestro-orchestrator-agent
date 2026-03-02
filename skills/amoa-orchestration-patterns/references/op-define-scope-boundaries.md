---
operation: define-scope-boundaries
procedure: proc-decompose-design
workflow-instruction: Step 10 - Design Decomposition
parent-skill: eoa-orchestration-patterns
parent-plugin: emasoft-orchestrator-agent
version: 1.0.0
---

# Define Scope Boundaries


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Identify Scope Dimensions](#step-1-identify-scope-dimensions)
  - [Step 2: Document Explicit Boundaries](#step-2-document-explicit-boundaries)
- [Task: [Task Name]](#task-task-name)
  - [In Scope](#in-scope)
  - [Out of Scope (DO NOT TOUCH)](#out-of-scope-do-not-touch)
  - [Step 3: Verify Non-Overlapping Scopes](#step-3-verify-non-overlapping-scopes)
  - [Step 4: Define Shared Resources Protocol](#step-4-define-shared-resources-protocol)
  - [Step 5: Include Boundaries in Task Prompt](#step-5-include-boundaries-in-task-prompt)
- [Scope Boundaries](#scope-boundaries)
- [Checklist](#checklist)
- [Examples](#examples)
  - [Example: Parallel Authentication Implementation](#example-parallel-authentication-implementation)
  - [Example: Line-Based Division](#example-line-based-division)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## When to Use

Trigger this operation when:
- You are assigning tasks to multiple agents
- You need to ensure non-overlapping work assignments
- You want to prevent file conflicts between parallel agents

## Prerequisites

- Tasks have been decomposed into modules/units
- Agents have been selected for each task
- Task dependencies are identified

## Procedure

### Step 1: Identify Scope Dimensions

Define boundaries across these dimensions:

| Dimension | Description | Example |
|-----------|-------------|---------|
| **Files** | Which files the agent can modify | `src/auth/*.py` only |
| **Functions** | Which functions to implement/modify | `login()`, `logout()` only |
| **Layers** | Which architectural layer | API layer only, not DB |
| **Features** | Which feature subset | Google OAuth only, not GitHub |
| **Tests** | Which test scope | Unit tests only, not e2e |

### Step 2: Document Explicit Boundaries

For each task assignment, document:

```markdown
## Task: [Task Name]
**Assigned to:** [Agent Name]

### In Scope
- [ ] Files: `src/auth/google_oauth.py`
- [ ] Functions: `authenticate_with_google()`, `refresh_google_token()`
- [ ] Tests: Unit tests in `tests/unit/test_google_oauth.py`

### Out of Scope (DO NOT TOUCH)
- Files: `src/auth/github_oauth.py` (assigned to another agent)
- Files: `src/db/*` (database layer)
- Functions: `session_manager.*` (shared utility)
```

### Step 3: Verify Non-Overlapping Scopes

Create a scope matrix to verify no overlaps:

| Resource | Agent 1 | Agent 2 | Agent 3 |
|----------|---------|---------|---------|
| `auth/google.py` | WRITE | - | - |
| `auth/github.py` | - | WRITE | - |
| `auth/session.py` | READ | READ | READ |
| `api/routes.py` | WRITE (lines 1-50) | - | WRITE (lines 51-100) |

**Rule:** No two agents can have WRITE access to the same resource.

### Step 4: Define Shared Resources Protocol

For resources that must be shared:

| Resource Type | Protocol |
|---------------|----------|
| Read-only shared | Any agent can read, no writes |
| Sequential shared | Only one agent at a time, pass token |
| Locked shared | Orchestrator holds lock, agents request access |

### Step 5: Include Boundaries in Task Prompt

Always include in the task prompt:

```
## Scope Boundaries

**You CAN modify:**
- `src/auth/google_oauth.py`
- `tests/unit/test_google_oauth.py`

**You CANNOT modify (other agents own these):**
- `src/auth/github_oauth.py`
- `src/auth/session.py`
- Any file in `src/db/`

**Shared resources (read-only for you):**
- `src/auth/constants.py`
- `src/utils/http_client.py`

If you need changes to out-of-scope files, report back instead of making changes.
```

## Checklist

Copy this checklist and track your progress:
- [ ] Identify all files involved in the overall task
- [ ] Assign each file to exactly one agent (or mark as shared read-only)
- [ ] Document in-scope and out-of-scope items for each agent
- [ ] Verify no overlapping WRITE access
- [ ] Define shared resource protocol
- [ ] Include scope boundaries in each task prompt

## Examples

### Example: Parallel Authentication Implementation

**Overall Task:** Implement OAuth2 for Google and GitHub

**Agent 1 Scope (Google OAuth):**
```
In Scope:
- src/auth/google_oauth.py (create)
- tests/unit/test_google_oauth.py (create)
- docs/google-oauth.md (create)

Out of Scope:
- src/auth/github_oauth.py (Agent 2)
- src/auth/base.py (shared, read-only)
```

**Agent 2 Scope (GitHub OAuth):**
```
In Scope:
- src/auth/github_oauth.py (create)
- tests/unit/test_github_oauth.py (create)
- docs/github-oauth.md (create)

Out of Scope:
- src/auth/google_oauth.py (Agent 1)
- src/auth/base.py (shared, read-only)
```

### Example: Line-Based Division

**Overall Task:** Implement 6 API endpoints in routes.py

**Agent 1 Scope:**
```
- routes.py lines 1-100 (endpoints: /users, /profile)
- Corresponding tests for these endpoints
```

**Agent 2 Scope:**
```
- routes.py lines 101-200 (endpoints: /posts, /comments, /likes, /shares)
- Corresponding tests for these endpoints
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| File conflict | Two agents modified same file | Roll back, re-define boundaries, retry |
| Scope creep | Agent modified out-of-scope file | Revert changes, reinforce boundaries |
| Unclear boundary | Ambiguous file ownership | Explicitly assign every file in scope matrix |
| Dependency conflict | Agent needs out-of-scope change | Report back to orchestrator for coordination |

## Related Operations

- [op-identify-task-dependencies.md](op-identify-task-dependencies.md) - Dependencies affect scope design
- [op-select-agent-for-task.md](op-select-agent-for-task.md) - Select agents before defining scope
- [op-decompose-goals-to-modules.md](op-decompose-goals-to-modules.md) - Decomposition informs boundaries
