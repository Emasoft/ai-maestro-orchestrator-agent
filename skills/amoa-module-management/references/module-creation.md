# Module Creation Reference

## Contents

- 1.1 When to add modules during orchestration
- 1.2 Required fields for new modules (name, criteria)
- 1.3 Optional fields (priority level)
- 1.4 Automatic GitHub Issue creation
- 1.5 State file update after addition
- 1.6 Complete examples with all variations

---

## 1.1 When to Add Modules During Orchestration

Module addition is a feature of EOA orchestration that allows dynamic scope expansion. This section explains when adding modules is appropriate.

### Appropriate Scenarios for Adding Modules

| Scenario | Description | Example |
|----------|-------------|---------|
| New feature request | User requests feature not in original plan | "Add password reset functionality" |
| Scope expansion | User wants to expand existing feature | "Also support SMS for 2FA" |
| Dependency discovery | During implementation, a new module is needed | "We need a notification service" |
| Risk mitigation | Adding a module to address discovered risk | "Add input validation module" |

### When NOT to Add Modules

| Situation | Correct Action |
|-----------|----------------|
| Sub-task of existing module | Add to acceptance criteria of existing module |
| Bug fix | Create bug issue, not module |
| Documentation | Part of module's acceptance criteria |
| Refactoring | Internal work, not a module |

### Dynamic Flexibility Concept

EOA orchestration supports "dynamic flexibility" which means the plan can evolve during execution. When a module is added:

1. The total module count increases
2. The stop hook now includes this module
3. Orchestration cannot complete until this module is done
4. The new module enters the pending queue

**Before adding a module**:
```
Modules: [A: done, B: in-progress]
Total: 2
Remaining: 1
```

**After adding module C**:
```
Modules: [A: done, B: in-progress, C: pending]
Total: 3
Remaining: 2
```

---

## 1.2 Required Fields for New Modules

Every new module MUST have two required fields: name and acceptance criteria.

### Module Name

The module name is the human-readable identifier for the module. It appears in:
- Status reports
- GitHub Issue title
- Assignment messages
- Progress tracking

**Name Requirements**:
| Requirement | Valid Example | Invalid Example |
|-------------|---------------|-----------------|
| Descriptive | "User Authentication" | "Module 1" |
| Concise | "Password Reset" | "The functionality to reset passwords" |
| Noun-based | "OAuth Integration" | "Integrate OAuth" |

**How Names Become IDs**:

The module name is automatically converted to a kebab-case ID:
- "User Authentication" becomes `user-authentication`
- "OAuth 2.0 Integration" becomes `oauth-20-integration`
- "Two-Factor Auth" becomes `two-factor-auth`

The ID is used for:
- Command arguments (`/modify-module user-authentication`)
- State file entries
- Internal references

### Acceptance Criteria

Acceptance criteria define what "done" means for this module. The criteria is used to:
- Verify implementation completeness
- Guide agent implementation
- Populate GitHub Issue body

**Criteria Requirements**:
| Requirement | Good Example | Bad Example |
|-------------|--------------|-------------|
| Measurable | "Support JWT with 24h expiry" | "Handle authentication" |
| Specific | "Email link expires in 1 hour" | "Send reset email" |
| Testable | "Return 401 for invalid tokens" | "Reject bad tokens" |

**Criteria Format**:

Single criteria (simple module):
```
--criteria "Users can reset password via email link"
```

Multiple criteria (complex module):
```
--criteria "1. Support TOTP via authenticator apps. 2. Support SMS as backup. 3. Require 2FA for admin accounts"
```

---

## 1.3 Optional Fields

### Priority Level

Priority determines the order in which modules should be assigned and completed.

| Priority | Meaning | When to Use |
|----------|---------|-------------|
| `critical` | Must complete first | Blocking other modules |
| `high` | Should complete early | Important but not blocking |
| `medium` | Standard priority | Most modules |
| `low` | Nice to have | Can be delayed |

**Default**: If not specified, priority is `medium`.

**Priority Effects**:

| Effect | Description |
|--------|-------------|
| Assignment order | Critical modules assigned first |
| Stop hook | All priorities must complete |
| GitHub labels | `priority:critical`, `priority:high`, etc. |
| Agent attention | Agents told module priority |

**Command Examples**:
```bash
# Critical priority
/add-module "Auth Core" --criteria "..." --priority critical

# High priority
/add-module "Auth Core" --criteria "..." --priority high

# Medium priority (explicit)
/add-module "Auth Core" --criteria "..." --priority medium

# Low priority
/add-module "Auth Core" --criteria "..." --priority low

# Default (medium)
/add-module "Auth Core" --criteria "..."
```

---

## 1.4 Automatic GitHub Issue Creation

When a module is added, a GitHub Issue is automatically created using the `gh` CLI.

### Issue Creation Process

1. Module name becomes issue title: `[Module] {module_name}`
2. Acceptance criteria becomes issue body
3. Labels applied automatically
4. Issue number captured and stored

### Issue Format

**Title**: `[Module] {module_name}`

**Body**:
```markdown
## Module: {module_name}

### Description
Implementation of the {module_name} module (added during orchestration).

### Acceptance Criteria
- [ ] {criteria}

### Priority
{priority}

### Related
- Plan ID: {plan_id}
- Added during: Orchestration Phase
```

### Labels Applied

| Label | Purpose |
|-------|---------|
| `module` | Identifies as module (not bug, not feature request) |
| `priority:{level}` | Priority level (critical, high, normal, low) |
| `status:todo` | Initial status |

### If Issue Creation Fails

If the `gh` CLI fails to create the issue:
1. Module is still added to state file
2. Warning is displayed
3. `github_issue` field is `null`
4. Manual issue creation is required

**Manual Sync**:
```bash
python3 scripts/github_sync.py sync module-id
```

---

## 1.5 State File Update After Addition

When a module is added, the state file at `design/state/exec-phase.md` is updated.

### New Module Entry Structure

```yaml
modules_status:
  # ... existing modules ...
  - id: "password-reset"           # Auto-generated from name
    name: "Password Reset"         # Original name
    status: "pending"              # Always starts as pending
    assigned_to: null              # Not yet assigned
    github_issue: "#47"            # Created issue number
    pr: null                       # No PR yet
    verification_loops: 0          # No verification yet
    acceptance_criteria: "Users can reset password via email link"
    priority: "high"               # Specified or default
```

### Module Count Update

The `modules_total` counter is automatically incremented:

**Before**:
```yaml
modules_total: 5
```

**After**:
```yaml
modules_total: 6
```

### Stop Hook Implications

The stop hook checks all modules before allowing orchestration to complete. Adding a module means:
- One more module must reach `complete` status
- Exit is blocked until all modules done

---

## 1.6 Complete Examples with All Variations

### Example 1: Basic Module Addition

**Scenario**: User requests password reset functionality.

**Command**:
```bash
/add-module "Password Reset" --criteria "Users can reset password via email link"
```

**Output**:
```
Added module: password-reset
  Name: Password Reset
  Criteria: Users can reset password via email link
  Priority: medium
  GitHub Issue: #47
```

### Example 2: Critical Module Addition

**Scenario**: Security audit requires immediate 2FA implementation.

**Command**:
```bash
/add-module "Two-Factor Authentication" --criteria "Support TOTP authenticators and SMS backup" --priority critical
```

**Output**:
```
Added module: two-factor-authentication
  Name: Two-Factor Authentication
  Criteria: Support TOTP authenticators and SMS backup
  Priority: critical
  GitHub Issue: #48
```

### Example 3: Low Priority Enhancement

**Scenario**: User wants "remember me" feature but it is not urgent.

**Command**:
```bash
/add-module "Remember Me" --criteria "Persist login session for 30 days with checkbox option" --priority low
```

**Output**:
```
Added module: remember-me
  Name: Remember Me
  Criteria: Persist login session for 30 days with checkbox option
  Priority: low
  GitHub Issue: #49
```

### Example 4: Complex Criteria

**Scenario**: Module with multiple acceptance criteria.

**Command**:
```bash
/add-module "OAuth Integration" --criteria "1. Support Google OAuth. 2. Support GitHub OAuth. 3. Map OAuth accounts to existing users by email" --priority high
```

**Output**:
```
Added module: oauth-integration
  Name: OAuth Integration
  Criteria: 1. Support Google OAuth. 2. Support GitHub OAuth. 3. Map OAuth accounts to existing users by email
  Priority: high
  GitHub Issue: #50
```

### Example 5: Handling Duplicate Module

**Scenario**: Attempting to add a module that already exists.

**Command**:
```bash
/add-module "Password Reset" --criteria "Different criteria"
```

**Output**:
```
ERROR: Module 'password-reset' already exists
```

**Solution**: Use `/modify-module password-reset --criteria "New criteria"` instead.

---

## Next Steps After Adding a Module

After successfully adding a module:

1. **View updated status**: `/orchestration-status`
2. **Assign to agent**: `/assign-module {module-id} {agent-id}`
3. **Execute Instruction Verification Protocol**
4. **Monitor progress**: `/check-agents`

---

## Related Commands

| Command | When to Use |
|---------|-------------|
| `/modify-module` | Change criteria after adding |
| `/assign-module` | Assign the new module |
| `/prioritize-module` | Change priority later |
| `/remove-module` | Cancel before assignment |
