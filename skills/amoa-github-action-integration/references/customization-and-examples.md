## Table of Contents

- [Changing the Model](#changing-the-model)
- [Restricting Tools](#restricting-tools)
- [Custom Prompts](#custom-prompts)
- [Example 1: Basic PR Review Setup](#example-1-basic-pr-review-setup)
- [Example 2: @claude Mention Handler](#example-2-claude-mention-handler)

---

## Changing the Model

Edit the `claude_args` section in any workflow:

```yaml
claude_args: |
  --model "claude-sonnet-4-20250514"  # or claude-opus-4-5-20251101
```

## Restricting Tools

Modify the `--allowedTools` argument to limit what Claude can do:

```yaml
--allowedTools "Read,Glob,Grep"  # Read-only, no bash
```

## Custom Prompts

Edit the `prompt` section to customize Claude's behavior for your project's specific needs.

---

## Example 1: Basic PR Review Setup

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

## Example 2: @claude Mention Handler

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
