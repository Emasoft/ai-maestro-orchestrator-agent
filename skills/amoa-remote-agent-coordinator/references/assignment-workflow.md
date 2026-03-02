# Assignment Workflow Reference

This document describes the complete workflow for assigning modules to registered agents.

---

## Contents

- 5.1 Pre-Assignment Validation
  - 5.1.1 Module exists and is pending
  - 5.1.2 Agent is registered
  - 5.1.3 Agent is not overloaded
- 5.2 Assignment Record Creation
  - 5.2.1 Task UUID generation
  - 5.2.2 Initial status values
- 5.3 Assignment Message Generation
- 5.4 State File Updates
- 5.5 Post-Assignment Workflow
- 5.6 Assignment Errors and Recovery

---

## 5.1 Pre-Assignment Validation

Before assigning a module, the system validates several conditions.

### 5.1.1 Module Exists and is Pending

**Check**: The module ID must exist in the decomposed modules list.

```yaml
# Valid - module exists and is pending
modules:
  auth-core:
    status: "pending"

# Invalid - module doesn't exist
modules:
  # auth-core not found

# Invalid - module already assigned
modules:
  auth-core:
    status: "in-progress"
    assigned_to: "implementer-2"
```

**Error if failed**:
```
Error: Module 'auth-core' not found in decomposed modules.
Available modules: oauth-google, session-manager, api-gateway
```

### 5.1.2 Agent is Registered

**Check**: The agent ID must exist in registered agents.

```yaml
# Valid - agent is registered
registered_agents:
  ai_agents:
    - agent_id: "implementer-1"
      session_name: "helper-agent-generic"
```

**Error if failed**:
```
Error: Agent 'implementer-1' is not registered.
Registered agents: implementer-2, dev-alice
Use /register-agent to register the agent first.
```

### 5.1.3 Agent is Not Overloaded

**Check**: The agent doesn't have too many active assignments.

Default limits:
- AI agents: 1 active assignment
- Human developers: 2-3 active assignments

```yaml
# Valid - agent is available
registered_agents:
  ai_agents:
    - agent_id: "implementer-1"
      status: "available"
      current_assignment: null

# Invalid - agent is busy
registered_agents:
  ai_agents:
    - agent_id: "implementer-1"
      status: "busy"
      current_assignment: "oauth-google"
```

**Error if failed**:
```
Error: Agent 'implementer-1' already has an active assignment (oauth-google).
Wait for completion or use /reassign-module to change assignment.
```

---

## 5.2 Assignment Record Creation

### 5.2.1 Task UUID Generation

Each assignment gets a unique task UUID for tracking:

```python
import uuid
task_uuid = f"task-{uuid.uuid4().hex[:8]}"
# Example: task-a1b2c3d4
```

**Why task UUIDs?**
- Unique identifier across all assignments
- Enables tracking in logs and messages
- Links messages to specific assignments
- Supports audit trail

### 5.2.2 Initial Status Values

New assignment record:

```yaml
active_assignments:
  - agent: "implementer-1"
    agent_type: "ai"
    module: "auth-core"
    github_issue: "#42"
    task_uuid: "task-a1b2c3d4"
    assigned_at: "2026-01-08T16:00:00+00:00"
    status: "pending_verification"
    instruction_verification:
      status: "awaiting_repetition"
      repetition_received: false
      repetition_correct: false
      questions_asked: 0
      questions_answered: 0
      authorized_at: null
    progress:
      percentage: 0
      last_update: null
      notes: []
    polling:
      poll_count: 0
      last_poll: null
      next_poll_due: null
```

---

## 5.3 Assignment Message Generation

### AI Agent Assignment Message

For AI agents, generate and send via AI Maestro:

```markdown
Subject: [TASK] Module: auth-core - UUID: task-a1b2c3d4

## Assignment

You have been assigned to implement: **auth-core**

GitHub Issue: https://github.com/org/repo/issues/42
Task UUID: task-a1b2c3d4

## Module Description

JWT token generation and validation for user authentication.

## Requirements Summary

1. Implement JWT token generation using RS256 algorithm
2. Token payload must include: user_id, role, exp, iat
3. Token expiry: 24 hours (configurable)
4. Implement token validation function
5. Handle expired tokens with clear error messages

## Acceptance Criteria

- [ ] generate_token(user_id, role) returns valid JWT
- [ ] validate_token(token) returns user info or raises error
- [ ] Expired tokens raise TokenExpiredError
- [ ] Unit tests with >90% coverage
- [ ] Integration test with mock user data

## Dependencies

- None (this is a leaf module)

## Estimated Effort

2-3 hours

## MANDATORY: Instruction Verification

Before you begin implementation, please:

1. **Repeat the key requirements** in your own words (3-5 bullet points)
2. **List any questions** you have about the requirements
3. **Confirm your understanding** of the acceptance criteria

I will verify your understanding before authorizing implementation.

Reply with your understanding summary.
```

### Human Developer Assignment

For human developers, update GitHub issue:

```bash
# Assign issue
gh issue edit 42 --add-assignee dev-alice

# Add comment
gh issue comment 42 --body "Assigned to @dev-alice. Please review the requirements and confirm understanding before starting."

# Update labels
gh issue edit 42 --add-label "in-progress,assigned"
```

---

## 5.4 State File Updates

After assignment, update the state file:

### Module Status Update

```yaml
modules:
  auth-core:
    status: "assigned"
    assigned_to: "implementer-1"
    assigned_at: "2026-01-08T16:00:00+00:00"
    task_uuid: "task-a1b2c3d4"
```

### Agent Status Update

```yaml
registered_agents:
  ai_agents:
    - agent_id: "implementer-1"
      status: "busy"
      current_assignment: "auth-core"
      current_task_uuid: "task-a1b2c3d4"
```

### Active Assignments Update

```yaml
active_assignments:
  - agent: "implementer-1"
    module: "auth-core"
    task_uuid: "task-a1b2c3d4"
    status: "pending_verification"
    # ... full record as shown above
```

---

## 5.5 Post-Assignment Workflow

After sending the assignment:

### Step 1: Wait for Understanding Response

Expected within 5-10 minutes for AI agents.

### Step 2: Verify Understanding

See: [instruction-verification-protocol.md](instruction-verification-protocol.md)

### Step 3: Answer Questions

Respond to any questions the agent has.

### Step 4: Authorize Implementation

Update status to "in-progress" and send authorization.

### Step 5: Begin Progress Polling

Set up polling schedule:

```yaml
polling:
  poll_count: 0
  last_poll: null
  next_poll_due: "2026-01-08T16:15:00+00:00"  # 15 min after authorization
  frequency: "15min"
```

### Step 6: Monitor Until Completion

See: [progress-polling-protocol.md](progress-polling-protocol.md)

---

## 5.6 Assignment Errors and Recovery

### Error: Module Already Assigned

```
Error: Module 'auth-core' is already assigned to 'implementer-2'.
```

**Recovery options**:
1. Wait for current assignment to complete
2. Use `/reassign-module auth-core implementer-1` to reassign
3. Check if this is a duplicate request

### Error: Agent Busy

```
Error: Agent 'implementer-1' is busy with 'oauth-google'.
```

**Recovery options**:
1. Assign to different agent
2. Wait for current task to complete
3. Reassign current task to another agent

### Error: Message Delivery Failed

```
Error: Failed to deliver assignment message to 'implementer-1'.
AI Maestro error: Session not found.
```

**Recovery options**:
1. Verify session is running
2. Ask user to start the session
3. Try alternative communication method
4. Assign to different agent

### Error: GitHub API Failed

```
Error: Failed to assign GitHub issue #42.
GitHub error: User 'dev-alice' is not a collaborator.
```

**Recovery options**:
1. Add user as collaborator
2. Verify GitHub credentials
3. Check repository permissions
4. Use manual assignment

---

## Summary

The assignment workflow ensures:

1. **Validation** - Module exists, agent available
2. **Tracking** - Unique UUID, state updates
3. **Communication** - Assignment message sent
4. **Verification** - Understanding confirmed before work
5. **Monitoring** - Progress polling established

Always follow the complete workflow. Do not skip validation or verification steps.
