---
name: amoa-module-management
description: "Trigger with module management tasks. Use when managing modules during Orchestration Phase (add, modify, remove, prioritize, reassign). Every module maps 1:1 to GitHub Issue."
license: Apache-2.0
compatibility: Requires Python 3.8+, PyYAML, gh CLI, AI Maestro.
metadata:
  author: Emasoft
  version: 1.0.0
user-invocable: false
context: fork
agent: amoa-main
---

# Module Management Commands Skill

Manages modules dynamically during the Orchestration Phase. Modules are atomic work units; each maps 1:1 to a GitHub Issue for traceability.

## Overview

Add, modify, remove, prioritize, or reassign modules during orchestration. Each module maps 1:1 to a GitHub Issue. See [references/command-details.md](./references/command-details.md) for full command specs.

## Prerequisites

- Orchestration Phase active (Plan Phase completed and approved)
- GitHub CLI (gh) authenticated
- AI Maestro running for agent notifications
- State file `design/state/exec-phase.md` exists

## Instructions

1. Identify the module management action needed
2. Verify prerequisites
3. Execute the appropriate command
4. Verify state update in `design/state/exec-phase.md`
5. Confirm GitHub Issue synchronization
6. Notify affected agents via AI Maestro if applicable

## Commands Overview

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/add-module` | Add new module | User requests new feature |
| `/modify-module` | Change module specs | Criteria or priority change |
| `/remove-module` | Delete pending module | Module cancelled |
| `/prioritize-module` | Change priority level | Urgency changed |
| `/reassign-module` | Transfer to different agent | Agent stuck or unavailable |

Full syntax, arguments, and examples for each command. See: [references/command-details.md](./references/command-details.md)

## Quick Reference by Situation

**New feature needed**: `/add-module` with name and criteria. See: [references/module-creation.md](./references/module-creation.md)

**Requirements changed**: `/modify-module` with new specs; agent notified if assigned. See: [references/module-modification.md](./references/module-modification.md)

**Module cancelled**: `/remove-module` (pending only). See: [references/module-removal-rules.md](./references/module-removal-rules.md)

**Urgency changed**: `/prioritize-module` with new level. See: [references/module-prioritization.md](./references/module-prioritization.md)

**Agent stuck**: `/reassign-module` to new agent; old agent notified. See: [references/module-reassignment.md](./references/module-reassignment.md)

## Module-Issue Synchronization

Every module event syncs to GitHub: add creates an issue, modify updates it, remove closes it with wontfix, priority change updates labels, assignment updates assignee, completion closes with linked PR. See: [references/github-issue-sync.md](./references/github-issue-sync.md)

## State File & YAML Format

Module and assignment entries are stored in `design/state/exec-phase.md`. See: [references/state-file-structure.md](./references/state-file-structure.md)

## Error Handling

| Problem | Solution |
|---------|----------|
| Module not found | Use `/orchestration-status` to see actual IDs |
| Cannot remove module | Status not pending; modify scope instead |
| GitHub Issue not created | Run `gh auth login` |
| Agent not notified | Verify AI Maestro AMP is running |

Full troubleshooting guide. See: [references/troubleshooting.md](./references/troubleshooting.md)

## Examples & Scripts

Usage examples and programmatic script reference. See: [references/usage-examples.md](./references/usage-examples.md)

## Related Commands

| Command | Purpose |
|---------|---------|
| `/orchestration-status` | View all modules and assignments |
| `/assign-module` | Initial assignment to agent |
| `/check-agents` | Monitor agent progress |
| `/register-agent` | Register new agents |

## Examples

See [references/usage-examples.md](./references/usage-examples.md) for complete usage examples of each command.

## Output

Commands update `design/state/exec-phase.md` and sync to GitHub Issues. See [references/state-file-structure.md](./references/state-file-structure.md) for output format details.

## Resources

- [references/command-details.md](./references/command-details.md) -- full command syntax and arguments
- [references/troubleshooting.md](./references/troubleshooting.md) -- error resolution guide
- [references/github-issue-sync.md](./references/github-issue-sync.md) -- GitHub synchronization rules

## Key Principles

- Every module = 1 GitHub Issue (modifications sync automatically)
- Agent notifications via AI Maestro; Instruction Verification required after reassignment
- Checklist and script output rules: See [references/checklist-and-scripts.md](./references/checklist-and-scripts.md)
