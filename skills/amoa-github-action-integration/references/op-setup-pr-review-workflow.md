---
procedure: support-skill
workflow-instruction: support
---

# Operation: Setup PR Review Workflow


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Create Workflow Directory](#step-1-create-workflow-directory)
  - [Step 2: Create Workflow File](#step-2-create-workflow-file)
  - [Step 3: Configure Repository Secret](#step-3-configure-repository-secret)
  - [Step 4: Configure Repository Permissions](#step-4-configure-repository-permissions)
  - [Step 5: Verify Workflow](#step-5-verify-workflow)
  - [Step 6: Test on a PR](#step-6-test-on-a-pr)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example](#example)
- [Checklist](#checklist)

## When to Use

Use this operation when setting up automated PR code reviews using Claude Code Action.

## Prerequisites

- GitHub repository with Actions enabled
- ANTHROPIC_API_KEY secret available
- Repository write permissions can be configured

## Procedure

### Step 1: Create Workflow Directory

```bash
# Ensure .github/workflows exists
mkdir -p .github/workflows
```

### Step 2: Create Workflow File

Create `.github/workflows/claude-pr-review.yml`:

```yaml
name: Claude Code Review

on:
  pull_request:
    types: [opened, synchronize, ready_for_review, reopened]

permissions:
  contents: read
  pull-requests: write
  issues: write

# Only one review per PR at a time
concurrency:
  group: claude-review-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  review:
    # Skip draft PRs
    if: github.event.pull_request.draft == false
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run Claude Code Review
        uses: anthropics/claude-code-action@v1
        with:
          prompt: |
            Review this pull request for:

            1. **Code Quality**
               - Design patterns and architecture
               - Naming conventions
               - Code organization and DRY principles

            2. **Potential Bugs**
               - Null/undefined handling
               - Edge cases
               - Race conditions
               - Resource leaks

            3. **Security**
               - Input validation
               - SQL injection
               - XSS vulnerabilities
               - Authentication/authorization issues

            4. **Performance**
               - Algorithm complexity
               - Unnecessary computations
               - Database query optimization
               - Caching opportunities

            5. **Testing**
               - Test coverage for new code
               - Edge case coverage
               - Test clarity and maintainability

            Provide inline comments for specific issues and a summary comment with overall assessment.
          claude_args: |
            --model "claude-sonnet-4-20250514"
            --allowedTools "Read,Glob,Grep,Bash(git diff:*)"
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Step 3: Configure Repository Secret

1. Go to repository **Settings > Secrets and variables > Actions**
2. Click **New repository secret**
3. Name: `ANTHROPIC_API_KEY`
4. Value: Your Anthropic API key
5. Click **Add secret**

### Step 4: Configure Repository Permissions

1. Go to **Settings > Actions > General**
2. Scroll to **Workflow permissions**
3. Select **Read and write permissions**
4. Check **Allow GitHub Actions to create and approve pull requests**
5. Click **Save**

### Step 5: Verify Workflow

```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('.github/workflows/claude-pr-review.yml'))"

# Commit and push
git add .github/workflows/claude-pr-review.yml
git commit -m "Add Claude PR review workflow"
git push
```

### Step 6: Test on a PR

1. Create a test branch
2. Make a small change
3. Open a PR
4. Watch the Actions tab for the review workflow
5. Check PR comments for Claude's review

## Output

| Field | Type | Description |
|-------|------|-------------|
| Workflow File | Path | `.github/workflows/claude-pr-review.yml` |
| Secret Configured | Boolean | ANTHROPIC_API_KEY set |
| Permissions | Boolean | Workflow permissions enabled |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Workflow not triggering | YAML syntax error | Validate YAML |
| Permission denied | Workflow permissions | Enable read/write permissions |
| API key error | Invalid or missing key | Check ANTHROPIC_API_KEY secret |
| Timeout | Review taking too long | Increase timeout or use faster model |

## Example

```yaml
# Minimal PR review workflow
name: Claude PR Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: anthropics/claude-code-action@v1
        with:
          prompt: "Review this PR for code quality and bugs"
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Checklist

- [ ] Create .github/workflows directory
- [ ] Create claude-pr-review.yml file
- [ ] Add ANTHROPIC_API_KEY secret
- [ ] Enable workflow permissions
- [ ] Enable PR creation permission
- [ ] Validate YAML syntax
- [ ] Commit and push workflow
- [ ] Test on a draft PR
- [ ] Verify review comments appear
