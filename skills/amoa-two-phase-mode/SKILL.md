---
name: amoa-two-phase-mode
description: "Use when running Plan-then-Execute workflows. Trigger with plan-execute or two-phase requests. Loaded by ai-maestro-orchestrator-agent-main-agent"
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
  <!-- TOC: Output Types and Locations | Step-by-Step Instructions | Agent Types | Stop Hook Enforcement | File Structure | Examples -->
- [orchestration-phase-workflow.md](references/orchestration-phase-workflow.md)
  <!-- TOC: Entering Orchestration Phase | 1 Using /start-orchestration command | 2 State file structure | Agent Registration | 1 Registering AI agents with /register-agent | 2 Registering human developers | 3 Agent types and differences | Module Assignment | 1 Assigning modules with /assign-module | 2 Reassigning modules with /reassign-module | Monitoring Progress | 1 Using /orchestration-status | 2 Using /check-agents for polling | Modifying During Orchestration | 1 Adding modules with /add-module | 2 Modifying modules with /modify-module | 3 Removing modules with /remove-module | 4 Prioritizing with /prioritize-module | Completion and Exit | 1 All modules complete criteria | 2 4-verification loops requirement | 3 Stop hook enforcement -->
- [instruction-verification-protocol.md](references/instruction-verification-protocol.md)
  <!-- TOC: Why This Protocol Exists | 1 Reasons for misinterpretation | 2 Orchestrator proactive responsibility | The 8-Step Protocol Flow | 1 Step 1: Send Module Assignment | 2 Step 2: Request Instruction Repetition | 3 Step 3: Agent Repeats Understanding | 4 Step 4: Verify Repetition Correct | 5 Step 5: Request Clarifying Questions | 6 Step 6: Agent Asks Questions | 7 Step 7: Answer ALL Questions | 8 Step 8: Authorize Implementation | Message Templates | 1 Initial Assignment Template | 2 Correction Message Template | 3 Question Resolution Template | 4 Authorization Template | Tracking Verification Status | 1 State file fields | 2 Status values and meanings | Failure Conditions | 1 When to NOT authorize | 2 Action on failure -->
- [state-file-formats.md](references/state-file-formats.md)
  <!-- TOC: Plan Phase State File | 1 File location | 2 Complete YAML schema | 3 Field descriptions | Orchestration Phase State File | Agent Assignment Structure | 1 Assignment fields | 2 Instruction verification tracking | 3 Progress polling tracking | Module Status Structure | 1 Module fields | 2 Status values -->
- [troubleshooting.md](references/troubleshooting.md)
  <!-- TOC: Plan Phase Issues | Orchestration Phase Issues | State File Issues | Communication Issues | Stop Hook Issues -->
