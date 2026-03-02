# Operation: Sync Module with GitHub Issue


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Command Syntax](#command-syntax)
- [What Gets Synchronized](#what-gets-synchronized)
- [Steps](#steps)
- [Sync Verification Report](#sync-verification-report)
- [Recovery from Desync](#recovery-from-desync)
  - [Scenario 1: State file is source of truth](#scenario-1-state-file-is-source-of-truth)
  - [Scenario 2: GitHub is source of truth](#scenario-2-github-is-source-of-truth)
  - [Scenario 3: Conflict resolution](#scenario-3-conflict-resolution)
- [Output](#output)
- [Success Criteria](#success-criteria)
- [Error Handling](#error-handling)
- [Orphan Detection](#orphan-detection)
  - [Orphaned Issue (issue without module)](#orphaned-issue-issue-without-module)
  - [Orphaned Module (module without issue)](#orphaned-module-module-without-issue)
- [Automatic Sync Triggers](#automatic-sync-triggers)
- [Important Rules](#important-rules)
- [Label Conventions](#label-conventions)
- [Next Operations](#next-operations)

## Metadata

| Field | Value |
|-------|-------|
| Operation ID | `op-sync-module-github-issue` |
| Procedure | `proc-update-tasks` |
| Workflow Step | Step 16 |
| Trigger | Sync verification or recovery from desync |
| Actor | Orchestrator (EOA) |
| Script | `scripts/github_sync.py` |

---

## Purpose

Ensure the module state file and its linked GitHub Issue are synchronized. This operation detects and fixes inconsistencies between the local state and GitHub.

---

## Prerequisites

- GitHub CLI (gh) authenticated
- State file exists at `design/state/exec-phase.md`
- Module has a linked GitHub Issue

---

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `module_id` | Optional | Specific module to sync (omit for all) |
| `direction` | Optional | `to-github` or `from-github` (default: bidirectional) |

---

## Command Syntax

```bash
# Sync all modules
python3 scripts/github_sync.py sync-all

# Sync specific module
python3 scripts/github_sync.py sync <module_id>

# Verify sync status
python3 scripts/github_sync.py verify

# Force sync state to GitHub
python3 scripts/github_sync.py sync <module_id> --direction to-github

# Force sync GitHub to state
python3 scripts/github_sync.py sync <module_id> --direction from-github
```

---

## What Gets Synchronized

| State File Field | GitHub Issue Field |
|------------------|-------------------|
| `name` | Issue title |
| `acceptance_criteria` | Issue body |
| `priority` | `priority:*` label |
| `status` | `status:*` label |
| `assigned_to` | Issue assignee |

---

## Steps

1. **Load state file**:
   - Parse `design/state/exec-phase.md`
   - Extract module data

2. **Fetch GitHub Issue data**:
   ```bash
   gh issue view <issue_number> --json title,body,labels,assignees
   ```

3. **Compare fields**:
   - Title vs. name
   - Body vs. criteria
   - Labels vs. priority/status
   - Assignees vs. assigned_to

4. **Detect discrepancies**:
   ```
   Module: auth-core (#42)
   - Title: MATCH
   - Body: MISMATCH (state file newer)
   - Priority: MATCH
   - Status: MISMATCH (GitHub newer)
   ```

5. **Resolve discrepancies**:
   - Bidirectional: Use most recent (requires timestamp tracking)
   - to-github: State file is authoritative
   - from-github: GitHub is authoritative

6. **Apply changes**:
   - Update state file if from-github
   - Update GitHub Issue if to-github

7. **Report results**

---

## Sync Verification Report

```
GitHub Sync Verification Report
===============================
Checked at: 2025-02-05T15:30:00Z

Module: auth-core (#42)
  Title:    MATCH
  Body:     MATCH
  Priority: MATCH
  Status:   MATCH
  Assignee: MATCH
  Result:   IN SYNC

Module: user-profile (#43)
  Title:    MATCH
  Body:     MISMATCH
  Priority: MATCH
  Status:   MATCH
  Assignee: MATCH
  Result:   NEEDS SYNC

Summary: 1 of 2 modules in sync
Action required: Run sync for user-profile
```

---

## Recovery from Desync

### Scenario 1: State file is source of truth

When local changes should propagate to GitHub:

```bash
python3 scripts/github_sync.py sync auth-core --direction to-github
```

### Scenario 2: GitHub is source of truth

When GitHub was updated manually and state file needs update:

```bash
python3 scripts/github_sync.py sync auth-core --direction from-github
```

### Scenario 3: Conflict resolution

When both have changes:

1. Verify report shows specific conflicts
2. Decide which version is correct
3. Run sync with appropriate direction
4. Verify with `sync verify`

---

## Output

| Output | Format | Description |
|--------|--------|-------------|
| Verification report | Text | Comparison of all fields |
| Sync results | Text | What was updated |
| State file changes | YAML | If from-github |
| GitHub changes | Issue updates | If to-github |

---

## Success Criteria

- All modules show "IN SYNC" after sync
- No orphaned issues (issues without modules)
- No orphaned modules (modules without issues)
- Labels match state file values

---

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Issue not found | Issue deleted | Create new issue or remove module |
| Module not found | State corruption | Add module entry or close orphan issue |
| gh auth failure | Token expired | Run `gh auth login` |
| Rate limit | Too many API calls | Wait and retry |

---

## Orphan Detection

### Orphaned Issue (issue without module)

```
WARNING: Orphaned issue detected
Issue #45 has label 'module' but no corresponding module in state file.

Actions:
1. Add module to state file: /add-module ... --link-issue 45
2. Close as orphan: gh issue close 45 --reason "orphaned"
```

### Orphaned Module (module without issue)

```
WARNING: Orphaned module detected
Module 'auth-core' has github_issue: #99 but issue does not exist.

Actions:
1. Create new issue: gh issue create --title "[Module] Auth Core"
2. Remove module: /remove-module auth-core
```

---

## Automatic Sync Triggers

Sync should run automatically after:

- `/add-module` - Create issue
- `/modify-module` - Update issue
- `/remove-module` - Close issue
- `/prioritize-module` - Update labels
- `/reassign-module` - Update assignee

**Manual sync needed when:**
- GitHub Issue edited directly via UI
- State file edited directly
- Recovery from system failure
- Periodic verification (recommended: daily)

---

## Important Rules

1. **State file is primary** - When in doubt, sync to-github
2. **Never delete issues** - Close with labels, don't delete
3. **Preserve history** - Issue comments are audit trail
4. **Verify after sync** - Always confirm with `sync verify`

---

## Label Conventions

| Label | Meaning |
|-------|---------|
| `module` | This issue tracks a module |
| `priority:critical` | Critical priority |
| `priority:high` | High priority |
| `priority:medium` | Medium priority |
| `priority:low` | Low priority |
| `status:backlog` | In backlog |
| `status:todo` | Not yet started |
| `status:in-progress` | Work underway |
| `status:ai-review` | PR awaiting AI review |
| `status:human-review` | Awaiting human review |
| `status:merge-release` | Ready to merge/release |
| `status:done` | Module finished |
| `status:blocked` | Blocked by dependency |

---

## Next Operations

After sync:
- Verify all modules: `sync verify`
- Continue normal operations
- Schedule periodic verification
