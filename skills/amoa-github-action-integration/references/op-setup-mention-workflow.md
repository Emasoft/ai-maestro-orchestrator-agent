---
procedure: support-skill
workflow-instruction: support
---

# Operation: Setup @claude Mention Workflow


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Create Workflow File](#step-1-create-workflow-file)
  - [Step 2: Configure Repository Secret](#step-2-configure-repository-secret)
  - [Step 3: Configure Permissions](#step-3-configure-permissions)
  - [Step 4: Customize Triggers (Optional)](#step-4-customize-triggers-optional)
  - [Step 5: Test the Workflow](#step-5-test-the-workflow)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example](#example)
- [Checklist](#checklist)

## When to Use

Use this operation when setting up responses to @claude mentions in issues and PRs.

## Prerequisites

- GitHub repository with Actions enabled
- ANTHROPIC_API_KEY secret available
- Repository write permissions can be configured

## Procedure

### Step 1: Create Workflow File

Create `.github/workflows/claude-mention.yml`:

```yaml
name: Claude Mention Response

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]

permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  respond:
    # Only respond when @claude is mentioned
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Respond to mention
        uses: anthropics/claude-code-action@v1
        with:
          prompt: |
            A user mentioned @claude in a comment. Please respond helpfully.

            Context:
            - Issue/PR: #${{ github.event.issue.number || github.event.pull_request.number }}
            - Comment author: ${{ github.event.comment.user.login }}
            - Comment: ${{ github.event.comment.body }}

            Guidelines:
            1. Address the user's question or request directly
            2. If asking about code, read relevant files before answering
            3. If suggesting changes, provide specific code examples
            4. Be concise but thorough
            5. If you cannot help, explain why and suggest alternatives

            Respond with a helpful comment addressing what was asked.
          claude_args: |
            --model "claude-sonnet-4-20250514"
            --allowedTools "Read,Glob,Grep"
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Step 2: Configure Repository Secret

If not already configured:

1. Go to **Settings > Secrets and variables > Actions**
2. Add `ANTHROPIC_API_KEY` secret

### Step 3: Configure Permissions

1. Go to **Settings > Actions > General**
2. Enable **Read and write permissions**
3. Enable **Allow GitHub Actions to create and approve pull requests**

### Step 4: Customize Triggers (Optional)

```yaml
# Only respond to specific users
if: |
  contains(github.event.comment.body, '@claude') &&
  (github.event.comment.user.login == 'maintainer1' ||
   github.event.comment.user.login == 'maintainer2')

# Only in specific labels
if: |
  contains(github.event.comment.body, '@claude') &&
  contains(github.event.issue.labels.*.name, 'ai-review')
```

### Step 5: Test the Workflow

1. Create a test issue
2. Add a comment: `@claude can you explain this function?`
3. Watch Actions tab for workflow trigger
4. Check issue comments for Claude's response

## Output

| Field | Type | Description |
|-------|------|-------------|
| Workflow File | Path | `.github/workflows/claude-mention.yml` |
| Trigger | Event | `issue_comment` and `pull_request_review_comment` |
| Response | Comment | Claude's response to the mention |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| No response | @claude not detected | Check comment body matching |
| Wrong context | Missing issue/PR context | Verify event payload access |
| Rate limited | Too many mentions | Add rate limiting or cooldown |

## Example

```yaml
# Simple mention handler
name: Claude Mention

on:
  issue_comment:
    types: [created]

jobs:
  respond:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: anthropics/claude-code-action@v1
        with:
          prompt: "Respond to this comment: ${{ github.event.comment.body }}"
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Checklist

- [ ] Create claude-mention.yml workflow
- [ ] Configure trigger conditions
- [ ] Set appropriate permissions
- [ ] Add ANTHROPIC_API_KEY secret (if needed)
- [ ] Customize prompt for your needs
- [ ] Test with a mention comment
- [ ] Verify response is posted
