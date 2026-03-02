# Central Configuration - Part 4: Workflows and Protocols


## Contents

- [Table of Contents](#table-of-contents)
- [Reference-Based Sharing](#reference-based-sharing)
  - [How Task Instructions Reference Configs](#how-task-instructions-reference-configs)
  - [Agent Workflow for Reading Configs](#agent-workflow-for-reading-configs)
  - [Example Agent Flow](#example-agent-flow)
- [Config Update Protocol](#config-update-protocol)
  - [When Configuration Changes](#when-configuration-changes)
  - [Change Notification Message](#change-notification-message)
  - [Agent Response to Config Change](#agent-response-to-config-change)
  - [Handling Config Update Conflicts](#handling-config-update-conflicts)
- [Integration with Change Notification](#integration-with-change-notification)
  - [Reference to Change Notification Protocol](#reference-to-change-notification-protocol)
  - [Config Changes Trigger Notifications](#config-changes-trigger-notifications)
- [Best Practices](#best-practices)
  - [DO](#do)
  - [DON'T](#dont)
- [Troubleshooting](#troubleshooting)
  - [Problem: Agent uses outdated configuration](#problem-agent-uses-outdated-configuration)
  - [Problem: Config files grow too large](#problem-config-files-grow-too-large)
  - [Problem: Multiple agents report same config conflict](#problem-multiple-agents-report-same-config-conflict)
  - [Problem: Config changes not reflected in agent output](#problem-config-changes-not-reflected-in-agent-output)
- [Related Documentation](#related-documentation)
- [Related Parts](#related-parts)

---

## Table of Contents

1. [If you need to reference configs in task messages](#reference-based-sharing)
   - [How Task Instructions Reference Configs](#how-task-instructions-reference-configs)
   - [Agent Workflow for Reading Configs](#agent-workflow-for-reading-configs)
   - [Example Agent Flow](#example-agent-flow)
2. [If you need to update a configuration file](#config-update-protocol)
   - [When Configuration Changes](#when-configuration-changes)
   - [Change Notification Message](#change-notification-message)
   - [Agent Response to Config Change](#agent-response-to-config-change)
   - [Handling Config Update Conflicts](#handling-config-update-conflicts)
3. [If config changes affect active agents](#integration-with-change-notification)
   - [Reference to Change Notification Protocol](#reference-to-change-notification-protocol)
   - [Config Changes Trigger Notifications](#config-changes-trigger-notifications)
4. [If you want to follow best practices for config management](#best-practices)
5. [If config management is not working as expected](#troubleshooting)
6. [If you need to understand related protocols and systems](#related-documentation)

---

## Reference-Based Sharing

### How Task Instructions Reference Configs

**WRONG** (embedding config in message):

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "dev-agent-1",
  "content": {
    "instructions": "Use Python 3.12, uv for packages, ruff for formatting with line length 88, pytest for tests, write docstrings for all functions, use snake_case for functions..."
  }
}
```

**Size**: 500+ tokens per message × 20 agents = 10,000 tokens wasted

---

**CORRECT** (referencing central config):

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "dev-agent-1",
  "content": {
    "instructions": "Implement user authentication according to `design/specs/requirements.md` feature GH-101. Follow toolchain in `design/config/toolchain.md` and standards in `design/config/standards.md`."
  }
}
```

**Size**: 50 tokens per message × 20 agents = 1,000 tokens

**Savings**: 90% reduction in message size

### Agent Workflow for Reading Configs

1. **Receive task message** with config references
2. **Read referenced config files** from `design/config/` and `design/specs/`
3. **Apply configuration** to task execution
4. **Report deviations** if config cannot be followed

### Example Agent Flow

```bash
# Agent receives task: "Implement GH-101 per design/specs/requirements.md"

# Step 1: Read requirement
cat design/specs/requirements.md | grep -A 20 "GH-101"

# Step 2: Read toolchain config
cat design/config/toolchain.md

# Step 3: Read code standards
cat design/config/standards.md

# Step 4: Execute task following all configs
uv venv --python 3.12
source .venv/bin/activate
# ... implement feature ...

# Step 5: Report back using the agent-messaging skill
# Send a task-completion message to orchestrator-master
# Include: type (task-completion), status (success),
# and the list of configs followed
```

---

## Config Update Protocol

### When Configuration Changes

1. **Orchestrator updates config file** in `design/config/`
2. **Orchestrator records change** in config file header:
   ```markdown
   **Last Updated**: 2025-12-31 04:15:00
   **Updated By**: orchestrator-master
   **Change Summary**: Updated Python version from 3.11 to 3.12
   ```
3. **Orchestrator sends change notification** to all active agents (see Change Notification Protocol)
4. **Agents acknowledge** and re-read config
5. **Orchestrator logs acknowledgments** in `design/memory/progress.md`

### Change Notification Message

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "all-active-agents",
  "subject": "CONFIG UPDATE: Toolchain configuration changed",
  "priority": "high",
  "content": {
    "type": "config-change-notification",
    "changed_files": [
      "design/config/toolchain.md"
    ],
    "change_summary": "Updated Python version from 3.11 to 3.12",
    "action_required": "Re-read config before starting next task",
    "effective_immediately": true
  }
}
```

### Agent Response to Config Change

**Agent must**:
1. **Acknowledge receipt** via echo acknowledgment protocol
2. **Re-read changed config files**
3. **Apply new config** to current/future tasks
4. **Report conflicts** if current task cannot comply with new config

**Acknowledgment message**:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "orchestrator-master",
  "subject": "ACK: Config update received",
  "content": {
    "type": "echo-acknowledgment",
    "original_subject": "CONFIG UPDATE: Toolchain configuration changed",
    "configs_reread": [
      "design/config/toolchain.md"
    ],
    "status": "applied|conflict",
    "conflict_details": "Currently using Python 3.11, will switch for next task"
  }
}
```

### Handling Config Update Conflicts

**If agent has task in progress**:

1. **Minor changes** (formatting, linting): Apply immediately
2. **Major changes** (language version, framework): Complete current task with old config, apply new config to next task
3. **Breaking changes** (incompatible requirements): Report conflict, wait for orchestrator decision

**Conflict report**:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "orchestrator-master",
  "subject": "CONFIG CONFLICT: Cannot apply update to current task",
  "priority": "high",
  "content": {
    "type": "config-conflict",
    "task_id": "GH-101",
    "changed_config": "design/config/toolchain.md",
    "conflict": "Task started with Python 3.11, new config requires 3.12",
    "options": [
      "A: Complete task with 3.11, apply 3.12 to next task",
      "B: Restart task with 3.12",
      "C: Rollback config change"
    ],
    "recommendation": "A",
    "awaiting_decision": true
  }
}
```

---

## Integration with Change Notification

### Reference to Change Notification Protocol

See `change-notification-protocol.md` for complete details on:

- **Broadcast mechanism** for notifying all agents
- **Echo acknowledgment pattern** for confirming receipt
- **Retry logic** for agents that don't acknowledge
- **Timeout handling** for offline agents

### Config Changes Trigger Notifications

Every update to any file in `design/config/` or `design/specs/` MUST trigger a change notification to all active agents.

**Orchestrator workflow**:

```bash
# 1. Update config file
echo "Updated content" >> design/config/toolchain.md

# 2. Send change notification
Send a config change notification to all active agents using the `agent-messaging` skill:
- **Recipient**: broadcast to all active agents
- **Subject**: "CONFIG UPDATE: toolchain.md changed"
- **Content**: notification of changed files and required action
- **Type**: `config-change-notification`
- **Priority**: `high`
- **Data**: include `changed_files`, `change_summary`, `action_required`, `acknowledge_required` (true)

**Verify**: confirm message delivery to all active agents.

# 3. Monitor for acknowledgments
# (See change-notification-protocol.md for ack tracking)
```

---

## Best Practices

### DO

- **Keep configs small and focused**: Each file addresses one concern
- **Document every change**: Update header with timestamp, author, summary
- **Reference, don't embed**: Always point agents to config files
- **Version control configs**: Commit all `design/` changes to git
- **Notify on updates**: Use change notification protocol
- **Track acknowledgments**: Ensure all agents received updates

### DON'T

- **Embed configuration in messages**: Use references instead
- **Skip change notifications**: Always notify when configs change
- **Allow config drift**: Enforce single source of truth
- **Update without documenting**: Every change needs rationale
- **Ignore conflicts**: Address agent conflicts promptly

---

## Troubleshooting

### Problem: Agent uses outdated configuration

**Symptoms**: Agent reports using old tool version or standard

**Solution**:
1. Check if change notification was sent
2. Verify agent acknowledged notification
3. Resend notification if not acknowledged
4. Check agent's `design/memory/config-snapshot.md` for what it read

### Problem: Config files grow too large

**Symptoms**: Config files exceed 5000 tokens

**Solution**:
1. Split into multiple focused files
2. Create subdirectories: `design/config/python/`, `design/config/typescript/`
3. Update references in task messages

### Problem: Multiple agents report same config conflict

**Symptoms**: Multiple agents blocked on same config change

**Solution**:
1. Review changed config for compatibility
2. Consider rollback if change is breaking
3. Provide migration guide in config file
4. Update task instructions to handle transition period

### Problem: Config changes not reflected in agent output

**Symptoms**: Agent output doesn't match current config

**Solution**:
1. Verify agent acknowledged config update
2. Check timestamp of agent's config read vs. update time
3. Force agent to re-read: send explicit "re-read config" message
4. If persistent, check if agent is caching config locally (shouldn't)

---

## Related Documentation

- `change-notification-protocol.md` - How to broadcast config updates
- `echo-acknowledgment-protocol.md` - How agents confirm receipt
- `messaging-protocol.md` - Base messaging system
- `task-instruction-format.md` - How to reference configs in tasks

---

## Related Parts

- **Part 1**: [Overview and Structure](central-configuration-part1-overview-structure.md) - Why config matters, directory layout
- **Part 2**: [Tooling Templates](central-configuration-part2-tooling-templates.md) - toolchain.md, standards.md, environment.md templates
- **Part 3**: [Spec Templates](central-configuration-part3-spec-templates.md) - decisions.md, requirements.md, architecture.md, interfaces.md templates
