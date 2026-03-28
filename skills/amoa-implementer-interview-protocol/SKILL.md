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

Interview implementers pre/post task to verify readiness and quality before PR creation.

## Prerequisites

AGENT_OPERATIONS.md, amoa-label-taxonomy, amoa-messaging-templates.

## Output

Interview decision (PROCEED/APPROVED/REVISE), handoff doc, and issue label update.

## Instructions

1. Identify implementer and issue. Send Pre-Task Interview via `agent-messaging`
   - Questions: [interview-templates.md](./references/interview-templates.md)
   <!-- TOC: Pre-Task Interview Questions | Post-Task Interview Questions -->
   - Escalation: [escalation-messages.md](./references/escalation-messages.md)
   <!-- TOC: REVISE Message | PROCEED Message -->
2. Evaluate responses; send PROCEED or REVISE
3. After execution, send Post-Task Interview. All pass → APPROVED, major → REVISE
4. On APPROVED, create PR, set `status:ai-review`, notify Integrator per [handoff-and-output.md](./references/handoff-and-output.md)
   <!-- TOC: Output Types | Handoff to Integrator -->

Copy this checklist and track your progress:

- [ ] Send Pre-Task Interview and evaluate
- [ ] Send PROCEED or REVISE
- [ ] Send Post-Task Interview and evaluate
- [ ] On APPROVED, execute handoff

Steps: [interview-workflow-steps.md](./references/interview-workflow-steps.md)
<!-- TOC: Pre-Task Interview Checklist | Post-Task Interview Checklist | Pre-Task Interview Steps | Post-Task Interview Steps -->

## Error Handling

See: [exception-handling.md](./references/exception-handling.md)
<!-- TOC: Implementer Disagrees with Requirements | Architect Recommends Design Change | User Approves Requirement Change | Implementer Never Acknowledges | Implementer Misunderstands Task | Implementer Has Design Concerns | Implementer Reports Incomplete Work | Tests Fail in Post-Task Interview | Implementer Creates PR Before Approval -->

## Examples

See [examples.md](./references/examples.md)
<!-- TOC: Example 1: Send Pre-Task Interview Questions | Example 2: Escalate Design Concern to Architect | Example 3: Send PROCEED After Satisfactory Interview | Example 4: Send Post-Task Verification Questions | Example 5: Send APPROVED and Handoff to Integrator -->

**Input:** Issue #42 assigned to `libs-svg-svgbbox`. **Output:** Pre-task → PROCEED → post-task → APPROVED → Integrator notified.

## Resources

- [interview-templates.md](./references/interview-templates.md)
  - Pre-Task Interview Questions
  - Pre-Task Interview: {TASK_ID}
  - Post-Task Interview Questions
  - Post-Task Interview: {TASK_ID}
  - ...
- [escalation-messages.md](./references/escalation-messages.md)
  - Design Issues → Architect
  - Immutable Requirement Issues → Manager → User
  - PROCEED Message
  - PROCEED: {TASK_ID}
  - ...
- [exception-handling.md](./references/exception-handling.md)
  - 1. Implementer Disagrees with Requirements
  - 2. Architect Recommends Design Change
  - 3. User Approves Requirement Change
  - 4. Implementer Never Acknowledges
  - ...
- [examples.md](./references/examples.md)
  - Example 1: Send Pre-Task Interview Questions
  - Example 2: Escalate Design Concern to Architect
  - Example 3: Send PROCEED After Satisfactory Interview
  - Example 4: Send Post-Task Verification Questions
  - ...
- [interview-workflow-steps.md](./references/interview-workflow-steps.md)
  - Pre-Task Interview Checklist
  - Post-Task Interview Checklist
  - Pre-Task Interview Steps
  - Post-Task Interview Steps
- [handoff-and-output.md](./references/handoff-and-output.md)
  - Handoff to Integrator
    - When PR is Created
    - Responsibility Transfer
  - Output Types

