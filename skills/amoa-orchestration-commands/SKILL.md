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
<!-- TOC: /start-orchestration | /orchestration-status | /orchestrator-status | /orchestrator-loop | /cancel-orchestrator -->

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
<!-- TOC: Checklist: Starting Orchestration | Checklist: Monitoring Progress | Checklist: Cancellation -->

Loop monitors task sources (Claude Tasks, GitHub Projects, task files, TODO list), uses 4-loop verification, prevents exit until complete. Stop hook blocks exit when tasks pending; signal `ALL_TASKS_COMPLETE`. State: `design/state/loop.md`, `design/state/exec-phase.md`.

See [orchestration-loop-mechanics.md](references/orchestration-loop-mechanics.md)
<!-- TOC: What the Orchestrator Loop Does | Loop Lifecycle | State File Structure | Task Source Monitoring and Priority | Iteration Counting and Max Iterations | Verification Mode (4-Loop Quadruple-Check) | Completion Signals (ALL_TASKS_COMPLETE) | Stop Hook Behavior and Blocking Logic -->
See [stop-hook-behavior.md](references/stop-hook-behavior.md)
<!-- TOC: Blocking Conditions | Completion Signals | Recovery Behavior -->
See [state-file-format.md](references/state-file-format.md)
<!-- TOC: Loop State File Format and Fields | Execution Phase State File Format | Frontmatter Field Definitions | How to Manually Edit State Files | State File Corruption Recovery -->

## Output

Status as Markdown tables; loop state as text; errors as hook blocking reasons.

## Examples

**Input:** `/start-orchestration --project-id PVT_kwDOB1234567`
**Output:** Phase activated, stop hook enabled, agents ready for assignment.

**Input:** `/orchestrator-loop "Complete auth tasks" --max-iterations 50`
**Output:** Continuous processing started, monitoring all task sources.

More: [examples.md](references/examples.md)
<!-- TOC: Example 1: Complete Orchestration Start | Example 2: Orchestrator Loop Usage | Example 3: Monitoring During Implementation -->

## Error Handling

See [troubleshooting.md](references/troubleshooting.md)
<!-- TOC: Loop Won't Start - Common Causes | Stop Hook Not Firing - Debugging Steps | Tasks Showing as Pending Incorrectly | Lock File Issues and Stale Locks | Concurrent Execution Conflicts | Verification Mode Stuck | Helper Script Failures | Using /reload-plugins | General Debugging Workflow -->

## Resources

- [start-orchestration-procedure.md](references/start-orchestration-procedure.md)
  <!-- TOC: Command syntax and options | GitHub Project integration setup -->
- [status-monitoring.md](references/status-monitoring.md)
  <!-- TOC: Reading module status indicators | Interpreting agent registry information -->
- [cancellation-cleanup.md](references/cancellation-cleanup.md)
  <!-- TOC: Cleanup of state files and locks | Cancellation procedure step-by-step -->
- [python-scripts.md](references/python-scripts.md)
  <!-- TOC: Script inventory - Scripts and their command mappings | Script output rules - Token-efficient output protocol -->
