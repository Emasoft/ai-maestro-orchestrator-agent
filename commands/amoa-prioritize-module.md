---
name: eoa-prioritize-module
description: "Change a module's priority level"
argument-hint: "<MODULE_ID> --priority <LEVEL>"
allowed-tools: ["Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/eoa_modify_module.py:*)"]
---

# Prioritize Module Command

Change the priority level of a module. This is a shortcut for `/modify-module --priority`.

## Usage

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_modify_module.py" modify $ARGUMENTS
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `MODULE_ID` | Yes | ID of the module |
| `--priority` | Yes | New priority: `critical`, `high`, `medium`, `low` |

## Priority Levels

| Priority | Meaning | Assignment Behavior |
|----------|---------|---------------------|
| `critical` | Must complete first | Assign immediately |
| `high` | Important | Assign early |
| `medium` | Standard | Normal queue |
| `low` | Nice to have | Assign last |

## What This Command Does

1. **Updates Priority**
   - Changes priority in state file
   - Updates GitHub Issue labels

2. **May Trigger Reassignment**
   - Critical modules may need faster agent
   - Low modules may be delayed

3. **Notifies Agent** (if assigned)
   - Informs of priority change
   - May affect their schedule

## Examples

```bash
# Escalate to critical
/prioritize-module auth-core --priority critical

# Downgrade priority
/prioritize-module remember-me --priority low

# Set to high
/prioritize-module oauth-google --priority high
```

## GitHub Label Update

Priority change updates the issue labels:

```
Before: module, priority-medium, status-in-progress
After:  module, priority-critical, status-in-progress
```

## Related Commands

- `/modify-module` - Full modification command
- `/orchestration-status` - View priorities
- `/reassign-module` - Change agent
