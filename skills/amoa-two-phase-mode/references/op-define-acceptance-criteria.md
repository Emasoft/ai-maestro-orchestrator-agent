---
operation: define-acceptance-criteria
procedure: proc-decompose-design
workflow-instruction: Step 10 - Design Decomposition
parent-skill: eoa-two-phase-mode
parent-plugin: emasoft-orchestrator-agent
version: 1.0.0
---

# Define Acceptance Criteria


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Apply SMART Criteria](#step-1-apply-smart-criteria)
  - [Step 2: Write Criterion Statement](#step-2-write-criterion-statement)
  - [Step 3: Add Verification Method](#step-3-add-verification-method)
  - [Step 4: Group by Category](#step-4-group-by-category)
  - [Step 5: Document in Module Definition](#step-5-document-in-module-definition)
- [Checklist](#checklist)
- [Examples](#examples)
  - [Example: User Profile Module](#example-user-profile-module)
  - [Example: File Upload Module](#example-file-upload-module)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## When to Use

Trigger this operation when:
- You are defining modules/tasks and need clear completion conditions
- You need to specify what "done" means for a task
- You want to create testable success conditions

## Prerequisites

- Module or task is defined with a description
- Understanding of the feature requirements
- Knowledge of testing approach

## Procedure

### Step 1: Apply SMART Criteria

Each acceptance criterion must be:

| Attribute | Description | Bad Example | Good Example |
|-----------|-------------|-------------|--------------|
| **Specific** | Precisely defined | "Auth works" | "Users can login with email/password" |
| **Measurable** | Quantifiable or verifiable | "Fast response" | "Response time < 200ms" |
| **Achievable** | Technically feasible | "100% uptime" | "99.9% uptime" |
| **Relevant** | Tied to requirement | "Nice animations" | "Form validates input" |
| **Testable** | Can be verified | "Users happy" | "All unit tests pass" |

### Step 2: Write Criterion Statement

Use this format:

```
[Actor] can [action] [object] [condition/result]
```

**Examples:**
- "Users can login with valid email/password and receive JWT token"
- "System rejects login attempts with invalid credentials after 3 tries"
- "API returns user profile within 200ms for authenticated requests"

### Step 3: Add Verification Method

For each criterion, specify how to verify:

```yaml
criterion: "Users can login with email/password"
verification:
  type: "automated_test"
  test_file: "tests/unit/test_login.py"
  test_function: "test_successful_login"

criterion: "Response time < 200ms"
verification:
  type: "performance_test"
  tool: "pytest-benchmark"
  threshold: "200ms p95"

criterion: "UI matches design spec"
verification:
  type: "manual_review"
  reviewer: "design_team"
  artifact: "screenshots"
```

### Step 4: Group by Category

Organize criteria into categories:

```yaml
acceptance_criteria:
  functional:
    - "Users can login with email/password"
    - "Users can logout and invalidate session"
    - "Users can reset password via email"

  non_functional:
    - "Login response time < 200ms"
    - "Password stored with bcrypt (cost factor 12)"
    - "Session tokens expire after 24 hours"

  edge_cases:
    - "System blocks after 5 failed login attempts"
    - "Concurrent sessions handled correctly"
```

### Step 5: Document in Module Definition

Update the module with complete criteria:

```yaml
module:
  id: "auth-core"
  name: "Core Authentication"
  acceptance_criteria:
    - "[FUNC-001] Users can login with valid email/password and receive JWT"
    - "[FUNC-002] System rejects invalid credentials with appropriate error"
    - "[FUNC-003] Users can logout and session is invalidated"
    - "[PERF-001] Login endpoint responds in < 200ms (p95)"
    - "[SEC-001] Passwords stored with bcrypt (cost 12)"
    - "[EDGE-001] Account locked after 5 failed attempts"
  verification_method: "automated_tests + security_review"
```

## Checklist

Copy this checklist and track your progress:
- [ ] Apply SMART criteria to each condition
- [ ] Use standard format: Actor + Action + Object + Condition
- [ ] Specify verification method for each criterion
- [ ] Group by category (functional, non-functional, edge cases)
- [ ] Assign unique IDs to criteria for tracking
- [ ] Document in module definition
- [ ] Verify all criteria are testable

## Examples

### Example: User Profile Module

**Bad Acceptance Criteria:**
- "Profile should work"
- "Users can update profile"
- "Fast and secure"

**Good Acceptance Criteria:**
```yaml
acceptance_criteria:
  functional:
    - "[FUNC-001] GET /api/profile returns current user's profile (name, email, avatar)"
    - "[FUNC-002] PATCH /api/profile updates allowed fields (name, avatar)"
    - "[FUNC-003] PATCH /api/profile rejects invalid email format"
    - "[FUNC-004] Profile changes are immediately reflected"

  non_functional:
    - "[PERF-001] GET /api/profile responds in < 100ms (p95)"
    - "[SEC-001] Profile endpoint requires valid JWT"
    - "[SEC-002] Users can only access their own profile"

  edge_cases:
    - "[EDGE-001] System handles missing optional fields gracefully"
    - "[EDGE-002] Concurrent updates to same profile handled correctly"

  verification:
    automated: "tests/unit/test_profile.py, tests/integration/test_profile_api.py"
    manual: "Security review checklist"
```

### Example: File Upload Module

**Acceptance Criteria:**
```yaml
acceptance_criteria:
  - "[FUNC-001] Users can upload files up to 10MB"
  - "[FUNC-002] System accepts: jpg, png, pdf, docx"
  - "[FUNC-003] Upload returns file URL and metadata"
  - "[FUNC-004] Files stored in cloud storage (S3)"
  - "[SEC-001] Files scanned for malware before storage"
  - "[SEC-002] Uploaded files not directly executable"
  - "[PERF-001] Upload completes within 5s for 10MB file"
  - "[EDGE-001] Partial upload can be resumed"
  - "[EDGE-002] Duplicate file detection by hash"
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Vague criterion | Missing specifics | Rewrite with SMART attributes |
| Untestable criterion | No clear verification | Add explicit test method |
| Missing edge cases | Only happy path covered | Add error/boundary conditions |
| Overlapping criteria | Duplicate conditions | Consolidate or clarify distinction |
| Scope creep | Criteria beyond module scope | Move to appropriate module |

## Related Operations

- [op-decompose-goals-to-modules.md](op-decompose-goals-to-modules.md) - Modules need acceptance criteria
- [op-create-github-issues.md](op-create-github-issues.md) - Criteria go into GitHub issues
- [op-approve-plan-transition.md](op-approve-plan-transition.md) - Validation checks criteria completeness
