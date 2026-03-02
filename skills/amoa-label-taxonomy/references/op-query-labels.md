---
procedure: support-skill
workflow-instruction: support
---

# Operation: Query Labels


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Determine Query Type](#step-1-determine-query-type)
  - [Step 2: Execute Query](#step-2-execute-query)
  - [Step 3: Format Output](#step-3-format-output)
  - [Step 4: View Issue Labels](#step-4-view-issue-labels)
- [Output](#output)
- [Error Handling](#error-handling)
- [Examples](#examples)
  - [Example 1: Find Work for Agent](#example-1-find-work-for-agent)
  - [Example 2: Workload Analysis](#example-2-workload-analysis)
  - [Example 3: Find Unassigned Ready Work](#example-3-find-unassigned-ready-work)

## When to Use

Use this operation when you need to find issues based on their labels, or list labels in a repository.

## Prerequisites

- GitHub CLI (`gh`) authenticated with repository access
- Knowledge of the label taxonomy prefix system

## Procedure

### Step 1: Determine Query Type

Choose the appropriate query based on your goal:

| Goal | Query Type |
|------|------------|
| Find issues with specific label | Single label filter |
| Find issues with multiple labels | AND filter (comma-separated) |
| List all labels in category | Label list with search |
| Find unassigned issues | Exclude label filter |

### Step 2: Execute Query

#### Query Issues by Single Label

```bash
# Find all issues assigned to a specific agent
gh issue list --label "assign:implementer-1"

# Find all in-progress issues
gh issue list --label "status:in-progress"

# Find all high-priority bugs
gh issue list --label "priority:high"
```

#### Query Issues by Multiple Labels (AND)

```bash
# Find high-priority bugs assigned to implementer-1
gh issue list --label "priority:high,type:bug,assign:implementer-1"

# Find in-progress features in the API component
gh issue list --label "status:in-progress,type:feature,component:api"
```

#### Query with State Filter

```bash
# Find open issues with label
gh issue list --label "status:ready" --state open

# Find closed issues for analysis
gh issue list --label "type:bug" --state closed

# Find all issues regardless of state
gh issue list --label "assign:implementer-1" --state all
```

#### List Labels in Category

```bash
# List all assignment labels
gh label list --search "assign:"

# List all status labels
gh label list --search "status:"

# List all labels (no filter)
gh label list
```

### Step 3: Format Output

```bash
# JSON output for parsing
gh issue list --label "assign:implementer-1" --json number,title,labels

# Table with specific columns
gh issue list --label "status:in-progress" --json number,title,assignees

# Get just issue numbers
gh issue list --label "priority:critical" --json number --jq '.[].number'
```

### Step 4: View Issue Labels

```bash
# See all labels on a specific issue
gh issue view 42 --json labels

# See labels in human-readable format
gh issue view 42 --json labels --jq '.labels[].name'
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| Issue List | Table/JSON | Issues matching the label criteria |
| Label List | Table | Labels matching the search pattern |
| Issue Labels | Array | Labels attached to a specific issue |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Empty results | No matching issues | Verify label name spelling and case |
| "label not found" | Label does not exist | Check available labels with `gh label list` |
| Rate limit | Too many API calls | Wait or use `--limit` to reduce results |

## Examples

### Example 1: Find Work for Agent

```bash
# Find all ready tasks for implementer-1
gh issue list --label "assign:implementer-1,status:ready" --json number,title

# Output:
# [{"number": 42, "title": "Implement auth module"}]
```

### Example 2: Workload Analysis

```bash
# Count issues per status
for status in backlog ready in-progress blocked ai-review human-review merge-release done; do
  count=$(gh issue list --label "status:$status" --json number | jq 'length')
  echo "status:$status = $count"
done
```

### Example 3: Find Unassigned Ready Work

```bash
# Find ready issues without assignment (requires jq filtering)
gh issue list --label "status:ready" --json number,title,labels \
  | jq '[.[] | select(.labels | map(.name) | map(startswith("assign:")) | any | not)]'
```
