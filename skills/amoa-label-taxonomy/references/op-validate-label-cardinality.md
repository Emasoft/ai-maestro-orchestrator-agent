---
procedure: support-skill
workflow-instruction: support
---

# Operation: Validate Label Cardinality


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Get Issue Labels](#step-1-get-issue-labels)
  - [Step 2: Check Each Category](#step-2-check-each-category)
  - [Step 3: Validation Script](#step-3-validation-script)
  - [Step 4: Fix Violations](#step-4-fix-violations)
- [Output](#output)
- [Error Handling](#error-handling)
- [Examples](#examples)
  - [Example 1: Quick Validation Check](#example-1-quick-validation-check)
  - [Example 2: Validate All Open Issues](#example-2-validate-all-open-issues)
  - [Example 3: Pre-Update Validation](#example-3-pre-update-validation)

## When to Use

Use this operation when you need to verify that an issue's labels comply with the cardinality rules, or before making label changes.

## Prerequisites

- GitHub CLI (`gh`) authenticated with repository access
- Understanding of label cardinality constraints

## Procedure

### Step 1: Get Issue Labels

```bash
# Get labels as JSON array
gh issue view 42 --json labels --jq '.labels[].name'
```

### Step 2: Check Each Category

Count labels per category and compare against rules:

| Category | Valid Count | Rule |
|----------|-------------|------|
| `assign:*` | 0 or 1 | At most one assignment |
| `status:*` | Exactly 1 | Must have exactly one |
| `priority:*` | Exactly 1 | Must have exactly one |
| `type:*` | Exactly 1 | Must have exactly one |
| `component:*` | 1 or more | At least one |
| `effort:*` | Exactly 1 | Must have exactly one |
| `platform:*` | 0 or more | Optional, unlimited |
| `toolchain:*` | 0 or more | Optional, unlimited |
| `review:*` | 0 or 1 | At most one |

### Step 3: Validation Script

```bash
#!/bin/bash
# validate_labels.sh - Check label cardinality for an issue
ISSUE_NUM=$1

labels=$(gh issue view $ISSUE_NUM --json labels --jq '.labels[].name')

# Count by category
assign_count=$(echo "$labels" | grep -c "^assign:" || echo 0)
status_count=$(echo "$labels" | grep -c "^status:" || echo 0)
priority_count=$(echo "$labels" | grep -c "^priority:" || echo 0)
type_count=$(echo "$labels" | grep -c "^type:" || echo 0)
component_count=$(echo "$labels" | grep -c "^component:" || echo 0)
effort_count=$(echo "$labels" | grep -c "^effort:" || echo 0)
review_count=$(echo "$labels" | grep -c "^review:" || echo 0)

# Validate
valid=true
[ $assign_count -gt 1 ] && echo "ERROR: Multiple assign labels ($assign_count)" && valid=false
[ $status_count -ne 1 ] && echo "ERROR: Status count is $status_count (must be 1)" && valid=false
[ $priority_count -ne 1 ] && echo "ERROR: Priority count is $priority_count (must be 1)" && valid=false
[ $type_count -ne 1 ] && echo "ERROR: Type count is $type_count (must be 1)" && valid=false
[ $component_count -lt 1 ] && echo "WARNING: No component labels" && valid=false
[ $effort_count -ne 1 ] && echo "WARNING: Effort count is $effort_count (should be 1)"
[ $review_count -gt 1 ] && echo "ERROR: Multiple review labels ($review_count)" && valid=false

$valid && echo "Valid: All cardinality rules satisfied"
```

### Step 4: Fix Violations

If violations found, use op-update-label to correct:

```bash
# Fix multiple status labels
gh issue view 42 --json labels --jq '.labels[].name' | grep "^status:" | while read label; do
  gh issue edit 42 --remove-label "$label"
done
gh issue edit 42 --add-label "status:backlog"  # Set correct status

# Fix multiple assign labels
gh issue view 42 --json labels --jq '.labels[].name' | grep "^assign:" | while read label; do
  gh issue edit 42 --remove-label "$label"
done
# Then add correct assignment if needed
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| Validation Result | Boolean | Whether all rules are satisfied |
| Violations | Array | List of cardinality violations |
| Warnings | Array | List of non-critical issues |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Multiple singleton labels | Concurrent updates or manual error | Remove all, add correct one |
| Missing required labels | Incomplete triage | Add missing required labels |
| "Issue not found" | Wrong issue number | Verify with `gh issue list` |

## Examples

### Example 1: Quick Validation Check

```bash
# One-liner to check an issue
gh issue view 42 --json labels --jq '.labels[].name' | sort | uniq -c | while read count label; do
  prefix=$(echo "$label" | cut -d: -f1)
  echo "$prefix: $count ($label)"
done
```

### Example 2: Validate All Open Issues

```bash
# Check all open issues for cardinality violations
for num in $(gh issue list --state open --json number --jq '.[].number'); do
  echo "Issue #$num:"
  # Run validation for each issue
  labels=$(gh issue view $num --json labels --jq '.labels[].name' 2>/dev/null)
  status_count=$(echo "$labels" | grep -c "^status:" 2>/dev/null || echo 0)
  [ "$status_count" != "1" ] && echo "  WARNING: status count = $status_count"
done
```

### Example 3: Pre-Update Validation

```bash
# Before updating, check current state
current_status=$(gh issue view 42 --json labels --jq '[.labels[].name | select(startswith("status:"))] | length')
if [ "$current_status" -gt 1 ]; then
  echo "Fix multiple status labels first"
  exit 1
fi
```
