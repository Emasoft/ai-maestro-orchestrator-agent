---
procedure: support-skill
workflow-instruction: support
---

# Operation: Customize Workflow


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Change the Model](#step-1-change-the-model)
  - [Step 2: Restrict Available Tools](#step-2-restrict-available-tools)
  - [Step 3: Customize Prompts](#step-3-customize-prompts)
  - [Step 4: Add Trigger Conditions](#step-4-add-trigger-conditions)
  - [Step 5: Add Concurrency Control](#step-5-add-concurrency-control)
  - [Step 6: Add Timeout and Retry](#step-6-add-timeout-and-retry)
  - [Step 7: Add Labels Based on Review](#step-7-add-labels-based-on-review)
  - [Step 8: Integrate with Other Actions](#step-8-integrate-with-other-actions)
- [Output](#output)
- [Error Handling](#error-handling)
- [Examples](#examples)
  - [Example 1: Security-Focused Review](#example-1-security-focused-review)
  - [Example 2: Documentation Check](#example-2-documentation-check)
  - [Example 3: Performance Review](#example-3-performance-review)
- [Checklist](#checklist)

## When to Use

Use this operation when customizing Claude Code Action workflows for your specific project needs.

## Prerequisites

- Base workflow already set up
- Understanding of your project's requirements
- Knowledge of available claude_args options

## Procedure

### Step 1: Change the Model

```yaml
# Default (Sonnet - fast, cost-effective)
claude_args: |
  --model "claude-sonnet-4-20250514"

# For complex reviews (Opus - more thorough)
claude_args: |
  --model "claude-opus-4-5-20251101"
```

### Step 2: Restrict Available Tools

```yaml
# Read-only review (safest)
claude_args: |
  --allowedTools "Read,Glob,Grep"

# Allow git operations
claude_args: |
  --allowedTools "Read,Glob,Grep,Bash(git diff:*,git log:*)"

# Allow issue operations
claude_args: |
  --allowedTools "Read,Glob,Grep,Bash(gh issue:*)"

# Full tool access (use carefully)
claude_args: |
  --allowedTools "Read,Glob,Grep,Bash,Edit"
```

### Step 3: Customize Prompts

```yaml
# Project-specific review prompt
prompt: |
  Review this PR with focus on our project standards:

  ## Our Coding Standards
  - Use TypeScript strict mode
  - All functions must have JSDoc comments
  - Maximum 50 lines per function
  - Required test coverage: 80%

  ## Our Architecture
  - Services in src/services/
  - Controllers in src/controllers/
  - No direct database access in controllers

  ## Review Focus
  1. Architecture compliance
  2. TypeScript strict compliance
  3. Test coverage
  4. Documentation completeness
```

### Step 4: Add Trigger Conditions

```yaml
on:
  pull_request:
    types: [opened, synchronize, ready_for_review]
    # Only review specific paths
    paths:
      - 'src/**'
      - 'tests/**'
      - '!**/*.md'
    # Only specific branches
    branches:
      - main
      - 'release/**'

jobs:
  review:
    # Skip draft PRs and bot PRs
    if: |
      github.event.pull_request.draft == false &&
      github.actor != 'dependabot[bot]'
```

### Step 5: Add Concurrency Control

```yaml
# Prevent multiple reviews of same PR
concurrency:
  group: claude-review-${{ github.event.pull_request.number }}
  cancel-in-progress: true

# Or allow queuing
concurrency:
  group: claude-review-${{ github.event.pull_request.number }}
  cancel-in-progress: false
```

### Step 6: Add Timeout and Retry

```yaml
jobs:
  review:
    timeout-minutes: 30

    steps:
      - uses: anthropics/claude-code-action@v1
        continue-on-error: true
        id: review

      - name: Retry on failure
        if: steps.review.outcome == 'failure'
        uses: anthropics/claude-code-action@v1
        with:
          prompt: "Brief review due to time constraints..."
          claude_args: |
            --model "claude-sonnet-4-20250514"
```

### Step 7: Add Labels Based on Review

```yaml
- name: Run review
  id: review
  uses: anthropics/claude-code-action@v1
  with:
    prompt: "Review and output JSON: {\"approved\": bool, \"severity\": \"none|minor|major\"}"

- name: Add labels
  if: contains(steps.review.outputs.result, '"severity": "major"')
  run: gh pr edit ${{ github.event.pull_request.number }} --add-label "needs-revision"
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Step 8: Integrate with Other Actions

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run lint

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm test

  claude-review:
    needs: [lint, test]  # Only review if lint and tests pass
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          prompt: |
            Lint and tests have passed. Review for:
            - Code quality
            - Architecture
            - Security
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| Customized Workflow | YAML | Modified workflow file |
| Model Selection | String | Chosen Claude model |
| Tool Restrictions | Array | Allowed tools list |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Invalid claude_args | Syntax error | Check argument formatting |
| Model not available | Wrong model name | Use valid model ID |
| Tool not allowed | Security restriction | Add to allowedTools |
| Timeout | Review too slow | Increase timeout or use Sonnet |

## Examples

### Example 1: Security-Focused Review

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    prompt: |
      Security-focused code review:
      1. Check for hardcoded secrets
      2. Verify input validation
      3. Look for SQL injection
      4. Check authentication
      5. Review authorization

      CRITICAL: Report any security issues found.
    claude_args: |
      --model "claude-opus-4-5-20251101"
      --allowedTools "Read,Glob,Grep"
```

### Example 2: Documentation Check

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    prompt: |
      Check documentation:
      1. All public APIs have JSDoc
      2. README is updated
      3. CHANGELOG has entry
      4. API docs are current
```

### Example 3: Performance Review

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    prompt: |
      Performance review:
      1. Check algorithm complexity
      2. Look for N+1 queries
      3. Identify unnecessary loops
      4. Check memory usage patterns
      5. Suggest optimizations
```

## Checklist

- [ ] Determine customization needs
- [ ] Select appropriate model
- [ ] Configure allowed tools
- [ ] Customize prompt for project
- [ ] Set trigger conditions
- [ ] Add concurrency control
- [ ] Configure timeout
- [ ] Test customized workflow
- [ ] Document customizations for team
