---
name: amoa-plan-phase
description: "Use when running Plan Phase of two-phase mode. Trigger with planning, requirements, or plan approval requests. Loaded by ai-maestro-orchestrator-agent-main-agent"
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
<!-- TOC: Overview - Why use Claude Code native Tasks | Task Tool Reference - TaskCreate, TaskUpdate, TaskList, TaskGet | Task Lifecycle - Creating, tracking, and completing tasks | Persistence Across Compacting - How tasks survive context limits | Stop Hook Integration - How orchestrator checks task completion | Best Practices - Effective task management patterns -->

1. `/start-planning` -- create state file, document requirements
2. Add/modify/remove requirements as needed
3. `/approve-plan` -- transition to Orchestration Phase, create GitHub Issues

Copy this checklist and track your progress:

- [ ] `/start-planning` -- state file + requirements
- [ ] Document and refine requirements
- [ ] `/approve-plan` -- create Issues, start orchestration

Commands: [command-reference.md](references/command-reference.md)
<!-- TOC: Plan Phase Commands (6) | 1 /start-planning | 2 /planning-status | 3 /add-requirement | 4 /modify-requirement | 5 /remove-requirement | 6 /approve-plan | Orchestration Phase Commands (10) | 1 /start-orchestration | 2 /orchestration-status | 3 /register-agent | 4 /assign-module | 5 /add-module | 6 /modify-module | 7 /remove-module | 8 /prioritize-module | 9 /reassign-module | 10 /check-agents -->

## Output

State YAML, GitHub Issues, phase confirmations. See [state-file-formats.md](references/state-file-formats.md).
<!-- TOC: Plan Phase State File | 1 File location | 2 Complete YAML schema | 3 Field descriptions | Orchestration Phase State File | 1 File location | 2 Complete YAML schema | 3 Field descriptions | Agent Assignment Structure | 1 Assignment fields | 2 Instruction verification tracking | 3 Progress polling tracking | Module Status Structure | 1 Module fields | 2 Status values -->

## Examples

**Input:** `/start-planning` -- **Output:** Creates `design/plan-state.yaml`, enters Plan Phase.
**Input:** `/approve-plan` -- **Output:** Creates GitHub Issues per module, starts Orchestration Phase.

## Error Handling

See [troubleshooting.md](references/troubleshooting.md).
<!-- TOC: Two-Phase Mode Troubleshooting | Contents | 1. Plan Phase Issues | 2. Orchestration Phase Issues | 3. State File Issues | 4. Communication Issues | 5. Stop Hook Issues | Related References -->

## Resources

- [command-reference.md](references/command-reference.md)
- [plan-phase-workflow.md](references/plan-phase-workflow.md)
- [state-file-formats.md](references/state-file-formats.md)
- [troubleshooting.md](references/troubleshooting.md)
