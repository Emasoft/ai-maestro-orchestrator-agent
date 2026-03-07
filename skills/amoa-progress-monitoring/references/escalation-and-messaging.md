## Table of Contents

- [Escalation Order](#escalation-order)
- [First Reminder](#first-reminder)
- [Urgent Reminder](#urgent-reminder)
- [Reassignment Decision](#reassignment-decision)
- [Progress Report Format](#progress-report-format)
- [Completion Verification](#completion-verification)

---

## Escalation Order

Escalation follows a strict **order**, not time-based triggers:

| Step | Trigger State | Action | Priority |
|------|---------------|--------|----------|
| 1 | No ACK | Send first reminder | Normal |
| 2 | Still No ACK after Step 1 | Send urgent reminder | High |
| 3 | Unresponsive after Step 2 | Notify user, consider reassignment | Urgent |

## First Reminder

When state = No ACK or No Progress:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "orchestrator",
  "to": "<agent-name>",
  "subject": "Status Request: <task-id>",
  "priority": "normal",
  "content": {
    "type": "request",
    "message": "What is your current status on <task-id>? Report progress, blockers, and next steps.",
    "data": {
      "task_id": "<task-id>"
    }
  }
}
```

## Urgent Reminder

When state = Unresponsive (no response to first reminder):

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "orchestrator",
  "to": "<agent-name>",
  "subject": "URGENT: <task-id> - Response Required",
  "priority": "urgent",
  "content": {
    "type": "escalation",
    "message": "No response received. Please provide status immediately or task may be reassigned.",
    "data": {
      "task_id": "<task-id>",
      "escalation_level": 2
    }
  }
}
```

## Reassignment Decision

When still unresponsive after urgent reminder:

1. Check if user is available → Present options (wait, reassign, abort)
2. If user unavailable → Auto-reassign to available agent
3. Notify original agent of reassignment
4. Transfer all context to new agent

---

## Progress Report Format

Agents should report progress using this format:

### Status Update

```
[IN_PROGRESS] <task-id> - <brief-description>
Progress: <percentage or milestone>
Next: <next-step>
Blockers: <none or blocker-list>
```

### Completion Report

```
[DONE] <task-id> - <result-summary>
Output: <file-path or PR-number>
Tests: <passed/failed>
```

### Blocker Report

```
[BLOCKED] <task-id> - <blocker-description>
Waiting on: <dependency or resource>
Impact: <what cannot proceed>
Suggested resolution: <if any>
```

---

## Completion Verification

When agent reports `[DONE]`:

### Verification Checklist

- [ ] PR exists and is linked to issue
- [ ] Tests pass (CI status)
- [ ] Code review approved (if required)
- [ ] Documentation updated (if required)
- [ ] Issue checklist items complete

### If Verification Passes

```bash
# Update status
gh issue edit $ISSUE --remove-label "status:in-progress" --add-label "status:done"

# Remove assignment (task complete)
gh issue edit $ISSUE --remove-label "assign:$AGENT_NAME"

# Close issue if all criteria met
gh issue close $ISSUE
```

### If Verification Fails

Send clarification request to agent:

```json
{
  "type": "request",
  "message": "Completion verification failed. Missing: <list>. Please address and report again."
}
```
