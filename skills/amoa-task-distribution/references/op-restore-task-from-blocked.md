# Operation: Restore Task from Blocked Column


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Preconditions](#preconditions)
- [Input](#input)
- [Procedure](#procedure)
- [Commands](#commands)
- [Output](#output)
- [Important Notes](#important-notes)
- [Checklist](#checklist)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-restore-task-from-blocked |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | Task Distribution |
| **Agent** | eoa-main |

## Purpose

Move a task back to its PREVIOUS column when the blocker has been resolved, and notify the assigned agent to resume work.

## Preconditions

- Blocker has been verified as actually resolved
- Task is currently in `status:blocked`
- Previous status is recorded in the blocker comment

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `issue_number` | int | Yes | The blocked task issue number |
| `blocker_issue_number` | int | Yes | The blocker issue number to close |
| `resolution_details` | string | Yes | How the blocker was resolved |
| `repo` | string | Yes | Repository in `owner/repo` format |

## Procedure

1. Verify the blocker is actually resolved (do not assume)
2. Retrieve the task's previous status from the blocker comment (`Previous status: ...`)
3. Add resolution comment on the blocked task issue
4. Close the blocker issue with resolution details
5. Remove `status:blocked` label from the task
6. Restore previous status label on the task
7. Move task back to its PREVIOUS column on the Kanban board
8. Notify the assigned agent via AI Maestro that blocker is resolved
9. Log the resolution in the issue timeline

## Commands

```bash
ISSUE=42
BLOCKER_ISSUE=99
PREVIOUS_STATUS="status:ai-review"
RESOLUTION="AWS credentials have been provisioned by DevOps team"
AGENT="implementer-1"

# Step 3: Add resolution comment
gh issue comment $ISSUE --body "## Blocker Resolved
**Resolution:** $RESOLUTION
**Restoring to:** $PREVIOUS_STATUS"

# Step 4: Close blocker issue
gh issue close $BLOCKER_ISSUE --comment "Resolved: $RESOLUTION"

# Step 5-6: Update labels
gh issue edit $ISSUE --remove-label "status:blocked" --add-label "$PREVIOUS_STATUS"

# Step 8: Notify agent using the agent-messaging skill:
# - Recipient: $AGENT
# - Subject: "Blocker Resolved: Task #$ISSUE"
# - Content: "The blocker for task #$ISSUE has been resolved: $RESOLUTION. Please resume work."
# - Type: blocker-resolved, Priority: high
# - Data: {
        \"task_id\": \"$ISSUE\",
        \"restored_status\": \"$PREVIOUS_STATUS\"
      }
    }
  }"
```

## Output

```json
{
  "unblocked": true,
  "issue_number": 42,
  "blocker_issue_closed": 99,
  "restored_status": "status:ai-review",
  "agent_notified": "implementer-1"
}
```

## Important Notes

- Restore to PREVIOUS column, NOT always "In Progress"
- The previous status is stored in the blocker comment (`Previous status: ...`)
- Do not assume the blocker is resolved - verify first

## Checklist

- [ ] Verify the blocker is actually resolved (do not assume)
- [ ] Retrieve the task's previous status from the blocker comment (`Previous status: ...`)
- [ ] Add resolution comment on the blocked task issue
- [ ] Close the blocker issue: `gh issue close $BLOCKER_ISSUE --comment "Resolved: [details]"`
- [ ] Remove `status:blocked` label from the task
- [ ] Restore previous status label on the task (e.g., `status:in-progress`, `status:ai-review`)
- [ ] Move task back to its PREVIOUS column on the Kanban board (not always "In Progress")
- [ ] Notify the assigned agent via AI Maestro that the blocker is resolved and work can resume
- [ ] Log the resolution in the issue timeline

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Previous status not found | Missing from comment | Default to `status:in-progress` |
| Agent not responding | Agent offline | Log and wait for agent to come online |

## Related Operations

- [op-move-task-to-blocked.md](op-move-task-to-blocked.md) - When task becomes blocked
- [op-assign-task.md](op-assign-task.md) - Reassign if needed
