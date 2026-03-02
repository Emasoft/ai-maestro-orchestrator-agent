---
name: eoa-progress-monitoring
description: Agent progress monitoring via state-based detection. Use when tracking task completion, detecting stalls, or escalating unresponsive agents. Trigger with progress checks.
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
context: fork
user-invocable: false
agent: eoa-main
workflow-instruction: "Step 17"
procedure: "proc-execute-task"
---

# Progress Monitoring Skill

## Overview

This skill defines how the Orchestrator (EOA) monitors agent progress. Monitoring is based on **state transitions** and **response order** - not fixed time intervals. Agents collaborate asynchronously and may be hibernated for extended periods. The orchestrator tracks agent states (Acknowledged, Active, No Progress, Stale, Unresponsive, Blocked, Complete) and escalates through ordered steps when issues are detected.

## Prerequisites

1. Read **AGENT_OPERATIONS.md** for orchestrator workflow
2. Read **eoa-label-taxonomy** for status labels and workflow states
3. Read **eoa-messaging-templates** for message formats and escalation templates
4. Access to AI Maestro API for agent message history
5. Access to GitHub CLI for issue status queries
6. Understanding of agent lifecycle and state transitions

---

## 1. Agent States

Monitor agents based on their current state:

| State | Definition | Action |
|-------|------------|--------|
| **Acknowledged** | Agent sent ACK for assigned task | Normal monitoring |
| **No ACK** | Task assigned but no acknowledgment received | Send reminder |
| **Active** | Agent sending progress updates | Continue monitoring |
| **No Progress** | Agent acknowledged but no updates since | Send status request |
| **Stale** | Agent's last update predates significant events | Escalate priority |
| **Unresponsive** | Multiple reminders without any response | Consider reassignment |
| **Blocked** | Agent reported blocker | Address blocker |
| **Complete** | Agent reported task done | Verify and close |

---

## 2. State Detection

### 2.1 Check Agent State

Use the `agent-messaging` skill to retrieve the agent's last message timestamp. Query the message list for the agent and extract the timestamp of the most recent message.

```bash
# Get task assignment event
gh issue view $ISSUE --json timelineItems | jq '.timelineItems[] | select(.label == "assign:$AGENT_NAME")'
```

### 2.2 State Transitions

```
Assigned → (ACK received) → Acknowledged
Acknowledged → (progress update) → Active
Acknowledged → (no updates) → No Progress
Active → (no updates after activity) → Stale
No Progress/Stale → (reminder sent, no response) → Unresponsive
Any → (blocker reported) → Blocked
Active → (completion reported) → Complete
```

---

## 3. Escalation Order

Escalation follows a strict **order**, not time-based triggers:

| Step | Trigger State | Action | Priority |
|------|---------------|--------|----------|
| 1 | No ACK | Send first reminder | Normal |
| 2 | Still No ACK after Step 1 | Send urgent reminder | High |
| 3 | Unresponsive after Step 2 | Notify user, consider reassignment | Urgent |

### 3.1 First Reminder

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

### 3.2 Urgent Reminder

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

### 3.3 Reassignment Decision

When still unresponsive after urgent reminder:

1. Check if user is available → Present options (wait, reassign, abort)
2. If user unavailable → Auto-reassign to available agent
3. Notify original agent of reassignment
4. Transfer all context to new agent

---

## 4. Progress Report Format

Agents should report progress using this format:

### 4.1 Status Update

```
[IN_PROGRESS] <task-id> - <brief-description>
Progress: <percentage or milestone>
Next: <next-step>
Blockers: <none or blocker-list>
```

### 4.2 Completion Report

```
[DONE] <task-id> - <result-summary>
Output: <file-path or PR-number>
Tests: <passed/failed>
```

### 4.3 Blocker Report

```
[BLOCKED] <task-id> - <blocker-description>
Waiting on: <dependency or resource>
Impact: <what cannot proceed>
Suggested resolution: <if any>
```

---

## 5. Blocker Handling

**IRON RULE FOR BLOCKERS**: The user must ALWAYS be informed of blockers immediately. There is NO scenario where a blocker should be "monitored quietly" for hours or days before telling the user. The user may have the solution ready in minutes — but only if they know about the problem.

When an agent reports `[BLOCKED]`, EOA must verify the blocker is real (agent cannot solve it themselves), then IMMEDIATELY escalate to EAMA for user notification. There is NO waiting period for user notification — escalation happens as soon as the blocker is confirmed.

### 5.1 Comprehensive Blocker Definition

A blocker is ANY condition preventing task progress that the assigned agent cannot resolve independently:

| Blocker Category | Examples | Verification |
|------------------|----------|--------------|
| **Task Dependency** | Feature B requires API from Feature A (still in development) | Check if blocking task is complete |
| **Problem Resolution** | Bug must be fixed before feature can be tested | Verify bug status, check if workaround exists |
| **Missing Resource** | Need API key, database access, test environment | Confirm resource is not available via normal channels |
| **Missing Approval** | Design decision, architecture choice, breaking change | Check if approval authority (user/architect) was consulted |
| **External Dependency** | Third-party API down, vendor response needed | Verify external status, check if alternative exists |
| **Access/Credentials** | Repository access, deployment credentials, service permissions | Confirm access cannot be obtained via team processes |

### 5.2 Blocker Response Protocol

When agent reports `[BLOCKED]`:

1. **Verify** the blocker is real (agent cannot solve it themselves)
2. **Record** the task's current column BEFORE moving to Blocked (for restoration after unblocking)
3. **Move** task to Blocked column and add `status:blocked` label
4. **Remove** the `status:in-progress` (or whatever status it had) label
5. **Comment** on the blocked task issue with blocker details
6. **Create a separate GitHub issue** for the blocker itself (labeled `type:blocker`, referencing the blocked task). This makes the blocking problem visible to all agents and team members on the issue tracker.
7. **Escalate** to EAMA IMMEDIATELY via AI Maestro blocker-escalation message (see eoa-messaging-templates). Include the blocker issue number.
8. **Continue** monitoring for self-resolution while waiting for user response
9. **Check** if other unblocked tasks can be assigned to the waiting agent

### 5.3 Update Labels and Create Blocker Issue

```bash
# BEFORE moving to blocked, record current status
CURRENT_STATUS=$(gh issue view $ISSUE --json labels | jq -r '.labels[] | select(.name | startswith("status:")) | .name')

# Mark task as blocked
gh issue edit $ISSUE --remove-label "$CURRENT_STATUS" --add-label "status:blocked"

# Create a GitHub issue for the blocker (the problem preventing progress)
BLOCKER_ISSUE=$(gh issue create --title "BLOCKER: <one-line description of the blocking problem>" --label "type:blocker" \
  --body "## Blocker

This issue tracks a problem that is blocking task #$ISSUE.

**Blocked Task**: #$ISSUE
**Category**: <Task Dependency | Problem Resolution | Missing Resource | Access/Credentials | Missing Approval | External Dependency>
**What's Needed**: <specific action to resolve>
**Impact**: <what work is prevented>
**Previous Status**: $CURRENT_STATUS

## Resolution
Close this issue when the blocking problem is resolved and the blocked task can resume." \
  | grep -oP '\d+$')

# Add blocker details as comment on the blocked task
gh issue comment $ISSUE --body "BLOCKED: <blocker-description>. Previous status: $CURRENT_STATUS. Blocker tracked in #$BLOCKER_ISSUE"
```

### 5.4 When Blocker Resolved

When a blocker is resolved, the task returns to the COLUMN IT WAS IN BEFORE being blocked (not always "In Progress" — it could have been in Testing, Review, Deploy, etc.).

```bash
# Retrieve previous status from issue comments or metadata
PREVIOUS_STATUS=$(gh issue view $ISSUE --json comments | jq -r '.comments[-1].body' | grep "Previous status:" | awk '{print $3}')

# Close the blocker issue (the issue tracking the blocking problem)
gh issue close $BLOCKER_ISSUE --comment "Resolved: <resolution details>. Blocked task #$ISSUE can now resume."

# Restore previous status on the blocked task
gh issue edit $ISSUE --remove-label "status:blocked" --add-label "$PREVIOUS_STATUS"

# Add resolution comment on the blocked task
gh issue comment $ISSUE --body "Unblocked. Blocker #$BLOCKER_ISSUE resolved. Returning to $PREVIOUS_STATUS."

# Notify agent that blocker is resolved
# (send message via AI Maestro using the agent-messaging skill)
```

### 5.5 Blocker Lifecycle Checklist

Copy this checklist and track your progress:

**When a task becomes blocked:**
- [ ] Verify the blocker is real (agent cannot solve it themselves)
- [ ] Record the task's current status label (`$CURRENT_STATUS`) before moving to Blocked
- [ ] Remove current `status:*` label from the blocked task
- [ ] Add `status:blocked` label to the blocked task
- [ ] Move task to Blocked column on Kanban board
- [ ] Add blocker details as comment on the blocked task issue (include `Previous status: $CURRENT_STATUS`)
- [ ] Create a separate GitHub issue for the blocker (`type:blocker` label, referencing the blocked task)
- [ ] Send blocker-escalation message to EAMA via AI Maestro using the `agent-messaging` skill (include `blocker_issue_number`)
- [ ] Check if other unblocked tasks can be assigned to the waiting agent

**When the blocker is resolved:**
- [ ] Verify the blocker is actually resolved (do not assume)
- [ ] Add resolution comment on the blocked task issue
- [ ] Close the blocker issue (`gh issue close $BLOCKER_ISSUE --comment "Resolved: ..."`)
- [ ] Retrieve previous status from the blocker comment on the blocked task
- [ ] Remove `status:blocked` label from the task
- [ ] Restore previous status label (`$PREVIOUS_STATUS`) on the task
- [ ] Move task back to its PREVIOUS column on the Kanban board (not always "In Progress")
- [ ] Notify the assigned agent via AI Maestro that the blocker is resolved
- [ ] Log the resolution in the issue timeline

---

## 6. Completion Verification

When agent reports `[DONE]`:

### 6.1 Verification Checklist

Copy this checklist and track your progress:

- [ ] PR exists and is linked to issue
- [ ] Tests pass (CI status)
- [ ] Code review approved (if required)
- [ ] Documentation updated (if required)
- [ ] Issue checklist items complete

### 6.2 If Verification Passes

```bash
# Update status
gh issue edit $ISSUE --remove-label "status:in-progress" --add-label "status:done"

# Remove assignment (task complete)
gh issue edit $ISSUE --remove-label "assign:$AGENT_NAME"

# Close issue if all criteria met
gh issue close $ISSUE
```

### 6.3 If Verification Fails

Send clarification request to agent:

```json
{
  "type": "request",
  "message": "Completion verification failed. Missing: <list>. Please address and report again."
}
```

---

## 7. Dashboard View

Track all active tasks:

| Task | Agent | State | Last Update | Priority |
|------|-------|-------|-------------|----------|
| #42 | impl-01 | Active | Recent | High |
| #43 | impl-02 | No Progress | Stale | Normal |
| #44 | reviewer | Blocked | Recent | High |

Query active tasks:

```bash
# All in-progress tasks
gh issue list --label "status:in-progress" --json number,title,labels

# Blocked tasks
gh issue list --label "status:blocked" --json number,title,labels

# Tasks by agent
gh issue list --label "assign:impl-01" --json number,title,labels
```

---

## Instructions

Follow these steps to monitor agent progress:

1. Query all issues with `status:in-progress` label
2. For each assigned task:
   1. Determine current agent state (section 1)
   2. Check AI Maestro for agent's last message timestamp
   3. Compare task assignment time vs. last agent update
   4. If state is "No ACK", send first reminder (section 3.1)
   5. If state is "No Progress" or "Stale", send status request
   6. If state is "Unresponsive" after reminders, send urgent escalation (section 3.2)
   7. If state is "Blocked", handle blocker (section 5)
   8. If state is "Complete", verify completion (section 6)
3. Update issue labels to reflect current state
4. Log all state transitions and escalations
5. Reassign tasks only after full escalation order (section 3.3)

---

## Output

| Output Type | Format | Example |
|-------------|--------|---------|
| Agent state report | Markdown table | Task #42, impl-01, Active, last update 2h ago |
| Escalation message | AI Maestro JSON | Reminder or urgent message sent to agent |
| Dashboard view | Markdown table | All in-progress tasks with states |
| Blocker report | Issue comment | "BLOCKED: Waiting on API design approval" |
| Completion verification | Boolean + checklist | PR exists ✓, tests pass ✓, docs updated ✓ |

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Agent never ACKs | Agent offline, hibernated, or unaware | Send reminder, escalate to ECOS if no response |
| Agent stops responding mid-task | Agent crashed, hibernated, or blocked | Follow escalation order (sections 3.1-3.3) |
| Blocker reported but not resolved | Dependency on external event | Coordinate with other agents or escalate to user |
| Completion reported but verification fails | Missing tests, failing CI, or incomplete requirements | Send REVISE message (see **eoa-implementer-interview-protocol**) |
| Multiple agents updating same task | Concurrent work or reassignment conflict | Check `assign:*` label, coordinate via AI Maestro |
| Stale state but agent actually hibernated | Normal hibernation, not a failure | Distinguish hibernation from unresponsiveness via ECOS |

---

## Examples

### Example 1: Query Agent State via AI Maestro

```bash
# Get agent's last message timestamp
AGENT="implementer-1"
# Use the agent-messaging skill to retrieve messages for the agent
# and extract the timestamp of the most recent message
echo "Agent $AGENT last seen: $LAST_MESSAGE"

# Get task assignment timestamp
ISSUE=42
ASSIGNED_AT=$(gh issue view $ISSUE --json timelineItems | \
  jq -r '.timelineItems[] | select(.label.name == "assign:'$AGENT'") | .createdAt')

echo "Task #$ISSUE assigned at: $ASSIGNED_AT"
```

### Example 2: Send First Reminder

Send a status request using the `agent-messaging` skill:
- **Recipient**: `implementer-1`
- **Subject**: "Status Request: #42"
- **Content**: "What is your current status on #42? Report progress, blockers, and next steps."
- **Type**: `request`, **Priority**: `normal`
- **Data**: include `task_id: 42`

**Verify**: confirm message delivery.

### Example 3: Escalate to Urgent

Send an urgent escalation using the `agent-messaging` skill:
- **Recipient**: `implementer-1`
- **Subject**: "URGENT: #42 - Response Required"
- **Content**: "No response received. Please provide status immediately or task may be reassigned."
- **Type**: `escalation`, **Priority**: `urgent`
- **Data**: include `task_id: 42`, `escalation_level: 2`

**Verify**: confirm message delivery.

### Example 4: Handle Blocker Report

```bash
ISSUE=42

# Agent reports blocker via message
# Update issue labels
gh issue edit $ISSUE --remove-label "status:in-progress" --add-label "status:blocked"

# Add blocker comment to issue
gh issue comment $ISSUE --body "BLOCKED: Waiting on API endpoint design approval. Cannot proceed until #38 is resolved."

# Query the blocking issue
BLOCKER_STATUS=$(gh issue view 38 --json state,labels | jq -r '.state')
echo "Blocking issue #38 status: $BLOCKER_STATUS"

# If blocker is resolved, notify agent
if [ "$BLOCKER_STATUS" = "closed" ]; then
  gh issue edit $ISSUE --remove-label "status:blocked" --add-label "status:in-progress"
  # Send message to agent
fi
```

### Example 5: Verify Completion

```bash
ISSUE=42

# Check PR existence
PR_NUMBER=$(gh issue view $ISSUE --json body | jq -r '.body | match("PR #([0-9]+)") | .captures[0].string')

if [ -z "$PR_NUMBER" ]; then
  echo "VERIFICATION FAILED: No PR linked"
else
  # Check CI status
  CI_STATUS=$(gh pr view $PR_NUMBER --json statusCheckRollup | jq -r '.statusCheckRollup[] | select(.conclusion) | .conclusion')

  if [ "$CI_STATUS" = "SUCCESS" ]; then
    echo "VERIFICATION PASSED: PR #$PR_NUMBER exists and CI passed"
    # Update to done
    gh issue edit $ISSUE --remove-label "status:in-progress" --add-label "status:done"
    gh issue edit $ISSUE --remove-label "assign:implementer-1"
  else
    echo "VERIFICATION FAILED: CI status is $CI_STATUS"
  fi
fi
```

---

## Resources

- **AGENT_OPERATIONS.md** - Core orchestrator workflow
- **eoa-label-taxonomy** - Status labels and workflow states
- **eoa-messaging-templates** - Escalation message templates
- **eoa-task-distribution** - Assignment protocol and agent states
- **eoa-implementer-interview-protocol** - Post-task verification protocol
