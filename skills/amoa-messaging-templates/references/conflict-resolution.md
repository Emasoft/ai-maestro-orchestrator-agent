# Cross-Plugin Conflict Resolution Protocol

This document defines how to resolve conflicts when multiple emasoft agents need to modify the same GitHub labels, issues, or resources.

## Table of Contents

- [Authority Hierarchy](#authority-hierarchy)
- [Label Conflict Resolution](#label-conflict-resolution)
- [Label Change Request Protocol](#label-change-request-protocol)
- [Emergency Override Cases](#emergency-override-cases)

---

## Authority Hierarchy

When conflicts arise, authority is based on role (higher takes precedence):

1. **EAMA** (Assistant Manager) - User-facing decisions, approval authority
2. **ECOS** (Chief of Staff) - Agent lifecycle, resource management
3. **EOA** (Orchestrator) - Task distribution, kanban management
4. **EIA** (Integrator) - Quality gates, integration decisions
5. **EAA** (Architect) - Design decisions (within approved scope)

---

## Label Conflict Resolution

When multiple agents attempt to modify the same issue labels:

| Conflict Type | Resolution |
|---------------|------------|
| Assignment conflict (EOA vs ECOS) | ECOS wins (lifecycle priority) |
| Priority change | EAMA approval required for critical |
| Status conflict | Working agent has authority |
| Review decision | EIA has final say |

---

## Label Change Request Protocol

When one agent needs to modify labels another agent set, send a message before making the change:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "<your-agent>",
  "to": "<other-agent>",
  "subject": "Label Change Request: Issue #42",
  "priority": "normal",
  "content": {
    "type": "request",
    "message": "Requesting to change assign:implementer-1 to assign:implementer-2 due to: <reason>. Please acknowledge or object.",
    "data": {
      "issue_number": 42,
      "current_label": "assign:implementer-1",
      "requested_label": "assign:implementer-2",
      "reason": "<reason>"
    }
  }
}
```

**Wait for acknowledgment** before proceeding with the label change.

---

## Emergency Override Cases

**No message required** in these cases (change labels immediately):

- Agent terminated unexpectedly
- Agent unresponsive after 3 ping attempts
- Critical blocker affecting production

**Document the emergency override** in the delegation log with justification.
