# Bug Reporting Protocol - Part 2: Response Flow and Escalation


## Contents

- [Orchestrator Response Flow](#orchestrator-response-flow)
  - [Step 1: Acknowledgment](#step-1-acknowledgment)
  - [Step 2: GitHub Issue Creation](#step-2-github-issue-creation)
  - [Step 3: Resolution Tracking](#step-3-resolution-tracking)
- [Escalation Handling](#escalation-handling)
  - [Escalation Triggers by Severity](#escalation-triggers-by-severity)
  - [Escalation Flow](#escalation-flow)
  - [Example Escalation Flow (High Severity)](#example-escalation-flow-high-severity)

---

This document covers how the orchestrator handles bug reports and escalation procedures.

**Parent document**: [bug-reporting-protocol.md](bug-reporting-protocol.md)

---

## Orchestrator Response Flow

### Step 1: Acknowledgment

Orchestrator acknowledges bug report (using echo-acknowledgment-protocol):

```json
{
  "type": "bug-report-ack",
  "task_id": "GH-42",
  "bug_id": "auto-generated-or-github-issue",
  "status": "received",
  "received_at": "2025-12-31T03:15:00Z",
  "action": "creating-github-issue"
}
```

### Step 2: GitHub Issue Creation

Orchestrator creates GitHub issue for tracking:

```bash
gh issue create \
  --title "BUG: JWT token validation fails on refresh (GH-42)" \
  --body "$(cat bug-report-GH-42.md)" \
  --label "bug,severity:high,component:auth" \
  --assignee dev-agent-1 \
  --milestone v1.0
```

Response to agent:

```json
{
  "type": "bug-report-response",
  "task_id": "GH-42",
  "bug_id": "GH-89",
  "status": "tracked",
  "github_issue": "https://github.com/user/repo/issues/89",
  "action_required": "fix-immediately",
  "assigned_to": "dev-agent-1",
  "max_attempts": 3
}
```

### Step 3: Resolution Tracking

Agent reports bug fixed:

```json
{
  "type": "bug-fix-report",
  "task_id": "GH-42",
  "bug_id": "GH-89",
  "status": "fixed",
  "fix_commit": "abc123def",
  "test_evidence": "All tests pass - artifacts/tests/fix-verification.log",
  "pr_url": "https://github.com/user/repo/pull/90"
}
```

Orchestrator verifies and closes:

```bash
# Orchestrator runs tests to verify fix
# If tests pass:
gh issue close 89 --comment "Verified fixed in commit abc123def. Tests pass."
```

---

## Escalation Handling

### Escalation Triggers by Severity

| Severity | Max Ack Attempts | Max Reproduction Attempts | Escalation Trigger |
|----------|------------------|---------------------------|-------------------|
| `critical` | 2 | 2 | Blocker identified or max attempts exceeded |
| `high` | 2 | 3 | Blocker identified or max attempts exceeded |
| `normal` | 3 | 3 | Max attempts exceeded |
| `low` | 3 | 3 | Max attempts exceeded |

### Escalation Flow

If orchestrator doesn't acknowledge:

1. **First attempt** (initial bug report):
   - Agent sends bug-report with `attempt: 1` field
   - Wait for acknowledgment

2. **Second attempt** (after no ack):
   - Agent retries bug report with `retry: true, attempt: 2` flag
   - Wait for acknowledgment

3. **Max attempts exceeded**:
   - Agent logs non-responsive orchestrator
   - Agent blocks development if bug severity is critical/high
   - Agent notifies user via session output

If bug cannot be reproduced:

1. **Max reproduction attempts exceeded**:
   - Orchestrator escalates to user
   - Orchestrator considers reassigning task or closing as cannot-reproduce
   - Orchestrator updates GitHub issue with reproduction status

### Example Escalation Flow (High Severity)

```
Attempt 1: Agent sends bug-report (severity: high, attempt: 1)
           -> No ack received
Attempt 2: Agent retries bug-report (retry: true, attempt: 2)
           -> No ack received
           -> Log "Orchestrator unresponsive", block development
           -> Max ack attempts (2) exceeded -> Escalate to user
```
