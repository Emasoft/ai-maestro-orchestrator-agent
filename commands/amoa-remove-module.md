---
name: eoa-remove-module
description: "Remove a pending module from Orchestration Phase (only if not started)"
argument-hint: "<MODULE_ID> [--force]"
allowed-tools: ["Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/eoa_modify_module.py:*)"]
---

# Remove Module Command

Remove a module from Orchestration Phase. Only modules with `pending` status can be removed.

## Usage

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_modify_module.py" remove $ARGUMENTS
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `MODULE_ID` | Yes | ID of the module to remove |
| `--force` | No | Skip confirmation |

## Restrictions

| Module Status | Can Remove? |
|---------------|-------------|
| `pending` | ✓ Yes |
| `in_progress` | ✗ Cannot remove |
| `complete` | ✗ Cannot remove |

## What This Command Does

1. **Validates Removal**
   - Checks module status is `pending`
   - No agent assigned

2. **Removes from State**
   - Deletes module entry
   - Updates completion tracking

3. **Closes GitHub Issue**
   - Closes linked issue with comment
   - Labels as `wontfix`

## Dynamic Flexibility

When you remove a module:

```
Before:
  - Modules: [A: done, B: in_progress, C: pending]
  - Pending: 2

/remove-module C

After:
  - Modules: [A: done, B: in_progress]
  - Pending: 1
  - Stop hook blocks: "1 module remaining"
```

## Why Removal is Restricted

Once a module is `in_progress`:
- Agent has invested time understanding requirements
- Code may already be written
- Removing would waste resources

Instead of removing in-progress modules:
- Use `/modify-module` to reduce scope
- Use `/reassign-module` if agent is stuck
- Complete with minimal implementation

## Examples

```bash
# Remove a pending module
/remove-module oauth-facebook

# Remove with force (skip confirmation)
/remove-module legacy-support --force
```

## Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Status is in_progress" | Module started | Cannot remove, modify instead |
| "Status is complete" | Module done | Cannot remove completed work |
| "Has assignment" | Agent assigned | Unassign first |

## Related Commands

- `/orchestration-status` - View module status
- `/modify-module` - Change specs instead
- `/reassign-module` - Change assignment
