## Table of Contents
- Example: Decompose and Delegate a Feature
- Input: Feature Request
- Output: Task Plan with Assignments
- Error Handling Reference

# Example: Decompose and Delegate a Feature

This example shows how to decompose a feature request into tasks and delegate them.

**Input:** A feature request from the user (via AMAMA):

```
Feature: Add user authentication module
Requirements:
- OAuth2 login with Google provider
- Session management with JWT tokens
- Rate limiting on login endpoint (5 attempts per minute)
```

**Output:** The orchestrator produces a task plan with assignments:

```
Task Plan: Authentication Module (3 parallel tasks)

Task 1: OAuth2 Integration
  Assign to: ampa-backend-001
  Scope: src/auth/oauth.py, src/auth/providers/google.py
  Success criteria: Google OAuth2 flow completes end-to-end, tokens stored
  Dependencies: None

Task 2: Session Management
  Assign to: ampa-backend-002
  Scope: src/auth/session.py, src/auth/jwt.py
  Success criteria: JWT issued on login, validated on protected routes, expires correctly
  Dependencies: None (uses mock OAuth response until Task 1 merges)

Task 3: Rate Limiting
  Assign to: ampa-backend-003
  Scope: src/middleware/rate_limit.py, tests/test_rate_limit.py
  Success criteria: Login endpoint rejects 6th attempt within 60s window, returns 429
  Dependencies: None (uses mock login endpoint)

Result: 3 tasks delegated in parallel, each with clear scope and success criteria.
```

For more detailed orchestration examples with transcripts, see [orchestration-examples.md](orchestration-examples.md):
- Authentication module implementation from plan handoff
- CI failure coordination with investigation-first pattern
- Parallel code review across 5 developers
- Blocked dependency handling with parallel escalation

---

# Error Handling

| Issue | Cause | Resolution |
|-------|-------|------------|
| Agent unresponsive | Agent crashed or blocked | Poll until response; reassign if unrecoverable |
| Task conflict | Same file modified by multiple agents | Assign non-overlapping scope |
| Verification loop stuck | Agent doesn't check changes | Send explicit verification message |
| Escalation pending | User unavailable | Queue issue, continue other work |

See individual reference files for detailed troubleshooting.
