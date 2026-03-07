## Table of Contents
- [Query and Sort Ready Tasks](#example-1-query-and-sort-ready-tasks)
- [Check Agent Availability](#example-2-check-agent-availability-via-ai-maestro)
- [Assign Task with Full Protocol](#example-3-assign-task-with-full-protocol)
- [Handle Circular Dependency](#example-4-handle-circular-dependency)

---

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

Use the `agent-messaging` skill to query agent availability:
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
  echo "CIRCULAR DEPENDENCY DETECTED: #10 <-> #11"
  echo "User intervention required to break cycle."
  # Report to user via AMAMA
fi
```
