---
name: amoa-github-action-integration
description: "Trigger with Claude Code action requests. Use when setting up Claude Code in GitHub Actions for automated PR reviews, @claude mention responses, and issue triage."
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
agent: amoa-main
context: fork
user-invocable: false
workflow-instruction: "support"
procedure: "support-skill"
---

# Claude Code Action Integration

## Prerequisites

- GitHub repository with Actions enabled
- Anthropic API key (ANTHROPIC_API_KEY secret)
- Repository write permissions configured
- Understanding of GitHub Actions workflow syntax

## Instructions

1. Choose the appropriate workflow template from `templates/workflows/` based on your use case (PR review, @claude mention, or issue triage)
2. Copy the selected YAML file to your repository's `.github/workflows/` directory
3. Add the `ANTHROPIC_API_KEY` secret in your repository settings under Settings > Secrets and variables > Actions
4. Configure repository permissions by enabling "Read and write permissions" and "Allow GitHub Actions to create and approve pull requests" in Settings > Actions > General
5. Customize the workflow file if needed (model selection, allowed tools, custom prompts)
6. Test the workflow on a draft PR or test issue to verify it triggers correctly
7. Monitor API usage and costs after deployment

## Trigger Conditions

- User asks to "set up automated code review"
- User wants "Claude to review PRs automatically"
- User asks about "GitHub Actions with Claude"
- User needs "@claude mention integration"
- User wants "automated issue triage"

---

## Overview

The `claude-code-action` is Anthropic's official GitHub Action for running Claude Code in CI/CD workflows. This skill provides ready-to-use workflow templates for common integration patterns.

## Available Templates

| Template | Purpose | Location |
|----------|---------|----------|
| **claude-pr-review.yml** | Automatic PR code review | `templates/workflows/` |
| **claude-mention.yml** | @claude mention responses | `templates/workflows/` |
| **claude-issue-triage.yml** | Automated issue triage | `templates/workflows/` |

---

## Quick Start

### Step 1: Choose a Template

Select the workflow template that matches your use case from `templates/workflows/`.

### Step 2: Copy to Repository

Copy the YAML file to your repository's `.github/workflows/` directory:

```bash
# Example: Set up PR review
cp claude-pr-review.yml /path/to/repo/.github/workflows/
```

### Step 3: Configure Secrets

Add required secrets in your repository settings:

1. Go to **Settings > Secrets and variables > Actions**
2. Add `ANTHROPIC_API_KEY` with your Anthropic API key

### Step 4: Configure Permissions

1. Go to **Settings > Actions > General**
2. Under "Workflow permissions", select "Read and write permissions"
3. Check "Allow GitHub Actions to create and approve pull requests"

---

## Template Details

### PR Review Workflow

**File**: `templates/workflows/claude-pr-review.yml`

**Triggers**:
- Pull request opened
- New commits pushed to PR
- PR marked ready for review
- PR reopened

**Features**:
- Comprehensive code review (quality, bugs, security, performance)
- Inline comments on specific code issues
- Summary comment with overall assessment
- Concurrency control (one review per PR at a time)
- Draft PR handling (skips drafts)

**Review Categories**:
1. Code Quality - patterns, naming, organization, DRY
2. Potential Bugs - null handling, edge cases, race conditions
3. Security - injection, XSS, auth issues
4. Performance - complexity, queries, caching
5. Testing - coverage, edge cases, clarity

### Mention Response Workflow

**File**: `templates/workflows/claude-mention.yml`

**Triggers**:
- @claude mentioned in issue comment
- @claude mentioned in PR comment

**Features**:
- Responds to direct questions
- Provides code explanations
- Suggests fixes for reported issues
- Answers architecture questions

### Issue Triage Workflow

**File**: `templates/workflows/claude-issue-triage.yml`

**Triggers**:
- New issue opened

**Features**:
- Automatic label assignment
- Priority assessment
- Initial response to reporter
- Related issue linking

---

## Customization

### Changing the Model

Edit the `claude_args` section in any workflow:

```yaml
claude_args: |
  --model "claude-sonnet-4-20250514"  # or claude-opus-4-5-20251101
```

### Restricting Tools

Modify the `--allowedTools` argument to limit what Claude can do:

```yaml
--allowedTools "Read,Glob,Grep"  # Read-only, no bash
```

### Custom Prompts

Edit the `prompt` section to customize Claude's behavior for your project's specific needs.

---

## Examples

### Example 1: Basic PR Review Setup

```yaml
# .github/workflows/claude-review.yml
name: Claude PR Review

on:
  pull_request:
    types: [opened, synchronize, ready_for_review]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          prompt: "Review this PR for code quality and potential bugs"
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Example 2: @claude Mention Handler

```yaml
# .github/workflows/claude-mention.yml
name: Claude Mention

on:
  issue_comment:
    types: [created]

jobs:
  respond:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          prompt: "Respond to this comment helpfully"
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

---

## Error Handling

### Workflow Not Triggering

1. Check workflow file is in `.github/workflows/`
2. Verify YAML syntax is valid
3. Ensure trigger conditions match your action

### Authentication Errors

1. Verify `ANTHROPIC_API_KEY` secret is set
2. Check API key has not expired
3. Ensure key has required permissions

### Permission Denied Errors

1. Enable "Read and write permissions" in repository settings
2. Add required permissions block to workflow

### Timeout Issues

1. Increase `timeout-minutes` in workflow
2. Consider using a faster model for large repos

---

## Resources

- [claude-code-action GitHub](https://github.com/anthropics/claude-code-action) - Official action repository
- [GitHub Actions Documentation](https://docs.github.com/en/actions) - Actions reference
- `templates/workflows/claude-pr-review.yml` - PR review template
- `templates/workflows/claude-mention.yml` - Mention handler template
- `templates/workflows/claude-issue-triage.yml` - Issue triage template

---

## Best Practices

1. **Start with PR Review** - Most common and valuable integration
2. **Use Sonnet for Speed** - Faster reviews, lower cost
3. **Limit Tools** - Only allow necessary tools for security
4. **Test on Draft PRs** - Test workflow before enabling widely
5. **Monitor Costs** - Watch API usage with track_progress enabled

---

## Output

| Field | Type | Description |
|-------|------|-------------|
| Workflow File | YAML | GitHub Actions workflow configured in `.github/workflows/` |
| API Key Secret | Secret | ANTHROPIC_API_KEY configured in repository settings |
| Permissions | Config | Repository permissions set to "Read and write" |
| Status | Boolean | Workflow enabled and ready to trigger |

---

## Checklist

Copy this checklist and track your progress:

- [ ] Select appropriate workflow template (PR review, @claude mention, or issue triage)
- [ ] Copy template YAML to `.github/workflows/` directory
- [ ] Add `ANTHROPIC_API_KEY` secret in repository settings
- [ ] Enable "Read and write permissions" for GitHub Actions
- [ ] Enable "Allow GitHub Actions to create and approve pull requests"
- [ ] Customize `claude_args` model if needed (default: sonnet)
- [ ] Customize `--allowedTools` for security requirements
- [ ] Test workflow on a draft PR or test issue
- [ ] Verify workflow triggers correctly
- [ ] Monitor API usage and costs
- [ ] Document custom prompts for team reference
