---
name: eoa-remote-agent-coordinator
description: "Use when coordinating remote AI agents. Trigger with task delegation or multi-agent coordination requests."
license: Apache-2.0
compatibility: Requires AI Maestro messaging system (AMP, handles routing automatically). Python 3.9+ for LSP management scripts. Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.2.0
context: fork
user-invocable: false
agent: eoa-main
workflow-instruction: "Step 17"
procedure: "proc-execute-task"
---

# Remote Agent Coordinator

## Overview

The Remote Agent Coordinator enables the EOA (Emasoft Orchestrator Agent) to delegate coding tasks to remote AI agents and human developers via the AI Maestro messaging system. This is the ONLY mechanism through which actual code is written.

**Critical Principle**: The orchestrator NEVER writes code. It creates precise instructions and sends them to remote agents who execute the coding work.

## Prerequisites

- AI Maestro messaging system (AMP) running
- Python 3.9+ for LSP management scripts
- Remote agents registered and available
- GitHub CLI (gh) for issue management

## Output

| Output Type | Format | Location |
|-------------|--------|----------|
| Agent roster | JSON file | `agent_roster.json` |
| Task delegation messages | AI Maestro message | Sent via API |
| Progress reports | AI Maestro message | Received via API |
| Verification loop state | JSON tracking | In-memory or file |
| Escalation messages | AI Maestro message | Sent to orchestrator-master |

## Instructions

Follow these steps when coordinating remote agents:

1. Verify AI Maestro is running and remote agents are registered
2. Review the task requirements and prepare delegation instructions
3. Include ACK protocol instructions in every task message (see MANDATORY section below)
4. Send task delegation message via AI Maestro using the `agent-messaging` skill with complete instruction format
5. Wait for agent acknowledgment (timeout: 5 minutes)
6. Monitor progress proactively every 10-15 minutes during active work
7. Enforce 4-verification-loop protocol before approving any PR requests
8. Review completion reports against acceptance criteria
9. Escalate to user when architecture/security decisions are needed

---

## Checklist

Copy this checklist and track your progress:

- [ ] AI Maestro messaging system is running and accessible
- [ ] Remote agents are registered and available in agent roster
- [ ] Task delegation includes ACK protocol instructions block
- [ ] Task delegation includes PR notification requirement
- [ ] Task delegation includes complete instruction format (context, scope, interface, files, tests, completion criteria)
- [ ] Agent acknowledgment received within 5 minutes
- [ ] Proactive progress monitoring active (polling every 10-15 minutes)
- [ ] 4-verification-loop protocol enforced before PR approval
- [ ] Completion report reviewed against acceptance criteria
- [ ] LSP servers verified for agent's working language
- [ ] All escalations resolved before considering task complete

---

## Quick Reference: Core Protocols

| Protocol | Reference | Use When |
|----------|-----------|----------|
| Acknowledgment | [echo-acknowledgment-protocol.md](./references/echo-acknowledgment-protocol.md) | Task requires confirmation of receipt |
| 4-Verification Loops | [verification-loops-protocol.md](./references/verification-loops-protocol.md) | Agent requests PR permission |
| Progress Monitoring | [progress-monitoring-protocol.md](./references/progress-monitoring-protocol.md) | Tracking agent progress |
| Error Handling | [error-handling-protocol.md](./references/error-handling-protocol.md) | Agent reports being blocked |
| Escalation | [escalation-procedures.md](./references/escalation-procedures.md) | Issue requires user decision |

---

## MANDATORY: Acknowledgment Protocol

**CRITICAL**: Remote agents DO NOT have this skill. The orchestrator MUST teach them the ACK protocol BY INCLUDING IT IN EVERY TASK DELEGATION MESSAGE.

**ACK template to copy-paste**: See [echo-acknowledgment-protocol.md](./references/echo-acknowledgment-protocol.md) section 2.3 for the exact template block.

**Full protocol details**: [echo-acknowledgment-protocol.md](./references/echo-acknowledgment-protocol.md)
- 1.0 Purpose and triggers
- 2.0 Message Types: Instructions vs Conversations
- 3.0 ACK Format and Examples (includes template block)
- 4.0 Timeout handling (5 min wait, reminder, reassign)
- 5.0 Proactive enforcement by orchestrator

---

## AI Maestro Messaging

**For messaging, use the official AI Maestro skill:** `~/.claude/skills/agent-messaging/SKILL.md`

### Message Types

| Type | Purpose | When to Use |
|------|---------|-------------|
| `task` | Assign new coding task | Starting work on feature/fix |
| `fix-request` | Request code fix | After PR review finds issues |
| `status-request` | Check on progress | No update received |
| `approval` | Approve completed work | After successful review |
| `escalation` | Escalate to user | Architecture/security decision |

**Full protocol details**: [messaging-protocol.md](./references/messaging-protocol.md)
- 1.0 Sending Messages
- 2.0 Message priorities and timeouts
- 3.0 Task Management messages
- 4.0 Status and Progress messages
- 5.0 Approvals and Rejections
- 6.0 Error Handling

---

## Task Instruction Format

Every task instruction MUST include:
1. **ACK Instructions Block** (at top)
2. **PR Notification Requirement** (mandatory)
3. **Context** - What problem is being solved
4. **Scope** - Exact boundaries (DO/DO NOT lists)
5. **Interface Contract** - Input/output specifications
6. **Files to Modify** - Specific files in scope
7. **Test Requirements** - What tests must pass
8. **Completion Criteria** - How to know when done

**Full template and examples**: [task-instruction-format.md](./references/task-instruction-format.md)
- 1.0 Complete instruction template
- 2.0 Example filled-in instruction
- 3.0 Config reference patterns
- 4.0 Error states and escalation

---

## Agent Response Templates

Include template references in EVERY task delegation:

| Template | Path | Purpose |
|----------|------|---------|
| ACK Response | `templates/ack-response.md` | How to acknowledge task receipt |
| Completion Report | `templates/completion-report.md` | How to report task completion |
| Status Update | `templates/status-update.md` | How to send progress updates |

**Full details**: [agent-response-templates.md](./references/agent-response-templates.md)
- 1.0 Available templates
- 2.0 Including templates in delegations
- 3.0 Generating ad-hoc skills for complex tasks

---

## Agent Onboarding

Before any agent can receive real tasks, they must complete onboarding.

**Quick flow**:
1. Agent reads required documentation
2. Agent sets up environment
3. Agent completes verification task
4. Agent sends registration message
5. Orchestrator approves registration

**Full onboarding guide**: [agent-onboarding.md](./references/agent-onboarding.md)
- 1.0 Onboarding Checklist
- 2.0 Environment Setup
- 3.0 Verification Task
- 4.0 Required Reading List
- 5.0 Roster Registration

**Agent registration format**: [agent-registration.md](./references/agent-registration.md)
- 1.0 Registration fields
- 2.0 Agent Roster management
- 3.0 Availability states

---

## MANDATORY: 4-Verification-Loops Before PR

**CRITICAL**: For EACH TASK, require 4 verification loops BEFORE allowing PR creation. The agent will make 5 PR requests total - respond to the first 4 with "Check your changes for errors", then approve or reject on the 5th.

**Full protocol with table**: [verification-loops-protocol.md](./references/verification-loops-protocol.md)
- 1.0 Understanding the 5 PR requests cycle
- 2.0 Verification message templates
- 3.0 Tracking verification state per task
- 4.0 Summary table: The 5 PR Requests (orchestrator responses)
- 5.0 Enforcement rules (MUST/MUST NOT)

---

## Progress Monitoring (PROACTIVE)

**CRITICAL**: Do not wait passively for updates - actively reach out.

### Proactive Monitoring Principles

1. **PROACTIVELY poll** every 10-15 minutes during active work
2. **PROACTIVELY send** status request if no update received
3. **PROACTIVELY offer** solutions when agents report blockers
4. **PROACTIVELY verify** agents don't stop until ALL tasks complete

**Full protocol**: [progress-monitoring-protocol.md](./references/progress-monitoring-protocol.md)
- 1.0 Polling intervals by task type
- 2.0 Status request messages
- 3.0 Unblocking protocol
- 4.0 No-update escalation timeline

---

## Error Handling

Remote agents must follow **FAIL-FAST**:
- NO workarounds
- NO fallbacks
- If blocked, REPORT and WAIT

**Full protocol**: [error-handling-protocol.md](./references/error-handling-protocol.md)
- 1.0 FAIL-FAST principle
- 2.0 Error report message format
- 3.0 Orchestrator response procedures

---

## Overnight Autonomous Operation

**Prerequisites before leaving**:
1. Agent Roster verified
2. GitHub Project ready
3. Branch permissions set
4. AI Maestro running
5. Tasks queued

**Full guide**: [overnight-operation.md](./references/overnight-operation.md)
- 1.0 Prerequisites Checklist
- 2.0 User Handoff Protocol
- 3.0 Operation Flow
- 4.0 Escalation rules during autonomous operation
- 5.0 Recovery procedures

---

## Escalation Protocol

**Escalate to user when**:
- Architecture decisions not covered by methodology
- Security vulnerabilities discovered
- Dependency conflicts requiring user choice
- Test failures suggesting spec issues

**Full procedures**: [escalation-procedures.md](./references/escalation-procedures.md)
- 1.0 Escalation hierarchy (Level 0-2)
- 2.0 Escalation message formats
- 3.0 Escalation categories
- 4.0 Queue management

---

## LSP Server Requirements

Remote agents MUST have LSP servers installed for working languages. Verify LSP availability before assigning tasks.

**LSP References**:
- [lsp-servers-overview.md](./references/lsp-servers-overview.md) - Available plugins table, install commands, configuration
- [lsp-installation-guide.md](./references/lsp-installation-guide.md) - Per-language installation
- [lsp-enforcement-checklist.md](./references/lsp-enforcement-checklist.md) - Pre-assignment verification
- [orchestrator-lsp-management.md](./references/orchestrator-lsp-management.md) - Orchestrator LSP guide

---

## Toolchain Template System

Templates provide pre-configured setups for rapid project initialization.

| Category | Purpose |
|----------|---------|
| Toolchain | Language-specific dev configs |
| Handoff | Task delegation formats |
| Report | Status reporting formats |
| GitHub | Kanban and project tracking |

**Full guide**: [toolchain-template-system.md](./references/toolchain-template-system.md)
- 1.0 Template categories
- 2.0 Using compile_template.py
- 3.0 Including templates in delegations

**Template index**: `templates/TEMPLATE_INDEX.md`

---

## Document Storage Protocol

Documents are NEVER embedded in AI Maestro messages - only GitHub issue comment URLs.

**Rules**:
1. Upload to GitHub issue comment as attachment
2. Share URL only in messages
3. Require ACK with SHA256 hash
4. Lock files read-only after download

**Full protocol**: [document-storage-protocol.md](./references/document-storage-protocol.md)
- 1.0 Storage architecture
- 2.0 Document delivery rules
- 3.0 Orchestrator scripts
- 4.0 Remote agent storage skill

---

## Orchestrator Rules

**RULE 15 - No Implementation**: The orchestrator NEVER writes code, runs builds, edits source files, or sets up infrastructure. See [rule-15-no-implementation.md](./references/rule-15-no-implementation.md).

**RULE 14 - Immutable Requirements**: Every task delegation MUST include requirement references, forbidden actions, and escalation protocol. See [rule-14-immutable-requirements.md](./references/rule-14-immutable-requirements.md).

---

## Additional References

| Document | Use When |
|----------|----------|
| [central-configuration.md](./references/central-configuration.md) | Setting up `design/` directory structure |
| [change-notification-protocol.md](./references/change-notification-protocol.md) | Notifying agents of config changes |
| [artifact-sharing-protocol.md](./references/artifact-sharing-protocol.md) | Sharing build artifacts between agents |
| [bug-reporting-protocol.md](./references/bug-reporting-protocol.md) | Receiving and handling bug reports |
| [skill-format-comparison.md](./references/skill-format-comparison.md) | Comparing Open Spec vs Claude Code Skills |
| [skill-authoring-best-practices.md](./references/skill-authoring-best-practices.md) | Writing new skills |
| [skill-directory-structure.md](./references/skill-directory-structure.md) | Full skill directory structure |
| [ecos-replacement-protocol.md](./references/ecos-replacement-protocol.md) | Agent failure or context loss replacement |
| [agent-types.md](./references/agent-types.md) | Worker agent types and role boundaries |
| [assignment-workflow.md](./references/assignment-workflow.md) | Agent availability and task-agent matching |
| [agent-communication-templates.md](./references/agent-communication-templates.md) | Standard message templates for agent communication |

---

## Extended Coordination Protocols

For decision trees, mid-task updates, reassignment, blockers, multi-project coordination, and verification feedback, see [extended-coordination-protocols.md](./references/extended-coordination-protocols.md):
- 1. Core Decision Trees - When deciding whether to escalate, reassign, retry, or handle directly
- 2. Mid-Task Updates - When relaying requirement changes or priority shifts to agents mid-task
- 3. Reassignment Communication - When reassigning tasks between agents due to failure or recovery
- 4. Blocker Reports - When agents report blockers and the orchestrator must triage
- 5. Multi-Project Coordination - When tasks span multiple projects with cross-dependencies
- 6. Verification Feedback (Loops 2-4) - When providing progressive feedback during the 4-verification-loop cycle

---

## Examples

**Complete examples with code**: [examples-remote-coordination.md](./references/examples-remote-coordination.md)
- 1.0 Example: Onboard and Assign Task to New Agent (with curl commands)
- 2.0 Example: 4-Verification Loop Sequence (complete conversation flow, tracking table)
- 3.0 Example: Progress Monitoring Flow (polling commands, timeline, no-response handling)

---

## Error Handling

### Issue: AI Maestro messages not being delivered

**Cause**: API endpoint unreachable or agent identifier incorrect.

**Solution**:
1. Verify API health using the `agent-messaging` skill health check
2. Check agent ID format (use full session name, not alias)
3. Verify agent is registered in AI Maestro
4. Check network connectivity

### Issue: Agent responds but doesn't understand instructions

**Cause**: Instruction Verification Protocol not executed.

**Solution**:
1. Always execute Instruction Verification Protocol before implementation
2. Request agent to repeat key requirements in their own words
3. Correct any misunderstandings before authorizing work
4. Provide clarification for all questions asked

### Issue: Agent progress stalls without reporting blockers

**Cause**: Proactive polling not configured or agent not responding.

**Solution**:
1. Ensure 10-15 minute polling cycle is active
2. Include ALL mandatory poll questions (issues, unclear items, difficulties)
3. If no response after 2 polls, send escalation message using the `agent-messaging` skill
4. Consider reassigning if agent unresponsive

### Issue: Module assignment conflicts between agents

**Cause**: Same module assigned to multiple agents.

**Solution**:
1. Check current assignments: `/orchestration-status`
2. Use `/reassign-module` to move module to single agent
3. Notify previous assignee to stop work
4. Never assign same module to multiple agents simultaneously

### Issue: Agent completes work but PR fails verification

**Cause**: Acceptance criteria not met or 4-verification-loop not followed.

**Solution**:
1. Review PR against original acceptance criteria
2. Ensure agent followed 4-verification-loop protocol
3. Request fixes for failing criteria
4. Do NOT merge until all criteria pass

---

## Design Document Scripts

This script helps locate design documents when coordinating with remote agents:

| Script | Purpose | Usage |
|--------|---------|-------|
| `eoa_design_search.py` | Search design documents for task delegation | `python scripts/eoa_design_search.py --type <TYPE> --status <STATUS>` |

Use `eoa_design_search.py` when:
- Looking up design specifications to include in task delegations
- Finding related designs for context when assigning work
- Verifying design status before creating implementation tasks

### Script Location

The script is located at `../../scripts/eoa_design_search.py` relative to this skill.

---

## Resources

- [echo-acknowledgment-protocol.md](./references/echo-acknowledgment-protocol.md) - ACK protocol
- [verification-loops-protocol.md](./references/verification-loops-protocol.md) - 4-verification loops
- [progress-monitoring-protocol.md](./references/progress-monitoring-protocol.md) - Proactive monitoring
- [error-handling-protocol.md](./references/error-handling-protocol.md) - FAIL-FAST principle
- [escalation-procedures.md](./references/escalation-procedures.md) - Escalation hierarchy
- [agent-onboarding.md](./references/agent-onboarding.md) - Onboarding checklist
- [task-instruction-format.md](./references/task-instruction-format.md) - Instruction template
- [overnight-operation.md](./references/overnight-operation.md) - Autonomous operation
- [lsp-servers-overview.md](./references/lsp-servers-overview.md) - LSP requirements
- [ecos-replacement-protocol.md](./references/ecos-replacement-protocol.md) - Agent replacement
- [agent-types.md](./references/agent-types.md) - Agent type definitions
- [assignment-workflow.md](./references/assignment-workflow.md) - Agent assignment
- [agent-communication-templates.md](./references/agent-communication-templates.md) - Communication templates
