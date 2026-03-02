# Orchestration Examples

## Table of Contents

- 1. Authentication Module Implementation
  - 1.1 When you receive a plan handoff from EAMA for authentication
  - 1.2 Task creation pattern for multi-component modules
- 2. CI Failure Coordination
  - 2.1 When CI tests fail and need coordinated fixes
  - 2.2 Investigation-first pattern for unknown root causes
- 3. Parallel Code Review
  - 3.1 When coordinating reviews across multiple developers
  - 3.2 Section-based decomposition for large codebases
- 4. Blocked Dependency Handling
  - 4.1 When one task blocks on external dependency
  - 4.2 Parallel escalation pattern for infrastructure blockers

---

## 1. Authentication Module Implementation

### 1.1 When you receive a plan handoff from EAMA for authentication

EAMA hands off an approved authentication plan. You create modules and assign tasks.

**Orchestration transcript:**

```
EAMA: Implement the user authentication module according to the approved plan

EOA (You): Creating modules and assigning tasks...

Module: user-authentication
Created TaskCreate(subject="Implement password hashing with bcrypt",
                   description="Use bcrypt with cost factor 12...",
                   activeForm="Implementing password hashing")
Created TaskCreate(subject="Implement session token generation",
                   description="JWT tokens with 24h expiry...",
                   activeForm="Implementing session tokens")
Created TaskCreate(subject="Implement rate limiting middleware",
                   description="Max 5 login attempts per minute...",
                   activeForm="Implementing rate limiting")

Assigning to remote agents via AI Maestro...
- Task 1 -> remote-dev-auth-001
- Task 2 -> remote-dev-auth-002
- Task 3 -> remote-dev-auth-003

Monitoring progress... All 3 tasks assigned. Polling for completion reports every 10 min.
```

### 1.2 Task creation pattern for multi-component modules

**Key points:**
- Break module into independent tasks that can run in parallel
- Each task has clear success criteria in description
- Use `activeForm` to describe current work
- Assign to different agents for parallel execution

---

## 2. CI Failure Coordination

### 2.1 When CI tests fail and need coordinated fixes

Build failures need investigation before fixes can be assigned.

**Orchestration transcript:**

```
EAMA: The build module CI tests are failing. Coordinate the fix across affected components.

EOA (You): Breaking down failure investigation...

Module: build-ci-fixes
Created TaskCreate(subject="Investigate test failures in build pipeline",
                   activeForm="Investigating CI failures")
Assigning to remote-debugger-001...

[After receiving investigation report]
Root cause: dependency version mismatch

Created TaskCreate(subject="Fix dependency version mismatch in package.json",
                   activeForm="Fixing dependency mismatch")
Created TaskCreate(subject="Update CI workflow to pin Node 20.x",
                   activeForm="Updating CI workflow")

Assigning to remote-dev-001 and remote-dev-002...
Monitoring for completion. Will report to EAMA when all tests pass.
```

### 2.2 Investigation-first pattern for unknown root causes

**Key points:**
- Start with investigation task before assigning fixes
- Wait for root cause before creating fix tasks
- Create parallel fix tasks after root cause is known
- Report to EAMA only after all tests pass

---

## 3. Parallel Code Review

### 3.1 When coordinating reviews across multiple developers

Large codebase needs review distributed across 5 developers.

**Orchestration approach:**

1. Decompose the codebase into 5 independent sections (no file conflicts)
2. Create one task per developer: "Review section X and report findings"
3. Each developer works independently and reports findings
4. Orchestrator collects reports and prioritizes issues
5. If any section blocks others, escalate immediately

**Success criteria:** All sections reviewed in parallel, maximizing parallel execution efficiency.

### 3.2 Section-based decomposition for large codebases

**Key points:**
- Ensure sections have no overlapping files
- Each section can be reviewed independently
- Collect all reports before prioritizing
- Escalate cross-section dependencies immediately

---

## 4. Blocked Dependency Handling

### 4.1 When one task blocks on external dependency

Testing team needs to run tests in parallel, but one developer is blocked waiting for database setup.

**Orchestration approach:**

1. Identify that database setup is a blocking dependency
2. Escalate database setup to operations team in parallel
3. Assign other tests that don't need database to other developers
4. When database is ready, unblock the waiting developer
5. Continue with database-dependent tests

**Success criteria:** Maximized parallelization despite dependency.

### 4.2 Parallel escalation pattern for infrastructure blockers

**Key points:**
- Don't wait for blockers to resolve before assigning other work
- Escalate infrastructure issues in parallel with unblocked tasks
- Track blocked and unblocked tasks separately
- Resume blocked tasks as soon as dependency is resolved
