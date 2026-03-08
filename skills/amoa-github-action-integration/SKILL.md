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
---

# Claude Code Action Integration

## Overview

Set up Claude Code in GitHub Actions for PR reviews, @claude mentions, and issue triage.

## Prerequisites

GitHub repo with Actions enabled, Anthropic API key, and write permissions.

## Instructions

1. Copy a template from `templates/workflows/` to `.github/workflows/`
2. Add `ANTHROPIC_API_KEY` secret in repo Settings > Secrets
3. Enable write permissions in Settings > Actions > General
4. Customize model/tools if needed, then test on a draft PR

## Output

Workflow YAML in `.github/workflows/`, API key secret configured, permissions enabled.

## Checklist

Copy this checklist and track your progress:

- [ ] Copy workflow template to `.github/workflows/`
- [ ] Add `ANTHROPIC_API_KEY` secret and enable write permissions
- [ ] Test on draft PR or test issue
- [ ] Monitor API costs

## Error Handling

See [error-handling.md](references/error-handling.md) for troubleshooting triggers, auth, permissions, and timeouts.

## Resources

- [claude-code-action](https://github.com/anthropics/claude-code-action) | [GitHub Actions docs](https://docs.github.com/en/actions)
- [template-details.md](references/template-details.md)
  <!-- TOC: PR Review Workflow | Mention Response Workflow | Issue Triage Workflow -->
- [customization-and-examples.md](references/customization-and-examples.md)
  <!-- TOC: Changing the Model | Restricting Tools | Custom Prompts | Example 1: Basic PR Review Setup | Example 2: @claude Mention Handler -->
- [error-handling.md](references/error-handling.md)
  <!-- TOC: Workflow Not Triggering | Authentication Errors | Permission Denied Errors | Timeout Issues -->

## Examples

**Input:** "set up automated PR review with Claude"
**Output:** `.github/workflows/claude-pr-review.yml` with secrets and permissions configured.
