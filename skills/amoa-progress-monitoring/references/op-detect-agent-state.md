---
procedure: proc-execute-task
workflow-instruction: Step 17 - Task Execution
operation: detect-agent-state
---

# Operation: Detect Agent State


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Agent States](#agent-states)
- [Steps](#steps)
  - [Step 1: Get Task Assignment Time](#step-1-get-task-assignment-time)
  - [Step 2: Get Agent's Last Message](#step-2-get-agents-last-message)
  - [Step 3: Check for ACK](#step-3-check-for-ack)
  - [Step 4: Check for Blocker Report](#step-4-check-for-blocker-report)
  - [Step 5: Check for Completion Report](#step-5-check-for-completion-report)
  - [Step 6: Calculate State Duration](#step-6-calculate-state-duration)
  - [Step 7: Determine State](#step-7-determine-state)
- [State Transition Diagram](#state-transition-diagram)
- [Output Format](#output-format)
- [Success Criteria](#success-criteria)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Determine the current state of an assigned agent based on message history and task activity.

## When to Use

- During progress monitoring cycles
- Before sending reminders or escalations
- When checking on task status
- Before reassignment decisions

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| task_id | Issue number | Yes |
| agent_name | Assigned agent | Yes |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| agent_state | Enum | Current state (see table below) |
| last_activity | ISO8601 | Timestamp of last agent message |
| state_duration | Integer | Minutes in current state |

## Agent States

| State | Definition | Typical Next Action |
|-------|------------|---------------------|
| **Acknowledged** | Agent sent ACK for assigned task | Normal monitoring |
| **No ACK** | Task assigned but no acknowledgment received | Send reminder |
| **Active** | Agent sending progress updates | Continue monitoring |
| **No Progress** | Agent acknowledged but no updates since | Send status request |
| **Stale** | Agent's last update predates significant events | Escalate priority |
| **Unresponsive** | Multiple reminders without any response | Consider reassignment |
| **Blocked** | Agent reported blocker | Address blocker |
| **Complete** | Agent reported task done | Verify and close |

## Steps

### Step 1: Get Task Assignment Time

```bash
TASK_ID=$1
AGENT_NAME=$2

# Get when task was assigned to agent
ASSIGNED_AT=$(gh issue view $TASK_ID --json timelineItems | \
  jq -r '.timelineItems[] | select(.label.name == "assign:'"$AGENT_NAME"'") | .createdAt' | tail -1)

if [ -z "$ASSIGNED_AT" ]; then
  echo "ERROR: No assignment found for agent $AGENT_NAME on task #$TASK_ID"
  exit 1
fi

echo "Task assigned at: $ASSIGNED_AT"
```

### Step 2: Get Agent's Last Message

```bash
# Use the agent-messaging skill to check inbox for messages from this agent.
# Filter by sender matching $AGENT_NAME and extract the most recent message.
LAST_MESSAGE=$(# retrieve most recent message from $AGENT_NAME)

LAST_ACTIVITY=$(echo "$LAST_MESSAGE" | jq -r '.timestamp')
MESSAGE_TYPE=$(echo "$LAST_MESSAGE" | jq -r '.type')

echo "Last activity: $LAST_ACTIVITY"
echo "Message type: $MESSAGE_TYPE"
```

### Step 3: Check for ACK

```bash
# Use the agent-messaging skill to check inbox for ACK messages from this agent.
# Filter by sender matching $AGENT_NAME and subject containing "[ACK]" or content.type == "ack"
ACK_EXISTS=$(# retrieve ACK message from $AGENT_NAME)

if [ -n "$ACK_EXISTS" ]; then
  HAS_ACK=true
else
  HAS_ACK=false
fi
```

### Step 4: Check for Blocker Report

```bash
# Use the agent-messaging skill to check inbox for blocker reports from this agent.
# Filter by sender matching $AGENT_NAME and content.type == "blocked"
BLOCKED=$(# retrieve blocker report from $AGENT_NAME)

if [ -n "$BLOCKED" ]; then
  IS_BLOCKED=true
else
  IS_BLOCKED=false
fi
```

### Step 5: Check for Completion Report

```bash
# Use the agent-messaging skill to check inbox for completion reports from this agent.
# Filter by sender matching $AGENT_NAME and subject containing "[DONE]" or content.type == "completion"
COMPLETED=$(# retrieve completion report from $AGENT_NAME)

if [ -n "$COMPLETED" ]; then
  IS_COMPLETE=true
else
  IS_COMPLETE=false
fi
```

### Step 6: Calculate State Duration

```bash
# Calculate minutes since last activity
if [ -n "$LAST_ACTIVITY" ]; then
  LAST_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${LAST_ACTIVITY%.*}" +%s 2>/dev/null || echo 0)
  CURRENT_EPOCH=$(date +%s)
  STATE_DURATION=$(( ($CURRENT_EPOCH - $LAST_EPOCH) / 60 ))
else
  STATE_DURATION=0
fi

echo "State duration: $STATE_DURATION minutes"
```

### Step 7: Determine State

```bash
# State determination logic
if [ "$IS_COMPLETE" = true ]; then
  AGENT_STATE="Complete"
elif [ "$IS_BLOCKED" = true ]; then
  AGENT_STATE="Blocked"
elif [ "$HAS_ACK" = false ]; then
  AGENT_STATE="No ACK"
elif [ -z "$LAST_ACTIVITY" ] || [ "$STATE_DURATION" -gt 60 ]; then
  # No activity in over an hour after ACK
  AGENT_STATE="No Progress"
elif [ "$STATE_DURATION" -gt 120 ]; then
  # Over 2 hours since last update
  AGENT_STATE="Stale"
else
  AGENT_STATE="Active"
fi

# Check for unresponsive (multiple reminders sent)
# Use the agent-messaging skill to count reminder messages sent to this agent.
# Filter messages sent to $AGENT_NAME where from == "orchestrator" and content.type == "reminder"
REMINDER_COUNT=$(# count reminder messages sent to $AGENT_NAME)

if [ "$REMINDER_COUNT" -gt 2 ] && [ "$STATE_DURATION" -gt 60 ]; then
  AGENT_STATE="Unresponsive"
fi

echo "Agent state: $AGENT_STATE"
```

## State Transition Diagram

```
Assigned → (ACK received) → Acknowledged
Acknowledged → (progress update) → Active
Acknowledged → (no updates) → No Progress
Active → (no updates after activity) → Stale
No Progress/Stale → (reminder sent, no response) → Unresponsive
Any → (blocker reported) → Blocked
Active → (completion reported) → Complete
```

## Output Format

```json
{
  "task_id": "42",
  "agent_name": "implementer-1",
  "agent_state": "Active",
  "last_activity": "2024-01-15T10:30:00Z",
  "state_duration_minutes": 45,
  "has_ack": true,
  "is_blocked": false,
  "is_complete": false,
  "reminder_count": 0
}
```

## Success Criteria

- [ ] Assignment timestamp retrieved
- [ ] Last agent message found (or confirmed none)
- [ ] ACK status determined
- [ ] Blocker status checked
- [ ] Completion status checked
- [ ] State correctly identified

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| No assignment found | Label missing or wrong agent | Check `assign:` labels on issue |
| AI Maestro unreachable | Service down | Use op-verify-aimaestro-availability |
| Ambiguous state | Multiple conditions true | Priority: Complete > Blocked > Unresponsive > Stale |

## Related Operations

- op-send-first-reminder
- op-send-urgent-reminder
- op-handle-blocker-report
