# Orchestration Phase Workflow

## Contents

- 1. Entering Orchestration Phase
  - 1.1 Using /start-orchestration command
  - 1.2 State file structure
- 2. Agent Registration
  - 2.1 Registering AI agents with /register-agent
  - 2.2 Registering human developers
  - 2.3 Agent types and differences
- 3. Module Assignment
  - 3.1 Assigning modules with /assign-module
  - 3.2 Reassigning modules with /reassign-module
- 4. Monitoring Progress
  - 4.1 Using /orchestration-status
  - 4.2 Using /check-agents for polling
- 5. Modifying During Orchestration
  - 5.1 Adding modules with /add-module
  - 5.2 Modifying modules with /modify-module
  - 5.3 Removing modules with /remove-module
  - 5.4 Prioritizing with /prioritize-module
- 6. Completion and Exit
  - 6.1 All modules complete criteria
  - 6.2 4-verification loops requirement
  - 6.3 Stop hook enforcement

---

## 1. Entering Orchestration Phase

### 1.1 Using /start-orchestration command

After plan approval, run:

```
/start-orchestration
```

**Prerequisites:**
- Plan Phase must be complete (`plan_phase_complete: true`)
- All modules must have GitHub Issues created

The command:
1. Creates orchestration phase state file
2. Copies modules from plan with GitHub issue links
3. Initializes agent registry
4. Sets status to "executing"

### 1.2 State file structure

Creates `design/state/exec-phase.md`:

```yaml
---
phase: "orchestration"
plan_id: "plan-20260108-143022"
status: "executing"
started_at: "ISO timestamp"

plan_file: "design/state/plan-phase.md"
requirements_file: "USER_REQUIREMENTS.md"

current_module: null
modules_status:
  - id: "auth-core"
    name: "Core Authentication"
    status: "pending"
    assigned_to: null
    github_issue: "#42"
    pr: null
    verification_loops: 0

registered_agents:
  ai_agents: []
  human_developers: []

active_assignments: []

modules_completed: 0
modules_total: 2
all_modules_complete: false
verification_mode: false
verification_loops_remaining: 0
---
```

---

## 2. Agent Registration

### 2.1 Registering AI agents with /register-agent

```
/register-agent ai helper-agent-generic
```

Parameters:
- `ai` - Agent type (ai or human)
- `helper-agent-generic` - Session name on AI Maestro

This adds to the registry:

```yaml
registered_agents:
  ai_agents:
    - agent_id: "implementer-1"
      session_name: "helper-agent-generic"
      assigned_by_user: true
      registered_at: "ISO timestamp"
```

### 2.2 Registering human developers

```
/register-agent human dev-alice
```

This adds:

```yaml
registered_agents:
  human_developers:
    - github_username: "dev-alice"
      assigned_by_user: true
      registered_at: "ISO timestamp"
```

### 2.3 Agent types and differences

| Agent Type | Implementation | Communication | Tracking |
|------------|----------------|---------------|----------|
| **Local Subagents** | NO CODE - analysis only | Task tool | Direct results |
| **Remote AI Agents** | DO CODE | AI Maestro messages | Via polls |
| **Human Developers** | DO CODE | GitHub notifications | Via GitHub |

**Critical:** Only agents explicitly registered by user are involved. The orchestrator does NOT contact arbitrary AI Maestro agents.

---

## 3. Module Assignment

### 3.1 Assigning modules with /assign-module

```
/assign-module auth-core implementer-1
```

This:
1. Creates active assignment record
2. Generates task UUID for tracking
3. Updates module status to "assigned"
4. **Triggers Instruction Verification Protocol**

Assignment record:

```yaml
active_assignments:
  - agent: "implementer-1"
    agent_type: "ai"
    module: "auth-core"
    github_issue: "#42"
    task_uuid: "task-uuid-12345"
    status: "awaiting_verification"
    instruction_verification:
      status: "pending"
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

### 3.2 Reassigning modules with /reassign-module

```
/reassign-module auth-core --to implementer-2
```

**Restrictions:**
- Only for modules with status "pending", "assigned", or "blocked"
- Cannot reassign "in-progress" or "complete" modules

Actions:
1. Notifies old agent (if AI) to stop work
2. Updates assignment to new agent
3. Resets instruction verification status
4. Notifies new agent with assignment

---

## 4. Monitoring Progress

### 4.1 Using /orchestration-status

```
/orchestration-status
```

Shows:
- Module completion progress
- Active assignments with status
- Verification status per agent
- Poll history summary
- Blocking issues

**Output example:**
```
Orchestration Status
====================
Plan ID: plan-20260108-143022
Status: executing

Modules: 1/3 complete
  [x] auth-core - Complete (PR #45 merged)
  [ ] oauth-google - In Progress (implementer-1)
  [ ] user-profile - Pending

Active Assignments:
  implementer-1 -> oauth-google
    Status: working
    Verification: verified
    Last poll: 5 min ago
    Issues reported: 0

Next poll due: 10 min
```

### 4.2 Using /check-agents for polling

```
/check-agents
```

Sends progress polls to ALL active AI agents with the **6 mandatory questions**.

See [Proactive Progress Polling Protocol](proactive-progress-polling.md) for details.

---

## 5. Modifying During Orchestration

### 5.1 Adding modules with /add-module

```
/add-module "Password Reset Flow" --priority high
```

Actions:
1. Creates GitHub Issue for new module
2. Adds to modules_status with "pending"
3. Increments modules_total
4. Stop hook now includes this module

### 5.2 Modifying modules with /modify-module

```
/modify-module auth-core --add-criteria "Support remember-me checkbox"
```

Actions:
1. Updates module acceptance criteria
2. Updates GitHub Issue
3. If assigned, notifies agent of spec change

### 5.3 Removing modules with /remove-module

```
/remove-module legacy-migration
```

**Restriction:** Only for modules with status "pending" (not started)

Actions:
1. Closes GitHub Issue
2. Removes from modules_status
3. Decrements modules_total
4. Stop hook no longer tracks this module

### 5.4 Prioritizing with /prioritize-module

```
/prioritize-module oauth-google --priority critical
```

Actions:
1. Updates module priority
2. Updates GitHub Issue labels
3. May trigger reassignment suggestions

---

## 6. Completion and Exit

### 6.1 All modules complete criteria

A module is "complete" when:
1. Implementation merged to main branch
2. All acceptance criteria verified
3. PR passed code review
4. All tests passing

All modules complete when:
- `modules_completed == modules_total`
- `all_modules_complete: true` in state file

### 6.2 4-verification loops requirement

After all modules complete, orchestration enters verification mode:

```yaml
all_modules_complete: true
verification_mode: true
verification_loops_remaining: 4
```

Each verification loop:
1. Orchestrator reviews all merged code
2. Runs full test suite
3. Checks for regressions
4. Decrements `verification_loops_remaining`

Exit allowed only when `verification_loops_remaining: 0`.

### 6.3 Stop hook enforcement

The stop hook blocks exit if:
- Any module status != "complete"
- `verification_loops_remaining > 0`
- Active assignments still pending

**Message shown:**
```
Orchestration Phase incomplete. Cannot exit.

Modules: 2/3 complete
  [ ] oauth-google - In Progress

1 active assignment remaining.

Run /orchestration-status for details.
```

---

## Dynamic Modification Flow

```
Before adding module:
  Modules: [A: done, B: in-progress]
  Pending: 1
  Stop hook blocks: "1 module remaining"

User: /add-module "Feature C"

After adding module:
  Modules: [A: done, B: in-progress, C: pending]
  Pending: 2
  Stop hook blocks: "2 modules remaining"

User: /remove-module "Feature C"

After removing module:
  Modules: [A: done, B: in-progress]
  Pending: 1
  Stop hook blocks: "1 module remaining"
```

**Key insight:** Stop hook always checks CURRENT state. Modifications are immediately reflected in completion requirements.
