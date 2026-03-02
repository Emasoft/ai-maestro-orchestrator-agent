---
procedure: support-skill
workflow-instruction: support
---

# Operation: Create Label


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Determine Label Category](#step-1-determine-label-category)
  - [Step 2: Choose Label Value](#step-2-choose-label-value)
  - [Step 3: Select Color](#step-3-select-color)
  - [Step 4: Create the Label](#step-4-create-the-label)
  - [Step 5: Verify Creation](#step-5-verify-creation)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example](#example)

## When to Use

Use this operation when you need to create a new GitHub label following the emasoft label taxonomy.

## Prerequisites

- GitHub CLI (`gh`) authenticated with repository access
- Understanding of label categories and naming conventions

## Procedure

### Step 1: Determine Label Category

Choose the appropriate prefix based on purpose:

| Prefix | Purpose |
|--------|---------|
| `assign:` | Agent assignment tracking |
| `status:` | Workflow state |
| `priority:` | Urgency level |
| `type:` | Kind of work |
| `component:` | Affected code areas |
| `effort:` | Size estimate |
| `platform:` | Target platforms |
| `toolchain:` | Required tools |
| `review:` | PR review status |

### Step 2: Choose Label Value

Select an appropriate value for the category. Values should be:
- Lowercase with hyphens (no spaces)
- Descriptive but concise
- Consistent with existing labels in the category

### Step 3: Select Color

Choose a color based on category conventions:

| Category | Color Convention |
|----------|------------------|
| `assign:` | Blues/purples (#1d76db, #9b59b6) |
| `status:` | Workflow colors (green=ready, yellow=progress, red=blocked) |
| `priority:` | Urgency (red=critical, orange=high, yellow=normal, green=low) |
| `type:` | Category colors |
| `component:` | Light pastels |
| `effort:` | Size-based (green=small, red=large) |

### Step 4: Create the Label

```bash
# Syntax
gh label create "<category>:<value>" --description "<description>" --color "<hex_color>"

# Example: Create assignment label
gh label create "assign:implementer-1" --description "Assigned to implementer-1" --color "1d76db"

# Example: Create status label
gh label create "status:in-progress" --description "Work actively in progress" --color "fbca04"

# Example: Create priority label
gh label create "priority:high" --description "High priority - address within 1-2 days" --color "ff6b6b"
```

### Step 5: Verify Creation

```bash
# List labels matching pattern
gh label list --search "assign:"
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| Label Name | String | Full label name in `category:value` format |
| Creation Status | Boolean | Whether label was created successfully |
| CLI Output | Text | Confirmation message from `gh label create` |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "Label already exists" | Duplicate label name | Check existing labels with `gh label list --search "pattern"` |
| "Resource not accessible" | Insufficient permissions | Verify `gh auth status` and repository access |
| "Invalid color" | Color format wrong | Use 6-character hex without # prefix |

## Example

```bash
# Create a complete set of effort labels
gh label create "effort:xs" --description "Extra small - < 1 hour" --color "0e8a16"
gh label create "effort:s" --description "Small - 1-4 hours" --color "5eb95e"
gh label create "effort:m" --description "Medium - 4-8 hours" --color "fbca04"
gh label create "effort:l" --description "Large - 1-2 days" --color "ff9f1c"
gh label create "effort:xl" --description "Extra large - > 2 days" --color "cb2431"
```
