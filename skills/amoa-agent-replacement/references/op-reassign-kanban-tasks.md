---
procedure: support-skill
workflow-instruction: support
---

# Operation: Reassign Kanban Tasks


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Find GitHub Project ID](#step-1-find-github-project-id)
  - [Step 2: Find All Cards Assigned to Failed Agent](#step-2-find-all-cards-assigned-to-failed-agent)
  - [Step 3: Get Item IDs for Reassignment](#step-3-get-item-ids-for-reassignment)
  - [Step 4: Update Each Card's Assignee](#step-4-update-each-cards-assignee)
  - [Step 5: Add Reassignment Comment](#step-5-add-reassignment-comment)
  - [Step 6: Preserve Status Labels](#step-6-preserve-status-labels)
  - [Step 7: Handle Partial Work](#step-7-handle-partial-work)
  - [Step 8: Update Orchestrator State](#step-8-update-orchestrator-state)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example](#example)
- [Checklist](#checklist)

## When to Use

Use this operation after generating the handoff document to update GitHub Project board assignments.

## Prerequisites

- Handoff document generated (op-generate-handoff-document)
- GitHub Project board ID known
- Replacement agent registered in orchestrator

## Procedure

### Step 1: Find GitHub Project ID

```bash
# List projects for the repository
gh project list --owner <OWNER> --format json

# Note the PROJECT_ID (format: PVT_kwDOBxxxxxx)
```

### Step 2: Find All Cards Assigned to Failed Agent

```bash
# Get all items in project
gh project item-list <PROJECT_NUMBER> --owner <OWNER> --format json

# Filter to failed agent's items
gh project item-list <PROJECT_NUMBER> --owner <OWNER> --format json \
  | jq '.items[] | select(.assignees[]?.login == "<failed_agent>")'
```

### Step 3: Get Item IDs for Reassignment

```bash
# Get item IDs assigned to failed agent
ITEM_IDS=$(gh project item-list <PROJECT_NUMBER> --owner <OWNER> --format json \
  | jq -r '.items[] | select(.labels[]?.name == "assign:<failed_agent>") | .id')
```

### Step 4: Update Each Card's Assignee

For GitHub Projects (v2), use GraphQL:

```bash
# Update assignee on project item
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(
    input: {
      projectId: "<PROJECT_ID>"
      itemId: "<ITEM_ID>"
      fieldId: "<ASSIGNEE_FIELD_ID>"
      value: {
        singleSelectOptionId: "<NEW_AGENT_OPTION_ID>"
      }
    }
  ) {
    projectV2Item {
      id
    }
  }
}'
```

For simpler label-based assignment:

```bash
# Update labels on the linked issue
gh issue edit <ISSUE_NUM> \
  --remove-label "assign:<failed_agent>" \
  --add-label "assign:<replacement_agent>"
```

### Step 5: Add Reassignment Comment

```bash
# Add audit comment to each reassigned issue
gh issue comment <ISSUE_NUM> --body "**Task Reassigned**
- From: <failed_agent>
- To: <replacement_agent>
- Reason: <failure_reason>
- Time: $(date -u +%Y-%m-%dT%H:%M:%SZ)
- Handoff document: [link or attached]"
```

### Step 6: Preserve Status Labels

Do NOT change status labels during reassignment:
- Keep `status:in-progress` if work was ongoing
- Keep priority labels
- Keep component labels

Only change `assign:*` label.

### Step 7: Handle Partial Work

If agent had partial commits:

```bash
# Create work-in-progress note
gh issue comment <ISSUE_NUM> --body "**Work-in-Progress State**
- Branch: feature/auth-42
- Commits: 3 ahead of main
- Last commit: \"Add token validation stub\"
- Files modified: src/auth/validation.py

New agent should checkout branch and continue from current state."
```

### Step 8: Update Orchestrator State

After kanban updates, update state file:

```yaml
# In design/state/exec-phase.md
assignments:
  implementer-2:  # NEW
    - issue: 42
      module: auth-core
      status: in-progress
      reassigned_from: implementer-1
      reassigned_at: 2024-01-15T15:30:00Z
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| Cards Updated | Number | Count of cards reassigned |
| Issues Updated | Array | List of issue numbers updated |
| Comments Added | Number | Count of audit comments |
| State Updated | Boolean | Whether state file was updated |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Project not found | Wrong project ID | Verify with `gh project list` |
| Item not found | Card deleted or wrong ID | Skip and log |
| Label update failed | Label doesn't exist | Create label first |
| Concurrent update | Another process editing | Retry with fresh data |
| Rate limit | Too many API calls | Add delays between updates |

## Example

```bash
#!/bin/bash
# Full kanban reassignment script

FAILED_AGENT="implementer-1"
REPLACEMENT_AGENT="implementer-2"
FAILURE_REASON="context_loss"

# Find all issues with failed agent's label
ISSUE_NUMS=$(gh issue list --label "assign:$FAILED_AGENT" --json number --jq '.[].number')

for issue_num in $ISSUE_NUMS; do
  echo "Reassigning issue #$issue_num..."

  # Update labels (atomic operation)
  gh issue edit "$issue_num" \
    --remove-label "assign:$FAILED_AGENT" \
    --add-label "assign:$REPLACEMENT_AGENT"

  # Add audit comment
  gh issue comment "$issue_num" --body "**Task Reassigned**
- From: $FAILED_AGENT
- To: $REPLACEMENT_AGENT
- Reason: $FAILURE_REASON
- Time: $(date -u +%Y-%m-%dT%H:%M:%SZ)

Work will continue from current progress state."

  echo "  Done: Issue #$issue_num reassigned"
done

echo "Kanban reassignment complete: $ISSUE_NUMS"
```

## Checklist

- [ ] Identify GitHub Project ID
- [ ] Find all cards/issues assigned to failed agent
- [ ] For each card/issue:
  - [ ] Update `assign:*` label
  - [ ] Add reassignment audit comment
  - [ ] Preserve all other labels
- [ ] Document partial work state
- [ ] Update orchestrator state file
- [ ] Verify all cards updated correctly
