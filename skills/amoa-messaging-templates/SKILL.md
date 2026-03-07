---
name: amoa-messaging-templates
description: AI Maestro message templates for ai-maestro plugins. Use when sending task assignments, status reports, or escalations between agents. Trigger with messaging requests.
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

Shared message templates and protocols for agent coordination, task assignment, status reporting, and escalation.

## Overview

Reusable JSON message templates for inter-agent communication. See [references/message-templates.md](references/message-templates.md).

## Prerequisites

1. AI Maestro messaging system (AMP) running
2. Understanding of ai-maestro agent roles (AMOA, AMCOS, AMIA, AMAMA)
3. Access to AI Maestro API; read **amoa-label-taxonomy** for GitHub label usage

## Instructions

1. Identify the communication scenario (task assignment, status report, approval request, etc.)
2. Select the appropriate message template from section 2
3. Fill in the template and send via AI Maestro using the `agent-messaging` skill
4. Wait for response, log the exchange in the delegation/coordination log

## 1. AI Maestro Message Format

Standard JSON message structure with from, to, subject, priority, and content fields. See: [references/message-format.md](references/message-format.md)

---

## 2. Message Templates by Scenario

For complete JSON templates, see **[references/message-templates.md](references/message-templates.md)**:

- **2.1** Task Assignment (AMOA -> Agent)
- **2.2** Task Completion Report (Agent -> AMOA)
- **2.3** Status Request (AMOA -> Agent)
- **2.4** Status Response (Agent -> AMOA)
- **2.5** Approval Request (AMCOS -> AMAMA)
- **2.6** Approval Response (AMAMA -> AMCOS)
- **2.7** Escalation (Any Agent -> AMCOS/AMAMA)
- **2.8** Acknowledgment (Any Agent)
- **2.9** Design Handoff (AMAA -> AMOA)
- **2.10** Integration Request (AMOA -> AMIA)
- **2.11** Integration Result (AMIA -> AMOA)

For curl command templates: **[references/ai-maestro-message-templates.md](references/ai-maestro-message-templates.md)**

### Extended Templates

| Reference File | Contents |
|---------------|----------|
| [amcos-response-templates.md](references/amcos-response-templates.md) | AMCOS/AMAMA/AMAA responses to AMOA with decision trees |
| [session-lifecycle-templates.md](references/session-lifecycle-templates.md) | Wake/Hibernate/Terminate messages and periodic status |
| [task-lifecycle-templates.md](references/task-lifecycle-templates.md) | Cancel/Pause/Resume/Broadcast/Stop commands |
| [resource-request-templates.md](references/resource-request-templates.md) | Agent resource and skill requests with grant/deny/escalate |

---

## 3. Cross-Plugin Protocol Reference

Communication hierarchy (USER -> AMAMA -> AMCOS -> AMOA/AMAA/AMIA), messaging rules, GitHub label conventions, and status labels. See: [references/cross-plugin-protocol.md](references/cross-plugin-protocol.md)

Conflict resolution protocol: [references/conflict-resolution.md](references/conflict-resolution.md)

Escalation order and priority rules: [references/escalation-protocol.md](references/escalation-protocol.md)

---

## 4. Record-Keeping Standards

Standard `docs_dev/` directory structure, filename conventions, and log entry format. See: [references/record-keeping.md](references/record-keeping.md)

---

## Error Handling

On failure, retry once then escalate per [references/escalation-protocol.md](references/escalation-protocol.md).

## Error Handling & Quick Reference

Error resolution table and scenario-to-template mapping. See: [references/error-handling-quickref.md](references/error-handling-quickref.md)

---

## Examples

Full task assignment flow and curl command examples. See: [references/examples.md](references/examples.md)

---

## Output

| Output Type | Format |
|-------------|--------|
| AI Maestro message | JSON (task assignment, status request, approval) |
| Message confirmation | API response with status and message_id |
| Message history | JSON array of all messages for an agent |
| Delegation log entry | Markdown timestamped record |

## Resources

- **AGENT_OPERATIONS.md** - Core orchestrator workflow
- **amoa-label-taxonomy** - GitHub label usage
- **amoa-task-distribution** - Task assignment protocol
- **amoa-progress-monitoring** - Agent state tracking
- [AI Maestro Message Templates](./references/ai-maestro-message-templates.md) - Curl command templates

## Script Output Rules

All scripts MUST follow the token-efficient output protocol:
1. Verbose output goes to a timestamped report file in `docs_dev/reports/`
2. Stdout emits only 2-3 lines: status + filepath
3. Format: `[OK/ERROR] script_name - one-line summary\nReport: docs_dev/reports/script_name-YYYYMMDD-HHMMSS.md`
4. **EXCEPTION**: Scripts in `scripts/amoa_stop_check/` MUST output JSON to stdout (Claude Code hook requirement)
