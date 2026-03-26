# Module Reassignment Reference

## Contents

- 5.1 When reassignment is appropriate
- 5.2 Reassignment workflow step by step
- 5.3 Old agent notification protocol
- 5.4 New agent assignment message
- 5.5 State file updates during reassignment
- 5.6 Instruction Verification Protocol reset

---

## 5.1 When Reassignment Is Appropriate

Reassignment transfers a module from one agent to another. This section explains when reassignment is the right action.

### Appropriate Scenarios for Reassignment

| Scenario | Signs | Recommended Action |
|----------|-------|-------------------|
| Agent blocked | No progress for 2+ poll cycles | Try unblocking first, then reassign |
| Agent unresponsive | No response to 3+ polls | Reassign immediately |
| Agent failed verification | Cannot pass Instruction Verification | Reassign to different agent |
| Priority escalation | Module became critical | May need faster agent |
| Agent overloaded | Agent has too many modules | Redistribute work |
| Skills mismatch | Agent lacks required expertise | Reassign to specialist |

### When NOT to Reassign

| Situation | Better Action |
|-----------|---------------|
| Agent just started | Give more time |
| Minor delay | Extend timeline |
| Agent requests help | Provide support |
| Nearly complete | Let agent finish |
| Module scope too large | Reduce scope |

### Reassignment vs Other Actions

| Issue | Action |
|-------|--------|
| Agent stuck on technical problem | Help agent, don't reassign |
| Agent doesn't understand requirements | Re-verify instructions, don't reassign |
| Agent overwhelmed with work | Reassign SOME modules, not all |
| Module requirements changed | Modify module, agent adapts |
| Agent unavailable temporarily | Wait if reasonable, reassign if long |

### Cost of Reassignment

Reassignment has costs:
1. Old agent's work may be lost (no handoff)
2. New agent starts from scratch
3. Instruction Verification must repeat
4. Time lost in transition

Consider these costs before deciding to reassign.

---

## 5.2 Reassignment Workflow Step by Step

When `/reassign-module` is executed, the following steps occur.

### Step 1: Validate Reassignment

Script validates:
- Module exists
- Module is not complete
- Module is currently assigned
- New agent is different from old agent
- New agent is registered

```python
if module.get("status") == "complete":
    print("ERROR: Cannot reassign completed module")
    return False

if not old_agent:
    print("ERROR: Module is not currently assigned")
    print("Use /assign-module instead")
    return False

if old_agent == new_agent:
    print("ERROR: Module already assigned to this agent")
    return False
```

### Step 2: Notify Old Agent (AI Only)

If old agent is an AI agent:
- STOP notification sent via AI Maestro
- Agent told to halt work immediately
- Agent requested to report progress

### Step 3: Remove Old Assignment

Old assignment record removed from `active_assignments`:

```python
assignments = data.get("active_assignments", [])
data["active_assignments"] = [
    a for a in assignments
    if a.get("module") != module_id
]
```

### Step 4: Create New Assignment

New assignment record created with:
- New agent ID
- New task UUID
- Reset verification status
- Reset polling status

### Step 5: Update Module

Module record updated:
- `assigned_to` changed to new agent
- `status` may reset to `assigned`

### Step 6: Notify New Agent (AI Only)

If new agent is an AI agent:
- Full assignment message sent
- Includes all requirements
- Includes verification request

### Step 7: Write State File

All changes written to state file.

### Step 8: Return Success

Output confirms reassignment with details.

---

## 5.3 Old Agent Notification Protocol

When a module is reassigned, the old agent must be notified to stop work.

### Notification Trigger

Old agent is notified when:
- Old agent type is `ai`
- Old agent has `session_name` configured
- AI Maestro is reachable

Human developers see the GitHub Issue assignee change instead.

### STOP Notification Message

**Subject**: `[STOP] Module: {module_name} - Reassigned`

**Body**:
```markdown
This module has been reassigned to another agent.
Please stop work immediately and report current progress.
Do NOT commit any incomplete changes.
```

### Expected Old Agent Response

After receiving STOP notification, old agent should:

1. **Stop work immediately** - Cease implementation
2. **Report progress** - Send status of what was done
3. **Do not commit** - Leave incomplete code uncommitted
4. **Do not push** - Do not push partial work
5. **Acknowledge** - Confirm receipt of STOP

### If Old Agent Continues Working

If old agent continues working despite STOP:
- New agent may encounter conflicts
- Old agent's work will be orphaned
- Orchestrator should follow up

**Follow-up message**:
```markdown
Subject: [URGENT] Stop Work Confirmation Required

You should have received a STOP notification for module {module_name}.
Please confirm you have stopped work and report your progress.
```

### No Handoff Between Agents

**Important**: There is no handoff mechanism between agents. The new agent starts fresh:
- No access to old agent's partial work
- No communication between agents
- New agent implements from scratch

If partial work is valuable:
1. Old agent should report what was done
2. Orchestrator can relay to new agent
3. New agent decides whether to incorporate

---

## 5.4 New Agent Assignment Message

The new agent receives a full assignment message, identical to initial assignment.

### Assignment Message Format

**Subject**: `[TASK] Module: {module_name} - UUID: {task_uuid}`

**Body**:
```markdown
## Assignment (Reassigned)

You have been assigned to implement: **{module_name}**

GitHub Issue: {issue_url}
Task UUID: {task_uuid}

## Acceptance Criteria
- {criteria}

## MANDATORY: Instruction Verification

Before you begin, please:
1. Repeat the key requirements in your own words
2. List any questions
3. Confirm your understanding

I will verify before authorizing implementation.
```

### Why "(Reassigned)" is Noted

The message includes "(Reassigned)" to inform the new agent that:
- This is not a fresh module
- Previous agent may have done partial work
- Be aware of potential existing artifacts

### New Task UUID

A new task UUID is generated for the reassignment:
- Old UUID: `task-abc123def456`
- New UUID: `task-xyz789ghij012`

The new UUID:
- Tracks this specific assignment
- Differentiates from previous assignment
- Used for correlation in messages

---

## 5.5 State File Updates During Reassignment

Reassignment modifies multiple sections of the state file.

### Module Record Update

**Before**:
```yaml
modules_status:
  - id: "auth-core"
    status: "in-progress"
    assigned_to: "implementer-1"
```

**After**:
```yaml
modules_status:
  - id: "auth-core"
    status: "assigned"
    assigned_to: "implementer-2"
```

### Old Assignment Removed

**Before**:
```yaml
active_assignments:
  - agent: "implementer-1"
    module: "auth-core"
    task_uuid: "task-old123"
```

**After**:
```yaml
active_assignments:
  # Old assignment removed
```

### New Assignment Added

```yaml
active_assignments:
  - agent: "implementer-2"
    agent_type: "ai"
    module: "auth-core"
    github_issue: "#42"
    task_uuid: "task-new456"
    status: "pending_verification"
    assigned_at: "2024-01-15T10:30:00Z"
    instruction_verification:
      status: "awaiting_repetition"
      repetition_received: false
      repetition_correct: false
      questions_asked: 0
      questions_answered: 0
      authorized_at: null
    progress_polling:
      last_poll: null
      poll_count: 0
      poll_history: []
      next_poll_due: null
```

### Complete State Change Example

**Before Reassignment**:
```yaml
modules_status:
  - id: "auth-core"
    name: "Core Authentication"
    status: "in-progress"
    assigned_to: "implementer-1"
    github_issue: "#42"

active_assignments:
  - agent: "implementer-1"
    agent_type: "ai"
    module: "auth-core"
    task_uuid: "task-abc123"
    status: "implementing"
    instruction_verification:
      status: "verified"
      authorized_at: "2024-01-10T08:00:00Z"
```

**After Reassignment to implementer-2**:
```yaml
modules_status:
  - id: "auth-core"
    name: "Core Authentication"
    status: "assigned"
    assigned_to: "implementer-2"
    github_issue: "#42"

active_assignments:
  - agent: "implementer-2"
    agent_type: "ai"
    module: "auth-core"
    task_uuid: "task-xyz789"
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

## 5.6 Instruction Verification Protocol Reset

When a module is reassigned, the Instruction Verification Protocol resets completely.

### Why Verification Resets

Even though the module was previously verified:
1. New agent may understand differently
2. Requirements may have evolved
3. Context from old verification is lost
4. Trust must be established fresh

### Verification Fields Reset

All instruction verification fields reset to initial state:

| Field | Reset Value |
|-------|-------------|
| `status` | `"awaiting_repetition"` |
| `repetition_received` | `false` |
| `repetition_correct` | `false` |
| `questions_asked` | `0` |
| `questions_answered` | `0` |
| `authorized_at` | `null` |

### Verification Process for New Agent

The full Instruction Verification Protocol must be executed:

1. **Assignment sent** - Message with verification request
2. **Agent repeats** - Agent sends understanding summary
3. **Orchestrator verifies** - Check understanding is correct
4. **Questions asked** - Agent asks clarifying questions
5. **Questions answered** - Orchestrator provides answers
6. **Authorization** - Orchestrator authorizes implementation

### No Shortcuts

There are no shortcuts for reassigned modules:
- Cannot skip verification because "it was verified before"
- Cannot assume new agent understands
- Full protocol required every time

### Verification After Reassignment Example

**Step 1**: New agent receives assignment message

**Step 2**: New agent responds:
```markdown
## My Understanding

1. Implement JWT-based authentication with 24h expiry
2. Support refresh token mechanism
3. Session tokens for web clients
4. API key support for service accounts

## Questions

1. Should refresh tokens have a longer expiry?
2. Is there an existing database schema for users?

Ready to confirm understanding after questions answered.
```

**Step 3**: Orchestrator answers questions and verifies understanding

**Step 4**: Orchestrator authorizes:
```markdown
Your understanding is correct.

Answers:
1. Yes, refresh tokens should have 7-day expiry
2. Yes, see schema in docs/database.md

You are authorized to begin implementation.
```

---

## Reassignment Command Reference

### Usage

```bash
/reassign-module <MODULE_ID> --to <NEW_AGENT_ID>
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| MODULE_ID | Yes | ID of module to reassign |
| --to | Yes | ID of the new agent |

### Complete Example

**Command**:
```bash
/reassign-module auth-core --to implementer-2
```

**Output**:
```
Notified old agent: implementer-1
Notified new agent: implementer-2

Reassigned module 'auth-core'
  From: implementer-1
  To: implementer-2
  New UUID: task-xyz789ghij012

IMPORTANT: Execute Instruction Verification Protocol with new agent
```

---

## Related Commands

| Command | When to Use |
|---------|-------------|
| `/assign-module` | Initial assignment (not reassignment) |
| `/check-agents` | Monitor agent progress before deciding |
| `/modify-module` | Change specs, not agent |
| `/orchestration-status` | View current assignments |
