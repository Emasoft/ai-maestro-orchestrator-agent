# Orchestration API Commands

## Table of Contents

- 1. AI Maestro Messaging for Remote Agents
  - 1.1 When to use AI Maestro vs Task tool
  - 1.2 Sending task assignments to remote agents
  - 1.3 Message types for EOA
- 2. Claude Code Tasks API
  - 2.1 When to use TaskCreate, TaskUpdate, TaskList
  - 2.2 Creating tasks with success criteria
  - 2.3 Task lifecycle commands
  - 2.4 Task success criteria requirements

---

## 1. AI Maestro Messaging for Remote Agents

### 1.1 When to use AI Maestro vs Task tool

| Scenario | Use |
|----------|-----|
| Sub-agent in same session | Task tool |
| Remote agent in different session | AI Maestro |
| Agent on different machine | AI Maestro |

### 1.2 Sending task assignments to remote agents

Send task assignments using the `agent-messaging` skill:
- **Recipient**: the remote agent session name (e.g., `remote-dev-001`)
- **Subject**: "Task Assignment: Implement module X"
- **Content**: "Please implement..."
- **Type**: `task-assignment`, **Priority**: `high`
- **Data**: include `taskId`, `deadline`

**Verify**: confirm message delivery.

### 1.3 Message types for EOA

| Type | Use When |
|------|----------|
| `task-assignment` | Assigning new work to remote agent |
| `status-request` | Polling for progress update |
| `unblock-guidance` | Providing help for blocked agent |
| `completion-ack` | Acknowledging task completion |

---

## 2. Claude Code Tasks API

### 2.1 When to use TaskCreate, TaskUpdate, TaskList

| Command | Use When |
|---------|----------|
| `TaskCreate` | Starting new work unit |
| `TaskUpdate` | Changing task status |
| `TaskList` | Checking overall progress |

### 2.2 Creating tasks with success criteria

Every task MUST have unambiguous completion conditions:

```
TaskCreate(
  subject="Implement module X",
  description="Full requirements here. Success criteria:
    - [ ] Unit tests pass
    - [ ] Linting passes
    - [ ] Documentation updated",
  activeForm="Implementing module X"
)
```

### 2.3 Task lifecycle commands

**Create a task:**
```
TaskCreate(
  subject="Implement module X",
  description="Full requirements here",
  activeForm="Implementing module X"
)
```

**Start work:**
```
TaskUpdate(taskId="1", status="in-progress")
```

**Complete work:**
```
TaskUpdate(taskId="1", status="completed")
```

**Check overall progress:**
```
TaskList()
```

### 2.4 Task success criteria requirements

- Every task MUST have unambiguous completion conditions
- Use checkboxes in description for verifiable criteria
- Include test requirements if applicable
- Agent cannot mark complete until all criteria met
