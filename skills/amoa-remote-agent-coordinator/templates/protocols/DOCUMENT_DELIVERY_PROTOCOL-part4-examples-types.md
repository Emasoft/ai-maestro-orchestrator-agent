# Document Delivery Protocol - Part 4: Message Examples and Document Types

**Parent:** [DOCUMENT_DELIVERY_PROTOCOL.md](./DOCUMENT_DELIVERY_PROTOCOL.md)

---

## 4.1 Message Format Examples

### 4.1.1 CORRECT: URL Only

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "libs-svg-svgbbox",
  "subject": "[DOC] TASK_DELEGATION - GH-42",
  "priority": "high",
  "content": {
    "type": "document_delivery",
    "task_id": "GH-42",
    "document_type": "TASK_DELEGATION",
    "github_comment_url": "https://github.com/owner/repo/issues/42#issuecomment-123456",
    "filename": "task-delegation-GH-42.md",
    "requires_ack": true
  }
}
```

### 4.1.2 WRONG: Embedded Content

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "libs-svg-svgbbox",
  "subject": "Task Assignment",
  "priority": "high",
  "content": {
    "type": "task",
    "message": "## Task: GH-42\n### Requirements\n- Implement feature X\n- Write tests\n- Update docs\n\n### Background\nThis task requires...\n(500+ lines of markdown)"
  }
}
```

**Why WRONG:** Embedded content >500 chars violates Rule 1. Use `document_delivery` type with GitHub URL instead.

---

## 4.2 Document Types

Common document types for `document_type` field:

| Document Type | Description | ACK Required |
|--------------|-------------|--------------|
| `TASK_DELEGATION` | Task assignment with full instructions | YES |
| `PROGRESS_REPORT` | Status update with detailed progress | YES |
| `COMPLETION_REPORT` | Final report with results/deliverables | YES |
| `CHECKLIST` | Task checklist or verification steps | YES |
| `SPECIFICATION` | Technical specification or requirements | YES |
| `REFERENCE_DOC` | Reference documentation or guide | NO* |
| `TROUBLESHOOTING` | Issue diagnosis and resolution steps | YES |
| `HANDOFF_DOC` | Context transfer for agent handoff | YES |

*Reference docs may not require ACK if sent proactively (not blocking any task).

---

## 4.3 Audit Trail

Every document delivery creates an audit trail:

1. **GitHub Issue Comment:** Permanent record with timestamp, sender, attachment
2. **AI Maestro Message:** Delivery notification with URL reference
3. **ACK Response:** Confirmation of receipt and processing start
4. **Issue Thread:** All follow-up discussion tied to original document

### 4.3.1 Example Audit Chain

```
[2026-01-05 15:30:00] Orchestrator → GitHub Issue #42 Comment
  - Attachment: task-delegation-GH-42.md

[2026-01-05 15:30:05] Orchestrator → libs-svg-svgbbox (AI Maestro)
  - Message: [DOC] TASK_DELEGATION - GH-42
  - URL: https://github.com/owner/repo/issues/42#issuecomment-123456

[2026-01-05 15:30:30] libs-svg-svgbbox → Orchestrator (AI Maestro)
  - Message: [ACK] GH-42 - RECEIVED

[2026-01-05 15:45:00] libs-svg-svgbbox → GitHub Issue #42 Comment
  - Progress update: "Completed step 1/5"
```

---

**Previous:** [Part 3: Orchestrator Enforcement](./DOCUMENT_DELIVERY_PROTOCOL-part3-orchestrator.md)

**Next:** [Part 5: Troubleshooting and Checklists](./DOCUMENT_DELIVERY_PROTOCOL-part5-troubleshooting.md)
