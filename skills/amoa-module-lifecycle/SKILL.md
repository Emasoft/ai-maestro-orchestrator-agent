---
name: amoa-module-lifecycle
description: "Use when adding, modifying, removing, prioritizing, or reassigning modules. Trigger with module CRUD requests. Loaded by ai-maestro-orchestrator-agent-main-agent"
license: Apache-2.0
compatibility: Python 3.8+, PyYAML, gh CLI, AI Maestro.
metadata:
  author: Emasoft
  version: 1.0.0
user-invocable: false
context: fork
agent: amoa-main
---

# Module Lifecycle Commands Skill

## Overview

Core CRUD operations for modules during Orchestration Phase. Each module maps 1:1 to a GitHub Issue.

## Prerequisites

Orchestration Phase active, gh CLI authenticated, AI Maestro running.

## Output

Module ID, Issue number, state update, and agent notification status.

## Instructions

1. Identify action: add, modify, remove, prioritize, or reassign
2. Run the command and verify state update in `design/state/exec-phase.md`
3. Confirm GitHub Issue sync and notify agents via AI Maestro

Copy this checklist and track your progress:

- [ ] Identify action and verify prerequisites
- [ ] Execute command and verify state update
- [ ] Confirm Issue sync and notify agents

Commands: `/add-module`, `/modify-module`, `/remove-module`, `/prioritize-module`, `/reassign-module`. Syntax: [command-details.md](./references/command-details.md)
<!-- TOC: 1 /add-module command syntax and arguments | 2 /modify-module command syntax and restrictions | 3 /remove-module command syntax and restrictions | 4 /prioritize-module command syntax | 5 /reassign-module command syntax and workflow -->

`/add-module` -- [module-creation.md](./references/module-creation.md)
<!-- TOC: 1 When to add modules during orchestration | 2 Required fields for new modules (name, criteria) | 3 Optional fields (priority level) | 4 Automatic GitHub Issue creation | 5 State file update after addition | 6 Complete examples with all variations -->

`/modify-module` -- [module-modification.md](./references/module-modification.md)
<!-- TOC: 1 What can be modified (name, criteria, priority) | 2 Modification restrictions by status | 3 Agent notification protocol | 4 GitHub Issue synchronization | 5 Complete modification examples -->

`/remove-module` (pending only) -- [module-removal-rules.md](./references/module-removal-rules.md)
<!-- TOC: 1 Which modules can be removed (pending only) | 2 Why in-progress modules cannot be removed | 3 Removal process step by step | 4 GitHub Issue closure with wontfix label | 5 Alternatives to removal (scope reduction) | 6 Error handling and recovery -->

`/prioritize-module` -- [module-prioritization.md](./references/module-prioritization.md)
<!-- TOC: 1 Priority levels explained (critical, high, medium, low) | 2 Effects on assignment queue | 3 GitHub Issue label updates | 4 When to escalate vs downgrade | 5 Complete priority change examples -->

`/reassign-module` -- [module-reassignment.md](./references/module-reassignment.md)
<!-- TOC: 1 When reassignment is appropriate | 2 Reassignment workflow step by step | 3 Old agent notification protocol | 4 New agent assignment message | 5 State file updates during reassignment | 6 Instruction Verification Protocol reset -->

## Examples

**Input:** `/add-module "Two-Factor Auth" --criteria "Support TOTP and SMS" --priority critical`
**Output:** Module `two-factor-auth` created, Issue #43 opened, pending

**Input:** `/reassign-module auth-core --to implementer-2`
**Output:** Old agent stopped, new agent assigned, verification reset

## Error Handling

Module not found: run `/orchestration-status`. Cannot remove: status not pending. Agent not notified: check AI Maestro AMP.

## Resources

See reference files above for complete command syntax and details.
