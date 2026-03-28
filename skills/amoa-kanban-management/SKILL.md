---
name: amoa-kanban-management
description: GitHub Projects V2 kanban board management via AI Maestro scripts. Use when creating tasks, moving cards, listing items. Trigger with kanban, task, or board requests.
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
<!-- TOC: Troubleshooting - Common scope-related errors | How to check current scopes - Verifying your authentication -->

## Instructions

1. Verify OAuth scopes: `gh auth status 2>&1 | grep -q "project" || echo "ERROR: gh auth refresh -h github.com -s project,read:project"`
2. Use AI Maestro kanban scripts for all operations:
   - **Create task:** `amp-kanban-create-task.sh "<title>" --repo <repo> --assignee <agent>`
   - **Move card:** `amp-kanban-move.sh <itemId> <status>` (status: backlog, todo, in_progress, review, done)
   - **List tasks:** `amp-kanban-list.sh [--status <status>] [--assignee <agent>]`
3. For advanced GraphQL operations, see [references/kanban-procedures.md](references/kanban-procedures.md)
4. After creating a task, send assignment via AMP: `amp-send.sh <agent> "Task Assignment" "<details>"`
5. When agent reports done: `amp-kanban-move.sh <itemId> review` → notify Integrator

Copy this checklist and track your progress:
- [ ] Verify OAuth scopes
- [ ] Create task with amp-kanban-create-task.sh
- [ ] Assign to agent via amp-send.sh
- [ ] Track status with amp-kanban-list.sh
- [ ] Move cards through columns as work progresses

## Output

JSON from GraphQL mutations and board state reports.

## Examples

**Input:** `move-item --project 42 --item ITEM_ID --column "AI Review"`
**Output:** `{"updateProjectV2ItemFieldValue":{"projectV2Item":{"id":"ITEM_ID"}}}`
See [references/kanban-examples.md](references/kanban-examples.md)
<!-- TOC: Example 1: Pre-Flight Scope Check | Example 3: Move Item to AI Review -->

## Error Handling

See [references/kanban-error-handling.md](references/kanban-error-handling.md)
<!-- TOC: Error Reference Table | Output Specification | Script Output Rules -->

## Resources

- [Auth & OAuth Scopes](references/gh-auth-scopes.md)
<!-- TOC: Troubleshooting - Common scope-related errors | How to check current scopes - Verifying your authentication -->
- [GraphQL Mutations](references/github-projects-v2-graphql.md)
<!-- TOC: Deleting a project item - deleteProjectV2Item mutation | Common parameter mistakes - fieldId vs projectId confusion -->
- [Pitfalls & Guards](references/kanban-pitfalls.md)
<!-- TOC: Safe column addition procedure | How to detect if an issue was auto-closed -->
- [Procedures](references/kanban-procedures.md)
<!-- TOC: PROCEDURE 4: Sync Kanban Status | PROCEDURE 1: Create Project Board -->
- [Column System](references/kanban-column-system.md)
<!-- TOC: Available Scripts | Standard 8-Column System -->
- [Checklists](references/kanban-checklist.md)
<!-- TOC: Pre-Flight Checklist | Board Setup Checklist -->
- [Error Handling](references/kanban-error-handling.md)
<!-- TOC: Script Output Rules | Output Specification -->
- [Examples](references/kanban-examples.md)
<!-- TOC: Example 1: Pre-Flight Scope Check | Example 3: Move Item to AI Review -->
