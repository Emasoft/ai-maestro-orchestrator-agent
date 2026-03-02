---
procedure: proc-execute-task
workflow-instruction: Step 17 - Task Execution
operation: send-first-reminder
---

# Operation: Send First Reminder


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Steps](#steps)
  - [Step 1: Prepare Reminder Message](#step-1-prepare-reminder-message)
  - [Step 2: Send Status Request (No ACK State)](#step-2-send-status-request-no-ack-state)
  - [Step 3: Send Progress Request (No Progress State)](#step-3-send-progress-request-no-progress-state)
  - [Step 4: Log Reminder](#step-4-log-reminder)
  - [Step 5: Set Follow-up Timer](#step-5-set-follow-up-timer)
- [Message Template: No ACK](#message-template-no-ack)
- [Message Template: No Progress](#message-template-no-progress)
- [Success Criteria](#success-criteria)
- [Next Steps](#next-steps)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Send a normal priority reminder to an agent who has not acknowledged a task or has not provided progress updates.

## When to Use

- Agent state is "No ACK" (no acknowledgment received)
- Agent state is "No Progress" (acknowledged but no updates)
- First step in escalation sequence

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| task_id | Issue number | Yes |
| agent_name | Assigned agent | Yes |
| state | Current agent state | Yes |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| message_sent | Boolean | Confirmation of delivery |
| reminder_timestamp | ISO8601 | When reminder was sent |
| escalation_level | Integer | 1 (first reminder) |

## Steps

### Step 1: Prepare Reminder Message

```bash
TASK_ID=$1
AGENT_NAME=$2
CURRENT_STATE=$3

# Get task title for context
TASK_TITLE=$(gh issue view $TASK_ID --json title | jq -r '.title')
```

### Step 2: Send Status Request (No ACK State)

If agent has not acknowledged the task:

Send a reminder using the `agent-messaging` skill:
- **Recipient**: the agent session name (`$AGENT_NAME`)
- **Subject**: "Reminder: ACK Required for #<TASK_ID>"
- **Content**: "Task #<TASK_ID> (<TASK_TITLE>) was assigned to you but no acknowledgment has been received. Please send an ACK message confirming: 1. You received the task 2. Your understanding of the requirements 3. Any questions you have"
- **Type**: `reminder`, **Priority**: `normal`
- **Data**: include `task_id`, `reminder_type: ack_required`, `escalation_level: 1`

**Verify**: confirm message delivery.

### Step 3: Send Progress Request (No Progress State)

If agent acknowledged but has not provided updates:

Send a status request using the `agent-messaging` skill:
- **Recipient**: the agent session name (`$AGENT_NAME`)
- **Subject**: "Status Request: #<TASK_ID>"
- **Content**: "What is your current status on task #<TASK_ID> (<TASK_TITLE>)? Please report: 1. Current progress 2. Any blockers 3. Anything unclear 4. Any difficulties 5. Estimated time to completion"
- **Type**: `status-request`, **Priority**: `normal`
- **Data**: include `task_id`, `reminder_type: progress_required`, `escalation_level: 1`

**Verify**: confirm message delivery.

### Step 4: Log Reminder

```bash
# Record reminder for escalation tracking
REMINDER_TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

echo "$REMINDER_TIMESTAMP|$TASK_ID|$AGENT_NAME|first_reminder|$CURRENT_STATE" >> reminder_log.txt

# Update issue with reminder note
gh issue comment $TASK_ID --body "Reminder sent to $AGENT_NAME at $REMINDER_TIMESTAMP (escalation level 1)"
```

### Step 5: Set Follow-up Timer

```bash
# Note: Actual timer implementation depends on orchestrator's scheduling mechanism
# This records when follow-up should occur

FOLLOWUP_TIME=$(date -u -v+15M +%Y-%m-%dT%H:%M:%SZ)
echo "Follow-up scheduled for: $FOLLOWUP_TIME"

# Store follow-up expectation
echo '{"task_id": "'"$TASK_ID"'", "agent": "'"$AGENT_NAME"'", "reminder_sent": "'"$REMINDER_TIMESTAMP"'", "followup_by": "'"$FOLLOWUP_TIME"'", "escalation_level": 1}' >> pending_followups.json
```

## Message Template: No ACK

```
Subject: Reminder: ACK Required for #[task_id]
Priority: normal

Task #[task_id] ([task_title]) was assigned to you but no acknowledgment has been received.

Please send an ACK message confirming:
1. You received the task
2. Your understanding of the requirements
3. Any questions you have

ACK Format:
[ACK] Task #[task_id] - <your understanding>
Questions: <list or "none">
```

## Message Template: No Progress

```
Subject: Status Request: #[task_id]
Priority: normal

What is your current status on task #[task_id] ([task_title])?

Please report:
1. Current progress (percentage or milestone)
2. Any blockers or issues encountered
3. Anything unclear in the requirements
4. Any difficulties you are facing
5. Estimated time to completion
```

## Success Criteria

- [ ] Correct message type sent based on state
- [ ] Message delivered successfully
- [ ] Reminder logged for tracking
- [ ] Follow-up time recorded
- [ ] Issue comment added

## Next Steps

After sending first reminder:
1. Wait 15 minutes for response
2. If response received: Update agent state, process response
3. If no response: Proceed to op-send-urgent-reminder

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Message delivery failed | AI Maestro unavailable | Retry after 5 minutes |
| Wrong agent state | State detection error | Re-run op-detect-agent-state |
| Duplicate reminder | Reminder already sent | Check reminder_log.txt first |

## Related Operations

- op-detect-agent-state
- op-send-urgent-reminder
- op-handle-reassignment
