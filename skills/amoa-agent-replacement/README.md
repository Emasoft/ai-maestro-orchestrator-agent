# AMOA Agent Replacement Skill

Handle agent replacement scenarios triggered by AMCOS (Emergency Context-loss Operations System).

## Purpose

When an agent fails, becomes unresponsive, or experiences context loss, this skill guides the orchestrator through:

1. Receiving and processing AMCOS replacement notifications
2. Compiling all task context for the failed agent
3. Generating comprehensive handoff documents
4. Reassigning GitHub Project kanban tasks
5. Sending handoffs to replacement agents
6. Confirming successful replacement

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Main skill instructions |
| `references/amcos-notification-handling.md` | AMCOS message handling |
| `references/context-compilation-workflow.md` | Gathering task context |
| `references/handoff-document-format.md` | Handoff document structure |
| `references/kanban-reassignment-protocol.md` | GitHub Project updates |
| `references/handoff-delivery-protocol.md` | Delivering to new agent |
| `references/confirmation-protocol.md` | Confirming replacement |
| `references/troubleshooting.md` | Common issues and solutions |

## Quick Start

When AMCOS notifies about a replacement:

```bash
# Generate handoff for replacement agent
/amoa-generate-replacement-handoff --failed-agent <old> --new-agent <new> --include-tasks --include-context

# Reassign GitHub Project tasks
/amoa-reassign-kanban-tasks --from-agent <old> --to-agent <new> --project-id <id>
```

## Related Commands

- `/amoa-generate-replacement-handoff` - Generate handoff document
- `/amoa-reassign-kanban-tasks` - Reassign GitHub Project cards

## Version

1.0.0
