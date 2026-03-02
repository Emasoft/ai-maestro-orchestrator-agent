# Inter-Agent Communication Protocols


## Contents

- [Table of Contents](#table-of-contents)
- [1. Communication Hierarchy](#1-communication-hierarchy)
  - [1.1 When communicating in a multi-agent system](#11-when-communicating-in-a-multi-agent-system)
  - [1.2 Orchestrator-exclusive communications (RULE 16)](#12-orchestrator-exclusive-communications-rule-16)
- [2. Message Routing Protocol](#2-message-routing-protocol)
  - [2.1 If sending messages to remote agents](#21-if-sending-messages-to-remote-agents)
  - [2.2 If receiving messages from orchestrator](#22-if-receiving-messages-from-orchestrator)
- [3. Acknowledgment Protocol](#3-acknowledgment-protocol)
  - [3.1 When acknowledgment is required](#31-when-acknowledgment-is-required)
  - [3.2 Acknowledgment timing requirements](#32-acknowledgment-timing-requirements)
- [4. Escalation Protocol](#4-escalation-protocol)
  - [4.1 If encountering blockers](#41-if-encountering-blockers)
  - [4.2 If requiring clarification](#42-if-requiring-clarification)
- [See Also](#see-also)

---

This document defines the protocols for communication between agents in the emasoft multi-agent system.

---

## Table of Contents

- 1. Communication Hierarchy
  - 1.1 When communicating in a multi-agent system
  - 1.2 Orchestrator-exclusive communications (RULE 16)
- 2. Message Routing Protocol
  - 2.1 If sending messages to remote agents
  - 2.2 If receiving messages from orchestrator
- 3. Acknowledgment Protocol
  - 3.1 When acknowledgment is required
  - 3.2 Acknowledgment timing requirements
- 4. Escalation Protocol
  - 4.1 If encountering blockers
  - 4.2 If requiring clarification

---

## 1. Communication Hierarchy

### 1.1 When communicating in a multi-agent system

The communication hierarchy within EOA's team follows strict rules:

```
ECOS (EOA's coordinator)
  ↓↑
EOA (team orchestrator)
  ↓↑
WORKER AGENTS (implementers, testers, sub-agents)
```

**Note**: This shows EOA's internal team structure. In the overall system, EOA receives work from ECOS (Chief of Staff), not directly from the human user. EAMA is the only agent that communicates directly with the human user.

**Rule**: Worker agents NEVER communicate directly with each other. All communication flows through EOA.

### 1.2 Orchestrator-exclusive communications (RULE 16)

Per RULE 16, only the orchestrator can:
- Send external messages (AI Maestro, email, notifications)
- Receive and process incoming messages
- Route messages between agents
- Commit and push changes

Sub-agents prepare content but NEVER send externally.

---

## 2. Message Routing Protocol

### 2.1 If sending messages to remote agents

The orchestrator sends messages using the `agent-messaging` skill:
- **Recipient**: the target agent session name
- **Subject**: the message subject
- **Content**: the message body
- **Type**: `request`, `assignment`, or `approval` as appropriate
- **Priority**: `normal`, `high`, or `urgent`

**Verify**: confirm message delivery.

### 2.2 If receiving messages from orchestrator

Remote agents use the `agent-messaging` skill to check their inbox for unread messages.

---

## 3. Acknowledgment Protocol

### 3.1 When acknowledgment is required

Acknowledgment is MANDATORY for:
- Task delegations
- Priority messages
- Assignment changes
- Escalation requests

Acknowledgment is NOT required for:
- Status inquiries
- Conversational messages
- FYI notifications

### 3.2 Acknowledgment timing requirements

| Message Priority | ACK Required Within |
|------------------|---------------------|
| URGENT | 30 seconds |
| HIGH | 2 minutes |
| NORMAL | 5 minutes |

---

## 4. Escalation Protocol

### 4.1 If encountering blockers

1. Document blocker in status report
2. Send BLOCKED status to orchestrator
3. Wait for orchestrator response
4. Do NOT attempt workarounds

### 4.2 If requiring clarification

1. Send CLARIFICATION_NEEDED acknowledgment
2. List specific questions
3. Continue other work if possible
4. Wait for orchestrator guidance

---

## See Also

- [agent-communication-formats.md](agent-communication-formats.md) - Message format specifications
- [templates-for-humans.md](templates-for-humans.md) - Human-facing communication templates
