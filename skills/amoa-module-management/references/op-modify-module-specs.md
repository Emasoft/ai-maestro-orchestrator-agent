# Operation: Modify Module Specifications


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Command Syntax](#command-syntax)
- [Modification Restrictions by Status](#modification-restrictions-by-status)
- [Steps](#steps)
- [Agent Notification Template](#agent-notification-template)
- [Module Modified: <module_id>](#module-modified-module_id)
  - [Changes](#changes)
  - [Updated Specifications](#updated-specifications)
  - [Action Required](#action-required)
- [GitHub Issue Update](#github-issue-update)
- [Output](#output)
- [Success Criteria](#success-criteria)
- [Error Handling](#error-handling)
- [Important Rules](#important-rules)
- [Modification Audit](#modification-audit)
- [Next Operations](#next-operations)

## Metadata

| Field | Value |
|-------|-------|
| Operation ID | `op-modify-module-specs` |
| Procedure | `proc-update-tasks` |
| Workflow Step | Step 16 |
| Trigger | Requirements change or need clarification |
| Actor | Orchestrator (EOA) |
| Command | `/modify-module` |

---

## Purpose

Update module specifications (name, criteria, or priority) during orchestration. Changes are synchronized to the linked GitHub Issue and affected agents are notified.

---

## Prerequisites

- Module exists in state file
- Module is not in `complete` status
- GitHub CLI (gh) authenticated
- AI Maestro running (for agent notifications)

---

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `module_id` | Yes | ID of module to modify |
| `name` | No | New display name |
| `criteria` | No | New acceptance criteria |
| `priority` | No | New priority level |

At least one of `name`, `criteria`, or `priority` must be provided.

---

## Command Syntax

```bash
/modify-module <MODULE_ID> [--name NAME] [--criteria TEXT] [--priority LEVEL]
```

**Examples**:

```bash
# Change criteria only
/modify-module auth-core --criteria "Support JWT with 24h expiry and refresh tokens"

# Change priority only
/modify-module auth-core --priority critical

# Change multiple fields
/modify-module auth-core --name "Core Auth v2" --criteria "New criteria" --priority high
```

---

## Modification Restrictions by Status

| Module Status | Name | Criteria | Priority |
|---------------|------|----------|----------|
| `pending` | Yes | Yes | Yes |
| `assigned` | Yes | Yes | Yes |
| `in-progress` | Yes* | Yes* | Yes |
| `complete` | No | No | No |

*Requires agent notification

---

## Steps

1. **Validate module exists**:
   - Check state file for module_id
   - Verify status allows modification

2. **Validate inputs**:
   - At least one field to modify
   - New values pass validation rules

3. **Check if agent notification needed**:
   - If status is `assigned` or `in-progress`, notify agent

4. **Update state file**:
   ```yaml
   modules_status:
     - id: "<module_id>"
       name: "<NEW_NAME or existing>"
       acceptance_criteria: "<NEW_CRITERIA or existing>"
       priority: "<NEW_PRIORITY or existing>"
   ```

5. **Update GitHub Issue**:
   - Update title if name changed
   - Update body if criteria changed
   - Update labels if priority changed

6. **Notify assigned agent** (if applicable). Send using the `agent-messaging` skill:
   - **Recipient**: the assigned agent session name
   - **Subject**: "Module Modified: <module_id>"
   - **Content**: "Module specifications updated. Review changes before continuing."
   - **Type**: `notification`, **Priority**: `high`

   **Verify**: confirm message delivery.

7. **Log the modification** in orchestration log

---

## Agent Notification Template

```markdown
## Module Modified: <module_id>

The specifications for your assigned module have been updated.

### Changes
<list_of_changes>

### Updated Specifications
**Name**: <current_name>
**Criteria**: <current_criteria>
**Priority**: <current_priority>

### Action Required
1. Review the updated specifications
2. Confirm understanding via message
3. Continue implementation with updated requirements

If you have concerns about the changes, reply immediately.
```

---

## GitHub Issue Update

```bash
# Update title if name changed
gh issue edit <issue_number> --title "[Module] <NEW_NAME>"

# Update body if criteria changed
gh issue edit <issue_number> --body "<UPDATED_BODY>"

# Update priority label
gh issue edit <issue_number> --remove-label "priority-<OLD>" --add-label "priority-<NEW>"
```

---

## Output

| Output | Format | Description |
|--------|--------|-------------|
| State file updated | YAML changes | Modified fields |
| GitHub Issue updated | Issue changes | Title/body/labels |
| Agent notified | AI Maestro message | If assigned/in-progress |
| Console confirmation | Text | "Module '<id>' modified" |

---

## Success Criteria

- State file reflects new values
- GitHub Issue matches state file
- Agent notified if work in progress
- Modification logged with timestamp

---

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Module not found | Wrong ID | Use `/orchestration-status` to list IDs |
| Cannot modify complete | Status restriction | No action possible |
| GitHub update fails | Network or permissions | Retry, manual update if needed |
| Agent notification fails | AI Maestro down | Retry, escalate if persistent |

---

## Important Rules

1. **Complete modules cannot be modified** - Create new module if needed
2. **Agent must be notified** - Never change specs silently during active work
3. **GitHub stays in sync** - State file and Issue must match
4. **Document the change** - Log who changed what and why

---

## Modification Audit

Each modification should be logged:

```yaml
modification_log:
  - module_id: "auth-core"
    timestamp: "2025-02-05T15:30:00Z"
    changed_by: "orchestrator"
    changes:
      criteria:
        from: "Support JWT"
        to: "Support JWT with 24h expiry"
    reason: "User clarification request"
```

---

## Next Operations

After modifying:
- If agent notified → Wait for agent acknowledgment
- View current state: `/orchestration-status`
- Further changes: Run `/modify-module` again
