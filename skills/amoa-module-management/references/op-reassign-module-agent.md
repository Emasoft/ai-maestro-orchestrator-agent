# Operation: Reassign Module to Different Agent


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Command Syntax](#command-syntax)
- [Reassignment Scenarios](#reassignment-scenarios)
- [Steps](#steps)
- [Old Agent STOP Message](#old-agent-stop-message)
- [STOP: Module Reassigned](#stop-module-reassigned)
- [New Agent Assignment Message](#new-agent-assignment-message)
- [Module Assignment: <module_id>](#module-assignment-module_id)
  - [Background](#background)
  - [Previous Progress (if any)](#previous-progress-if-any)
  - [Specifications](#specifications)
  - [Instructions](#instructions)
- [Output](#output)
- [Success Criteria](#success-criteria)
- [Error Handling](#error-handling)
- [Important Rules](#important-rules)
- [Instruction Verification Protocol Reset](#instruction-verification-protocol-reset)
- [Reassignment Audit](#reassignment-audit)
- [Next Operations](#next-operations)

## Metadata

| Field | Value |
|-------|-------|
| Operation ID | `op-reassign-module-agent` |
| Procedure | `proc-update-tasks` |
| Workflow Step | Step 16 |
| Trigger | Agent stuck, unavailable, or reassignment needed |
| Actor | Orchestrator (EOA) |
| Command | `/reassign-module` |

---

## Purpose

Transfer a module from one implementer agent to another. This involves notifying the old agent to stop work, transferring context, and restarting the Instruction Verification Protocol with the new agent.

---

## Prerequisites

- Module exists and is assigned or in-progress
- New agent is registered and available
- AI Maestro running for notifications
- Old agent's progress information accessible

---

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `module_id` | Yes | ID of module to reassign |
| `to` | Yes | ID of new agent to assign |

---

## Command Syntax

```bash
/reassign-module <MODULE_ID> --to <NEW_AGENT_ID>
```

**Example**:

```bash
/reassign-module auth-core --to implementer-2
```

---

## Reassignment Scenarios

| Scenario | When to Reassign |
|----------|------------------|
| Agent blocked | Cannot progress due to external dependency |
| Agent unavailable | Offline, crashed, or unresponsive |
| Skill mismatch | Task needs different expertise |
| Load balancing | One agent overloaded |
| Escalation | Task needs more experienced agent |

---

## Steps

1. **Validate inputs**:
   - Module exists and is assigned/in-progress
   - New agent is different from current
   - New agent is registered

2. **Request progress report** from old agent (if responsive). Send using the `agent-messaging` skill:
   - **Recipient**: the old agent session name
   - **Subject**: "Progress Report Request: <module_id>"
   - **Content**: "Please provide current progress on module before reassignment."
   - **Type**: `request`, **Priority**: `urgent`

3. **Notify old agent to stop**. Send using the `agent-messaging` skill:
   - **Recipient**: the old agent session name
   - **Subject**: "STOP: Module Reassigned - <module_id>"
   - **Content**: "Stop work on this module immediately. It is being reassigned."
   - **Type**: `command`, **Priority**: `urgent`

   **Verify**: confirm both messages were delivered.

4. **Update state file**:
   ```yaml
   modules_status:
     - id: "<module_id>"
       status: "assigned"  # Reset from in-progress if applicable
       assigned_to: "<new_agent_id>"

   active_assignments:
     # Remove old assignment
     # Add new assignment with reset verification
     - agent: "<new_agent_id>"
       module: "<module_id>"
       status: "pending_verification"
       instruction_verification:
         status: "awaiting_repetition"
         repetition_received: false
         repetition_correct: false
         authorized_at: null
   ```

5. **Update GitHub Issue**:
   ```bash
   gh issue edit <issue_number> \
     --remove-assignee "<old_agent>" \
     --add-assignee "<new_agent>"

   gh issue comment <issue_number> \
     --body "Module reassigned from @<old_agent> to @<new_agent>"
   ```

6. **Send full assignment to new agent**:
   - Include module specifications
   - Include any progress context from old agent
   - Start Instruction Verification Protocol

7. **Log the reassignment**

---

## Old Agent STOP Message

```markdown
## STOP: Module Reassigned

**Module**: <module_id>
**GitHub Issue**: <issue_number>

This module is being reassigned to another agent. Please:

1. **Stop all work** on this module immediately
2. **Do not commit** any uncommitted changes
3. **Do not create PR** for this module
4. **Report** any completed work that should be preserved

Reason for reassignment: <reason>

Thank you for your work on this module.
```

---

## New Agent Assignment Message

```markdown
## Module Assignment: <module_id>

**GitHub Issue**: <issue_number>
**Priority**: <priority>

### Background
This module was previously assigned to another agent. You are taking over.

### Previous Progress (if any)
<progress_from_old_agent_or_"None - starting fresh">

### Specifications

**Module Name**: <name>

**Acceptance Criteria**:
<criteria>

### Instructions

1. Review the specifications above
2. Respond with your understanding (Instruction Verification Protocol)
3. Wait for PROCEED before starting implementation

Do NOT begin coding until you receive PROCEED.
```

---

## Output

| Output | Format | Description |
|--------|--------|-------------|
| Old agent notified | AI Maestro message | STOP command |
| State file updated | YAML changes | Assignment transferred |
| GitHub Issue updated | Assignee changed | New agent assigned |
| New agent notified | AI Maestro message | Full assignment |
| Console confirmation | Text | "Module reassigned from X to Y" |

---

## Success Criteria

- Old agent received STOP notification
- State file shows new assignment
- Instruction Verification Protocol reset
- GitHub Issue assignee updated
- New agent received full context
- Progress preserved if applicable

---

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Old agent unresponsive | Agent crashed | Proceed without progress report |
| New agent unavailable | Not registered | Register first, then reassign |
| Module complete | Cannot reassign | No action needed |
| GitHub update fails | Permissions | Manual update |

---

## Important Rules

1. **Always notify old agent** - Even if unresponsive, send STOP
2. **Reset verification** - New agent must go through full IVP
3. **Preserve progress** - Get status before reassigning if possible
4. **Document reason** - Log why reassignment was needed

---

## Instruction Verification Protocol Reset

After reassignment, the new agent must:

1. Receive full module specifications
2. Repeat understanding back (IVP Step 1)
3. Answer clarifying questions (IVP Step 2)
4. Receive PROCEED authorization (IVP Step 3)

**No shortcuts** - Even if old agent was partway through, new agent starts fresh verification.

---

## Reassignment Audit

Log each reassignment:

```yaml
reassignment_log:
  - module_id: "auth-core"
    reassigned_at: "2025-02-05T15:30:00Z"
    from_agent: "implementer-1"
    to_agent: "implementer-2"
    reason: "implementer-1 blocked on external API"
    progress_at_reassignment: "40% - JWT implementation complete, refresh tokens pending"
```

---

## Next Operations

After reassignment:
- Wait for new agent acknowledgment
- Start Instruction Verification Protocol
- Monitor old agent for STOP compliance
- Continue with new agent through normal workflow
