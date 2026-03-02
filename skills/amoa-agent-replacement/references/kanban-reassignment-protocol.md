# Kanban Reassignment Protocol Reference

## Contents

- [4.1 Finding Assigned Cards](#41-finding-assigned-cards)
- [4.2 Updating Assignee](#42-updating-assignee)
- [4.3 Adding Audit Comments](#43-adding-audit-comments)
- [4.4 Preserving State](#44-preserving-state)
- [4.5 Handling Partial Work](#45-handling-partial-work)

---

## 4.1 Finding Assigned Cards

### By GitHub Username

If the agent has a GitHub username:

```bash
# List all issues assigned to the agent
gh issue list --assignee "@GITHUB_USERNAME" --json number,title,state,projectCards

# With project filter
gh issue list --assignee "@GITHUB_USERNAME" --project "PROJECT_NAME" --json number,title,state
```

### By Agent ID in Labels

If using labels to track agent assignments:

```bash
# Find issues with agent label
gh issue list --label "assigned:implementer-1" --json number,title,state
```

### By Project Card Custom Fields

For GitHub Projects (V2) with custom fields:

```bash
# Query project items
gh api graphql -f query='
query {
  organization(login: "OWNER") {
    projectV2(number: PROJECT_NUMBER) {
      items(first: 100) {
        nodes {
          content {
            ... on Issue {
              number
              title
            }
          }
          fieldValues(first: 10) {
            nodes {
              ... on ProjectV2ItemFieldTextValue {
                field { ... on ProjectV2Field { name } }
                text
              }
            }
          }
        }
      }
    }
  }
}' | jq '.data.organization.projectV2.items.nodes[] | select(.fieldValues.nodes[].text == "implementer-1")'
```

### From Orchestrator State File

Cross-reference with state file:

```bash
# Get all GitHub issues from state file for the agent
yq '.active_assignments[] | select(.agent == "implementer-1") | .github_issue' $STATE_FILE
```

---

## 4.2 Updating Assignee

### Remove Old Assignee and Add New

```bash
# For each issue
ISSUE_NUMBER=42
OLD_AGENT="old-agent-username"
NEW_AGENT="new-agent-username"

# Update assignees
gh issue edit $ISSUE_NUMBER --remove-assignee "$OLD_AGENT" --add-assignee "$NEW_AGENT"
```

### Batch Update Script

```bash
#!/bin/bash
# reassign_issues.sh

OLD_AGENT="$1"
NEW_AGENT="$2"
PROJECT_NAME="$3"

# Get all issues assigned to old agent
ISSUES=$(gh issue list --assignee "@$OLD_AGENT" --project "$PROJECT_NAME" --json number --jq '.[].number')

for ISSUE in $ISSUES; do
  echo "Reassigning issue #$ISSUE from $OLD_AGENT to $NEW_AGENT"
  gh issue edit "$ISSUE" --remove-assignee "$OLD_AGENT" --add-assignee "$NEW_AGENT"
done
```

### GitHub Projects V2 Card Update

For Projects V2 with assignee field:

```bash
# Update project item assignee
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(
    input: {
      projectId: "PROJECT_ID"
      itemId: "ITEM_ID"
      fieldId: "ASSIGNEE_FIELD_ID"
      value: { singleSelectOptionId: "NEW_AGENT_OPTION_ID" }
    }
  ) {
    projectV2Item { id }
  }
}'
```

---

## 4.3 Adding Audit Comments

Every reassignment MUST include an audit comment on the issue.

### Comment Template

```markdown
## Agent Reassignment Notice

| Field | Value |
|-------|-------|
| **Previous Agent** | @{{OLD_AGENT}} |
| **New Agent** | @{{NEW_AGENT}} |
| **Reassignment Reason** | {{REASON}} |
| **Reassigned At** | {{TIMESTAMP}} |
| **Orchestrator** | @{{ORCHESTRATOR}} |

### Context

This task has been reassigned due to: {{DETAILED_REASON}}

### Handoff Document

Full context for the new agent is available in the handoff document:
{{HANDOFF_URL}}

### For New Agent

Please:
1. Review the handoff document completely
2. ACK receipt via AI Maestro
3. Continue from the documented checkpoint

### Previous Progress

{{PROGRESS_SUMMARY}}

---
*Automated reassignment by EOA (Emasoft Orchestrator Agent)*
```

### Add Comment via CLI

```bash
ISSUE_NUMBER=42
COMMENT_BODY="## Agent Reassignment Notice

| Field | Value |
|-------|-------|
| **Previous Agent** | @old-agent |
| **New Agent** | @new-agent |
| **Reassignment Reason** | context_loss |
| **Reassigned At** | 2026-01-31T14:30:00Z |

This task has been reassigned due to agent context loss.
Handoff document: https://github.com/owner/repo/issues/42#issuecomment-123456

*Automated reassignment by EOA*"

gh issue comment "$ISSUE_NUMBER" --body "$COMMENT_BODY"
```

---

## 4.4 Preserving State

### DO NOT Change These

When reassigning, preserve the following:

| Field | Preserve | Reason |
|-------|----------|--------|
| Labels (except assigned:*) | Yes | Status tracking |
| Milestone | Yes | Deadline context |
| Priority | Yes | Work order |
| Project column | Yes | Workflow state |
| Issue body | Yes | Requirements |
| Previous comments | Yes | Discussion history |

### Update These

| Field | Update To | Reason |
|-------|-----------|--------|
| Assignee | New agent | Ownership |
| `assigned:*` label | New agent ID | Tracking |
| Last updated | Now | Audit |

### Label Update

```bash
ISSUE_NUMBER=42
OLD_LABEL="assigned:implementer-1"
NEW_LABEL="assigned:implementer-2"

# Remove old, add new
gh issue edit "$ISSUE_NUMBER" --remove-label "$OLD_LABEL" --add-label "$NEW_LABEL"

# Also add reassignment indicator
gh issue edit "$ISSUE_NUMBER" --add-label "reassigned"
```

---

## 4.5 Handling Partial Work

### Identify Partial Work

Before reassignment, determine what partial work exists:

```bash
# Check for open PRs from failed agent
gh pr list --author "@OLD_AGENT" --state open --json number,title,headRefName

# Check for branches
git branch -r | grep "$OLD_AGENT"
```

### Open PR Scenarios

| Scenario | Action |
|----------|--------|
| PR exists, incomplete | Keep open, reassign for completion |
| PR exists, review comments | Include review feedback in handoff |
| PR exists, conflicts | Note conflicts in handoff |
| No PR | New agent creates fresh PR |

### PR Reassignment

If there's an open PR:

```bash
PR_NUMBER=123

# Add comment about reassignment
gh pr comment "$PR_NUMBER" --body "This PR is being reassigned from @old-agent to @new-agent due to agent replacement. See handoff: URL"

# Note: GitHub doesn't allow reassigning PR authors
# New agent may need to continue on same branch or create new PR
```

### Branch Handling

| Branch State | Action |
|--------------|--------|
| Has commits, no PR | New agent continues on same branch |
| Has uncommitted work | Include patch in handoff |
| Merge conflicts | Document conflicts in handoff |
| Clean, up to date | New agent continues directly |

### Documenting Partial Work in Handoff

```markdown
## Partial Work Status

### Open Pull Request

| Field | Value |
|-------|-------|
| PR Number | #123 |
| Branch | feature/auth-core |
| Status | Changes requested |
| Conflicts | None |

**Review Comments to Address:**
1. Line 42: Add error handling for null token
2. Line 78: Use constant for expiration time

### Branch State

| Metric | Value |
|--------|-------|
| Commits ahead of main | 5 |
| Uncommitted changes | Yes |
| Last commit | GREEN: implement token refresh |

### Uncommitted Work

Patch file: `uncommitted_work.patch` (attached to this issue)

**Files with uncommitted changes:**
- `src/auth/tokens.py` (modified)
- `tests/test_tokens.py` (new file)

**Instructions:**
1. Checkout branch: `git checkout feature/auth-core`
2. Review patch: `git apply --stat uncommitted_work.patch`
3. Apply if appropriate: `git apply uncommitted_work.patch`
4. Or discard and reimplement from last commit
```

---

## Complete Reassignment Script

```bash
#!/bin/bash
# eoa_reassign_kanban_tasks.sh

OLD_AGENT="$1"
NEW_AGENT="$2"
PROJECT_ID="$3"
HANDOFF_URL="$4"

echo "Reassigning tasks from $OLD_AGENT to $NEW_AGENT"

# Get all issues assigned to old agent
ISSUES=$(gh issue list --assignee "@$OLD_AGENT" --json number --jq '.[].number')

for ISSUE in $ISSUES; do
  echo "Processing issue #$ISSUE..."

  # Update assignee
  gh issue edit "$ISSUE" --remove-assignee "$OLD_AGENT" --add-assignee "$NEW_AGENT"

  # Update labels
  gh issue edit "$ISSUE" --remove-label "assigned:$OLD_AGENT" --add-label "assigned:$NEW_AGENT" --add-label "reassigned"

  # Add audit comment
  gh issue comment "$ISSUE" --body "## Agent Reassignment

**From**: @$OLD_AGENT
**To**: @$NEW_AGENT
**Reason**: Agent replacement
**Handoff**: $HANDOFF_URL

*Automated by EOA*"

  echo "  Issue #$ISSUE reassigned"
done

echo "Reassignment complete. $ISSUES issues updated."
```

---

## Verification

After reassignment, verify:

```bash
# Verify no issues still assigned to old agent
gh issue list --assignee "@$OLD_AGENT" --json number --jq 'length'
# Should return 0

# Verify issues now assigned to new agent
gh issue list --assignee "@$NEW_AGENT" --label "reassigned" --json number,title
# Should list all reassigned issues
```

---

**Version**: 1.0.0
**Last Updated**: 2026-02-02
