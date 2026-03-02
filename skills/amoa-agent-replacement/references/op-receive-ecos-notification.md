---
procedure: support-skill
workflow-instruction: support
---

# Operation: Receive AMCOS Notification


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Detect AMCOS Notification](#step-1-detect-amcos-notification)
  - [Step 2: Check Message Queue](#step-2-check-message-queue)
  - [Step 3: Identify Notification Type](#step-3-identify-notification-type)
  - [Step 4: Acknowledge Notification](#step-4-acknowledge-notification)
  - [Step 5: Pause New Assignments](#step-5-pause-new-assignments)
  - [Step 6: Log Notification](#step-6-log-notification)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example](#example)
- [Checklist](#checklist)

## When to Use

Use this operation when AMCOS (Emergency Context-loss Operations System) sends a notification about agent failure or replacement.

## Prerequisites

- AI Maestro running and accessible
- AMCOS system operational
- Orchestrator in active state

## Procedure

### Step 1: Detect AMCOS Notification

AMCOS notifications arrive via AI Maestro with specific message format:

```json
{
  "from": "ecos",
  "subject": "Agent Replacement Required",
  "priority": "urgent",
  "content": {
    "type": "replacement_required",
    "failed_agent": "implementer-1",
    "failure_reason": "context_loss",
    "replacement_agent": "implementer-2",
    "urgency": "immediate"
  }
}
```

### Step 2: Check Message Queue

Use the `agent-messaging` skill to check your inbox for unread messages, then filter for messages from AMCOS (where `from` equals `ecos`).

### Step 3: Identify Notification Type

| Type | Meaning | Urgency |
|------|---------|---------|
| `context_loss` | Agent lost context, recovery impossible | immediate |
| `unresponsive` | Agent not responding to polls | high |
| `error_state` | Agent in error loop | high |
| `manual_request` | User requested replacement | normal |
| `session_ended` | Agent session terminated | immediate |

### Step 4: Acknowledge Notification

Send an acknowledgment using the `agent-messaging` skill:
- **Recipient**: `ecos`
- **Subject**: "ACK: Replacement for <failed_agent>"
- **Content**: "Received replacement notification. Beginning context compilation."
- **Type**: `acknowledgment`, **Priority**: `high`
- **Data**: include `failed_agent`, `replacement_agent`

**Verify**: confirm message delivery.

### Step 5: Pause New Assignments

Do NOT assign any new work to any agent until replacement is complete:

1. Mark orchestrator state as "replacement_in_progress"
2. Queue any pending assignments
3. Hold agent polling

### Step 6: Log Notification

```bash
# Log the replacement event
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) AMCOS_NOTIFICATION: Failed=$failed_agent Replacement=$replacement_agent Reason=$failure_reason" >> orchestrator.log
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| Notification Type | String | Type of failure/replacement |
| Failed Agent | String | Agent ID that failed |
| Replacement Agent | String | Agent ID of replacement |
| Acknowledgment | Boolean | Whether ACK was sent |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| No AMCOS message found | Network issue or false alarm | Check AI Maestro status |
| Invalid message format | AMCOS version mismatch | Check AMCOS compatibility |
| Replacement agent unavailable | Agent not registered | Request alternative from AMCOS |
| AI Maestro unreachable | Service down | Restart AI Maestro service |

## Example

```bash
# Full notification handling sequence

# 1. Check for AMCOS notifications
# Use the agent-messaging skill to check your inbox for unread messages,
# then filter for messages where content.type == "replacement_required"
AMCOS_MSG=$(# retrieve unread messages and filter by content type)

if [ -n "$AMCOS_MSG" ]; then
  # 2. Extract details
  FAILED=$(echo "$AMCOS_MSG" | jq -r '.content.failed_agent')
  REPLACEMENT=$(echo "$AMCOS_MSG" | jq -r '.content.replacement_agent')
  REASON=$(echo "$AMCOS_MSG" | jq -r '.content.failure_reason')

  # 3. Log
  echo "AMCOS: Replacing $FAILED with $REPLACEMENT due to $REASON"

  # 4. Acknowledge
  # Use the agent-messaging skill to send acknowledgment:
  # - Recipient: ecos
  # - Subject: "ACK: Replacement for $FAILED"
  # - Content: "Beginning replacement process"
  # - Type: acknowledgment, Priority: high
  # - Data: failed_agent=$FAILED, replacement_agent=$REPLACEMENT

  # 5. Proceed to context compilation
  echo "Proceed to: op-compile-task-context"
fi
```

## Checklist

- [ ] Check AI Maestro message queue
- [ ] Identify AMCOS notification
- [ ] Parse notification details (failed agent, replacement, reason)
- [ ] Send acknowledgment to AMCOS
- [ ] Pause new agent assignments
- [ ] Log the replacement event
- [ ] Proceed to context compilation
