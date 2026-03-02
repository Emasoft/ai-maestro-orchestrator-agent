# Handoff Protocols Reference

## Purpose

This document defines the standard protocols for handing off tasks, documents, and communications between the orchestrator and remote agents in the EOA ecosystem.

---

## Contents

- [Document Delivery Protocol](#document-delivery-protocol)
- [Task Delegation Protocol](#task-delegation-protocol)
- [Acknowledgment Protocol](#acknowledgment-protocol)
- [Completion Reporting Protocol](#completion-reporting-protocol)
- [Blocker Escalation Protocol](#blocker-escalation-protocol)

---

## Standard Handoff Format

All handoffs use the EAMA standard format:
- **Location**: `docs_dev/handoffs/`
- **Naming**: `handoff-{uuid}-{from}-to-{to}.md`
- **Delivery**: AI Maestro message with file path
- **Template**: See `shared/handoff_template.md`

---

## Document Delivery Protocol

All documents (.md files) shared between agents MUST follow this protocol:

### Delivery Rules

1. **NEVER embed full document content in AI Maestro messages**
2. Save document to local handoff directory: `docs_dev/handoffs/`
3. Use standard filename format: `handoff-{uuid}-{from}-to-{to}.md`
4. Send AI Maestro message using the `agent-messaging` skill with local file path only
5. Recipient reads from local handoff directory

### Message Format

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "{{AGENT_SESSION}}",
  "subject": "document_delivery",
  "priority": "high",
  "content": {
    "type": "document_delivery",
    "message": "Document ready. Path: docs_dev/handoffs/handoff-{{UUID}}-{{FROM}}-to-{{TO}}.md"
  }
}
```

### Storage Structure

```
docs_dev/handoffs/
  handoff-{uuid}-{from}-to-{to}.md  # All handoff documents
```

---

## Task Delegation Protocol

When orchestrator delegates a task to a remote agent:

1. **Compile task template** with all variables substituted
2. **Save to local handoff directory**: `docs_dev/handoffs/`
3. **Send AI Maestro message** using the `agent-messaging` skill with local file path
4. **Wait for ACK** within timeout period
5. **Track progress** via handoff status updates

### Template Reference

See: [TASK_DELEGATION_TEMPLATE.md](../../eoa-remote-agent-coordinator/templates/handoff/TASK_DELEGATION_TEMPLATE.md)

---

## Acknowledgment Protocol

Remote agents MUST acknowledge task receipt:

### ACK Format

```
[ACK] {{TASK_ID}} - {{STATUS}}
Understanding: {{ONE_LINE_SUMMARY}}
```

### Status Values

| Status | Meaning |
|--------|---------|
| RECEIVED | Task received, will begin work immediately |
| CLARIFICATION_NEEDED | Need more info (list questions) |
| REJECTED | Cannot accept task (explain why) |
| QUEUED | Have prior tasks, will start after them |

### Escalation Rules

- If no ACK received: Orchestrator sends reminder
- If still no response: Orchestrator sends urgent reminder
- If still unresponsive: Mark agent as unresponsive, consider reassignment

### Template Reference

See: [ACK_TEMPLATE.md](../../eoa-remote-agent-coordinator/templates/handoff/ACK_TEMPLATE.md)

---

## Completion Reporting Protocol

When agent completes a task:

1. **Create completion report** using template
2. **Save to local handoff directory**: `docs_dev/handoffs/`
3. **Update handoff file** with status: completed
4. **Send AI Maestro message** using the `agent-messaging` skill with local file path
5. **Wait for orchestrator sign-off**

### Template Reference

See: [COMPLETION_REPORT_TEMPLATE.md](../../eoa-remote-agent-coordinator/templates/handoff/COMPLETION_REPORT_TEMPLATE.md)

---

## Blocker Escalation Protocol

When agent encounters a blocker:

1. **Document blocker** with context and impact
2. **Save to local handoff directory**: `docs_dev/handoffs/`
3. **Update handoff file** with status: blocked
4. **Send AI Maestro message** using the `agent-messaging` skill with URGENT priority and file path
5. **Wait for orchestrator response**

### Blocker Categories

| Category | Example |
|----------|---------|
| Missing dependency | Required package not available |
| Auth failure | Cannot access required resource |
| Spec ambiguity | Requirements unclear |
| Technical block | API limit, rate limiting |
| Conflict | Merge conflict, resource contention |

### Template Reference

See: [BLOCKER_REPORT_TEMPLATE.md](../../eoa-remote-agent-coordinator/templates/handoff/BLOCKER_REPORT_TEMPLATE.md)

---

## Integration with Other Protocols

This protocol integrates with:

- **echo-acknowledgment-protocol.md** - ACK timing and retries
- **messaging-protocol.md** - AI Maestro message format
- **artifact-sharing-protocol.md** - Large file sharing
- **document-storage-protocol.md** - Local storage rules

---

## Troubleshooting

### Document Not Received

1. Check local handoff directory for document
2. Verify AI Maestro message was sent
3. Check recipient agent is online
4. Resend with explicit file path

### ACK Not Received

1. Wait for timeout period
2. Send explicit ACK reminder
3. If still no response, mark unresponsive
4. Consider reassigning task

### Document Corrupted

1. Re-read from local handoff directory
2. Verify file integrity
3. Contact sender for re-creation if needed

---

**Version**: 1.0.0
**Last Updated**: 2026-01-15
