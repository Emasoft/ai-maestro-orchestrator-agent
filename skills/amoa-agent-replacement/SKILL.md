---
name: eoa-agent-replacement
description: "Use when replacing agents. Trigger with agent replacement or handoff requests."
license: Apache-2.0
compatibility: "Requires Python 3.8+, PyYAML, GitHub CLI. Requires AI Maestro for inter-agent messaging. Requires ECOS notifications for replacement triggers. Requires AI Maestro installed."
metadata:
  author: Emasoft
  version: 1.0.0
user-invocable: false
context: fork
agent: eoa-main
workflow-instruction: "support"
procedure: "support-skill"
---

# Agent Replacement Skill

## Overview

Handle agent replacement scenarios triggered by ECOS (Emergency Context-loss Operations System). When an agent fails, becomes unresponsive, or experiences context loss, compile all task context and generate handoff documents for the replacement agent.

## Prerequisites

- Python 3.8+ with PyYAML installed
- GitHub CLI (gh) authenticated
- AI Maestro running for inter-agent messaging
- ECOS system operational for replacement notifications
- Active orchestration state with agent assignments

## Output

| Output Type | Location | Format |
|-------------|----------|--------|
| Handoff Document | GitHub issue comment | Markdown with task context, progress, next steps |
| State File Update | Orchestrator state YAML | Updated agent assignment with replacement metadata |
| ECOS Confirmation | AI Maestro message | JSON confirmation with replacement status |
| Kanban Reassignment | GitHub Project board | Updated assignee on all task cards |

---

## Instructions

1. Receive and acknowledge the ECOS replacement notification via AI Maestro
2. Compile all task context from the failed agent (assignments, progress, blockers, file changes)
3. Generate a comprehensive handoff document with all necessary context
4. Reassign GitHub Project kanban tasks to the replacement agent
5. Send the handoff document to the new agent using the `agent-messaging` skill and request acknowledgment
6. Confirm replacement by verifying ACK, updating state, and notifying ECOS

**Use this skill when**: ECOS notifies you of agent failure, context loss, unresponsive behavior, or manual replacement is needed.

---

## Checklist

Copy this checklist and track your progress:

- [ ] Receive and acknowledge ECOS replacement notification
- [ ] Compile all task context from failed agent
- [ ] Generate comprehensive handoff document
- [ ] Reassign GitHub Project kanban tasks
- [ ] Send handoff document to new agent via AI Maestro using the `agent-messaging` skill
- [ ] Confirm ACK receipt and requirements understanding
- [ ] Update orchestrator state file
- [ ] Notify ECOS of successful replacement

---

## Contents

| Section | Reference |
|---------|-----------|
| Step 1: Receive ECOS Notification | [ecos-notification-handling.md](references/ecos-notification-handling.md) |
| Step 2: Compile Task Context | [context-compilation-workflow.md](references/context-compilation-workflow.md) |
| Step 3: Generate Handoff Document | [handoff-document-format.md](references/handoff-document-format.md) |
| Step 4: Reassign Kanban Tasks | [kanban-reassignment-protocol.md](references/kanban-reassignment-protocol.md) |
| Step 5: Send Handoff to New Agent | [handoff-delivery-protocol.md](references/handoff-delivery-protocol.md) |
| Step 6: Confirm Reassignment | [confirmation-protocol.md](references/confirmation-protocol.md) |
| Handoff Protocols | [handoff-protocols.md](references/handoff-protocols.md) |
| Design Document Protocol | [design-document-protocol.md](references/design-document-protocol.md) |
| Edge Case Protocols | [edge-case-protocols.md](references/edge-case-protocols.md) |
| Task Completion Checklist | [task-completion-checklist.md](references/task-completion-checklist.md) |

---

## Replacement Protocol Flow

```
ECOS → EOA: Agent X failed, replacement is Agent Y
                    ↓
EOA: Compile all task context for Agent X
                    ↓
EOA: Generate comprehensive handoff document
                    ↓
EOA: Update GitHub Project kanban (reassign tasks)
                    ↓
EOA: Send handoff to replacement agent
                    ↓
EOA: Confirm reassignment complete
```

**CRITICAL**: Before any replacement action: SAVE all state, DOCUMENT progress, PRESERVE communication history, NEVER assume new agent has any context.

---

## Step 1: Receive ECOS Notification

Acknowledge ECOS notification, pause new assignments, begin context compilation.

See: [ecos-notification-handling.md](references/ecos-notification-handling.md) - 1.1 Notification Types, 1.2 Urgency Levels, 1.3 Acknowledgment Protocol, 1.4 Error Handling

---

## Step 2: Compile Task Context

Gather ALL information: task assignments, requirements, current progress, blockers, file changes, communication history, GitHub issues.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_compile_replacement_context.py" \
  --failed-agent "implementer-1" --output "replacement-context.md"
```

See: [context-compilation-workflow.md](references/context-compilation-workflow.md) - 2.1 Information Sources, 2.2 State File Extraction, 2.3 GitHub Issue Collection, 2.4 Communication History, 2.5 Git Branch Analysis

---

## Step 3: Generate Handoff Document

Create comprehensive handoff with: metadata, task context, user requirements, progress, technical context, communication history, next steps, verification requirements.

```
/eoa-generate-replacement-handoff --failed-agent implementer-1 --new-agent implementer-2 --include-tasks --include-context
```

See: [handoff-document-format.md](references/handoff-document-format.md) - 3.1 Required Sections, 3.2 Task Detail Format, 3.3 Progress Documentation, 3.4 Communication History Format, 3.5 Next Steps Clarity

---

## Step 4: Reassign Kanban Tasks

Find all cards assigned to failed agent, update assignee, add reassignment comment, preserve labels/status, log for audit.

```
/eoa-reassign-kanban-tasks --from-agent implementer-1 --to-agent implementer-2 --project-id PROJECT_ID
```

See: [kanban-reassignment-protocol.md](references/kanban-reassignment-protocol.md) - 4.1 Finding Assigned Cards, 4.2 Updating Assignee, 4.3 Audit Comments, 4.4 Preserving State, 4.5 Handling Partial Work

---

## Step 5: Send Handoff to New Agent

Upload handoff to GitHub issue, send AI Maestro message using the `agent-messaging` skill with URL, include urgency level, request ACK within timeout.

See: [handoff-delivery-protocol.md](references/handoff-delivery-protocol.md) - 5.1 Document Upload, 5.2 AI Maestro Notification, 5.3 ACK Requirements, 5.4 Timeout Handling

---

## Step 6: Confirm Reassignment

Verify: new agent ACKed, requirements understood, GitHub cards updated, state file updated, ECOS notified, failed agent removed from roster.

See: [confirmation-protocol.md](references/confirmation-protocol.md) - 6.1 ACK Verification, 6.2 State File Updates, 6.3 ECOS Notification, 6.4 Audit Logging

---

## Python Scripts

| Script | Purpose |
|--------|---------|
| `eoa_compile_replacement_context.py` | Gather all context about failed agent's work |
| `eoa_generate_replacement_handoff.py` | Generate handoff document from compiled context |
| `eoa_reassign_kanban_tasks.py` | Reassign GitHub Project cards |
| `eoa_confirm_replacement.py` | Verify replacement completion and notify ECOS |

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| ECOS notification not received | AI Maestro communication failure | Check AI Maestro service status |
| Context compilation failed | State file missing or git unavailable | See troubleshooting.md section 7.2 |
| Handoff generation failed | Template or incomplete data error | See troubleshooting.md section 7.3 |
| GitHub API rate limit | Too many API calls | Wait or use batch operations |
| New agent ACK timeout | Agent unresponsive | Retry or alert user |

See: [troubleshooting.md](references/troubleshooting.md) for detailed troubleshooting procedures.

See: [emergency-procedures.md](references/emergency-procedures.md) for critical failure scenarios.

---

## Examples

See: [examples.md](references/examples.md) - Standard replacement flow, emergency replacement with partial context

---

## Resources

| Reference | Description |
|-----------|-------------|
| [ecos-notification-handling.md](references/ecos-notification-handling.md) | ECOS message handling + Agent Recovery decision tree and response template |
| [context-compilation-workflow.md](references/context-compilation-workflow.md) | Gathering task context |
| [handoff-document-format.md](references/handoff-document-format.md) | Handoff document structure |
| [kanban-reassignment-protocol.md](references/kanban-reassignment-protocol.md) | GitHub Project updates |
| [handoff-delivery-protocol.md](references/handoff-delivery-protocol.md) | Delivering to new agent + Handoff delivery method decision tree and ACK template |
| [confirmation-protocol.md](references/confirmation-protocol.md) | Confirming replacement + Confirmation outcome decision tree and ECOS notification template |
| [handoff-protocols.md](references/handoff-protocols.md) | Handoff protocol procedures |
| [design-document-protocol.md](references/design-document-protocol.md) | Design document protocol |
| [edge-case-protocols.md](references/edge-case-protocols.md) | Edge case protocols |
| [task-completion-checklist.md](references/task-completion-checklist.md) | Task completion checklist |
| [troubleshooting.md](references/troubleshooting.md) | Common issues and solutions |
| [emergency-procedures.md](references/emergency-procedures.md) | Emergency procedures |
| [examples.md](references/examples.md) | Usage examples |

## Related Skills

- `eoa-remote-agent-coordinator` - Agent registration and assignment
- `eoa-remote-agent-coordinator` - Remote agent communication
- `eoa-orchestration-patterns` - General orchestration patterns
- `eoa-agent-replacement` - Shared handoff protocols

---

**Version**: 1.0.0 | **Last Updated**: 2026-02-03
