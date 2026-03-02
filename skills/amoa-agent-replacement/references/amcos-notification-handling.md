# ECOS Notification Handling Reference

## Contents

- [1.1 Notification Types](#11-notification-types)
- [1.2 Urgency Levels](#12-urgency-levels)
- [1.3 Acknowledgment Protocol](#13-acknowledgment-protocol)
- [1.4 Error Handling](#14-error-handling)

---

## 1.1 Notification Types

ECOS sends different notification types for agent replacement scenarios:

### Agent Failure Notification

Sent when an agent has definitively failed:

```json
{
  "content": {
    "type": "agent_replacement",
    "failed_agent": {
      "failure_reason": "crash",
      "recoverable": false
    }
  }
}
```

**Failure Reasons:**

| Reason | Description | Action |
|--------|-------------|--------|
| `crash` | Agent process crashed unexpectedly | Immediate replacement |
| `context_loss` | Agent lost context and cannot recover | Immediate replacement |
| `unresponsive` | Agent stopped responding to messages | Wait 2 minutes, then replace |
| `timeout` | Agent exceeded task timeout | Evaluate, may replace |
| `manual` | User requested replacement | Follow user instructions |

### Pre-emptive Replacement Notification

Sent when ECOS anticipates a failure:

```json
{
  "content": {
    "type": "agent_replacement",
    "failed_agent": {
      "failure_reason": "context_loss_imminent",
      "current_context_usage": "95%"
    },
    "urgency": "prepare"
  }
}
```

**Pre-emptive Reasons:**

| Reason | Description | Action |
|--------|-------------|--------|
| `context_loss_imminent` | Agent approaching context limit | Prepare handoff |
| `resource_exhaustion` | Agent running low on resources | Prepare handoff |
| `scheduled_maintenance` | Planned agent restart | Schedule handoff |

### Recovery Notification

Sent when a failed agent recovers:

```json
{
  "content": {
    "type": "agent_recovery",
    "recovered_agent": {
      "session": "helper-agent-generic",
      "agent_id": "implementer-1"
    },
    "replacement_agent": {
      "session": "helper-agent-2",
      "agent_id": "implementer-2"
    },
    "action": "keep_replacement|revert_to_original"
  }
}
```

---

## 1.2 Urgency Levels

### Immediate

Agent has failed and replacement must happen NOW:

```json
{
  "urgency": "immediate"
}
```

**Response Requirements:**
- ACK within 30 seconds
- Begin context compilation immediately
- Prioritize over all other orchestrator tasks
- Complete handoff within 5 minutes

### Prepare

Agent may fail soon, prepare handoff:

```json
{
  "urgency": "prepare"
}
```

**Response Requirements:**
- ACK within 2 minutes
- Begin context compilation in background
- Do not interrupt current orchestrator tasks
- Have handoff ready within 15 minutes

### When Available

Non-critical replacement, handle when convenient:

```json
{
  "urgency": "when_available"
}
```

**Response Requirements:**
- ACK within 5 minutes
- Schedule context compilation
- Complete before end of orchestration session

---

## 1.3 Acknowledgment Protocol

### ACK Message Format

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "ecos-controller",
  "subject": "[EOA-ACK] Replacement Notification Received",
  "priority": "high",
  "content": {
    "type": "ack",
    "message": "Replacement notification acknowledged",
    "original_notification_id": "<notification-uuid>",
    "failed_agent": "implementer-1",
    "replacement_agent": "implementer-2",
    "estimated_handoff_time": "5 minutes",
    "status": "processing"
  }
}
```

### ACK Required Fields

| Field | Description |
|-------|-------------|
| `original_notification_id` | UUID of the ECOS notification |
| `failed_agent` | ID of agent being replaced |
| `replacement_agent` | ID of new agent |
| `estimated_handoff_time` | How long until handoff complete |
| `status` | `processing`, `blocked`, `cannot_proceed` |

### ACK Status Values

| Status | Meaning | Next Step |
|--------|---------|-----------|
| `processing` | Working on handoff | ECOS waits |
| `blocked` | Cannot proceed, need help | ECOS investigates |
| `cannot_proceed` | Fatal issue | ECOS escalates to user |
| `complete` | Handoff finished | ECOS confirms |

### ACK Timeout Handling

If ECOS does not receive ACK within expected time:

1. ECOS sends reminder notification
2. After 2 reminders, ECOS alerts user
3. ECOS may attempt automatic recovery

---

## 1.4 Error Handling

### Notification Parsing Errors

If notification cannot be parsed:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "ecos-controller",
  "subject": "[EOA-ERROR] Invalid Notification",
  "priority": "urgent",
  "content": {
    "type": "error",
    "message": "Cannot parse replacement notification",
    "error_details": "Missing required field: failed_agent.session",
    "original_notification": "<raw-notification>"
  }
}
```

### Unknown Agent IDs

If failed agent is not in orchestrator's roster:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "ecos-controller",
  "subject": "[EOA-ERROR] Unknown Agent",
  "priority": "high",
  "content": {
    "type": "error",
    "message": "Failed agent not found in roster",
    "failed_agent": "unknown-agent-1",
    "known_agents": ["implementer-1", "implementer-2", "dev-alice"]
  }
}
```

### Replacement Agent Not Ready

If replacement agent is not available:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "ecos-controller",
  "subject": "[EOA-ERROR] Replacement Not Available",
  "priority": "urgent",
  "content": {
    "type": "error",
    "message": "Replacement agent not available",
    "replacement_agent": "implementer-2",
    "reason": "Session not found in AI Maestro registry"
  }
}
```

### Multiple Failures

If replacement agent also fails during handoff:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "ecos-controller",
  "subject": "[EOA-ESCALATE] Multiple Agent Failures",
  "priority": "urgent",
  "content": {
    "type": "escalation",
    "message": "Replacement agent also failed during handoff",
    "failed_agents": ["implementer-1", "implementer-2"],
    "tasks_affected": ["task-uuid-1", "task-uuid-2"],
    "action_required": "user_intervention"
  }
}
```

---

## Integration Points

### AI Maestro Integration

All ECOS notifications arrive via AI Maestro. Use the `agent-messaging` skill to check your inbox regularly for unread messages and filter for those where `content.type` equals `agent_replacement`.

### State File Integration

Update orchestrator state when processing notifications:

```yaml
ecos_notifications:
  - id: "notification-uuid"
    received: "2026-01-31T14:30:00Z"
    type: "agent_replacement"
    status: "processing"
    failed_agent: "implementer-1"
    replacement_agent: "implementer-2"
```

---

## Decision Trees for Agent Recovery and Response

### Agent Recovery Decision Tree

When ECOS notifies EOA that the original failed agent has recovered:

```
ECOS sends "Agent Recovery Notification" — original agent is back online
├─ Has replacement agent already started work?
│   ├─ No (replacement not yet assigned or hasn't begun)
│   │   → Cancel replacement assignment
│   │   → Re-assign task to original agent (it has prior context)
│   │   → Send ACK to ECOS: "Reverting to original agent, replacement cancelled"
│   │
│   ├─ Yes, replacement is in-progress but < 25% complete
│   │   → Compare: original agent's prior progress vs replacement's current progress
│   │   ├─ Original was further along → Revert to original agent
│   │   │   → Send stop notice to replacement → Collect work summary
│   │   │   → Send recovery context to original → Original resumes
│   │   └─ Replacement is further along → Keep replacement
│   │       → Notify original agent it's been superseded
│   │       → Send ACK to ECOS: "Keeping replacement, original released"
│   │
│   └─ Yes, replacement is > 25% complete
│       → Keep replacement agent (switching cost too high)
│       → Notify original agent it's been superseded
│       → Optionally: assign original to a different pending task
│       → Send ACK to ECOS: "Keeping replacement (>25% progress), original available for other tasks"
```

### EOA Response to Recovery Notification Template

```json
{
  "to": "<ecos-session-name>",
  "subject": "Agent Recovery Decision",
  "priority": "high",
  "content": {
    "type": "response",
    "message": "EOA has processed the agent recovery notification.",
    "data": {
      "original_agent": "<original-agent-session-name>",
      "replacement_agent": "<replacement-agent-session-name>",
      "task_id": "<task-id>",
      "decision": "REVERT_TO_ORIGINAL | KEEP_REPLACEMENT",
      "reason": "<explanation of decision>",
      "replacement_progress_pct": 15,
      "original_prior_progress_pct": 40,
      "action_taken": "<what EOA did: cancelled replacement / notified original / etc.>"
    }
  }
}
```

**Cross-reference**: For the full recovery decision framework, see `decision-trees-core.md` Section 5 (Agent Recovery Decision).

---

**Version**: 1.0.0
**Last Updated**: 2026-02-02
