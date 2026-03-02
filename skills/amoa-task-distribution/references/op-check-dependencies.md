# Operation: Check Task Dependencies

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-check-dependencies |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | Task Distribution |
| **Agent** | eoa-main |

## Purpose

Verify that a task's dependencies (blockedBy list) are all resolved before the task can be assigned to an agent.

## Preconditions

- Task has been identified for potential assignment
- Task body contains dependency information (blockedBy field)

## Dependency Types

| Type | Description | Handling |
|------|-------------|----------|
| Hard | Module B needs Module A's API | Block B until A complete |
| Soft | Testing can start with stubs | Assign with dependency note |
| None | Independent tasks | Assign immediately |

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `issue_number` | int | Yes | The task issue number |
| `repo` | string | Yes | Repository in `owner/repo` format |

## Procedure

1. Get the task issue body
2. Parse the `blockedBy` field from the body (expected format: `blockedBy: [10, 20, 30]`)
3. For each blocking issue number:
   - Check if the issue has `status:done` label
   - If ANY blocking issue is NOT done, task is blocked
4. Return blocking status

## Command

```bash
# Get task body and check blockedBy issues
ISSUE=42
BLOCKED_BY=$(gh issue view $ISSUE --json body | jq -r '.body | match("blockedBy: \\[([0-9, ]+)\\]") | .captures[0].string // ""')

if [ -n "$BLOCKED_BY" ]; then
  for BLOCKER in $(echo $BLOCKED_BY | tr ',' ' '); do
    STATUS=$(gh issue view $BLOCKER --json labels | jq -r '.labels[].name' | grep '^status:' | head -1)
    if [ "$STATUS" != "status:done" ]; then
      echo "BLOCKED by #$BLOCKER (status: $STATUS)"
      exit 1
    fi
  done
fi
echo "READY - no unresolved dependencies"
```

## Output

| Status | Meaning |
|--------|---------|
| READY | All dependencies resolved, can assign |
| BLOCKED | One or more dependencies unresolved |

## Circular Dependency Detection

If circular dependency is detected:

```
CIRCULAR DEPENDENCY:
Task A -> depends on -> Task B
Task B -> depends on -> Task A

Cannot proceed. User decision required.
```

**Action:** Stop processing and escalate to user immediately.

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Circular dependency | Tasks block each other | Escalate to user for resolution |
| Missing blockedBy | No dependency field in body | Treat as no dependencies |
| Blocker issue not found | Invalid issue reference | Log warning, continue checking others |

## Related Operations

- [op-sort-tasks-by-priority.md](op-sort-tasks-by-priority.md) - Sorting before dependency check
- [op-select-agent.md](op-select-agent.md) - Next step if dependencies resolved
