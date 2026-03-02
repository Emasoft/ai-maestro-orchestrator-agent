# GitHub Project Setup Template

## Overview
This template provides commands and configuration for setting up a GitHub project board with EOA orchestrator integration.

## Project Creation

### Create New Project
```bash
# Create project linked to repository
gh project create \
  --owner {{GITHUB_OWNER}} \
  --title "{{PROJECT_NAME}}" \
  --body "{{PROJECT_DESCRIPTION}}"

# Get project number (will be displayed in output)
# Store this as {{PROJECT_NUMBER}}
```

### Get Project ID
```bash
# List projects to get PROJECT_ID
gh project list --owner {{GITHUB_OWNER}} --format json | jq '.projects[] | select(.title=="{{PROJECT_NAME}}") | .id'

# Store the ID as {{PROJECT_ID}}
```

## Standard EOA Columns

### Column Structure
The EOA orchestrator uses a standard eight-column workflow:

1. **Backlog** - Tasks awaiting triage or prioritization
2. **Todo** - Tasks ready to start, assigned and prioritized
3. **In Progress** - Tasks actively being worked on
4. **AI Review** - Tasks awaiting Integrator AI review
5. **Human Review** - Tasks requiring human review (big or sensitive tasks)
6. **Merge/Release** - Tasks reviewed and ready to merge or release
7. **Done** - Completed tasks
8. **Blocked** - Tasks blocked by dependencies or external factors

### Add Status Field
```bash
# Add single-select Status field
gh project field-create {{PROJECT_NUMBER}} \
  --owner {{GITHUB_OWNER}} \
  --name "Status" \
  --data-type "SINGLE_SELECT" \
  --single-select-options "Backlog,Todo,In Progress,AI Review,Human Review,Merge/Release,Done,Blocked"
```

## Custom Fields

### Platform Field
```bash
# Platform where agent will run
gh project field-create {{PROJECT_NUMBER}} \
  --owner {{GITHUB_OWNER}} \
  --name "Platform" \
  --data-type "SINGLE_SELECT" \
  --single-select-options "macos,linux,docker,cloud,windows"
```

### Priority Field
```bash
gh project field-create {{PROJECT_NUMBER}} \
  --owner {{GITHUB_OWNER}} \
  --name "Priority" \
  --data-type "SINGLE_SELECT" \
  --single-select-options "critical,high,medium,low"
```

### Component Field
```bash
# Which component/module is affected
gh project field-create {{PROJECT_NUMBER}} \
  --owner {{GITHUB_OWNER}} \
  --name "Component" \
  --data-type "TEXT"
```

### Toolchain Field
```bash
# Link to toolchain template
gh project field-create {{PROJECT_NUMBER}} \
  --owner {{GITHUB_OWNER}} \
  --name "Toolchain" \
  --data-type "TEXT"
```

### Agent Assignee Field
```bash
# Which remote agent is assigned
gh project field-create {{PROJECT_NUMBER}} \
  --owner {{GITHUB_OWNER}} \
  --name "Agent" \
  --data-type "TEXT"
```

### Complexity Field (per RULE 13 - no time estimates)
```bash
gh project field-create {{PROJECT_NUMBER}} \
  --owner {{GITHUB_OWNER}} \
  --name "Complexity" \
  --data-type "SINGLE_SELECT" \
  --single-select-options "Simple,Medium,Complex,Epic"
```

## Labels Setup

### Status Labels
```bash
# Status tracking
gh label create "status:backlog" --color "d4c5f9" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "status:todo" --color "D4C5F9" --description "Ready to start" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "status:in-progress" --color "fbca04" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "status:ai-review" --color "0E8A16" --description "Integrator AI review" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "status:human-review" --color "FBCA04" --description "Human review (big tasks)" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "status:merge-release" --color "1D76DB" --description "Ready to merge" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "status:blocked" --color "d93f0b" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "status:done" --color "0075ca" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
```

### Priority Labels
```bash
gh label create "priority:critical" --color "b60205" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "priority:high" --color "d93f0b" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "priority:medium" --color "fbca04" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "priority:low" --color "0e8a16" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
```

### Platform Labels
```bash
gh label create "platform:macos" --color "5319e7" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "platform:linux" --color "0052cc" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "platform:docker" --color "1d76db" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "platform:cloud" --color "006b75" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "platform:windows" --color "5319e7" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
```

### Type Labels
```bash
gh label create "type:feature" --color "a2eeef" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "type:bugfix" --color "d73a4a" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "type:refactor" --color "c5def5" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "type:test" --color "bfdadc" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "type:docs" --color "0075ca" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "type:chore" --color "fef2c0" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
```

### Toolchain Labels
```bash
gh label create "toolchain:python" --color "3572A5" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "toolchain:node" --color "43853d" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "toolchain:rust" --color "dea584" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "toolchain:go" --color "00ADD8" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "toolchain:docker" --color "2496ED" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
```

### Assignment Labels
```bash
# Labels to track which agent is assigned to work on an issue
# Use assign:* prefix consistently across all plugins
gh label create "assign:remote" --color "f9d0c4" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "assign:local" --color "c2e0c6" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
gh label create "assign:orchestrator" --color "bfdadc" --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
```

## Repository Settings

### Enable Issues and Projects
```bash
# Enable issues
gh repo edit {{GITHUB_OWNER}}/{{REPO_NAME}} --enable-issues

# Enable projects
gh repo edit {{GITHUB_OWNER}}/{{REPO_NAME}} --enable-projects
```

### Set Default Branch Protection
```bash
# Require PR reviews
gh api repos/{{GITHUB_OWNER}}/{{REPO_NAME}}/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":[]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":false,"required_approving_review_count":1}' \
  --field restrictions=null
```

## Link Repository to Project

```bash
# Add repository to project
gh project link {{PROJECT_NUMBER}} \
  --owner {{GITHUB_OWNER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}}
```

## Automation Rules

### Auto-add Issues to Project
```bash
# When issue is created, add to project
gh project item-add {{PROJECT_NUMBER}} \
  --owner {{GITHUB_OWNER}} \
  --url https://github.com/{{GITHUB_OWNER}}/{{REPO_NAME}}/issues/{{ISSUE_NUMBER}}
```

### Example Automation Workflow
Create `.github/workflows/project-automation.yml`:

```yaml
name: Project Automation
on:
  issues:
    types: [opened, labeled, assigned]
  pull_request:
    types: [opened, ready_for_review, closed]

jobs:
  add-to-project:
    runs-on: ubuntu-latest
    steps:
      - name: Add issue to project
        if: github.event_name == 'issues' && github.event.action == 'opened'
        run: |
          gh project item-add {{PROJECT_NUMBER}} \
            --owner {{GITHUB_OWNER}} \
            --url ${{ github.event.issue.html_url }}
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Move to In Progress when assigned
        if: github.event_name == 'issues' && github.event.action == 'assigned'
        run: |
          gh project item-edit \
            --project-id {{PROJECT_ID}} \
            --field-id {{STATUS_FIELD_ID}} \
            --value "In Progress"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Verification Checklist

After setup, verify:

- [ ] Project created and visible in GitHub
- [ ] All eight status columns exist
- [ ] All custom fields added
- [ ] All labels created with correct colors
- [ ] Repository linked to project
- [ ] Issues feature enabled
- [ ] Projects feature enabled
- [ ] Branch protection rules configured
- [ ] Automation workflow committed

## Get Field IDs for Scripts

```bash
# Get all field IDs for the project
gh project field-list {{PROJECT_NUMBER}} --owner {{GITHUB_OWNER}} --format json | jq -r '.[] | "\(.name): \(.id)"'

# Store these IDs for use in KANBAN_SYNC_PROTOCOL.md
```

## Example Usage

```bash
# Full setup example
export GITHUB_OWNER="myorg"
export REPO_NAME="myrepo"
export PROJECT_NAME="EOA Development"
export PROJECT_DESCRIPTION="EOA orchestrator task tracking"

# 1. Create project
gh project create --owner $GITHUB_OWNER --title "$PROJECT_NAME" --body "$PROJECT_DESCRIPTION"

# 2. Get project number from output (e.g., 3)
export PROJECT_NUMBER=3

# 3. Add status field
gh project field-create $PROJECT_NUMBER --owner $GITHUB_OWNER --name "Status" --data-type "SINGLE_SELECT" --single-select-options "Backlog,Todo,In Progress,AI Review,Human Review,Merge/Release,Done,Blocked"

# 4. Add other fields (Platform, Priority, etc.)
# ... repeat for each field above

# 5. Create labels
# ... run all label creation commands

# 6. Link repository
gh project link $PROJECT_NUMBER --owner $GITHUB_OWNER --repo $GITHUB_OWNER/$REPO_NAME

# 7. Get field IDs for automation
gh project field-list $PROJECT_NUMBER --owner $GITHUB_OWNER --format json > project-fields.json
```

## Troubleshooting

### Project Not Visible
- Verify organization/user permissions
- Check if projects feature is enabled: `gh repo edit {{GITHUB_OWNER}}/{{REPO_NAME}} --enable-projects`

### Cannot Add Issues to Project
- Verify repository is linked to project
- Check issue URL is correct
- Ensure project number is correct (not project ID)

### Field Updates Not Working
- Field IDs change between projects - always get fresh IDs
- Use `gh project field-list` to verify field names and IDs
- Some fields require specific value formats (e.g., dates: "YYYY-MM-DD")

### Labels Not Showing
- Labels are repository-specific, not project-specific
- Verify you're creating labels in the correct repository
- Check label names don't conflict with existing labels
