# Operation: Change Module Priority


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Command Syntax](#command-syntax)
- [Priority Levels](#priority-levels)
- [Steps](#steps)
- [Effects on Assignment Queue](#effects-on-assignment-queue)
- [Agent Notification](#agent-notification)
- [Priority Change: <module_id>](#priority-change-module_id)
  - [Impact](#impact)
  - [Action Required](#action-required)
- [Output](#output)
- [Success Criteria](#success-criteria)
- [When to Escalate vs. Downgrade](#when-to-escalate-vs-downgrade)
  - [Escalate (increase priority) when:](#escalate-increase-priority-when)
  - [Downgrade (decrease priority) when:](#downgrade-decrease-priority-when)
- [Error Handling](#error-handling)
- [GitHub Label Conventions](#github-label-conventions)
- [Important Rules](#important-rules)
- [Priority Change Audit](#priority-change-audit)
- [Next Operations](#next-operations)

## Metadata

| Field | Value |
|-------|-------|
| Operation ID | `op-change-module-priority` |
| Procedure | `proc-update-tasks` |
| Workflow Step | Step 16 |
| Trigger | Urgency of module changes |
| Actor | Orchestrator (EOA) |
| Command | `/prioritize-module` |

---

## Purpose

Change the priority level of a module to reflect changed urgency. This affects assignment queue ordering and GitHub Issue labels.

---

## Prerequisites

- Module exists in state file
- Module is not in `complete` status
- GitHub CLI (gh) authenticated

---

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `module_id` | Yes | ID of module to prioritize |
| `priority` | Yes | New priority: critical, high, medium, low |

---

## Command Syntax

```bash
/prioritize-module <MODULE_ID> --priority <LEVEL>
```

**Examples**:

```bash
# Escalate to critical
/prioritize-module auth-core --priority critical

# Downgrade to low
/prioritize-module nice-to-have-feature --priority low
```

---

## Priority Levels

| Level | Meaning | Assignment Queue | Response Time |
|-------|---------|------------------|---------------|
| `critical` | Blocking release/other work | Immediate attention | < 1 hour |
| `high` | Important for milestone | Next available agent | < 4 hours |
| `medium` | Standard priority | Normal queue order | < 24 hours |
| `low` | Nice to have | After higher priority | Best effort |

---

## Steps

1. **Validate module exists**:
   - Check state file for module_id
   - Verify not in `complete` status

2. **Validate priority level**:
   - Must be: critical, high, medium, low

3. **Update state file**:
   ```yaml
   modules_status:
     - id: "<module_id>"
       priority: "<NEW_PRIORITY>"
   ```

4. **Update GitHub Issue labels**:
   ```bash
   # Remove old priority label
   gh issue edit <issue_number> --remove-label "priority-<OLD>"

   # Add new priority label
   gh issue edit <issue_number> --add-label "priority-<NEW>"
   ```

5. **Notify assigned agent** (if applicable and escalating):
   - Only notify when escalating (medium->high, high->critical)
   - Include reason for urgency change

6. **Log the change** in orchestration log

---

## Effects on Assignment Queue

Priority affects which modules get assigned first:

```
Assignment Order:
1. critical (status:pending)
2. high (status:pending)
3. medium (status:pending)
4. low (status:pending)
```

**Example queue before priority change:**
```
1. feature-a (medium)
2. feature-b (medium)
3. feature-c (low)
```

**After `/prioritize-module feature-c --priority critical`:**
```
1. feature-c (critical)  ← Moved to top
2. feature-a (medium)
3. feature-b (medium)
```

---

## Agent Notification

Notify when escalating assigned/in-progress modules:

```markdown
## Priority Change: <module_id>

Your assigned module has been escalated to **<NEW_PRIORITY>**.

**Previous Priority**: <OLD_PRIORITY>
**New Priority**: <NEW_PRIORITY>

### Impact
<reason_for_escalation>

### Action Required
- Please prioritize this work
- Update if any blockers prevent progress
- Report completion as soon as possible
```

---

## Output

| Output | Format | Description |
|--------|--------|-------------|
| State file updated | YAML change | Priority field |
| GitHub labels updated | Label change | priority-X label |
| Agent notified | AI Maestro message | If escalating in-progress |
| Console confirmation | Text | "Module '<id>' priority: <old> -> <new>" |

---

## Success Criteria

- State file shows new priority
- GitHub Issue has correct priority label
- Old priority label removed
- Agent notified if escalating active work

---

## When to Escalate vs. Downgrade

### Escalate (increase priority) when:
- Blocking other modules
- User urgently needs the feature
- External deadline discovered
- Security issue identified
- Dependencies now available

### Downgrade (decrease priority) when:
- Feature less important than thought
- User feedback suggests deferral
- Resources needed elsewhere
- Scope changed to reduce need
- Dependent features delayed

---

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Module not found | Wrong ID | Use `/orchestration-status` |
| Invalid priority | Typo | Use: critical, high, medium, low |
| Label update fails | GitHub permissions | Manual label change |
| Complete module | Cannot change | No action needed |

---

## GitHub Label Conventions

| Priority | Label |
|----------|-------|
| critical | `priority-critical` |
| high | `priority-high` |
| medium | `priority-medium` |
| low | `priority-low` |

**Note**: Only one priority label should exist at a time.

---

## Important Rules

1. **One priority label** - Remove old before adding new
2. **Notify on escalation** - Don't surprise agents with urgency
3. **Document reason** - Log why priority changed
4. **Complete modules unchanged** - Priority is moot after completion

---

## Priority Change Audit

Log each change:

```yaml
priority_log:
  - module_id: "auth-core"
    changed_at: "2025-02-05T15:30:00Z"
    changed_by: "orchestrator"
    from: "medium"
    to: "critical"
    reason: "Security vulnerability discovered requiring immediate auth hardening"
```

---

## Next Operations

After priority change:
- If critical: Consider reassigning to faster agent
- If downgraded: Update stakeholders
- View queue: `/orchestration-status`
