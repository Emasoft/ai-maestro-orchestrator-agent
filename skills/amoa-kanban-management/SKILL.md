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

Manage GitHub Projects V2 kanban boards: create boards, columns, move items, sync status.

## Prerequisites

`gh` CLI authenticated with `project` and `read:project` OAuth scopes. See [references/gh-auth-scopes.md](references/gh-auth-scopes.md)
<!-- TOC: 1 Why project scopes are required - Default gh auth login does not include them | 2 Complete list of required OAuth scopes - All scopes needed for agent operations | 3 How to check current scopes - Verifying your authentication | 4 How to add missing scopes - Interactive browser flow required | 5 Pre-flight validation command - One-liner to check before operations | 6 Scope provisioning is a manual pre-deployment step - Cannot be automated by agents | 7 Troubleshooting - Common scope-related errors -->

## Instructions

1. Verify scopes: `gh auth status 2>&1 | grep -q "project" || echo "ERROR: gh auth refresh -h github.com -s project,read:project"`
2. Query board/column IDs via GraphQL. See [references/kanban-procedures.md](references/kanban-procedures.md)
<!-- TOC: Table of Contents | Add new columns safely (preserves existing columns and their assignments) -->
3. Execute procedure. NEVER call `updateProjectV2Field` directly -- use `scripts/gh-project-add-columns.py`
4. Verify JSON output. Columns: [references/kanban-column-system.md](references/kanban-column-system.md)
<!-- TOC: Table of Contents | Standard 8-Column System | Available Scripts -->

Copy this checklist and track your progress:

- [ ] Verify OAuth scopes with pre-flight check
- [ ] Query board/column IDs, execute procedure from [references/kanban-procedures.md](references/kanban-procedures.md)
- [ ] Confirm JSON output matches expected format

## Output

JSON from GraphQL mutations and board state reports.

## Examples

**Input:** `move-item --project 42 --item ITEM_ID --column "AI Review"`
**Output:** `{"updateProjectV2ItemFieldValue":{"projectV2Item":{"id":"ITEM_ID"}}}`
See [references/kanban-examples.md](references/kanban-examples.md)
<!-- TOC: Example 1: Pre-Flight Scope Check | Example 2: Create Task and Add to Board | Example 3: Move Item to AI Review | Example 4: Safe Guard Before Closing Issue -->

## Error Handling

See [references/kanban-error-handling.md](references/kanban-error-handling.md)
<!-- TOC: Table of Contents | Error Reference Table | Output Specification | Script Output Rules -->

## Resources

- [Auth & OAuth Scopes](references/gh-auth-scopes.md)
- [GraphQL Mutations](references/github-projects-v2-graphql.md)
- [Pitfalls & Guards](references/kanban-pitfalls.md)
- [Procedures](references/kanban-procedures.md)
- [Column System](references/kanban-column-system.md)
- [Checklists](references/kanban-checklist.md)
- [Error Handling](references/kanban-error-handling.md)
- [Examples](references/kanban-examples.md)
