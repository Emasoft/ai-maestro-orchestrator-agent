# AI Maestro Message Response Decision Tree


## Contents

- [Step 1: Priority Triage](#step-1-priority-triage)
- [Step 2: Message Type Routing](#step-2-message-type-routing)
- [Step 3: Response Actions](#step-3-response-actions)
- [Step 4: ACK Protocol](#step-4-ack-protocol)

---

## Step 1: Priority Triage

| Priority | Action |
|----------|--------|
| URGENT | Interrupt current task, process immediately |
| HIGH | Process within 5 minutes |
| NORMAL | Process within 15 minutes |
| LOW | Process when available |

## Step 2: Message Type Routing

```
Message Received
│
├─► Priority = URGENT?
│   ├─ YES → Interrupt, save state, handle immediately
│   └─ NO → Continue
│
├─► Type = "task"?
│   ├─ YES → Send ACK, add to queue
│   └─ NO → Continue
│
├─► Type = "status-request"?
│   ├─ YES → Respond with current status
│   └─ NO → Continue
│
├─► Type = "completion"?
│   ├─ YES → Verify deliverables, approve/reject
│   └─ NO → Continue
│
├─► Type = "blocker"?
│   ├─ YES → Investigate, provide solution
│   └─ NO → Continue
│
├─► Type = "question"?
│   ├─ YES → Answer or escalate
│   └─ NO → Log unknown type
```

## Step 3: Response Actions

| Type | Timeout | Action |
|------|---------|--------|
| blocker | 10 min | Investigate, provide solution |
| error | 10 min | Diagnose, create fix task |
| completion | 30 min | Verify, approve/reject |
| status-update | 15 min | Record, update tracking |
| question | 15 min | Answer or escalate |
| notification | None | Log only |

## Step 4: ACK Protocol

After processing any message:
1. Send ACK with status (received/processing/completed/failed)
2. Include estimated completion time if processing
3. Include result summary if completed
