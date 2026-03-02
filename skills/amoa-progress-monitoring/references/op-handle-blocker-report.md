---
procedure: proc-execute-task
workflow-instruction: Step 17 - Task Execution
operation: handle-blocker-report
---

# Operation: Handle Blocker Report


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [IRON RULE](#iron-rule)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Blocker Categories](#blocker-categories)
- [Steps](#steps)
  - [Step 1: Parse Blocker Report](#step-1-parse-blocker-report)
  - [Step 2: Verify Blocker Is Real](#step-2-verify-blocker-is-real)
  - [Step 3: Record Previous Status](#step-3-record-previous-status)
  - [Step 4: Update Task to Blocked Status](#step-4-update-task-to-blocked-status)
  - [Step 5: Create Blocker Tracking Issue](#step-5-create-blocker-tracking-issue)
- [Resolution](#resolution)
- [Notes](#notes)
  - [Step 6: Escalate to EAMA Immediately](#step-6-escalate-to-eama-immediately)
  - [Step 7: Check for Alternative Work](#step-7-check-for-alternative-work)
- [Blocker Lifecycle Checklist](#blocker-lifecycle-checklist)
  - [When a task becomes blocked:](#when-a-task-becomes-blocked)
- [Success Criteria](#success-criteria)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Process a blocker report from an agent, create tracking issue, update task status, and escalate to user immediately.

## When to Use

- Agent sends a `[BLOCKED]` status message
- Agent reports inability to proceed due to dependency
- External resource or approval is required

## IRON RULE

The user must ALWAYS be informed of blockers immediately. There is NO scenario where a blocker should be "monitored quietly" for hours or days before telling the user. The user may have the solution ready in minutes - but only if they know about the problem.

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| task_id | Issue number | Yes |
| agent_name | Reporting agent | Yes |
| blocker_message | Agent's blocker report | Yes |
| blocker_category | Classification | Yes |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| blocker_issue_number | Integer | Created blocker tracking issue |
| task_status_updated | Boolean | Task moved to blocked |
| user_notified | Boolean | EAMA escalation sent |

## Blocker Categories

| Category | Examples | Resolution Owner |
|----------|----------|------------------|
| Task Dependency | Feature B requires API from Feature A | Orchestrator (coordinate) |
| Problem Resolution | Bug must be fixed before feature can be tested | Orchestrator (prioritize) |
| Missing Resource | API key, database access, test environment | User |
| Missing Approval | Design decision, architecture choice | User/Architect |
| External Dependency | Third-party API down, vendor response | User (external contact) |
| Access/Credentials | Repository access, deployment credentials | User |

## Steps

### Step 1: Parse Blocker Report

```bash
TASK_ID=$1
AGENT_NAME=$2
BLOCKER_MESSAGE=$3

# Expected format from agent:
# [BLOCKED] <task-id> - <blocker-description>
# Waiting on: <dependency or resource>
# Impact: <what cannot proceed>
# Suggested resolution: <if any>

BLOCKER_DESCRIPTION=$(echo "$BLOCKER_MESSAGE" | head -1 | sed 's/\[BLOCKED\] [0-9]* - //')
WAITING_ON=$(echo "$BLOCKER_MESSAGE" | grep "Waiting on:" | sed 's/Waiting on: //')
IMPACT=$(echo "$BLOCKER_MESSAGE" | grep "Impact:" | sed 's/Impact: //')
SUGGESTED=$(echo "$BLOCKER_MESSAGE" | grep "Suggested resolution:" | sed 's/Suggested resolution: //')
```

### Step 2: Verify Blocker Is Real

```bash
# Check if agent can actually solve this themselves
# This requires judgment - some things that seem blocking may have workarounds

# For dependency blockers, check if the blocking task exists and is in progress
if echo "$BLOCKER_MESSAGE" | grep -q "requires.*#"; then
  BLOCKING_ISSUE=$(echo "$BLOCKER_MESSAGE" | grep -oP '#\d+' | head -1 | tr -d '#')
  BLOCKING_STATUS=$(gh issue view $BLOCKING_ISSUE --json state,labels | jq -r '.state')

  if [ "$BLOCKING_STATUS" = "CLOSED" ]; then
    echo "Blocking issue #$BLOCKING_ISSUE is already closed. Agent may have stale info."
    # Notify agent that blocker may be resolved
  fi
fi
```

### Step 3: Record Previous Status

```bash
# CRITICAL: Record current status BEFORE moving to blocked
CURRENT_STATUS=$(gh issue view $TASK_ID --json labels | jq -r '.labels[] | select(.name | startswith("status:")) | .name')

echo "Previous status: $CURRENT_STATUS"
```

### Step 4: Update Task to Blocked Status

```bash
# Remove current status, add blocked
gh issue edit $TASK_ID --remove-label "$CURRENT_STATUS" --add-label "status:blocked"

# Add blocker comment to task
gh issue comment $TASK_ID --body "**BLOCKED**

$BLOCKER_DESCRIPTION

**Waiting on:** $WAITING_ON
**Impact:** $IMPACT
**Previous status:** $CURRENT_STATUS
**Reported by:** $AGENT_NAME
**Reported at:** $(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

### Step 5: Create Blocker Tracking Issue

```bash
# Create separate issue to track the blocker itself
BLOCKER_ISSUE=$(gh issue create \
  --title "BLOCKER: $BLOCKER_DESCRIPTION" \
  --label "type:blocker" \
  --body "## Blocker Details

This issue tracks a problem that is blocking task #$TASK_ID.

**Blocked Task:** #$TASK_ID
**Blocked Agent:** $AGENT_NAME
**Category:** $BLOCKER_CATEGORY
**What's Needed:** $WAITING_ON
**Impact:** $IMPACT
**Suggested Resolution:** $SUGGESTED

**Previous Task Status:** $CURRENT_STATUS

## Resolution

Close this issue when the blocking problem is resolved and the blocked task can resume.

## Notes

Add updates on resolution progress here." | grep -oP '\d+$')

echo "Created blocker issue: #$BLOCKER_ISSUE"

# Link blocker issue to blocked task
gh issue comment $TASK_ID --body "Blocker tracked in #$BLOCKER_ISSUE"
```

### Step 6: Escalate to EAMA Immediately

```bash
# CRITICAL: Immediate user notification - no waiting period
# Send blocker escalation using the agent-messaging skill:
# - Recipient: eama-main
# - Subject: "[BLOCKER] Task #$TASK_ID blocked - User action required"
# - Content: "Task Blocked - Immediate Attention Required. Task: #$TASK_ID, Agent: $AGENT_NAME, Blocker: $BLOCKER_DESCRIPTION, Category: $BLOCKER_CATEGORY, What is needed: $WAITING_ON, Impact: $IMPACT, Blocker tracking issue: #$BLOCKER_ISSUE. Please provide resolution or guidance."
# - Type: blocker-escalation, Priority: urgent
# - Data: task_id, blocker_issue, agent, category, previous_status
```

### Step 7: Check for Alternative Work

```bash
# See if agent can work on other tasks while blocked
AVAILABLE_TASKS=$(gh issue list --label "status:ready" --json number,title | jq -r '.[] | "#\(.number) - \(.title)"')

if [ -n "$AVAILABLE_TASKS" ]; then
  # Send alternative tasks notification using the agent-messaging skill:
  # - Recipient: $AGENT_NAME
  # - Subject: "Blocker Acknowledged - Alternative Tasks Available"
  # - Content: "Your blocker on #$TASK_ID has been recorded and escalated. While waiting for resolution, you may work on: $AVAILABLE_TASKS. Would you like to be assigned one of these tasks?"
  # - Type: info, Priority: normal
  # - Data: blocked_task, available_tasks
fi
```

## Blocker Lifecycle Checklist

### When a task becomes blocked:

- [ ] Verify the blocker is real (agent cannot solve it themselves)
- [ ] Record the task's current status label before moving to Blocked
- [ ] Remove current `status:*` label from the blocked task
- [ ] Add `status:blocked` label to the blocked task
- [ ] Add blocker details as comment on the blocked task issue
- [ ] Create a separate GitHub issue for the blocker (`type:blocker` label)
- [ ] Send blocker-escalation message to EAMA via AI Maestro using the `agent-messaging` skill IMMEDIATELY
- [ ] Check if other unblocked tasks can be assigned to the waiting agent

## Success Criteria

- [ ] Blocker parsed and categorized
- [ ] Previous status recorded
- [ ] Task status updated to blocked
- [ ] Blocker tracking issue created
- [ ] EAMA notified immediately
- [ ] Agent offered alternative work (if available)

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Blocker already reported | Duplicate message | Check if blocker issue exists |
| Category unclear | Vague blocker description | Ask agent for clarification |
| EAMA unavailable | Agent offline | Queue escalation, retry |

## Related Operations

- op-resolve-blocker
- op-detect-agent-state
- op-escalate-to-user (in remote-agent-coordinator skill)
