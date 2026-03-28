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

Runs orchestration phase commands to coordinate agents executing approved plans.

## Prerequisites

Plan Phase complete (`/approve-plan`), state file `design/state/exec-phase.md` exists.

## Instructions

Commands: `/start-orchestration`, `/orchestration-status`, `/orchestrator-status`, `/orchestrator-loop`, `/cancel-orchestrator`. Full syntax: [command-details.md](references/command-details.md)
<!-- TOC: /orchestrator-status - Check loop state | /cancel-orchestrator - Cancel active loop -->

1. Run `/start-orchestration` to activate
2. Register agents and assign modules
3. Monitor with `/orchestration-status` every 10-15 min
4. Use `/orchestrator-loop` for continuous processing; cancel with `/cancel-orchestrator` when done

Copy this checklist and track your progress:

- [ ] Run `/start-orchestration`
- [ ] Register agents, assign modules
- [ ] Monitor with `/orchestration-status`
- [ ] Use loop or cancel when complete

Details: [checklists.md](references/checklists.md)
<!-- TOC: Cancellation checklist | Monitoring Progress checklist -->

Loop monitors task sources (Claude Tasks, GitHub Projects, task files, TODO list), uses 4-loop verification, prevents exit until complete. Stop hook blocks exit when tasks pending; signal `ALL_TASKS_COMPLETE`. State: `design/state/loop.md`, `design/state/exec-phase.md`.

See [orchestration-loop-mechanics.md](references/orchestration-loop-mechanics.md)
<!-- TOC: What the orchestrator loop does | Task source monitoring and priority -->
See [stop-hook-behavior.md](references/stop-hook-behavior.md)
<!-- TOC: Recovery behavior - Fail-safe and retry logic | Completion signals - How to signal task completion -->
See [state-file-format.md](references/state-file-format.md)
<!-- TOC: Frontmatter field definitions | State file corruption recovery -->

## Output

Status as Markdown tables; loop state as text; errors as hook blocking reasons.

## Examples

**Input:** `/start-orchestration --project-id PVT_kwDOB1234567`
**Output:** Phase activated, stop hook enabled, agents ready for assignment.

**Input:** `/orchestrator-loop "Complete auth tasks" --max-iterations 50`
**Output:** Continuous processing started, monitoring all task sources.

More: [examples.md](references/examples.md)
<!-- TOC: Complete Orchestration Start - Full startup workflow | Orchestrator Loop Usage - Loop start, status, cancel -->

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
