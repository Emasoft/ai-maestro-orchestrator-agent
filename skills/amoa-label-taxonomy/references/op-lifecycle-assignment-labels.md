---
procedure: support-skill
workflow-instruction: support
---

# Operation: Set Labels During Assignment


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Verify Issue is Ready](#step-1-verify-issue-is-ready)
  - [Step 2: Verify No Existing Assignment](#step-2-verify-no-existing-assignment)
  - [Step 3: Determine Agent ID](#step-3-determine-agent-id)
  - [Step 4: Apply Assignment Labels](#step-4-apply-assignment-labels)
  - [Step 5: Notify Agent (if using AI Maestro)](#step-5-notify-agent-if-using-ai-maestro)
  - [Step 6: Add Assignment Comment](#step-6-add-assignment-comment)
- [Output](#output)
- [Error Handling](#error-handling)
- [Examples](#examples)
  - [Example 1: Standard Assignment](#example-1-standard-assignment)
  - [Example 2: Assignment with Full Notification](#example-2-assignment-with-full-notification)
  - [Example 3: Reassignment](#example-3-reassignment)
- [Checklist](#checklist)

## When to Use

Use this operation when assigning an issue to an agent for implementation.

## Prerequisites

- Issue is in `status:ready` state
- Issue has been triaged (has priority, effort, type, component)
- Agent is registered and available
- GitHub CLI (`gh`) authenticated

## Procedure

### Step 1: Verify Issue is Ready

```bash
# Check current labels
gh issue view <ISSUE_NUM> --json labels --jq '.labels[].name'

# Must have:
# - status:ready
# - priority:*
# - effort:*
# - type:*
```

### Step 2: Verify No Existing Assignment

```bash
# Check for assign: label
gh issue view <ISSUE_NUM> --json labels --jq '[.labels[].name | select(startswith("assign:"))]'

# Should return empty array []
```

### Step 3: Determine Agent ID

Agent IDs follow the pattern: `<role>-<number>`

| Agent Type | ID Pattern |
|------------|------------|
| AI Implementer | `implementer-1`, `implementer-2` |
| Human Developer | `dev-alice`, `dev-bob` |
| Reviewer | `reviewer-1` |

### Step 4: Apply Assignment Labels

```bash
# Assign and update status in single command
gh issue edit <ISSUE_NUM> \
  --remove-label "status:ready" \
  --add-label "assign:<agent-id>,status:in-progress"
```

### Step 5: Notify Agent (if using AI Maestro)

Send an assignment notification using the `agent-messaging` skill:
- **Recipient**: the agent session name
- **Subject**: "Task Assignment: Issue #<ISSUE_NUM>"
- **Content**: "You have been assigned issue #<ISSUE_NUM>: <TITLE>"
- **Type**: `task_assignment`, **Priority**: `high`

**Verify**: confirm message delivery.

### Step 6: Add Assignment Comment

```bash
gh issue comment <ISSUE_NUM> --body "**Assigned to <agent-id>**
- Status changed: ready -> in-progress
- Agent session: <session-name>
- Assignment time: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| Assignment Label | String | `assign:<agent-id>` |
| Status Change | String | `status:ready` -> `status:in-progress` |
| Notification | Boolean | Whether agent was notified |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Already assigned | Issue has `assign:*` label | Use reassignment procedure instead |
| Not ready | Issue not in `status:ready` | Complete triage first |
| Agent unavailable | Agent session not responding | Choose different agent or wait |

## Examples

### Example 1: Standard Assignment

```bash
# Assign issue 42 to implementer-1
gh issue edit 42 \
  --remove-label "status:ready" \
  --add-label "assign:implementer-1,status:in-progress"
```

### Example 2: Assignment with Full Notification

```bash
# Assign and notify
gh issue edit 42 \
  --remove-label "status:ready" \
  --add-label "assign:implementer-1,status:in-progress"

gh issue comment 42 --body "**Assigned to implementer-1**
- Priority: high
- Effort: m (4-8 hours)
- Acceptance criteria in issue description"

# Notify via AI Maestro using the agent-messaging skill:
# - Recipient: helper-agent-generic
# - Subject: "Task Assignment: Issue #42"
# - Content: "Assigned: Implement auth module (issue #42)"
# - Type: task_assignment, Priority: high
```

### Example 3: Reassignment

```bash
# Remove old assignment, add new
gh issue edit 42 \
  --remove-label "assign:implementer-1" \
  --add-label "assign:implementer-2"

gh issue comment 42 --body "**Reassigned from implementer-1 to implementer-2**
- Reason: Context loss recovery
- Work continues from previous progress"
```

## Checklist

- [ ] Verify issue has `status:ready`
- [ ] Verify issue has priority, effort, type labels
- [ ] Verify no existing `assign:*` label
- [ ] Identify target agent
- [ ] Remove `status:ready`
- [ ] Add `assign:<agent>` and `status:in-progress`
- [ ] Add assignment comment to issue
- [ ] Notify agent via AI Maestro (if applicable)
- [ ] Update orchestrator state file
