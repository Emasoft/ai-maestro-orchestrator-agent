---
name: amoa-module-lifecycle
description: "Use when adding, modifying, removing, prioritizing, or reassigning modules. Trigger with module CRUD requests."
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
<!-- TOC: 1 /add-module | 2 /modify-module | 3 /remove-module | 4 /prioritize-module | 5 /reassign-module -->

`/add-module` -- [module-creation.md](./references/module-creation.md)
<!-- TOC: Module Creation Reference | When to Add Modules During Orchestration | Appropriate Scenarios for Adding Modules | When NOT to Add Modules | Dynamic Flexibility Concept | Required Fields for New Modules | Optional Fields | Automatic GitHub Issue Creation | State File Update After Addition | Complete Examples with All Variations | Next Steps After Adding a Module | Related Commands -->

`/modify-module` -- [module-modification.md](./references/module-modification.md)
<!-- TOC: Module Modification Reference | What Can Be Modified | Modifiable Fields | When to Modify Each Field | What Cannot Be Modified | Modification Restrictions by Status | Agent Notification Protocol | GitHub Issue Synchronization | Complete Modification Examples | Best Practices for Modifications | Related Commands -->

`/remove-module` (pending only) -- [module-removal-rules.md](./references/module-removal-rules.md)
<!-- TOC: Module Removal Rules Reference | Which Modules Can Be Removed | Removal Eligibility by Status | Why In-Progress Modules Cannot Be Removed | Removal Process Step by Step | GitHub Issue Closure with Wontfix Label | Alternatives to Removal (Scope Reduction) | Error Handling and Recovery | Force Removal Flag | Related Commands -->

`/prioritize-module` -- [module-prioritization.md](./references/module-prioritization.md)
<!-- TOC: Module Prioritization Reference | Priority Levels Explained | Priority Level Definitions | Effects on Assignment Queue | GitHub Issue Label Updates | When to Escalate vs Downgrade | Complete Priority Change Examples | Priority Labels Visual Reference | Best Practices | Related Commands -->

`/reassign-module` -- [module-reassignment.md](./references/module-reassignment.md)
<!-- TOC: Module Reassignment Reference | When Reassignment Is Appropriate | Reassignment Workflow Step by Step | Old Agent Notification Protocol | New Agent Assignment Message | State File Updates During Reassignment | Instruction Verification Protocol Reset | Reassignment Command Reference | Related Commands -->

## Examples

**Input:** `/add-module "Two-Factor Auth" --criteria "Support TOTP and SMS" --priority critical`
**Output:** Module `two-factor-auth` created, Issue #43 opened, pending

**Input:** `/reassign-module auth-core --to implementer-2`
**Output:** Old agent stopped, new agent assigned, verification reset

## Error Handling

Module not found: run `/orchestration-status`. Cannot remove: status not pending. Agent not notified: check AI Maestro AMP.

## Resources

See reference files above for complete command syntax and details.
