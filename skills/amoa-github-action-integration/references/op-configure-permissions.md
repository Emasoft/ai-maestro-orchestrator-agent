---
procedure: support-skill
workflow-instruction: support
---

# Operation: Configure Repository Permissions


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Understand Permission Requirements](#step-1-understand-permission-requirements)
  - [Step 2: Configure Workflow Permissions (Default)](#step-2-configure-workflow-permissions-default)
  - [Step 3: Set Permissions in Workflow File](#step-3-set-permissions-in-workflow-file)
  - [Step 4: Permission Reference](#step-4-permission-reference)
  - [Step 5: Configure Branch Protection (Recommended)](#step-5-configure-branch-protection-recommended)
  - [Step 6: Verify Permissions](#step-6-verify-permissions)
  - [Step 7: Handle Permission Errors](#step-7-handle-permission-errors)
- [Output](#output)
- [Error Handling](#error-handling)
- [Security Considerations](#security-considerations)
- [Example](#example)
- [Checklist](#checklist)

## When to Use

Use this operation when configuring GitHub repository permissions for Claude Code Action workflows.

## Prerequisites

- Repository admin access
- Understanding of required permissions per workflow type

## Procedure

### Step 1: Understand Permission Requirements

| Workflow Type | Required Permissions |
|---------------|---------------------|
| PR Review | contents: read, pull-requests: write |
| Mention Response | contents: read, issues: write, pull-requests: write |
| Issue Triage | contents: read, issues: write |
| Code Modification | contents: write |

### Step 2: Configure Workflow Permissions (Default)

1. Navigate to repository **Settings**
2. Click **Actions > General** in sidebar
3. Scroll to **Workflow permissions**
4. Select **Read and write permissions**
5. Check **Allow GitHub Actions to create and approve pull requests**
6. Click **Save**

### Step 3: Set Permissions in Workflow File

For fine-grained control, add permissions block:

```yaml
permissions:
  contents: read        # Read repository files
  pull-requests: write  # Comment on PRs
  issues: write         # Label and comment on issues
```

### Step 4: Permission Reference

```yaml
# Read-only operations (code review, mention response)
permissions:
  contents: read
  pull-requests: write
  issues: write

# Code modification (auto-fix, formatting)
permissions:
  contents: write
  pull-requests: write

# Full access (rare, use cautiously)
permissions:
  contents: write
  pull-requests: write
  issues: write
  actions: write
```

### Step 5: Configure Branch Protection (Recommended)

1. Go to **Settings > Branches**
2. Add branch protection rule for `main`
3. Configure:
   - Require pull request reviews
   - Require status checks (include Claude review)
   - Do not allow bypassing

### Step 6: Verify Permissions

Test workflow with minimal permissions first:

```yaml
# Test workflow
name: Permission Test

on:
  workflow_dispatch:

permissions:
  contents: read
  issues: write

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Test issue comment
        run: |
          gh issue comment 1 --body "Permission test successful"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Step 7: Handle Permission Errors

If workflow fails with permission errors:

```yaml
# Check current permissions in workflow run
- name: Debug permissions
  run: |
    echo "Token permissions:"
    gh api -H "Accept: application/vnd.github+json" /repos/${{ github.repository }}
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| Workflow Permissions | String | Read and write / Read-only |
| PR Creation | Boolean | Whether PR creation is allowed |
| Branch Protection | Boolean | Whether protection is configured |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "Resource not accessible" | Missing write permission | Enable write in settings |
| "Cannot comment on PR" | pull-requests: write missing | Add permission to workflow |
| "Cannot add labels" | issues: write missing | Add permission to workflow |
| "Push declined" | Branch protection | Adjust rules or use PR |

## Security Considerations

1. **Principle of least privilege** - Only grant needed permissions
2. **Branch protection** - Prevent direct pushes to main
3. **Required reviews** - Human approval before merge
4. **No force push** - Protect history
5. **Audit logs** - Review workflow runs regularly

## Example

```yaml
# Complete workflow with permissions
name: Claude PR Review

on:
  pull_request:
    types: [opened, synchronize]

# Explicit permissions (recommended over defaults)
permissions:
  contents: read
  pull-requests: write

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: anthropics/claude-code-action@v1
        with:
          prompt: "Review this PR"
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Checklist

- [ ] Navigate to repository Settings
- [ ] Go to Actions > General
- [ ] Enable "Read and write permissions"
- [ ] Enable "Allow GitHub Actions to create and approve pull requests"
- [ ] Save settings
- [ ] Add permissions block to workflow file
- [ ] Configure branch protection (recommended)
- [ ] Test workflow permissions
- [ ] Verify no permission errors in logs
