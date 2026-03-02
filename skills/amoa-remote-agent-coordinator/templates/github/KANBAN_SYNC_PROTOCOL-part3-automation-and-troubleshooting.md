# Kanban Synchronization Protocol - Part 3: Automation Script and Troubleshooting

This document contains the automation script, required field checklists, error handling, and troubleshooting guides.

**Parent document:** [KANBAN_SYNC_PROTOCOL.md](./KANBAN_SYNC_PROTOCOL.md)

---

## Automation Script

Save as `scripts/sync-issue-status.sh`:

```bash
#!/bin/bash
set -e

# Usage: ./sync-issue-status.sh ISSUE_NUMBER NEW_STATUS [COMMENT]
# Example: ./sync-issue-status.sh 42 "In Progress" "Started work"

ISSUE_NUMBER="$1"
NEW_STATUS="$2"
COMMENT="${3:-}"

GITHUB_OWNER="${GITHUB_OWNER:-myorg}"
REPO_NAME="${REPO_NAME:-myrepo}"
PROJECT_NUMBER="${PROJECT_NUMBER:-1}"
AGENT_NAME="${AGENT_NAME:-unknown}"

# Determine label transitions
case "$NEW_STATUS" in
  "Backlog")
    OLD_LABEL_PATTERN="status:"
    NEW_LABEL="status:backlog"
    ;;
  "In Progress")
    OLD_LABEL_PATTERN="status:"
    NEW_LABEL="status:in-progress"
    ;;
  "Todo")
    OLD_LABEL_PATTERN="status:"
    NEW_LABEL="status:todo"
    ;;
  "AI Review")
    OLD_LABEL_PATTERN="status:"
    NEW_LABEL="status:ai-review"
    ;;
  "Human Review")
    OLD_LABEL_PATTERN="status:"
    NEW_LABEL="status:human-review"
    ;;
  "Merge/Release")
    OLD_LABEL_PATTERN="status:"
    NEW_LABEL="status:merge-release"
    ;;
  "Done")
    OLD_LABEL_PATTERN="status:"
    NEW_LABEL="status:done"
    ;;
  "Blocked")
    OLD_LABEL_PATTERN="status:"
    NEW_LABEL="status:blocked"
    ;;
  *)
    echo "Error: Invalid status '$NEW_STATUS'"
    echo "Valid: Backlog, Todo, In Progress, AI Review, Human Review, Merge/Release, Done, Blocked"
    exit 1
    ;;
esac

# Get current labels
CURRENT_LABELS=$(gh issue view "$ISSUE_NUMBER" \
  --repo "$GITHUB_OWNER/$REPO_NAME" \
  --json labels \
  --jq '.labels[].name')

# Remove old status labels
for LABEL in $CURRENT_LABELS; do
  if [[ "$LABEL" == status:* ]]; then
    gh issue edit "$ISSUE_NUMBER" \
      --repo "$GITHUB_OWNER/$REPO_NAME" \
      --remove-label "$LABEL"
  fi
done

# Add new status label
gh issue edit "$ISSUE_NUMBER" \
  --repo "$GITHUB_OWNER/$REPO_NAME" \
  --add-label "$NEW_LABEL"

# Get project item ID
ITEM_ID=$(gh project item-list "$PROJECT_NUMBER" \
  --owner "$GITHUB_OWNER" \
  --format json | \
  jq -r ".items[] | select(.content.number == $ISSUE_NUMBER) | .id")

if [ -n "$ITEM_ID" ]; then
  # Get project ID
  PROJECT_ID=$(gh project list --owner "$GITHUB_OWNER" --format json | \
    jq -r ".projects[] | select(.number == $PROJECT_NUMBER) | .id")

  # Get status field ID
  STATUS_FIELD_ID=$(gh project field-list "$PROJECT_NUMBER" \
    --owner "$GITHUB_OWNER" \
    --format json | \
    jq -r '.[] | select(.name == "Status") | .id')

  # Update project item
  gh project item-edit \
    --project-id "$PROJECT_ID" \
    --id "$ITEM_ID" \
    --field-id "$STATUS_FIELD_ID" \
    --value "$NEW_STATUS"
fi

# Add comment if provided
if [ -n "$COMMENT" ]; then
  gh issue comment "$ISSUE_NUMBER" \
    --repo "$GITHUB_OWNER/$REPO_NAME" \
    --body "**Status:** $NEW_STATUS

$COMMENT

**Agent:** $AGENT_NAME
**Time:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
fi

echo "✅ Issue #$ISSUE_NUMBER status updated to: $NEW_STATUS"
```

---

## Required Fields Before Status Change

### Before Moving to "In Progress"
- [ ] Issue assigned to agent
- [ ] Toolchain template specified
- [ ] All required tools available
- [ ] Environment setup script tested
- [ ] Agent authenticated to GitHub

### Before Moving to "AI Review"
- [ ] All acceptance criteria met
- [ ] All tests passing locally
- [ ] Code formatted and linted
- [ ] Documentation updated
- [ ] Toolchain verified
- [ ] PR created and linked
- [ ] PR template filled completely
- [ ] Test results included in PR

### Before Moving to "Human Review"
- [ ] AI review completed and approved
- [ ] All AI-flagged issues resolved
- [ ] PR ready for human reviewer

### Before Moving to "Merge/Release"
- [ ] Human review completed and approved
- [ ] All review comments addressed
- [ ] Final CI checks passing

### Before Moving to "Done"
- [ ] PR approved by reviewer
- [ ] All CI checks passing
- [ ] No merge conflicts
- [ ] Branch up to date with base
- [ ] PR merged to main
- [ ] Issue closed

### Before Setting "Blocked"
- [ ] Blocker clearly described
- [ ] Required action identified
- [ ] Impact assessed
- [ ] Orchestrator notified

---

## Error Handling

### Issue Not Found
```bash
# Verify issue exists
gh issue view {{ISSUE_NUMBER}} --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
```

### Project Item Not Found
```bash
# Add issue to project if missing
gh project item-add {{PROJECT_NUMBER}} \
  --owner {{GITHUB_OWNER}} \
  --url "https://github.com/{{GITHUB_OWNER}}/{{REPO_NAME}}/issues/{{ISSUE_NUMBER}}"
```

### Field ID Not Found
```bash
# Refresh field IDs
gh project field-list {{PROJECT_NUMBER}} \
  --owner {{GITHUB_OWNER}} \
  --format json > project-fields.json
```

### Permission Denied
- Verify agent has write access to repository
- Check GitHub token has correct scopes
- Verify project permissions

---

## Best Practices

1. **Always comment when changing status** - Provide context for the transition
2. **Update both labels and project board** - Keep them in sync
3. **Verify required fields before transition** - Don't skip validation
4. **Notify orchestrator on critical events** - Blocked, failed, completed
5. **Use atomic operations** - Update label and board in same script
6. **Log all transitions** - Keep audit trail of status changes
7. **Handle errors gracefully** - Don't leave issues in inconsistent state
8. **Test sync script before use** - Verify it works on test issue first

---

## Troubleshooting

### Labels and Board Out of Sync
Run sync script to reconcile:
```bash
./scripts/sync-issue-status.sh {{ISSUE_NUMBER}} "{{CORRECT_STATUS}}"
```

### Multiple Status Labels on Issue
Remove all status labels and re-apply correct one:
```bash
for label in $(gh issue view {{ISSUE_NUMBER}} --json labels --jq '.labels[].name' | grep "^status:"); do
  gh issue edit {{ISSUE_NUMBER}} --remove-label "$label"
done
gh issue edit {{ISSUE_NUMBER}} --add-label "status:{{CORRECT_STATUS}}"
```

### Project Item Missing
Add issue to project:
```bash
gh project item-add {{PROJECT_NUMBER}} \
  --owner {{GITHUB_OWNER}} \
  --url "https://github.com/{{GITHUB_OWNER}}/{{REPO_NAME}}/issues/{{ISSUE_NUMBER}}"
```

### Cannot Update Project Fields
- Check project ID is correct (not project number)
- Verify field ID is current
- Ensure value matches field type (single-select vs text)
