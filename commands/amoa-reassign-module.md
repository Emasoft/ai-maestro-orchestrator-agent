---
name: eoa-reassign-module
description: "Reassign a module to a different agent"
argument-hint: "<MODULE_ID> --to <NEW_AGENT_ID>"
allowed-tools: ["Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/eoa_reassign_module.py:*)"]
---

# Reassign Module Command

Transfer a module assignment from one agent to another. Notifies both the old and new agent.

## Usage

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_reassign_module.py" $ARGUMENTS
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `MODULE_ID` | Yes | ID of the module to reassign |
| `--to` | Yes | ID of the new agent |

## When to Reassign

| Scenario | Recommended Action |
|----------|-------------------|
| Agent blocked | Try unblocking first, then reassign |
| Agent unresponsive | Reassign after 3 failed polls |
| Agent failed verification | Reassign to different agent |
| Priority change | Reassign to faster agent |
| Agent overloaded | Distribute to other agents |

## What This Command Does

1. **Validates Reassignment**
   - Module exists and is assigned
   - New agent is registered
   - New agent is available

2. **Notifies Old Agent** (AI agents)
   ```markdown
   Subject: [STOP] Module: {module_name} - Reassigned

   This module has been reassigned to another agent.
   Please stop work immediately and report current progress.

   Do NOT commit any incomplete changes.
   ```

3. **Notifies New Agent** (AI agents)
   - Full assignment message
   - Instruction Verification Protocol initiates

4. **Updates State**
   - Changes assignment record
   - Resets verification status

## Restrictions

| Module Status | Can Reassign? |
|---------------|---------------|
| `pending` | ✓ Yes |
| `in_progress` | ✓ With caution |
| `complete` | ✗ No |

## Reassigning In-Progress Modules

When reassigning an in-progress module:
- Old agent may have partial work
- Request status report before reassignment
- New agent starts fresh (no handoff)
- Document reason in GitHub Issue

## Examples

```bash
# Reassign to different AI agent
/reassign-module auth-core --to implementer-2

# Reassign to human developer
/reassign-module oauth-google --to dev-alice
```

## State File Update

```yaml
active_assignments:
  - agent: "implementer-2"  # Changed
    agent_type: "ai"
    module: "auth-core"
    github_issue: "#42"
    task_uuid: "task-uuid-67890"  # New UUID
    status: "pending_verification"  # Reset
    instruction_verification:
      status: "awaiting_repetition"  # Reset
      # ... reset all verification fields
```

## Related Commands

- `/assign-module` - Initial assignment
- `/check-agents` - Monitor progress
- `/orchestration-status` - View assignments
