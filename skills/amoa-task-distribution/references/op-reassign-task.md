# Operation: Reassign Task to Different Agent


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Preconditions](#preconditions)
- [When to Reassign](#when-to-reassign)
- [Input](#input)
- [Procedure](#procedure)
- [Commands](#commands)
- [Partial Progress Gathering](#partial-progress-gathering)
- [Output](#output)
- [Checklist](#checklist)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-reassign-task |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | Task Distribution |
| **Agent** | eoa-main |

## Purpose

Reassign a task from one agent to another when the current agent is unresponsive, blocked, or at capacity.

## Preconditions

- Task is currently assigned to an agent
- Reassignment is necessary (agent unresponsive after full escalation, or agent at capacity)
- New agent has been selected

## When to Reassign

| Situation | Reassign? |
|-----------|-----------|
| Agent unresponsive after 3 reminders | Yes |
| Agent at capacity with higher priority work | Yes |
| Agent reports cannot complete (skills mismatch) | Yes |
| Agent requests reassignment | Yes |
| Task simply taking longer than expected | No - wait |

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `issue_number` | int | Yes | The task issue number |
| `old_agent` | string | Yes | Current agent name |
| `new_agent` | string | Yes | New agent name |
| `reason` | string | Yes | Reason for reassignment |
| `repo` | string | Yes | Repository in `owner/repo` format |

## Procedure

1. Confirm reassignment is necessary
2. Gather partial progress from original agent (check issue comments, PRs, branches)
3. Remove current `assign:*` label from the issue
4. Add `assign:<new-agent>` label to the issue
5. Send reassignment message to new agent using the `agent-messaging` skill with full context and partial progress
6. Notify original agent that task has been reassigned
7. Verify new agent sends ACK
8. Log reassignment in delegation log

## Commands

```bash
ISSUE=42
OLD_AGENT="implementer-1"
NEW_AGENT="implementer-2"
REASON="Original agent unresponsive after 3 reminders"

# Step 3: Remove old assignment
gh issue edit $ISSUE --remove-label "assign:$OLD_AGENT"

# Step 4: Add new assignment
gh issue edit $ISSUE --add-label "assign:$NEW_AGENT"

# Step 5: Message new agent using the agent-messaging skill:
# - Recipient: $NEW_AGENT
# - Subject: "Task Reassignment: Issue #$ISSUE"
# - Content: "Task #$ISSUE has been reassigned to you from $OLD_AGENT. Reason: $REASON. Please review existing progress and continue."
# - Type: reassignment, Priority: high
# - Data: issue_number, previous_agent, partial_progress
# Verify: confirm delivery

# Step 6: Notify old agent using the agent-messaging skill:
# - Recipient: $OLD_AGENT
# - Subject: "Task Reassigned: Issue #$ISSUE"
# - Content: "Task #$ISSUE has been reassigned to $NEW_AGENT. Reason: $REASON."
# - Type: notification, Priority: normal
# Verify: confirm delivery
```

## Partial Progress Gathering

Before reassigning, gather any partial progress:

1. **Issue comments** - Check for status updates
2. **Branches** - `gh api repos/OWNER/REPO/branches | jq '.[] | select(.name | contains("issue-42"))'`
3. **Draft PRs** - `gh pr list --state all --search "head:issue-42"`
4. **Handoff docs** - Check `docs_dev/handoffs/`

Include all partial progress in the reassignment message.

## Output

```json
{
  "reassigned": true,
  "issue_number": 42,
  "from_agent": "implementer-1",
  "to_agent": "implementer-2",
  "reason": "Agent unresponsive after 3 reminders",
  "partial_progress_included": true
}
```

## Checklist

- [ ] Confirm reassignment is necessary (agent unresponsive after full escalation, or agent at capacity)
- [ ] Gather partial progress from original agent (check issue comments, PRs, branches)
- [ ] Remove current `assign:*` label from the issue
- [ ] Add `assign:<new-agent>` label to the issue
- [ ] Send reassignment message to new agent via AI Maestro using the `agent-messaging` skill (include all task context and partial progress)
- [ ] Notify original agent via AI Maestro: "Task reassigned to <new-agent>"
- [ ] Verify new agent sends ACK
- [ ] Log reassignment in delegation log file

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| New agent also unavailable | No agents available | Escalate to user |
| Partial progress lost | Agent did not document | Log warning, start fresh |

## Related Operations

- [op-assign-task.md](op-assign-task.md) - Initial assignment
- [op-select-agent.md](op-select-agent.md) - Selecting new agent
