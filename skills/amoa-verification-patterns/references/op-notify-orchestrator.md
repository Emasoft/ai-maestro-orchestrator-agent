# Operation: Notify Orchestrator


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Steps](#steps)
  - [Step 1: Prepare Notification Content](#step-1-prepare-notification-content)
  - [Step 2: Send via AI Maestro](#step-2-send-via-ai-maestro)
  - [Step 3: Wait for Acknowledgment](#step-3-wait-for-acknowledgment)
- [Notification Content](#notification-content)
- [Minimal Summary Format](#minimal-summary-format)
- [Progress Updates](#progress-updates)
- [Additional Attempts Request](#additional-attempts-request)
- [Troubleshooting](#troubleshooting)
  - [Notification Not Delivered](#notification-not-delivered)
  - [Notification Format](#notification-format)
- [Exit Criteria](#exit-criteria)
- [Related Operations](#related-operations)

---
procedure: proc-complete-task
workflow-instruction: Step 19 - Task Completion
operation-id: op-notify-orchestrator
---

## Purpose

Send verification results and test reports to orchestrator via AI Maestro messaging.

## When to Use

- After completing test execution
- When tests finish in CI/CD
- To alert orchestrator of verification failures
- To trigger next workflow step after successful verification

## Prerequisites

- AI Maestro server is running
- Verification results are ready
- Agent session name is known
- Network connectivity to AI Maestro

## Steps

### Step 1: Prepare Notification Content

Assemble the notification with test results:

```json
{
  "type": "verification-complete",
  "task_id": "GH-42",
  "status": "passed",
  "summary": {
    "total": 45,
    "passed": 42,
    "failed": 2,
    "skipped": 1
  },
  "report_path": "artifacts/tests/pytest-report.json"
}
```

### Step 2: Send via AI Maestro

Using testing protocol with notification:

```bash
python shared/testing_protocol.py \
  --pytest tests/ \
  --notify \
  --branch feature-xyz \
  --output test-results.json
```

Or send directly using the `agent-messaging` skill:
- **Recipient**: `orchestrator-master`
- **Subject**: "Verification Complete: GH-42"
- **Content**: "[TESTS] 45 total: 42 passed, 2 failed, 1 skipped (12.5s)"
- **Type**: `verification-complete`, **Priority**: `high`
- **Data**: include `task_id`, `status`

**Verify**: confirm message delivery.

### Step 3: Wait for Acknowledgment

Orchestrator responds with next action:

**On Pass:**
```json
{
  "type": "test-report-ack",
  "task_id": "GH-42",
  "status": "approved",
  "message": "All tests passed. Proceed to PR creation.",
  "next_action": "create-pr"
}
```

**On Fail:**
```json
{
  "type": "test-report-ack",
  "task_id": "GH-42",
  "status": "rejected",
  "message": "Fix 2 failing tests before proceeding",
  "required_actions": [
    "Fix test_auth.py:45 - assertion failed",
    "Fix test_api.py:89 - timeout exceeded"
  ],
  "next_action": "fix-and-rerun"
}
```

## Notification Content

Notification must include:

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | `verification-complete` |
| `task_id` | Yes | Task being verified |
| `status` | Yes | `passed`, `failed`, `error` |
| `summary` | Yes | Test counts (total, passed, failed, skipped) |
| `report_path` | No | Path to full report |
| `branch` | No | Git branch name |
| `timestamp` | No | When verification completed |
| `error_details` | Conditional | Required if status is failed/error |

## Minimal Summary Format

For orchestrator consumption:

```
[TESTS] 45 total: 42 passed, 2 failed, 1 skipped (12.5s)
FAILED: test_auth.py:45, test_api.py:89
COVERAGE: 85% lines, 72% branches
```

## Progress Updates

For long-running test suites, send progress updates:

Send a progress update using the `agent-messaging` skill:
- **Recipient**: `orchestrator-master`
- **Subject**: "Test Progress: GH-42"
- **Content**: "5000/10000 tests complete, 2 failures so far"
- **Type**: `progress-update`, **Priority**: `normal`
- **Data**: include `task_id`, `phase: running-tests`, `progress_percent: 50`

**Verify**: confirm message delivery.

## Additional Attempts Request

If more time is needed:

Send an extension request using the `agent-messaging` skill:
- **Recipient**: `orchestrator-master`
- **Subject**: "Extension Request: GH-42"
- **Content**: "Integration tests running (10k+ tests), 80% complete"
- **Type**: `additional-attempts-request`, **Priority**: `high`
- **Data**: include `task_id`, `requested_additional_attempts: 3`, `reason`, `current_progress`

**Verify**: confirm message delivery.

## Troubleshooting

### Notification Not Delivered

1. Use the `agent-messaging` skill to perform a health check on the AI Maestro service.

2. Check agent session name is correct

3. Verify network connectivity

4. Check message format matches schema

5. Review AI Maestro logs for errors

### Notification Format

| Issue | Cause | Solution |
|-------|-------|----------|
| Message rejected | Invalid JSON | Validate JSON format |
| Agent not found | Wrong session name | Use full session name (domain-subdomain-name) |
| Timeout | Network issue | Check connectivity, retry |

## Exit Criteria

This operation is complete when:
- [ ] Notification content prepared with all required fields
- [ ] Message sent to orchestrator via AI Maestro
- [ ] Acknowledgment received (or timeout handled)
- [ ] Next action determined from response
- [ ] Follow-up action initiated (if needed)

## Related Operations

- [op-run-test-suite.md](./op-run-test-suite.md) - Running tests that produce results
- [op-format-verification-report.md](./op-format-verification-report.md) - Creating report to send
- [op-generate-test-report.md](./op-generate-test-report.md) - Standard test report format
- [op-update-github-issue.md](./op-update-github-issue.md) - Updating GitHub with results
