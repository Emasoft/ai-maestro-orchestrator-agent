# Agent Management Commands Reference

This document describes the CLI commands for managing remote agents (registration, assignment, progress polling).

---

## Contents

- 1.0 Overview
- 2.0 Command 1: /register-agent
  - 2.1 Syntax
  - 2.2 Arguments
  - 2.3 Examples
  - 2.4 Behavior
- 3.0 Command 2: /assign-module
  - 3.1 Syntax
  - 3.2 Arguments
  - 3.3 Examples
  - 3.4 Post-Assignment Workflow
- 4.0 Command 3: /check-agents
  - 4.1 Syntax
  - 4.2 Options
  - 4.3 Examples
  - 4.4 The 6 Mandatory Questions
  - 4.5 Response Action Matrix

---

## 1.0 Overview

The agent management system provides three core commands for coordinating remote agents:

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/register-agent` | Add agent to registry | Before assigning any modules |
| `/assign-module` | Assign module to agent | After decomposition, when agent is registered |
| `/check-agents` | Poll progress | Every 10-15 minutes during implementation |

---

## 2.0 Command 1: /register-agent

Register a remote agent (AI or human) before assigning modules.

### 2.1 Syntax

```
/register-agent <TYPE> <AGENT_ID> [--session NAME]
```

### 2.2 Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `TYPE` | Yes | `ai` or `human` |
| `AGENT_ID` | Yes | Unique identifier |
| `--session` | No | AI Maestro session name (AI agents only) |

### 2.3 Examples

```bash
# Register AI agent
/register-agent ai implementer-1 --session helper-agent-generic

# Register human developer
/register-agent human dev-alice
```

### 2.4 Behavior

When you run `/register-agent`:

1. **Validation checks run**:
   - Agent type is valid (`ai` or `human`)
   - Agent ID is unique (not already registered)
   - For AI agents: session name is provided and active in AI Maestro
   - For human developers: GitHub username matches a repository collaborator

2. **State file updates**:
   - Agent added to `design/agents.yaml`
   - Status set to `available`
   - Capabilities recorded

3. **Verification**:
   - For AI agents: AI Maestro session verified
   - For human developers: GitHub API verified

**See also**:
- [agent-registration-commands.md](agent-registration-commands.md) - Detailed registration workflow
- [agent-types.md](agent-types.md) - AI vs human agent differences

---

## 3.0 Command 2: /assign-module

Assign a module to a registered agent and initiate verification.

### 3.1 Syntax

```
/assign-module <MODULE_ID> <AGENT_ID>
```

### 3.2 Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `MODULE_ID` | Yes | ID of the module to assign |
| `AGENT_ID` | Yes | ID of the registered agent |

### 3.3 Examples

```bash
# Assign to AI agent
/assign-module auth-core implementer-1

# Assign to human developer
/assign-module oauth-google dev-alice
```

### 3.4 Post-Assignment Workflow

After running `/assign-module`:

1. **Validation checks run**:
   - Module exists and is pending
   - Agent is registered
   - Agent is not overloaded

2. **Assignment record created**:
   - Task UUID generated
   - Initial status: `pending_verification`

3. **Assignment message sent**:
   - AI agents: via AI Maestro
   - Human developers: via GitHub issue assignment

4. **YOU MUST execute Instruction Verification Protocol**:
   - Wait for agent to repeat requirements
   - Verify understanding is correct
   - Answer all questions
   - Authorize implementation

5. **YOU MUST begin progress polling**:
   - Poll every 10-15 minutes with `/check-agents`

**See also**:
- [assignment-workflow.md](assignment-workflow.md) - Complete assignment flow
- [instruction-verification-protocol.md](instruction-verification-protocol.md) - 8-step verification
- [github-assignment-workflow.md](github-assignment-workflow.md) - Human developer workflow

---

## 4.0 Command 3: /check-agents

Poll all active agents for progress with mandatory questions.

### 4.1 Syntax

```
/check-agents [--agent AGENT_ID]
```

### 4.2 Options

| Option | Description |
|--------|-------------|
| `--agent` | Poll only a specific agent |

### 4.3 Examples

```bash
# Poll all active agents
/check-agents

# Poll specific agent
/check-agents --agent implementer-1
```

### 4.4 The 6 Mandatory Questions

**EVERY poll MUST include these questions. Non-negotiable.**

1. **Current progress** (% complete, what's done)
2. **Next steps** (what you're working on now)
3. **Are there any issues or problems?**
4. **Is anything unclear?**
5. **Any unforeseen difficulties?**
6. **Do you need anything from me?**

**Why these questions matter**:
- Questions 1-2: Track progress and direction
- Questions 3-5: Surface blockers before they become critical
- Question 6: Identify how orchestrator can help

### 4.5 Response Action Matrix

| Agent Response | Orchestrator Action |
|----------------|---------------------|
| Reports issue | Provide solution or delegate research |
| Something unclear | Provide clarification immediately |
| Unforeseen difficulty | Evaluate: adapt approach or reassign |
| Needs documentation | Create/provide detailed docs |
| Needs decision | Make decision or escalate to user |
| Blocked | Unblock immediately (highest priority) |

**See also**:
- [progress-polling-protocol.md](progress-polling-protocol.md) - Complete polling protocol
- [agent-communication-templates.md](agent-communication-templates.md) - Poll message templates

---

## Typical Workflow

```
1. User provides agent information
   ↓
2. /register-agent ai implementer-1 --session helper-agent-generic
   ↓
3. Module decomposition complete (separate skill)
   ↓
4. /assign-module auth-core implementer-1
   ↓
5. [MANDATORY] Instruction Verification Protocol
   - Wait for agent to repeat requirements
   - Verify understanding is correct
   - Answer all questions
   - Authorize implementation
   ↓
6. [MANDATORY] Progress Polling (every 10-15 min)
   - /check-agents
   - Ask 6 mandatory questions
   - Respond to issues immediately
   ↓
7. Agent reports completion
   ↓
8. Verify deliverables (separate skill)
```

---

## Integration with State Files

All commands interact with YAML state files in `design/`:

| File | Purpose |
|------|---------|
| `design/agents.yaml` | Registered agents |
| `design/assignments.yaml` | Active assignments |
| `design/verification_status.yaml` | Verification tracking |
| `design/logs/polls/` | Progress poll logs |

---

## Error Handling

**See**:
- [agent-management-troubleshooting.md](agent-management-troubleshooting.md) - Common issues and solutions

---

## Summary

The 3 commands provide a complete agent management workflow:

1. **Register** - Add agents before use
2. **Assign** - Delegate modules with verification
3. **Poll** - Monitor progress proactively

Always follow the complete workflow. Do not skip verification or polling steps.
