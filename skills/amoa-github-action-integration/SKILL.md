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

1. **Choose a Template** from `templates/workflows/`
2. **Copy to Repository**: `cp <template>.yml /path/to/repo/.github/workflows/`
3. **Configure Secrets**: Add `ANTHROPIC_API_KEY` in Settings > Secrets and variables > Actions
4. **Configure Permissions**: Enable "Read and write permissions" and "Allow GitHub Actions to create and approve pull requests" in Settings > Actions > General

---

## Template Details

Three workflow templates are provided: PR Review (triggers on PR events, reviews code quality/bugs/security/performance), Mention Response (triggers on @claude mentions in comments), and Issue Triage (triggers on new issues, auto-labels and assesses priority).
See: `references/template-details.md`

## Customization & Examples

Model selection, tool restrictions, custom prompts, and complete YAML examples for PR review and @claude mention workflows.
See: `references/customization-and-examples.md`

## Error Handling

Troubleshooting for workflow triggers, authentication, permissions, and timeouts.
See: `references/error-handling.md`

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

- [ ] Select and copy workflow template to `.github/workflows/`
- [ ] Add `ANTHROPIC_API_KEY` secret
- [ ] Enable read/write permissions and PR creation for Actions
- [ ] Customize model and tools if needed
- [ ] Test on draft PR or test issue, then monitor costs

## References

- [claude-code-action](https://github.com/anthropics/claude-code-action) | [GitHub Actions docs](https://docs.github.com/en/actions)
- `references/template-details.md` - Workflow template specs
- `references/customization-and-examples.md` - Customization and YAML examples
- `references/error-handling.md` - Troubleshooting

## Examples

See: `references/customization-and-examples.md`

## Resources

See `## References` above.

## Script Output Rules

Scripts MUST write verbose output to `docs_dev/reports/` and emit only `[OK/ERROR] name - summary` on stdout. Scripts in `scripts/amoa_stop_check/` output JSON to stdout (hook requirement).
