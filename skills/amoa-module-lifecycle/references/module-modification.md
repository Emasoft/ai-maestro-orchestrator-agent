# Module Modification Reference

## Contents

- 2.1 What can be modified (name, criteria, priority)
- 2.2 Modification restrictions by status
- 2.3 Agent notification protocol
- 2.4 GitHub Issue synchronization
- 2.5 Complete modification examples

---

## 2.1 What Can Be Modified

Module modification allows changing three fields of an existing module: name, criteria, and priority.

### Modifiable Fields

| Field | Option | Description | Impact |
|-------|--------|-------------|--------|
| Name | `--name` | Display name of module | Issue title, reports |
| Criteria | `--criteria` | Acceptance criteria | Issue body, verification |
| Priority | `--priority` | Priority level | Labels, assignment order |

### When to Modify Each Field

**Name Changes**:
- Original name was unclear
- Scope of module changed
- Naming convention updated

**Criteria Changes**:
- Requirements clarified
- Scope expanded or reduced
- Acceptance tests refined

**Priority Changes**:
- Urgency changed (use `/prioritize-module` shortcut)
- Dependencies discovered
- Resource availability changed

### What Cannot Be Modified

| Field | Why Not Modifiable |
|-------|-------------------|
| Module ID | Would break all references |
| GitHub Issue | Created automatically, linked forever |
| Status | Managed by assignment/completion workflow |
| Assigned Agent | Use `/reassign-module` instead |

---

## 2.2 Modification Restrictions by Status

Not all modules can be modified. Restrictions depend on the module's current status.

### Status-Based Restrictions

| Status | Can Modify Name? | Can Modify Criteria? | Can Modify Priority? |
|--------|------------------|---------------------|---------------------|
| `pending` | Yes | Yes | Yes |
| `assigned` | Yes | Yes (with notification) | Yes (with notification) |
| `in-progress` | Yes | Yes (with notification) | Yes (with notification) |
| `complete` | No | No | No |

### Why Complete Modules Cannot Be Modified

Once a module is complete:
1. Work has been done according to original criteria
2. PR has been merged based on those criteria
3. Changing criteria would invalidate completed work
4. Historical accuracy must be maintained

**If requirements changed for a complete module**:
- Create a new module with updated requirements
- Reference the original module in the new module's description
- The new module represents a "phase 2" or "enhancement"

### Pending Modules: Full Flexibility

Pending modules have not been started, so all modifications are allowed:

```bash
# Change name
/modify-module auth-core --name "Authentication Service"

# Change criteria
/modify-module auth-core --criteria "New acceptance criteria"

# Change priority
/modify-module auth-core --priority critical

# Change multiple
/modify-module auth-core --name "Auth Service" --criteria "New criteria" --priority high
```

### In-Progress Modules: With Caution

When modifying an in-progress module (status `in-progress`):
1. Agent may have started work based on old specs
2. Changes may require rework
3. Agent MUST be notified
4. Consider the rework cost before modifying

---

## 2.3 Agent Notification Protocol

When a module with an assigned agent is modified, the agent must be notified via AI Maestro.

### Notification Trigger

Notifications are sent when:
- Module has `assigned_to` field set (not null)
- Agent type is `ai` (human developers see GitHub Issue update)
- Any field is modified

### Notification Message Format

**Subject**: `[UPDATE] Module: {module_name} - Spec Change`

**Body**:
```markdown
The specifications for your assigned module have been updated:

**Changes:**
- Criteria: {new_criteria}  # If criteria changed
- Priority: {new_priority}  # If priority changed
- Name: {new_name}          # If name changed

Please acknowledge this update and adjust your implementation accordingly.

If this significantly impacts your current work, report the impact immediately.
```

### Expected Agent Response

After receiving a modification notification, the agent should:

1. **Acknowledge receipt** - Confirm message received
2. **Assess impact** - Determine how changes affect current work
3. **Report impact** - If significant, report to orchestrator
4. **Adjust implementation** - Update approach based on new specs

### If Agent Does Not Respond

If agent does not acknowledge within reasonable time (15-30 minutes):
1. Send follow-up poll
2. If still no response, consider reassignment
3. Document unresponsiveness in GitHub Issue

### Human Developer Notification

Human developers are notified via GitHub Issue update only. The issue body is updated with new criteria, and labels are updated for priority changes.

---

## 2.4 GitHub Issue Synchronization

When a module is modified, the linked GitHub Issue is automatically updated.

### Automatic Updates

| Module Change | GitHub Issue Update |
|---------------|---------------------|
| Name change | Issue title updated |
| Criteria change | Issue body updated |
| Priority change | Priority label replaced |

### Issue Title Update

**Before**:
```
[Module] Auth Core
```

**After** (name changed to "Authentication Service"):
```
[Module] Authentication Service
```

### Issue Body Update

The acceptance criteria section in the issue body is replaced with the new criteria:

**Before**:
```markdown
### Acceptance Criteria
- [ ] Support basic username/password
```

**After**:
```markdown
### Acceptance Criteria
- [ ] Support JWT with 24h expiry
- [ ] Support refresh tokens
```

### Priority Label Update

Old priority label is removed and new one added:

**Before labels**: `module, priority:normal, status:in-progress`

**After** (changed to critical): `module, priority:critical, status:in-progress`

### If Sync Fails

If GitHub Issue update fails:
1. Warning displayed in command output
2. State file is still updated
3. Manual sync required

**Manual sync command**:
```bash
# Sync specific module
python3 scripts/github_sync.py sync auth-core

# Verify sync status
python3 scripts/github_sync.py verify
```

---

## 2.5 Complete Modification Examples

### Example 1: Update Criteria Only

**Scenario**: User wants to add JWT support requirement to existing auth module.

**Current State**:
```yaml
- id: "auth-core"
  name: "Core Authentication"
  acceptance_criteria: "Support basic login"
  priority: "medium"
```

**Command**:
```bash
/modify-module auth-core --criteria "Support JWT with 24h expiry and refresh tokens"
```

**Output**:
```
Modified module: auth-core
  Criteria updated
  Agent 'implementer-1' should be notified
```

**Updated State**:
```yaml
- id: "auth-core"
  name: "Core Authentication"
  acceptance_criteria: "Support JWT with 24h expiry and refresh tokens"
  priority: "medium"
```

### Example 2: Change Priority Only

**Scenario**: Auth module becomes blocking for other work.

**Command**:
```bash
/modify-module auth-core --priority critical
```

**Output**:
```
Modified module: auth-core
  Priority: critical
  Agent 'implementer-1' should be notified
```

**Alternative** (using shortcut):
```bash
/prioritize-module auth-core --priority critical
```

### Example 3: Rename Module

**Scenario**: "Auth Core" is unclear, should be "Authentication Service".

**Command**:
```bash
/modify-module auth-core --name "Authentication Service"
```

**Output**:
```
Modified module: auth-core
  Name: Authentication Service
```

**Note**: The module ID (`auth-core`) does NOT change. Only the display name changes.

### Example 4: Multiple Changes

**Scenario**: Complete requirements revision with priority escalation.

**Command**:
```bash
/modify-module password-reset --name "Password Recovery" --criteria "Support email and SMS recovery options with rate limiting" --priority high
```

**Output**:
```
Modified module: password-reset
  Name: Password Recovery
  Criteria updated
  Priority: high
```

### Example 5: Modify Pending Module (No Notification)

**Scenario**: Module not yet assigned, change freely.

**Current State**:
```yaml
- id: "oauth-google"
  name: "Google OAuth"
  status: "pending"
  assigned_to: null
```

**Command**:
```bash
/modify-module oauth-google --criteria "Support Google OAuth with automatic account linking"
```

**Output**:
```
Modified module: oauth-google
  Criteria updated
```

**Note**: No agent notification because no agent is assigned.

### Example 6: Attempt to Modify Complete Module

**Scenario**: Trying to change a finished module.

**Current State**:
```yaml
- id: "basic-auth"
  status: "complete"
```

**Command**:
```bash
/modify-module basic-auth --criteria "New requirements"
```

**Output**:
```
ERROR: Cannot modify completed module
```

**Solution**: Create a new module for additional requirements.

### Example 7: Module Not Found

**Scenario**: Wrong module ID used.

**Command**:
```bash
/modify-module auth-coree --criteria "..."
```

**Output**:
```
ERROR: Module 'auth-coree' not found
```

**Solution**: Use `/orchestration-status` to see correct module IDs.

---

## Best Practices for Modifications

| Practice | Rationale |
|----------|-----------|
| Modify early | Less rework if changed before implementation starts |
| Document reasons | Add comment to GitHub Issue explaining why changed |
| Notify verbally | For critical changes, follow up with poll |
| Review impact | Consider downstream effects before changing |
| Test after | Verify change reflected in status and issue |

---

## Related Commands

| Command | When to Use |
|---------|-------------|
| `/prioritize-module` | Shortcut for priority-only changes |
| `/orchestration-status` | View current module specs |
| `/reassign-module` | Change assigned agent |
| `/remove-module` | Cancel module instead of modifying |
