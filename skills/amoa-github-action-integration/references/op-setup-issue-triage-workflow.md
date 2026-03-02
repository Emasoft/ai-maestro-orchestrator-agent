---
procedure: support-skill
workflow-instruction: support
---

# Operation: Setup Issue Triage Workflow


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Ensure Labels Exist](#step-1-ensure-labels-exist)
  - [Step 2: Create Workflow File](#step-2-create-workflow-file)
  - [Step 3: Configure Permissions](#step-3-configure-permissions)
  - [Step 4: Customize Triage Rules](#step-4-customize-triage-rules)
  - [Step 5: Test the Workflow](#step-5-test-the-workflow)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example](#example)
- [Checklist](#checklist)

## When to Use

Use this operation when setting up automated issue triage using Claude Code Action.

## Prerequisites

- GitHub repository with Actions enabled
- ANTHROPIC_API_KEY secret available
- Labels created for triage (type:*, priority:*, component:*)

## Procedure

### Step 1: Ensure Labels Exist

Create required labels if not present:

```bash
# Type labels
gh label create "type:bug" --description "Bug report" --color "d73a4a"
gh label create "type:feature" --description "Feature request" --color "a2eeef"
gh label create "type:docs" --description "Documentation" --color "0075ca"
gh label create "type:question" --description "Question" --color "d876e3"

# Priority labels
gh label create "priority:critical" --description "Critical priority" --color "b60205"
gh label create "priority:high" --description "High priority" --color "ff6b6b"
gh label create "priority:normal" --description "Normal priority" --color "fbca04"
gh label create "priority:low" --description "Low priority" --color "0e8a16"

# Component labels (customize for your project)
gh label create "component:api" --description "API related" --color "c5def5"
gh label create "component:ui" --description "UI related" --color "bfdadc"
gh label create "component:core" --description "Core functionality" --color "fef2c0"
```

### Step 2: Create Workflow File

Create `.github/workflows/claude-issue-triage.yml`:

```yaml
name: Claude Issue Triage

on:
  issues:
    types: [opened]

permissions:
  contents: read
  issues: write

jobs:
  triage:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Triage issue
        uses: anthropics/claude-code-action@v1
        with:
          prompt: |
            Triage this new issue by analyzing its content and applying appropriate labels.

            Issue Title: ${{ github.event.issue.title }}
            Issue Body: ${{ github.event.issue.body }}
            Author: ${{ github.event.issue.user.login }}

            Available labels:
            - Type: type:bug, type:feature, type:docs, type:question
            - Priority: priority:critical, priority:high, priority:normal, priority:low
            - Component: component:api, component:ui, component:core

            Tasks:
            1. Determine the issue type (bug, feature, docs, question)
            2. Assess priority based on impact and urgency
            3. Identify affected component(s) if determinable
            4. Apply appropriate labels using: gh issue edit ${{ github.event.issue.number }} --add-label "label1,label2"
            5. Add a welcome comment acknowledging the issue and summarizing the triage

            Guidelines:
            - Default to priority:normal if unclear
            - Only add component labels if clearly identifiable
            - Be welcoming in the response
            - If issue lacks information, add a comment requesting clarification
          claude_args: |
            --model "claude-sonnet-4-20250514"
            --allowedTools "Read,Glob,Grep,Bash(gh issue:*)"
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Step 3: Configure Permissions

1. Go to **Settings > Actions > General**
2. Enable **Read and write permissions**

### Step 4: Customize Triage Rules

Adjust the prompt for your project's specific needs:

```yaml
# For specific triage rules
prompt: |
  Triage rules for this project:
  - Security issues are always priority:critical
  - Performance issues default to priority:high
  - Typos and minor docs are priority:low
  - If "regression" mentioned, add type:bug and priority:high
```

### Step 5: Test the Workflow

1. Create a test issue with a clear bug report
2. Watch Actions tab for triage workflow
3. Verify labels are applied
4. Check for welcome comment

## Output

| Field | Type | Description |
|-------|------|-------------|
| Workflow File | Path | `.github/workflows/claude-issue-triage.yml` |
| Labels Applied | Array | Labels added to the issue |
| Welcome Comment | Comment | Triage summary comment |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Labels not applied | Label doesn't exist | Create missing labels first |
| Wrong type detected | Ambiguous issue | Improve triage prompt |
| No comment added | Action didn't complete | Check workflow logs |

## Example

```yaml
# Minimal triage workflow
name: Issue Triage

on:
  issues:
    types: [opened]

jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: anthropics/claude-code-action@v1
        with:
          prompt: |
            Triage issue: ${{ github.event.issue.title }}
            Body: ${{ github.event.issue.body }}

            Apply labels using gh issue edit command.
          claude_args: |
            --allowedTools "Bash(gh issue:*)"
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Checklist

- [ ] Create required labels (type:*, priority:*, component:*)
- [ ] Create claude-issue-triage.yml workflow
- [ ] Configure issue write permissions
- [ ] Customize triage prompt for project
- [ ] Define triage rules in prompt
- [ ] Test with a new issue
- [ ] Verify labels applied correctly
- [ ] Verify welcome comment posted
