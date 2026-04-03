---
name: amoa-agent-replacement
description: "Use when replacing agents. Trigger with agent replacement or handoff requests. Loaded by ai-maestro-orchestrator-agent-main-agent"
license: Apache-2.0
compatibility: "Python 3.8+, PyYAML, GitHub CLI, AI Maestro, AMCOS."
metadata:
  author: Emasoft
  version: 1.0.0
user-invocable: false
context: fork
agent: amoa-main
---

# Agent Replacement Skill

## Overview

Handle agent replacement triggered by AMCOS. When an agent fails or loses context, compile task context and generate handoff documents for the replacement.


## Prerequisites

Python 3.8+, PyYAML, GitHub CLI (gh) authenticated, AI Maestro running, AMCOS operational.

## Output

Handoff document (GitHub issue comment), state file update, AMCOS confirmation, kanban reassignment.

## Instructions

1. On AMCOS notification, compile task context from the failed agent's GitHub issues, kanban cards, and AI Maestro message history.
2. Generate a handoff document and deliver it to the replacement agent via AI Maestro `agent-messaging` skill.
3. Wait for ACK, confirm reassignment, and notify AMCOS of successful replacement.

See: [replacement-workflow-steps.md](references/replacement-workflow-steps.md) for detailed steps.
<!-- TOC: Replacement Protocol Flow | Step 1: Receive AMCOS Notification | Step 2: Compile Task Context | Step 3: Generate Handoff Document | Step 4: Reassign Kanban Tasks | Step 5: Send Handoff to New Agent | Step 6: Confirm Reassignment | Python Scripts -->

## Checklist

Copy this checklist and track your progress:

- [ ] Receive and acknowledge AMCOS replacement notification
- [ ] Compile all task context from failed agent
- [ ] Generate comprehensive handoff document
- [ ] Reassign GitHub Project kanban tasks
- [ ] Send handoff to new agent via AI Maestro `agent-messaging` skill
- [ ] Confirm ACK receipt and requirements understanding
- [ ] Update orchestrator state file
- [ ] Notify AMCOS of successful replacement

## Examples

**Input:** AMCOS notification `{"type": "agent-failed", "agent": "libs-svg-svgbbox", "reason": "context-loss"}`
**Output:** Handoff document posted to GitHub issue + kanban tasks reassigned + AMCOS confirmation sent

See: [examples.md](references/examples.md) for full examples.
<!-- TOC: Example 1: Standard Replacement Flow | Example 2: Emergency Replacement with Partial Context -->

## Error Handling

See: [error-handling-reference.md](references/error-handling-reference.md) for errors and solutions.
<!-- TOC: Common Errors and Solutions | Troubleshooting References | Emergency Procedures -->

## Resources

- [replacement-workflow-steps.md](references/replacement-workflow-steps.md) - 6-step workflow
  - 1. Replacement Protocol Flow
  - 2. Step 1: Receive AMCOS Notification
  - 3. Step 2: Compile Task Context
  - 4. Step 3: Generate Handoff Document
  - 5. Step 4: Reassign Kanban Tasks
  - ...
- [error-handling-reference.md](references/error-handling-reference.md) - Errors
  - 1. Common Errors and Solutions
  - 2. Troubleshooting References
  - 3. Emergency Procedures
- [handoff-document-format.md](references/handoff-document-format.md) - Handoff format
  - 3.1 Required Sections
    - Mandatory Sections
    - Section Order
  - Template
  - Handoff Metadata
  - ...
- [examples.md](references/examples.md) - Examples
  - Example 1: Standard Replacement Flow
  - Example 2: Emergency Replacement with Partial Context
- [emergency-procedures.md](references/emergency-procedures.md) - Emergencies
  - Replacement Agent Also Fails
  - Handoff Document Corrupted
  - GitHub Project Access Issues
- [context-compilation-workflow.md](references/context-compilation-workflow.md) - Context gathering
  - 2.1 Information Sources
    - Primary Sources (MUST check)
    - Secondary Sources (SHOULD check)
    - Tertiary Sources (MAY check)
  - 2.2 State File Extraction
  - ...

