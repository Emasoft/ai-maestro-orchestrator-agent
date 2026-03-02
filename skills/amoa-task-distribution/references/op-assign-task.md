# Operation: Assign Task to Agent


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Preconditions](#preconditions)
- [Input](#input)
- [Procedure](#procedure)
- [Commands](#commands)
  - [Step 1-3: Update Labels](#step-1-3-update-labels)
  - [Step 4: Send AI Maestro Message](#step-4-send-ai-maestro-message)
- [AI Maestro Message Format](#ai-maestro-message-format)
- [Output](#output)
- [Post-Assignment](#post-assignment)
- [Error Handling](#error-handling)
- [Checklist](#checklist)
- [Related Operations](#related-operations)

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-assign-task |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | Task Distribution |
| **Agent** | eoa-main |

## Purpose

Assign a ready task to a selected agent by updating GitHub labels and sending an AI Maestro message.

## Preconditions

- Task is ready (dependencies resolved)
- Agent has been selected (see op-select-agent)
- Agent is available and has capacity

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `issue_number` | int | Yes | The task issue number |
| `agent_name` | string | Yes | The selected agent's name |
| `repo` | string | Yes | Repository in `owner/repo` format |

## Procedure

1. Remove any existing `assign:*` label from the issue
2. Add new `assign:<agent-name>` label to the issue
3. Update status from `status:ready` to `status:in-progress`
4. Send task assignment message via AI Maestro using the `agent-messaging` skill
5. Wait for agent ACK
6. Log assignment in delegation log

## Commands

### Step 1-3: Update Labels

```bash
ISSUE=42
AGENT="implementer-1"

# Remove existing assign:* label first
gh issue view $ISSUE --json labels | jq -r '.labels[].name' | grep '^assign:' | while read label; do
  gh issue edit $ISSUE --remove-label "$label"
done

# Add new assignment
gh issue edit $ISSUE --add-label "assign:$AGENT"

# Update status
gh issue edit $ISSUE --remove-label "status:ready" --add-label "status:in-progress"
```

### Step 4: Send AI Maestro Message

```bash
# Send task assignment using the agent-messaging skill:
# - Recipient: $AGENT
# - Subject: "Task Assignment: Issue #$ISSUE"
# - Content: "You are assigned issue #$ISSUE. Success criteria: [criteria]. Report when complete."
# - Type: request, Priority: high
# - Data: task_id, issue_number, handoff_doc
# Verify: confirm message delivery
# {
#   "data": {
#     "task_id": "$ISSUE",
#     "issue_number": $ISSUE,
#     "handoff_doc": "docs_dev/handoffs/task-$ISSUE.md"
#   }
    }
  }"
```

## AI Maestro Message Format

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "orchestrator",
  "to": "<agent-name>",
  "subject": "Task Assignment: <task-title>",
  "priority": "high",
  "content": {
    "type": "request",
    "message": "You are assigned: <task-description>. Success criteria: <criteria>. Report status when starting and when complete.",
    "data": {
      "task_id": "<task-id>",
      "issue_number": "<github-issue-number>",
      "handoff_doc": "docs_dev/handoffs/<handoff-filename>.md"
    }
  }
}
```

## Output

```json
{
  "assigned": true,
  "issue_number": 42,
  "agent": "implementer-1",
  "previous_status": "status:ready",
  "new_status": "status:in-progress",
  "message_sent": true,
  "ack_received": false
}
```

## Post-Assignment

After sending assignment, wait for agent acknowledgment. See eoa-progress-monitoring for response handling.

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Label conflict | Multiple assign:* labels | Remove all, reapply correct one |
| Agent does not ACK | Agent unresponsive | Send reminder, then escalate |
| Message send failed | AI Maestro unavailable | Retry with exponential backoff |

## Checklist

- [ ] Remove existing `assign:*` label from the issue
- [ ] Add `assign:<agent-name>` label to the issue
- [ ] Update status from `status:ready` to `status:in-progress`
- [ ] Send task assignment message via AI Maestro using the `agent-messaging` skill
- [ ] Wait for agent ACK
- [ ] Log assignment in delegation log file

## Related Operations

- [op-select-agent.md](op-select-agent.md) - Previous step
- [op-reassign-task.md](op-reassign-task.md) - If reassignment needed
