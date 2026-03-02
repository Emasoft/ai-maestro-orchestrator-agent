# Agent Registration Reference

This document describes how to register AI agents and human developers for module assignment.

---

## Contents

- 3.1 Registering AI Agents
  - 3.1.1 Required information
  - 3.1.2 Session name requirements
  - 3.1.3 Verifying session is active
- 3.2 Registering Human Developers
  - 3.2.1 GitHub username matching
  - 3.2.2 GitHub Project integration
- 3.3 Registration Rules
  - 3.3.1 User-provided only rule
  - 3.3.2 No auto-discovery rule
- 3.4 State File Updates
- 3.5 Registration Validation
- 3.6 Deregistering Agents

---

## 3.1 Registering AI Agents

AI agents are independent Claude Code sessions that receive tasks via AI Maestro messaging system.

### 3.1.1 Required Information

To register an AI agent, you need:

| Information | Description | Example |
|-------------|-------------|---------|
| Agent ID | Unique identifier for this agent | `implementer-1` |
| Session Name | AI Maestro session name | `helper-agent-generic` |

**Command**:
```bash
/register-agent ai <AGENT_ID> --session <SESSION_NAME>
```

**Example**:
```bash
/register-agent ai implementer-1 --session helper-agent-generic
```

### 3.1.2 Session Name Requirements

The session name must match an active AI Maestro session.

**Session naming convention**: `domain-subdomain-name`

| Session Name | Domain | Subdomain | Name |
|--------------|--------|-----------|------|
| `helper-agent-generic` | helper | agent | generic |
| `helper-agent-python` | helper | agent | python |
| `libs-svg-svgbbox` | libs | svg | svgbbox |

**Important**: Use the FULL session name, not aliases or short names.

### 3.1.3 Verifying Session is Active

Before registering, verify the session exists and is active:

Use the `agent-messaging` skill to query the agent registry and verify whether the session (e.g., `helper-agent-generic`) exists and is active.

**Verify**: confirm the agent is listed and active in the registry.

If the session doesn't exist:
1. Ask the user to start the session
2. Do NOT register until session is confirmed active
3. Wait for user confirmation before proceeding

---

## 3.2 Registering Human Developers

Human developers receive assignments via GitHub (Issues, Projects, PR assignments).

### 3.2.1 GitHub Username Matching

The agent ID should match the developer's GitHub username:

**Command**:
```bash
/register-agent human <GITHUB_USERNAME>
```

**Example**:
```bash
/register-agent human dev-alice
```

**Why match GitHub username?**
- Enables automatic issue assignment
- Links PRs to developer
- Enables @mentions in comments

### 3.2.2 GitHub Project Integration

When a human developer is registered:

1. Verify they have access to the GitHub repository
2. Verify they're a member of the GitHub Project (if using Projects)
3. Their assigned issues will appear in their GitHub notifications

---

## 3.3 Registration Rules

### 3.3.1 User-Provided Only Rule

**CRITICAL**: Only register agents that the user explicitly provides.

**DO**:
```
User: "Register helper-agent-generic as an implementer"
You: /register-agent ai implementer-1 --session helper-agent-generic
```

**DO NOT**:
```
You: "I'll scan AI Maestro for available agents and register them all"
```

**Rationale**: The user controls which agents are available for work. Some sessions may be:
- Reserved for other projects
- Running long tasks
- Not suitable for this project
- Personal sessions not to be disturbed

### 3.3.2 No Auto-Discovery Rule

**CRITICAL**: Do NOT automatically discover and register agents.

**Forbidden actions**:
- Scanning AI Maestro for all active sessions
- Automatically registering all found sessions
- Assuming any session is available for work

**Correct behavior**:
1. Wait for user to specify agents
2. Register only specified agents
3. Confirm registration with user

---

## 3.4 State File Updates

When an agent is registered, update the state file:

### AI Agent Registration

```yaml
registered_agents:
  ai_agents:
    - agent_id: "implementer-1"
      session_name: "helper-agent-generic"
      registered_at: "2026-01-08T15:00:00+00:00"
      assigned_by_user: true
      status: "available"  # available, busy, offline
      current_assignment: null
      assignments_completed: 0
```

### Human Developer Registration

```yaml
registered_agents:
  human_developers:
    - agent_id: "dev-alice"
      github_username: "dev-alice"
      registered_at: "2026-01-08T15:00:00+00:00"
      assigned_by_user: true
      status: "available"
      current_assignment: null
      assignments_completed: 0
```

---

## 3.5 Registration Validation

Before completing registration, validate:

### AI Agent Validation

| Check | How to Verify | Action if Failed |
|-------|---------------|------------------|
| Session exists | Query AI Maestro API | Ask user to start session |
| Session active | Check agent status | Ask user to activate |
| Agent ID unique | Check state file | Reject with error |
| Valid session name | Match naming convention | Warn but allow |

### Human Developer Validation

| Check | How to Verify | Action if Failed |
|-------|---------------|------------------|
| GitHub user exists | Query GitHub API | Reject with error |
| Has repo access | Check collaborators | Ask user to grant access |
| Agent ID unique | Check state file | Reject with error |

---

## 3.6 Deregistering Agents

To remove an agent from the registry:

**Note**: This is typically done manually by editing the state file. There is no `/deregister-agent` command.

**When to deregister**:
- Agent session no longer available
- Developer left the team
- User requests removal
- Agent consistently unresponsive

**Deregistration process**:
1. Ensure agent has no active assignments
2. If active assignment: reassign first
3. Remove from state file
4. Confirm removal to user

---

## Examples

### Example 1: Register AI Agent

```
User: "I have helper-agent-generic available for tasks"

You: I'll register helper-agent-generic as an AI agent.

/register-agent ai implementer-1 --session helper-agent-generic

Registered:
- Agent ID: implementer-1
- Type: AI
- Session: helper-agent-generic
- Status: Available

This agent can now receive module assignments via /assign-module.
```

### Example 2: Register Multiple AI Agents

```
User: "Register helper-agent-generic and helper-agent-python"

You: I'll register both agents.

/register-agent ai implementer-1 --session helper-agent-generic
/register-agent ai implementer-2 --session helper-agent-python

Registered 2 AI agents:
1. implementer-1 (helper-agent-generic)
2. implementer-2 (helper-agent-python)

Both agents are now available for module assignment.
```

### Example 3: Register Human Developer

```
User: "Alice (GitHub: alice-dev) will help with the frontend"

You: I'll register Alice as a human developer.

/register-agent human alice-dev

Registered:
- Agent ID: alice-dev
- Type: Human
- GitHub: alice-dev
- Status: Available

Alice will receive assignments via GitHub issue assignment and notifications.
```
