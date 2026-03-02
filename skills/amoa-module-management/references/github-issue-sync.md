# GitHub Issue Synchronization Reference

## Contents

- 6.1 Issue creation format and labels
- 6.2 Issue update synchronization
- 6.3 Issue closure protocols
- 6.4 Label conventions (module, priority:*, status:*)
- 6.5 Manual sync when automation fails
- 6.6 Troubleshooting sync issues

---

## 6.1 Issue Creation Format and Labels

Every module in EOA orchestration has a corresponding GitHub Issue. This section explains how issues are created.

### Automatic Issue Creation

When a module is added via `/add-module`, a GitHub Issue is automatically created using the `gh` CLI.

### Issue Title Format

**Format**: `[Module] {module_name}`

**Examples**:
- `[Module] Core Authentication`
- `[Module] Password Reset`
- `[Module] OAuth Google Integration`

The `[Module]` prefix:
- Distinguishes modules from bugs and feature requests
- Enables filtering: `label:module` or title contains `[Module]`
- Provides immediate context

### Issue Body Format

```markdown
## Module: {module_name}

### Description
Implementation of the {module_name} module (added during orchestration).

### Acceptance Criteria
- [ ] {criteria_line_1}
- [ ] {criteria_line_2}
...

### Priority
{priority}

### Related
- Plan ID: {plan_id}
- Added during: Orchestration Phase
```

### Labels Applied on Creation

| Label | Purpose |
|-------|---------|
| `module` | Identifies this issue as a module |
| `priority:{level}` | Indicates priority (critical/high/normal/low) |
| `status:todo` | Initial status |

**Example label set**: `module, priority:normal, status:todo`

### Issue Creation Command

The script uses this gh command:

```bash
gh issue create \
  --title "[Module] {module_name}" \
  --body "{body}" \
  --label "module,priority:{priority},status:todo"
```

### Capturing Issue Number

After creation, the issue URL is returned:
```
https://github.com/owner/repo/issues/47
```

The issue number (`#47`) is extracted and stored in the module's `github_issue` field.

---

## 6.2 Issue Update Synchronization

When modules are modified, the linked GitHub Issue is updated to stay in sync.

### Triggering Updates

Issue updates occur when:
- Module name changes -> Issue title updated
- Acceptance criteria changes -> Issue body updated
- Priority changes -> Priority label updated
- Status changes -> Status label updated

### Name Change Sync

When module name changes:

**Command**: `/modify-module auth-core --name "Authentication Service"`

**Issue update**:
```bash
gh issue edit 42 --title "[Module] Authentication Service"
```

### Criteria Change Sync

When acceptance criteria changes:

**Command**: `/modify-module auth-core --criteria "New criteria here"`

**Issue update**: Issue body is regenerated with new criteria and updated:
```bash
gh issue edit 42 --body "{new_body}"
```

### Priority Change Sync

When priority changes:

**Command**: `/prioritize-module auth-core --priority critical`

**Issue update**:
```bash
gh issue edit 42 --remove-label "priority:normal" --add-label "priority:critical"
```

### Status Change Sync

Status labels are updated as module progresses:

| Module Status | Status Label |
|---------------|-------------|
| `pending` | `status:todo` |
| `assigned` | `status:todo` (or `status:assigned`) |
| `in-progress` | `status:in-progress` |
| `complete` | `status:done` |

### Assignment Sync (Human Developers)

When module assigned to human developer, issue is assigned:

```bash
gh issue edit 42 --assignee "username"
```

---

## 6.3 Issue Closure Protocols

GitHub Issues are closed when modules are removed or completed.

### Closure on Module Removal

When a pending module is removed via `/remove-module`:

1. Issue is closed
2. Comment added explaining closure
3. `wontfix` label may be added

**Closure command**:
```bash
gh issue close 47 -c "Module removed from plan"
```

### Closure on Module Completion

When a module is marked complete:

1. Issue is closed
2. PR is linked (if available)
3. `status:done` label added

**Completion closure**:
```bash
gh issue close 42 -c "Module completed. PR: #56"
```

### Linking PR to Issue

PRs should reference the issue for automatic linking:

**In PR description**:
```markdown
Closes #42

Implementation of Core Authentication module.
```

**Or using keywords**:
- `Closes #42`
- `Fixes #42`
- `Resolves #42`

When PR is merged, the issue is automatically closed by GitHub.

### Reopening Closed Issues

If a module is accidentally removed and needs to be restored:

```bash
gh issue reopen 47
```

---

## 6.4 Label Conventions

EOA orchestration uses a specific set of labels for module tracking.

### Required Labels

| Label | Purpose | Color (suggested) |
|-------|---------|-------------------|
| `module` | Identifies issue as a module | Blue (#0052CC) |

### Priority Labels

| Label | Meaning | Color (suggested) |
|-------|---------|-------------------|
| `priority:critical` | Must complete first | Red (#B60205) |
| `priority:high` | Should complete early | Orange (#D93F0B) |
| `priority:normal` | Standard priority | Yellow (#FBCA04) |
| `priority:low` | Nice to have | Green (#0E8A16) |

### Status Labels

| Label | Meaning | Color (suggested) |
|-------|---------|-------------------|
| `status:todo` | Not started | Gray (#EDEDED) |
| `status:assigned` | Assigned to agent | Light Blue (#C2E0FF) |
| `status:in-progress` | Work ongoing | Purple (#5319E7) |
| `status:done` | Completed | Green (#0E8A16) |

### Creating Labels in Repository

If labels don't exist, create them:

```bash
# Module identifier
gh label create "module" --color "0052CC" --description "EOA orchestration module"

# Priority labels
gh label create "priority:critical" --color "B60205" --description "Critical priority - must complete first"
gh label create "priority:high" --color "D93F0B" --description "High priority - complete early"
gh label create "priority:normal" --color "FBCA04" --description "Normal priority - standard"
gh label create "priority:low" --color "0E8A16" --description "Low priority - nice to have"

# Status labels
gh label create "status:todo" --color "EDEDED" --description "Not yet started"
gh label create "status:assigned" --color "C2E0FF" --description "Assigned to agent"
gh label create "status:in-progress" --color "5319E7" --description "Work in progress"
gh label create "status:done" --color "0E8A16" --description "Completed"
```

### Label Filtering

Useful GitHub filters for EOA modules:

| Filter | Purpose |
|--------|---------|
| `label:module` | All modules |
| `label:module label:priority:critical` | Critical modules |
| `label:module label:status:in-progress` | Active modules |
| `label:module -label:status:done` | Incomplete modules |
| `label:module is:open` | Open module issues |

---

## 6.5 Manual Sync When Automation Fails

Sometimes automatic sync fails. This section explains manual synchronization.

### Detecting Sync Failures

Sync may fail due to:
- `gh` CLI not authenticated
- Network issues
- GitHub API rate limits
- Label doesn't exist

**Symptoms**:
- Warning in command output
- `github_issue` field is `null`
- Issue doesn't reflect latest changes

### Manual Issue Creation

If issue creation failed:

```bash
# Create issue manually
gh issue create \
  --title "[Module] Module Name" \
  --body "$(cat <<'EOF'
## Module: Module Name

### Description
Implementation of the Module Name module.

### Acceptance Criteria
- [ ] Criteria here

### Priority
medium

### Related
- Plan ID: plan-xxx
- Added during: Orchestration Phase
EOF
)" \
  --label "module,priority:normal,status:todo"

# Note the issue number from output
# Update state file manually with issue number
```

### Manual Label Update

If priority label didn't update:

```bash
# Remove old label
gh issue edit 42 --remove-label "priority:normal"

# Add new label
gh issue edit 42 --add-label "priority:critical"
```

### Manual Body Update

If criteria change didn't sync:

```bash
# Update issue body
gh issue edit 42 --body "$(cat <<'EOF'
## Module: Auth Core

### Description
Implementation of the Auth Core module.

### Acceptance Criteria
- [ ] New criteria here

### Priority
high
EOF
)"
```

### Using the Sync Script

The skill includes a sync script for bulk synchronization:

```bash
# Sync all modules
python3 scripts/github_sync.py sync-all

# Sync specific module
python3 scripts/github_sync.py sync auth-core

# Verify sync status
python3 scripts/github_sync.py verify
```

---

## 6.6 Troubleshooting Sync Issues

Common sync issues and their solutions.

### Issue: "gh: command not found"

**Cause**: GitHub CLI not installed.

**Solution**:
```bash
# macOS
brew install gh

# Linux
sudo apt install gh

# Then authenticate
gh auth login
```

### Issue: "HTTP 401: Bad credentials"

**Cause**: GitHub CLI not authenticated or token expired.

**Solution**:
```bash
gh auth login
# Follow prompts to authenticate
```

### Issue: "Label does not exist"

**Cause**: Priority or status label not in repository.

**Solution**: Create the labels (see section 6.4) or create manually in GitHub UI.

### Issue: "Rate limit exceeded"

**Cause**: Too many API calls in short time.

**Solution**: Wait for rate limit reset (usually 1 hour) or use authenticated requests (higher limit).

### Issue: Issue number is null

**Cause**: Issue creation failed and wasn't captured.

**Solution**:
1. Check if issue exists by searching: `is:issue [Module] {name}`
2. If exists, manually update state file with issue number
3. If not exists, create manually

### Issue: Labels not updating

**Cause**: Label name mismatch or API error.

**Solution**:
1. Verify label exists in repository
2. Check label name matches exactly (case-sensitive)
3. Update manually if needed

### Issue: Body not updating

**Cause**: Markdown formatting issue or API error.

**Solution**:
1. Manually edit issue in GitHub UI
2. Or use `gh issue edit` with proper escaping

### Verification Command

Check if sync is working:

```bash
# List module issues
gh issue list --label "module"

# View specific issue
gh issue view 42

# Check issue labels
gh issue view 42 --json labels
```

---

## Sync State Diagram

```
Module Added
    │
    ├──► GitHub Issue Created
    │         │
    │         ├──► Labels Applied
    │         │
    │         └──► Issue Number Stored
    │
Module Modified
    │
    ├──► Name Change ──► Issue Title Updated
    │
    ├──► Criteria Change ──► Issue Body Updated
    │
    └──► Priority Change ──► Labels Updated

Module Removed
    │
    └──► Issue Closed with Comment

Module Completed
    │
    └──► Issue Closed, PR Linked
```

---

## Related Commands

| Command | GitHub Effect |
|---------|--------------|
| `/add-module` | Creates new issue |
| `/modify-module` | Updates issue |
| `/remove-module` | Closes issue |
| `/prioritize-module` | Updates priority label |
| `/assign-module` | Assigns issue (human devs) |
