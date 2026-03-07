## Table of Contents
- [Error Handling](#error-handling)
- [Quick Reference Card](#quick-reference-card)

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Message not delivered | AI Maestro offline or agent not found | Check AI Maestro health, verify agent session name |
| No response from agent | Agent hibernated, offline, or unresponsive | Follow escalation order from escalation-protocol.md |
| Invalid JSON | Malformed message content | Validate JSON syntax before sending |
| Wrong recipient | Incorrect agent name or session ID | Verify agent name from roster or AI Maestro |
| Label conflict | Multiple agents modifying same issue | Follow conflict resolution protocol from conflict-resolution.md |

## Quick Reference Card

| Scenario | Template | Priority |
|----------|----------|----------|
| Assign task | 2.1 | high |
| Task complete | 2.2 | normal |
| Status request | 2.3 | normal |
| Status response | 2.4 | normal |
| Approval request | 2.5 | high |
| Approval response | 2.6 | high |
| Escalation | 2.7 | high |
| Acknowledgment | 2.8 | low |
| Design handoff | 2.9 | high |
| Integration request | 2.10 | high |
| Integration result | 2.11 | high |
