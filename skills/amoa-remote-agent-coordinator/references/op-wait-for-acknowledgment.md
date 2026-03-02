---
procedure: proc-execute-task
workflow-instruction: Step 17 - Task Execution
operation: wait-for-acknowledgment
---

# Operation: Wait for Acknowledgment


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Steps](#steps)
  - [Step 1: Set Timeout](#step-1-set-timeout)
  - [Step 2: Poll for ACK Message](#step-2-poll-for-ack-message)
  - [Step 3: Parse ACK Content](#step-3-parse-ack-content)
  - [Step 4: Handle Timeout](#step-4-handle-timeout)
- [ACK Format Expected](#ack-format-expected)
- [Success Criteria](#success-criteria)
- [Error Handling](#error-handling)
- [Escalation](#escalation)
- [Related Operations](#related-operations)

## Purpose

Wait for agent to acknowledge receipt of task assignment with a 5-minute timeout.

## When to Use

- Immediately after sending task delegation
- After reassigning a task to a new agent
- After sending urgent task updates

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| task_id | Issue number | Yes |
| agent_name | Assigned agent | Yes |
| sent_timestamp | op-send-task-delegation output | Yes |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| ack_received | Boolean | True if ACK received |
| ack_message | String | Agent's understanding statement |
| questions | Array | Questions raised by agent |
| timeout_reached | Boolean | True if 5 min elapsed |

## Steps

### Step 1: Set Timeout

```bash
TIMEOUT_SECONDS=300  # 5 minutes
START_TIME=$(date +%s)
```

### Step 2: Poll for ACK Message

```bash
while true; do
  CURRENT_TIME=$(date +%s)
  ELAPSED=$((CURRENT_TIME - START_TIME))

  if [ $ELAPSED -gt $TIMEOUT_SECONDS ]; then
    echo "TIMEOUT: No ACK received within 5 minutes"
    break
  fi

  # Check for ACK message using the agent-messaging skill
  # Query inbox for messages from the target agent containing "[ACK]" in the subject
  # Use the agent-messaging skill to retrieve and filter messages

  if [ -n "$ACK_MESSAGE" ]; then
    echo "ACK received from $AGENT_NAME"
    break
  fi

  sleep 30  # Poll every 30 seconds
done
```

### Step 3: Parse ACK Content

If ACK received:

```bash
# Extract understanding statement
UNDERSTANDING=$(echo "$ACK_MESSAGE" | grep -A1 "Task #$TASK_ID" | head -1)

# Extract questions
QUESTIONS=$(echo "$ACK_MESSAGE" | grep -A5 "Questions:" | tail -n +2)
```

### Step 4: Handle Timeout

If timeout reached without ACK:

Send a reminder message using the `agent-messaging` skill:
- **Recipient**: the agent session name
- **Subject**: "Reminder: ACK Required for #[TASK_ID]"
- **Content**: "Please acknowledge receipt of task #[TASK_ID] immediately. No ACK received within 5 minutes."
- **Type**: `reminder`
- **Priority**: `high`
- **Data**: include `task_id`, `original_assignment_time`

**Verify**: confirm message delivery.

```bash
# NOTE: The reminder is sent using the agent-messaging skill as described above

# Log timeout for escalation tracking
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) | NO_ACK | #$TASK_ID | $AGENT_NAME | Reminder sent" >> assignment_log.txt
```

## ACK Format Expected

The agent should respond with:

```
[ACK] Task #<id> - <one-line summary of understanding>
Questions: <list or "none">
```

Example:

```
[ACK] Task #42 - Implement user authentication with JWT tokens
Questions:
- Should refresh tokens be stored in database or memory?
- What is the expected token expiry time?
```

## Success Criteria

- [ ] ACK received within 5 minutes
- [ ] ACK contains task ID
- [ ] ACK includes understanding statement
- [ ] Questions (if any) are recorded

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Timeout | Agent offline/busy | Send reminder, escalate if persistent |
| ACK unclear | Agent misunderstood | Reply with clarification |
| Wrong task ID in ACK | Agent confused | Resend task with emphasis on ID |

## Escalation

If no ACK after reminder:
1. Wait additional 5 minutes
2. Send urgent reminder (priority: urgent)
3. If still no response, consider reassignment via op-handle-reassignment

## Related Operations

- op-send-task-delegation
- op-poll-agent-progress
- op-handle-reassignment (in progress-monitoring skill)
