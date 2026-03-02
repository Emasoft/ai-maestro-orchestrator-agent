---
procedure: support-skill
workflow-instruction: support
---

# Operation: Configure API Key Secret


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Obtain API Key](#step-1-obtain-api-key)
  - [Step 2: Add Secret via GitHub UI](#step-2-add-secret-via-github-ui)
  - [Step 3: Alternative - Add Secret via CLI](#step-3-alternative-add-secret-via-cli)
  - [Step 4: Verify Secret Exists](#step-4-verify-secret-exists)
  - [Step 5: Reference in Workflow](#step-5-reference-in-workflow)
  - [Step 6: Set Up Organization Secret (Optional)](#step-6-set-up-organization-secret-optional)
  - [Step 7: Set Up Environment Secret (Optional)](#step-7-set-up-environment-secret-optional)
- [Output](#output)
- [Error Handling](#error-handling)
- [Security Best Practices](#security-best-practices)
- [Example](#example)
- [Checklist](#checklist)

## When to Use

Use this operation when setting up the ANTHROPIC_API_KEY secret for Claude Code Action workflows.

## Prerequisites

- Anthropic API account with API key
- Repository admin or maintainer access
- GitHub CLI authenticated (for CLI method)

## Procedure

### Step 1: Obtain API Key

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Navigate to API Keys section
3. Create a new key or copy existing key
4. **Important**: Store the key securely - it cannot be viewed again

### Step 2: Add Secret via GitHub UI

1. Navigate to repository on GitHub
2. Click **Settings** tab
3. In sidebar, click **Secrets and variables > Actions**
4. Click **New repository secret**
5. Enter:
   - Name: `ANTHROPIC_API_KEY`
   - Secret: Your API key
6. Click **Add secret**

### Step 3: Alternative - Add Secret via CLI

```bash
# Using GitHub CLI
gh secret set ANTHROPIC_API_KEY

# Paste your API key when prompted
# Or pipe from a file
cat api_key.txt | gh secret set ANTHROPIC_API_KEY
```

### Step 4: Verify Secret Exists

```bash
# List secrets (names only, not values)
gh secret list

# Should show:
# ANTHROPIC_API_KEY  Updated 2024-01-15
```

### Step 5: Reference in Workflow

In your workflow file:

```yaml
jobs:
  my-job:
    steps:
      - uses: anthropics/claude-code-action@v1
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Step 6: Set Up Organization Secret (Optional)

For multiple repositories:

1. Go to Organization Settings
2. Navigate to **Secrets and variables > Actions**
3. Click **New organization secret**
4. Add ANTHROPIC_API_KEY
5. Select which repositories can access it

### Step 7: Set Up Environment Secret (Optional)

For environment-specific keys:

1. Go to repository **Settings > Environments**
2. Create or select environment (e.g., "production")
3. Add ANTHROPIC_API_KEY as environment secret
4. Reference in workflow:

```yaml
jobs:
  my-job:
    environment: production
    steps:
      - uses: anthropics/claude-code-action@v1
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| Secret Name | String | `ANTHROPIC_API_KEY` |
| Scope | String | Repository, Organization, or Environment |
| Access | Array | Workflows that can use the secret |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Secret not found | Wrong name or not created | Verify with `gh secret list` |
| Invalid API key | Key expired or wrong | Get new key from Anthropic Console |
| Permission denied | No admin access | Request admin to add secret |
| Rate limit exceeded | Key usage exceeded | Check Anthropic usage limits |

## Security Best Practices

1. **Never commit API keys** to repository
2. **Rotate keys** periodically
3. **Use environment secrets** for production
4. **Limit repository access** for org secrets
5. **Monitor usage** in Anthropic Console

## Example

```bash
# Complete setup flow

# 1. Create API key file (temporary)
echo "sk-ant-..." > /tmp/api_key.txt

# 2. Add secret
gh secret set ANTHROPIC_API_KEY < /tmp/api_key.txt

# 3. Verify
gh secret list

# 4. Clean up
rm /tmp/api_key.txt

# 5. Test workflow (create test PR or issue)
git checkout -b test-claude-action
echo "test" >> test.txt
git add test.txt
git commit -m "Test Claude action"
git push -u origin test-claude-action
gh pr create --title "Test Claude Action" --body "Testing API key setup"
```

## Checklist

- [ ] Obtain API key from Anthropic Console
- [ ] Navigate to repository Settings
- [ ] Add ANTHROPIC_API_KEY secret
- [ ] Verify secret with `gh secret list`
- [ ] Update workflow to reference secret
- [ ] Test workflow triggers correctly
- [ ] Verify no API key errors in logs
- [ ] Delete temporary key files
