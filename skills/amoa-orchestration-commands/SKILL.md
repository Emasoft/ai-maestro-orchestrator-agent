---
name: amoa-orchestration-commands
description: "Use when running orchestration phase commands. Trigger with start, monitor, or loop control requests."
license: Apache-2.0
compatibility: "Python 3.8+, PyYAML, GitHub CLI, AI Maestro."
metadata:
  author: Emasoft
  version: 1.0.0
user-invocable: false
context: fork
agent: amoa-main
---

# Orchestration Commands Skill

## Overview

Coordinates remote agents to implement approved plans via execution loop commands.

## Prerequisites

1. Plan Phase complete (via `/approve-plan`)
2. State file `design/state/exec-phase.md` exists

## Command Summary

| Command | Purpose |
|---------|---------|
| `/start-orchestration` | Activate orchestration phase |
| `/orchestration-status` | View module/agent progress |
| `/orchestrator-status` | Check loop state and tasks |
| `/orchestrator-loop` | Start continuous task loop |
| `/cancel-orchestrator` | Cancel active loop |

Full syntax: [command-details.md](references/command-details.md)
<!-- TOC: /orchestrator-status - Check loop state | /cancel-orchestrator - Cancel active loop -->

## Examples

**Input:** `/start-orchestration --project-id PVT_kwDOB1234567`
**Output:** Phase activated, stop hook enabled, agent tracking ready.

**Input:** `/orchestrator-loop "Complete auth tasks" --max-iterations 50`
**Output:** Loop state created, continuous task processing begins.

**Input:** `/orchestration-status --verbose`
**Output:** Table with modules, agents, assignments, polling history.

More examples: [examples.md](references/examples.md)
<!-- TOC: Complete Orchestration Start - Full startup workflow | Orchestrator Loop Usage - Loop start, status, cancel -->

## Instructions

1. Run `/start-orchestration` to activate the orchestration phase
2. Register agents with `/register-agent` and assign modules with `/assign-module`
3. Monitor progress with `/orchestration-status` every 10-15 minutes
4. Use `/orchestrator-loop` for continuous task processing when needed
5. Cancel with `/cancel-orchestrator` when all tasks are complete

Copy this checklist and track your progress:

- [ ] Run `/start-orchestration` (optionally with `--project-id`)
- [ ] Register agents with `/register-agent`
- [ ] Assign modules with `/assign-module`
- [ ] Monitor with `/orchestration-status` every 10-15 min
- [ ] Use `/orchestrator-loop` for continuous task processing
- [ ] Cancel with `/cancel-orchestrator` when done

Details: [checklists.md](references/checklists.md)
<!-- TOC: Cancellation checklist | Monitoring Progress checklist -->

## Output

Status as Markdown tables; loop state as text; cancellation as confirmation; errors as hook blocking reasons.

## Orchestrator Loop

Monitors task sources (Claude Tasks, GitHub Projects, task files, TODO list), prevents exit until ALL complete, uses 4-loop verification.

See [orchestration-loop-mechanics.md](references/orchestration-loop-mechanics.md)
<!-- TOC: What the orchestrator loop does | Task source monitoring and priority -->

## Stop Hook

Blocks exit when incomplete or tasks pending. Signal completion via `ALL_TASKS_COMPLETE`.

See [stop-hook-behavior.md](references/stop-hook-behavior.md)
<!-- TOC: Recovery behavior - Fail-safe and retry logic | Completion signals - How to signal task completion -->

## State Files

- `design/state/loop.md` - Loop state
- `design/state/exec-phase.md` - Execution phase state

See [state-file-format.md](references/state-file-format.md)
<!-- TOC: Frontmatter field definitions | State file corruption recovery -->

## Error Handling

See [troubleshooting.md](references/troubleshooting.md)
<!-- TOC: Using /reload-plugins | Helper script failures -->

## Resources

- [start-orchestration-procedure.md](references/start-orchestration-procedure.md)
  <!-- TOC: Command syntax and options | GitHub Project integration setup -->
- [status-monitoring.md](references/status-monitoring.md)
  <!-- TOC: Reading module status indicators | Interpreting agent registry information -->
- [cancellation-cleanup.md](references/cancellation-cleanup.md)
  <!-- TOC: Cleanup of state files and locks | Cancellation procedure step-by-step -->
- [python-scripts.md](references/python-scripts.md)
  <!-- TOC: Script inventory - Scripts and their command mappings | Script output rules - Token-efficient output protocol -->
