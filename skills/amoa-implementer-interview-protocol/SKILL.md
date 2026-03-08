---
name: amoa-implementer-interview-protocol
description: "Use when verifying implementer readiness. Trigger with interview or PR approval requests."
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
context: fork
user-invocable: false
agent: amoa-main
---

# Implementer Interview Protocol

## Overview

Interview the Implementer before and after task execution. Pre-task verifies understanding, capability, feasibility. Post-task verifies completeness, quality, testing before PR creation.

## Prerequisites

1. Read **AGENT_OPERATIONS.md**, **amoa-label-taxonomy**, **amoa-messaging-templates**
2. Read **amoa-remote-agent-coordinator/references/rule-14-immutable-requirements.md**

## 1. Pre-Task Interview (MANDATORY)

Verifies: Understanding, Capability, Compatibility, Feasibility.

**Questions**: [interview-templates.md](./references/interview-templates.md)
<!-- TOC: Pre-Task Interview Questions | Post-Task Interview Questions -->

**Escalation**: Design → AMAA. Immutable → AMAMA → User. See: [escalation-messages.md](./references/escalation-messages.md)
<!-- TOC: REVISE Message | PROCEED Message -->

## 2. Post-Task Interview (MANDATORY)

Verifies: Completeness, Quality, Testing, Documentation.

**Protocol**: [interview-templates.md](./references/interview-templates.md). All pass → APPROVED. Minor → Fix. Major → REVISE.
<!-- TOC: Pre-Task Interview Questions | Post-Task Interview Questions -->

## 3. Handoff

After APPROVED, implementer creates PR. Orchestrator sets `status:ai-review`, notifies Integrator.
See: [handoff-and-output.md](./references/handoff-and-output.md)
<!-- TOC: Output Types | Handoff to Integrator -->

## Output

- **Interview result**: PROCEED, APPROVED, or REVISE decision
- **Handoff document**: Markdown with task context for replacement or next agent
- **Issue update**: GitHub issue labels and comments reflecting interview outcome

## Instructions

1. Identify the implementer agent and task issue number
2. Send the Pre-Task Interview via `agent-messaging` skill
3. Evaluate responses per interview-templates.md; escalate design/requirement issues
4. Send PROCEED if pre-task passes; after execution send Post-Task Interview
5. Evaluate post-task results; issue REVISE or APPROVED
6. If APPROVED, execute handoff per handoff-and-output.md

Copy this checklist and track your progress:

- [ ] Identify the implementer agent and task issue number
- [ ] Send Pre-Task Interview via `agent-messaging` skill
- [ ] Evaluate responses and escalate if needed
- [ ] Send PROCEED or REVISE decision
- [ ] After execution, send Post-Task Interview
- [ ] If APPROVED, execute handoff

Steps: [interview-workflow-steps.md](./references/interview-workflow-steps.md)
<!-- TOC: Pre-Task Interview Steps | Post-Task Interview Steps -->

## Error Handling

See: [exception-handling.md](./references/exception-handling.md)
<!-- TOC: Implementer Misunderstands Task | Implementer Never Acknowledges -->

| Error | Solution |
|-------|----------|
| No ACK | Reminder → escalate |
| Misunderstands task | Clarify, re-interview |
| Design/requirement concerns | Escalate to AMAA/AMAMA |
| Incomplete or tests fail | REVISE with specifics |
| PR before approval | Remind protocol |

## Examples

See [examples.md](./references/examples.md)
<!-- TOC: Example 1: Send Pre-Task Interview Questions | Example 2: Escalate Design Concern to Architect -->

**Input:** Task assignment for issue #42 to implementer `libs-svg-svgbbox`.
**Output:** Pre-task interview → PROCEED → post-task → APPROVED → Integrator notified.

## Resources

- [interview-templates.md](./references/interview-templates.md) — Questions, evaluation, decision trees
  <!-- TOC: Pre-Task Interview Questions | Post-Task Interview Questions -->
- [escalation-messages.md](./references/escalation-messages.md) — Escalation and approval messages
  <!-- TOC: REVISE Message | PROCEED Message -->
- [exception-handling.md](./references/exception-handling.md) — Exception procedures
  <!-- TOC: Implementer Misunderstands Task | Implementer Never Acknowledges -->
- [examples.md](./references/examples.md) — Curl examples
  <!-- TOC: Example 1: Send Pre-Task Interview Questions | Example 2: Escalate Design Concern to Architect -->
- [interview-workflow-steps.md](./references/interview-workflow-steps.md) — Checklists and procedures
  <!-- TOC: Pre-Task Interview Steps | Post-Task Interview Steps -->
- [handoff-and-output.md](./references/handoff-and-output.md) — Handoff and output types
  <!-- TOC: Output Types | Handoff to Integrator -->

