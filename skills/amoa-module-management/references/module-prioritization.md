# Module Prioritization Reference

## Contents

- 4.1 Priority levels explained (critical, high, medium, low)
- 4.2 Effects on assignment queue
- 4.3 GitHub Issue label updates
- 4.4 When to escalate vs downgrade
- 4.5 Complete priority change examples

---

## 4.1 Priority Levels Explained

EOA orchestration uses four priority levels to indicate the urgency and importance of modules.

### Priority Level Definitions

| Level | Meaning | Typical Use Case |
|-------|---------|-----------------|
| `critical` | Must complete first, blocking other work | Security fixes, core infrastructure |
| `high` | Should complete early, important to success | Key features, user-facing functionality |
| `medium` | Standard priority, part of planned scope | Most features and modules |
| `low` | Nice to have, can be delayed if needed | Enhancements, polish, non-essential |

### Detailed Level Descriptions

**Critical Priority**:
- Blocks other modules from starting or completing
- Must be assigned immediately to best available agent
- May require interrupting other work
- Failure to complete impacts entire project
- Examples: Authentication core, database schema, security patches

**High Priority**:
- Important but not blocking
- Should be assigned early in orchestration
- Completion is expected for project success
- Examples: Main user features, API endpoints, core UI

**Medium Priority** (Default):
- Standard level of importance
- Assigned in normal order
- Expected to complete within project scope
- Examples: Secondary features, integrations, documentation

**Low Priority**:
- Optional or enhancement
- Can be deferred if resources constrained
- Removal would not significantly impact project
- Examples: Nice-to-have features, optimizations, polish

### Priority Comparison Table

| Aspect | Critical | High | Medium | Low |
|--------|----------|------|--------|-----|
| Assignment order | First | Early | Normal | Last |
| Can be deferred? | No | Rarely | Sometimes | Often |
| Blocks others? | Often | Sometimes | Rarely | Never |
| Removal impact | Severe | Significant | Moderate | Minimal |

---

## 4.2 Effects on Assignment Queue

Priority affects how modules are assigned to agents during orchestration.

### Assignment Order

The orchestrator assigns modules in priority order:

1. All `critical` modules first
2. Then `high` modules
3. Then `medium` modules
4. Finally `low` modules

**Within same priority**: Order determined by other factors (dependencies, agent availability).

### Example Assignment Sequence

Given modules:
- Auth Core (critical)
- OAuth Google (high)
- Remember Me (medium)
- UI Polish (low)
- Database Schema (critical)

Assignment order:
1. Auth Core (critical)
2. Database Schema (critical)
3. OAuth Google (high)
4. Remember Me (medium)
5. UI Polish (low)

### Dynamic Priority Changes

When priority is changed during orchestration:

**Escalation** (medium -> critical):
- Module moves up in queue
- May be assigned next if agents available
- Stop hook continues to include it

**Downgrade** (high -> low):
- Module moves down in queue
- Other modules may be assigned first
- Still required for completion (unless removed)

### Stop Hook Behavior

All priority levels are required for orchestration completion. The stop hook blocks until:
- All critical modules complete
- All high modules complete
- All medium modules complete
- All low modules complete

Priority does NOT affect whether a module is required, only WHEN it is assigned.

---

## 4.3 GitHub Issue Label Updates

When priority changes, the linked GitHub Issue labels are updated automatically.

### Priority Labels

| Priority | GitHub Label |
|----------|-------------|
| `critical` | `priority:critical` |
| `high` | `priority:high` |
| `medium` | `priority:normal` |
| `low` | `priority:low` |

### Label Update Process

When priority changes:
1. Old priority label is removed
2. New priority label is added
3. Other labels remain unchanged

**Before**:
```
Labels: module, priority:normal, status:in-progress
```

**After** (changed to critical):
```
Labels: module, priority:critical, status:in-progress
```

### Label Update Command

The script uses `gh issue edit` to update labels:

```bash
# Remove old label
gh issue edit 42 --remove-label priority:normal

# Add new label
gh issue edit 42 --add-label priority:critical
```

### If Labels Don't Exist

If the priority label doesn't exist in the repository:
- Warning may be displayed
- Label is created automatically (if repo settings allow)
- Or label update silently skipped

**Creating labels manually**:
```bash
gh label create priority:critical --color "B60205" --description "Critical priority module"
gh label create priority:high --color "D93F0B" --description "High priority module"
gh label create priority:normal --color "FBCA04" --description "Normal priority module"
gh label create priority:low --color "0E8A16" --description "Low priority module"
```

---

## 4.4 When to Escalate vs Downgrade

This section provides guidance on when to change priority levels.

### Reasons to Escalate Priority

| Reason | From | To | Justification |
|--------|------|-----|---------------|
| Discovered dependency | medium | critical | Other modules blocked |
| Security concern | any | critical | Security always critical |
| User demand | low | high | User priority changed |
| Deadline pressure | medium | high | Time constraints |
| Resource availability | medium | high | Agent has capacity now |

### Reasons to Downgrade Priority

| Reason | From | To | Justification |
|--------|------|-----|---------------|
| Scope reduction | high | medium | Less important than thought |
| Resource constraints | high | low | Cannot staff it now |
| Dependency removed | critical | high | No longer blocking |
| User feedback | high | low | Users don't want it |
| Timeline extension | high | medium | More time available |

### Decision Questions

Before escalating, ask:
1. Does this genuinely block other work?
2. Will escalation cause other work to be delayed?
3. Is there a less disruptive alternative?

Before downgrading, ask:
1. Will this cause the module to not complete?
2. Are there dependencies on this module?
3. Will the user accept this change?

### Priority Change Communication

When changing priority:
1. Document the reason in GitHub Issue
2. Notify assigned agent (if any)
3. Inform user if significant change
4. Update any external stakeholders

---

## 4.5 Complete Priority Change Examples

### Example 1: Escalate to Critical

**Scenario**: Auth module discovered to be blocking all other modules.

**Current State**:
```yaml
- id: "auth-core"
  priority: "medium"
  status: "pending"
```

**Command**:
```bash
/prioritize-module auth-core --priority critical
```

**Output**:
```
Modified module: auth-core
  Priority: critical
```

**Updated State**:
```yaml
- id: "auth-core"
  priority: "critical"
  status: "pending"
```

**GitHub Issue**: Label changed from `priority:normal` to `priority:critical`

### Example 2: Downgrade to Low

**Scenario**: "Remember me" feature is nice-to-have, not essential.

**Command**:
```bash
/prioritize-module remember-me --priority low
```

**Output**:
```
Modified module: remember-me
  Priority: low
```

### Example 3: Escalate with Agent Notification

**Scenario**: In-progress module needs to be escalated. Agent must be notified.

**Current State**:
```yaml
- id: "oauth-google"
  priority: "medium"
  status: "in-progress"
  assigned_to: "implementer-1"
```

**Command**:
```bash
/prioritize-module oauth-google --priority critical
```

**Output**:
```
Modified module: oauth-google
  Priority: critical
  Agent 'implementer-1' should be notified
```

**Agent Notification**:
```markdown
Subject: [UPDATE] Module: OAuth Google - Spec Change

The specifications for your assigned module have been updated:

**Changes:**
- Priority: critical

Please acknowledge this update and adjust your implementation accordingly.
```

### Example 4: Using /modify-module Instead

The `/prioritize-module` command is a shortcut. The same result can be achieved with `/modify-module`:

```bash
# Using prioritize-module
/prioritize-module auth-core --priority critical

# Equivalent using modify-module
/modify-module auth-core --priority critical
```

Both commands:
- Update the state file
- Update GitHub Issue labels
- Notify assigned agent (if any)

### Example 5: Multiple Priority Changes

**Scenario**: Reorganizing priorities after user feedback.

**Commands**:
```bash
# Escalate security-related
/prioritize-module auth-core --priority critical
/prioritize-module password-reset --priority high

# Downgrade nice-to-haves
/prioritize-module remember-me --priority low
/prioritize-module ui-animations --priority low
```

### Example 6: Error - Module Not Found

**Command**:
```bash
/prioritize-module wrong-id --priority critical
```

**Output**:
```
ERROR: Module 'wrong-id' not found
```

**Solution**: Check correct module ID with `/orchestration-status`.

### Example 7: Error - Cannot Modify Complete

**Command**:
```bash
/prioritize-module basic-auth --priority critical
```

**Output** (if module is complete):
```
ERROR: Cannot modify completed module
```

**Solution**: Complete modules cannot have priority changed. Historical record is preserved.

---

## Priority Labels Visual Reference

For easy identification in GitHub:

| Priority | Suggested Color | Hex Code |
|----------|-----------------|----------|
| Critical | Red | `#B60205` |
| High | Orange | `#D93F0B` |
| Medium | Yellow | `#FBCA04` |
| Low | Green | `#0E8A16` |

---

## Best Practices

| Practice | Rationale |
|----------|-----------|
| Start most modules at medium | Avoid priority inflation |
| Reserve critical for genuine blocks | Critical loses meaning if overused |
| Document priority changes | Maintain transparency |
| Consider ripple effects | Escalation may delay other work |
| Review priorities regularly | Priorities change as project evolves |

---

## Related Commands

| Command | When to Use |
|---------|-------------|
| `/modify-module` | Full modification including priority |
| `/orchestration-status` | View all module priorities |
| `/add-module` | Set priority when adding |
| `/check-agents` | See what agents are working on |
