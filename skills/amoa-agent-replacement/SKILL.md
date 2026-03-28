---
name: amoa-agent-replacement
description: "Use when replacing agents. Trigger with agent replacement or handoff requests."
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

**Use this skill when**: AMCOS notifies of agent failure, context loss, or manual replacement is needed.

## Prerequisites

- Python 3.8+ with PyYAML
- GitHub CLI (gh) authenticated — all commands need `--repo "$OWNER/$REPO"`
- AI Maestro running
- AMCOS system operational

## Output

| Output Type | Location | Format |
|-------------|----------|--------|
| Handoff Document | GitHub issue comment | Markdown with context and next steps |
| State File | Orchestrator state YAML | Updated agent assignment |
| AMCOS Confirmation | AI Maestro message | JSON replacement status |
| Kanban Update | GitHub Project board | Reassigned task cards |

---

## Instructions

**Multi-Repo Rule:** When compiling task context, use `gh issue list --repo "$OWNER/$REPO"` for each repo the failed agent worked on. All handoff documents go to `$AGENT_DIR/reports/`.

1. On AMCOS notification, compile task context from the failed agent's GitHub issues (using `--repo`), kanban cards, and AI Maestro message history.
2. Generate a handoff document and deliver it to the replacement agent via AI Maestro `agent-messaging` skill. Include target repo path(s) in the handoff.
3. Wait for ACK, confirm reassignment, and notify AMCOS of successful replacement.

See: [replacement-workflow-steps.md](references/replacement-workflow-steps.md) for detailed steps.
<!-- TOC: Python Scripts | Replacement Protocol Flow -->

---

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

---

## Examples

**Input:** AMCOS notification `{"type": "agent-failed", "agent": "libs-svg-svgbbox", "reason": "context-loss"}`
**Output:** Handoff document posted to GitHub issue + kanban tasks reassigned + AMCOS confirmation sent

See: [examples.md](references/examples.md) for full examples.
<!-- TOC: Example 1: Standard Replacement Flow | Example 2: Emergency Replacement with Partial Context -->

---

## Error Handling

See: [error-handling-reference.md](references/error-handling-reference.md) for errors and solutions.
<!-- TOC: Emergency Procedures | Common Errors and Solutions -->

---

## Resources

- [replacement-workflow-steps.md](references/replacement-workflow-steps.md) - 6-step workflow
  <!-- TOC: Python Scripts | Replacement Protocol Flow -->
- [error-handling-reference.md](references/error-handling-reference.md) - Errors
  <!-- TOC: Emergency Procedures | Common Errors and Solutions -->
- [handoff-document-format.md](references/handoff-document-format.md) - Handoff format
  <!-- TOC: Required Sections | Task Detail Format -->
- [examples.md](references/examples.md) - Examples
  <!-- TOC: Example 1: Standard Replacement Flow | Example 2: Emergency Replacement with Partial Context -->
- [emergency-procedures.md](references/emergency-procedures.md) - Emergencies
  <!-- TOC: Replacement Agent Also Fails | Handoff Document Corrupted -->
- [context-compilation-workflow.md](references/context-compilation-workflow.md) - Context gathering
  <!-- TOC: Information Sources | State File Extraction -->

---

## Related Skills

- `amoa-remote-agent-coordinator` - Agent registration and remote agent communication
- `amoa-orchestration-patterns` - General orchestration patterns

---

**Version**: 1.0.0 | **Last Updated**: 2026-02-03
