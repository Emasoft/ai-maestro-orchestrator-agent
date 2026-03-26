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
<!-- TOC: Output Types and Locations | Step-by-Step Instructions | Agent Types | Stop Hook Enforcement | File Structure | Examples | Example 1: Complete Two-Phase Workflow | Example 2: Dynamic Module Addition -->

## Examples

**Input:** `/start-planning` -- **Output:** Creates `design/plan-state.yaml`, enters Plan Phase.
**Input:** `/approve-plan` -- **Output:** Creates GitHub Issues per module, starts Orchestration Phase.

## Output

State YAML, GitHub Issues, phase confirmations. See [state-file-formats.md](references/state-file-formats.md).
<!-- TOC: State File Formats | Plan Phase State File | File location | Complete YAML schema | Field descriptions | Orchestration Phase State File | File location | Complete YAML schema | Field descriptions | Agent Assignment Structure | Assignment fields | Instruction verification tracking | Progress polling tracking | Module Status Structure | Module fields | Status values | Parsing State Files -->

## Error Handling

See [troubleshooting.md](references/troubleshooting.md).
<!-- TOC: Plan Phase Issues | Orchestration Phase Issues | State File Issues | Communication Issues | Stop Hook Issues -->

## Resources

- [skill-overview-details.md](references/skill-overview-details.md)
  <!-- TOC: Output Types and Locations | Step-by-Step Instructions | Agent Types | Stop Hook Enforcement | File Structure | Examples | Example 1: Complete Two-Phase Workflow | Example 2: Dynamic Module Addition -->
- [orchestration-phase-workflow.md](references/orchestration-phase-workflow.md)
  <!-- TOC: Entering Orchestration Phase | Agent Registration | Module Assignment | Monitoring Progress | Modifying During Orchestration | Completion and Exit -->
- [instruction-verification-protocol.md](references/instruction-verification-protocol.md)
  <!-- TOC: Why This Protocol Exists | The 8-Step Protocol Flow | Message Templates | Tracking Verification Status | Failure Conditions -->
- [state-file-formats.md](references/state-file-formats.md)
  <!-- TOC: State File Formats | Plan Phase State File | File location | Complete YAML schema | Field descriptions | Orchestration Phase State File | File location | Complete YAML schema | Field descriptions | Agent Assignment Structure | Assignment fields | Instruction verification tracking | Progress polling tracking | Module Status Structure | Module fields | Status values | Parsing State Files -->
- [troubleshooting.md](references/troubleshooting.md)
  <!-- TOC: Plan Phase Issues | Orchestration Phase Issues | State File Issues | Communication Issues | Stop Hook Issues -->
