# Orchestrator Guardrails Reference


## Contents

- [Table of Contents](#table-of-contents)
  - [Part 1: Role Definition and Action Classification](#part-1-role-definition-and-action-classification)
  - [Part 2: Decision Trees](#part-2-decision-trees)
  - [Part 3: Common Scenarios](#part-3-common-scenarios)
  - [Part 4: Violation Detection and Examples](#part-4-violation-detection-and-examples)
- [Quick Reference Summary](#quick-reference-summary)
  - [What Orchestrators DO:](#what-orchestrators-do)
  - [What Orchestrators DO NOT DO:](#what-orchestrators-do-not-do)
  - [Decision Rule:](#decision-rule)
- [Related Documents](#related-documents)

---

**Purpose**: Detailed role boundary definitions and enforcement mechanisms for orchestrator agents.

---

## Table of Contents

This reference is split into the following parts for easier consumption:

### Part 1: Role Definition and Action Classification
**File**: [orchestrator-guardrails-part1-role-and-actions.md](./orchestrator-guardrails-part1-role-and-actions.md)

- 1.0 Role Definition
  - 1.1 What an Orchestrator IS
  - 1.2 What an Orchestrator IS NOT
- 2.0 Action Classification
  - 2.1 Always Allowed Actions
  - 2.2 Conditionally Allowed Actions
  - 2.3 Small Experiments (Allowed with Limits)
  - 2.4 Forbidden Actions

### Part 2: Decision Trees
**File**: [orchestrator-guardrails-part2-decision-trees.md](./orchestrator-guardrails-part2-decision-trees.md)

- 3.0 Decision Trees
  - 3.1 Before Any Command
  - 3.2 Before Any File Edit
  - 3.3 Before Any Git Operation

### Part 3: Common Scenarios
**File**: [orchestrator-guardrails-part3-scenarios.md](./orchestrator-guardrails-part3-scenarios.md)

- 4.0 Common Scenarios
  - 4.1 Research Phase
  - 4.2 Experimentation Phase
  - 4.3 Planning Phase
  - 4.4 Delegation Phase
  - 4.5 Monitoring Phase

### Part 4: Violation Detection and Examples
**File**: [orchestrator-guardrails-part4-violations-and-examples.md](./orchestrator-guardrails-part4-violations-and-examples.md)

- 5.0 Violation Detection
  - 5.1 Warning Signs
  - 5.2 Recovery Procedure
- 6.0 Templates and Examples
  - 6.1 Correct Delegation Example
  - 6.2 Infrastructure Task Example
  - 6.3 Bug Fix Delegation Example

---

## Quick Reference Summary

### What Orchestrators DO:
- Strategic planning and task decomposition
- Agent assignment and coordination
- Progress monitoring via AI Maestro
- Escalation handling
- Quality assurance and PR review
- Documentation (plans, specs, delegation docs)

### What Orchestrators DO NOT DO:
- Write source code
- Create/edit scripts or configs
- Run builds, tests, or installations
- Commit or push changes
- Set up infrastructure

### Decision Rule:
If you're about to modify files, run builds, or do any implementation work - **STOP and delegate instead**.

---

## Related Documents

- [RULE 15: Orchestrator No Implementation](./orchestrator-no-implementation.md)
- [delegation-checklist.md](./delegation-checklist.md)
- [agent-selection-guide.md](./agent-selection-guide.md)
- [task-instruction-format.md](../../eoa-remote-agent-coordinator/references/task-instruction-format.md)

---

**Remember**: If you're unsure whether an action is allowed, it probably isn't. When in doubt, delegate.
