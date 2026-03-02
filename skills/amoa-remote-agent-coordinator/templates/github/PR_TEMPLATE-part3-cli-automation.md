# PR CLI Commands and Automation

This document provides gh CLI commands and automation scripts for PR management.

**Parent Document:** [PR_TEMPLATE.md](PR_TEMPLATE.md)

---

## gh CLI Command Examples

### Create Pull Request

```bash
# Create PR from current branch
gh pr create \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --title "[{{TASK_ID}}] {{TITLE}}" \
  --body "$(cat pr-body.md)" \
  --base main \
  --head {{BRANCH_NAME}} \
  --label "status:ai-review" \
  --label "priority:{{PRIORITY}}" \
  --label "platform:{{PLATFORM}}" \
  --assignee "{{ASSIGNEE}}" \
  --reviewer "{{REVIEWER}}"
```

### Create PR and Link to Issue

```bash
# PR body should include "Closes #{{ISSUE_NUMBER}}"
gh pr create \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --title "[{{TASK_ID}}] {{TITLE}}" \
  --body "Closes #{{ISSUE_NUMBER}}" \
  --base main
```

### Update PR with Test Results

```bash
# Add comment with test results
gh pr comment {{PR_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --body "## Test Results

Unit Tests: 12/12 passed
Integration Tests: 3/3 passed
Coverage: 94%"
```

### Request Review

```bash
gh pr edit {{PR_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --add-reviewer "{{REVIEWER}}"
```

### Mark PR as Ready for Review

```bash
gh pr ready {{PR_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
```

### Merge PR

```bash
# Squash merge (recommended for EOA)
gh pr merge {{PR_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --squash \
  --delete-branch \
  --body "Verified all tests passing"
```

---

## Automated PR Creation Script

Save as `scripts/create-eoa-pr.sh`:

```bash
#!/bin/bash
set -e

# Usage: ./create-eoa-pr.sh TASK_ID TITLE ISSUE_NUMBER

TASK_ID="$1"
TITLE="$2"
ISSUE_NUMBER="$3"
BRANCH_NAME="${4:-$(git branch --show-current)}"

GITHUB_OWNER="${GITHUB_OWNER:-myorg}"
REPO_NAME="${REPO_NAME:-myrepo}"

# Create PR body
cat > /tmp/pr-body.md << EOF
## Summary

${TITLE}

## Linked Issue

Closes #${ISSUE_NUMBER}

## Changes Made

### Core Changes
- TBD

## Toolchain Verification

**Platform Tested:** TBD
**Toolchain Template:** TBD

### Toolchain Verification Checklist

- [ ] All required tools installed at correct versions
- [ ] Environment setup script ran successfully
- [ ] No missing dependencies reported
- [ ] Build completed without errors
- [ ] Tests ran in correct environment

## Test Results

- **Total:** TBD
- **Passed:** TBD
- **Failed:** 0

## Review Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation updated
EOF

# Create PR
PR_URL=$(gh pr create \
  --repo "$GITHUB_OWNER/$REPO_NAME" \
  --title "[${TASK_ID}] ${TITLE}" \
  --body "$(cat /tmp/pr-body.md)" \
  --base main \
  --head "$BRANCH_NAME" \
  --label "status:ai-review" \
  --json url \
  --jq .url)

echo "PR created: $PR_URL"

# Clean up
rm /tmp/pr-body.md
```

---

## Troubleshooting

### Cannot Create PR

- Verify branch has commits ahead of base
- Check branch exists on remote: `git push -u origin {{BRANCH_NAME}}`
- Verify repository permissions

### PR Not Linked to Issue

- Use "Closes #{{ISSUE_NUMBER}}" in PR body
- Use "Fixes #{{ISSUE_NUMBER}}" for bugs
- GitHub automatically links when PR is merged

### Tests Failing in CI but Passing Locally

- Check toolchain matches CI environment
- Verify all dependencies in CI config
- Compare Python/Node versions
- Check for platform-specific code

### Reviewer Not Notified

- Verify reviewer has repository access
- Check GitHub notification settings
- Use `--reviewer` flag when creating PR
- Add reviewer manually via web UI if needed
