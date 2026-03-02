---
procedure: support-skill
workflow-instruction: support
---

# Operation: Monitor Orchestration Status


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Execute Status Command](#step-1-execute-status-command)
  - [Step 2: Interpret Phase Status Header](#step-2-interpret-phase-status-header)
- [Orchestration Status](#orchestration-status)
  - [Step 3: Read Module Status Table](#step-3-read-module-status-table)
- [Module Status](#module-status)
  - [Step 4: Review Agent Registry](#step-4-review-agent-registry)
- [Agent Registry](#agent-registry)
  - [Step 5: Check Active Assignments](#step-5-check-active-assignments)
- [Active Assignments](#active-assignments)
  - [Step 6: Review Polling History (Verbose)](#step-6-review-polling-history-verbose)
- [Polling History](#polling-history)
  - [Step 7: Identify Issues](#step-7-identify-issues)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example](#example)
- [Checklist](#checklist)

## When to Use

Use this operation to check the current state of the orchestration phase, including module progress and agent assignments.

## Prerequisites

- Orchestration phase started (`/start-orchestration` executed)
- State file exists at `design/state/exec-phase.md`

## Procedure

### Step 1: Execute Status Command

```bash
# Basic status
/orchestration-status

# With verbose output
/orchestration-status --verbose

# Agents only
/orchestration-status --agents-only

# Modules only
/orchestration-status --modules-only
```

### Step 2: Interpret Phase Status Header

```markdown
## Orchestration Status

**Plan ID**: plan-20240115
**Status**: executing
**Started**: 2024-01-15T10:00:00Z
**Progress**: 35% (7/20 tasks complete)
```

| Status | Meaning |
|--------|---------|
| `executing` | Active orchestration in progress |
| `paused` | Temporarily halted (manual pause) |
| `blocked` | Waiting on external dependency |
| `completing` | All tasks done, running verification |
| `complete` | Orchestration finished successfully |

### Step 3: Read Module Status Table

```markdown
## Module Status

| Module | Status | Assigned | Progress | Last Update |
|--------|--------|----------|----------|-------------|
| auth-core | in-progress | implementer-1 | 70% | 5 min ago |
| api-routes | ready | - | 0% | - |
| user-model | blocked | implementer-2 | 30% | 20 min ago |
| tests | pending | - | 0% | - |
```

| Status | Meaning |
|--------|---------|
| `pending` | Not yet started |
| `ready` | Available for assignment |
| `in-progress` | Actively being worked on |
| `blocked` | Waiting on dependency |
| `review` | Awaiting code review |
| `complete` | Finished and verified |

### Step 4: Review Agent Registry

```markdown
## Agent Registry

| Agent ID | Type | Session | Status | Current Task |
|----------|------|---------|--------|--------------|
| implementer-1 | AI | helper-agent-generic | active | auth-core |
| implementer-2 | AI | helper-agent-generic-2 | blocked | user-model |
| reviewer-1 | Human | - | idle | - |
```

### Step 5: Check Active Assignments

```markdown
## Active Assignments

| Agent | Module | Issue | Started | IVP Status |
|-------|--------|-------|---------|------------|
| implementer-1 | auth-core | #42 | 2h ago | verified |
| implementer-2 | user-model | #45 | 30m ago | pending |
```

IVP Status (Instruction Verification Protocol):
- `pending` - Not yet verified
- `verified` - Agent confirmed understanding
- `clarification-needed` - Questions pending

### Step 6: Review Polling History (Verbose)

With `--verbose`:

```markdown
## Polling History

| Time | Agent | Response | Action |
|------|-------|----------|--------|
| 14:30 | implementer-1 | "70% complete" | Continue |
| 14:15 | implementer-2 | "Blocked on #38" | Notify |
| 14:00 | implementer-1 | "Tests passing" | Continue |
```

### Step 7: Identify Issues

Look for:
- Agents stuck (no progress for 30+ minutes)
- Blocked modules (dependencies not met)
- Missing assignments (ready modules without agents)
- Failed IVP (agent doesn't understand task)

## Output

| Field | Type | Description |
|-------|------|-------------|
| Phase Status | String | Current orchestration state |
| Module Table | Markdown | All modules with status |
| Agent Table | Markdown | All agents with status |
| Progress | Percentage | Overall completion |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "No orchestration active" | Not started | Run `/start-orchestration` |
| "State file not found" | File deleted or wrong path | Check design/state/ |
| "Cannot parse state" | Corrupted file | Reset from backup |

## Example

```bash
# Complete monitoring sequence

# 1. Quick status check
/orchestration-status

# 2. If issues detected, get details
/orchestration-status --verbose

# 3. Check specific agent
/check-agents --agent implementer-1

# 4. Check specific module
/orchestration-status --modules-only | grep "auth-core"

# 5. Based on findings, take action
# - If agent stuck: Send prompt via AI Maestro
# - If module blocked: Check dependencies
# - If ready modules unassigned: Assign agents
```

## Checklist

- [ ] Run `/orchestration-status` command
- [ ] Review phase status header
- [ ] Check module status table for blockers
- [ ] Review agent registry for idle/blocked agents
- [ ] Check active assignments for IVP status
- [ ] Review polling history (if verbose)
- [ ] Identify and address any issues found
- [ ] Schedule next status check (10-15 min)
