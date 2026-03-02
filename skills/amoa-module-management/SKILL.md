---
name: eoa-module-management-commands
description: "Trigger with module management tasks. Use when managing modules during Orchestration Phase (add, modify, remove, prioritize, reassign). Every module maps 1:1 to GitHub Issue."
license: Apache-2.0
compatibility: Cross-platform compatible. Requires Python 3.8+ and PyYAML for scripts. Requires gh CLI for GitHub Issue operations. Works with AI Maestro messaging for agent notifications. Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
user-invocable: false
context: fork
agent: eoa-main
workflow-instruction: "Steps 11, 16"
procedure: "proc-create-task-docs, proc-update-tasks"
---

# Module Management Commands Skill

## Overview

This skill teaches orchestrators how to dynamically manage modules during the Orchestration Phase.

## Prerequisites

- Orchestration Phase active (Plan Phase completed and approved)
- GitHub CLI (gh) authenticated
- AI Maestro running for agent notifications
- State file `design/state/exec-phase.md` exists Modules are the atomic units of work in EOA orchestration. Each module represents one feature, component, or deliverable that an agent will implement.

**CRITICAL RULE**: Every module is tied 1:1 to a GitHub Issue. When you add a module, an issue is created. When you remove a module, the issue is closed. When you modify a module, the issue is updated. This linkage ensures traceability and transparency.

## Instructions

1. Identify the module management action needed (add, modify, remove, prioritize, or reassign)
2. Verify prerequisites: Orchestration Phase active, gh CLI authenticated, AI Maestro running
3. Execute the appropriate command with required parameters
4. Verify the module state update in `design/state/exec-phase.md`
5. Confirm GitHub Issue synchronization completed
6. Notify affected agents via AI Maestro if applicable

## Output

| Output Type | Format | Location |
|-------------|--------|----------|
| Module state update | YAML | `design/state/exec-phase.md` |
| GitHub Issue created/updated | Issue number | GitHub repository |
| Agent notification | AI Maestro message | Agent inbox |
| Command success/failure | Status message | Console output |

## Commands Overview

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/add-module` | Add new module | User requests new feature |
| `/modify-module` | Change module specs | Criteria or priority change |
| `/remove-module` | Delete pending module | Module cancelled |
| `/prioritize-module` | Change priority level | Urgency changed |
| `/reassign-module` | Transfer to different agent | Agent stuck or unavailable |

---

## Quick Reference by Situation

### Situation: User wants a new feature

1. Use `/add-module` with name and criteria
2. System creates GitHub Issue automatically
3. Module appears in pending queue
4. Assign to agent when ready

**Read**: [module-creation.md](./references/module-creation.md)
- 1.1 When to add modules during orchestration
- 1.2 Required fields for new modules (name, criteria)
- 1.3 Optional fields (priority level)
- 1.4 Automatic GitHub Issue creation
- 1.5 State file update after addition
- 1.6 Complete examples with all variations

### Situation: Requirements changed for a module

1. Use `/modify-module` with new specs
2. System updates linked GitHub Issue
3. If module assigned, agent is notified

**Read**: [module-modification.md](./references/module-modification.md)
- 2.1 What can be modified (name, criteria, priority)
- 2.2 Modification restrictions by status
- 2.3 Agent notification protocol
- 2.4 GitHub Issue synchronization
- 2.5 Complete modification examples

### Situation: Module needs to be cancelled

1. Verify module status is `pending`
2. Use `/remove-module` with module ID
3. System closes linked GitHub Issue

**Read**: [module-removal-rules.md](./references/module-removal-rules.md)
- 3.1 Which modules can be removed (pending only)
- 3.2 Why in-progress modules cannot be removed
- 3.3 Removal process step by step
- 3.4 GitHub Issue closure with wontfix label
- 3.5 Alternatives to removal (scope reduction)
- 3.6 Error handling and recovery

### Situation: Module urgency changed

1. Use `/prioritize-module` with new level
2. System updates GitHub Issue labels
3. Agent notified if assigned

**Read**: [module-prioritization.md](./references/module-prioritization.md)
- 4.1 Priority levels explained (critical, high, medium, low)
- 4.2 Effects on assignment queue
- 4.3 GitHub Issue label updates
- 4.4 When to escalate vs downgrade
- 4.5 Complete priority change examples

### Situation: Module needs different agent

1. Request progress report from current agent
2. Use `/reassign-module` with new agent ID
3. Old agent notified to stop work
4. New agent receives full assignment

**Read**: [module-reassignment.md](./references/module-reassignment.md)
- 5.1 When reassignment is appropriate
- 5.2 Reassignment workflow step by step
- 5.3 Old agent notification protocol
- 5.4 New agent assignment message
- 5.5 State file updates during reassignment
- 5.6 Instruction Verification Protocol reset

---

## The Module-Issue Relationship

Every module in EOA orchestration has a corresponding GitHub Issue. This relationship is fundamental and cannot be bypassed.

### Why Modules Map to Issues

| Reason | Benefit |
|--------|---------|
| Traceability | All work is tracked in GitHub |
| Transparency | Stakeholders see progress |
| Integration | PRs link to issues |
| History | Changes documented |
| Accountability | Assignment visible |

### Automatic Synchronization

| Module Event | GitHub Issue Action |
|--------------|---------------------|
| Module added | Issue created with labels |
| Module modified | Issue body/labels updated |
| Module removed | Issue closed with wontfix |
| Priority changed | Priority label updated |
| Agent assigned | Issue assigned to developer |
| Module completed | Issue closed with linked PR |

**Read**: [github-issue-sync.md](./references/github-issue-sync.md)
- 6.1 Issue creation format and labels
- 6.2 Issue update synchronization
- 6.3 Issue closure protocols
- 6.4 Label conventions (module, priority-*, status-*)
- 6.5 Manual sync when automation fails
- 6.6 Troubleshooting sync issues

---

## Command Details

### /add-module

**Usage**: `/add-module "<NAME>" --criteria "<TEXT>" [--priority LEVEL]`

| Argument | Required | Description |
|----------|----------|-------------|
| NAME | Yes | Display name for the module |
| --criteria | Yes | Acceptance criteria text |
| --priority | No | `critical`, `high`, `medium`, `low` (default: medium) |

**What Happens**:
1. Module entry created in state file
2. GitHub Issue created with labels
3. Stop hook updated to include new module

**Example**:
```bash
/add-module "Two-Factor Auth" --criteria "Support TOTP and SMS" --priority critical
```

### /modify-module

**Usage**: `/modify-module <MODULE_ID> [--name NAME] [--criteria TEXT] [--priority LEVEL]`

| Argument | Required | Description |
|----------|----------|-------------|
| MODULE_ID | Yes | ID of module to modify |
| --name | No | New display name |
| --criteria | No | New acceptance criteria |
| --priority | No | New priority level |

**Restrictions**:
- `pending` modules: All fields modifiable
- `in-progress` modules: Modifiable with agent notification
- `complete` modules: Cannot modify

**Example**:
```bash
/modify-module auth-core --criteria "Support JWT with 24h expiry" --priority high
```

### /remove-module

**Usage**: `/remove-module <MODULE_ID> [--force]`

| Argument | Required | Description |
|----------|----------|-------------|
| MODULE_ID | Yes | ID of module to remove |
| --force | No | Skip confirmation |

**Restrictions**:
- Only `pending` modules can be removed
- `in-progress` modules cannot be removed
- `complete` modules cannot be removed

**Example**:
```bash
/remove-module oauth-facebook
```

### /prioritize-module

**Usage**: `/prioritize-module <MODULE_ID> --priority <LEVEL>`

| Argument | Required | Description |
|----------|----------|-------------|
| MODULE_ID | Yes | ID of module |
| --priority | Yes | `critical`, `high`, `medium`, `low` |

**Example**:
```bash
/prioritize-module auth-core --priority critical
```

### /reassign-module

**Usage**: `/reassign-module <MODULE_ID> --to <AGENT_ID>`

| Argument | Required | Description |
|----------|----------|-------------|
| MODULE_ID | Yes | ID of module to reassign |
| --to | Yes | ID of new agent |

**What Happens**:
1. Old agent receives STOP notification
2. Assignment record transferred
3. New agent receives full assignment
4. Instruction Verification Protocol resets

**Example**:
```bash
/reassign-module auth-core --to implementer-2
```

---

## State File Structure

Module management commands modify the orchestration state file at `design/state/exec-phase.md`.

### Module Entry Format

```yaml
modules_status:
  - id: "auth-core"           # Kebab-case identifier
    name: "Core Authentication"  # Display name
    status: "pending"         # pending|assigned|in-progress|complete
    assigned_to: null         # Agent ID or null
    github_issue: "#42"       # Linked issue number
    pr: null                  # Linked PR when complete
    verification_loops: 0     # Number of review cycles
    acceptance_criteria: "Support JWT and session tokens"
    priority: "high"          # critical|high|medium|low
```

### Assignment Entry Format

```yaml
active_assignments:
  - agent: "implementer-1"
    agent_type: "ai"
    module: "auth-core"
    github_issue: "#42"
    task_uuid: "task-abc123def456"
    status: "pending_verification"
    instruction_verification:
      status: "awaiting_repetition"
      repetition_received: false
      repetition_correct: false
      questions_asked: 0
      questions_answered: 0
      authorized_at: null
```

---

## Examples

### Example 1: Add New Module Mid-Orchestration

```bash
# User requests two-factor authentication
/add-module "Two-Factor Auth" --criteria "Support TOTP and SMS" --priority critical

# System automatically creates GitHub Issue #43
# Module appears in pending queue with status: pending
```

### Example 2: Reassign Blocked Module

```bash
# Agent implementer-1 is blocked on auth-core
# Request progress report first
/check-agents --agent implementer-1

# Reassign to implementer-2
/reassign-module auth-core --to implementer-2

# Old agent notified to stop
# New agent receives full assignment with Instruction Verification Protocol reset
```

---

## Error Handling

| Problem | Likely Cause | Solution |
|---------|--------------|----------|
| Module not found | Wrong ID used | Use `/orchestration-status` to see actual IDs |
| Cannot remove module | Status not pending | Modify scope instead of removing |
| GitHub Issue not created | gh CLI not authenticated | Run `gh auth login` |
| Agent not notified | AI Maestro not running | Verify AI Maestro AMP messaging is running using the `agent-messaging` skill health check |
| Priority not updating | Issue labels mismatch | Manually update GitHub Issue |

**For detailed troubleshooting**: [troubleshooting.md](./references/troubleshooting.md)
- 7.1 State file corruption recovery
- 7.2 GitHub sync failure recovery
- 7.3 Agent notification failures
- 7.4 Module ID conflicts
- 7.5 Force removal scenarios

---

## Scripts Reference

### Module Operations Script

**Location**: `scripts/module_operations.py`

Provides programmatic access to all module operations:

```bash
# Add module
python3 scripts/module_operations.py add "Module Name" --criteria "Criteria"

# Modify module
python3 scripts/module_operations.py modify module-id --priority critical

# Remove module
python3 scripts/module_operations.py remove module-id

# List modules
python3 scripts/module_operations.py list

# Validate module state
python3 scripts/module_operations.py validate
```

### GitHub Sync Script

**Location**: `scripts/github_sync.py`

Synchronizes module state with GitHub Issues:

```bash
# Sync all modules to GitHub
python3 scripts/github_sync.py sync-all

# Sync specific module
python3 scripts/github_sync.py sync module-id

# Verify sync status
python3 scripts/github_sync.py verify
```

---

## Reference Documents

| Reference | Contents |
|-----------|----------|
| [module-creation.md](./references/module-creation.md) | Add-module workflow, validation, examples |
| [module-modification.md](./references/module-modification.md) | Modify specs, notifications, restrictions |
| [module-removal-rules.md](./references/module-removal-rules.md) | Removal conditions, cleanup, alternatives |
| [module-prioritization.md](./references/module-prioritization.md) | Priority levels, effects, label updates |
| [module-reassignment.md](./references/module-reassignment.md) | Transfer workflow, notifications, reset |
| [github-issue-sync.md](./references/github-issue-sync.md) | Issue creation, labels, sync protocol |
| [troubleshooting.md](./references/troubleshooting.md) | Error recovery, force operations |

---

## Related Commands

| Command | Purpose |
|---------|---------|
| `/orchestration-status` | View all modules and assignments |
| `/assign-module` | Initial assignment to agent |
| `/check-agents` | Monitor agent progress |
| `/register-agent` | Register new agents |

---

## Summary

| Action | Command | Restrictions |
|--------|---------|--------------|
| Add module | `/add-module` | None |
| Modify specs | `/modify-module` | Cannot modify complete |
| Remove module | `/remove-module` | Pending only |
| Change priority | `/prioritize-module` | None |
| Reassign agent | `/reassign-module` | Cannot reassign complete |

**Key Principles**:
- Every module = 1 GitHub Issue
- Modifications sync to GitHub automatically
- Agent notifications via AI Maestro
- Instruction Verification required after reassignment

---

## Resources

- [module-creation.md](./references/module-creation.md) - Add-module workflow and validation
- [module-modification.md](./references/module-modification.md) - Modify specs and notifications
- [module-removal-rules.md](./references/module-removal-rules.md) - Removal conditions and cleanup
- [module-prioritization.md](./references/module-prioritization.md) - Priority levels and effects
- [module-reassignment.md](./references/module-reassignment.md) - Transfer workflow
- [github-issue-sync.md](./references/github-issue-sync.md) - Issue creation and sync
- [troubleshooting.md](./references/troubleshooting.md) - Error recovery

---

## Checklist

Copy this checklist and track your progress:

- [ ] Identify module management action needed (add/modify/remove/prioritize/reassign)
- [ ] Verify Orchestration Phase is active
- [ ] Confirm gh CLI is authenticated
- [ ] Verify AI Maestro messaging system (AMP) is running
- [ ] Execute appropriate command with required parameters
- [ ] Check module state updated in design/state/exec-phase.md
- [ ] Verify GitHub Issue created/updated with correct labels
- [ ] Confirm agent notification sent via AI Maestro (if applicable)
- [ ] Validate module-to-issue 1:1 relationship maintained
- [ ] Document any errors in troubleshooting log
