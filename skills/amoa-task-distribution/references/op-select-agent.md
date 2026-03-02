# Operation: Select Agent for Task


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Preconditions](#preconditions)
- [Selection Criteria (Evaluation Order)](#selection-criteria-evaluation-order)
  - [1. Availability Check](#1-availability-check)
  - [2. Skill Match](#2-skill-match)
  - [3. Capacity Check](#3-capacity-check)
- [Input](#input)
- [Procedure](#procedure)
- [Command](#command)
- [Output](#output)
- [Specialization Preferences](#specialization-preferences)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-select-agent |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | Task Distribution |
| **Agent** | eoa-main |

## Purpose

Select the best available agent to handle a task based on availability, skills match, and current workload.

## Preconditions

- Task is ready (dependencies resolved)
- At least one agent is available
- Agent skills registry is accessible

## Selection Criteria (Evaluation Order)

### 1. Availability Check

| State | Can Assign | Action |
|-------|------------|--------|
| Active, no current task | Yes | Assign immediately |
| Active, has current task | Maybe | Check if at capacity |
| Hibernated | No | Wake first or select different agent |
| Offline | No | Select different agent |

### 2. Skill Match

Match task requirements (`toolchain:*`, `component:*` labels) to agent capabilities.

```
Task labels: toolchain:python, component:api
Agent skills: python, api, testing

Match score: 2/2 required = 100% match
```

### 3. Capacity Check

| Agent Load | Can Assign |
|------------|------------|
| 0 active tasks | Yes |
| 1-2 active tasks | Yes, if high priority |
| 3+ active tasks | No, agent at capacity |

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_labels` | array | Yes | Task's toolchain/component labels |
| `agents` | array | Yes | List of available agents with skills |

## Procedure

1. Filter agents by availability (exclude hibernated/offline)
2. For each available agent:
   - Calculate skill match score
   - Get current task count
3. Sort agents by:
   - Skill match score (descending)
   - Current load (ascending)
4. Select top agent
5. If no suitable agent, return error

## Command

Use the `ai-maestro-agents-management` skill to query agent availability:
- Query agent registry for `implementer-1` to get their active task count and last seen timestamp
- If the agent has fewer than 3 active tasks, they are available
- If they have 3 or more, they are at capacity

## Output

```json
{
  "selected_agent": "implementer-1",
  "match_score": 0.85,
  "current_load": 1,
  "reason": "Best skill match with available capacity"
}
```

## Specialization Preferences

| Task Type | Preferred Agent |
|-----------|-----------------|
| Code review | Agent who wrote the code (context) |
| Bug fix | Agent who implemented feature |
| New feature | Agent with matching skills |

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| No available agents | All agents at capacity/offline | Wait for capacity or escalate to user |
| No skill match | No agent has required skills | Escalate to user for training/reassignment |

## Related Operations

- [op-check-dependencies.md](op-check-dependencies.md) - Previous step
- [op-assign-task.md](op-assign-task.md) - Next step after selection
