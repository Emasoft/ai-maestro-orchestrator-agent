## Table of Contents
- [Example 1: Pre-Flight Scope Check](#example-1-pre-flight-scope-check)
- [Example 2: Create Task and Add to Board](#example-2-create-task-and-add-to-board)
- [Example 3: Move Item to AI Review](#example-3-move-item-to-ai-review)
- [Example 4: Safe Guard Before Closing Issue](#example-4-safe-guard-before-closing-issue)

---

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
  --label "assign:ampa-impl-01,priority:high,status:todo")

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
