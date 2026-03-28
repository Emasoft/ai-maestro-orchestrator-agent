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

## Overview

Reusable JSON message templates for agent coordination, task assignment, status reporting, and escalation.

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

## 2. Message Templates by Scenario

JSON templates: [references/message-templates.md](references/message-templates.md)
<!-- TOC: 1 Task Assignment (AMOA to Remote Agent) | 2 Task Completion Report (Agent to AMOA) | 3 Status Request (AMOA to Agent) | 4 Status Response (Agent to AMOA) | 5 Approval Request (AMCOS to AMAMA) | 6 Approval Response (AMAMA to AMCOS) | 7 Escalation (Any Agent to AMCOS/AMAMA) | 8 Acknowledgment (Any Agent) | 9 Design Handoff (AMAA to AMOA) | 10 Integration Request (AMOA to AMIA) | 11 Integration Result (AMIA to AMOA) | Decision Trees for Core Message Templates -->

Curl templates: [references/ai-maestro-message-templates.md](references/ai-maestro-message-templates.md)
<!-- TOC: 1 Acknowledging Task Assignment from AMCOS/AMAMA | 2 Delegating Task to Sub-Agent | 3 Requesting Status Update from Sub-Agent | 4 Reporting Task Completion to AMCOS | 5 Escalating Blocked Task to AMCOS | 6 Escalating Blocked Task to AMAMA (User Decision Needed) | 7 Standard AI Maestro API Format and Conventions | Quick Reference: Common Patterns | Notes | Decision Trees for AI Maestro Message Handling -->

## Error Handling

On failure, retry once then escalate per [references/escalation-protocol.md](references/escalation-protocol.md)
<!-- TOC: Escalation Order | State-Based Triggers | Priority Escalation | Important Notes -->
See also: [references/error-handling-quickref.md](references/error-handling-quickref.md)
<!-- TOC: Error Handling | Quick Reference Card -->

## Examples

See: [references/examples.md](references/examples.md)
<!-- TOC: Full Task Assignment Flow | Example 1: Send Task Assignment | Example 2: Send Status Request | Example 3: Escalate to Assistant Manager -->

**Input:** Send task assignment to agent via `agent-messaging` skill with scenario=task_assignment, to=agent-name, subject="Run tests"
**Output:** `{"status":"sent","message_id":"msg-12345"}`

## Output

JSON messages, API confirmations with message_id, and markdown delegation log entries.

## Resources

- **AGENT_OPERATIONS.md**, **amoa-label-taxonomy**, **amoa-task-distribution**, **amoa-progress-monitoring**

