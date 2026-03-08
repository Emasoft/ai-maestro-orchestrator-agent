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

Manages GitHub Projects V2 kanban boards: creating boards, columns, moving items, and syncing status.

## Prerequisites

1. GitHub CLI (`gh`) installed and authenticated
2. **OAuth scopes**: `project` and `read:project` scopes required. See [references/gh-auth-scopes.md](references/gh-auth-scopes.md)
   <!-- TOC: Troubleshooting - Common scope-related errors | How to check current scopes - Verifying your authentication -->
3. Read **amoa-task-distribution** and **amoa-label-taxonomy** skills
4. Standard 8-column system: Backlog, Todo, In Progress, AI Review, Human Review, Merge/Release, Done, Blocked

## Critical Pre-Flight Check

**Before ANY kanban operation**, verify OAuth scopes:

```bash
gh auth status 2>&1 | grep -q "project" || echo "ERROR: Run: gh auth refresh -h github.com -s project,read:project"
```

## Core Procedures

See: [references/kanban-procedures.md](references/kanban-procedures.md)
<!-- TOC: PROCEDURE 4: Sync Kanban Status | PROCEDURE 1: Create Project Board -->

**WARNING:** NEVER call `updateProjectV2Field` directly -- it REPLACES all options. Use `scripts/gh-project-add-columns.py`.

## Column System

See: [references/kanban-column-system.md](references/kanban-column-system.md)
<!-- TOC: Standard 8-Column System | Available Scripts -->

## Output

JSON responses from GitHub GraphQL mutations, status confirmations, and board state reports. See: [references/kanban-error-handling.md](references/kanban-error-handling.md)
<!-- TOC: Error Reference Table | Output Specification | Script Output Rules -->

## Error Handling

See: [references/kanban-error-handling.md](references/kanban-error-handling.md)
<!-- TOC: Error Reference Table | Output Specification | Script Output Rules -->

## Examples

See: [references/kanban-examples.md](references/kanban-examples.md)
<!-- TOC: Example 1: Pre-Flight Scope Check | Example 3: Move Item to AI Review -->

**Input:** `move-item --project 42 --item ITEM_ID --column "AI Review"`
**Output:** `{"updateProjectV2ItemFieldValue":{"projectV2Item":{"id":"ITEM_ID"}}}`

## Instructions

1. Run the pre-flight OAuth scope check before any kanban operation
2. Identify target board and column IDs using GraphQL queries
3. Execute the appropriate procedure from kanban-procedures.md
4. Verify JSON output matches expected format
5. Never call `updateProjectV2Field` directly — use provided scripts

Copy this checklist and track your progress:

- [ ] Verify OAuth scopes with pre-flight check
- [ ] Identify target board and column IDs
- [ ] Execute procedure from [references/kanban-procedures.md](references/kanban-procedures.md)
<!-- TOC: PROCEDURE 4: Sync Kanban Status | PROCEDURE 1: Create Project Board -->
- [ ] Confirm JSON output matches expected format
- [ ] Never call `updateProjectV2Field` directly -- use provided scripts

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
- **amoa-task-distribution** - Task assignment
- **amoa-label-taxonomy** - Label categories
- **amoa-progress-monitoring** - Agent tracking

**Version:** 1.0.0 | **Last Updated:** 2026-02-15 | **Audience:** Orchestrator Agents
