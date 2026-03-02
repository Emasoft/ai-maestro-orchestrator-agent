# Operation: Query Ready Tasks

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-query-ready-tasks |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | Task Distribution |
| **Agent** | eoa-main |

## Purpose

Query all GitHub issues that have the `status:ready` label, indicating they are ready to be assigned to agents.

## Preconditions

- GitHub CLI (`gh`) is authenticated
- Repository access is available
- Labels follow the standard taxonomy (`status:ready`)

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo` | string | Yes | Repository in `owner/repo` format |

## Procedure

1. Use `gh issue list` to query issues with `status:ready` label
2. Output as JSON for further processing
3. Return issue numbers, titles, and labels

## Command

```bash
gh issue list --label "status:ready" --json number,title,labels,createdAt
```

## Output

```json
[
  {
    "number": 42,
    "title": "Implement feature X",
    "labels": [
      {"name": "status:ready"},
      {"name": "priority:high"},
      {"name": "type:feature"}
    ],
    "createdAt": "2024-01-15T10:00:00Z"
  }
]
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Empty result | No ready tasks | Normal - no tasks to assign |
| Auth error | gh not authenticated | Run `gh auth login` |
| Repo not found | Invalid repo path | Verify repository exists |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (may return empty list) |
| 1 | CLI error |

## Related Operations

- [op-sort-tasks-by-priority.md](op-sort-tasks-by-priority.md) - Sort the queried tasks
- [op-check-dependencies.md](op-check-dependencies.md) - Check task dependencies
