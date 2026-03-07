## Table of Contents
- [Blocker Response Steps](#blocker-response-steps)
- [Blocker Escalation Message Example](#blocker-escalation-message-example)
- [Verification Before Escalation](#verification-before-escalation)
- [Checklist: Move Task to Blocked Column](#checklist-move-task-to-blocked-column)
- [Checklist: Restore Task from Blocked](#checklist-restore-task-from-blocked)

---

## Blocker Response Steps

If an agent reports that a distributed task is blocked, AMOA must take IMMEDIATE action:

1. **Acknowledge** the blocker via AI Maestro message to the reporting agent
2. **Record** the task's previous column BEFORE moving to Blocked (e.g., "In Progress", "AI Review", "Testing")
3. **Move** the task to the Blocked column on the Kanban board
4. **Update** labels: remove current `status:*`, add `status:blocked`
5. **Add comment** to the blocked task issue with blocker details and previous status
6. **Create a separate GitHub issue** for the blocker itself (labeled `type:blocker`, referencing the blocked task). Example:
   ```bash
   gh issue create --title "BLOCKER: Missing AWS credentials" --label "type:blocker" \
     --body "Blocking task #42. Category: Access/Credentials. What's needed: AWS credentials provisioned."
   ```
7. **Escalate** to AMAMA IMMEDIATELY with blocker-escalation message (see amoa-messaging-templates). Include the blocker issue number.
   - Do NOT wait or "monitor for 24h first"
   - User must be informed immediately - they may have the solution ready
8. **Check** if any other unblocked tasks can be assigned to the waiting agent
9. **Monitor** for self-resolution while waiting for user response
10. **When resolved**, close the blocker issue and restore task to its PREVIOUS column (not always "In Progress")

## Blocker Escalation Message Example

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "amoa-orchestrator",
  "to": "amama-assistant-manager",
  "subject": "BLOCKER: Task #42 - Missing API Credentials",
  "priority": "high",
  "content": {
    "type": "blocker-escalation",
    "message": "Task #42 is blocked. Agent impl-01 reports: Cannot deploy to staging - missing AWS credentials. Blocker tracked in issue #99.",
    "data": {
      "task_id": "42",
      "blocker_issue_number": "99",
      "assigned_agent": "impl-01",
      "blocker_category": "access-credentials",
      "previous_status": "status:ai-review",
      "impact": "Cannot complete deployment testing"
    }
  }
}
```

## Verification Before Escalation

Before escalating, verify the blocker is REAL:

| Check | Question | Action if False |
|-------|----------|-----------------|
| Cannot self-resolve | Can the agent solve this themselves? | Guide agent to solution, do not escalate |
| Not a knowledge gap | Is this a "how to" question? | Direct to documentation/skills, do not escalate |
| Not a process issue | Is this a team process the agent should follow? | Explain process, do not escalate |
| Truly blocking | Can work continue on other parts of the task? | Suggest parallel work, escalate only the blocking part |

Only escalate TRUE blockers that require user/architect intervention or resources the agent cannot access.

## Checklist: Move Task to Blocked Column

Copy this checklist and track your progress:

- [ ] Verify the blocker is real (verification table above)
- [ ] Acknowledge the blocker via AI Maestro to the reporting agent
- [ ] Record the task's current column/status BEFORE moving to Blocked
- [ ] Move the task to the Blocked column on the Kanban board
- [ ] Remove current `status:*` label, add `status:blocked`
- [ ] Add blocker details as comment on the blocked task issue (include `Previous status: $CURRENT_STATUS`)
- [ ] Create a separate GitHub issue for the blocker (`type:blocker` label, referencing the blocked task)
- [ ] Send blocker-escalation message to AMAMA via AI Maestro using the `agent-messaging` skill (include `blocker_issue_number`)
- [ ] Check if other unblocked tasks can be assigned to the waiting agent

## Checklist: Restore Task from Blocked

Copy this checklist and track your progress:

- [ ] Verify the blocker is actually resolved (do not assume)
- [ ] Retrieve the task's previous status from the blocker comment (`Previous status: ...`)
- [ ] Add resolution comment on the blocked task issue
- [ ] Close the blocker issue: `gh issue close $BLOCKER_ISSUE --comment "Resolved: [details]"`
- [ ] Remove `status:blocked` label from the task
- [ ] Restore previous status label on the task (e.g., `status:in-progress`, `status:ai-review`)
- [ ] Move task back to its PREVIOUS column on the Kanban board (not always "In Progress")
- [ ] Notify the assigned agent via AI Maestro that the blocker is resolved and work can resume
- [ ] Log the resolution in the issue timeline
