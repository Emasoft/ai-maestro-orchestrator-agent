---
name: amoa-module-management
description: "Use when managing modules during Orchestration Phase. Trigger with module add, modify, or reassign requests."
license: Apache-2.0
compatibility: Python 3.8+, PyYAML, gh CLI, AI Maestro.
metadata:
  author: Emasoft
  version: 1.0.0
user-invocable: false
context: fork
agent: amoa-main
---

# Module Management Commands Skill

## Overview

Manages modules during Orchestration Phase. Each module maps 1:1 to a GitHub Issue.

## Prerequisites

Orchestration Phase active, gh CLI authenticated (all commands need `--repo "$OWNER/$REPO"`), AI Maestro running.

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
<!-- TOC: /add-module command syntax and arguments | /modify-module command syntax and restrictions -->

`/add-module` -- [module-creation.md](./references/module-creation.md)
<!-- TOC: When to add modules during orchestration | Required fields for new modules (name, criteria) -->

`/modify-module` -- [module-modification.md](./references/module-modification.md)
<!-- TOC: What can be modified (name, criteria, priority) | Modification restrictions by status -->

`/remove-module` (pending only) -- [module-removal-rules.md](./references/module-removal-rules.md)
<!-- TOC: Which modules can be removed (pending only) | Removal process step by step -->

`/prioritize-module` -- [module-prioritization.md](./references/module-prioritization.md)
<!-- TOC: Priority levels explained (critical, high, medium, low) | Effects on assignment queue -->

`/reassign-module` -- [module-reassignment.md](./references/module-reassignment.md)
<!-- TOC: When reassignment is appropriate | New agent assignment message -->

## Examples

**Input:** `/add-module "Two-Factor Auth" --criteria "Support TOTP and SMS" --priority critical`
**Output:** Module `two-factor-auth` created, Issue #43 opened, pending

**Input:** `/reassign-module auth-core --to implementer-2`
**Output:** Old agent stopped, new agent assigned, verification reset

More: [usage-examples.md](./references/usage-examples.md)
<!-- TOC: Add new module mid-orchestration | Reassign a blocked module -->

Issue sync: [github-issue-sync.md](./references/github-issue-sync.md)
<!-- TOC: Issue creation format and labels | Issue closure protocols -->

## Error Handling

Module not found: run `/orchestration-status`. Cannot remove: status not pending. Issue not created: run `gh auth login`. Agent not notified: check AI Maestro AMP.

Guide: [troubleshooting.md](./references/troubleshooting.md)
<!-- TOC: Module ID conflicts | Force removal scenarios -->

## Resources

- [command-details.md](./references/command-details.md)
  <!-- TOC: /add-module command syntax and arguments | /modify-module command syntax and restrictions -->
- [checklist-and-scripts.md](./references/checklist-and-scripts.md)
  <!-- TOC: Module management checklist | Script output rules and token-efficient protocol -->

