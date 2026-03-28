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
<!-- TOC: /start-orchestration - Enter orchestration phase | /orchestration-status - View phase progress | /orchestrator-status - Check loop state | /orchestrator-loop - Start continuous loop | /cancel-orchestrator - Cancel active loop -->

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
<!-- TOC: Starting Orchestration checklist | Monitoring Progress checklist | Cancellation checklist -->

For loop mechanics and stop hook, see skill `amoa-orchestration-loop`.

## Output

Status as Markdown tables; errors as hook blocking reasons.

## Examples

**Input:** `/start-orchestration --project-id PVT_kwDOB1234567`
**Output:** Phase activated, stop hook enabled, agents ready for assignment.

## Error Handling

See [troubleshooting.md](references/troubleshooting.md)
<!-- TOC: 1 Loop won't start - common causes | 2 Stop hook not firing - debugging steps | 3 Tasks showing as pending incorrectly | 4 Lock file issues and stale locks | 5 Concurrent execution conflicts | 6 Verification mode stuck | 7 Helper script failures | 8 Using /reload-plugins -->

## Resources

- [command-details.md](references/command-details.md)
- [checklists.md](references/checklists.md)
- [start-orchestration-procedure.md](references/start-orchestration-procedure.md)
- [status-monitoring.md](references/status-monitoring.md)
- [cancellation-cleanup.md](references/cancellation-cleanup.md)
- [python-scripts.md](references/python-scripts.md)
