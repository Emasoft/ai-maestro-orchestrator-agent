---
name: amoa-kanban-management
description: GitHub Projects V2 kanban board management. Use when creating boards, adding columns, moving items. Trigger with kanban or column requests.
license: Apache-2.0
compatibility: Requires gh CLI authenticated with project scopes. Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
context: fork
user-invocable: false
agent: amoa-main
---

# Kanban Board Management Skill

## Overview

Manages GitHub Projects V2 kanban boards: creating boards, adding/modifying columns, moving items between columns, and synchronizing task status. Documents critical pitfalls that can cause data loss.

## Prerequisites

1. GitHub CLI (`gh`) installed and authenticated
2. **OAuth scopes**: `project` and `read:project` scopes required. See [references/gh-auth-scopes.md](references/gh-auth-scopes.md)
3. Read **amoa-task-distribution** and **amoa-label-taxonomy** skills
4. Standard 8-column system: Backlog, Todo, In Progress, AI Review, Human Review, Merge/Release, Done, Blocked

---

## Critical Pre-Flight Check

**Before ANY kanban operation**, verify OAuth scopes:

```bash
gh auth status 2>&1 | grep -q "project" || echo "ERROR: Missing project scope. Run: gh auth refresh -h github.com -s project,read:project"
```

If scopes are missing, the agent CANNOT proceed.

---

## Core Procedures

4 procedures for board management: create board, add columns, move items, sync status.
See: [references/kanban-procedures.md](references/kanban-procedures.md)

**Key warning:** NEVER manually call `updateProjectV2Field` -- it REPLACES all options and causes data loss. Always use `scripts/gh-project-add-columns.py`.

---

## Column System and Scripts

Standard 8-column kanban system with status labels and 4 management scripts.
See: [references/kanban-column-system.md](references/kanban-column-system.md)

---

## Checklists

Pre-flight, board setup, and task management checklists.
See: [references/kanban-checklist.md](references/kanban-checklist.md)

---

## Error Handling, Output, and Script Rules

Common errors with solutions, expected output per operation, and script output protocol.
See: [references/kanban-error-handling.md](references/kanban-error-handling.md)

---

## Examples

4 copy-paste examples: scope check, create task, move item, safe close guard.
See: [references/kanban-examples.md](references/kanban-examples.md)

---

## Error Handling

Common errors (missing scopes, field replacement data loss) and recovery steps.
See: [references/kanban-error-handling.md](references/kanban-error-handling.md)

---

## Instructions

1. Run the pre-flight OAuth scope check before any operation.
2. Follow procedures in [references/kanban-procedures.md](references/kanban-procedures.md).
3. Never call `updateProjectV2Field` directly -- use the provided scripts.

---

## Output

Each operation prints a JSON confirmation or error to stdout. Expected formats per operation are documented in [references/kanban-error-handling.md](references/kanban-error-handling.md).

---

## Resources

- Scripts: `scripts/gh-project-add-columns.py` and companion scripts in [references/kanban-column-system.md](references/kanban-column-system.md)
- GraphQL reference: [references/github-projects-v2-graphql.md](references/github-projects-v2-graphql.md)

---

## References

- [GitHub CLI Authentication and OAuth Scopes](references/gh-auth-scopes.md)
- [GitHub Projects V2 GraphQL Mutations](references/github-projects-v2-graphql.md)
- [Kanban Pitfalls and Guards](references/kanban-pitfalls.md)
- [Core Procedures](references/kanban-procedures.md)
- [Column System and Scripts](references/kanban-column-system.md)
- [Checklists](references/kanban-checklist.md)
- [Error Handling and Output](references/kanban-error-handling.md)
- [Examples](references/kanban-examples.md)
- **amoa-task-distribution** skill - Task assignment workflow
- **amoa-label-taxonomy** skill - Label categories and cardinality
- **amoa-progress-monitoring** skill - Agent tracking and escalation

---

**Version:** 1.0.0 | **Last Updated:** 2026-02-15 | **Audience:** Orchestrator Agents
