# GitHub Assignment Workflow Reference

This document describes how to assign modules to human developers via GitHub.

---

## Contents

- 7.1 Human Developer Assignment Process
- 7.2 GitHub Issue Assignment
- 7.3 GitHub Project Card Movement
- 7.4 Label Updates
- 7.5 Tracking Progress via GitHub
- 7.6 GitHub Comment Templates
- 7.7 Pull Request Workflow
- 7.8 GitHub CLI Commands Reference

---

## 7.1 Human Developer Assignment Process

When assigning a module to a human developer:

```
1. Verify GitHub Issue exists for module
   ↓
2. Assign issue to developer
   ↓
3. Add appropriate labels
   ↓
4. Move Project card (if using Projects)
   ↓
5. Post assignment comment
   ↓
6. Await developer acknowledgment
   ↓
7. Track progress via GitHub activity
```

---

## 7.2 GitHub Issue Assignment

### Assign via GitHub CLI

```bash
# Assign issue to developer
gh issue edit <ISSUE_NUMBER> --add-assignee <GITHUB_USERNAME>

# Example
gh issue edit 42 --add-assignee dev-alice
```

### Verify Assignment

```bash
# Check issue details
gh issue view 42 --json assignees

# Expected output
{
  "assignees": [
    {"login": "dev-alice"}
  ]
}
```

### Multiple Assignees

For collaborative modules:

```bash
gh issue edit 42 --add-assignee dev-alice --add-assignee dev-bob
```

---

## 7.3 GitHub Project Card Movement

If using GitHub Projects for tracking:

### Project Board Columns

| Column | Status | When to Move |
|--------|--------|--------------|
| Backlog | Pending | Initial state |
| Ready | Pending | Requirements clear, ready to assign |
| In Progress | Assigned | Developer starts work |
| In Review | Review | PR submitted |
| Done | Complete | Merged and verified |

### Move Card via CLI

```bash
# Note: GitHub CLI doesn't directly move Project cards
# Use the web UI or GitHub API

# Via API (example)
gh api graphql -f query='
  mutation {
    moveProjectCard(input: {
      cardId: "CARD_ID",
      columnId: "TARGET_COLUMN_ID"
    }) {
      cardEdge {
        node { id }
      }
    }
  }
'
```

### Alternative: Use Labels for Status

Instead of Project cards, use labels:

```bash
# Remove old status, add new status
gh issue edit 42 --remove-label "status:ready" --add-label "status:in-progress"
```

---

## 7.4 Label Updates

### Standard Labels

| Label | Color | Meaning |
|-------|-------|---------|
| `status:pending` | Gray | Not started |
| `status:in-progress` | Blue | Work in progress |
| `status:review` | Yellow | Under review |
| `status:blocked` | Red | Blocked by issue |
| `priority:high` | Red | High priority |
| `priority:medium` | Yellow | Medium priority |
| `priority:low` | Green | Low priority |
| `type:module` | Purple | Module implementation |
| `assigned` | Teal | Has assignee |

### Update Labels

```bash
# Add multiple labels
gh issue edit 42 \
  --add-label "status:in-progress" \
  --add-label "priority:high" \
  --add-label "assigned"

# Remove label
gh issue edit 42 --remove-label "status:pending"
```

---

## 7.5 Tracking Progress via GitHub

### Monitor Issue Activity

```bash
# View issue with comments
gh issue view 42 --comments

# List recent comments
gh api repos/{owner}/{repo}/issues/42/comments \
  --jq '.[-3:] | .[] | "\(.created_at): \(.body)"'
```

### Monitor Pull Requests

```bash
# List PRs that reference this issue
gh pr list --search "fixes #42"

# View PR status
gh pr view <PR_NUMBER> --json state,reviews,checks
```

### Activity Indicators

| Activity | Meaning |
|----------|---------|
| New comment | Developer update or question |
| PR opened | Work submitted for review |
| PR updated | Changes pushed |
| Review requested | Ready for review |
| Label changed | Status update |

---

## 7.6 GitHub Comment Templates

### Assignment Comment

```markdown
## Module Assignment

Hi @{github_username}, you've been assigned to implement the **{module_name}** module.

### Requirements Summary

{requirements_summary}

### Acceptance Criteria

{acceptance_criteria}

### Getting Started

1. Review the requirements above
2. Comment here to confirm your understanding
3. Ask any clarifying questions
4. Begin implementation when ready

### Expected Timeline

- **Estimated effort**: {hours} hours
- **Target completion**: {date}

Let me know if you have any questions!

/cc @{orchestrator_username}
```

### Progress Check Comment

```markdown
## Progress Check

Hi @{github_username}, checking in on the **{module_name}** module.

Could you provide an update on:
- Current progress (% complete)
- Any blockers or issues?
- Estimated completion date?

Thanks!
```

### Blocker Response Comment

```markdown
## Re: Blocker

@{github_username} regarding the blocker you reported:

> {quoted_blocker}

{resolution}

Let me know if this unblocks you!
```

### Completion Acknowledgment Comment

```markdown
## Implementation Complete

Thank you @{github_username} for completing the **{module_name}** module!

### Verification

- [x] Code review passed
- [x] Tests passing
- [x] Documentation updated
- [x] Merged to main

Great work! Moving on to the next phase.
```

---

## 7.7 Pull Request Workflow

### Developer Creates PR

Expected PR format:

```markdown
## Summary

Implements the {module_name} module as specified in #{issue_number}.

## Changes

- {change_1}
- {change_2}
- {change_3}

## Testing

- Unit tests: {description}
- Integration tests: {description}

## Checklist

- [ ] Tests passing
- [ ] Code follows project style
- [ ] Documentation updated
- [ ] Linked to issue

Fixes #{issue_number}
```

### Review PR

```bash
# View PR details
gh pr view <PR_NUMBER>

# Check CI status
gh pr checks <PR_NUMBER>

# Request changes
gh pr review <PR_NUMBER> --request-changes --body "..."

# Approve
gh pr review <PR_NUMBER> --approve --body "LGTM!"
```

### Merge PR

```bash
# Squash and merge
gh pr merge <PR_NUMBER> --squash --delete-branch

# Or merge commit
gh pr merge <PR_NUMBER> --merge --delete-branch
```

---

## 7.8 GitHub CLI Commands Reference

### Issue Commands

| Command | Purpose |
|---------|---------|
| `gh issue create` | Create new issue |
| `gh issue edit` | Update issue |
| `gh issue view` | View issue details |
| `gh issue comment` | Add comment |
| `gh issue close` | Close issue |
| `gh issue list` | List issues |

### PR Commands

| Command | Purpose |
|---------|---------|
| `gh pr list` | List pull requests |
| `gh pr view` | View PR details |
| `gh pr review` | Review PR |
| `gh pr merge` | Merge PR |
| `gh pr checks` | View CI status |

### Common Options

```bash
# View in JSON format
gh issue view 42 --json title,state,assignees

# Filter lists
gh pr list --state open --assignee dev-alice

# Search
gh issue list --search "module in:title"
```

---

## Summary

The GitHub workflow for human developers:

1. **Assign** - Use `gh issue edit --add-assignee`
2. **Label** - Set status and priority labels
3. **Comment** - Post assignment details
4. **Monitor** - Watch issue/PR activity
5. **Review** - Review submitted PRs
6. **Merge** - Merge when approved

Key differences from AI agents:
- Async communication (hours, not minutes)
- PR-based submission (not direct commits)
- GitHub as primary communication channel
- Less frequent polling (daily vs. 10-15 min)
