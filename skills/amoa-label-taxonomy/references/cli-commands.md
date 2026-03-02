# CLI Commands for Label Management

## Create Labels

### Assignment Labels
```bash
gh label create "assign:implementer-1" --color "1D76DB" --description "Assigned to implementer-1"
gh label create "assign:implementer-2" --color "5319E7" --description "Assigned to implementer-2"
gh label create "assign:code-reviewer" --color "0E8A16" --description "Assigned to code reviewer"
gh label create "assign:orchestrator" --color "D876E3" --description "Orchestrator handling"
gh label create "assign:human" --color "FBCA04" --description "Human developer"
```

### Status Labels
```bash
gh label create "status:backlog" --color "CFD3D7" --description "In backlog, awaiting triage or deferred"
gh label create "status:ready" --color "0E8A16" --description "Ready to work on"
gh label create "status:in-progress" --color "FBCA04" --description "Currently being worked on"
gh label create "status:blocked" --color "D73A4A" --description "Cannot proceed, waiting for info or intentionally paused"
gh label create "status:ai-review" --color "1D76DB" --description "Integrator reviews ALL tasks"
gh label create "status:human-review" --color "C2E0C6" --description "User reviews BIG tasks only"
gh label create "status:merge-release" --color "5319E7" --description "Ready to merge"
gh label create "status:done" --color "0E8A16" --description "Completed"
```

### Priority Labels
```bash
gh label create "priority:critical" --color "B60205" --description "Must fix immediately"
gh label create "priority:high" --color "D93F0B" --description "High priority"
gh label create "priority:normal" --color "FBCA04" --description "Normal priority"
gh label create "priority:low" --color "0E8A16" --description "Low priority"
```

### Type Labels
```bash
gh label create "type:feature" --color "1D76DB" --description "New functionality"
gh label create "type:bug" --color "D73A4A" --description "Something isn't working"
gh label create "type:refactor" --color "FBCA04" --description "Code improvement"
gh label create "type:docs" --color "0075CA" --description "Documentation"
gh label create "type:test" --color "7057FF" --description "Testing improvements"
gh label create "type:chore" --color "CFD3D7" --description "Maintenance"
```

## Query Labels

```bash
# Find all issues assigned to implementer-1
gh issue list --label "assign:implementer-1"

# Find blocked issues
gh issue list --label "status:blocked"

# Find high-priority bugs
gh issue list --label "priority:high" --label "type:bug"

# Find issues for a specific component
gh issue list --label "component:api"
```

## Update Labels

```bash
# Reassign issue (CORRECT - remove then add)
gh issue edit 42 --remove-label "assign:implementer-1"
gh issue edit 42 --add-label "assign:implementer-2"

# Update status
gh issue edit 42 --remove-label "status:in-progress" --add-label "status:ai-review"
```

## Validate Label Cardinality

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
