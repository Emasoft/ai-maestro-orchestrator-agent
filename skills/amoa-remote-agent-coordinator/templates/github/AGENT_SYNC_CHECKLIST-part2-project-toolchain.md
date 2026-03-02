# Agent Pre-Work Sync Checklist - Part 2: Project Board, Toolchain & Branch

> This is Part 2 of the Agent Pre-Work Sync Checklist.
> See [AGENT_SYNC_CHECKLIST.md](./AGENT_SYNC_CHECKLIST.md) for the full index.

---

## 3. Project Board Verification

### 3.1. Issue Linked to Project
```bash
# Check if issue is in project
gh project item-list {{PROJECT_NUMBER}} \
  --owner {{GITHUB_OWNER}} \
  --format json | \
  jq -r ".items[] | select(.content.number == {{ISSUE_NUMBER}}) | .id"
```

**Expected Output:**
- Returns a project item ID (not empty)

**If Failed:**
```bash
# Add issue to project
gh project item-add {{PROJECT_NUMBER}} \
  --owner {{GITHUB_OWNER}} \
  --url "https://github.com/{{GITHUB_OWNER}}/{{REPO_NAME}}/issues/{{ISSUE_NUMBER}}"
```

### 3.2. Project Status Set
```bash
# Get item status
ITEM_ID=$(gh project item-list {{PROJECT_NUMBER}} \
  --owner {{GITHUB_OWNER}} \
  --format json | \
  jq -r ".items[] | select(.content.number == {{ISSUE_NUMBER}}) | .id")

gh api graphql -f query='
  query($itemId: ID!) {
    node(id: $itemId) {
      ... on ProjectV2Item {
        fieldValues(first: 10) {
          nodes {
            ... on ProjectV2ItemFieldSingleSelectValue {
              name
              field {
                ... on ProjectV2FieldCommon {
                  name
                }
              }
            }
          }
        }
      }
    }
  }
' -f itemId="$ITEM_ID" | jq -r '.data.node.fieldValues.nodes[] | select(.field.name == "Status") | .name'
```

**Expected Output:**
- "Backlog" (before starting work)

**If Failed:**
```bash
# Set status to Backlog
STATUS_FIELD_ID=$(gh project field-list {{PROJECT_NUMBER}} \
  --owner {{GITHUB_OWNER}} \
  --format json | \
  jq -r '.[] | select(.name == "Status") | .id')

PROJECT_ID=$(gh project list --owner {{GITHUB_OWNER}} --format json | \
  jq -r ".projects[] | select(.number == {{PROJECT_NUMBER}}) | .id")

gh project item-edit \
  --project-id "$PROJECT_ID" \
  --id "$ITEM_ID" \
  --field-id "$STATUS_FIELD_ID" \
  --value "Backlog"
```

**Checkpoint:**
- [ ] Issue is linked to project board
- [ ] Project status is set to "Backlog"

---

## 4. Toolchain Template Verification

### 4.1. Toolchain Template Exists
```bash
# Extract toolchain template path from issue body
TOOLCHAIN_PATH=$(gh issue view {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --json body --jq .body | \
  grep -oP 'Toolchain Template.*?\K[^\s\)]+\.md')

# Check if file exists
if [ -f "$TOOLCHAIN_PATH" ]; then
  echo "Toolchain template found: $TOOLCHAIN_PATH"
else
  echo "Toolchain template not found: $TOOLCHAIN_PATH"
  exit 1
fi
```

**Expected Output:**
- Template file exists and is readable

**If Failed:**
- Request orchestrator to create/specify toolchain template
- Do not proceed without toolchain template

### 4.2. Toolchain Template Valid
```bash
# Validate toolchain template structure
cat "$TOOLCHAIN_PATH" | grep -q "## Platform" && \
cat "$TOOLCHAIN_PATH" | grep -q "## Required Tools" && \
cat "$TOOLCHAIN_PATH" | grep -q "## Setup Script" && \
echo "Toolchain template is valid" || \
echo "Toolchain template is missing required sections"
```

**Expected Sections:**
- `## Platform`
- `## Required Tools`
- `## Setup Script`
- `## Verification`

**If Failed:**
- Request orchestrator to fix toolchain template
- Verify you're reading correct file

**Checkpoint:**
- [ ] Toolchain template path specified in issue
- [ ] Toolchain template file exists
- [ ] Toolchain template has all required sections

---

## 5. Branch Creation

### 5.1. Create Feature Branch
```bash
# Branch naming convention: feature/TASK_ID-short-description
BRANCH_NAME="feature/{{TASK_ID}}-$(echo "{{TITLE}}" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g' | cut -c1-40)"

# Ensure on latest main
git checkout main
git pull origin main

# Create and checkout feature branch
git checkout -b "$BRANCH_NAME"

# Push to remote to establish tracking
git push -u origin "$BRANCH_NAME"

echo "Branch created: $BRANCH_NAME"
```

**Expected Output:**
- New branch created and pushed to remote
- Branch name follows convention: `feature/{{TASK_ID}}-description`

**If Failed:**
- Check git credentials
- Verify repository access
- Ensure main branch exists

### 5.2. Verify Branch Protection
```bash
# Check if feature branch can push
git commit --allow-empty -m "Test commit for branch verification"
git push origin "$BRANCH_NAME"
git reset --hard HEAD~1

echo "Branch is pushable"
```

**Expected Output:**
- Push succeeds without errors

**If Failed:**
- Check branch protection rules
- Verify write permissions
- Contact orchestrator if blocked

**Checkpoint:**
- [ ] Feature branch created with correct naming
- [ ] Branch pushed to remote
- [ ] Branch is pushable

---

## Next Steps

Continue to [Part 3: Environment & Registration](./AGENT_SYNC_CHECKLIST-part3-environment-registration.md) for:
- Local Environment Setup
- Agent Registration
- Complete Checklist Summary
