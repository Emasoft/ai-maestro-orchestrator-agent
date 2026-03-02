---
procedure: proc-execute-task
workflow-instruction: Step 17 - Task Execution
operation: send-urgent-reminder
---

# Operation: Send Urgent Reminder


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Steps](#steps)
  - [Step 1: Verify First Reminder Was Sent](#step-1-verify-first-reminder-was-sent)
  - [Step 2: Verify No Response Received](#step-2-verify-no-response-received)
  - [Step 3: Send Urgent Escalation](#step-3-send-urgent-escalation)
  - [Step 4: Log Escalation](#step-4-log-escalation)
  - [Step 5: Set Reassignment Timer](#step-5-set-reassignment-timer)
- [Message Template](#message-template)
- [Escalation Timeline](#escalation-timeline)
- [Success Criteria](#success-criteria)
- [Next Steps](#next-steps)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Send a high-priority escalation message to an agent who did not respond to the first reminder.

## When to Use

- Agent state is "Unresponsive" (no response to first reminder)
- 15+ minutes elapsed since first reminder with no response
- Second step in escalation sequence (before reassignment)

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| task_id | Issue number | Yes |
| agent_name | Assigned agent | Yes |
| first_reminder_time | From reminder_log.txt | Yes |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| message_sent | Boolean | Confirmation of delivery |
| escalation_timestamp | ISO8601 | When escalation was sent |
| escalation_level | Integer | 2 (urgent reminder) |

## Steps

### Step 1: Verify First Reminder Was Sent

```bash
TASK_ID=$1
AGENT_NAME=$2

# Check reminder log for first reminder
FIRST_REMINDER=$(grep "$TASK_ID|$AGENT_NAME|first_reminder" reminder_log.txt | tail -1)

if [ -z "$FIRST_REMINDER" ]; then
  echo "ERROR: No first reminder found. Run op-send-first-reminder first."
  exit 1
fi

FIRST_REMINDER_TIME=$(echo "$FIRST_REMINDER" | cut -d'|' -f1)
echo "First reminder was sent at: $FIRST_REMINDER_TIME"
```

### Step 2: Verify No Response Received

```bash
# Check if agent responded after first reminder
FIRST_REMINDER_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${FIRST_REMINDER_TIME%.*}" +%s)

# Use the agent-messaging skill to check inbox for messages from the agent
# received after the first reminder timestamp. Filter by sender matching
# $AGENT_NAME and timestamp after $FIRST_REMINDER_EPOCH.
RESPONSE_AFTER_REMINDER=$(# check if agent responded after first reminder)

if [ "$RESPONSE_AFTER_REMINDER" = "found" ]; then
  echo "Agent responded after first reminder. No urgent escalation needed."
  exit 0
fi
```

### Step 3: Send Urgent Escalation

```bash
TASK_TITLE=$(gh issue view $TASK_ID --json title | jq -r '.title')

TASK_TITLE=$(gh issue view $TASK_ID --json title | jq -r '.title')

# Send urgent escalation using the agent-messaging skill:
# - Recipient: $AGENT_NAME
# - Subject: "URGENT: #$TASK_ID - Response Required Immediately"
# - Content: "URGENT ESCALATION: No response received for task #$TASK_ID ($TASK_TITLE). A first reminder was sent at $FIRST_REMINDER_TIME with no response. Please respond immediately with your current status. If no response within 30 minutes, this task may be reassigned."
# - Type: escalation, Priority: urgent
# - Data: task_id, escalation_level: 2, first_reminder_time, reassignment_warning: true
# Verify: confirm message delivery
```

### Step 4: Log Escalation

```bash
ESCALATION_TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

echo "$ESCALATION_TIMESTAMP|$TASK_ID|$AGENT_NAME|urgent_reminder|unresponsive" >> reminder_log.txt

# Update issue with escalation note
gh issue comment $TASK_ID --body "**URGENT ESCALATION** sent to $AGENT_NAME at $ESCALATION_TIMESTAMP (escalation level 2). Reassignment may occur if no response within 30 minutes."
```

### Step 5: Set Reassignment Timer

```bash
# Record reassignment deadline
REASSIGNMENT_DEADLINE=$(date -u -v+30M +%Y-%m-%dT%H:%M:%SZ)

echo '{"task_id": "'"$TASK_ID"'", "agent": "'"$AGENT_NAME"'", "escalation_sent": "'"$ESCALATION_TIMESTAMP"'", "reassignment_deadline": "'"$REASSIGNMENT_DEADLINE"'", "escalation_level": 2}' >> pending_reassignments.json

echo "Reassignment deadline: $REASSIGNMENT_DEADLINE"
```

## Message Template

```
Subject: URGENT: #[task_id] - Response Required Immediately
Priority: urgent

**URGENT ESCALATION**

No response received for task #[task_id] ([task_title]).

A first reminder was sent at [first_reminder_time] with no response.

**Action Required:**
Please respond immediately with your current status. If no response is received within the next 30 minutes, this task may be reassigned.

If you are blocked, experiencing issues, or unable to continue, please report that as well.

**Respond with:**
- Current progress
- Any blockers
- Why there was no earlier response
- Estimated completion time
```

## Escalation Timeline

| Step | Time from Assignment | Action |
|------|---------------------|--------|
| 1 | +15 min (no ACK) | First reminder (normal priority) |
| 2 | +30 min (no response) | Urgent reminder (urgent priority) |
| 3 | +60 min (still no response) | Notify user, consider reassignment |

## Success Criteria

- [ ] First reminder verified as sent
- [ ] No response verified since first reminder
- [ ] Urgent message sent with priority=urgent
- [ ] Escalation logged
- [ ] Reassignment deadline recorded
- [ ] Issue commented with escalation status

## Next Steps

After sending urgent reminder:
1. Wait 30 minutes for response
2. If response received: Update agent state, process response, clear reassignment timer
3. If no response: Proceed to op-handle-reassignment

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| First reminder not found | Skipped escalation step | Send first reminder first |
| Agent responded | Response not detected | Re-check message history |
| Message delivery failed | AI Maestro unavailable | Retry immediately (urgent) |

## Related Operations

- op-send-first-reminder
- op-handle-reassignment
- op-detect-agent-state
