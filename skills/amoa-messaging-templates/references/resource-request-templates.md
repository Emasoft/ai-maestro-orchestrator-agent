# Resource and Skill Request Templates

Templates for agents requesting resources or capabilities from EOA, and the formal JSON format for EOA acknowledging ECOS task assignments. Use the `agent-messaging` skill for all message operations.

## Table of Contents

- [1. Agent Resource Request (Agent to EOA)](#1-agent-resource-request-agent-to-eoa)
- [2. EOA Resource Response (EOA to Agent)](#2-eoa-resource-response-eoa-to-agent)
- [3. Agent Skill/Capability Request (Agent to EOA)](#3-agent-skillcapability-request-agent-to-eoa)
- [4. EOA Skill Response (EOA to Agent)](#4-eoa-skill-response-eoa-to-agent)
- [5. EOA Formal ACK of ECOS Task Assignment (EOA to ECOS)](#5-eoa-formal-ack-of-ecos-task-assignment-eoa-to-ecos)
- [6. Resource Request Decision Tree](#6-resource-request-decision-tree)

---

## 1. Agent Resource Request (Agent to EOA)

**When to use:** An agent (implementer, tester, or any sub-agent) needs a resource it does not currently have access to. A "resource" is any tool, file access permission, credential, or external service that the agent cannot obtain on its own. Examples include: access to a private repository, a database credential, a specific CLI tool not installed in the agent's environment, or access to an external API service.

> **Note**: Use the agent-messaging skill to send messages. The JSON structure below shows the message content.

**Send template:**

```json
{
  "from": "<agent-session-name>",
  "to": "eoa-<project-name>",
  "subject": "Resource Request: <resource-name>",
  "priority": "high",
  "content": {
    "type": "request",
    "message": "Requesting access to <resource-name>. Type: <resource-type>. Justification: <why-needed>. Urgency: <blocking|non-blocking>.",
    "data": {
      "task_uuid": "<uuid-of-current-task>",
      "resource_type": "<tool|access|credentials|service>",
      "resource_name": "<human-readable-resource-name>",
      "justification": "<why-this-resource-is-needed-for-the-task>",
      "urgency": "<blocking|non-blocking>"
    }
  }
}
```

**Field definitions:**

| Field | Type | Description |
|-------|------|-------------|
| `resource_type` | String | One of: `tool` (CLI tool, binary, package), `access` (file system, repository, directory permission), `credentials` (API key, token, password), `service` (external API, database, cloud service) |
| `resource_name` | String | Human-readable name of the resource (e.g., "GitHub PAT for repo X", "PostgreSQL credentials", "ffmpeg CLI tool") |
| `justification` | String | Explanation of why the resource is needed to complete the assigned task |
| `urgency` | String | `blocking` means the agent cannot continue any work without this resource. `non-blocking` means the agent can continue other parts of the task while waiting |

**Priority rules:**
- Use `high` when `urgency` is `blocking`
- Use `normal` when `urgency` is `non-blocking`

---

## 2. EOA Resource Response (EOA to Agent)

**When to use:** EOA has evaluated an agent's resource request and is responding with the decision. EOA evaluates the request based on three possible outcomes: granted, denied, or escalated.

> **Note**: Use the agent-messaging skill to send messages. The JSON structure below shows the message content.

### 2.1 Resource Granted

**When to use:** EOA has the authority to grant the resource and the resource is available.

```json
{
  "from": "eoa-<project-name>",
  "to": "<agent-session-name>",
  "subject": "Resource Granted: <resource-name>",
  "priority": "normal",
  "content": {
    "type": "response",
    "message": "Resource granted: <resource-name>. Access details provided in data field. Proceed with your task.",
    "data": {
      "task_uuid": "<uuid>",
      "decision": "granted",
      "resource_name": "<resource-name>",
      "access_details": "<how-to-access-the-resource>",
      "expiry": "<ISO8601-or-null>"
    }
  }
}
```

### 2.2 Resource Denied

**When to use:** The resource cannot be provided and no workaround exists, or the request is outside policy.

```json
{
  "from": "eoa-<project-name>",
  "to": "<agent-session-name>",
  "subject": "Resource Denied: <resource-name>",
  "priority": "normal",
  "content": {
    "type": "response",
    "message": "Resource denied: <resource-name>. Reason: <denial-reason>. Alternative: <alternative-or-none>.",
    "data": {
      "task_uuid": "<uuid>",
      "decision": "denied",
      "resource_name": "<resource-name>",
      "reason": "<why-the-resource-cannot-be-provided>",
      "alternative": "<suggested-alternative-approach-or-null>"
    }
  }
}
```

### 2.3 Resource Escalated

**When to use:** The resource request is outside EOA's authority (security-sensitive credentials, cross-project access, budget-impacting services). EOA forwards the request to ECOS for approval.

```json
{
  "from": "eoa-<project-name>",
  "to": "<agent-session-name>",
  "subject": "Resource Escalated: <resource-name>",
  "priority": "normal",
  "content": {
    "type": "response",
    "message": "Resource request escalated to ECOS for approval: <resource-name>. You will be notified when a decision is made.",
    "data": {
      "task_uuid": "<uuid>",
      "decision": "escalated",
      "resource_name": "<resource-name>",
      "escalated_to": "ecos-main",
      "reason": "<why-escalation-is-needed>"
    }
  }
}
```

**EOA also sends a forwarding message to ECOS:**

```json
{
  "from": "eoa-<project-name>",
  "to": "ecos-main",
  "subject": "Resource Approval Needed: <resource-name>",
  "priority": "high",
  "content": {
    "type": "request",
    "message": "Agent <agent-session-name> requests <resource-name> (<resource-type>). Justification: <justification>. Urgency: <urgency>. Awaiting your approval.",
    "data": {
      "task_uuid": "<uuid>",
      "requesting_agent": "<agent-session-name>",
      "resource_type": "<tool|access|credentials|service>",
      "resource_name": "<resource-name>",
      "justification": "<justification>",
      "urgency": "<blocking|non-blocking>",
      "security_flag": true
    }
  }
}
```

---

## 3. Agent Skill/Capability Request (Agent to EOA)

**When to use:** An agent needs a capability that is outside its current plugin's skill set. A "capability" is a skill, workflow, or specialized knowledge that the agent's plugin does not include. Examples include: an implementer needing code review skills, a tester needing deployment capabilities, or any agent needing a domain-specific skill not loaded in its plugin.

> **Note**: Use the agent-messaging skill to send messages. The JSON structure below shows the message content.

**Send template:**

```json
{
  "from": "<agent-session-name>",
  "to": "eoa-<project-name>",
  "subject": "Skill Request: <capability-needed>",
  "priority": "high",
  "content": {
    "type": "request",
    "message": "Need capability: <capability-needed>. Current limitation: <what-I-cannot-do>. Suggested skill: <skill-name-if-known>.",
    "data": {
      "task_uuid": "<uuid-of-current-task>",
      "capability_needed": "<description-of-what-the-agent-needs-to-do>",
      "current_limitation": "<what-the-agent-cannot-do-with-its-current-skills>",
      "suggested_skill": "<skill-name-or-null-if-unknown>"
    }
  }
}
```

**Field definitions:**

| Field | Type | Description |
|-------|------|-------------|
| `capability_needed` | String | Description of what the agent needs to be able to do (e.g., "run database migrations", "perform security audit", "generate API documentation") |
| `current_limitation` | String | What the agent tried or why its current skills are insufficient (e.g., "my plugin does not include database migration skills", "I lack the security-audit skill needed for OWASP checks") |
| `suggested_skill` | String or null | If the agent knows which skill would help, provide its name (e.g., "epa-database-migration"). Set to `null` if the agent does not know which skill is needed |

---

## 4. EOA Skill Response (EOA to Agent)

**When to use:** EOA has evaluated a skill/capability request and is responding with how to proceed. EOA evaluates the request based on three possible outcomes: skill available, not available with workaround, or escalated to ECOS.

> **Note**: Use the agent-messaging skill to send messages. The JSON structure below shows the message content.

### 4.1 Skill Available

**When to use:** The requested capability exists as a globally installed skill or agent that the requesting agent can use directly.

```json
{
  "from": "eoa-<project-name>",
  "to": "<agent-session-name>",
  "subject": "Skill Available: <capability-needed>",
  "priority": "normal",
  "content": {
    "type": "response",
    "message": "Skill available: <skill-name>. Access method: <how-to-use-it>. Proceed with your task using this skill.",
    "data": {
      "task_uuid": "<uuid>",
      "decision": "skill_available",
      "skill_name": "<skill-name>",
      "access_method": "<how-to-invoke-or-use-the-skill>",
      "documentation": "<path-to-skill-docs-or-null>"
    }
  }
}
```

### 4.2 Skill Not Available (Workaround Provided)

**When to use:** The requested capability does not exist as a skill, but the task can be accomplished through an alternative approach.

```json
{
  "from": "eoa-<project-name>",
  "to": "<agent-session-name>",
  "subject": "Skill Not Available: <capability-needed>",
  "priority": "normal",
  "content": {
    "type": "response",
    "message": "Skill not available for: <capability-needed>. Workaround: <alternative-approach>. Use this approach to continue your task.",
    "data": {
      "task_uuid": "<uuid>",
      "decision": "not_available",
      "capability_needed": "<capability-needed>",
      "workaround": "<step-by-step-alternative-approach>",
      "limitations": "<any-limitations-of-the-workaround>"
    }
  }
}
```

### 4.3 Skill Escalated (Specialized Agent Needed)

**When to use:** The capability requires a specialized agent that ECOS must spawn. No workaround exists within the current agent's scope.

```json
{
  "from": "eoa-<project-name>",
  "to": "<agent-session-name>",
  "subject": "Skill Escalated: <capability-needed>",
  "priority": "normal",
  "content": {
    "type": "response",
    "message": "Capability requires specialized agent. Escalated to ECOS to spawn <suggested-agent-role>. You will be notified when the agent is available.",
    "data": {
      "task_uuid": "<uuid>",
      "decision": "escalated",
      "capability_needed": "<capability-needed>",
      "escalated_to": "ecos-main",
      "suggested_agent_role": "<role-name-e.g.-security-auditor>"
    }
  }
}
```

**EOA also sends a spawn request to ECOS:**

```json
{
  "from": "eoa-<project-name>",
  "to": "ecos-main",
  "subject": "Agent Spawn Request: <suggested-agent-role>",
  "priority": "high",
  "content": {
    "type": "request",
    "message": "Agent <agent-session-name> needs <capability-needed> which requires a specialized <suggested-agent-role> agent. Requesting spawn.",
    "data": {
      "task_uuid": "<uuid>",
      "requesting_agent": "<agent-session-name>",
      "capability_needed": "<capability-needed>",
      "suggested_agent_role": "<role-name>",
      "task_context": "<brief-description-of-the-task-requiring-this-capability>"
    }
  }
}
```

---

## 5. EOA Formal ACK of ECOS Task Assignment (EOA to ECOS)

**When to use:** EOA receives a task assignment from ECOS (as described in [ai-maestro-message-templates.md](ai-maestro-message-templates.md) section 1.1) and must send a formal JSON acknowledgment confirming receipt. This replaces the prose-style acknowledgment with a structured, machine-parseable format.

> **Note**: Use the agent-messaging skill to send messages. The JSON structure below shows the message content.

**Send template:**

```json
{
  "from": "eoa-<project-name>",
  "to": "ecos-main",
  "subject": "ACK: Task Assignment <task-name>",
  "priority": "normal",
  "content": {
    "type": "acknowledgment",
    "message": "Task received and logged. UUID: <uuid>. Expected completion: <timestamp>.",
    "data": {
      "task_uuid": "<uuid>",
      "status": "received",
      "estimated_completion": "<ISO8601>"
    }
  }
}
```

**Field definitions:**

| Field | Type | Description |
|-------|------|-------------|
| `task_uuid` | String | The UUID echoed back from the incoming ECOS assignment message. Must match exactly |
| `status` | String | Always `"received"` for initial acknowledgment. Other valid values in later messages: `"in-progress"`, `"complete"`, `"blocked"` |
| `estimated_completion` | String | ISO8601 timestamp (e.g., `2026-02-10T18:00:00Z`) representing when EOA expects to deliver the completed task |

**Procedure after sending ACK:**

1. Log the task in EOA's local task registry (Kanban board or task tracking file)
2. Analyze the task to determine which sub-agents are needed
3. Begin task decomposition and delegation planning
4. Send the first delegation message to sub-agents (see [ai-maestro-message-templates.md](ai-maestro-message-templates.md) section 1.2)

**Key rules:**
- ACK must be sent within 5 minutes of receiving the assignment
- The `task_uuid` must be echoed back exactly as received
- The `estimated_completion` timestamp must be a realistic estimate, not a placeholder
- If EOA cannot estimate completion, set `estimated_completion` to `null` and add `"estimation_pending": true` to the `data` object

---

## 6. Resource Request Decision Tree

This decision tree shows the complete evaluation process EOA follows when receiving a resource or skill request from an agent.

### 6.1 Resource Request Evaluation

```
Resource request received from agent
│
├─ Is resource within EOA's authority to grant?
│   │
│   ├─ Yes
│   │   │
│   │   ├─ Is resource available?
│   │   │   │
│   │   │   ├─ Yes
│   │   │   │   └─ Grant immediately (Section 2.1)
│   │   │   │       Notify agent with access details
│   │   │   │
│   │   │   └─ No
│   │   │       │
│   │   │       ├─ Can workaround be provided?
│   │   │       │   │
│   │   │       │   ├─ Yes
│   │   │       │   │   └─ Provide workaround in denial message (Section 2.2)
│   │   │       │   │       Set alternative field with step-by-step instructions
│   │   │       │   │
│   │   │       │   └─ No
│   │   │       │       └─ Escalate to ECOS (Section 2.3)
│   │   │       │           Forward full request with context
│   │   │       │
│   │   │       └─ (end)
│   │   │
│   │   └─ (end)
│   │
│   └─ No
│       │
│       ├─ Is it a security-sensitive resource?
│       │   (credentials, private repo access, production systems, API keys)
│       │   │
│       │   ├─ Yes
│       │   │   └─ Deny request (Section 2.2)
│       │   │       Escalate to ECOS with security_flag: true (Section 2.3)
│       │   │       Reason: "Security-sensitive resource requires ECOS approval"
│       │   │
│       │   └─ No
│       │       └─ Forward request to ECOS for approval (Section 2.3)
│       │           Notify agent that request was escalated
│       │
│       └─ (end)
│
└─ (end)
```

### 6.2 Skill Request Evaluation

```
Skill/capability request received from agent
│
├─ Does a matching skill exist in the global skill registry?
│   │
│   ├─ Yes
│   │   │
│   │   ├─ Can the requesting agent use it directly?
│   │   │   (globally installed, no special permissions needed)
│   │   │   │
│   │   │   ├─ Yes
│   │   │   │   └─ Respond with skill details (Section 4.1)
│   │   │   │       Provide access method and documentation path
│   │   │   │
│   │   │   └─ No
│   │   │       └─ Escalate to ECOS to spawn specialized agent (Section 4.3)
│   │   │           The skill requires a dedicated agent with the right plugin
│   │   │
│   │   └─ (end)
│   │
│   └─ No
│       │
│       ├─ Can the task be accomplished with a workaround?
│       │   (alternative tools, manual steps, different approach)
│       │   │
│       │   ├─ Yes
│       │   │   └─ Provide workaround (Section 4.2)
│       │   │       Document limitations of the workaround
│       │   │
│       │   └─ No
│       │       └─ Escalate to ECOS (Section 4.3)
│       │           Request spawn of specialized agent with needed capability
│       │
│       └─ (end)
│
└─ (end)
```

### 6.3 EOA Authority Boundaries

The following table defines what EOA can grant directly versus what requires ECOS approval:

| Resource Type | EOA Can Grant Directly | Requires ECOS Approval |
|---------------|----------------------|------------------------|
| **Tools** | CLI tools already installed in the environment | Installing new system-level packages |
| **File Access** | Files within the current project directory | Cross-project file access, system directories |
| **Credentials** | None (all credentials are security-sensitive) | All credential requests |
| **Services** | Services already configured and running locally | New service provisioning, external API access |
| **Skills** | Globally installed skills the agent can invoke | Skills requiring new plugin installation or agent spawn |

---

## Notes

- All timestamps use ISO8601 format (e.g., `2026-02-10T18:00:00Z`)
- Message `content` MUST be a JSON object, NOT a string
- Session names are case-sensitive
- Always echo back `task_uuid` from the originating task in all related messages
- Resource requests with `urgency: blocking` should be prioritized over `non-blocking`
- If ECOS does not respond to an escalated resource request within a reasonable time, EOA should send a reminder following the escalation protocol described in [escalation-protocol.md](escalation-protocol.md)
