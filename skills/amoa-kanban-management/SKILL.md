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
<!-- TOC: GitHub CLI Authentication and OAuth Scopes | Why project scopes are required | Complete list of required OAuth scopes | How to check current scopes | How to add missing scopes | Pre-flight validation command | Scope provisioning is a manual pre-deployment step | Troubleshooting -->

## Instructions

1. Verify scopes: `gh auth status 2>&1 | grep -q "project" || echo "ERROR: gh auth refresh -h github.com -s project,read:project"`
2. Query board/column IDs via GraphQL. See [references/kanban-procedures.md](references/kanban-procedures.md)
<!-- TOC: PROCEDURE 4: Sync Kanban Status | PROCEDURE 1: Create Project Board -->
3. Execute procedure. NEVER call `updateProjectV2Field` directly -- use `scripts/gh-project-add-columns.py`
4. Verify JSON output. Columns: [references/kanban-column-system.md](references/kanban-column-system.md)
<!-- TOC: Standard 8-Column System | Available Scripts -->

Copy this checklist and track your progress:

- [ ] Verify OAuth scopes with pre-flight check
- [ ] Query board/column IDs, execute procedure from [references/kanban-procedures.md](references/kanban-procedures.md)
<!-- TOC: PROCEDURE 4: Sync Kanban Status | PROCEDURE 1: Create Project Board -->
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
<!-- TOC: Error Reference Table | Output Specification | Script Output Rules -->

## Resources

- [Auth & OAuth Scopes](references/gh-auth-scopes.md)
  - 1.1 Why project scopes are required
  - 1.2 Complete list of required OAuth scopes
  - 1.3 How to check current scopes
  - ...
- [GraphQL Mutations](references/github-projects-v2-graphql.md)
  - 2.1 Querying project fields and their IDs
  - 2.2 Moving an item to a different column
  - 2.3 Adding columns to a field
  - ...
- [Pitfalls & Guards](references/kanban-pitfalls.md)
  - 3.1 Done column auto-closes linked issues
    - What happens
    - 3.1.1 How to detect if an issue was auto-closed
  - ...
- [Procedures](references/kanban-procedures.md)
    - PROCEDURE 1: Create Project Board
    - PROCEDURE 2: Add or Modify Columns
    - PROCEDURE 3: Move Items Between Columns
  - ...
- [Column System](references/kanban-column-system.md)
  - Standard 8-Column System
  - Available Scripts
- [Checklists](references/kanban-checklist.md)
  - Step-by-Step Instructions
  - Pre-Flight Checklist
  - Board Setup Checklist
  - ...
- [Error Handling](references/kanban-error-handling.md)
  - Error Reference Table
  - Output Specification
  - Script Output Rules
- [Examples](references/kanban-examples.md)
    - Example 1: Pre-Flight Scope Check
    - Example 2: Create Task and Add to Board
    - Example 3: Move Item to AI Review
  - ...
