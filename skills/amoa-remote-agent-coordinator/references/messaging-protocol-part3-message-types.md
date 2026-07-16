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

`fix-request` — same structure as [Task Assignment](#task-assignment) above (`type` and `task_id` required; here `task_id` is the original task reference). Fields that differ:

- `pr_url` (required) — URL to the PR needing fixes
- `issues` (required) — array of specific issues found
- `fix_instructions` (required) — clear instructions for fixing

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

`completion-report` — same structure as [Task Assignment](#task-assignment) above (`type` and `task_id` required; here `task_id` is the task being reported on). Fields that differ:

- `status` (required) — `"success"`, `"blocked"`, or `"failed"`
- `pr_url` (conditional) — required if status is success
- `test_results` (required) — summary of test execution
- `notes` (optional) — additional context or issues encountered

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

`status-request` — same structure as [Task Assignment](#task-assignment) above (`type` and `task_id` required; here `task_id` is the task to get status for). Fields that differ:

- `last_update` (optional) — last known update timestamp

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

`progress-update` — same structure as [Task Assignment](#task-assignment) above (`type` and `task_id` required; here `task_id` is the task being reported on). Fields that differ:

- `progress_percent` (required) — estimated completion (0-100)
- `current_activity` (required) — what agent is currently doing
- `blockers` (required) — array of blocking issues (empty if none)
- `remaining_steps` (required) — list of remaining work

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

`approval` — same structure as [Task Assignment](#task-assignment) above (`type` and `task_id` required; here `task_id` is the task being approved). Fields that differ:

- `pr_url` (required) — URL of approved PR
- `message` (optional) — additional feedback

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

`rejection` — same structure as [Task Assignment](#task-assignment) above (`type` and `task_id` required; here `task_id` is the task being rejected). Fields that differ:

- `pr_url` (required) — URL of rejected PR
- `reason` (required) — clear explanation of rejection
- `required_fixes` (required) — list of changes needed

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

`escalation` — same structure as [Task Assignment](#task-assignment) above (`type` and `task_id` required; here `task_id` is the related task). Fields that differ:

- `escalation_type` (required) — `"architecture"`, `"security"`, `"dependency"`, or `"unclear-spec"`
- `description` (required) — detailed description of the issue
- `options` (required) — array of possible resolutions
- `recommendation` (optional) — agent's recommended option
- `awaiting_response` (required) — set to `true`

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

`escalation-response` — same structure as [Task Assignment](#task-assignment) above (`type` and `task_id` required; here `task_id` is the related task). Fields that differ:

- `decision` (required) — chosen option (matches option letter)
- `additional_instructions` (optional) — extra guidance for implementation

---

## Related Sections

- [Part 1: API and Schema](messaging-protocol-part1-api-schema.md) - Message envelope format
- [Part 2: Send and Receive](messaging-protocol-part2-send-receive.md) - How to send these messages
- [Part 5: Response Expectations](messaging-protocol-part5-notifications-responses.md) - What response each type expects
