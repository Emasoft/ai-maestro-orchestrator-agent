# Label Taxonomy Examples

## Example 1: Assign Task to Agent

```bash
# Check current assignment
gh issue view 42 --json labels | jq -r '.labels[] | select(.name | startswith("assign:"))'

# Remove existing assignment (if any)
gh issue edit 42 --remove-label "assign:implementer-1"

# Add new assignment
gh issue edit 42 --add-label "assign:implementer-2"

# Verify
gh issue view 42 --json labels | jq -r '.labels[] | select(.name | startswith("assign:"))'
```

## Example 2: Update Status During Workflow

```bash
# Task is ready to start
gh issue edit 42 --remove-label "status:ready" --add-label "status:in-progress"

# Task is blocked
gh issue edit 42 --remove-label "status:in-progress" --add-label "status:blocked"

# Blocker resolved
gh issue edit 42 --remove-label "status:blocked" --add-label "status:in-progress"

# Task completed
gh issue edit 42 --remove-label "status:in-progress" --add-label "status:done"
```

## Example 3: Query Issues by Multiple Labels

```bash
# Find all high-priority bugs assigned to implementer-1
gh issue list --label "priority:high" --label "type:bug" --label "assign:implementer-1"

# Find all blocked issues
gh issue list --label "status:blocked"

# Find all ready tasks for the API component
gh issue list --label "status:ready" --label "component:api"
```

## Example 4: Validate Label Cardinality

```bash
# Check if issue has exactly one status label
STATUS_COUNT=$(gh issue view 42 --json labels | jq '[.labels[] | select(.name | startswith("status:"))] | length')
if [ "$STATUS_COUNT" -ne 1 ]; then
  echo "ERROR: Issue has $STATUS_COUNT status labels (expected 1)"
fi

# Check if issue has at most one assign label
ASSIGN_COUNT=$(gh issue view 42 --json labels | jq '[.labels[] | select(.name | startswith("assign:"))] | length')
if [ "$ASSIGN_COUNT" -gt 1 ]; then
  echo "ERROR: Issue has $ASSIGN_COUNT assign labels (expected 0 or 1)"
fi
```
