---
name: eoa-orchestration-commands
description: "Use when managing orchestration phase commands. Trigger with start, monitor, loop control, cancellation, or stop hook enforcement requests."
license: Apache-2.0
compatibility: "Requires Python 3.8+, PyYAML, GitHub CLI. Works with AI Maestro for remote agent communication. Requires AI Maestro installed."
metadata:
  author: Emasoft
  version: 1.0.0
user-invocable: false
context: fork
agent: eoa-main
workflow-instruction: "support"
procedure: "support-skill"
---

# Orchestration Commands Skill

## Overview

This skill teaches how to use the orchestration phase commands in the Orchestrator Agent plugin. These commands manage the execution loop that coordinates remote agents to implement approved plans.

## Instructions

1. Start an orchestration phase to implement an approved plan
2. Monitor the status of modules, agents, and assignments
3. Check the orchestrator loop state and pending tasks
4. Control or cancel the orchestrator loop
5. Understand how the stop hook prevents premature exit

## Output

| Output Type | Format | Example |
|-------------|--------|---------|
| Status report | Markdown table | Module completion percentages, agent assignments |
| Loop state | Text summary | Active/inactive, iteration count, pending tasks |
| Cancellation | Confirmation | "Orchestrator loop cancelled at iteration X" |
| Error messages | Text | Hook blocking reasons, state file issues |

## Prerequisites

Before using orchestration commands, ensure:
1. Plan Phase is complete (via `/approve-plan`)
2. The state file `design/state/exec-phase.md` exists
3. You understand the Two-Phase Mode workflow (Plan Phase then Orchestration Phase)

---

## Command Summary

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/start-orchestration` | Activate orchestration phase | After plan approval, to begin implementation |
| `/orchestration-status` | View module/agent progress | To monitor implementation progress |
| `/orchestrator-status` | Check loop state and tasks | To see pending tasks across all sources |
| `/orchestrator-loop` | Start continuous task loop | To activate task-driven development loop |
| `/cancel-orchestrator` | Cancel active loop | To manually stop the orchestrator loop |

## Examples

### Example 1: Start Orchestration After Plan Approval

```bash
# Step 1: Start orchestration with GitHub Project sync
/start-orchestration --project-id PVT_kwDOB1234567

# Step 2: Register your agents
/register-agent ai implementer-1 --session helper-agent-generic

# Step 3: Assign first module
/assign-module auth-core implementer-1

# Step 4: Monitor progress
/orchestration-status
```

### Example 2: Start Orchestrator Loop

```bash
# Start continuous task-driven development
/orchestrator-loop "Complete all pending authentication tasks" --max-iterations 50

# Check loop status
/orchestrator-status --verbose

# Cancel if needed
/cancel-orchestrator
```

---

## Quick Reference: Starting Orchestration

**If you need to start the orchestration phase after plan approval:**

1. Run `/start-orchestration` (optionally with `--project-id` for GitHub sync)
2. Register agents with `/register-agent`
3. Assign modules with `/assign-module`
4. Monitor with `/orchestration-status` every 10-15 minutes

See [references/start-orchestration-procedure.md](references/start-orchestration-procedure.md):
- 1.1 When to start orchestration phase
- 1.2 Prerequisites verification checklist
- 1.3 Command syntax and options
- 1.4 Post-start agent registration workflow
- 1.5 GitHub Project integration setup

---

## Quick Reference: Monitoring Status

**If you need to check implementation progress:**

Use `/orchestration-status` to see:
- Module completion percentages
- Registered agents and their assignments
- Instruction verification status
- Progress polling history

See [references/status-monitoring.md](references/status-monitoring.md):
- 2.1 Understanding the orchestration status output
- 2.2 Reading module status indicators
- 2.3 Interpreting agent registry information
- 2.4 Tracking active assignments and polling
- 2.5 Using verbose mode for detailed diagnostics

---

## Quick Reference: Orchestrator Loop Control

**If you need to start or manage the orchestrator loop:**

The orchestrator loop monitors multiple task sources and prevents exit until ALL are complete:
- Claude Tasks via TaskList API
- GitHub Projects open items
- Task file markdown checklists
- Claude TODO list (session)

See [references/orchestration-loop-mechanics.md](references/orchestration-loop-mechanics.md):
- 3.1 What the orchestrator loop does
- 3.2 Task source monitoring and priority
- 3.3 Iteration counting and max iterations
- 3.4 Verification mode (4-loop quadruple-check)
- 3.5 Completion signals (ALL_TASKS_COMPLETE)
- 3.6 Stop hook behavior and blocking logic

---

## Quick Reference: Cancellation

**If you need to cancel the orchestrator loop:**

Use `/cancel-orchestrator` to:
1. Check if a loop is active
2. Read current iteration from state file
3. Remove the state file to stop the loop

See [references/cancellation-cleanup.md](references/cancellation-cleanup.md):
- 4.1 When to cancel vs let loop complete naturally
- 4.2 Cancellation procedure step-by-step
- 4.3 Cleanup of state files and locks
- 4.4 Recovery after unexpected termination

---

## State File Reference

**If you need to understand or debug state files:**

The orchestrator uses markdown files with YAML frontmatter to track state:
- `design/state/loop.md` - Loop state
- `design/state/exec-phase.md` - Execution phase state

See [references/state-file-format.md](references/state-file-format.md):
- 5.1 Loop state file format and fields
- 5.2 Execution phase state file format
- 5.3 Frontmatter field definitions
- 5.4 How to manually edit state files
- 5.5 State file corruption recovery

---

## Troubleshooting

## Error Handling

See [references/troubleshooting.md](references/troubleshooting.md):
- 6.1 Loop won't start - common causes
- 6.2 Stop hook not firing - debugging steps
- 6.3 Tasks showing as pending incorrectly
- 6.4 Lock file issues and stale locks
- 6.5 Concurrent execution conflicts
- 6.6 Verification mode stuck
- 6.7 Helper script failures

---

## Python Scripts Reference

The following scripts implement the orchestration commands. Located in the plugin's `scripts/` directory:

| Script | Purpose | Used By |
|--------|---------|---------|
| `eoa_start_orchestration.py` | Activates orchestration phase | `/start-orchestration` |
| `eoa_orchestration_status.py` <!-- TODO: Script not implemented --> | Displays phase status | `/orchestration-status` |
| `eoa_check_orchestrator_status.py` <!-- TODO: Script not implemented --> | Shows loop state | `/orchestrator-status` |
| `eoa_setup_orchestrator_loop.py` | Creates loop state file | `/orchestrator-loop` |
| `eoa_orchestrator_stop_check.py` <!-- TODO: Script not implemented --> | Stop hook enforcement | Hook event |

---

## Command Details

### /start-orchestration

**Purpose**: Enter Orchestration Phase to coordinate remote agents implementing the approved plan.

**Syntax**:
```bash
/start-orchestration [--project-id PVT_kwDOBxxxxxx]
```

**Options**:
- `--project-id`: GitHub Project ID for Kanban synchronization

**What it does**:
1. Verifies Plan Phase is complete
2. Sets orchestration status to "executing"
3. Loads module list from approved plan
4. Enables stop hook enforcement
5. Prepares agent tracking structures

**Example**:
```
/start-orchestration --project-id PVT_kwDOB1234567
```

---

### /orchestration-status

**Purpose**: View current Orchestration Phase progress including modules, agents, and verification status.

**Syntax**:
```bash
/orchestration-status [--verbose] [--agents-only] [--modules-only]
```

**Options**:
- `--verbose`: Show detailed polling history and acceptance criteria
- `--agents-only`: Show only agent information
- `--modules-only`: Show only module status

**Output sections**:
- Phase status header (plan ID, status, progress percentage)
- Module status table with completion indicators
- Registered agents list (AI and human)
- Active assignments with verification and polling info

---

### /orchestrator-status

**Purpose**: Check orchestrator loop status and pending tasks across all sources.

**Syntax**:
```bash
/orchestrator-status [--verbose]
```

**Options**:
- `--verbose`: Show detailed debug information and recent log entries

**Output sections**:
- Loop active/inactive status
- Iteration count and limits
- Task sources with pending counts (Claude Tasks, GitHub, Task file, TODO)
- Current task preview
- Debug info (log file, lock file status)

---

### /orchestrator-loop

**Purpose**: Start orchestrator loop for continuous task-driven development.

**Syntax**:
```bash
/orchestrator-loop [PROMPT] [options]
```

**Options**:
- `--max-iterations N`: Maximum iterations before escalation (default: 100)
- `--completion-promise TEXT`: Promise phrase to trigger completion
- `--task-file PATH`: Markdown task file to monitor
- `--check-tasks BOOL`: Check Claude Tasks (default: true)
- `--check-github BOOL`: Check GitHub Projects (default: true)
- `--github-project ID`: Specific GitHub Project ID

**Example**:
```
/orchestrator-loop "Complete all pending authentication tasks" --max-iterations 50
```

---

### /cancel-orchestrator

**Purpose**: Cancel active orchestrator loop.

**What it does**:
1. Checks if loop state file exists
2. Reads current iteration number
3. Removes state file to stop loop
4. Reports cancellation with iteration count

**Note**: This command is hidden from slash command suggestions but remains functional.

---

## Stop Hook Behavior

The orchestrator stop hook (`eoa_orchestrator_stop_check.py` <!-- TODO: Script not implemented -->) enforces completion requirements:

**Blocking conditions**:
- Plan Phase incomplete (requirements not documented, plan not approved)
- Orchestration Phase incomplete (modules not implemented)
- Pending tasks in any monitored source
- Instruction verification incomplete
- Config feedback requests unresolved
- Verification loops remaining (4 required after all tasks complete)

**Completion signals**:
- Output `ALL_TASKS_COMPLETE` when all tasks genuinely done
- Output `<promise>YOUR_PHRASE</promise>` matching configured promise

**Recovery behavior**:
- Fail-safe exit on unrecoverable errors (prevents user trap)
- Conservative blocking when task status cannot be determined
- Retry logic for transient failures
- Lock file cleanup for stale processes

---

## Examples

### Example 1: Complete Orchestration Start

```bash
# Step 1: Start orchestration with GitHub Project sync
/start-orchestration --project-id PVT_kwDOB1234567

# Step 2: Register AI agent
/register-agent ai implementer-1 --session helper-agent-generic

# Step 3: Assign first module
/assign-module auth-core implementer-1

# Step 4: Monitor progress
/orchestration-status --verbose
```

### Example 2: Check Orchestrator Loop Status

```bash
# Start loop
/orchestrator-loop "Complete all authentication tasks" --max-iterations 50

# Check status
/orchestrator-status --verbose

# If needed, cancel
/cancel-orchestrator
```

### Example 3: Monitoring During Implementation

```bash
# Check all agents every 10-15 minutes
/check-agents

# Or check specific agent
/check-agents --agent implementer-1

# View orchestration status
/orchestration-status --modules-only
```

---

## Checklist: Starting Orchestration

Copy this checklist and track your progress:

- [ ] Plan Phase complete (`/approve-plan` executed)
- [ ] State file `design/state/exec-phase.md` exists
- [ ] Run `/start-orchestration` with optional `--project-id`
- [ ] Register AI agents with `/register-agent ai <agent_id> --session <session>`
- [ ] Assign modules with `/assign-module <module_id> <agent_id>`
- [ ] Execute Instruction Verification Protocol for each agent
- [ ] Begin polling with `/check-agents` every 10-15 minutes

---

## Checklist: Monitoring Progress

Copy this checklist and track your progress:

- [ ] Run `/orchestration-status` to see module completion
- [ ] Check for agents with incomplete instruction verification
- [ ] Review polling history for stuck agents
- [ ] Use `--verbose` flag for detailed diagnostics
- [ ] Check `/orchestrator-status` for pending tasks across sources

---

## Checklist: Cancellation

Copy this checklist and track your progress:

- [ ] Confirm you want to cancel (tasks may be incomplete)
- [ ] Run `/cancel-orchestrator`
- [ ] Verify state file removed
- [ ] Check no orphaned lock files in `.claude/`
- [ ] If needed, manually remove `design/state/loop.md`

---

## Resources

- [start-orchestration-procedure.md](references/start-orchestration-procedure.md) - Starting orchestration
- [status-monitoring.md](references/status-monitoring.md) - Reading status output
- [orchestration-loop-mechanics.md](references/orchestration-loop-mechanics.md) - Loop behavior
- [cancellation-cleanup.md](references/cancellation-cleanup.md) - Cancellation procedures
- [state-file-format.md](references/state-file-format.md) - State file schemas
- [troubleshooting.md](references/troubleshooting.md) - Common issues and solutions
