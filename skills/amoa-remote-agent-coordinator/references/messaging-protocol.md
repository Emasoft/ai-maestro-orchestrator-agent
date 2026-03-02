# AI Maestro Messaging Protocol


## Contents

- [IMPORTANT: Official Skill Reference](#important-official-skill-reference)
- [Overview](#overview)
- [Document Structure](#document-structure)
  - [Part 1: API and Schema Reference](#part-1-api-and-schema-reference)
  - [Part 2: Sending and Receiving Messages](#part-2-sending-and-receiving-messages)
  - [Part 3: Message Types by Category](#part-3-message-types-by-category)
  - [Part 4: Agents, Errors, and Best Practices](#part-4-agents-errors-and-best-practices)
  - [Part 5: Notifications and Response Expectations](#part-5-notifications-and-response-expectations)
  - [Part 6: Timeouts and Protocol Integration](#part-6-timeouts-and-protocol-integration)
  - [Part 7: Troubleshooting](#part-7-troubleshooting)
- [Quick Reference](#quick-reference)
  - [Essential Commands](#essential-commands)
  - [Priority Quick Guide](#priority-quick-guide)
  - [Required Message Fields](#required-message-fields)
- [Navigation](#navigation)

---

## IMPORTANT: Official Skill Reference

**For sending and receiving messages, always use the official AI Maestro skill:**

```
~/.claude/skills/agent-messaging/SKILL.md
```

This skill is maintained by AI Maestro and automatically updated when the API changes. It provides operations for:
- Checking your inbox for unread messages
- Reading and marking messages as read
- Sending messages to other agents

**This document describes the MESSAGE PROTOCOL (formats, types, schemas) for EOA (Emasoft Orchestrator Agent) coordination, NOT the API usage.**

---

## Overview

AI Maestro provides inter-agent messaging between Claude Code sessions. This document details the message protocol and schemas for EOA orchestrator communication with remote developer agents.

## Document Structure

This protocol reference is split into focused sections. Read only what you need:

---

### Part 1: API and Schema Reference
**File**: [messaging-protocol-part1-api-schema.md](messaging-protocol-part1-api-schema.md)

**Contents**:
- 1.1 API Base URL and Endpoints
- 1.2 Complete Message Object Schema
- 1.3 Priority Levels and Expected Response Times

**Read when**: You need to understand the API structure, message format, or priority system.

---

### Part 2: Sending and Receiving Messages
**File**: [messaging-protocol-part2-send-receive.md](messaging-protocol-part2-send-receive.md)

**Contents**:
- 2.1 Basic Send Syntax
- 2.2 Send with Task Assignment (complex JSON)
- 2.3 Check Inbox Command
- 2.4 Read and Mark Message as Read

**Read when**: You need to send a message or check your inbox.

---

### Part 3: Message Types by Category
**File**: [messaging-protocol-part3-message-types.md](messaging-protocol-part3-message-types.md)

**Contents**:
- 3.1 Task Management Messages (task, fix-request, completion-report)
- 3.2 Status and Progress Messages (status-request, progress-update)
- 3.3 Approvals and Rejections (approval, rejection)
- 3.4 Escalations (escalation, escalation-response)

**Read when**: You need to format a specific type of message or understand message content schemas.

---

### Part 4: Agents, Errors, and Best Practices
**File**: [messaging-protocol-part4-agents-errors.md](messaging-protocol-part4-agents-errors.md)

**Contents**:
- 4.1 Agent Identification and Session Name Format
- 4.2 Resolving Agent Names (full name, alias, UUID)
- 4.3 API Error Codes and Meanings
- 4.4 Message Delivery Failure Handling
- 4.5 Message Size Best Practices
- 4.6 Subject Line Formatting
- 4.7 Content Structure Requirements
- 4.8 Environment Variables

**Read when**: You need to identify agents, handle errors, or follow best practices.

---

### Part 5: Notifications and Response Expectations
**File**: [messaging-protocol-part5-notifications-responses.md](messaging-protocol-part5-notifications-responses.md)

**Contents**:
- 5.1 Automatic Message Notification (Subconscious)
- 5.2 How Subconscious Polling Works
- 5.3 Response Expectations by Message Type Table
- 5.4 No-Response-Required Messages

**Read when**: You need to understand automatic notifications or know what response to expect.

---

### Part 6: Timeouts and Protocol Integration
**File**: [messaging-protocol-part6-timeouts-integration.md](messaging-protocol-part6-timeouts-integration.md)

**Contents**:
- 6.1 Response Timeouts by Priority Level
- 6.2 Timeout Flow (first timeout, retry, escalation)
- 6.3 Retry Message Format
- 6.4 Integration with Other Protocols
- 6.5 Protocol Hierarchy Diagram
- 6.6 Message Type Registry

**Read when**: You need to handle timeouts or understand how this protocol relates to others.

---

### Part 7: Troubleshooting
**File**: [messaging-protocol-part7-troubleshooting.md](messaging-protocol-part7-troubleshooting.md)

**Contents**:
- 7.1 Messages Not Being Delivered
- 7.2 Agent Not Found (404)
- 7.3 Message Content Malformed (400)
- 7.4 Messages Arrive Out of Order
- 7.5 Duplicate Messages Received
- 7.6 Subconscious Notifications Not Appearing
- 7.7 High Priority Messages Not Prioritized
- 7.8 Message Timeout But Agent Is Working

**Read when**: You encounter problems with messaging.

---

## Quick Reference

### Essential Operations

Use the `agent-messaging` skill for all messaging operations:
- **Send a message**: specify recipient, subject, message body, priority, and type
- **Check inbox**: retrieve all unread messages for your session
- **Read specific message**: retrieve and mark a message as read by its ID

**Verify**: confirm each operation completes successfully.

### Priority Quick Guide

| Level | Use Case | Response Time |
|-------|----------|---------------|
| `urgent` | Blocking/security | Immediate |
| `high` | Important tasks | 30 min |
| `normal` | Standard tasks | 2 hours |
| `low` | FYI updates | When convenient |

### Required Message Fields

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "recipient-session-name",
  "subject": "Brief subject line",
  "content": {
    "type": "message-type",
    "message": "Content here"
  }
}
```

---

## Navigation

| If you need to... | Read... |
|------------------|---------|
| Understand API structure | [Part 1](messaging-protocol-part1-api-schema.md) |
| Send or receive messages | [Part 2](messaging-protocol-part2-send-receive.md) |
| Format specific message types | [Part 3](messaging-protocol-part3-message-types.md) |
| Handle errors or follow best practices | [Part 4](messaging-protocol-part4-agents-errors.md) |
| Understand notifications/responses | [Part 5](messaging-protocol-part5-notifications-responses.md) |
| Handle timeouts or protocol integration | [Part 6](messaging-protocol-part6-timeouts-integration.md) |
| Fix problems | [Part 7](messaging-protocol-part7-troubleshooting.md) |
