---
name: eoa-task-distribution
description: Task distribution based on skills and availability. Use when assigning work to agents, balancing load, or resolving dependencies. Trigger with assignment requests.
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
context: fork
user-invocable: false
agent: eoa-main
workflow-instruction: "Steps 13, 16, 18, 22"
procedure: "proc-populate-kanban, proc-update-tasks, proc-update-kanban-status, proc-handle-failed-pr"
---

# Task Distribution Skill

## Overview

This skill defines how the Orchestrator (EOA) distributes tasks to agents. Distribution is based on **order**, **priority**, and **agent state** - not arbitrary timing. Tasks are selected from the ready queue, sorted by priority, filtered by dependencies, matched to agent capabilities, and assigned via labeled issues and AI Maestro messages.

## Prerequisites

1. Read **AGENT_OPERATIONS.md** for orchestrator workflow
2. Read **eoa-label-taxonomy** for label usage and cardinality rules
3. Read **eoa-messaging-templates** for message formats
4. Access to GitHub CLI (`gh`) and AI Maestro API
5. Understanding of agent states (active, hibernated, offline)

---

## 1. Task Distribution Order

Tasks are distributed following this order:

| Step | Action | Condition |
|------|--------|-----------|
| 1 | Identify ready tasks | Tasks with `status:ready` label |
| 2 | Sort by priority | `priority:critical` > `priority:high` > `priority:normal` > `priority:low` |
| 3 | Check dependencies | Task's blockedBy list is empty |
| 4 | Select agent | Match task requirements to available agents |
| 5 | Assign task | Add `assign:<agent>` label, send AI Maestro message using the `agent-messaging` skill |

---

## 2. Agent Selection Criteria

When selecting an agent for a task, evaluate in this order:

### 2.1 Availability Check

| State | Can Assign | Action |
|-------|------------|--------|
| Active, no current task | Yes | Assign immediately |
| Active, has current task | Maybe | Check if at capacity |
| Hibernated | No | Wake first or select different agent |
| Offline | No | Select different agent |

### 2.2 Skill Match

Match task requirements (`toolchain:*`, `component:*` labels) to agent capabilities:

```
Task labels: toolchain:python, component:api
Agent skills: python, api, testing

Match score: 2/2 required = 100% match
```

### 2.3 Capacity Check

| Agent Load | Can Assign |
|------------|------------|
| 0 active tasks | Yes |
| 1-2 active tasks | Yes, if high priority |
| 3+ active tasks | No, agent at capacity |

---

## 3. Assignment Protocol

### 3.1 Update Labels

```bash
# Remove any existing assign:* label first
gh issue view $ISSUE --json labels | jq -r '.labels[].name' | grep '^assign:' | while read label; do
  gh issue edit $ISSUE --remove-label "$label"
done

# Add new assignment
gh issue edit $ISSUE --add-label "assign:$AGENT_NAME"

# Update status
gh issue edit $ISSUE --remove-label "status:ready" --add-label "status:in-progress"
```

### 3.2 Send Assignment Message

Use template from eoa-messaging-templates (section 2.1):

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "orchestrator",
  "to": "<agent-name>",
  "subject": "Task Assignment: <task-title>",
  "priority": "high",
  "content": {
    "type": "request",
    "message": "You are assigned: <task-description>. Success criteria: <criteria>. Report status when starting and when complete.",
    "data": {
      "task_id": "<task-id>",
      "issue_number": "<github-issue-number>",
      "handoff_doc": "docs_dev/handoffs/<handoff-filename>.md"
    }
  }
}
```

### 3.3 Wait for ACK

After sending assignment, wait for agent acknowledgment. See **eoa-progress-monitoring** for response handling.

---

## 4. Dependency Management

### 4.1 Dependency Types

| Type | Example | Handling |
|------|---------|----------|
| Hard | Module B needs Module A's API | Block B until A complete |
| Soft | Testing can start with stubs | Assign with note about dependency |
| None | Independent tasks | Assign in parallel |

### 4.2 Dependency Resolution

```
Task A: status:in-progress, blocks: [B, C]
Task B: status:ready, blockedBy: [A] → Cannot assign yet
Task C: status:ready, blockedBy: [A] → Cannot assign yet

When Task A completes:
- Update A: status:done
- B and C become assignable
```

### 4.3 Circular Dependency Detection

If detected, STOP and report to user:

```
CIRCULAR DEPENDENCY:
Task A → depends on → Task B
Task B → depends on → Task A

Cannot proceed. User decision required.
```

---

## 5. Load Balancing

### 5.1 Even Distribution

When multiple agents can handle a task:

1. Check current load (active tasks per agent)
2. Prefer agent with lowest load
3. If equal load, prefer agent who completed similar tasks recently

### 5.2 Specialization

Some tasks benefit from agent specialization:

| Task Type | Preferred Agent |
|-----------|-----------------|
| Code review | Agent who wrote the code (context) |
| Bug fix | Agent who implemented feature |
| New feature | Agent with matching skills |

---

## 6. Reassignment

When reassigning a task (agent unresponsive or blocked):

1. Remove current `assign:*` label
2. Add `assign:<new-agent>` label
3. Send reassignment message to new agent using the `agent-messaging` skill with context
4. Notify original agent: "Task reassigned"
5. Include any partial progress from original agent

### 6.1 Reassignment Checklist

Copy this checklist and track your progress:

- [ ] Confirm reassignment is necessary (agent unresponsive after full escalation, or agent at capacity)
- [ ] Gather partial progress from original agent (check issue comments, PRs, branches)
- [ ] Remove current `assign:*` label from the issue
- [ ] Add `assign:<new-agent>` label to the issue
- [ ] Send reassignment message to new agent via AI Maestro using the `agent-messaging` skill (include all task context and partial progress)
- [ ] Notify original agent via AI Maestro: "Task reassigned to <new-agent>"
- [ ] Verify new agent sends ACK
- [ ] Log reassignment in delegation log file

---

## 7. When a Distributed Task Becomes Blocked

If an agent reports that a distributed task is blocked, EOA must take IMMEDIATE action:

### 7.1 Blocker Response Steps

1. **Acknowledge** the blocker via AI Maestro message to the reporting agent
2. **Record** the task's previous column BEFORE moving to Blocked (e.g., "In Progress", "AI Review", "Testing")
3. **Move** the task to the Blocked column on the Kanban board
4. **Update** labels: remove current `status:*`, add `status:blocked`
5. **Add comment** to the blocked task issue with blocker details and previous status
6. **Create a separate GitHub issue** for the blocker itself (labeled `type:blocker`, referencing the blocked task). This makes the blocking problem visible to all agents and team members on the issue tracker. Example:
   ```bash
   gh issue create --title "BLOCKER: Missing AWS credentials" --label "type:blocker" \
     --body "Blocking task #42. Category: Access/Credentials. What's needed: AWS credentials provisioned."
   ```
7. **Escalate** to EAMA IMMEDIATELY with blocker-escalation message (see eoa-messaging-templates). Include the blocker issue number.
   - Do NOT wait or "monitor for 24h first"
   - User must be informed immediately - they may have the solution ready
8. **Check** if any other unblocked tasks can be assigned to the waiting agent
9. **Monitor** for self-resolution while waiting for user response
10. **When resolved**, close the blocker issue and restore task to its PREVIOUS column (not always "In Progress")

### 7.2 Example Blocker Escalation Message

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "eoa-orchestrator",
  "to": "eama-assistant-manager",
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

### 7.3 Verification Before Escalation

Before escalating, verify the blocker is REAL:

| Check | Question | Action if False |
|-------|----------|-----------------|
| Cannot self-resolve | Can the agent solve this themselves? | Guide agent to solution, do not escalate |
| Not a knowledge gap | Is this a "how to" question? | Direct to documentation/skills, do not escalate |
| Not a process issue | Is this a team process the agent should follow? | Explain process, do not escalate |
| Truly blocking | Can work continue on other parts of the task? | Suggest parallel work, escalate only the blocking part |

Only escalate TRUE blockers that require user/architect intervention or resources the agent cannot access.

### 7.4 Checklist: Move Task to Blocked Column

Copy this checklist and track your progress:

- [ ] Verify the blocker is real (section 7.3 verification table)
- [ ] Acknowledge the blocker via AI Maestro to the reporting agent
- [ ] Record the task's current column/status BEFORE moving to Blocked
- [ ] Move the task to the Blocked column on the Kanban board
- [ ] Remove current `status:*` label, add `status:blocked`
- [ ] Add blocker details as comment on the blocked task issue (include `Previous status: $CURRENT_STATUS`)
- [ ] Create a separate GitHub issue for the blocker (`type:blocker` label, referencing the blocked task)
- [ ] Send blocker-escalation message to EAMA via AI Maestro using the `agent-messaging` skill (include `blocker_issue_number`)
- [ ] Check if other unblocked tasks can be assigned to the waiting agent

### 7.5 Checklist: Move Task Back to Original Column (Blocker Resolved)

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

---

## Instructions

Follow these steps to distribute tasks to agents:

1. Query all issues with `status:ready` label
2. Sort ready tasks by priority (critical > high > normal > low)
3. For each task in priority order:
   1. Check if dependencies are resolved (blockedBy list is empty)
   2. If blocked, skip to next task
   3. If ready, evaluate available agents for skill match
   4. Select agent with best match score and lowest current load
   5. Remove any existing `assign:*` label from the issue
   6. Add `assign:<agent-name>` label to the issue
   7. Update issue status from `status:ready` to `status:in-progress`
   8. Send task assignment message via AI Maestro using the `agent-messaging` skill (see section 3.2)
   9. Wait for agent ACK before considering next task
   10. Log assignment in delegation log file

### Checklist

Copy this checklist and track your progress:

**Task Distribution Workflow:**
- [ ] Query all issues with `status:ready` label
- [ ] Sort ready tasks by priority (critical > high > normal > low)
- [ ] Check if task dependencies are resolved (blockedBy list empty)
- [ ] If blocked, skip to next task
- [ ] Evaluate available agents for skill match
- [ ] Check agent availability (active, hibernated, offline)
- [ ] Check agent capacity (0-2 tasks acceptable, 3+ at capacity)
- [ ] Select agent with best match score and lowest load
- [ ] Remove any existing `assign:*` label from the issue
- [ ] Add `assign:<agent-name>` label to the issue
- [ ] Update issue status from `status:ready` to `status:in-progress`
- [ ] Send task assignment message via AI Maestro using the `agent-messaging` skill
- [ ] Wait for agent ACK before considering next task
- [ ] Log assignment in delegation log file

---

## Output

| Output Type | Format | Example |
|-------------|--------|---------|
| Assignment confirmation | GitHub label + AI Maestro message | `assign:implementer-1` label + ACK message received |
| Task queue report | Markdown table | List of ready tasks sorted by priority |
| Agent availability report | JSON | `{"agent": "impl-01", "load": 1, "state": "active"}` |
| Dependency graph | Text or diagram | Task A blocks [B, C], Task D ready |
| Delegation log entry | Timestamped text | `2024-01-15T10:30:00Z: Assigned #42 to implementer-1` |

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| No available agents | All agents at capacity or offline | Wait for agent capacity or escalate to user |
| Circular dependency detected | Task A blocks B, B blocks A | Report to user for manual resolution |
| Agent does not ACK assignment | Agent unresponsive or hibernated | Send reminder, then escalate to **eoa-progress-monitoring** |
| Skill mismatch | No agent has required toolchain | Escalate to user or reassign with training |
| Dependency never completes | Blocking task stuck | Escalate to **eoa-progress-monitoring** for blocker resolution |
| Label conflict (multiple assign:*) | Concurrent update | Remove all `assign:*` labels, reapply correct one |

---

## Examples

### Example 1: Query and Sort Ready Tasks

```bash
# Get all ready tasks as JSON
gh issue list --label "status:ready" --json number,title,labels,createdAt | \
  jq 'sort_by(
    .labels[] | select(.name | startswith("priority:")) | .name |
    if . == "priority:critical" then 0
    elif . == "priority:high" then 1
    elif . == "priority:normal" then 2
    else 3 end
  )'
```

### Example 2: Check Agent Availability via AI Maestro

Use the `ai-maestro-agents-management` skill to query agent availability:
- Query the agent registry for `implementer-1` to get their current task count
- Check the agent's last seen timestamp to determine if they are responsive

### Example 3: Assign Task with Full Protocol

```bash
ISSUE=42
AGENT="implementer-1"

# 1. Remove existing assignment
gh issue view $ISSUE --json labels | jq -r '.labels[] | select(.name | startswith("assign:")) | .name' | \
  xargs -I {} gh issue edit $ISSUE --remove-label "{}"

# 2. Add new assignment
gh issue edit $ISSUE --add-label "assign:$AGENT"

# 3. Update status
gh issue edit $ISSUE --remove-label "status:ready" --add-label "status:in-progress"

# 4. Send task assignment using the agent-messaging skill:
# - Recipient: $AGENT
# - Subject: "Task Assignment: Implement feature X"
# - Content: "You are assigned issue #$ISSUE. Success criteria: implement X, pass tests. Report when complete."
# - Type: request, Priority: high
# - Data: issue_number
# Verify: confirm message delivery
```

### Example 4: Handle Circular Dependency

```bash
# Detect circular dependency
TASK_A_BLOCKS=$(gh issue view 10 --json body | jq -r '.body | match("blocks: \\[([0-9, ]+)\\]") | .captures[0].string')
TASK_B_BLOCKS=$(gh issue view 11 --json body | jq -r '.body | match("blocks: \\[([0-9, ]+)\\]") | .captures[0].string')

# If A blocks B and B blocks A:
if echo "$TASK_A_BLOCKS" | grep -q "11" && echo "$TASK_B_BLOCKS" | grep -q "10"; then
  echo "CIRCULAR DEPENDENCY DETECTED: #10 ↔ #11"
  echo "User intervention required to break cycle."
  # Report to user via EAMA
fi
```

---

## Resources

- **AGENT_OPERATIONS.md** - Core orchestrator workflow
- **eoa-label-taxonomy** - Label categories and cardinality rules
- **eoa-messaging-templates** - Message templates for task assignment
- **eoa-progress-monitoring** - Agent state tracking and escalation
- **eoa-implementer-interview-protocol** - Pre-task and post-task verification
