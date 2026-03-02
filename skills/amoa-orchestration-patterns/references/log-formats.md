# Log Formats Reference

This document specifies all log entry formats, progress report structures, and status update templates used by the Emasoft Orchestrator Agent (EOA).

## Table of Contents

1. [Task Log Format](#task-log-format)
2. [Delegation Log Format](#delegation-log-format)
3. [Status File Format](#status-file-format)
4. [Progress Update Format](#progress-update-format)
5. [Archive Structure](#archive-structure)
6. [Output Report Format](#output-report-format)
7. [AI Maestro Message Formats](#ai-maestro-message-formats)

---

## Task Log Format

**Location:** `docs_dev/orchestration/task-log.md`

**Purpose:** Central log of all tasks received, delegated, and completed

**Update Frequency:** After every task status change

**Format:**

```markdown
# Task Log - [Project Name]

## Active Tasks

| UUID | Task Name | Type | Received | Deadline | Status | Assigned To |
|------|-----------|------|----------|----------|--------|-------------|
| uuid-1 | Implement feature X | implementation | 2026-02-04 10:00 | 2026-02-05 18:00 | DELEGATED | implementer-1 |

## Completed Tasks

| UUID | Task Name | Type | Received | Completed | Duration | Assigned To |
|------|-----------|------|----------|-----------|----------|-------------|
| uuid-0 | Fix bug Y | fix | 2026-02-03 14:00 | 2026-02-03 16:30 | 2.5h | debugger-1 |

## Archived Tasks

[Older completed tasks moved here after 30 days]
```

**Field Definitions:**

| Field | Description | Valid Values |
|-------|-------------|--------------|
| `UUID` | Unique task identifier | UUID format string |
| `Task Name` | Brief task description | Free text (50 chars max) |
| `Type` | Task category | `implementation`, `review`, `fix`, `research` |
| `Received` | Timestamp task received | ISO8601 format (YYYY-MM-DD HH:MM) |
| `Deadline` | Expected completion time | ISO8601 format (YYYY-MM-DD HH:MM) |
| `Completed` | Actual completion time | ISO8601 format (YYYY-MM-DD HH:MM) |
| `Status` | Current task state | `RECEIVED`, `DELEGATED`, `IN_PROGRESS`, `COMPLETE`, `REPORTED` |
| `Assigned To` | Agent handling task | Agent name from team registry |
| `Duration` | Time to complete | Human-readable format (e.g., "2.5h", "45m") |

---

## Delegation Log Format

**Location:** `docs_dev/orchestration/delegation-log.md`

**Purpose:** Track all delegations, retries, reassignments

**Update Frequency:** After every delegation event (assign, retry, reassign, complete, fail)

**Format:**

```markdown
# Delegation Log - [Project Name]

## Current Delegations

| Task UUID | Agent | Delegated At | Expected Completion | Attempt | Status |
|-----------|-------|--------------|---------------------|---------|--------|
| uuid-1 | implementer-1 | 2026-02-04 10:15 | 2026-02-04 16:00 | 1 | IN_PROGRESS |

## Completed Delegations

| Task UUID | Agent | Delegated At | Completed At | Duration | Outcome |
|-----------|-------|--------------|--------------|----------|---------|
| uuid-0 | debugger-1 | 2026-02-03 14:10 | 2026-02-03 16:30 | 2h 20m | SUCCESS |

## Failed Delegations

| Task UUID | Agent | Delegated At | Failed At | Attempt | Failure Reason | Action Taken |
|-----------|-------|--------------|-----------|---------|----------------|--------------|
| uuid-2 | tester-1 | 2026-02-02 09:00 | 2026-02-02 11:00 | 1 | CI env issue | Reassigned to tester-2 |
```

**Field Definitions:**

| Field | Description | Valid Values |
|-------|-------------|--------------|
| `Task UUID` | Reference to task in task-log | UUID format string |
| `Agent` | Agent name receiving delegation | Agent name from team registry |
| `Delegated At` | Timestamp delegation sent | ISO8601 format (YYYY-MM-DD HH:MM) |
| `Expected Completion` | When agent should complete | ISO8601 format (YYYY-MM-DD HH:MM) |
| `Completed At` | Actual completion timestamp | ISO8601 format (YYYY-MM-DD HH:MM) |
| `Failed At` | When failure occurred | ISO8601 format (YYYY-MM-DD HH:MM) |
| `Attempt` | Retry count | Integer (1, 2, 3...) |
| `Status` | Current delegation state | `IN_PROGRESS`, `COMPLETE`, `FAILED` |
| `Outcome` | Final result | `SUCCESS`, `FAILED`, `REASSIGNED` |
| `Duration` | Time from delegate to complete | Human-readable format (e.g., "2h 20m") |
| `Failure Reason` | Why delegation failed | Free text (100 chars max) |
| `Action Taken` | Response to failure | Free text (100 chars max) |

---

## Status File Format

**Location:** `docs_dev/orchestration/status/[task-uuid].md`

**Purpose:** Detailed tracking of individual task progress

**Update Frequency:** After every progress update or status change

**Format:**

```markdown
# Task Status: [Task Name]

**UUID:** [task-uuid]
**Type:** [implementation|review|fix|research]
**Priority:** [normal|high|urgent]

## Timeline

- **Received:** 2026-02-04 10:00
- **Delegated:** 2026-02-04 10:15 to implementer-1
- **Expected Completion:** 2026-02-04 16:00
- **Actual Completion:** [timestamp when done]

## Current Status

**Status:** DELEGATED
**Progress:** 60%
**Last Update:** 2026-02-04 12:30

## Progress Updates

### 2026-02-04 12:30 - Status update from implementer-1
- Tests written and passing
- Implementation 60% complete
- No blockers
- Expected completion: 2026-02-04 15:00

### 2026-02-04 10:15 - Delegated to implementer-1
- Task assigned
- GitHub issue created: [issue-url]
- ACK received

## Acceptance Criteria

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Code reviewed
- [ ] No lint errors

## Artifacts

- [Link to completion report when done]
- [Link to test results when done]
- [Link to GitHub PR when done]

## Notes

[Any additional context or decisions made]
```

**Section Definitions:**

| Section | Required | Description |
|---------|----------|-------------|
| **Metadata Block** | Yes | UUID, Type, Priority fields at top |
| **Timeline** | Yes | Key timestamps (Received, Delegated, Expected, Actual) |
| **Current Status** | Yes | Status, Progress %, Last Update timestamp |
| **Progress Updates** | Yes | Chronological log of all updates (newest first) |
| **Acceptance Criteria** | Yes | Checklist of completion requirements |
| **Artifacts** | Yes | Links to deliverables (may be empty until complete) |
| **Notes** | Optional | Additional context, decisions, or observations |

---

## Progress Update Format

**Context:** Progress update entries within status files

**Format:**

```markdown
### [Timestamp] - [Update Source]
- [Bullet point 1]
- [Bullet point 2]
- [Bullet point 3]
- Expected completion: [timestamp]
```

**Example:**

```markdown
### 2026-02-04 12:30 - Status update from implementer-1
- Tests written and passing
- Implementation 60% complete
- No blockers
- Expected completion: 2026-02-04 15:00
```

**Rules:**

1. Timestamp must be ISO8601 format (YYYY-MM-DD HH:MM)
2. Source identifies who provided update (agent name or "Self" for orchestrator)
3. Bullet points describe concrete progress items
4. Last bullet should indicate expected completion (if not yet complete)
5. Updates ordered newest-first (reverse chronological)

---

## Archive Structure

**Location:** `docs_dev/orchestration/archive/[task-uuid]/`

**Purpose:** Long-term storage of completed task records

**Archive Trigger:** 7 days after task completion

**Structure:**

```
archive/
└── [task-uuid]/
    ├── status.md (final status file)
    ├── delegation-history.md (all delegation events)
    ├── messages/ (AI Maestro message transcripts)
    │   ├── assignment.json
    │   ├── progress-updates.json
    │   └── completion.json
    ├── artifacts/ (deliverables from agent)
    │   ├── completion-report.md
    │   ├── test-results.log
    │   └── [other artifacts]
    └── metadata.json (task metadata for indexing)
```

**metadata.json Format:**

```json
{
  "task_uuid": "uuid-string",
  "task_name": "Task name",
  "task_type": "implementation|review|fix|research",
  "priority": "normal|high|urgent",
  "received_at": "ISO8601 timestamp",
  "completed_at": "ISO8601 timestamp",
  "duration_hours": 2.5,
  "assigned_to": "agent-name",
  "outcome": "SUCCESS|FAILED|ESCALATED",
  "acceptance_criteria_met": true,
  "github_issue": "issue-url",
  "artifacts": [
    "artifacts/completion-report.md",
    "artifacts/test-results.log"
  ]
}
```

---

## Output Report Format

**Purpose:** Minimal report format returned to task sender (ECOS/EAMA)

**Format:**

```
[DONE/FAILED] task_name - brief_result
Key finding: [one-line summary]
Details: [filename if written]
```

**Example:**

```
[DONE] implement-auth - Authentication module completed
Key finding: OAuth2 integration tested and passing
Details: docs_dev/orchestration/reports/uuid-123.md
```

**Rules:**

1. First line: `[DONE]` or `[FAILED]` followed by task name and brief result
2. Second line: "Key finding:" followed by one-line summary
3. Third line: "Details:" followed by path to detailed report file
4. **NEVER exceed 3 lines**
5. **NEVER include code blocks**
6. **NEVER include verbose output**

---

## AI Maestro Message Formats

All AI Maestro messages follow JSON format with required fields: `from`, `to`, `subject`, `priority`, `content`.

### Message Priority Levels

| Priority | When to Use |
|----------|-------------|
| `normal` | Regular task assignments, status updates, completion reports |
| `high` | Time-sensitive tasks, overdue notifications |
| `urgent` | Escalations, critical blockers, system failures |

### Message Type: Assignment

**From ECOS or EAMA to EOA:**

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "ecos-main",
  "to": "eoa-[project-name]",
  "subject": "Task Assignment: [Task Name]",
  "priority": "normal|high|urgent",
  "content": {
    "type": "assignment",
    "message": "Task description and requirements",
    "task_uuid": "UUID",
    "deadline": "ISO8601 timestamp",
    "acceptance_criteria": [
      "Criterion 1",
      "Criterion 2"
    ]
  }
}
```

**EOA Response (ACK):**

Send an acknowledgment using the `agent-messaging` skill:
- **Recipient**: `ecos-main`
- **Subject**: "ACK: Task Assignment [Task Name]"
- **Content**: "Task received and logged. UUID: [task-uuid]. Expected completion: [timestamp]."
- **Type**: `acknowledgment`, **Priority**: `normal`
- **Data**: include `task_uuid`, `status: received`

**Verify**: confirm message delivery.

### Message Type: Delegation

**EOA to Sub-Agent:**

Send a task assignment using the `agent-messaging` skill:
- **Recipient**: the sub-agent session name
- **Subject**: "Task Assignment: [Task Name]"
- **Content**: "Detailed task description with all context needed"
- **Type**: `assignment`, **Priority**: `normal`, `high`, or `urgent` as appropriate
- **Data**: include `task_uuid`, `deadline`, `acceptance_criteria`, `deliverables`, `github_issue`

**Verify**: confirm message delivery.

**Sub-Agent Response (ACK):**

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "[sub-agent-name]",
  "to": "eoa-[project-name]",
  "subject": "ACK: Task Assignment [Task Name]",
  "content": {
    "type": "acknowledgment",
    "message": "Task received and understood. Starting work.",
    "task_uuid": "[task-uuid]",
    "expected_completion": "[timestamp]"
  }
}
```

### Message Type: Status Request

**EOA to Sub-Agent:**

Send a status request using the `agent-messaging` skill:
- **Recipient**: the sub-agent session name
- **Subject**: "Status Request: [Task Name]"
- **Content**: "Please provide status update on task [task-uuid]. Expected completion was [timestamp]."
- **Type**: `request`, **Priority**: `normal`
- **Data**: include `task_uuid`

**Verify**: confirm message delivery.

**Sub-Agent Response:**

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "[sub-agent-name]",
  "to": "eoa-[project-name]",
  "subject": "Status Update: [Task Name]",
  "content": {
    "type": "status_update",
    "message": "Current progress summary",
    "task_uuid": "[task-uuid]",
    "progress_percentage": 60,
    "blockers": ["Optional list of blockers"],
    "expected_completion": "[updated-timestamp]"
  }
}
```

### Message Type: Completion Report

**EOA to ECOS:**

Send a completion report using the `agent-messaging` skill:
- **Recipient**: `ecos-main`
- **Subject**: "Task Complete: [Task Name]"
- **Content**: "[1-2 line summary]. Key finding: [one-line summary]. Details: docs_dev/orchestration/reports/[task-uuid].md"
- **Type**: `completion`, **Priority**: `normal`
- **Data**: include `task_uuid`, `completion_timestamp`, `all_criteria_met: true`

**Verify**: confirm message delivery.

### Message Type: Escalation

**EOA to ECOS:**

Send an escalation using the `agent-messaging` skill:
- **Recipient**: `ecos-main`
- **Subject**: "ESCALATION: [Issue Description]"
- **Type**: `escalation`, **Priority**: `urgent`
- **Content and Data**: include relevant escalation details such as `{
      "type": "escalation",
      "message": "Escalation reason and details",
      "task_uuid": "[task-uuid]",
      "failed_agent": "[agent-name]",
      "failure_reason": "Specific reason for escalation",
      "attempts": 3,
      "request": "Agent replacement|Technical guidance|User decision"
    }
  }'
```

---

## Content Type Summary

All AI Maestro message content objects must have a `type` field. Valid types:

| Type | Direction | Purpose |
|------|-----------|---------|
| `assignment` | Sender → Receiver | Assign new task |
| `acknowledgment` | Receiver → Sender | Confirm task received |
| `request` | Any → Any | Request information/status |
| `status_update` | Any → Any | Provide progress update |
| `completion` | Receiver → Sender | Report task complete |
| `escalation` | Receiver → Sender | Escalate blocker/issue |

---

## Log File Locations Summary

| Log Type | Location | Purpose |
|----------|----------|---------|
| Task Log | `docs_dev/orchestration/task-log.md` | Central task registry |
| Delegation Log | `docs_dev/orchestration/delegation-log.md` | All delegation events |
| Status Files | `docs_dev/orchestration/status/[task-uuid].md` | Individual task tracking |
| Archive | `docs_dev/orchestration/archive/[task-uuid]/` | Completed task records |
| Reports | `docs_dev/orchestration/reports/[task-uuid].md` | Detailed completion reports |

---

## Best Practices

1. **Always use ISO8601 timestamps** (YYYY-MM-DD HH:MM format)
2. **Update logs immediately** after status changes
3. **Keep reports minimal** (max 3 lines for orchestrator output)
4. **Archive after 7 days** of completion
5. **Include task UUID** in all log entries for cross-referencing
6. **Use structured formats** (markdown tables, JSON) for machine readability
7. **Preserve all AI Maestro message transcripts** in archive
8. **Never delete active task records** - move to archive instead
