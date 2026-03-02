---
name: eoa-kanban-management
description: GitHub Projects V2 kanban board management. Use when creating boards, adding columns, moving items. Trigger with kanban or column requests.
license: Apache-2.0
compatibility: Requires gh CLI authenticated with project scopes. Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
context: fork
user-invocable: false
agent: eoa-main
workflow-instruction: "Steps 12, 13, 14, 15"
procedure: "proc-populate-kanban, proc-update-kanban-status, proc-add-columns, proc-sync-kanban"
---

# Kanban Board Management Skill

## Overview

This skill teaches the Orchestrator (EOA) how to manage GitHub Projects V2 kanban boards. It covers creating project boards, adding and modifying columns, moving items between columns, and synchronizing task status. This skill also documents critical pitfalls discovered during production use that can cause data loss if not followed.

## Prerequisites

1. GitHub CLI (`gh`) installed and authenticated
2. **OAuth scopes**: `project` and `read:project` scopes MUST be added to `gh auth`. See [references/gh-auth-scopes.md](references/gh-auth-scopes.md) for details
3. Read **eoa-task-distribution** for task assignment workflow
4. Read **eoa-label-taxonomy** for label usage
5. Understanding of the 8-column kanban system (Backlog, Todo, In Progress, AI Review, Human Review, Merge/Release, Done, Blocked)

---

## Critical Pre-Flight Check

**Before ANY kanban operation**, verify OAuth scopes:

```bash
gh auth status 2>&1 | grep -q "project" || echo "ERROR: Missing project scope. Run: gh auth refresh -h github.com -s project,read:project"
```

If scopes are missing, the agent CANNOT proceed. See [references/gh-auth-scopes.md](references/gh-auth-scopes.md) for how to add scopes.

---

## Core Procedures

### PROCEDURE 1: Create Project Board

**When to use:** When setting up a new project's kanban board for the first time.

**Steps:**
1. Verify gh auth has project scopes (pre-flight check)
2. Create the GitHub Project via `gh project create`
3. Add the 8 standard columns using `gh-project-add-columns.sh`
4. Link the repository to the project
5. Register the project number in `.github/project.json`

### PROCEDURE 2: Add or Modify Columns

**When to use:** When adding new status columns to an existing project board.

**CRITICAL WARNING:** The `updateProjectV2Field` GraphQL mutation REPLACES all options. If you do not include existing option IDs in the mutation, ALL existing column assignments will be lost. See [references/kanban-pitfalls.md](references/kanban-pitfalls.md) Section 3.2 for details.

**Steps:**
1. ALWAYS use the safe column adder script: `scripts/gh-project-add-columns.sh`
2. NEVER manually call `updateProjectV2Field` without preserving existing option IDs
3. Verify existing assignments survived after the mutation

**Script usage:**
```bash
# Add new columns safely (preserves existing columns and their assignments)
./scripts/gh-project-add-columns.sh --project <number> --field "Status" --add "AI Review" --add "Human Review"
```

### PROCEDURE 3: Move Items Between Columns

**When to use:** When updating a task's kanban status (e.g., moving from "In Progress" to "AI Review").

**Steps:**
1. Get the project item ID and field ID
2. Get the option ID for the target column
3. Execute `gh project item-edit` with the correct IDs
4. If moving to "Done", check if the linked issue was auto-closed (see pitfalls)

### PROCEDURE 4: Sync Kanban Status

**When to use:** When synchronizing label-based status with the GitHub Project board, or vice versa.

**Steps:**
1. Run the sync script: `eoa_sync_kanban.py`
2. Verify label status matches board column
3. Resolve any conflicts (board takes precedence for manual moves)

---

## Available Scripts

The EOA plugin includes these kanban management scripts in `scripts/`:

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `eoa_kanban_manager.py` | Create tasks, assign agents, update status, check ready tasks | Day-to-day kanban operations |
| `eoa_sync_kanban.py` | Sync label status with GitHub Project board | After manual board changes or to reconcile state |
| `check-github-projects.sh` | Query project board for pending items | Stop-hook checks, status queries |
| `gh-project-add-columns.sh` | Safely add columns preserving existing assignments | When adding new columns to a live board |

---

## Kanban Column System

The standard 8-column kanban system:

| Column | Status Label | Description |
|--------|-------------|-------------|
| Backlog | `status:backlog` | Tasks identified but not yet scheduled |
| Todo | `status:todo` | Tasks scheduled for current sprint |
| In Progress | `status:in-progress` | Tasks actively being worked on |
| AI Review | `status:ai-review` | Code submitted for automated review |
| Human Review | `status:human-review` | Code awaiting human review |
| Merge/Release | `status:merge-release` | Approved and ready to merge |
| Done | `status:done` | Completed tasks |
| Blocked | `status:blocked` | Tasks blocked by dependencies |

---

## Reference Documentation

### GitHub CLI Authentication and OAuth Scopes ([references/gh-auth-scopes.md](references/gh-auth-scopes.md))

- 1.1 Why project scopes are required - Default gh auth login does not include them
- 1.2 Complete list of required OAuth scopes - All scopes needed for agent operations
- 1.3 How to check current scopes - Verifying your authentication
- 1.4 How to add missing scopes - Interactive browser flow required
- 1.5 Pre-flight validation command - One-liner to check before operations
- 1.6 Scope provisioning is a manual pre-deployment step - Cannot be automated by agents
- 1.7 Troubleshooting - Common scope-related errors

### GitHub Projects V2 GraphQL Mutations ([references/github-projects-v2-graphql.md](references/github-projects-v2-graphql.md))

- 2.1 Querying project fields and their IDs - Getting field and option IDs
- 2.2 Moving an item to a different column - updateProjectV2ItemFieldValue mutation
- 2.3 Adding columns to a field - updateProjectV2Field mutation (DANGER: replaces all options)
- 2.4 Creating a project item from an issue - addProjectV2ItemById mutation
- 2.5 Deleting a project item - deleteProjectV2Item mutation
- 2.6 Common parameter mistakes - fieldId vs projectId confusion
- 2.7 Working examples with gh api graphql - Copy-paste ready commands

### Kanban Pitfalls and Guards ([references/kanban-pitfalls.md](references/kanban-pitfalls.md))

- 3.1 Done column auto-closes linked issues - GitHub built-in automation
  - 3.1.1 How to detect if an issue was auto-closed
  - 3.1.2 Guard: check issue state before attempting gh issue close
- 3.2 updateProjectV2Field replaces ALL options - Data loss risk
  - 3.2.1 Why this happens - Option IDs are regenerated
  - 3.2.2 Safe column addition procedure
  - 3.2.3 Using gh-project-add-columns.sh script
- 3.3 gh auth refresh requires interactive browser - Cannot be automated
- 3.4 updateProjectV2Field does not accept projectId - Only fieldId

---

## Instructions

Follow these steps to manage the kanban board:

1. **Before first use**: Verify OAuth scopes (Section "Critical Pre-Flight Check")
2. **Creating a board**: Follow PROCEDURE 1
3. **Adding columns**: ALWAYS use `gh-project-add-columns.sh` (PROCEDURE 2)
4. **Moving items**: Follow PROCEDURE 3
5. **Syncing status**: Follow PROCEDURE 4

### Checklist

Copy this checklist and track your progress:

**Pre-Flight:**
- [ ] Verify gh CLI is installed (`which gh`)
- [ ] Verify gh is authenticated (`gh auth status`)
- [ ] Verify project scopes are present (`gh auth status 2>&1 | grep project`)
- [ ] If scopes missing, request human to run `gh auth refresh -h github.com -s project,read:project`

**Board Setup:**
- [ ] Create GitHub Project: `gh project create --owner Emasoft --title "<project>"`
- [ ] Add standard 8 columns using `gh-project-add-columns.sh`
- [ ] Save project number to `.github/project.json`

**Task Management:**
- [ ] Create task issues with proper labels (`assign:*`, `priority:*`, `status:*`)
- [ ] Add issues to project board
- [ ] Move items between columns as status changes
- [ ] When moving to Done: check if issue was auto-closed before attempting `gh issue close`

---

## Output

After executing kanban operations, the agent produces:

- **Board creation**: Project number (integer) and project URL. Store the project number in `.github/project.json` for future reference.
- **Column addition**: Confirmation message listing preserved columns and newly added columns. Verify no assignments were lost.
- **Item moves**: Updated item status. Verify the item appears in the target column with `gh project item-list`.
- **Status sync**: Reconciliation report showing label-to-column mappings and any conflicts resolved.
- **Error case**: Error message with cause and remediation steps (see Error Handling below).

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `missing required scopes [project read:project]` | gh auth lacks project scopes | See [gh-auth-scopes.md](references/gh-auth-scopes.md) Section 1.4 |
| `InputObject doesn't accept argument 'projectId'` | Wrong parameter name | Use `fieldId` only. See [github-projects-v2-graphql.md](references/github-projects-v2-graphql.md) Section 2.6 |
| Items lost column assignments after adding columns | Used raw `updateProjectV2Field` | See [kanban-pitfalls.md](references/kanban-pitfalls.md) Section 3.2 |
| Issue auto-closed when moved to Done | GitHub Projects V2 built-in automation | See [kanban-pitfalls.md](references/kanban-pitfalls.md) Section 3.1 |
| `gh auth refresh` fails in non-interactive session | Requires browser-based OAuth flow | Must be done by human before agent deployment |

---

## Examples

### Example 1: Pre-Flight Scope Check

```bash
# Check if project scopes are available
if ! gh auth status 2>&1 | grep -q "project"; then
  echo "ERROR: Missing project scope."
  echo "A human must run: gh auth refresh -h github.com -s project,read:project"
  echo "This requires interactive browser approval."
  exit 1
fi
echo "OK: Project scopes are available."
```

### Example 2: Create Task and Add to Board

```bash
# 1. Create the issue
ISSUE_URL=$(gh issue create --repo Emasoft/myproject \
  --title "Implement feature X" \
  --body "Description..." \
  --label "assign:epa-impl-01,priority:high,status:todo")

ISSUE_NUMBER=$(echo "$ISSUE_URL" | grep -oE '[0-9]+$')

# 2. Add to project board
gh project item-add <project-number> --owner Emasoft --url "$ISSUE_URL"
```

### Example 3: Move Item to AI Review

```bash
# Get the project item ID and Status field ID
ITEM_ID=$(gh project item-list <project-number> --owner Emasoft --format json | \
  jq -r ".items[] | select(.content.number == $ISSUE_NUMBER) | .id")

# Move to AI Review column
gh project item-edit \
  --project-id <project-id> \
  --id "$ITEM_ID" \
  --field-id <status-field-id> \
  --single-select-option-id <ai-review-option-id>
```

### Example 4: Safe Guard Before Closing Issue

```bash
# Check if issue is already closed (Done column may auto-close it)
STATE=$(gh issue view $ISSUE_NUMBER --repo Emasoft/myproject --json state -q '.state')
if [ "$STATE" = "CLOSED" ]; then
  echo "Issue #$ISSUE_NUMBER is already closed (likely auto-closed by Done column)"
else
  gh issue close $ISSUE_NUMBER --repo Emasoft/myproject --comment "Task completed."
fi
```

---

## Resources

- [GitHub CLI Authentication and OAuth Scopes](references/gh-auth-scopes.md)
- [GitHub Projects V2 GraphQL Mutations](references/github-projects-v2-graphql.md)
- [Kanban Pitfalls and Guards](references/kanban-pitfalls.md)
- **eoa-task-distribution** skill - Task assignment workflow
- **eoa-label-taxonomy** skill - Label categories and cardinality
- **eoa-progress-monitoring** skill - Agent tracking and escalation

---

**Version:** 1.0.0
**Last Updated:** 2026-02-15
**Target Audience:** Orchestrator Agents
**Difficulty Level:** Intermediate
