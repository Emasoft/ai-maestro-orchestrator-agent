---
procedure: proc-execute-task
workflow-instruction: Step 17 - Task Execution
operation: query-progress-dashboard
---

# Operation: Query Progress Dashboard


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Steps](#steps)
  - [Step 1: Query All In-Progress Tasks](#step-1-query-all-in-progress-tasks)
  - [Step 2: Query Blocked Tasks](#step-2-query-blocked-tasks)
  - [Step 3: Get Agent Assignments](#step-3-get-agent-assignments)
  - [Step 4: Calculate Task Staleness](#step-4-calculate-task-staleness)
  - [Step 5: Query Agent Message Activity](#step-5-query-agent-message-activity)
  - [Step 6: Generate Dashboard Table](#step-6-generate-dashboard-table)
- [Progress Dashboard](#progress-dashboard)
  - [Summary](#summary)
  - [Active Tasks](#active-tasks)
- [Dashboard Output Format](#dashboard-output-format)
- [Progress Dashboard](#progress-dashboard)
  - [Summary](#summary)
  - [Active Tasks](#active-tasks)
  - [Blocked Tasks](#blocked-tasks)
  - [Agent Status](#agent-status)
- [Success Criteria](#success-criteria)
- [Use Cases](#use-cases)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Generate a comprehensive view of all active tasks, agent states, and progress metrics.

## When to Use

- During monitoring cycles
- When user requests status overview
- Before daily handoffs
- When checking system health

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| filter_status | Status label to filter by | No |
| filter_agent | Agent name to filter by | No |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| dashboard_table | Markdown | Formatted status table |
| blocked_count | Integer | Number of blocked tasks |
| stale_count | Integer | Tasks needing attention |

## Steps

### Step 1: Query All In-Progress Tasks

```bash
# Get all tasks with in-progress status
IN_PROGRESS=$(gh issue list --label "status:in-progress" --json number,title,labels,updatedAt | \
  jq -r '.[] | {number, title, labels: [.labels[].name], updated: .updatedAt}')

echo "In-progress tasks:"
echo "$IN_PROGRESS"
```

### Step 2: Query Blocked Tasks

```bash
# Get all blocked tasks
BLOCKED=$(gh issue list --label "status:blocked" --json number,title,labels,updatedAt | \
  jq -r '.[] | {number, title, labels: [.labels[].name], updated: .updatedAt}')

BLOCKED_COUNT=$(echo "$BLOCKED" | jq -s 'length')
echo "Blocked tasks: $BLOCKED_COUNT"
```

### Step 3: Get Agent Assignments

```bash
# Get all assigned tasks grouped by agent
ASSIGNMENTS=$(gh issue list --search "label:assign:" --json number,title,labels | \
  jq -r '.[] | {
    number,
    title,
    agent: (.labels[] | select(.name | startswith("assign:")) | .name | sub("assign:"; "")),
    status: (.labels[] | select(.name | startswith("status:")) | .name | sub("status:"; ""))
  }')

echo "Assignments:"
echo "$ASSIGNMENTS" | jq -s 'group_by(.agent) | .[] | {agent: .[0].agent, tasks: [.[].number]}'
```

### Step 4: Calculate Task Staleness

```bash
# Check which tasks have stale updates (>2 hours)
CURRENT_TIME=$(date +%s)

STALE_TASKS=()
echo "$IN_PROGRESS" | jq -c '.' | while read -r task; do
  TASK_NUM=$(echo "$task" | jq -r '.number')
  UPDATED=$(echo "$task" | jq -r '.updated')
  UPDATED_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${UPDATED%.*}" +%s 2>/dev/null || echo 0)
  HOURS_AGO=$(( ($CURRENT_TIME - $UPDATED_EPOCH) / 3600 ))

  if [ "$HOURS_AGO" -gt 2 ]; then
    STALE_TASKS+=("$TASK_NUM")
  fi
done

STALE_COUNT=${#STALE_TASKS[@]}
echo "Stale tasks (>2h): $STALE_COUNT"
```

### Step 5: Query Agent Message Activity

```bash
# Use the agent-messaging skill to retrieve recent messages (last 50)
# from the orchestrator's inbox, then group by sender to produce
# per-agent activity counts and last-seen timestamps
RECENT_MESSAGES=$(# retrieve and group messages by agent)

echo "Agent activity:"
echo "$RECENT_MESSAGES"
```

### Step 6: Generate Dashboard Table

```bash
cat << 'EOF'
## Progress Dashboard

Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)

### Summary
| Metric | Count |
|--------|-------|
| In Progress | $IN_PROGRESS_COUNT |
| Blocked | $BLOCKED_COUNT |
| Stale (>2h) | $STALE_COUNT |
| Ready | $READY_COUNT |
| Done (today) | $DONE_TODAY |

### Active Tasks

| Task | Agent | State | Last Update | Priority |
|------|-------|-------|-------------|----------|
EOF

# Generate table rows
echo "$IN_PROGRESS" | jq -c '.' | while read -r task; do
  TASK_NUM=$(echo "$task" | jq -r '.number')
  TASK_TITLE=$(echo "$task" | jq -r '.title' | cut -c1-40)
  AGENT=$(echo "$task" | jq -r '.labels[] | select(startswith("assign:"))' | sed 's/assign://' | head -1)
  STATUS=$(echo "$task" | jq -r '.labels[] | select(startswith("status:"))' | sed 's/status://' | head -1)
  UPDATED=$(echo "$task" | jq -r '.updated')

  # Determine state based on op-detect-agent-state logic
  STATE="Active"  # Simplified - full logic in op-detect-agent-state

  PRIORITY=$(echo "$task" | jq -r '.labels[] | select(startswith("priority:"))' | sed 's/priority://' | head -1)
  [ -z "$PRIORITY" ] && PRIORITY="Normal"

  echo "| #$TASK_NUM $TASK_TITLE | $AGENT | $STATE | $UPDATED | $PRIORITY |"
done

# Add blocked tasks
echo ""
echo "### Blocked Tasks"
echo ""
echo "| Task | Agent | Blocker | Blocked Since |"
echo "|------|-------|---------|---------------|"

echo "$BLOCKED" | jq -c '.' | while read -r task; do
  TASK_NUM=$(echo "$task" | jq -r '.number')
  TASK_TITLE=$(echo "$task" | jq -r '.title' | cut -c1-30)
  AGENT=$(echo "$task" | jq -r '.labels[] | select(startswith("assign:"))' | sed 's/assign://' | head -1)
  UPDATED=$(echo "$task" | jq -r '.updated')

  # Get blocker info from comments
  BLOCKER_INFO=$(gh issue view $TASK_NUM --json comments | jq -r '.comments[] | select(.body | contains("BLOCKED:")) | .body' | head -1 | cut -c1-40)

  echo "| #$TASK_NUM | $AGENT | $BLOCKER_INFO | $UPDATED |"
done
```

## Dashboard Output Format

```markdown
## Progress Dashboard

Generated: 2024-01-15T10:30:00Z

### Summary
| Metric | Count |
|--------|-------|
| In Progress | 5 |
| Blocked | 2 |
| Stale (>2h) | 1 |
| Ready | 3 |
| Done (today) | 4 |

### Active Tasks

| Task | Agent | State | Last Update | Priority |
|------|-------|-------|-------------|----------|
| #42 Implement auth | impl-01 | Active | 1h ago | High |
| #43 Add logging | impl-02 | No Progress | 3h ago | Normal |
| #45 Update docs | docs-01 | Active | 30m ago | Low |

### Blocked Tasks

| Task | Agent | Blocker | Blocked Since |
|------|-------|---------|---------------|
| #44 Deploy | impl-01 | Waiting on #38 | 2024-01-15 |
| #46 API test | test-01 | Missing API key | 2024-01-14 |

### Agent Status

| Agent | Active Tasks | Last Seen | State |
|-------|--------------|-----------|-------|
| impl-01 | 2 | 1h ago | Active |
| impl-02 | 1 | 3h ago | Stale |
| test-01 | 1 | 2h ago | Blocked |
```

## Success Criteria

- [ ] All in-progress tasks queried
- [ ] Blocked tasks identified
- [ ] Stale tasks flagged
- [ ] Agent activity checked
- [ ] Dashboard table generated

## Use Cases

| Scenario | Focus On |
|----------|----------|
| Morning standup | Full dashboard |
| Check specific agent | Filter by agent |
| Find stale work | Stale and blocked sections |
| Before overnight | All active tasks, blocker status |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| No tasks found | All work complete or labels missing | Verify label usage |
| Agent activity missing | AI Maestro unavailable | Query GitHub comments instead |
| Stale calculation wrong | Timezone issue | Use UTC timestamps |

## Related Operations

- op-detect-agent-state
- op-poll-agent-progress (in remote-agent-coordinator skill)
