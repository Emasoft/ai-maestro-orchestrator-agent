---
name: amoa-kanban-management
description: GitHub Projects V2 kanban board management. Use when creating boards, adding columns, moving items. Trigger with kanban or column requests. Loaded by ai-maestro-orchestrator-agent-main-agent
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
  <!-- TOC: 1 Why project scopes are required - Default gh auth login does not include them | 2 Complete list of required OAuth scopes - All scopes needed for agent operations | 3 How to check current scopes - Verifying your authentication | 4 How to add missing scopes - Interactive browser flow required | 5 Pre-flight validation command - One-liner to check before operations | 6 Scope provisioning is a manual pre-deployment step - Cannot be automated by agents | 7 Troubleshooting - Common scope-related errors -->
- [GraphQL Mutations](references/github-projects-v2-graphql.md)
  <!-- TOC: 1 Querying project fields and their IDs - Getting field and option IDs | 2 Moving an item to a different column - updateProjectV2ItemFieldValue mutation | 3 Adding columns to a field - updateProjectV2Field mutation (DANGER: replaces all options) | 4 Creating a project item from an issue - addProjectV2ItemById mutation | 5 Deleting a project item - deleteProjectV2Item mutation | 6 Common parameter mistakes - fieldId vs projectId confusion | 7 Working examples with gh api graphql - Copy-paste ready commands -->
- [Pitfalls & Guards](references/kanban-pitfalls.md)
  <!-- TOC: 1 Done column auto-closes linked issues - GitHub built-in automation | 1.1 How to detect if an issue was auto-closed | 1.2 Guard: check issue state before attempting gh issue close | 2 updateProjectV2Field replaces ALL options - Data loss risk | 2.1 Why this happens - Option IDs are regenerated | 2.2 Safe column addition procedure | 2.3 Using gh-project-add-columns.py script | 3 gh auth refresh requires interactive browser - Cannot be automated | 4 updateProjectV2Field does not accept projectId - Only fieldId -->
- [Procedures](references/kanban-procedures.md)
  <!-- TOC: PROCEDURE 1: Create Project Board | PROCEDURE 2: Add or Modify Columns | PROCEDURE 3: Move Items Between Columns | PROCEDURE 4: Sync Kanban Status | Verify gh auth has project scopes (pre-flight check) | Create the GitHub Project via `gh project create` | Add the 8 standard columns using `gh-project-add-columns.py` | Link the repository to the project | Register the project number in `.github/project.json` | ALWAYS use the safe column adder script: `scripts/gh-project-add-columns.py` | NEVER manually call `updateProjectV2Field` without preserving existing option IDs | Verify existing assignments survived after the mutation | Get the project item ID and field ID | Get the option ID for the target column | Execute `gh project item-edit` with the correct IDs | If moving to "Done", check if the linked issue was auto-closed (see pitfalls) | Run the sync script: `amoa_sync_kanban.py` | Verify label status matches board column | Resolve any conflicts (board takes precedence for manual moves) -->
- [Column System](references/kanban-column-system.md)
  <!-- TOC: Standard 8-Column System | Available Scripts -->
- [Checklists](references/kanban-checklist.md)
  <!-- TOC: Step-by-Step Instructions | Pre-Flight Checklist | Board Setup Checklist | Task Management Checklist -->
- [Error Handling](references/kanban-error-handling.md)
  <!-- TOC: Error Reference Table | Output Specification | Script Output Rules -->
- [Examples](references/kanban-examples.md)
  <!-- TOC: Example 1: Pre-Flight Scope Check | Example 2: Create Task and Add to Board | Example 3: Move Item to AI Review | Example 4: Safe Guard Before Closing Issue -->
