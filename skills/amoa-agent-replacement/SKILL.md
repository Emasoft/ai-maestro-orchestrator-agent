---
name: amoa-agent-replacement
description: "Use when replacing agents. Trigger with agent replacement or handoff requests."
license: Apache-2.0
compatibility: "Requires Python 3.8+, PyYAML, GitHub CLI. Requires AI Maestro for inter-agent messaging. Requires AMCOS notifications for replacement triggers. Requires AI Maestro installed."
metadata:
  author: Emasoft
  version: 1.0.0
user-invocable: false
context: fork
agent: amoa-main
---

# Agent Replacement Skill

## Overview

Handle agent replacement scenarios triggered by AMCOS (Emergency Context-loss Operations System). When an agent fails, becomes unresponsive, or experiences context loss, compile all task context and generate handoff documents for the replacement agent.

**Use this skill when**: AMCOS notifies you of agent failure, context loss, unresponsive behavior, or manual replacement is needed.

## Prerequisites

- Python 3.8+ with PyYAML installed
- GitHub CLI (gh) authenticated
- AI Maestro running for inter-agent messaging
- AMCOS system operational for replacement notifications

## Output

| Output Type | Location | Format |
|-------------|----------|--------|
| Handoff Document | GitHub issue comment | Markdown with task context, progress, next steps |
| State File Update | Orchestrator state YAML | Updated agent assignment with replacement metadata |
| AMCOS Confirmation | AI Maestro message | JSON confirmation with replacement status |
| Kanban Reassignment | GitHub Project board | Updated assignee on all task cards |

---

## Workflow Summary

Six-step replacement protocol: receive AMCOS notification, compile task context, generate handoff document, reassign kanban tasks, send handoff to new agent, confirm reassignment.

See: [references/replacement-workflow-steps.md](references/replacement-workflow-steps.md) for detailed steps, commands, and scripts.

---

## Checklist

- [ ] Receive and acknowledge AMCOS replacement notification
- [ ] Compile all task context from failed agent
- [ ] Generate comprehensive handoff document
- [ ] Reassign GitHub Project kanban tasks
- [ ] Send handoff document to new agent via AI Maestro using the `agent-messaging` skill
- [ ] Confirm ACK receipt and requirements understanding
- [ ] Update orchestrator state file
- [ ] Notify AMCOS of successful replacement

---

## Error Handling

Common errors include AMCOS notification failures, context compilation issues, GitHub API rate limits, and ACK timeouts.

See: [references/error-handling-reference.md](references/error-handling-reference.md) for error table and solutions.

---

## References

All reference files are in `references/`. Key documents:

- [replacement-workflow-steps.md](references/replacement-workflow-steps.md) - Full 6-step workflow and scripts
- [error-handling-reference.md](references/error-handling-reference.md) - Error table and troubleshooting
- [handoff-document-format.md](references/handoff-document-format.md) - Handoff document structure
- [examples.md](references/examples.md) - Usage examples
- [emergency-procedures.md](references/emergency-procedures.md) - Emergency procedures

Additional references: `amcos-notification-handling`, `context-compilation-workflow`, `kanban-reassignment-protocol`, `handoff-delivery-protocol`, `confirmation-protocol`, `handoff-protocols`, `design-document-protocol`, `edge-case-protocols`, `task-completion-checklist`, `troubleshooting`.

## Examples

See: [references/examples.md](references/examples.md) for full replacement workflow examples and sample handoff documents.

---

## Instructions

1. On AMCOS notification, compile task context from the failed agent's GitHub issues, kanban cards, and AI Maestro message history.
2. Generate a handoff document and deliver it to the replacement agent via AI Maestro `agent-messaging` skill.
3. Wait for ACK, confirm reassignment, and notify AMCOS of successful replacement.

---

## Resources

- [references/replacement-workflow-steps.md](references/replacement-workflow-steps.md) - Protocol steps and scripts
- [references/handoff-document-format.md](references/handoff-document-format.md) - Handoff structure
- [references/context-compilation-workflow.md](references/context-compilation-workflow.md) - Context gathering

---

## Related Skills

- `amoa-remote-agent-coordinator` - Agent registration, assignment, and remote agent communication
- `amoa-orchestration-patterns` - General orchestration patterns

---

**Version**: 1.0.0 | **Last Updated**: 2026-02-03

## Script Output Rules

All scripts invoked by this skill MUST follow the token-efficient output protocol:

1. **Verbose output** goes to a timestamped report file in `docs_dev/reports/`
2. **Stdout** emits only 2-3 lines: `[OK/ERROR] script_name - summary` + `Report: path`
3. Scripts accept `--output-dir` to override the default report directory
4. **EXCEPTION**: Scripts in `scripts/amoa_stop_check/` MUST output JSON to stdout (Claude Code hook requirement)
