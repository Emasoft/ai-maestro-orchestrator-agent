---
name: amoa-reassign-module
description: "Reassign a module to a different agent"
argument-hint: "<MODULE_ID> --to <NEW_AGENT_ID> --reason \"<why>\""
allowed-tools: ["Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/amoa_reassign_module.py:*)"]
---

# Reassign Module Command

Transfer a module assignment from one agent to another. Notifies both the old and new agent.

## Usage

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/amoa_reassign_module.py" $ARGUMENTS
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `MODULE_ID` | Yes | ID of the module to reassign |
| `--to` | Yes | ID of the new agent |
| `--reason` | Yes | WHY you are taking the module from the current agent. Delivered verbatim to it. |

## `--reason` is required — you are refusing an agent's work

Taking a module from an agent IS a refusal, and a refusal is a **design review,
not a verdict** (USER-ratified fleet principle, 2026-07-16). The reason is
delivered verbatim in the `[STOP]` message, so write it for the agent, carrying:

1. **The precise defect** — which behavior/output/step. Not "not working out".
2. **The bar** — what would have kept the assignment.
3. **An invitation to respond** — it may be right about half your call.
4. **A push toward alternatives** when its approach is unsalvageable — refuse
   the implementation, never the need.

There is deliberately **no default reason**: a content-free string would satisfy
the flag and tell the agent nothing, which is the failure this prevents. An
agent overridden without explanation stops proposing approaches, and you never
see what you lost.

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

2. **Notifies Old Agent** (AI agents) — carrying your `--reason`
   ```markdown
   Subject: [STOP] Module: {module_name} - Reassigned

   This module has been reassigned to another agent.

   WHY: {your --reason, verbatim}

   Please stop work immediately and report current progress.
   Do NOT commit any incomplete changes.

   This is a design review, not a verdict on you. If you think
   the reason above is wrong or incomplete, reply and say so —
   the decision is reversible and you may be right.
   ```
   If the old agent has no `session_name`, the reason cannot be delivered and
   the command warns you on stderr — tell it another way.

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
/reassign-module auth-core --to implementer-2 \
  --reason "Blocked 3 polls on the OAuth callback with no progress report; impl-2 already holds the token-store context. The approach was sound — if you were nearly through it, reply and I'll hand it back."

# Reassign to human developer
/reassign-module oauth-google --to dev-alice \
  --reason "Google's consent screen needs a human in the browser for the one-time verification; nothing about your implementation is wrong. Alice does that step, then it comes back to you."
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
