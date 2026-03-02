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
workflow-instruction: "support"
procedure: "support-skill"
---

# Agent Replacement Skill

## Overview

Handle agent replacement scenarios triggered by AMCOS (Emergency Context-loss Operations System). When an agent fails, becomes unresponsive, or experiences context loss, compile all task context and generate handoff documents for the replacement agent.

## Prerequisites

- Python 3.8+ with PyYAML installed
- GitHub CLI (gh) authenticated
- AI Maestro running for inter-agent messaging
- AMCOS system operational for replacement notifications
- Active orchestration state with agent assignments

## Output

| Output Type | Location | Format |
|-------------|----------|--------|
| Handoff Document | GitHub issue comment | Markdown with task context, progress, next steps |
| State File Update | Orchestrator state YAML | Updated agent assignment with replacement metadata |
| AMCOS Confirmation | AI Maestro message | JSON confirmation with replacement status |
| Kanban Reassignment | GitHub Project board | Updated assignee on all task cards |

---

## Instructions

1. Receive and acknowledge the AMCOS replacement notification via AI Maestro
2. Compile all task context from the failed agent (assignments, progress, blockers, file changes)
3. Generate a comprehensive handoff document with all necessary context
4. Reassign GitHub Project kanban tasks to the replacement agent
5. Send the handoff document to the new agent using the `agent-messaging` skill and request acknowledgment
6. Confirm replacement by verifying ACK, updating state, and notifying AMCOS

**Use this skill when**: AMCOS notifies you of agent failure, context loss, unresponsive behavior, or manual replacement is needed.

---

## Checklist

Copy this checklist and track your progress:

- [ ] Receive and acknowledge AMCOS replacement notification
- [ ] Compile all task context from failed agent
- [ ] Generate comprehensive handoff document
- [ ] Reassign GitHub Project kanban tasks
- [ ] Send handoff document to new agent via AI Maestro using the `agent-messaging` skill
- [ ] Confirm ACK receipt and requirements understanding
- [ ] Update orchestrator state file
- [ ] Notify AMCOS of successful replacement

---

## Contents

| Section | Reference |
|---------|-----------|
| Step 1: Receive AMCOS Notification | [amcos-notification-handling.md](references/amcos-notification-handling.md) |
| Step 2: Compile Task Context | [context-compilation-workflow.md](references/context-compilation-workflow.md) |
<!-- TOC: 1 Information Sources | 2 State File Extraction | 3 GitHub Issue Collection -->
| Step 3: Generate Handoff Document | [handoff-document-format.md](references/handoff-document-format.md) |
<!-- TOC: 1 Required Sections | 2 Task Detail Format | 3 Progress Documentation -->
| Step 4: Reassign Kanban Tasks | [kanban-reassignment-protocol.md](references/kanban-reassignment-protocol.md) |
<!-- TOC: 1 Finding Assigned Cards | 2 Updating Assignee | 3 Adding Audit Comments -->
| Step 5: Send Handoff to New Agent | [handoff-delivery-protocol.md](references/handoff-delivery-protocol.md) |
<!-- TOC: 1 Document Upload | 2 AI Maestro Notification | 3 ACK Requirements -->
| Step 6: Confirm Reassignment | [confirmation-protocol.md](references/confirmation-protocol.md) |
<!-- TOC: 1 ACK Verification | 2 State File Updates | 3 AMCOS Notification -->
| Handoff Protocols | [handoff-protocols.md](references/handoff-protocols.md) |
| Design Document Protocol | [design-document-protocol.md](references/design-document-protocol.md) |
<!-- TOC: Document UUID Format (GUUID) | Required Frontmatter Schema | Document Lifecycle -->
| Edge Case Protocols | [edge-case-protocols.md](references/edge-case-protocols.md) |
<!-- TOC: Table of Contents | 0 AI Maestro Unavailable | 1 Detection Methods -->
| Task Completion Checklist | [task-completion-checklist.md](references/task-completion-checklist.md) |
<!-- TOC: Before Reporting Task Complete | Acceptance Criteria Met | Quality Gates Passed -->

---

## Replacement Protocol Flow

```
AMCOS → AMOA: Agent X failed, replacement is Agent Y
                    ↓
AMOA: Compile all task context for Agent X
                    ↓
AMOA: Generate comprehensive handoff document
                    ↓
AMOA: Update GitHub Project kanban (reassign tasks)
                    ↓
AMOA: Send handoff to replacement agent
                    ↓
AMOA: Confirm reassignment complete
```

**CRITICAL**: Before any replacement action: SAVE all state, DOCUMENT progress, PRESERVE communication history, NEVER assume new agent has any context.

---

## Step 1: Receive AMCOS Notification

Acknowledge AMCOS notification, pause new assignments, begin context compilation.

See: [amcos-notification-handling.md](references/amcos-notification-handling.md) - 1.1 Notification Types, 1.2 Urgency Levels, 1.3 Acknowledgment Protocol, 1.4 Error Handling

---

## Step 2: Compile Task Context

Gather ALL information: task assignments, requirements, current progress, blockers, file changes, communication history, GitHub issues.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/amoa_compile_replacement_context.py" \
  --failed-agent "implementer-1" --output "replacement-context.md"
```

See: [context-compilation-workflow.md](references/context-compilation-workflow.md) - 2.1 Information Sources, 2.2 State File Extraction, 2.3 GitHub Issue Collection, 2.4 Communication History, 2.5 Git Branch Analysis

---

## Step 3: Generate Handoff Document

Create comprehensive handoff with: metadata, task context, user requirements, progress, technical context, communication history, next steps, verification requirements.

```
/amoa-generate-replacement-handoff --failed-agent implementer-1 --new-agent implementer-2 --include-tasks --include-context
```

See: [handoff-document-format.md](references/handoff-document-format.md) - 3.1 Required Sections, 3.2 Task Detail Format, 3.3 Progress Documentation, 3.4 Communication History Format, 3.5 Next Steps Clarity

---

## Step 4: Reassign Kanban Tasks

Find all cards assigned to failed agent, update assignee, add reassignment comment, preserve labels/status, log for audit.

```
/amoa-reassign-kanban-tasks --from-agent implementer-1 --to-agent implementer-2 --project-id PROJECT_ID
```

See: [kanban-reassignment-protocol.md](references/kanban-reassignment-protocol.md) - 4.1 Finding Assigned Cards, 4.2 Updating Assignee, 4.3 Audit Comments, 4.4 Preserving State, 4.5 Handling Partial Work

---

## Step 5: Send Handoff to New Agent

Upload handoff to GitHub issue, send AI Maestro message using the `agent-messaging` skill with URL, include urgency level, request ACK within timeout.

See: [handoff-delivery-protocol.md](references/handoff-delivery-protocol.md) - 5.1 Document Upload, 5.2 AI Maestro Notification, 5.3 ACK Requirements, 5.4 Timeout Handling

---

## Step 6: Confirm Reassignment

Verify: new agent ACKed, requirements understood, GitHub cards updated, state file updated, AMCOS notified, failed agent removed from roster.

See: [confirmation-protocol.md](references/confirmation-protocol.md) - 6.1 ACK Verification, 6.2 State File Updates, 6.3 AMCOS Notification, 6.4 Audit Logging

---

## Python Scripts

| Script | Purpose |
|--------|---------|
| `amoa_compile_replacement_context.py` | Gather all context about failed agent's work |
| `amoa_generate_replacement_handoff.py` | Generate handoff document from compiled context |
| `amoa_reassign_kanban_tasks.py` | Reassign GitHub Project cards |
| `amoa_confirm_replacement.py` | Verify replacement completion and notify AMCOS |

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| AMCOS notification not received | AI Maestro communication failure | Check AI Maestro service status |
| Context compilation failed | State file missing or git unavailable | See troubleshooting.md section 7.2 |
| Handoff generation failed | Template or incomplete data error | See troubleshooting.md section 7.3 |
| GitHub API rate limit | Too many API calls | Wait or use batch operations |
| New agent ACK timeout | Agent unresponsive | Retry or alert user |

See: [troubleshooting.md](references/troubleshooting.md) for detailed troubleshooting procedures.
<!-- TOC: 1 AMCOS Communication Failures | 2 Context Compilation Failures | 3 Handoff Generation Failures -->

See: [emergency-procedures.md](references/emergency-procedures.md) for critical failure scenarios.
<!-- TOC: Replacement Agent Also Fails | Handoff Document Corrupted | GitHub Project Access Issues -->

---

## Examples

See: [examples.md](references/examples.md) - Standard replacement flow, emergency replacement with partial context
<!-- TOC: Example 1: Standard Replacement Flow | Example 2: Emergency Replacement with Partial Context -->

---

## Resources

| Reference | Description |
|-----------|-------------|
| [amcos-notification-handling.md](references/amcos-notification-handling.md) | AMCOS message handling + Agent Recovery decision tree and response template |
<!-- TOC: 1 Notification Types | 2 Urgency Levels | 3 Acknowledgment Protocol -->
| [context-compilation-workflow.md](references/context-compilation-workflow.md) | Gathering task context |
<!-- TOC: 1 Information Sources | 2 State File Extraction | 3 GitHub Issue Collection -->
| [handoff-document-format.md](references/handoff-document-format.md) | Handoff document structure |
<!-- TOC: 1 Required Sections | 2 Task Detail Format | 3 Progress Documentation -->
| [kanban-reassignment-protocol.md](references/kanban-reassignment-protocol.md) | GitHub Project updates |
<!-- TOC: 1 Finding Assigned Cards | 2 Updating Assignee | 3 Adding Audit Comments -->
| [handoff-delivery-protocol.md](references/handoff-delivery-protocol.md) | Delivering to new agent + Handoff delivery method decision tree and ACK template |
<!-- TOC: 1 Document Upload | 2 AI Maestro Notification | 3 ACK Requirements -->
| [confirmation-protocol.md](references/confirmation-protocol.md) | Confirming replacement + Confirmation outcome decision tree and AMCOS notification template |
<!-- TOC: 1 ACK Verification | 2 State File Updates | 3 AMCOS Notification -->
| [handoff-protocols.md](references/handoff-protocols.md) | Handoff protocol procedures |
<!-- TOC: Document Delivery Protocol | Task Delegation Protocol | Acknowledgment Protocol -->
| [design-document-protocol.md](references/design-document-protocol.md) | Design document protocol |
<!-- TOC: Document UUID Format (GUUID) | Required Frontmatter Schema | Document Lifecycle -->
| [edge-case-protocols.md](references/edge-case-protocols.md) | Edge case protocols |
<!-- TOC: Table of Contents | 0 AI Maestro Unavailable | 1 Detection Methods -->
| [task-completion-checklist.md](references/task-completion-checklist.md) | Task completion checklist |
<!-- TOC: Before Reporting Task Complete | Acceptance Criteria Met | Quality Gates Passed -->
| [troubleshooting.md](references/troubleshooting.md) | Common issues and solutions |
<!-- TOC: 1 AMCOS Communication Failures | 2 Context Compilation Failures | 3 Handoff Generation Failures -->
| [emergency-procedures.md](references/emergency-procedures.md) | Emergency procedures |
<!-- TOC: Replacement Agent Also Fails | Handoff Document Corrupted | GitHub Project Access Issues -->
| [examples.md](references/examples.md) | Usage examples |
<!-- TOC: Example 1: Standard Replacement Flow | Example 2: Emergency Replacement with Partial Context -->

## Related Skills

- `amoa-remote-agent-coordinator` - Agent registration and assignment
- `amoa-remote-agent-coordinator` - Remote agent communication
- `amoa-orchestration-patterns` - General orchestration patterns
- `amoa-agent-replacement` - Shared handoff protocols

---

**Version**: 1.0.0 | **Last Updated**: 2026-02-03
