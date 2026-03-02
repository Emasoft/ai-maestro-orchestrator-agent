# Status Update Template

## Purpose

This template shows remote agents the EXACT format for sending progress updates during long-running tasks.

---

## When to Send Updates

| Situation | Required? |
|-----------|-----------|
| Reaching a checkpoint defined in task | YES |
| Every 30 minutes for long tasks | YES |
| Encountering a blocker | YES (immediately) |
| Completing a major subtask | YES |
| Making routine progress | NO (only if relevant) |

---

## Required Format

```
[PROGRESS] {TASK_ID} - Checkpoint {N}: {checkpoint_name}

Status: {ACTIVE | BLOCKED | PAUSED}
Progress: {percentage}% complete
Current: {what you just finished}
Next: {what you will do next}
```

---

## Examples

### Example 1: Regular Progress Update

```
[PROGRESS] GH-42-auth - Checkpoint 2: Implementation Complete

Status: ACTIVE
Progress: 60% complete
Current: Finished JWT token generation and validation
Next: Implementing refresh token rotation
```

### Example 2: Blocked Progress

```
[PROGRESS] GH-42-auth - Checkpoint 2: Blocked

Status: BLOCKED
Progress: 40% complete
Current: JWT generation works
Blocker: Database connection failing - need credentials
Next: Cannot proceed until blocker resolved

Action Needed: Please provide database credentials or check DB status
```

### Example 3: Completing Checkpoint

```
[PROGRESS] GH-42-auth - Checkpoint 3: Tests Written

Status: ACTIVE
Progress: 80% complete
Current: All unit tests passing (15/15)
Next: Creating PR and documentation
```

---

## Checkpoint Naming Convention

Use the checkpoint names from the original task delegation:

| Checkpoint | Description |
|------------|-------------|
| Checkpoint 1 | Research/Planning complete |
| Checkpoint 2 | Implementation complete |
| Checkpoint 3 | Tests written |
| Checkpoint 4 | PR created |
| Checkpoint 5 | Documentation updated |

---

## Status Values

| Status | Meaning | Orchestrator Action |
|--------|---------|---------------------|
| `ACTIVE` | Working normally | No action needed |
| `BLOCKED` | Cannot proceed | Must resolve blocker |
| `PAUSED` | Temporarily stopped | Acknowledge pause |
| `RESUMING` | Continuing after pause | No action needed |

---

## Blocker Report Format

When blocked, include additional details:

```
[PROGRESS] {TASK_ID} - BLOCKED

Status: BLOCKED
Progress: {percentage}% complete
Current: {last successful step}

## Blocker Details
Type: {DEPENDENCY | RESOURCE | CLARIFICATION | ERROR}
Description: {what is blocking you}
Attempted: {what you tried to resolve it}
Need: {what you need from orchestrator}

## Options
1. {option 1 with tradeoffs}
2. {option 2 with tradeoffs}
3. Wait for {dependency/resource}
```

---

## Long-Running Task Updates

For tasks expected to take more than 1 hour:

```
[PROGRESS] {TASK_ID} - Hourly Update

Status: ACTIVE
Progress: {percentage}% complete
Time Elapsed: {hours}h {minutes}m
Estimated Remaining: {hours}h {minutes}m

## Completed Since Last Update
- {item 1}
- {item 2}

## In Progress
- {current work}

## Upcoming
- {next items}

No blockers. Proceeding as planned.
```

---

## Common Mistakes to Avoid

| Wrong | Correct |
|-------|---------|
| No updates for hours | Send update every 30 min |
| `Still working on it` | Include specific progress % |
| Blocking without immediate report | Report blockers ASAP |
| Vague status | Specific checkpoint + % |

---

## If Orchestrator Asks for Status

Reply immediately with current state:

```
[STATUS] {TASK_ID}

Current Checkpoint: {N} - {name}
Progress: {percentage}% complete
Status: {ACTIVE | BLOCKED | PAUSED}
Last Action: {what you just did}
Next Action: {what you will do next}
```
