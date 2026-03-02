# Messaging Protocol Part 5: Notifications and Response Expectations


## Contents

- [5.1 Automatic Message Notification (Subconscious)](#51-automatic-message-notification-subconscious)
  - [What It Does](#what-it-does)
- [5.2 How Subconscious Polling Works](#52-how-subconscious-polling-works)
  - [Polling Cycle](#polling-cycle)
  - [Notification Format](#notification-format)
  - [Checking Subconscious Status](#checking-subconscious-status)
  - [Key Implications](#key-implications)
- [5.3 Response Expectations by Message Type](#53-response-expectations-by-message-type)
  - [Response Flow Diagram](#response-flow-diagram)
- [5.4 No-Response-Required Messages](#54-no-response-required-messages)
  - [When Progress Updates DO Require Response](#when-progress-updates-do-require-response)
- [5.5 Handling No Response](#55-handling-no-response)
  - [For Required Responses](#for-required-responses)
  - [For Optional Responses](#for-optional-responses)
- [Related Sections](#related-sections)

---

**Parent document**: [messaging-protocol.md](messaging-protocol.md)

---

## 5.1 Automatic Message Notification (Subconscious)

AI Maestro includes an automatic notification system called "subconscious" that runs in the background for each registered agent session.

### What It Does

The subconscious system:
- Monitors each agent's inbox for unread messages
- Types notifications directly into idle terminals
- Requires no setup or configuration
- Runs automatically with AI Maestro server

---

## 5.2 How Subconscious Polling Works

### Polling Cycle

1. **Interval**: Checks every 5 minutes per agent
2. **Idle Detection**: Only notifies when session is idle (30+ seconds)
3. **Notification Method**: Uses tmux `send-keys` to type into terminal

### Notification Format

When a new message arrives:
```
You have a new message from [sender] about [subject]. Please check your inbox.
```

### Checking Subconscious Status

Verify by checking your inbox using the `agent-messaging` skill. If the subconscious polling is running, you will see inbox notifications automatically.

### Key Implications

| Aspect | Behavior |
|--------|----------|
| No hooks needed | Notifications are automatic |
| 5-minute latency | For urgent messages, use high/urgent priority |
| Idle requirement | Notifications only appear when agent is not actively processing |
| tmux dependency | Requires active tmux session |

---

## 5.3 Response Expectations by Message Type

| Sent Message Type | Expected Response Type | Timeout | Required? |
|-------------------|------------------------|---------|-----------|
| `task` | `task-acknowledgment` | 5 min | YES |
| `fix-request` | `task-acknowledgment` | 5 min | YES |
| `status-request` | `progress-update` | 2 min | YES |
| `approval` | None | N/A | NO |
| `rejection` | `task-acknowledgment` | 5 min | YES |
| `escalation` | `escalation-response` | Varies | YES |
| `escalation-response` | None | N/A | NO |
| `completion-report` (success) | `report-ack` | 5 min | YES |
| `completion-report` (failed/blocked) | `escalation-response` | 30 min | YES |

### Response Flow Diagram

```
Orchestrator                    Agent
    │                            │
    ├──── task ─────────────────►│
    │◄─── task-acknowledgment ───┤
    │                            │
    │◄─── progress-update ───────┤ (periodic)
    │                            │
    │◄─── completion-report ─────┤
    ├──── report-ack ───────────►│
    │                            │
```

---

## 5.4 No-Response-Required Messages

These message types do NOT require acknowledgment:

| Message Type | Reason |
|--------------|--------|
| `approval` | Informational confirmation of successful review |
| `escalation-response` | Ends the escalation thread |
| `progress-update` | Periodic status (unless specifically requested) |

### When Progress Updates DO Require Response

A `progress-update` requires response when:
- It contains `blockers` that need resolution
- It includes `awaiting_decision: true`
- It's sent in response to a `status-request`

---

## 5.5 Handling No Response

When expected response is not received:

### For Required Responses

1. Log timeout event
2. Send retry with `retry: true` metadata
3. If still no response, escalate or reassign

### For Optional Responses

1. Continue with workflow
2. Log for tracking purposes
3. Consider agent potentially busy

---

## Related Sections

- [Part 3: Message Types](messaging-protocol-part3-message-types.md) - Full message type schemas
- [Part 6: Timeouts](messaging-protocol-part6-timeouts-integration.md) - Detailed timeout handling
- [Part 7: Troubleshooting](messaging-protocol-part7-troubleshooting.md) - Notification problems
