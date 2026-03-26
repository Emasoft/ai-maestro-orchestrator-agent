---
name: amoa-plan-phase
description: "Use when running Plan Phase of two-phase mode. Trigger with planning, requirements, or plan approval requests."
license: Apache-2.0
compatibility: AI Maestro, GitHub CLI (gh), remote agents.
metadata:
  author: Emasoft
  version: 1.0.0
context: fork
user-invocable: false
agent: amoa-main
---

# Plan Phase Skill

## Overview

Plan Phase of two-phase mode: document requirements, decompose into modules, approve plan for execution.

## Prerequisites

AI Maestro messaging, GitHub CLI (gh).

## Instructions

Use [native-task-persistence.md](references/native-task-persistence.md) for Claude Tasks.
<!-- TOC: Native Task Persistence Principle | Overview | Why Native Tasks? | Key Advantages | Task Tool Reference | Task Lifecycle | Persistence Across Compacting | Stop Hook Integration | Best Practices | Summary -->

1. `/start-planning` -- create state file, document requirements
2. Add/modify/remove requirements as needed
3. `/approve-plan` -- transition to Orchestration Phase, create GitHub Issues

Copy this checklist and track your progress:

- [ ] `/start-planning` -- state file + requirements
- [ ] Document and refine requirements
- [ ] `/approve-plan` -- create Issues, start orchestration

Commands: [command-reference.md](references/command-reference.md)
<!-- TOC: Command Reference | Plan Phase Commands | /start-planning | /planning-status | /add-requirement | /modify-requirement | /remove-requirement | /approve-plan | Orchestration Phase Commands | /start-orchestration | /orchestration-status | /register-agent | /assign-module | /add-module | /modify-module | /remove-module | /prioritize-module | /reassign-module | /check-agents -->

## Output

State YAML, GitHub Issues, phase confirmations. See [state-file-formats.md](references/state-file-formats.md).
<!-- TOC: State File Formats | Plan Phase State File | File location | Complete YAML schema | Field descriptions | Orchestration Phase State File | File location | Complete YAML schema | Field descriptions | Agent Assignment Structure | Assignment fields | Instruction verification tracking | Progress polling tracking | Module Status Structure | Module fields | Status values | Parsing State Files -->

## Examples

**Input:** `/start-planning` -- **Output:** Creates `design/plan-state.yaml`, enters Plan Phase.
**Input:** `/approve-plan` -- **Output:** Creates GitHub Issues per module, starts Orchestration Phase.

## Error Handling

See [troubleshooting.md](references/troubleshooting.md).
<!-- TOC: Plan Phase Issues | Orchestration Phase Issues | State File Issues | Communication Issues | Stop Hook Issues -->

## Resources

- [command-reference.md](references/command-reference.md)
  - 1. Plan Phase Commands
    - 1.1 /start-planning
    - 1.2 /planning-status
    - 1.3 /add-requirement
    - 1.4 /modify-requirement
  - ...
- [plan-phase-workflow.md](references/plan-phase-workflow.md)
  - 1. Entering Plan Phase
    - 1.1 Using /start-planning command
    - 1.2 State file initialization
  - 2. Planning Activities
    - 2.1 Gathering user goals
  - ...
- [state-file-formats.md](references/state-file-formats.md)
  - 1. Plan Phase State File
    - 1.1 File location
    - 1.2 Complete YAML schema
    - 1.3 Field descriptions
  - 2. Orchestration Phase State File
  - ...
- [troubleshooting.md](references/troubleshooting.md)
  - 1. Plan Phase Issues
    - Issue: Plan Phase won't transition to Orchestration Phase
    - Issue: USER_REQUIREMENTS.md validation fails
    - Issue: /approve-plan creates duplicate GitHub Issues
  - 2. Orchestration Phase Issues
  - ...
