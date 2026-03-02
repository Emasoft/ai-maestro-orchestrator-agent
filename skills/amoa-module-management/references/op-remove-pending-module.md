# Operation: Remove Pending Module


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Command Syntax](#command-syntax)
- [Removal Restrictions](#removal-restrictions)
- [Steps](#steps)
- [Output](#output)
- [Success Criteria](#success-criteria)
- [GitHub Issue Closure](#github-issue-closure)
- [Error Handling](#error-handling)
- [Alternatives to Removal](#alternatives-to-removal)
  - [Scope Reduction Example](#scope-reduction-example)
- [Important Rules](#important-rules)
- [Removal Audit](#removal-audit)
- [Confirmation Dialog](#confirmation-dialog)
- [Next Operations](#next-operations)

## Metadata

| Field | Value |
|-------|-------|
| Operation ID | `op-remove-pending-module` |
| Procedure | `proc-update-tasks` |
| Workflow Step | Step 16 |
| Trigger | Module cancelled or no longer needed |
| Actor | Orchestrator (EOA) |
| Command | `/remove-module` |

---

## Purpose

Remove a module from the orchestration plan that is no longer needed. Only pending modules can be removed. This closes the linked GitHub Issue with appropriate labels.

---

## Prerequisites

- Module exists in state file
- Module status is `pending`
- GitHub CLI (gh) authenticated

---

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `module_id` | Yes | ID of module to remove |
| `force` | No | Skip confirmation prompt |

---

## Command Syntax

```bash
/remove-module <MODULE_ID> [--force]
```

**Examples**:

```bash
# With confirmation
/remove-module oauth-facebook

# Skip confirmation
/remove-module oauth-facebook --force
```

---

## Removal Restrictions

| Module Status | Can Remove? | Reason |
|---------------|-------------|--------|
| `pending` | Yes | No work started |
| `assigned` | No | Agent has accepted |
| `in-progress` | No | Work underway |
| `complete` | No | Work finished |

**Why in-progress modules cannot be removed:**
- Agent has invested effort
- Work may be partially complete
- Sudden removal causes confusion

**Alternative to removal for non-pending**: Reduce scope via `/modify-module`

---

## Steps

1. **Validate module exists**:
   ```bash
   # Check state file for module_id
   grep -A5 "id: \"$MODULE_ID\"" design/state/exec-phase.md
   ```

2. **Check status is `pending`**:
   - If not pending, reject with error
   - Suggest alternatives if in-progress

3. **Confirm removal** (unless --force):
   ```
   Remove module 'oauth-facebook' (#45)?
   This will close GitHub Issue #45 as wontfix.
   Type 'yes' to confirm:
   ```

4. **Remove from state file**:
   - Delete module entry from `modules_status`

5. **Close GitHub Issue**:
   ```bash
   gh issue close <issue_number> \
     --comment "Module removed from orchestration plan" \
     --reason "not planned"

   gh issue edit <issue_number> \
     --add-label "status:wontfix"
   ```

6. **Log the removal** in orchestration log

---

## Output

| Output | Format | Description |
|--------|--------|-------------|
| State file updated | Entry removed | Module no longer in list |
| GitHub Issue closed | Issue state | Closed with wontfix label |
| Console confirmation | Text | "Module '<id>' removed, Issue #N closed" |

---

## Success Criteria

- Module entry removed from state file
- GitHub Issue closed with "not planned" reason
- Issue has `status:wontfix` label
- Removal logged with timestamp and reason

---

## GitHub Issue Closure

```bash
# Close with comment explaining removal
gh issue close <ISSUE_NUMBER> \
  --comment "This module has been removed from the orchestration plan.

Reason: <REMOVAL_REASON>

The feature request can be reconsidered in a future iteration." \
  --reason "not planned"

# Add wontfix label
gh issue edit <ISSUE_NUMBER> --add-label "status:wontfix"
```

---

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Module not found | Wrong ID | Use `/orchestration-status` to list |
| Cannot remove (status) | Not pending | Use alternatives below |
| GitHub close fails | Permissions | Manual close via GitHub UI |

---

## Alternatives to Removal

When you can't remove because status is not pending:

| Situation | Alternative |
|-----------|-------------|
| `assigned` module | Unassign first, then remove |
| `in-progress` module | Reduce scope with `/modify-module` |
| `complete` module | Cannot undo; create correcting module |
| Want to defer | Change priority to low instead |

### Scope Reduction Example

Instead of removing `user-profile` that's in progress:

```bash
# Reduce scope to essentials
/modify-module user-profile \
  --criteria "Display name editing only. Avatar and email change deferred."
```

---

## Important Rules

1. **Only pending modules removable** - Work preservation is paramount
2. **Issue always closed** - Never orphan GitHub Issues
3. **Reason documented** - Log why module was removed
4. **Consider alternatives** - Scope reduction often better than removal

---

## Removal Audit

Log each removal:

```yaml
removal_log:
  - module_id: "oauth-facebook"
    removed_at: "2025-02-05T15:30:00Z"
    removed_by: "orchestrator"
    github_issue: "#45"
    reason: "User decided Facebook login not needed for MVP"
```

---

## Confirmation Dialog

Without --force flag:

```
┌─────────────────────────────────────────────────┐
│           CONFIRM MODULE REMOVAL                │
├─────────────────────────────────────────────────┤
│ Module:       oauth-facebook                    │
│ GitHub Issue: #45                               │
│ Status:       pending                           │
│                                                 │
│ This action will:                               │
│ - Remove module from orchestration plan         │
│ - Close GitHub Issue #45 as wontfix             │
│                                                 │
│ This cannot be undone. Continue? [yes/no]       │
└─────────────────────────────────────────────────┘
```

---

## Next Operations

After removal:
- View updated plan: `/orchestration-status`
- Add replacement if needed: `/add-module`
- Continue with remaining modules
