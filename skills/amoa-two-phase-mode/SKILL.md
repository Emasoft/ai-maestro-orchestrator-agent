---
name: amoa-two-phase-mode
description: "Use when running Plan-then-Execute workflows. Trigger with plan-execute or two-phase requests."
license: Apache-2.0
compatibility: AI Maestro, GitHub CLI (gh), remote agents.
metadata:
  author: Emasoft
  version: 2.6.0
context: fork
user-invocable: false
agent: amoa-main
---

# Two-Phase Mode Skill

## Overview

Plan Phase then Orchestration Phase. Stop hook enforces completion. For Plan Phase details, see skill `amoa-plan-phase`.

## Prerequisites

AI Maestro messaging, GitHub CLI (gh), remote agents registered.

## Instructions

1. `/start-planning` -- create state file, document requirements (see `amoa-plan-phase`)
2. `/approve-plan` -- transition to Orchestration Phase, create GitHub Issues
3. Register agents, assign modules, run Verification Protocol
4. `/check-agents` every 10-15 min; 4 verification loops per module

Copy this checklist and track your progress:

- [ ] `/start-planning` -- state file + requirements
- [ ] `/approve-plan` -- create Issues, start orchestration
- [ ] Assign modules, verify agents, monitor progress

Details: [skill-overview-details.md](references/skill-overview-details.md)
<!-- TOC: Output Types and Locations | Step-by-Step Instructions | Agent Types | Stop Hook Enforcement | File Structure | Examples -->

## Examples

**Input:** `/start-planning` -- **Output:** Creates `design/plan-state.yaml`, enters Plan Phase.
**Input:** `/approve-plan` -- **Output:** Creates GitHub Issues per module, starts Orchestration Phase.

## Output

State YAML, GitHub Issues, phase confirmations. See [state-file-formats.md](references/state-file-formats.md).
<!-- TOC: Plan Phase State File | 1 File location | 2 Complete YAML schema | 3 Field descriptions | Orchestration Phase State File | 1 File location | 2 Complete YAML schema | 3 Field descriptions | Agent Assignment Structure | 1 Assignment fields | 2 Instruction verification tracking | 3 Progress polling tracking | Module Status Structure | 1 Module fields | 2 Status values -->

## Error Handling

See [troubleshooting.md](references/troubleshooting.md).
<!-- TOC: Two-Phase Mode Troubleshooting | Contents | 1. Plan Phase Issues | 2. Orchestration Phase Issues | 3. State File Issues | 4. Communication Issues | 5. Stop Hook Issues | Related References -->

## Resources

- [skill-overview-details.md](references/skill-overview-details.md)
- [orchestration-phase-workflow.md](references/orchestration-phase-workflow.md)
- [instruction-verification-protocol.md](references/instruction-verification-protocol.md)
- [state-file-formats.md](references/state-file-formats.md)
- [troubleshooting.md](references/troubleshooting.md)
