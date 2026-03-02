---
operation: create-github-issues
procedure: proc-create-task-plan
workflow-instruction: Step 12 - Task Plan Creation
parent-skill: eoa-two-phase-mode
parent-plugin: emasoft-orchestrator-agent
version: 1.0.0
---

# Create GitHub Issues


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Prepare Issue Content](#step-1-prepare-issue-content)
- [Module: [Module Name]](#module-module-name)
  - [Description](#description)
  - [Acceptance Criteria](#acceptance-criteria)
  - [Priority](#priority)
  - [Dependencies](#dependencies)
  - [Related](#related)
  - [Step 2: Determine Labels](#step-2-determine-labels)
  - [Step 3: Create Issues Using gh CLI](#step-3-create-issues-using-gh-cli)
- [Module: Core Authentication](#module-core-authentication)
  - [Description](#description)
  - [Acceptance Criteria](#acceptance-criteria)
  - [Priority](#priority)
  - [Related](#related)
  - [Step 4: Link Dependencies](#step-4-link-dependencies)
  - [Step 5: Update State File](#step-5-update-state-file)
- [Checklist](#checklist)
- [Examples](#examples)
  - [Example: Complete Module Issue](#example-complete-module-issue)
- [Module: Google OAuth2 Integration](#module-google-oauth2-integration)
  - [Description](#description)
  - [Acceptance Criteria](#acceptance-criteria)
  - [Priority](#priority)
  - [Dependencies](#dependencies)
  - [Technical Notes](#technical-notes)
  - [Related](#related)
  - [Example: Batch Issue Creation Script](#example-batch-issue-creation-script)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## When to Use

Trigger this operation when:
- Plan phase is being approved and transitioning to orchestration
- Modules need to be tracked in GitHub for visibility
- Human developers will be assigned to modules

## Prerequisites

- Modules are defined with acceptance criteria
- GitHub repository exists and is accessible
- GitHub CLI (gh) is authenticated

## Procedure

### Step 1: Prepare Issue Content

For each module, prepare the issue content:

```markdown
## Module: [Module Name]

### Description
[Module description from plan]

### Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

### Priority
[high|medium|low]

### Dependencies
- Depends on: #[issue-number] ([module-name])
- Blocked by: [module-ids]

### Related
- Plan ID: [plan-id]
- Module ID: [module-id]
```

### Step 2: Determine Labels

Apply consistent labels:

| Label | Usage |
|-------|-------|
| `module` | All module issues |
| `priority-high` / `priority-medium` / `priority-low` | Priority level |
| `status:todo` | Initial status |
| `status:in-progress` | When assigned and started |
| `status:review` | When PR submitted |
| `status:done` | When completed |

### Step 3: Create Issues Using gh CLI

```bash
# Create module issue
gh issue create \
  --title "[Module] Core Authentication" \
  --body "$(cat <<'EOF'
## Module: Core Authentication

### Description
Implementation of user login, logout, and session management.

### Acceptance Criteria
- [ ] Users can login with email/password
- [ ] Users receive JWT token valid for 24h
- [ ] Token refresh works correctly
- [ ] Logout invalidates session

### Priority
high

### Related
- Plan ID: plan-20260205-143022
- Module ID: auth-core
EOF
)" \
  --label "module,priority-high,status:todo"
```

### Step 4: Link Dependencies

After creating all issues, add dependency links:

```bash
# Get issue numbers
AUTH_CORE_ISSUE=1
OAUTH_GOOGLE_ISSUE=2

# Add dependency comment to dependent issue
gh issue comment $OAUTH_GOOGLE_ISSUE \
  --body "**Dependencies:** Blocked by #$AUTH_CORE_ISSUE (auth-core)"
```

### Step 5: Update State File

Record created issues in orchestration state file:

```yaml
modules:
  - id: "auth-core"
    name: "Core Authentication"
    github_issue: 1
    github_issue_url: "https://github.com/owner/repo/issues/1"
    status: "todo"

  - id: "oauth-google"
    name: "Google OAuth2"
    github_issue: 2
    github_issue_url: "https://github.com/owner/repo/issues/2"
    status: "blocked"
    blocked_by: ["auth-core"]
```

## Checklist

Copy this checklist and track your progress:
- [ ] Verify gh CLI is authenticated (`gh auth status`)
- [ ] Prepare issue content for each module
- [ ] Determine labels to apply
- [ ] Create issues using gh CLI
- [ ] Record issue numbers
- [ ] Add dependency comments/links
- [ ] Update state file with issue URLs
- [ ] Verify all issues created successfully

## Examples

### Example: Complete Module Issue

**Command:**
```bash
gh issue create \
  --title "[Module] Google OAuth2 Integration" \
  --body "$(cat <<'EOF'
## Module: Google OAuth2 Integration

### Description
Implementation of Google sign-in support using OAuth2.

### Acceptance Criteria
- [ ] Google sign-in button renders on login page
- [ ] OAuth2 flow redirects to Google and back
- [ ] Token exchange works correctly
- [ ] New users are created in database
- [ ] Existing users can link Google account
- [ ] Token refresh handles expiration

### Priority
medium

### Dependencies
- Blocked by: #1 (auth-core)

### Technical Notes
- Use Google OAuth2 library
- Store refresh tokens securely
- Handle CORS for redirect

### Related
- Plan ID: plan-20260205-143022
- Module ID: oauth-google
- Design Doc: design/auth/google-oauth-spec.md
EOF
)" \
  --label "module,priority-medium,status:blocked"
```

### Example: Batch Issue Creation Script

```bash
#!/bin/bash
# Create all module issues from plan

# Module 1: auth-core
AUTH_CORE=$(gh issue create \
  --title "[Module] Core Authentication" \
  --body "..." \
  --label "module,priority-high,status:todo" \
  --json number -q '.number')

# Module 2: oauth-google (depends on auth-core)
OAUTH_GOOGLE=$(gh issue create \
  --title "[Module] Google OAuth2" \
  --body "## Dependencies\nBlocked by: #$AUTH_CORE" \
  --label "module,priority-medium,status:blocked" \
  --json number -q '.number')

# Module 3: oauth-github (depends on auth-core)
OAUTH_GITHUB=$(gh issue create \
  --title "[Module] GitHub OAuth2" \
  --body "## Dependencies\nBlocked by: #$AUTH_CORE" \
  --label "module,priority-medium,status:blocked" \
  --json number -q '.number')

echo "Created issues: auth-core=#$AUTH_CORE, oauth-google=#$OAUTH_GOOGLE, oauth-github=#$OAUTH_GITHUB"
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `gh: command not found` | gh CLI not installed | Install with `brew install gh` |
| Authentication error | gh not logged in | Run `gh auth login` |
| Repository not found | Wrong directory or remote | Verify `gh repo view` works |
| Label not found | Label doesn't exist | Create label first with `gh label create` |
| Issue create failed | Network or permission issue | Check permissions, retry |

## Related Operations

- [op-approve-plan-transition.md](op-approve-plan-transition.md) - Issues created during transition
- [op-schedule-claude-tasks.md](op-schedule-claude-tasks.md) - Claude tasks parallel GitHub issues
- [op-decompose-goals-to-modules.md](op-decompose-goals-to-modules.md) - Modules become issues
