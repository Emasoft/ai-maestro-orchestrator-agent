# Messaging Protocol Part 3: Message Types by Category


## Contents

- [3.1 Task Management Messages](#31-task-management-messages)
  - [Task Assignment](#task-assignment)
  - [Fix Request](#fix-request)
  - [Completion Report](#completion-report)
- [3.2 Status and Progress Messages](#32-status-and-progress-messages)
  - [Status Request](#status-request)
  - [Progress Update](#progress-update)
- [3.3 Approvals and Rejections](#33-approvals-and-rejections)
  - [Approval](#approval)
  - [Rejection](#rejection)
- [3.4 Escalations](#34-escalations)
  - [Escalation to Orchestrator/User](#escalation-to-orchestratoruser)
  - [Escalation Response](#escalation-response)
- [Related Sections](#related-sections)

---

**Parent document**: [messaging-protocol.md](messaging-protocol.md)

---

## 3.1 Task Management Messages

### Task Assignment

Use when assigning new work to an agent.

```json
{
  "type": "task",
  "task_id": "GH-42",
  "instructions": "Detailed instructions for the task",
  "completion_criteria": [
    "All unit tests pass",
    "PR created with description",
    "No linting errors"
  ],
  "test_requirements": [
    "test_feature_basic",
    "test_feature_edge_cases"
  ],
  "report_back": true
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | YES | Must be `"task"` |
| `task_id` | YES | GitHub issue reference (e.g., `GH-42`) |
| `instructions` | YES | Clear task description |
| `completion_criteria` | YES | List of success conditions |
| `test_requirements` | NO | Specific tests that must pass |
| `report_back` | NO | Whether to send completion report (default: true) |

---

### Fix Request

Use when requesting fixes to submitted work.

```json
{
  "type": "fix-request",
  "task_id": "GH-42",
  "pr_url": "https://github.com/org/repo/pull/123",
  "issues": [
    {"file": "src/auth.py", "line": 42, "issue": "Missing null check before accessing user.id"},
    {"file": "src/auth.py", "line": 67, "issue": "Test coverage insufficient for error path"}
  ],
  "fix_instructions": "Add null check before accessing user.id. Add test case for user=None scenario."
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | YES | Must be `"fix-request"` |
| `task_id` | YES | Original task reference |
| `pr_url` | YES | URL to the PR needing fixes |
| `issues` | YES | Array of specific issues found |
| `fix_instructions` | YES | Clear instructions for fixing |

---

### Completion Report

Sent by agent when task is complete.

```json
{
  "type": "completion-report",
  "task_id": "GH-42",
  "status": "success",
  "pr_url": "https://github.com/org/repo/pull/123",
  "test_results": "All 47 tests pass (32 unit, 15 integration)",
  "notes": "Encountered minor issue with OAuth token refresh, added workaround documented in PR."
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | YES | Must be `"completion-report"` |
| `task_id` | YES | Task being reported on |
| `status` | YES | `"success"`, `"blocked"`, or `"failed"` |
| `pr_url` | Conditional | Required if status is success |
| `test_results` | YES | Summary of test execution |
| `notes` | NO | Additional context or issues encountered |

---

## 3.2 Status and Progress Messages

### Status Request

Use to request current status of a task.

```json
{
  "type": "status-request",
  "task_id": "GH-42",
  "last_update": "2025-12-30T08:00:00Z"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | YES | Must be `"status-request"` |
| `task_id` | YES | Task to get status for |
| `last_update` | NO | Last known update timestamp |

---

### Progress Update

Sent by agent to report ongoing progress.

```json
{
  "type": "progress-update",
  "task_id": "GH-42",
  "progress_percent": 60,
  "current_activity": "Writing integration tests for OAuth flow",
  "blockers": [],
  "remaining_steps": [
    "Complete integration tests",
    "Run full test suite",
    "Create PR with description"
  ]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | YES | Must be `"progress-update"` |
| `task_id` | YES | Task being reported on |
| `progress_percent` | YES | Estimated completion (0-100) |
| `current_activity` | YES | What agent is currently doing |
| `blockers` | YES | Array of blocking issues (empty if none) |
| `remaining_steps` | YES | List of remaining work |

---

## 3.3 Approvals and Rejections

### Approval

Use to approve completed work.

```json
{
  "type": "approval",
  "task_id": "GH-42",
  "pr_url": "https://github.com/org/repo/pull/123",
  "message": "Approved. Code looks good, merging now."
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | YES | Must be `"approval"` |
| `task_id` | YES | Task being approved |
| `pr_url` | YES | URL of approved PR |
| `message` | NO | Additional feedback |

---

### Rejection

Use to reject work that needs changes.

```json
{
  "type": "rejection",
  "task_id": "GH-42",
  "pr_url": "https://github.com/org/repo/pull/123",
  "reason": "Tests fail on CI due to missing mock configuration",
  "required_fixes": [
    "Fix flaky test in test_auth.py:test_timeout",
    "Configure test instance of external service",
    "Add retry logic for network calls"
  ]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | YES | Must be `"rejection"` |
| `task_id` | YES | Task being rejected |
| `pr_url` | YES | URL of rejected PR |
| `reason` | YES | Clear explanation of rejection |
| `required_fixes` | YES | List of changes needed |

---

## 3.4 Escalations

### Escalation to Orchestrator/User

Use when agent encounters a decision requiring input.

```json
{
  "type": "escalation",
  "task_id": "GH-42",
  "escalation_type": "architecture",
  "description": "OAuth implementation requires choosing between implicit grant and authorization code flow. Implicit is simpler but less secure.",
  "options": [
    "Option A: Use implicit grant - simpler, works for SPA, less secure",
    "Option B: Use authorization code flow - more complex, requires backend, more secure"
  ],
  "recommendation": "B",
  "awaiting_response": true
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | YES | Must be `"escalation"` |
| `task_id` | YES | Related task |
| `escalation_type` | YES | `"architecture"`, `"security"`, `"dependency"`, or `"unclear-spec"` |
| `description` | YES | Detailed description of the issue |
| `options` | YES | Array of possible resolutions |
| `recommendation` | NO | Agent's recommended option |
| `awaiting_response` | YES | Set to `true` |

---

### Escalation Response

Use to respond to an escalation.

```json
{
  "type": "escalation-response",
  "task_id": "GH-42",
  "decision": "B",
  "additional_instructions": "Proceed with authorization code flow. Use PKCE for additional security. Coordinate with backend team for token endpoint."
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | YES | Must be `"escalation-response"` |
| `task_id` | YES | Related task |
| `decision` | YES | Chosen option (matches option letter) |
| `additional_instructions` | NO | Extra guidance for implementation |

---

## Related Sections

- [Part 1: API and Schema](messaging-protocol-part1-api-schema.md) - Message envelope format
- [Part 2: Send and Receive](messaging-protocol-part2-send-receive.md) - How to send these messages
- [Part 5: Response Expectations](messaging-protocol-part5-notifications-responses.md) - What response each type expects
