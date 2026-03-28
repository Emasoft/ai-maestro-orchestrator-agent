# CLI Commands for Label Management

**IMPORTANT: All `gh` commands below MUST include `--repo "$OWNER/$REPO"`. Set `OWNER_REPO` variable before running any commands.**

## Table of Contents

- [Create Labels](#create-labels)
- [Query Labels](#query-labels)
- [Update Labels](#update-labels)
- [Validate Label Cardinality](#validate-label-cardinality)


## Create Labels

### Assignment Labels
```bash
gh label create "assign:implementer-1" --repo "$OWNER_REPO" --color "1D76DB" --description "Assigned to implementer-1"
gh label create "assign:implementer-2" --repo "$OWNER_REPO" --color "5319E7" --description "Assigned to implementer-2"
gh label create "assign:code-reviewer" --repo "$OWNER_REPO" --color "0E8A16" --description "Assigned to code reviewer"
gh label create "assign:orchestrator" --repo "$OWNER_REPO" --color "D876E3" --description "Orchestrator handling"
gh label create "assign:human" --repo "$OWNER_REPO" --color "FBCA04" --description "Human developer"
```

### Status Labels
```bash
gh label create "status:backlog" --repo "$OWNER_REPO" --color "CFD3D7" --description "In backlog, awaiting triage or deferred"
gh label create "status:ready" --repo "$OWNER_REPO" --color "0E8A16" --description "Ready to work on"
gh label create "status:in-progress" --repo "$OWNER_REPO" --color "FBCA04" --description "Currently being worked on"
gh label create "status:blocked" --repo "$OWNER_REPO" --color "D73A4A" --description "Cannot proceed, waiting for info or intentionally paused"
gh label create "status:ai-review" --repo "$OWNER_REPO" --color "1D76DB" --description "Integrator reviews ALL tasks"
gh label create "status:human-review" --repo "$OWNER_REPO" --color "C2E0C6" --description "User reviews BIG tasks only"
gh label create "status:merge-release" --repo "$OWNER_REPO" --color "5319E7" --description "Ready to merge"
gh label create "status:done" --repo "$OWNER_REPO" --color "0E8A16" --description "Completed"
```

### Priority Labels
```bash
gh label create "priority:critical" --repo "$OWNER_REPO" --color "B60205" --description "Must fix immediately"
gh label create "priority:high" --repo "$OWNER_REPO" --color "D93F0B" --description "High priority"
gh label create "priority:normal" --repo "$OWNER_REPO" --color "FBCA04" --description "Normal priority"
gh label create "priority:low" --repo "$OWNER_REPO" --color "0E8A16" --description "Low priority"
```

### Type Labels
```bash
gh label create "type:feature" --repo "$OWNER_REPO" --color "1D76DB" --description "New functionality"
gh label create "type:bug" --repo "$OWNER_REPO" --color "D73A4A" --description "Something isn't working"
gh label create "type:refactor" --repo "$OWNER_REPO" --color "FBCA04" --description "Code improvement"
gh label create "type:docs" --repo "$OWNER_REPO" --color "0075CA" --description "Documentation"
gh label create "type:test" --repo "$OWNER_REPO" --color "7057FF" --description "Testing improvements"
gh label create "type:chore" --repo "$OWNER_REPO" --color "CFD3D7" --description "Maintenance"
```

## Query Labels

```bash
# Find all issues assigned to implementer-1
gh issue list --repo "$OWNER_REPO" --label "assign:implementer-1"

# Find blocked issues
gh issue list --repo "$OWNER_REPO" --label "status:blocked"

# Find high-priority bugs
gh issue list --repo "$OWNER_REPO" --label "priority:high" --label "type:bug"

# Find issues for a specific component
gh issue list --repo "$OWNER_REPO" --label "component:api"
```

## Update Labels

```bash
# Reassign issue (CORRECT - remove then add)
gh issue edit 42 --repo "$OWNER_REPO" --remove-label "assign:implementer-1"
gh issue edit 42 --repo "$OWNER_REPO" --add-label "assign:implementer-2"

# Update status
gh issue edit 42 --repo "$OWNER_REPO" --remove-label "status:in-progress" --add-label "status:ai-review"
```

## Validate Label Cardinality

```bash
# Check if issue has exactly one status label
STATUS_COUNT=$(gh issue view 42 --repo "$OWNER_REPO" --json labels | jq '[.labels[] | select(.name | startswith("status:"))] | length')
if [ "$STATUS_COUNT" -ne 1 ]; then
  echo "ERROR: Issue has $STATUS_COUNT status labels (expected 1)"
fi

# Check if issue has at most one assign label
ASSIGN_COUNT=$(gh issue view 42 --repo "$OWNER_REPO" --json labels | jq '[.labels[] | select(.name | startswith("assign:"))] | length')
if [ "$ASSIGN_COUNT" -gt 1 ]; then
  echo "ERROR: Issue has $ASSIGN_COUNT assign labels (expected 0 or 1)"
fi
```
