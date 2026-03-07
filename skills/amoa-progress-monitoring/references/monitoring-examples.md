## Table of Contents

- [Query Agent State via AI Maestro](#example-1-query-agent-state-via-ai-maestro)
- [Send First Reminder](#example-2-send-first-reminder)
- [Escalate to Urgent](#example-3-escalate-to-urgent)
- [Handle Blocker Report](#example-4-handle-blocker-report)
- [Verify Completion](#example-5-verify-completion)
- [Dashboard Queries](#dashboard-queries)
- [Error Handling](#error-handling)

---

## Example 1: Query Agent State via AI Maestro

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

## Example 2: Send First Reminder

Send a status request using the `agent-messaging` skill:
- **Recipient**: `implementer-1`
- **Subject**: "Status Request: #42"
- **Content**: "What is your current status on #42? Report progress, blockers, and next steps."
- **Type**: `request`, **Priority**: `normal`
- **Data**: include `task_id: 42`

**Verify**: confirm message delivery.

## Example 3: Escalate to Urgent

Send an urgent escalation using the `agent-messaging` skill:
- **Recipient**: `implementer-1`
- **Subject**: "URGENT: #42 - Response Required"
- **Content**: "No response received. Please provide status immediately or task may be reassigned."
- **Type**: `escalation`, **Priority**: `urgent`
- **Data**: include `task_id: 42`, `escalation_level: 2`

**Verify**: confirm message delivery.

## Example 4: Handle Blocker Report

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

## Example 5: Verify Completion

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

## Dashboard Queries

Track all active tasks:

| Task | Agent | State | Last Update | Priority |
|------|-------|-------|-------------|----------|
| #42 | impl-01 | Active | Recent | High |
| #43 | impl-02 | No Progress | Stale | Normal |
| #44 | reviewer | Blocked | Recent | High |

```bash
# All in-progress tasks
gh issue list --label "status:in-progress" --json number,title,labels

# Blocked tasks
gh issue list --label "status:blocked" --json number,title,labels

# Tasks by agent
gh issue list --label "assign:impl-01" --json number,title,labels
```

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Agent never ACKs | Agent offline, hibernated, or unaware | Send reminder, escalate to AMCOS if no response |
| Agent stops responding mid-task | Agent crashed, hibernated, or blocked | Follow escalation order (sections 3.1-3.3) |
| Blocker reported but not resolved | Dependency on external event | Coordinate with other agents or escalate to user |
| Completion reported but verification fails | Missing tests, failing CI, or incomplete requirements | Send REVISE message (see **amoa-implementer-interview-protocol**) |
| Multiple agents updating same task | Concurrent work or reassignment conflict | Check `assign:*` label, coordinate via AI Maestro |
| Stale state but agent actually hibernated | Normal hibernation, not a failure | Distinguish hibernation from unresponsiveness via AMCOS |
