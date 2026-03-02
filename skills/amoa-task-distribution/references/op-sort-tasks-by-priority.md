# Operation: Sort Tasks by Priority

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-sort-tasks-by-priority |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | Task Distribution |
| **Agent** | eoa-main |

## Purpose

Sort a list of ready tasks by priority label to ensure critical tasks are distributed first.

## Preconditions

- Tasks have been queried (see op-query-ready-tasks)
- Tasks have priority labels following the taxonomy

## Priority Order

| Priority | Label | Sort Order |
|----------|-------|------------|
| Critical | `priority:critical` | 0 (highest) |
| High | `priority:high` | 1 |
| Normal | `priority:normal` | 2 |
| Low | `priority:low` | 3 (lowest) |

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tasks_json` | JSON array | Yes | Array of task objects from gh issue list |

## Procedure

1. Parse the JSON array of tasks
2. Extract priority label from each task's labels array
3. Map priority labels to sort order numbers
4. Sort tasks by sort order (ascending)
5. Return sorted array

## Command

```bash
# Sort using jq
gh issue list --label "status:ready" --json number,title,labels,createdAt | \
  jq 'sort_by(
    .labels[] | select(.name | startswith("priority:")) | .name |
    if . == "priority:critical" then 0
    elif . == "priority:high" then 1
    elif . == "priority:normal" then 2
    else 3 end
  )'
```

## Output

Sorted JSON array with highest priority tasks first.

```json
[
  {"number": 10, "title": "Critical bug", "labels": [{"name": "priority:critical"}]},
  {"number": 20, "title": "High priority", "labels": [{"name": "priority:high"}]},
  {"number": 30, "title": "Normal task", "labels": [{"name": "priority:normal"}]}
]
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Missing priority | Task has no priority label | Treat as lowest priority |
| Multiple priorities | Task has multiple priority labels | Use highest priority found |

## Related Operations

- [op-query-ready-tasks.md](op-query-ready-tasks.md) - Get tasks to sort
- [op-check-dependencies.md](op-check-dependencies.md) - Next step after sorting
