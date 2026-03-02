# Module Management Troubleshooting Reference

## Contents

- 7.1 State file corruption recovery
- 7.2 GitHub sync failure recovery
- 7.3 Agent notification failures
- 7.4 Module ID conflicts
- 7.5 Force removal scenarios

---

## 7.1 State File Corruption Recovery

The state file at `design/state/exec-phase.md` can become corrupted. This section explains recovery procedures.

### Detecting Corruption

**Symptoms**:
- Commands return "Could not parse orchestration state file"
- YAML parsing errors
- Missing or malformed fields
- Inconsistent module counts

**Validation check**:
```bash
# Check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('design/state/exec-phase.md').read())"
```

### Common Corruption Causes

| Cause | Prevention |
|-------|------------|
| Concurrent edits | Don't run multiple module commands simultaneously |
| Interrupted write | Don't interrupt commands mid-execution |
| Manual editing | Don't manually edit state file |
| Disk full | Ensure adequate disk space |

### Recovery from Git

If state file is tracked in git:

```bash
# Check git status
git status design/state/exec-phase.md

# Restore from last commit
git checkout -- design/state/exec-phase.md

# Or restore from specific commit
git checkout <commit-hash> -- design/state/exec-phase.md
```

### Recovery from Backup

If backups exist:

```bash
# Find backup files
ls -la .claude/*.bak

# Restore from backup
cp design/state/exec-phase.md.bak design/state/exec-phase.md
```

### Manual Reconstruction

If no backup available, reconstruct from GitHub:

1. **List all module issues**:
   ```bash
   gh issue list --label "module" --json number,title,labels,state
   ```

2. **Get issue details**:
   ```bash
   gh issue view 42 --json body,assignees,labels
   ```

3. **Rebuild state file** with correct structure

### Minimal Valid State File

Template for reconstruction:

```yaml
---
phase: "orchestration"
plan_id: "plan-xxx"
modules_total: 2
modules_complete: 0
registered_agents:
  ai_agents: []
  human_developers: []
modules_status:
  - id: "module-one"
    name: "Module One"
    status: "pending"
    assigned_to: null
    github_issue: "#42"
    pr: null
    verification_loops: 0
    acceptance_criteria: "Criteria here"
    priority: "medium"
active_assignments: []
---

# Orchestration State

Reconstructed state file.
```

---

## 7.2 GitHub Sync Failure Recovery

When GitHub synchronization fails, manual intervention is required.

### Diagnosing Sync Failures

**Check gh CLI status**:
```bash
# Verify authentication
gh auth status

# Test API access
gh api user
```

**Check network**:
```bash
# Test GitHub connectivity
curl -I https://github.com
```

### Issue Creation Failed

**Problem**: Module added but no GitHub Issue created.

**Solution**:
```bash
# Create issue manually
gh issue create \
  --title "[Module] {module_name}" \
  --body "{body}" \
  --label "module,priority:{priority},status:todo"

# Get issue number from output
# Update state file:
# Change github_issue: null to github_issue: "#XX"
```

### Issue Update Failed

**Problem**: Module modified but Issue not updated.

**Solution**:
```bash
# Update title
gh issue edit {number} --title "[Module] {new_name}"

# Update body
gh issue edit {number} --body "{new_body}"

# Update labels
gh issue edit {number} --remove-label "priority:{old}" --add-label "priority:{new}"
```

### Issue Closure Failed

**Problem**: Module removed but Issue still open.

**Solution**:
```bash
gh issue close {number} -c "Module removed from plan"
```

### Bulk Sync Recovery

Use the sync script to recover multiple issues:

```bash
# Verify all modules have issues
python3 scripts/github_sync.py verify

# Sync modules missing issues
python3 scripts/github_sync.py sync-all

# Sync specific module
python3 scripts/github_sync.py sync module-id
```

---

## 7.3 Agent Notification Failures

AI Maestro notifications may fail. This section covers recovery.

### Diagnosing Notification Failures

**Check AI Maestro is running**: Use the `agent-messaging` skill to perform a health check.

**Check message was sent**: Use the `agent-messaging` skill to list recently sent messages for your session.

### AI Maestro Not Running

**Problem**: AI Maestro service is down.

**Solution**:
1. Start AI Maestro service
2. Verify it is running using the `agent-messaging` skill health check

### Agent Session Not Found

**Problem**: Agent session name incorrect or agent not registered.

**Solution**:
1. Verify agent's session name in registered_agents
2. Verify agent is running
3. Re-register agent if needed

### Manual Notification

If automated notification failed, send manually:

Send a notification manually using the `agent-messaging` skill:
- **Recipient**: the agent session name
- **Subject**: "[UPDATE] Module: {name} - Spec Change"
- **Content**: "The specifications for your assigned module have been updated..."
- **Type**: `notification`
- **Priority**: `high`

**Verify**: confirm message delivery.

### Direct Agent Communication

If AI Maestro is down and cannot be restored:

1. **For AI agents**: Cannot directly communicate; wait for AI Maestro
2. **For human developers**: Contact via GitHub Issue comment or email
3. **Document the failure**: Note in GitHub Issue that notification failed

---

## 7.4 Module ID Conflicts

Module IDs are generated from names and must be unique.

### Detecting ID Conflicts

**Problem**: Attempting to add module with name that generates existing ID.

**Error**: `ERROR: Module 'module-id' already exists`

### How IDs Are Generated

Name to ID conversion:
1. Convert to lowercase
2. Replace non-alphanumeric with hyphens
3. Trim leading/trailing hyphens

**Examples**:
| Name | Generated ID |
|------|-------------|
| "Core Authentication" | `core-authentication` |
| "OAuth 2.0" | `oauth-20` |
| "Two-Factor Auth" | `two-factor-auth` |
| "UI/UX Design" | `ui-ux-design` |

### ID Collision Scenarios

| Name 1 | Name 2 | Same ID |
|--------|--------|---------|
| "Auth Core" | "AUTH CORE" | `auth-core` |
| "OAuth 2.0" | "OAuth-2.0" | `oauth-20` |
| "User Login" | "user_login" | `user-login` |

### Resolving ID Conflicts

**Option 1**: Use more specific name
```bash
# Instead of
/add-module "Auth" --criteria "..."

# Use
/add-module "OAuth2 Auth" --criteria "..."
```

**Option 2**: Modify existing module
```bash
# If duplicate is update to existing
/modify-module auth-core --criteria "Updated criteria"
```

**Option 3**: Remove existing first (if pending)
```bash
# Remove old, add new
/remove-module auth-core
/add-module "Auth Core v2" --criteria "..."
```

### Checking Existing IDs

View all module IDs before adding:
```bash
/orchestration-status
# Or
python3 scripts/module_operations.py list
```

---

## 7.5 Force Removal Scenarios

The `--force` flag bypasses certain safety checks. Use with caution.

### What --force Does

| Check | Normal | With --force |
|-------|--------|--------------|
| Confirmation prompt | Required | Skipped |
| Agent assignment check | Blocked if assigned | Proceeds anyway |

### What --force Does NOT Bypass

| Check | Behavior |
|-------|----------|
| Status is in-progress | Still blocked |
| Status is complete | Still blocked |
| Module existence | Must exist |

### When to Use --force

**Appropriate scenarios**:
- Module assigned but agent hasn't started
- Quick cleanup during testing
- Agent confirmed they haven't started
- Emergency scope reduction

**Inappropriate scenarios**:
- Agent is actively working
- You don't know if agent started
- Trying to remove in-progress module
- Avoiding proper communication

### Force Removal Process

```bash
# Standard removal (will prompt or error if assigned)
/remove-module oauth-facebook

# Force removal (no prompt, ignores assignment)
/remove-module oauth-facebook --force
```

### Force Removal with Agent Assigned

When force-removing an assigned module:

1. **Agent NOT notified automatically** - Manual notification required
2. **Assignment orphaned** - Clean up may be needed
3. **Agent may continue working** - Lost effort

**Recovery steps**:
```bash
# 1. Force remove
/remove-module oauth-facebook --force

# 2. Manually notify agent using the agent-messaging skill:
# Recipient: the agent session name
# Subject: "[STOP] Module Removed: oauth-facebook"
# Content: "The module oauth-facebook has been removed. Stop any work immediately."
# Type: notification, Priority: high
```

### Force Removal Audit Trail

When using --force, document:
- Why force was needed
- What state was before
- Whether agent was notified manually
- GitHub Issue status

**In GitHub Issue** (before closing):
```bash
gh issue comment 45 --body "Module force-removed. Agent was notified manually. Reason: Feature cancelled by product owner."
```

---

## General Troubleshooting Checklist

When encountering any module management issue:

### 1. Check Prerequisites

- [ ] In orchestration phase (state file exists)
- [ ] gh CLI authenticated
- [ ] AI Maestro running (for notifications)
- [ ] Correct module ID (check with /orchestration-status)

### 2. Check Error Message

- [ ] Read full error message
- [ ] Identify which validation failed
- [ ] Check suggested solution in error

### 3. Verify State

- [ ] State file is valid YAML
- [ ] Module exists in state
- [ ] Status allows operation
- [ ] GitHub Issue exists and is linked

### 4. Check External Systems

- [ ] GitHub accessible
- [ ] AI Maestro running
- [ ] Agent sessions active
- [ ] Network connectivity

### 5. Recovery Options

- [ ] Git restore if state corrupted
- [ ] Manual GitHub operations if sync failed
- [ ] Manual notifications if AI Maestro down
- [ ] Force operations as last resort

---

## Error Reference Table

| Error | Cause | Solution |
|-------|-------|----------|
| "Not in Orchestration Phase" | State file missing | Run `/start-orchestration` |
| "Could not parse state file" | YAML syntax error | Recover from git/backup |
| "Module not found" | Wrong ID | Check `/orchestration-status` |
| "Cannot modify completed" | Module is done | Create new module instead |
| "Cannot remove in-progress" | Work ongoing | Modify scope instead |
| "Agent not registered" | Unknown agent | Run `/register-agent` |
| "Already assigned" | Module has agent | Use `/reassign-module` |
| "gh: command not found" | CLI not installed | Install and auth gh |
| "HTTP 401" | Not authenticated | Run `gh auth login` |

---

## Related Commands

| Command | Troubleshooting Use |
|---------|---------------------|
| `/orchestration-status` | View current state |
| `/check-agents` | Verify agent status |
| `gh auth status` | Check GitHub auth |
| `gh issue list` | Verify issues exist |
