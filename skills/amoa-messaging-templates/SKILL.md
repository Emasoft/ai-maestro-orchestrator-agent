---
name: amoa-messaging-templates
description: "Use when sending inter-agent messages. Trigger with task assignment, status report, or escalation needs."
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
context: fork
user-invocable: false
agent: amoa-main
---

# AMOA Shared Communication Templates

Message templates and protocols for agent coordination, task assignment, status reporting, and escalation.

## Overview

Reusable JSON message templates for inter-agent communication.

## Prerequisites

1. AI Maestro messaging system (AMP) running
2. Understanding of ai-maestro agent roles (AMOA, AMCOS, AMIA, AMAMA)
3. Access to AI Maestro API; read **amoa-label-taxonomy** for GitHub label usage

## Instructions

1. Identify the communication scenario (task assignment, status report, approval, escalation)
2. Select the appropriate template from section 2 reference files
3. Fill in template fields with task-specific values
4. Send via `agent-messaging` skill and wait for response
5. Log the exchange in the delegation log

Copy this checklist and track your progress:

- [ ] Identify communication scenario (task assignment, status report, approval, escalation)
- [ ] Select the appropriate template from section 2
- [ ] Fill in template fields and send via `agent-messaging` skill
- [ ] Wait for response and log the exchange in the delegation log

## 1. AI Maestro Message Format

Standard JSON message structure with from, to, subject, priority, and content fields. See: [references/message-format.md](references/message-format.md)
<!-- TOC: Standard Message Structure | Sending Messages | Checking Inbox -->

---

## 2. Message Templates by Scenario

JSON templates: [references/message-templates.md](references/message-templates.md)
<!-- TOC: Task Assignment (AMOA to Remote Agent) | Task Completion Report (Agent to AMOA) | Decision Trees for Core Message Templates -->

Curl templates: [references/ai-maestro-message-templates.md](references/ai-maestro-message-templates.md)
<!-- TOC: Acknowledging Task Assignment from AMCOS/AMAMA | Delegating Task to Sub-Agent | Decision Trees for AI Maestro Message Handling -->

---

## Error Handling

On failure, retry once then escalate per [references/escalation-protocol.md](references/escalation-protocol.md)
<!-- TOC: Escalation Order | State-Based Triggers | Priority Escalation | Important Notes -->
Error resolution and scenario mapping: [references/error-handling-quickref.md](references/error-handling-quickref.md)
<!-- TOC: Error Handling | Quick Reference Card -->

---

## Examples

See: [references/examples.md](references/examples.md)
<!-- TOC: Full Task Assignment Flow | Example 1: Send Task Assignment | Example 2: Send Status Request -->

**Input:** Send task assignment to agent via `agent-messaging` skill with scenario=task_assignment, to=agent-name, subject="Run tests"
**Output:** `{"status":"sent","message_id":"msg-12345"}`

---

## Output

JSON messages (task/status/approval), API confirmations with message_id, message history arrays, and markdown delegation log entries.

## Resources

- **AGENT_OPERATIONS.md**, **amoa-label-taxonomy**, **amoa-task-distribution**, **amoa-progress-monitoring**

