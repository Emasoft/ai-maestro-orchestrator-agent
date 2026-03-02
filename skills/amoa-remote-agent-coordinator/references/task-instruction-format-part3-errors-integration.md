# Task Instruction Format - Part 3: Errors and Integration

## Contents

- **[3.1 Error States](#31-error-states)** - All possible error states and actions
- **[3.2 Blocked Report Format](#32-blocked-report-format)** - JSON format for blocked tasks
- **[3.3 Failed Report Format](#33-failed-report-format)** - JSON format for failed tasks
- **[3.4 Integration with Other Protocols](#34-integration-with-other-protocols)** - Protocol connections
- **[3.5 Protocol Flow](#35-protocol-flow)** - End-to-end flow diagram
- **[3.6 Example Completed Task](#36-example-completed-task)** - Filled-in instruction example

---

## 3.1 Error States

| State | Trigger | Agent Action | Orchestrator Action |
|-------|---------|--------------|-------------------|
| `blocked` | Cannot proceed | Send escalation message | Provide guidance or reassign |
| `failed` | Implementation impossible | Send completion report (failed) | Reassess requirements |
| `tests-failing` | Cannot make tests pass | Send escalation with test output | Review test expectations |
| `spec-ambiguous` | Unclear requirements | Send escalation with questions | Clarify specification |
| `dependency-blocked` | Waiting on external task | Send blocked notification | Update task dependencies |
| `timeout` | Exceeded time limit | Send status + estimate | Extend or reassign |
| `environment-issue` | Cannot set up environment | Report environment details | Provide alternative approach |

### Error State Transitions

```
ACTIVE → blocked → ACTIVE (after unblocked)
ACTIVE → blocked → REASSIGNED (if cannot unblock)
ACTIVE → failed → CLOSED (task closed)
ACTIVE → tests-failing → ACTIVE (after fix)
ACTIVE → timeout → ACTIVE (after extension)
ACTIVE → timeout → REASSIGNED (if no extension)
```

---

## 3.2 Blocked Report Format

When task is blocked:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "orchestrator-master",
  "subject": "BLOCKED: GH-42 [TASK_NAME]",
  "priority": "high",
  "content": {
    "type": "completion-report",
    "task_id": "GH-42",
    "status": "blocked",
    "blocker": {
      "type": "dependency",
      "description": "Waiting for GH-41 to complete - provides auth module",
      "blocking_task": "GH-41",
      "attempted_solutions": [
        "Tried stubbing auth module: insufficient for integration tests"
      ],
      "assistance_needed": "Expedite GH-41 or provide test auth service instance"
    },
    "partial_completion": {
      "completed_checkpoints": ["Database setup", "API routes"],
      "remaining_work": "Authentication integration",
      "pr_url": "https://github.com/owner/repo/pull/42"
    }
  }
}
```

### Blocker Types

| Type | Description | Example |
|------|-------------|---------|
| `dependency` | Waiting on another task | GH-41 must complete first |
| `spec-clarification` | Requirements unclear | "Should X handle Y case?" |
| `architecture-decision` | Design choice needed | "REST vs GraphQL for this endpoint?" |
| `environment` | Setup issues | "Cannot connect to staging database" |
| `permissions` | Access issues | "Need write access to repo X" |
| `external` | Third-party issue | "API rate limited, waiting reset" |

---

## 3.3 Failed Report Format

When task cannot be completed:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "orchestrator-master",
  "subject": "FAILED: GH-42 [TASK_NAME]",
  "priority": "high",
  "content": {
    "type": "completion-report",
    "task_id": "GH-42",
    "status": "failed",
    "failure": {
      "reason": "Architectural constraint prevents implementation",
      "details": "The existing auth system uses synchronous calls, but the requirement needs async. Refactoring auth is out of scope.",
      "attempted_approaches": [
        "Approach 1: Wrapper around sync calls - too slow",
        "Approach 2: Background job - doesn't meet real-time requirement"
      ],
      "recommendation": "Either expand scope to include auth refactor (estimate: 3 days) or adjust requirement to allow 500ms latency"
    },
    "work_completed": {
      "description": "Research and POC of both approaches",
      "artifacts": [
        "docs_dev/reports/GH-42_approach_analysis.md"
      ],
      "can_be_salvaged": true
    }
  }
}
```

---

## 3.4 Integration with Other Protocols

This format integrates with:

| Protocol | Integration Point | Purpose |
|----------|------------------|---------|
| `echo-acknowledgment-protocol.md` | ACK block | Agent must acknowledge task before starting |
| `messaging-protocol.md` | All messages | Use message schema for task transmission |
| `test-report-format.md` | Completion report | Test results format for completion report |
| `artifact-sharing-protocol.md` | Artifacts section | How to share build outputs |
| `change-notification-protocol.md` | Config updates | Receive config updates during task |

### Cross-Protocol References

**In task instruction, include:**

```markdown
## Protocol References

Before starting this task, familiarize yourself with:

1. **Acknowledgment Protocol**: `references/echo-acknowledgment-protocol.md`
   - How to send ACK when receiving task
   - Status update format

2. **Messaging Protocol**: `references/messaging-protocol.md`
   - Message envelope format
   - Priority levels and routing

3. **Test Report Format**: `references/test-report-format.md`
   - How to format test results
   - Coverage reporting

4. **Artifact Sharing**: `references/artifact-sharing-protocol.md`
   - How to share built artifacts
   - File location conventions
```

---

## 3.5 Protocol Flow

End-to-end task execution flow:

```
1. Orchestrator sends task (this format) via messaging-protocol
   ↓
2. Agent receives task
   ↓
3. Agent acknowledges via echo-acknowledgment-protocol
   ↓
4. Agent reads project config files
   ↓
5. Agent works on task
   ↓
6. Agent sends progress updates at checkpoints
   ↓
7. [Optional] Agent may receive change-notifications during work
   ↓
8. [Optional] Agent may hit blocker → sends blocked report
   ↓
9. Agent runs tests, generates test-report-format
   ↓
10. Agent shares artifacts via artifact-sharing-protocol
    ↓
11. Agent creates PR and links to issue
    ↓
12. Agent sends completion report (this format)
    ↓
13. Orchestrator reviews and closes task
```

### Message Flow Diagram

```
Orchestrator                              Agent
    |                                        |
    |-------- TASK INSTRUCTION ------------->|
    |                                        |
    |<------- [ACK] RECEIVED ----------------|
    |                                        |
    |<------- [PROGRESS] Checkpoint 1 -------|
    |                                        |
    |<------- [PROGRESS] Checkpoint 2 -------|
    |                                        |
    |-------- [STATUS_REQUEST] ------------->|  (if no update)
    |                                        |
    |<------- [PROGRESS] Checkpoint 3 -------|
    |                                        |
    |<------- [DONE] Completion Report ------|
    |                                        |
    |-------- [TASK_CLOSED] ---------------->|
```

---

## 3.6 Example Completed Task

Example of a filled-in task instruction:

```markdown
================================================================================
ACKNOWLEDGMENT REQUIRED (MANDATORY)
================================================================================

Before starting work, you MUST reply with an acknowledgment in this exact format:

[ACK] GH-42-password-reset - {status}
Understanding: {1-line summary of what you will do}

Status options:
- RECEIVED - Task received, will begin work immediately
- CLARIFICATION_NEEDED - Need more info (list your questions)
- REJECTED - Cannot accept task (explain why)
- QUEUED - Have prior tasks, will start after them

DO NOT begin work until you have sent this acknowledgment.
================================================================================

# Task: Implement Password Reset Flow

## Metadata
- **Issue**: GH-42
- **Branch**: feature/password-reset
- **Priority**: high
- **Assigned To**: dev-agent-1
- **Assigned By**: orchestrator-master
- **Assigned At**: 2025-12-30T10:00:00Z
- **Due By**: N/A

---

## Context

### Problem Statement
Users cannot reset their password if they forget it. This task implements
the password reset flow via email verification.

### Background
The auth system already handles login/logout. This adds the "forgot password"
functionality that sends a reset token via email.

### Related Issues
- GH-38: Email service setup (COMPLETE)
- GH-41: User model updates (COMPLETE)

---

## Scope

### DO - What to Implement
1. Add `request_password_reset(email)` endpoint
2. Add `reset_password(token, new_password)` endpoint
3. Generate secure reset tokens with 1-hour expiry
4. Send reset email using existing email service

### DO NOT - Out of Scope
1. Rate limiting (separate issue GH-45)
2. Password strength validation (already exists)
3. Email template redesign (separate issue)

---

## Project Configuration

**Config Location**: `design/config/`
**Config Version**: 2025-12-30T09:00:00Z

### Required Config Files
- `design/config/toolchain.md` - Python 3.12, uv, ruff, pytest
- `design/config/standards.md` - Code standards, TDD, FAIL-FAST
- `design/config/environment.md` - Git config, AI Maestro settings
- `design/specs/architecture.md` - Auth system architecture
- `design/specs/requirements.md` - Password reset requirements (GH-42)

**IMPORTANT**: Read ALL config files before starting. Do NOT rely on this summary alone.

### Critical Settings Summary
(Minimal inline context - full details in config files)
- **Python**: 3.12
- **Package Manager**: uv
- **Line Length**: 88
- **Test Framework**: pytest

---

## Interface Contract

### Inputs

**Request Password Reset:**
- `email: str` - User's email address

**Reset Password:**
- `token: str` - Reset token from email
- `new_password: str` - New password (min 8 chars)

### Outputs

**Request Password Reset:**
- `success: bool` - Always true (don't reveal if email exists)
- `message: str` - "If email exists, reset link sent"

**Reset Password:**
- `success: bool` - True if reset successful
- `error: str | None` - Error message if failed

---

## Files to Modify

| File | Action | Changes |
|------|--------|---------|
| `src/auth/routes.py` | MODIFY | Add reset endpoints |
| `src/auth/services.py` | MODIFY | Add reset logic |
| `src/auth/tokens.py` | CREATE | Token generation |
| `tests/auth/test_reset.py` | CREATE | Reset flow tests |

---

## Test Requirements

### Required Tests
- [ ] `test_request_reset_existing_user`
- [ ] `test_request_reset_nonexistent_user`
- [ ] `test_reset_with_valid_token`
- [ ] `test_reset_with_expired_token`
- [ ] `test_reset_with_invalid_token`
- [ ] `test_token_single_use`

---

## Completion Criteria

### Code Quality
- [ ] All new functions have docstrings
- [ ] Type hints on all function signatures
- [ ] No linting errors
- [ ] Formatted with ruff

### Testing
- [ ] All new tests pass
- [ ] All existing tests pass
- [ ] 80%+ coverage on new code

### Git
- [ ] Committed to feature/password-reset
- [ ] Pushed to origin
- [ ] Conventional commit messages

### Pull Request
- [ ] PR created against main
- [ ] Linked to GH-42
```

---

## Navigation

- **Index**: [task-instruction-format.md](task-instruction-format.md)
- **Previous**: [Part 2: Config and Monitoring](task-instruction-format-part2-config-monitoring.md)
