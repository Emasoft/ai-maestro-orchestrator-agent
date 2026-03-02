---
procedure: support-skill
workflow-instruction: support
---

# Operation: Check Orchestrator Loop Status


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Execute Status Command](#step-1-execute-status-command)
  - [Step 2: Interpret Loop Status](#step-2-interpret-loop-status)
- [Orchestrator Loop Status](#orchestrator-loop-status)
  - [Step 3: Review Task Sources](#step-3-review-task-sources)
- [Task Sources](#task-sources)
  - [Step 4: View Current Task](#step-4-view-current-task)
- [Current Task](#current-task)
  - [Step 5: Check Verification State](#step-5-check-verification-state)
- [Verification Status](#verification-status)
  - [Step 6: Review Debug Info (Verbose)](#step-6-review-debug-info-verbose)
- [Debug Information](#debug-information)
  - [Step 7: Understand Blocking Behavior](#step-7-understand-blocking-behavior)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example](#example)
- [Checklist](#checklist)

## When to Use

Use this operation to check the status of the orchestrator loop, which monitors tasks across multiple sources.

## Prerequisites

- Orchestrator loop started (`/orchestrator-loop` executed)
- Loop state file exists at `design/state/loop.md`

## Procedure

### Step 1: Execute Status Command

```bash
# Basic status
/orchestrator-status

# With verbose debug info
/orchestrator-status --verbose
```

### Step 2: Interpret Loop Status

```markdown
## Orchestrator Loop Status

**Status**: ACTIVE
**Iteration**: 23 of 100
**Started**: 2024-01-15T10:00:00Z
**Last Check**: 2 minutes ago
```

| Status | Meaning |
|--------|---------|
| `ACTIVE` | Loop is running and checking tasks |
| `INACTIVE` | No loop running |
| `COMPLETING` | All tasks done, in verification phase |
| `CANCELLED` | Loop was manually cancelled |

### Step 3: Review Task Sources

```markdown
## Task Sources

| Source | Pending | Checked At |
|--------|---------|------------|
| Claude Tasks | 3 | 2 min ago |
| GitHub Projects | 5 | 2 min ago |
| Task File | 2 | 2 min ago |
| TODO List | 0 | 2 min ago |
| **Total** | **10** | |
```

Task sources monitored:
- **Claude Tasks**: Via TaskList API
- **GitHub Projects**: Open items on Kanban board
- **Task File**: Markdown checklist (e.g., `TASKS.md`)
- **TODO List**: Claude session TODO items

### Step 4: View Current Task

```markdown
## Current Task

**Source**: GitHub Projects
**ID**: PVTI_lADOBxxxxxxx
**Title**: Implement JWT validation
**Priority**: high
**Assigned**: implementer-1
```

### Step 5: Check Verification State

```markdown
## Verification Status

**Mode**: VERIFICATION
**Loop**: 2 of 4
**Reason**: All tasks complete, running verification loops
```

The orchestrator requires 4 verification loops after all tasks show complete:
- Loop 1: Initial verification
- Loop 2: Double-check
- Loop 3: Edge case review
- Loop 4: Final confirmation

### Step 6: Review Debug Info (Verbose)

With `--verbose`:

```markdown
## Debug Information

**Log File**: orchestrator-loop.log
**Lock File**: .claude/orchestrator.lock (active)
**State File**: design/state/loop.md

**Recent Log Entries**:
```
14:30:15 Checking Claude Tasks... found 3 pending
14:30:16 Checking GitHub Projects... found 5 open items
14:30:17 Total pending: 10, continuing loop
```
```

### Step 7: Understand Blocking Behavior

When the stop hook fires:
- If tasks pending: Loop continues, stop blocked
- If in verification: Must complete 4 loops
- If all verified: `ALL_TASKS_COMPLETE` output, stop allowed

## Output

| Field | Type | Description |
|-------|------|-------------|
| Loop Status | String | ACTIVE, INACTIVE, etc. |
| Iteration | Number | Current iteration count |
| Pending Tasks | Number | Total pending across all sources |
| Current Task | Object | Details of current task |
| Verification Loop | Number | 1-4 if in verification mode |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "No loop active" | Loop not started or completed | Run `/orchestrator-loop` |
| "State file missing" | File deleted | Check design/state/loop.md |
| "Stale lock file" | Previous crash | Delete .claude/orchestrator.lock |
| "Cannot check tasks" | API failure | Check connectivity |

## Example

```bash
# Complete orchestrator status check

# 1. Quick status
/orchestrator-status

# Output:
# Orchestrator Loop: ACTIVE
# Iteration: 23/100
# Pending Tasks: 10
#   - Claude Tasks: 3
#   - GitHub Projects: 5
#   - Task File: 2
#   - TODO List: 0

# 2. If issues, get debug info
/orchestrator-status --verbose

# 3. Common actions based on status:
# - If stuck at high iteration: Check for blocking issue
# - If pending count not decreasing: Verify agents working
# - If in verification but failing: Check what changed
```

## Checklist

- [ ] Run `/orchestrator-status` command
- [ ] Check loop status (ACTIVE/INACTIVE)
- [ ] Review iteration count vs max
- [ ] Check pending task count per source
- [ ] Verify current task assignment
- [ ] Check verification loop status (if completing)
- [ ] Review debug info if issues found
- [ ] Take action on any blockers
