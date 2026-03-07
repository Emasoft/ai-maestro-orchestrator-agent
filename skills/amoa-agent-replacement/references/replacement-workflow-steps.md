## Table of Contents
1. Replacement Protocol Flow
2. Step 1: Receive AMCOS Notification
3. Step 2: Compile Task Context
4. Step 3: Generate Handoff Document
5. Step 4: Reassign Kanban Tasks
6. Step 5: Send Handoff to New Agent
7. Step 6: Confirm Reassignment
8. Python Scripts

---

## 1. Replacement Protocol Flow

```
AMCOS -> AMOA: Agent X failed, replacement is Agent Y
                    |
AMOA: Compile all task context for Agent X
                    |
AMOA: Generate comprehensive handoff document
                    |
AMOA: Update GitHub Project kanban (reassign tasks)
                    |
AMOA: Send handoff to replacement agent
                    |
AMOA: Confirm reassignment complete
```

**CRITICAL**: Before any replacement action: SAVE all state, DOCUMENT progress, PRESERVE communication history, NEVER assume new agent has any context.

---

## 2. Step 1: Receive AMCOS Notification

Acknowledge AMCOS notification, pause new assignments, begin context compilation.

See: [amcos-notification-handling.md](amcos-notification-handling.md) - 1.1 Notification Types, 1.2 Urgency Levels, 1.3 Acknowledgment Protocol, 1.4 Error Handling

---

## 3. Step 2: Compile Task Context

Gather ALL information: task assignments, requirements, current progress, blockers, file changes, communication history, GitHub issues.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/amoa_compile_replacement_context.py" \
  --failed-agent "implementer-1" --output "replacement-context.md"
```

See: [context-compilation-workflow.md](context-compilation-workflow.md) - 2.1 Information Sources, 2.2 State File Extraction, 2.3 GitHub Issue Collection, 2.4 Communication History, 2.5 Git Branch Analysis

---

## 4. Step 3: Generate Handoff Document

Create comprehensive handoff with: metadata, task context, user requirements, progress, technical context, communication history, next steps, verification requirements.

```
/amoa-generate-replacement-handoff --failed-agent implementer-1 --new-agent implementer-2 --include-tasks --include-context
```

See: [handoff-document-format.md](handoff-document-format.md) - 3.1 Required Sections, 3.2 Task Detail Format, 3.3 Progress Documentation, 3.4 Communication History Format, 3.5 Next Steps Clarity

---

## 5. Step 4: Reassign Kanban Tasks

Find all cards assigned to failed agent, update assignee, add reassignment comment, preserve labels/status, log for audit.

```
/amoa-reassign-kanban-tasks --from-agent implementer-1 --to-agent implementer-2 --project-id PROJECT_ID
```

See: [kanban-reassignment-protocol.md](kanban-reassignment-protocol.md) - 4.1 Finding Assigned Cards, 4.2 Updating Assignee, 4.3 Audit Comments, 4.4 Preserving State, 4.5 Handling Partial Work

---

## 6. Step 5: Send Handoff to New Agent

Upload handoff to GitHub issue, send AI Maestro message using the `agent-messaging` skill with URL, include urgency level, request ACK within timeout.

See: [handoff-delivery-protocol.md](handoff-delivery-protocol.md) - 5.1 Document Upload, 5.2 AI Maestro Notification, 5.3 ACK Requirements, 5.4 Timeout Handling

---

## 7. Step 6: Confirm Reassignment

Verify: new agent ACKed, requirements understood, GitHub cards updated, state file updated, AMCOS notified, failed agent removed from roster.

See: [confirmation-protocol.md](confirmation-protocol.md) - 6.1 ACK Verification, 6.2 State File Updates, 6.3 AMCOS Notification, 6.4 Audit Logging

---

## 8. Python Scripts

| Script | Purpose |
|--------|---------|
| `amoa_compile_replacement_context.py` | Gather all context about failed agent's work |
| `amoa_generate_replacement_handoff.py` | Generate handoff document from compiled context |
| `amoa_reassign_kanban_tasks.py` | Reassign GitHub Project cards |
| `amoa_confirm_replacement.py` | Verify replacement completion and notify AMCOS |
