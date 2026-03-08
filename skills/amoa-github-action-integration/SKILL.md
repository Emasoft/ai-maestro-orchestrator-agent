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

Integrate Claude Code into GitHub Actions for automated PR reviews, @claude mention responses, and issue triage workflows.

## Prerequisites

- GitHub repository with Actions enabled
- Anthropic API key (ANTHROPIC_API_KEY secret)
- Repository write permissions configured
- Basic GitHub Actions knowledge

## Instructions

1. Choose a workflow template from `templates/workflows/` (PR review, @claude mention, or issue triage)
2. Copy the YAML file to `.github/workflows/`
3. Add `ANTHROPIC_API_KEY` secret in Settings > Secrets and variables > Actions
4. Enable "Read and write permissions" and "Allow GitHub Actions to create and approve pull requests" in Settings > Actions > General
5. Customize model, tools, and prompts if needed
6. Test on a draft PR or test issue, then monitor API costs

## Trigger Conditions

- User asks to "set up automated code review"
- User wants "Claude to review PRs automatically"
- User asks about "GitHub Actions with Claude"
- User needs "@claude mention integration"
- User wants "automated issue triage"

---

## Template Details

PR Review, @claude Mention Response, and Issue Triage templates in `templates/workflows/`.
See: `references/template-details.md`
<!-- TOC: PR Review Workflow | Mention Response Workflow | Issue Triage Workflow -->

## Customization & Examples

Model selection, tool restrictions, custom prompts, and YAML examples.
See: `references/customization-and-examples.md`
<!-- TOC: Changing the Model | Restricting Tools | Custom Prompts | Example 1: Basic PR Review Setup | Example 2: @claude Mention Handler -->

## Error Handling

Troubleshooting for workflow triggers, authentication, permissions, and timeouts.
See: `references/error-handling.md`
<!-- TOC: Workflow Not Triggering | Authentication Errors | Permission Denied Errors | Timeout Issues -->

---

## Best Practices

1. **Start with PR Review** - Most common and valuable integration
2. **Use Sonnet for Speed** - Faster reviews, lower cost
3. **Limit Tools** - Only allow necessary tools for security
4. **Test on Draft PRs** - Test workflow before enabling widely
5. **Monitor Costs** - Watch API usage with track_progress enabled

---

## Output

| Field | Description |
|-------|-------------|
| Workflow File | YAML workflow in `.github/workflows/` |
| API Key Secret | ANTHROPIC_API_KEY in repository settings |
| Permissions | Read and write permissions enabled |
| Status | Workflow enabled and ready to trigger |

---

## Checklist

Copy this checklist and track your progress:

- [ ] Select and copy workflow template to `.github/workflows/`
- [ ] Add `ANTHROPIC_API_KEY` secret
- [ ] Enable read/write permissions and PR creation for Actions
- [ ] Customize model and tools if needed
- [ ] Test on draft PR or test issue, then monitor costs

## Resources

- [claude-code-action](https://github.com/anthropics/claude-code-action) | [GitHub Actions docs](https://docs.github.com/en/actions)
- `references/template-details.md` - Workflow template specs
  <!-- TOC: PR Review Workflow | Mention Response Workflow | Issue Triage Workflow -->
- `references/customization-and-examples.md` - Customization and YAML examples
  <!-- TOC: Changing the Model | Restricting Tools | Custom Prompts | Example 1: Basic PR Review Setup | Example 2: @claude Mention Handler -->
- `references/error-handling.md` - Troubleshooting
  <!-- TOC: Workflow Not Triggering | Authentication Errors | Permission Denied Errors | Timeout Issues -->

## Examples

**Input:** User asks "set up automated PR review with Claude"
**Output:** Workflow `.github/workflows/claude-pr-review.yml` configured with secrets and permissions.

See: `references/customization-and-examples.md`
<!-- TOC: Changing the Model | Restricting Tools | Custom Prompts | Example 1: Basic PR Review Setup | Example 2: @claude Mention Handler -->

## Script Output Rules

Scripts write verbose output to `docs_dev/reports/` and emit only `[OK/ERROR] name - summary` on stdout. Scripts in `scripts/amoa_stop_check/` output JSON to stdout (hook requirement).
