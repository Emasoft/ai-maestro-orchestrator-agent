---
name: eoa-add-module
description: "Add a new module during Orchestration Phase (dynamic flexibility)"
argument-hint: "<NAME> --criteria <TEXT> [--priority LEVEL]"
allowed-tools: ["Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/eoa_modify_module.py:*)"]
---

# Add Module Command

Add a new module to the plan during Orchestration Phase. Supports dynamic flexibility where user can expand scope on the go.

## Usage

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_modify_module.py" add $ARGUMENTS
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `NAME` | Yes | Name of the new module |
| `--criteria` | Yes | Acceptance criteria |
| `--priority` | No | Priority: `critical`, `high`, `medium`, `low` |

## What This Command Does

1. **Adds Module to State File**
   - Creates new module entry with pending status
   - Generates module ID from name

2. **Creates GitHub Issue**
   - Automatically creates issue for the new module
   - Applies appropriate labels

3. **Updates Completion Tracking**
   - Stop hook now includes this module
   - Exit blocked until this module completes

## Dynamic Flexibility

When you add a module mid-orchestration:

```
Before:
  - Modules: [A: done, B: in_progress]
  - Pending: 1

/add-module "Password Reset" --criteria "Reset via email link" --priority high

After:
  - Modules: [A: done, B: in_progress, C: pending]
  - Pending: 2
  - Stop hook blocks: "2 modules remaining"
```

## Examples

```bash
# Add a critical feature
/add-module "Two-Factor Auth" --criteria "Support TOTP and SMS" --priority critical

# Add a medium priority enhancement
/add-module "Remember Me" --criteria "Persist login for 30 days" --priority medium

# Add with default priority
/add-module "Password Strength Meter" --criteria "Show strength indicator"
```

## State File Update

```yaml
modules_status:
  # ... existing modules ...
  - id: "password-reset"
    name: "Password Reset"
    status: "pending"
    assigned_to: null
    github_issue: "#47"
    pr: null
    verification_loops: 0
    acceptance_criteria: "Reset via email link"
    priority: "high"
```

## Next Steps After Adding

1. Run `/orchestration-status` to see updated module list
2. Use `/assign-module` to assign the new module
3. Continue with Instruction Verification Protocol

## Related Commands

- `/orchestration-status` - View all modules
- `/modify-module` - Change module specs
- `/remove-module` - Remove pending module
- `/assign-module` - Assign to agent
