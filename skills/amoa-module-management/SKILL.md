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

Manages modules dynamically during Orchestration Phase. Each module maps 1:1 to a GitHub Issue.

## Prerequisites

- Orchestration Phase active (Plan Phase completed)
- GitHub CLI (gh) authenticated
- AI Maestro running
- State file `design/state/exec-phase.md` exists

## Output

Command confirmation with module ID, GitHub Issue number, updated state file entry, and agent notification status.

## Instructions

1. Identify the module management action needed (add, modify, remove, prioritize, reassign)
2. Verify prerequisites (orchestration phase active, gh auth, AI Maestro running)
3. Execute the appropriate command from the Commands table
4. Verify state update in `design/state/exec-phase.md` and GitHub Issue sync
5. Notify affected agents via AI Maestro if applicable

Copy this checklist and track your progress:

- [ ] Identify the module management action needed
- [ ] Verify prerequisites (phase active, gh auth, AI Maestro)
- [ ] Execute the appropriate command
- [ ] Verify state update in `design/state/exec-phase.md`
- [ ] Confirm GitHub Issue synchronization
- [ ] Notify affected agents via AI Maestro if applicable

## Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/add-module` | Add new module | New feature requested |
| `/modify-module` | Change specs | Criteria or priority change |
| `/remove-module` | Delete pending module | Module cancelled |
| `/prioritize-module` | Change priority | Urgency changed |
| `/reassign-module` | Transfer to agent | Agent stuck/unavailable |

Full syntax: [command-details.md](./references/command-details.md)
<!-- TOC: /add-module command syntax and arguments | /modify-module command syntax and restrictions -->

## Quick Reference

**New feature**: `/add-module` -- [module-creation.md](./references/module-creation.md)
<!-- TOC: When to add modules during orchestration | Required fields for new modules (name, criteria) -->

**Specs changed**: `/modify-module` -- [module-modification.md](./references/module-modification.md)
<!-- TOC: What can be modified (name, criteria, priority) | Modification restrictions by status -->

**Cancelled**: `/remove-module` (pending only) -- [module-removal-rules.md](./references/module-removal-rules.md)
<!-- TOC: Which modules can be removed (pending only) | Removal process step by step -->

**Urgency changed**: `/prioritize-module` -- [module-prioritization.md](./references/module-prioritization.md)
<!-- TOC: Priority levels explained (critical, high, medium, low) | Effects on assignment queue -->

**Agent stuck**: `/reassign-module` -- [module-reassignment.md](./references/module-reassignment.md)
<!-- TOC: When reassignment is appropriate | New agent assignment message -->

## Examples

**Input:** `/add-module "Two-Factor Auth" --criteria "Support TOTP and SMS" --priority critical`
**Output:** Module `two-factor-auth` created, GitHub Issue #43 opened, status: pending

**Input:** `/reassign-module auth-core --to implementer-2`
**Output:** Old agent notified to stop, new agent receives assignment, verification resets

More examples: [usage-examples.md](./references/usage-examples.md)
<!-- TOC: Add new module mid-orchestration | Reassign a blocked module -->

## Module-Issue Sync

Module events sync to GitHub automatically. See: [github-issue-sync.md](./references/github-issue-sync.md)
<!-- TOC: Issue creation format and labels | Issue closure protocols -->

## Error Handling

| Problem | Solution |
|---------|----------|
| Module not found | `/orchestration-status` to see IDs |
| Cannot remove | Status not pending; modify scope instead |
| Issue not created | Run `gh auth login` |
| Agent not notified | Verify AI Maestro AMP is running |

Full guide: [troubleshooting.md](./references/troubleshooting.md)
<!-- TOC: Module ID conflicts | Force removal scenarios -->

## Resources

- [command-details.md](./references/command-details.md) -- full command syntax
  <!-- TOC: /add-module command syntax and arguments | /modify-module command syntax and restrictions -->
- [checklist-and-scripts.md](./references/checklist-and-scripts.md) -- checklist and script output rules
  <!-- TOC: Module management checklist | Script output rules and token-efficient protocol -->

