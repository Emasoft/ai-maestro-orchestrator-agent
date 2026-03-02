# Agent Pre-Work Sync Checklist - Part 4: Automation & Troubleshooting

> This is Part 4 of the Agent Pre-Work Sync Checklist.
> See [AGENT_SYNC_CHECKLIST.md](./AGENT_SYNC_CHECKLIST.md) for the full index.

---

## Automation Script

Save as `scripts/pre-work-checklist.sh`:

```bash
#!/bin/bash
set -e

# Usage: ./pre-work-checklist.sh ISSUE_NUMBER TASK_ID

ISSUE_NUMBER="$1"
TASK_ID="$2"

GITHUB_OWNER="${GITHUB_OWNER:-myorg}"
REPO_NAME="${REPO_NAME:-myrepo}"
PROJECT_NUMBER="${PROJECT_NUMBER:-1}"
AGENT_NAME="${AGENT_NAME:-$(whoami)}"
SESSION_ID="${SESSION_ID:-session_$(date +%Y%m%d_%H%M%S)}"
PLATFORM="${PLATFORM:-$(uname -s | tr '[:upper:]' '[:lower:]')}"

echo "Running pre-work checklist for Issue #$ISSUE_NUMBER (Task $TASK_ID)..."

# 1. Verify issue exists
echo -n "1. Checking issue exists... "
gh issue view "$ISSUE_NUMBER" --repo "$GITHUB_OWNER/$REPO_NAME" > /dev/null
echo "Done"

# 2. Check assignment
echo -n "2. Checking assignment... "
ASSIGNEE=$(gh issue view "$ISSUE_NUMBER" --repo "$GITHUB_OWNER/$REPO_NAME" --json assignees --jq '.assignees[].login' | grep "^$AGENT_NAME$" || echo "")
if [ -z "$ASSIGNEE" ]; then
  echo "Not assigned, assigning..."
  gh issue edit "$ISSUE_NUMBER" --repo "$GITHUB_OWNER/$REPO_NAME" --add-assignee "@me"
fi
echo "Done"

# 3. Verify labels
echo -n "3. Checking labels... "
LABELS=$(gh issue view "$ISSUE_NUMBER" --repo "$GITHUB_OWNER/$REPO_NAME" --json labels --jq '.labels[].name')
if ! echo "$LABELS" | grep -q "^status:"; then
  gh issue edit "$ISSUE_NUMBER" --repo "$GITHUB_OWNER/$REPO_NAME" --add-label "status:backlog"
fi
echo "Done"

# 4. Check project link
echo -n "4. Checking project link... "
ITEM_ID=$(gh project item-list "$PROJECT_NUMBER" --owner "$GITHUB_OWNER" --format json | \
  jq -r ".items[] | select(.content.number == $ISSUE_NUMBER) | .id")
if [ -z "$ITEM_ID" ]; then
  echo "Not linked, adding to project..."
  gh project item-add "$PROJECT_NUMBER" --owner "$GITHUB_OWNER" \
    --url "https://github.com/$GITHUB_OWNER/$REPO_NAME/issues/$ISSUE_NUMBER"
fi
echo "Done"

# 5. Extract and verify toolchain
echo -n "5. Checking toolchain template... "
TOOLCHAIN_PATH=$(gh issue view "$ISSUE_NUMBER" --repo "$GITHUB_OWNER/$REPO_NAME" --json body --jq .body | \
  grep -oP 'Toolchain Template.*?\K[^\s\)]+\.md' | head -1)
if [ ! -f "$TOOLCHAIN_PATH" ]; then
  echo "Toolchain template not found: $TOOLCHAIN_PATH"
  exit 1
fi
echo "Done"

# 6. Create branch
echo -n "6. Creating feature branch... "
TITLE=$(gh issue view "$ISSUE_NUMBER" --repo "$GITHUB_OWNER/$REPO_NAME" --json title --jq .title)
BRANCH_NAME="feature/${TASK_ID}-$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g' | cut -c1-40)"
git checkout main && git pull origin main
git checkout -b "$BRANCH_NAME" || git checkout "$BRANCH_NAME"
git push -u origin "$BRANCH_NAME" || echo "(already pushed)"
echo "Done: $BRANCH_NAME"

# 7. Update status to In Progress
echo -n "7. Updating status to In Progress... "
./scripts/sync-issue-status.sh "$ISSUE_NUMBER" "In Progress" "Agent **$AGENT_NAME** started work.

**Session:** $SESSION_ID
**Branch:** \`$BRANCH_NAME\`
**Platform:** $PLATFORM
**Started:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo "Done"

echo ""
echo "Pre-work checklist complete!"
echo "Ready to begin implementation on branch: $BRANCH_NAME"
```

---

## Troubleshooting

### Checklist Step Fails

**Problem:** A checklist step fails and you cannot proceed

**Solution:**
1. Read error message carefully
2. Check corresponding section in this document
3. Try manual commands from that section
4. If still blocked, set issue to "status:blocked"
5. Notify orchestrator with error details

### Cannot Access Issue

**Problem:** `gh issue view` fails with permission error

**Solution:**
```bash
# Check GitHub authentication
gh auth status

# Re-authenticate if needed
gh auth login

# Verify repository access
gh repo view {{GITHUB_OWNER}}/{{REPO_NAME}}
```

### Toolchain Setup Fails

**Problem:** Tools cannot be installed or versions mismatch

**Solution:**
1. Review toolchain template requirements
2. Check system compatibility
3. Try manual installation steps
4. Document exact error in issue comment
5. Set issue to "status:blocked"
6. Request orchestrator assistance

### Branch Already Exists

**Problem:** Feature branch already exists from previous attempt

**Solution:**
```bash
# Checkout existing branch
git checkout feature/{{TASK_ID}}-*

# Or delete and recreate
git branch -D feature/{{TASK_ID}}-*
git push origin --delete feature/{{TASK_ID}}-*
# Then re-run step 5
```

### Cannot Update Project Board

**Problem:** Project item edit fails

**Solution:**
1. Verify project ID (not project number)
2. Refresh field IDs: `gh project field-list {{PROJECT_NUMBER}} --format json`
3. Check permissions: ensure agent has project write access
4. Try web UI: manually update as fallback

---

## When Checklist Complete

After successfully completing all checklist steps:

1. **Post checklist summary** to issue as comment
2. **Begin implementation** following toolchain template
3. **Commit frequently** with descriptive messages
4. **Run tests regularly** during development
5. **Keep issue updated** with progress comments
6. **Follow KANBAN_SYNC_PROTOCOL.md** for status transitions

---

## Post-Work Checklist

When implementation complete, see:
- **KANBAN_SYNC_PROTOCOL.md** - Status transition rules
- **PR_TEMPLATE.md** - Pull request creation
- **Agent Reporting Guidelines** - Final report format
