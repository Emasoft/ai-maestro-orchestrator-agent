---
procedure: proc-execute-task
workflow-instruction: Step 17 - Task Execution
operation: send-task-delegation
---

# Operation: Send Task Delegation


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Steps](#steps)
  - [Step 1: Verify Agent Availability](#step-1-verify-agent-availability)
  - [Step 2: Send Task Message](#step-2-send-task-message)
  - [Step 3: Update GitHub Issue](#step-3-update-github-issue)
  - [Step 4: Record Assignment in Tracking](#step-4-record-assignment-in-tracking)
- [Success Criteria](#success-criteria)
- [Error Handling](#error-handling)
- [Next Operation](#next-operation)
- [Related Operations](#related-operations)

## Purpose

Send a prepared task delegation message to a remote agent via AI Maestro.

## When to Use

- After preparing complete task delegation instructions
- When assigning new work to an available agent
- When reassigning a task from an unresponsive agent

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| delegation_message | op-prepare-task-delegation output | Yes |
| agent_name | Agent roster | Yes |
| issue_number | GitHub issue | Yes |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| message_id | String | AI Maestro message ID |
| sent_timestamp | ISO8601 | When message was sent |
| delivery_status | String | success/failed |

## Steps

### Step 1: Verify Agent Availability

Use the `agent-messaging` skill to query the agent registry and verify the target agent is available (state is "available" or "idle"). If the agent is busy, log a warning.

**Verify**: confirm agent state before proceeding.

### Step 2: Send Task Message

Send a task delegation message using the `agent-messaging` skill:
- **Recipient**: the target agent session name
- **Subject**: "Task Assignment: #[ISSUE_NUMBER] - [TASK_TITLE]"
- **Content**: the full delegation message with instructions
- **Type**: `task`
- **Priority**: `normal`
- **Data**: include `task_id`, `files_in_scope`, `completion_criteria`

**Verify**: confirm message delivery.

```bash
# NOTE: The delegation message is sent using the agent-messaging skill
# The data fields include task_id, files_in_scope, and completion_criteria
  }'
```

### Step 3: Update GitHub Issue

```bash
# Add assignment label
gh issue edit $ISSUE_NUMBER --add-label "assign:$AGENT_NAME"

# Update status to in-progress
gh issue edit $ISSUE_NUMBER --add-label "status:in-progress"

# Add assignment comment
gh issue comment $ISSUE_NUMBER --body "Assigned to agent: $AGENT_NAME via AI Maestro at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

### Step 4: Record Assignment in Tracking

```bash
# Log assignment for monitoring
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) | ASSIGNED | #$ISSUE_NUMBER | $AGENT_NAME" >> assignment_log.txt
```

## Success Criteria

- [ ] Message sent successfully (AI Maestro returns message ID)
- [ ] GitHub issue labeled with `assign:<agent>` and `status:in-progress`
- [ ] Assignment comment added to issue
- [ ] Assignment logged for progress monitoring

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Message send failed | AI Maestro unavailable | Run op-verify-aimaestro-availability |
| Agent not found | Agent not registered | Complete agent onboarding |
| Issue label failed | GitHub CLI auth issue | Re-authenticate gh CLI |

## Next Operation

After sending task delegation, proceed to:
- op-wait-for-acknowledgment

## Related Operations

- op-verify-aimaestro-availability
- op-prepare-task-delegation
- op-wait-for-acknowledgment
