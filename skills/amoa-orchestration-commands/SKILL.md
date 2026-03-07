---
name: amoa-orchestration-commands
description: "Use when managing orchestration phase commands. Trigger with start, monitor, loop control, cancellation, or stop hook enforcement requests."
license: Apache-2.0
compatibility: "Requires Python 3.8+, PyYAML, GitHub CLI. Works with AI Maestro for remote agent communication. Requires AI Maestro installed."
metadata:
  author: Emasoft
  version: 1.0.0
user-invocable: false
context: fork
agent: amoa-main
---

# Orchestration Commands Skill

## Overview

Manages the execution loop that coordinates remote agents to implement approved plans. Covers starting orchestration, monitoring status, loop control, cancellation, and stop hook enforcement.

## Prerequisites

1. Plan Phase complete (via `/approve-plan`)
2. State file `design/state/exec-phase.md` exists
3. Two-Phase Mode workflow understood (Plan Phase then Orchestration Phase)

## Command Summary

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/start-orchestration` | Activate orchestration phase | After plan approval |
| `/orchestration-status` | View module/agent progress | To monitor implementation |
| `/orchestrator-status` | Check loop state and tasks | To see pending tasks |
| `/orchestrator-loop` | Start continuous task loop | To activate dev loop |
| `/cancel-orchestrator` | Cancel active loop | To stop the loop |

Full syntax and options: See [references/command-details.md](references/command-details.md)

## Output

| Output Type | Format |
|-------------|--------|
| Status report | Markdown table (modules, agents) |
| Loop state | Text summary (iteration, tasks) |
| Cancellation | Confirmation message |
| Error messages | Hook blocking reasons |

## Quick Start

1. `/start-orchestration` (optionally with `--project-id`)
2. Register agents with `/register-agent`
3. Assign modules with `/assign-module`
4. Monitor with `/orchestration-status` every 10-15 min

## Instructions

1. Run `/start-orchestration` to activate orchestration phase after plan approval.
2. Register agents with `/register-agent` and assign modules with `/assign-module`.
3. Monitor progress with `/orchestration-status` every 10-15 minutes.
4. Use `/orchestrator-loop` to activate continuous task processing if needed.
5. Cancel the loop with `/cancel-orchestrator` when tasks are complete or need to stop.

For full command syntax and flags see [references/command-details.md](references/command-details.md) and [references/checklists.md](references/checklists.md).

## Examples

See [references/examples.md](references/examples.md) for complete usage examples covering start, monitor, loop, and cancel workflows.

## Orchestrator Loop

Monitors multiple task sources and prevents exit until ALL are complete: Claude Tasks, GitHub Projects, task file checklists, Claude TODO list. Uses 4-loop verification after completion.

See [references/orchestration-loop-mechanics.md](references/orchestration-loop-mechanics.md)

## Stop Hook

Blocks exit when plan/orchestration incomplete, tasks pending, or verification loops remaining. Signals completion via `ALL_TASKS_COMPLETE` or configured promise phrase.

See [references/stop-hook-behavior.md](references/stop-hook-behavior.md)

## State Files

- `design/state/loop.md` - Loop state
- `design/state/exec-phase.md` - Execution phase state

See [references/state-file-format.md](references/state-file-format.md)

## Error Handling

Hook blocking errors and common failure modes are documented in [references/troubleshooting.md](references/troubleshooting.md). The stop hook signals completion via `ALL_TASKS_COMPLETE`; see [references/stop-hook-behavior.md](references/stop-hook-behavior.md) for recovery procedures.

## Resources

- [command-details.md](references/command-details.md) - Full command syntax and options
- [start-orchestration-procedure.md](references/start-orchestration-procedure.md) - Starting orchestration
- [status-monitoring.md](references/status-monitoring.md) - Reading status output
- [orchestration-loop-mechanics.md](references/orchestration-loop-mechanics.md) - Loop behavior
- [stop-hook-behavior.md](references/stop-hook-behavior.md) - Stop hook blocking and recovery
- [cancellation-cleanup.md](references/cancellation-cleanup.md) - Cancellation procedures
- [state-file-format.md](references/state-file-format.md) - State file schemas
- [checklists.md](references/checklists.md) - Step-by-step checklists
- [examples.md](references/examples.md) - Usage examples
- [python-scripts.md](references/python-scripts.md) - Script inventory and output rules
- [troubleshooting.md](references/troubleshooting.md) - Common issues and solutions
