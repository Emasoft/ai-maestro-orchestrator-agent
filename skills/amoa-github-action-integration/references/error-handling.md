## Table of Contents

- [Workflow Not Triggering](#workflow-not-triggering)
- [Authentication Errors](#authentication-errors)
- [Permission Denied Errors](#permission-denied-errors)
- [Timeout Issues](#timeout-issues)

---

## Workflow Not Triggering

1. Check workflow file is in `.github/workflows/`
2. Verify YAML syntax is valid
3. Ensure trigger conditions match your action

## Authentication Errors

1. Verify `ANTHROPIC_API_KEY` secret is set
2. Check API key has not expired
3. Ensure key has required permissions

## Permission Denied Errors

1. Enable "Read and write permissions" in repository settings
2. Add required permissions block to workflow

## Timeout Issues

1. Increase `timeout-minutes` in workflow
2. Consider using a faster model for large repos
