# Proactive Handoff Protocol

## Standard Handoff Format

All handoffs use the EAMA standard format:
- **Location**: `docs_dev/handoffs/`
- **Naming**: `handoff-{uuid}-{from}-to-{to}.md`
- **Delivery**: AI Maestro message with file path
- **Template**: See `../../shared/handoff_template.md`

---

## Contents

- [Standard Handoff Format](#standard-handoff-format)
- [Automatic Handoff Triggers](#automatic-handoff-triggers)
- [Handoff Document Location](#handoff-document-location)
- [Mandatory Handoff Sections](#mandatory-handoff-sections)
- [Context](#context)
- [Progress](#progress)
- [Current State](#current-state)
- [Blockers (if any)](#blockers-if-any)
- [Next Steps](#next-steps)
- [References](#references)
- [Proactive Writing Rules](#proactive-writing-rules)
- [Handoff Quality Checklist](#handoff-quality-checklist)

---

## Automatic Handoff Triggers

This agent MUST automatically write a handoff document when:

1. **Task Completion**: Before reporting task done
2. **Session End**: When session is about to end (PreCompact, Stop)
3. **Role Transition**: When work moves to another role
4. **Context Limit**: When approaching context window limit
5. **Blocking Issue**: When blocked and escalating

## Handoff Document Location

Write handoffs to: `$CLAUDE_PROJECT_DIR/docs_dev/handoffs/`

**Filename format**: `handoff-{uuid}-{from_role}-to-{to_role}-{timestamp}.md`

## Mandatory Handoff Sections

```yaml
---
uuid: <generated-uuid>
from: <agent-name>
to: <target-agent-or-user>
timestamp: <ISO-8601>
priority: normal|high|urgent
requires_ack: true|false
---

## Context
What was being worked on? Why was it started?

## Progress
- [x] Completed steps
- [ ] Pending steps

## Current State
Where exactly did work stop? What files are affected?

## Blockers (if any)
What's preventing progress?

## Next Steps
Exactly what the next agent should do first.

## References
- File paths
- Issue/PR numbers
- Previous handoff links
```

## Proactive Writing Rules

1. **ALWAYS write handoff before reporting completion** via AI Maestro
2. **ALWAYS write handoff before session ends** (hook should block if missing)
3. **NEVER assume next agent knows context** - be explicit
4. **ALWAYS include file paths** with line numbers when relevant
5. **ALWAYS send AI Maestro message** using the `agent-messaging` skill after writing handoff with file path

## Handoff Quality Checklist

Before sending handoff:
- [ ] UUID is unique and recorded
- [ ] Context explains WHY work was started
- [ ] All affected files listed with paths
- [ ] Current state is specific (not "almost done")
- [ ] Next steps are actionable (first action is clear)
- [ ] AI Maestro notification prepared
