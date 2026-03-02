---
procedure: support-skill
workflow-instruction: support
---

# Operation: Update Label


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Check Cardinality Rules](#step-1-check-cardinality-rules)
  - [Step 2: Add Labels](#step-2-add-labels)
  - [Step 3: Remove Labels](#step-3-remove-labels)
  - [Step 4: Replace Labels (Atomic Operation)](#step-4-replace-labels-atomic-operation)
  - [Step 5: Modify Label Definition](#step-5-modify-label-definition)
- [Output](#output)
- [Error Handling](#error-handling)
- [Examples](#examples)
  - [Example 1: Full Workflow Transition](#example-1-full-workflow-transition)
  - [Example 2: Task Completion](#example-2-task-completion)
  - [Example 3: Reassignment During Work](#example-3-reassignment-during-work)
  - [Example 4: Bulk Update (with loop)](#example-4-bulk-update-with-loop)

## When to Use

Use this operation when you need to change, add, or remove labels on an issue, or modify a label definition.

## Prerequisites

- GitHub CLI (`gh`) authenticated with repository access
- Understanding of label cardinality rules

## Procedure

### Step 1: Check Cardinality Rules

Before updating, verify the cardinality rule for the label category:

| Category | Cardinality | Rule |
|----------|-------------|------|
| `assign:*` | 0-1 | Remove existing before adding new |
| `status:*` | 1 | Remove existing before adding new |
| `priority:*` | 1 | Remove existing before adding new |
| `type:*` | 1 | Generally do not change after creation |
| `component:*` | 1+ | Can add multiple |
| `effort:*` | 1 | Remove existing before adding new |
| `platform:*` | 0+ | Can add multiple |
| `toolchain:*` | 0+ | Can add multiple |
| `review:*` | 0-1 | Remove existing before adding new |

### Step 2: Add Labels

```bash
# Add a single label
gh issue edit 42 --add-label "assign:implementer-1"

# Add multiple labels
gh issue edit 42 --add-label "component:api,component:auth"
```

### Step 3: Remove Labels

```bash
# Remove a single label
gh issue edit 42 --remove-label "assign:implementer-1"

# Remove multiple labels
gh issue edit 42 --remove-label "status:ready,status:backlog"
```

### Step 4: Replace Labels (Atomic Operation)

For categories with cardinality 0-1 or 1, always remove then add in single command:

```bash
# Reassign to different agent (atomic)
gh issue edit 42 --remove-label "assign:implementer-1" --add-label "assign:implementer-2"

# Change status (atomic)
gh issue edit 42 --remove-label "status:ready" --add-label "status:in-progress"

# Change priority (atomic)
gh issue edit 42 --remove-label "priority:normal" --add-label "priority:high"
```

### Step 5: Modify Label Definition

```bash
# Rename a label
gh label edit "old-name" --name "new-name"

# Change label color
gh label edit "status:blocked" --color "cb2431"

# Update description
gh label edit "assign:implementer-1" --description "Assigned to AI implementer agent 1"
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| Update Status | Boolean | Whether the update succeeded |
| CLI Output | Text | Confirmation from `gh issue edit` |
| Issue State | JSON | Updated issue state with new labels |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Multiple status labels | Concurrent update or forgot to remove | Remove all status labels, add correct one |
| Multiple assign labels | Concurrent update or forgot to remove | Remove all assign labels, add correct one |
| "Label not found" | Label does not exist | Create label first with `gh label create` |
| "Issue not found" | Wrong issue number | Verify issue exists with `gh issue view N` |

## Examples

### Example 1: Full Workflow Transition

```bash
# Issue moves from ready to in-progress with assignment
gh issue edit 42 \
  --remove-label "status:ready" \
  --add-label "status:in-progress,assign:implementer-1"
```

### Example 2: Task Completion

```bash
# Mark task complete, remove assignment
gh issue edit 42 \
  --remove-label "status:in-progress,assign:implementer-1" \
  --add-label "status:done"
```

### Example 3: Reassignment During Work

```bash
# Reassign from implementer-1 to implementer-2
gh issue edit 42 \
  --remove-label "assign:implementer-1" \
  --add-label "assign:implementer-2"

# Add comment explaining reassignment
gh issue comment 42 --body "Reassigned from implementer-1 to implementer-2 due to context loss recovery."
```

### Example 4: Bulk Update (with loop)

```bash
# Update all issues from one status to another
for issue_num in $(gh issue list --label "status:backlog" --json number --jq '.[].number'); do
  gh issue edit $issue_num --remove-label "status:backlog" --add-label "status:ready"
done
```
