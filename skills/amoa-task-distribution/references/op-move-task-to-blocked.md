# Operation: Move Task to Blocked Column


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Preconditions](#preconditions)
- [Blocker Verification (BEFORE Moving)](#blocker-verification-before-moving)
- [Input](#input)
- [Procedure](#procedure)
- [Commands](#commands)
- [Escalation Message to EAMA](#escalation-message-to-eama)
- [Checklist](#checklist)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-move-task-to-blocked |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | Task Distribution |
| **Agent** | eoa-main |

## Purpose

Move a task to the Blocked column when an agent reports the task cannot proceed, and escalate to EAMA immediately.

## Preconditions

- Agent has reported a blocker
- Blocker has been verified as REAL (see verification table)
- Task is currently in an active status (not already blocked)

## Blocker Verification (BEFORE Moving)

| Check | Question | Action if False |
|-------|----------|-----------------|
| Cannot self-resolve | Can the agent solve this themselves? | Guide agent to solution, do not block |
| Not a knowledge gap | Is this a "how to" question? | Direct to documentation/skills |
| Not a process issue | Is this a team process? | Explain process |
| Truly blocking | Can work continue on other parts? | Suggest parallel work |

**Only move to Blocked if ALL checks pass (true blocker requiring user/architect intervention).**

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `issue_number` | int | Yes | The blocked task issue number |
| `blocker_reason` | string | Yes | Description of what is blocking |
| `blocker_category` | string | Yes | Category (access-credentials, dependency, etc.) |
| `current_status` | string | Yes | Current status BEFORE blocking |
| `repo` | string | Yes | Repository in `owner/repo` format |

## Procedure

1. Acknowledge the blocker via AI Maestro to the reporting agent
2. Record the task's current column/status BEFORE moving
3. Move the task to the Blocked column on the Kanban board
4. Update labels: remove current `status:*`, add `status:blocked`
5. Add blocker details as comment on the issue (include previous status)
6. Create a separate GitHub issue for the blocker itself (`type:blocker` label)
7. Send blocker-escalation message to EAMA using the `agent-messaging` skill IMMEDIATELY
8. Check if other unblocked tasks can be assigned to the waiting agent

## Commands

```bash
ISSUE=42
CURRENT_STATUS="status:ai-review"
BLOCKER_REASON="Missing AWS credentials"
AGENT="implementer-1"

# Step 1: Acknowledge blocker using the agent-messaging skill:
# - Recipient: $AGENT
# - Subject: "Blocker Acknowledged"
# - Content: "Blocker received for #$ISSUE"
# - Type: ack

# Step 4: Update labels
gh issue edit $ISSUE --remove-label "$CURRENT_STATUS" --add-label "status:blocked"

# Step 5: Add comment with previous status
gh issue comment $ISSUE --body "## Blocked
**Reason:** $BLOCKER_REASON
**Previous status:** $CURRENT_STATUS
**Assigned agent:** $AGENT"

# Step 6: Create blocker issue
gh issue create --title "BLOCKER: $BLOCKER_REASON" --label "type:blocker" \
  --body "Blocking task #$ISSUE. Category: Access/Credentials. What's needed: AWS credentials provisioned."
```

## Escalation Message to EAMA

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "eoa-orchestrator",
  "to": "eama-assistant-manager",
  "subject": "BLOCKER: Task #42 - Missing API Credentials",
  "priority": "high",
  "content": {
    "type": "blocker-escalation",
    "message": "Task #42 is blocked. Agent impl-01 reports: Cannot deploy to staging - missing AWS credentials. Blocker tracked in issue #99.",
    "data": {
      "task_id": "42",
      "blocker_issue_number": "99",
      "assigned_agent": "impl-01",
      "blocker_category": "access-credentials",
      "previous_status": "status:ai-review",
      "impact": "Cannot complete deployment testing"
    }
  }
}
```

**CRITICAL:** Do NOT wait or "monitor for 24h first". Escalate IMMEDIATELY - user may have solution ready.

## Checklist

- [ ] Verify the blocker is real (verification table)
- [ ] Acknowledge the blocker via AI Maestro to the reporting agent
- [ ] Record the task's current column/status BEFORE moving to Blocked
- [ ] Move the task to the Blocked column on the Kanban board
- [ ] Remove current `status:*` label, add `status:blocked`
- [ ] Add blocker details as comment on the blocked task issue (include `Previous status: $CURRENT_STATUS`)
- [ ] Create a separate GitHub issue for the blocker (`type:blocker` label, referencing the blocked task)
- [ ] Send blocker-escalation message to EAMA via AI Maestro using the `agent-messaging` skill (include `blocker_issue_number`)
- [ ] Check if other unblocked tasks can be assigned to the waiting agent

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Cannot create blocker issue | Permission denied | Check write access to repo |
| EAMA unreachable | AI Maestro down | Log and retry, notify user directly |

## Related Operations

- [op-restore-task-from-blocked.md](op-restore-task-from-blocked.md) - When blocker resolved
- [op-assign-task.md](op-assign-task.md) - Assign other tasks to waiting agent
