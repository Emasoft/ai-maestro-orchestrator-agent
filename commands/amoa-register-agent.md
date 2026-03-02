---
name: eoa-register-agent
description: "Register a remote agent (AI or human) for module assignment"
argument-hint: "<TYPE> <AGENT_ID> [--session NAME]"
allowed-tools: ["Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/eoa_register_agent.py:*)"]
---

# Register Agent Command

Register a remote agent that will be assigned modules during Orchestration Phase. Only registered agents can receive module assignments.

## Usage

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_register_agent.py" $ARGUMENTS
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `TYPE` | Yes | Agent type: `ai` or `human` |
| `AGENT_ID` | Yes | Unique identifier for the agent |
| `--session` | No | AI Maestro session name (for AI agents) |

## Registering an AI Agent

```
/register-agent ai implementer-1 --session helper-agent-generic
```

This registers:
- Agent ID: `implementer-1`
- Type: AI (communicates via AI Maestro)
- Session: `helper-agent-generic`

## Registering a Human Developer

```
/register-agent human dev-alice
```

This registers:
- Agent ID: `dev-alice` (should match GitHub username)
- Type: Human (communicates via GitHub)

## Agent Types Explained

### AI Agents
- Independent Claude Code sessions
- Receive tasks via AI Maestro messages
- Must be provided by user (not auto-discovered)
- Require Instruction Verification Protocol

### Human Developers
- Assigned via GitHub Project Kanban
- Receive notifications via GitHub
- Track progress via PR/Issue updates

## State File Update

```yaml
registered_agents:
  ai_agents:
    - agent_id: "implementer-1"
      session_name: "helper-agent-generic"
      assigned_by_user: true
  human_developers:
    - github_username: "dev-alice"
      assigned_by_user: true
```

## Important Rules

1. **User-Provided Only**: Only register agents explicitly provided by the user
2. **No Auto-Discovery**: Do NOT register all AI Maestro agents automatically
3. **Verify Existence**: For AI agents, verify session is active before assignment
4. **GitHub Match**: For humans, agent ID should match GitHub username

## Examples

```bash
# Register AI agent with specific session
/register-agent ai implementer-1 --session helper-agent-generic

# Register multiple AI agents
/register-agent ai implementer-2 --session helper-agent-python

# Register human developer
/register-agent human dev-alice

# Register another human
/register-agent human dev-bob
```

## Related Commands

- `/orchestration-status` - View registered agents
- `/assign-module` - Assign module to agent
- `/check-agents` - Poll agent progress
