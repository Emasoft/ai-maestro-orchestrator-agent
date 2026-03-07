---
name: amoa-implementer-interview-protocol
description: Interview protocols for task verification. Use when checking implementer readiness or approving PR creation. Trigger with task assignment.
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

The Orchestrator (AMOA) MUST interview the Implementer agent both **before** and **after** task execution. This is NOT optional. The pre-task interview verifies understanding, capability, compatibility, and feasibility. The post-task interview verifies completeness, quality, testing, and documentation before approving PR creation.

## Prerequisites

1. Read **AGENT_OPERATIONS.md** for orchestrator workflow
2. Read **amoa-remote-agent-coordinator/references/rule-14-immutable-requirements.md** for immutable vs. mutable requirements
3. Read **amoa-label-taxonomy** for status labels
4. Read **amoa-messaging-templates** for message formats

---

## 1. Pre-Task Interview (MANDATORY)

Verifies: Understanding, Capability, Compatibility, Feasibility.

**Questions and evaluation criteria**: See [interview-templates.md](./references/interview-templates.md)

**Escalation triggers**: Design concerns → Architect (AMAA). Immutable requirement concerns → Manager (AMAMA) → User. Capability issues → Reassign. Blockers → Resolve first.
See: [escalation-messages.md](./references/escalation-messages.md)

---

## 2. Post-Task Interview (MANDATORY)

Verifies: Completeness, Quality, Testing, Documentation.

**Verification protocol**: See [interview-templates.md](./references/interview-templates.md)

**Outcomes**: All pass → APPROVED. Minor issues → Request fixes, re-interview. Major issues → REVISE. Requirement deviations → Escalate.

---

## 3. Handoff and Output

After APPROVED, implementer creates PR. Orchestrator updates issue status to `status:ai-review` and notifies Integrator.
See: [handoff-and-output.md](./references/handoff-and-output.md)

---

## Instructions

1. Identify the implementer agent and the task issue number to interview about.
2. Send a **Pre-Task Interview** message via `agent-messaging` skill asking: Task Summary, Acceptance Criteria, Concerns, Approach, Blockers.
3. Evaluate the implementer's responses against the criteria in [interview-templates.md](./references/interview-templates.md). Escalate if needed.
4. After task execution, send a **Post-Task Interview** message verifying: Completeness, Quality, Testing, Documentation.
5. If all checks pass, mark APPROVED and proceed to handoff per [handoff-and-output.md](./references/handoff-and-output.md).

Full checklists: [interview-workflow-steps.md](./references/interview-workflow-steps.md)

---

## Error Handling

See: [exception-handling.md](./references/exception-handling.md)

| Error | Quick Solution |
|-------|----------------|
| No ACK | Reminder → escalate to progress-monitoring |
| Misunderstands task | Clarify, update handoff, re-interview |
| Design concerns | Escalate to Architect (AMAA) |
| Requirement concerns | Escalate to Manager (AMAMA) → User |
| Incomplete work | REVISE with specific items |
| Tests fail | REVISE, require passing tests |
| PR before approval | Remind protocol, manual review |

---

## Examples

Complete interview curl examples and sample dialogues: See [examples.md](./references/examples.md)

---

## Output

Interview outcomes and integrator handoff artifacts: See [handoff-and-output.md](./references/handoff-and-output.md)

---

## Resources

- **[interview-templates.md](./references/interview-templates.md)** - Question templates, evaluation, and decision trees
- **[escalation-messages.md](./references/escalation-messages.md)** - Escalation and approval messages
- **[exception-handling.md](./references/exception-handling.md)** - Exception procedures
- **[examples.md](./references/examples.md)** - Complete curl examples
- **[interview-workflow-steps.md](./references/interview-workflow-steps.md)** - Full checklists and step-by-step procedures
- **[handoff-and-output.md](./references/handoff-and-output.md)** - Integrator handoff and output types
- **AGENT_OPERATIONS.md** - Core orchestrator workflow
- **amoa-label-taxonomy** - Status label workflow
- **amoa-messaging-templates** - Message templates
- **amoa-task-distribution** - Task assignment protocol

## Script Output Rules

All scripts invoked by this skill MUST follow the token-efficient output protocol:

1. **Verbose output** goes to a timestamped report file in `docs_dev/reports/`
2. **Stdout** emits only 2-3 lines: `[OK/ERROR] script_name - summary` + `Report: path`
3. Scripts accept `--output-dir` to override the default report directory
4. **EXCEPTION**: Scripts in `scripts/amoa_stop_check/` MUST output JSON to stdout (Claude Code hook requirement)
