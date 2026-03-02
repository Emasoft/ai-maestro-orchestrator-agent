---
name: eoa-modify-module
description: "Modify a module's specifications during Orchestration Phase"
argument-hint: "<MODULE_ID> [--name NAME] [--criteria TEXT] [--priority LEVEL]"
allowed-tools: ["Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/eoa_modify_module.py:*)"]
---

# Modify Module Command

Change the specifications of a module during Orchestration Phase. If module is assigned, notifies the assigned agent.

## Usage

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_modify_module.py" modify $ARGUMENTS
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `MODULE_ID` | Yes | ID of the module to modify |
| `--name` | No | New display name |
| `--criteria` | No | New acceptance criteria |
| `--priority` | No | New priority level |

## What This Command Does

1. **Updates Module Specifications**
   - Changes requested fields
   - Updates state file

2. **Updates GitHub Issue**
   - Syncs changes to linked issue
   - Updates labels if priority changed

3. **Notifies Assigned Agent** (if assigned)
   - Sends update message via AI Maestro using the `agent-messaging` skill
   - Agent must acknowledge spec change

## Restrictions

| Module Status | Can Modify? |
|---------------|-------------|
| `pending` | ✓ All fields |
| `in_progress` | ✓ With notification |
| `complete` | ✗ Cannot modify |

## Agent Notification

When modifying an in-progress module, the assigned agent receives:

```markdown
Subject: [UPDATE] Module: {module_name} - Spec Change

The specifications for your assigned module have been updated:

**Changes:**
- Criteria: {new_criteria}
- Priority: {new_priority}

Please acknowledge this update and adjust your implementation accordingly.

If this significantly impacts your current work, report the impact immediately.
```

## Examples

```bash
# Add criteria to existing module
/modify-module auth-core --criteria "Support JWT with 24h expiry"

# Change priority
/modify-module oauth-google --priority critical

# Change name
/modify-module auth-2fa --name "Multi-Factor Authentication"

# Multiple changes
/modify-module password-reset --criteria "Include OTP option" --priority high
```

## State File Update

The module entry is updated with new values:

```yaml
modules_status:
  - id: "auth-core"
    name: "Core Authentication"
    status: "in_progress"
    acceptance_criteria: "Support JWT with 24h expiry"  # Updated
    priority: "critical"  # Updated
    # ... other fields unchanged
```

## Related Commands

- `/orchestration-status` - View module details
- `/add-module` - Add new module
- `/remove-module` - Remove pending module
