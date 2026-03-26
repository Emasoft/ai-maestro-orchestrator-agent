---
name: amoa-orchestration-commands
description: "Use when running orchestration phase commands. Trigger with start, monitor, or cancel orchestration requests."
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

Commands: `/start-orchestration`, `/orchestration-status`, `/orchestrator-status`, `/cancel-orchestrator`. Full syntax: [command-details.md](references/command-details.md)
<!-- TOC: /start-orchestration | /orchestration-status | /orchestrator-status | /orchestrator-loop | /cancel-orchestrator -->

1. Run `/start-orchestration` to activate
2. Register agents and assign modules
3. Monitor with `/orchestration-status` every 10-15 min
4. Cancel with `/cancel-orchestrator` when done

Copy this checklist and track your progress:

- [ ] Run `/start-orchestration`
- [ ] Register agents, assign modules
- [ ] Monitor with `/orchestration-status`
- [ ] Cancel when complete

Details: [checklists.md](references/checklists.md)
<!-- TOC: Checklist: Starting Orchestration | Checklist: Monitoring Progress | Checklist: Cancellation -->

For loop mechanics and stop hook, see skill `amoa-orchestration-loop`.

## Output

Status as Markdown tables; errors as hook blocking reasons.

## Examples

**Input:** `/start-orchestration --project-id PVT_kwDOB1234567`
**Output:** Phase activated, stop hook enabled, agents ready for assignment.

## Error Handling

See [troubleshooting.md](references/troubleshooting.md)
<!-- TOC: Troubleshooting | Loop Won't Start - Common Causes | Stop Hook Not Firing - Debugging Steps | Tasks Showing as Pending Incorrectly | Lock File Issues and Stale Locks | Concurrent Execution Conflicts | Verification Mode Stuck | Helper Script Failures | Using /reload-plugins | General Debugging Workflow -->

## Resources

- [command-details.md](references/command-details.md)
  <!-- TOC: /start-orchestration | /orchestration-status | /orchestrator-status | /orchestrator-loop | /cancel-orchestrator -->
- [checklists.md](references/checklists.md)
  <!-- TOC: Checklist: Starting Orchestration | Checklist: Monitoring Progress | Checklist: Cancellation -->
- [start-orchestration-procedure.md](references/start-orchestration-procedure.md)
  <!-- TOC: Command syntax and options | GitHub Project integration setup -->
- [status-monitoring.md](references/status-monitoring.md)
  <!-- TOC: Reading module status indicators | Interpreting agent registry information -->
- [cancellation-cleanup.md](references/cancellation-cleanup.md)
  <!-- TOC: Cleanup of state files and locks | Cancellation procedure step-by-step -->
- [python-scripts.md](references/python-scripts.md)
  <!-- TOC: Script inventory - Scripts and their command mappings | Script output rules - Token-efficient output protocol -->
