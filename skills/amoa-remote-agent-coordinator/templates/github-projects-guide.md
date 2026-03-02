# GitHub Projects Interaction Guide

## Purpose

This guide teaches remote agents how to interact with GitHub Projects kanban boards when working on tasks.

---

## Overview

GitHub Projects is used to track task status visually. As a remote agent, you MUST update the project board as you work.

---

## Required Tools

All GitHub Projects operations use the `gh` CLI tool:

```bash
# Verify gh is authenticated
gh auth status

# List projects
gh project list --owner {OWNER}

# View project items
gh project item-list {PROJECT_NUMBER} --owner {OWNER}
```

---

## Task Status Columns

| Column | When to Move Here |
|--------|-------------------|
| Backlog | Entry point for new tasks |
| Todo | Ready to start |
| In Progress | Active work |
| AI Review | Integrator reviews ALL tasks |
| Human Review | User reviews BIG tasks only |
| Merge/Release | Ready to merge |
| Done | Completed |
| Blocked | Blocked at any stage |

---

## Updating Task Status

### Move Issue to "In Progress"

When you ACK a task:

```bash
# Get the item ID first
gh project item-list {PROJECT_NUM} --owner {OWNER} --format json | \
  jq '.items[] | select(.content.number == {ISSUE_NUM})'

# Update status field
gh project item-edit --project-id {PROJECT_ID} --id {ITEM_ID} \
  --field-id {STATUS_FIELD_ID} --single-select-option-id {IN_PROGRESS_OPTION_ID}
```

### Simplified: Use Issue Labels

If project field IDs are complex, use labels instead:

```bash
# Add "in-progress" label
gh issue edit {ISSUE_NUM} --add-label "status:in-progress"

# Remove old status label
gh issue edit {ISSUE_NUM} --remove-label "status:todo"
```

---

## Status Labels Convention

| Label | Meaning |
|-------|---------|
| `status:backlog` | Entry point for new tasks |
| `status:todo` | Ready to start |
| `status:in-progress` | Currently being worked on |
| `status:ai-review` | Integrator reviewing task |
| `status:human-review` | User reviewing big task |
| `status:merge-release` | Ready to merge |
| `status:blocked` | Waiting for dependency |
| `status:done` | Completed and merged |

---

## Workflow: From ACK to Done

### Step 1: Receive Task (ACK)

```bash
# Update issue status
gh issue edit {ISSUE_NUM} --add-label "status:in-progress"
gh issue edit {ISSUE_NUM} --remove-label "status:todo"

# Add comment
gh issue comment {ISSUE_NUM} --body "[ACK] Starting work."
```

### Step 2: Create Branch

```bash
# Create feature branch named after issue
git checkout -b feature/GH-{ISSUE_NUM}-{short-description}
git push -u origin feature/GH-{ISSUE_NUM}-{short-description}
```

### Step 3: Progress Updates

```bash
# Add progress comment to issue
gh issue comment {ISSUE_NUM} --body "[PROGRESS] Checkpoint 2: Implementation 60% complete"
```

### Step 4: Create PR

```bash
# Create PR linked to issue
gh pr create --title "feat: {description}" \
  --body "Closes #{ISSUE_NUM}

## Summary
- {changes made}

## Verification
\`\`\`
{test output}
\`\`\`
"

# Update issue status
gh issue edit {ISSUE_NUM} --add-label "status:ai-review"
gh issue edit {ISSUE_NUM} --remove-label "status:in-progress"
```

### Step 5: After Merge

```bash
# The "Closes #X" in PR body auto-closes issue on merge
# But verify status updated
gh issue view {ISSUE_NUM}
```

---

## Commenting on Issues

### Progress Comment Format

```bash
gh issue comment {ISSUE_NUM} --body "## Progress Update

**Status**: In Progress
**Checkpoint**: 2/4
**Progress**: 50%

### Completed
- [x] Research existing code
- [x] Design implementation

### In Progress
- [ ] Write core logic

### Upcoming
- [ ] Add tests
- [ ] Create PR"
```

### Blocker Comment Format

```bash
gh issue comment {ISSUE_NUM} --body "## Blocked

**Type**: Dependency
**Blocker**: Waiting for #42 to merge
**Impact**: Cannot proceed with database integration

**Options**:
1. Wait for #42 (recommended)
2. Mock database layer temporarily
3. Split into two PRs

@orchestrator Please advise."
```

---

## Linking PRs to Issues

Always link PRs to their issues:

```bash
# In PR body, use one of:
Closes #42      # Auto-closes issue on merge
Fixes #42       # Auto-closes issue on merge
Resolves #42    # Auto-closes issue on merge
Related to #42  # Links but doesn't auto-close
```

---

## Custom Project Fields

If the project has custom fields:

```bash
# List project fields
gh project field-list {PROJECT_NUM} --owner {OWNER}

# Update custom field (e.g., Priority)
gh project item-edit --project-id {PROJECT_ID} --id {ITEM_ID} \
  --field-id {PRIORITY_FIELD_ID} --single-select-option-id {HIGH_OPTION_ID}
```

---

## Common Fields and Values

| Field | Typical Values |
|-------|----------------|
| Status | Backlog, Todo, In Progress, AI Review, Human Review, Merge/Release, Done, Blocked |
| Priority | P0-Critical, P1-High, P2-Medium, P3-Low |
| Component | Frontend, Backend, API, Database, CI/CD |
| Platform | macOS, Windows, Linux, Cross-platform |
| Sprint | Week 1, Week 2, etc. |

---

## Error Handling

### If gh project commands fail

```bash
# Check authentication
gh auth status

# Check project access
gh project list --owner {OWNER}

# Fall back to labels
gh issue edit {ISSUE_NUM} --add-label "{status-label}"
```

### If issue is locked

Report to orchestrator:
```
[BLOCKED] GH-42 - Issue locked, cannot update status
Need: Issue to be unlocked or orchestrator to update
```

---

## Summary Checklist

When working on a GitHub issue:

- [ ] ACK sent with task ID
- [ ] Issue moved to "In Progress"
- [ ] Feature branch created with issue number
- [ ] Progress comments added at checkpoints
- [ ] PR created with "Closes #X" in body
- [ ] Issue moved to "AI Review"
- [ ] Completion report sent after merge
