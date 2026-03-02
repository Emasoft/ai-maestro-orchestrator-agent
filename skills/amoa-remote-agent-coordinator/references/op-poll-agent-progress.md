---
procedure: proc-execute-task
workflow-instruction: Step 17 - Task Execution
operation: poll-agent-progress
---

# Operation: Poll Agent Progress


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Steps](#steps)
  - [Step 1: Check Time Since Last Update](#step-1-check-time-since-last-update)
  - [Step 2: Send Proactive Status Request](#step-2-send-proactive-status-request)
  - [Step 3: Mandatory Poll Questions](#step-3-mandatory-poll-questions)
  - [Step 4: Process Response](#step-4-process-response)
- [Polling Schedule](#polling-schedule)
- [No-Response Escalation Timeline](#no-response-escalation-timeline)
- [Success Criteria](#success-criteria)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Proactively poll remote agents for progress updates every 10-15 minutes during active work.

## When to Use

- After agent acknowledges task (ongoing)
- When no progress update received
- During active work periods
- Before overnight handoff to verify agent status

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| task_id | Issue number | Yes |
| agent_name | Assigned agent | Yes |
| last_update_time | AI Maestro message history | Yes |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| progress_report | Object | Agent's status update |
| blockers | Array | Any blockers reported |
| estimated_completion | String | Agent's ETA if provided |
| needs_escalation | Boolean | True if no response |

## Steps

### Step 1: Check Time Since Last Update

```bash
# Get last message from agent about this task
# Use the agent-messaging skill to query inbox messages, filtering for
# messages from the target agent about the specific task ID

# Calculate minutes since last update
LAST_UPDATE_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%S" "$LAST_UPDATE" +%s 2>/dev/null || echo 0)
CURRENT_EPOCH=$(date +%s)
MINUTES_SINCE=$((($CURRENT_EPOCH - $LAST_UPDATE_EPOCH) / 60))

echo "Minutes since last update: $MINUTES_SINCE"
```

### Step 2: Send Proactive Status Request

If more than 10-15 minutes since last update:

Send a status request using the `agent-messaging` skill:
- **Recipient**: the agent session name
- **Subject**: "Status Check: #[TASK_ID]"
- **Content**: "Please provide a progress update for task #[TASK_ID]. Report: 1. Current progress 2. Any blockers 3. Anything unclear 4. Estimated time to completion"
- **Type**: `status-request`
- **Priority**: `normal`
- **Data**: include `task_id`, `last_known_update`

**Verify**: confirm message delivery.

```bash
# NOTE: The status request is sent using the agent-messaging skill as described above
```

### Step 3: Mandatory Poll Questions

Every status request MUST include these questions:

1. **Current progress** - What has been completed?
2. **Blockers or issues** - What is preventing progress?
3. **Unclear items** - What needs clarification?
4. **Difficulties encountered** - What challenges arose?
5. **Estimated completion** - When do you expect to finish?

### Step 4: Process Response

When agent responds:

```bash
# Parse progress report
PROGRESS=$(echo "$RESPONSE" | jq -r '.content.message')
BLOCKERS=$(echo "$RESPONSE" | jq -r '.content.data.blockers // []')
ETA=$(echo "$RESPONSE" | jq -r '.content.data.estimated_completion // "unknown"')

# Log progress
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) | PROGRESS | #$TASK_ID | $AGENT_NAME | $PROGRESS" >> progress_log.txt

# Check for blockers
if [ "$(echo "$BLOCKERS" | jq 'length')" -gt 0 ]; then
  echo "BLOCKERS DETECTED - triggering blocker handling"
  # Proceed to op-handle-blocker-report
fi
```

## Polling Schedule

| Task Type | Poll Interval | Notes |
|-----------|---------------|-------|
| Critical/Urgent | Every 10 minutes | High priority tasks |
| Normal | Every 15 minutes | Standard development |
| Low priority | Every 30 minutes | Non-blocking tasks |

## No-Response Escalation Timeline

| Step | Condition | Action |
|------|-----------|--------|
| 1 | No response to first poll | Wait 15 more minutes |
| 2 | No response after 30 min total | Send high-priority reminder |
| 3 | No response after 1 hour | Send urgent escalation |
| 4 | No response after 2 hours | Notify user, consider reassignment |

## Success Criteria

- [ ] Status request sent with all mandatory questions
- [ ] Response received and parsed
- [ ] Progress logged
- [ ] Blockers identified and escalated if present
- [ ] Escalation triggered if no response

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| No response | Agent hibernated/offline | Distinguish via ECOS check |
| Stale progress | Agent stuck | Offer assistance or reassign |
| Missing ETA | Agent uncertain | Request breakdown of remaining work |

## Related Operations

- op-wait-for-acknowledgment
- op-handle-blocker-report (in progress-monitoring skill)
- op-send-urgent-reminder (in progress-monitoring skill)
