# Agent Pre-Work Sync Checklist - Part 1: GitHub Issues & Labels

> This is Part 1 of the Agent Pre-Work Sync Checklist.
> See [AGENT_SYNC_CHECKLIST.md](./AGENT_SYNC_CHECKLIST.md) for the full index.

---

## 1. GitHub Issue Verification

### 1.1. Issue Exists
```bash
# Verify issue exists and is accessible
gh issue view {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --json number,title,state,assignees,labels | jq
```

**Expected Output:**
- Issue number matches task assignment
- Issue state is "OPEN"
- Issue has descriptive title with `[{{TASK_ID}}]` prefix

**If Failed:**
- Contact orchestrator to create issue
- Do not proceed without valid issue

### 1.2. Issue Assigned to Agent
```bash
# Check assignee
gh issue view {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --json assignees --jq '.assignees[].login'
```

**Expected Output:**
- Your GitHub username appears in assignees list

**If Failed:**
```bash
# Self-assign if you have permission
gh issue edit {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --add-assignee "@me"

# Or request orchestrator to assign
```

**Checkpoint:**
- [ ] Issue exists and is accessible
- [ ] Issue is assigned to me

---

## 2. Issue Labels Verification

### 2.1. Status Label Present
```bash
# Check for status label
gh issue view {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --json labels --jq '.labels[].name' | grep "^status:"
```

**Expected Output:**
- `status:backlog` (before starting)
- Will change to `status:in-progress` when you start work

**If Failed:**
```bash
# Add status:backlog label
gh issue edit {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --add-label "status:backlog"
```

### 2.2. Required Labels Present
```bash
# Verify all required labels
gh issue view {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --json labels --jq '.labels[].name'
```

**Expected Labels:**
- `status:*` (status indicator)
- `priority:*` (priority level)
- `platform:*` (target platform)
- `type:*` (task type)
- Optional: `toolchain:*`, `agent:*`

**If Failed:**
```bash
# Add missing labels
gh issue edit {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --add-label "priority:{{PRIORITY}}" \
  --add-label "platform:{{PLATFORM}}" \
  --add-label "type:{{TYPE}}"
```

**Checkpoint:**
- [ ] Issue has status label
- [ ] Issue has priority label
- [ ] Issue has platform label
- [ ] Issue has type label

---

## Next Steps

Continue to [Part 2: Project Board & Toolchain](./AGENT_SYNC_CHECKLIST-part2-project-toolchain.md) for:
- Project Board Verification
- Toolchain Template Verification
- Branch Creation
