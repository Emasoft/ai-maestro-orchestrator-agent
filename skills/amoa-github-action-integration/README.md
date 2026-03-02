# Claude Code Action Integration

Set up Claude Code in GitHub Actions for automated PR reviews, @claude mention responses, and issue triage.

## When to Use

- Setting up automated PR code review with Claude
- Configuring @claude mention responses in issues/PRs
- Enabling AI-powered issue triage and labeling
- Integrating Claude Code into CI/CD pipelines

## Quick Start

1. Copy a workflow template from `templates/workflows/` to your repo's `.github/workflows/`
2. Add `ANTHROPIC_API_KEY` secret to repository settings
3. Enable "Read and write permissions" in Actions settings

## Available Templates

| Template | Purpose |
|----------|---------|
| `claude-pr-review.yml` | Automatic code review on PRs |
| `claude-mention.yml` | Respond to @claude mentions |
| `claude-issue-triage.yml` | Auto-label and triage new issues |

## Key Features

**PR Review**:
- Code quality, bugs, security, performance checks
- Inline comments on specific issues
- Summary with overall assessment

**Mention Response**:
- Answers questions in issues/PRs
- Provides code explanations
- Suggests fixes

**Issue Triage**:
- Automatic label assignment
- Priority assessment
- Initial response to reporter

## Customization

Edit `claude_args` to change model or restrict tools:
```yaml
claude_args: |
  --model "claude-sonnet-4-20250514"
  --allowedTools "Read,Glob,Grep"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Workflow not triggering | Verify YAML in `.github/workflows/`, check trigger conditions |
| Authentication errors | Check `ANTHROPIC_API_KEY` secret is set and valid |
| Permission denied | Enable "Read and write permissions" in Actions settings |

## Best Practices

1. Start with PR Review - most valuable integration
2. Use Sonnet for speed and lower cost
3. Limit tools with `--allowedTools` for security
4. Test on draft PRs before enabling widely

## References

- [claude-code-action GitHub](https://github.com/anthropics/claude-code-action)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- See `SKILL.md` for full documentation
