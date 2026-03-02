# ECOS Agent Replacement Protocol


## Contents

- [Overview](#overview)
- [ECOS Notification Format](#ecos-notification-format)
  - [Urgency Levels](#urgency-levels)
- [Replacement Protocol Steps](#replacement-protocol-steps)
  - [Step 1: Acknowledge ECOS Notification](#step-1-acknowledge-ecos-notification)
  - [Step 2: Compile Context for Failed Agent](#step-2-compile-context-for-failed-agent)
  - [Step 3: Generate Handoff Document](#step-3-generate-handoff-document)
- [Task Assignment](#task-assignment)
- [Work Completed](#work-completed)
- [Work Remaining](#work-remaining)
- [Context Transfer](#context-transfer)
- [Critical Information](#critical-information)
- [Verification Requirements](#verification-requirements)
- [Contact](#contact)
  - [Step 4: Reassign GitHub Project Tasks](#step-4-reassign-github-project-tasks)
  - [Step 5: Send Handoff to Replacement Agent](#step-5-send-handoff-to-replacement-agent)
  - [Step 6: Wait for Acknowledgment](#step-6-wait-for-acknowledgment)
  - [Step 7: Confirm to ECOS](#step-7-confirm-to-ecos)
- [Quick Command Reference](#quick-command-reference)
- [Critical Rules](#critical-rules)
  - [Rule 1: Preserve Task UUIDs](#rule-1-preserve-task-uuids)
  - [Rule 2: Reset Instruction Verification](#rule-2-reset-instruction-verification)
  - [Rule 3: Include ALL Context](#rule-3-include-all-context)
  - [Rule 4: Update Orchestrator State File](#rule-4-update-orchestrator-state-file)
  - [Rule 5: RULE 14 Applies Through Replacement](#rule-5-rule-14-applies-through-replacement)
- [IRON RULE: USER REQUIREMENTS ARE IMMUTABLE](#iron-rule-user-requirements-are-immutable)
- [Emergency Procedures](#emergency-procedures)
  - [If Replacement Agent Also Fails](#if-replacement-agent-also-fails)
  - [If Handoff Information Incomplete](#if-handoff-information-incomplete)
  - [If Original Task Requirements Unclear](#if-original-task-requirements-unclear)
- [Audit Trail](#audit-trail)
- [Handoff Quality Checklist](#handoff-quality-checklist)
- [Context Transfer Best Practices](#context-transfer-best-practices)
  - [DO Include](#do-include)
  - [DO NOT Include](#do-not-include)
- [Success Criteria](#success-criteria)
- [See Also](#see-also)

## Overview

When ECOS (Emergency Context-loss Operations System) detects an agent failure or initiates a replacement, the orchestrator must execute a structured handoff protocol to transfer tasks and context to a replacement agent without losing work progress.

## ECOS Notification Format

ECOS sends replacement notifications via AI Maestro with message type `agent_replacement`:

```json
{
  "content": {
    "type": "agent_replacement",
    "failed_agent": {
      "session": "libs-feature-implementer",
      "agent_id": "implementer-1",
      "failure_reason": "context_exhaustion|session_crash|timeout"
    },
    "replacement_agent": {
      "session": "libs-feature-implementer-backup",
      "agent_id": "implementer-2"
    },
    "urgency": "immediate|prepare|when_available"
  }
}
```

### Urgency Levels

| Level | Meaning | Response Time |
|-------|---------|---------------|
| `immediate` | Agent crashed mid-task, work blocked | < 5 minutes |
| `prepare` | Agent approaching limits, replacement needed soon | < 30 minutes |
| `when_available` | Planned rotation, no urgency | Next available slot |

## Replacement Protocol Steps

### Step 1: Acknowledge ECOS Notification

**Immediately** send an acknowledgment message to ECOS using the `agent-messaging` skill:
- **Recipient**: `ecos-monitor`
- **Subject**: "ACK: Agent Replacement"
- **Content**: "Replacement protocol initiated for [failed_agent_session]"
- **Type**: `acknowledgment`
- **Priority**: `high`

**Verify**: confirm message delivery.

### Step 2: Compile Context for Failed Agent

Gather all information about the failed agent's work:

**Tasks:**
- GitHub Project issues assigned to failed agent
- Current task status (in-progress, blocked, waiting_review)
- Task dependencies and blocking relationships

**Progress:**
- Last completion report received
- Work completed vs. remaining
- Files modified/created
- Test results (if available)

**Communications:**
- All AI Maestro messages sent to/from failed agent
- Any clarifications or instruction modifications
- Reported blockers or issues

**State:**
- Git branch name (if applicable)
- Last known working state
- Any work-in-progress commits

### Step 3: Generate Handoff Document

Use the command:

```bash
/eoa-generate-replacement-handoff \
  --failed-agent implementer-1 \
  --new-agent implementer-2 \
  --include-tasks \
  --include-context
```

**Handoff document structure:**

```markdown
# Agent Replacement Handoff
Generated: [timestamp]
From: [failed_agent_session]
To: [replacement_agent_session]

## Task Assignment
- Task ID: [GitHub issue number]
- Task UUID: [preserve from original]
- Description: [full task description]
- Acceptance Criteria: [checklist]
- Dependencies: [list]

## Work Completed
- Files Modified: [list with descriptions]
- Tests Written: [list]
- Progress: [percentage estimate]
- Last Report: [link or inline]

## Work Remaining
- [ ] [Specific subtask 1]
- [ ] [Specific subtask 2]
- [ ] [Test coverage gaps]
- [ ] [Documentation updates needed]

## Context Transfer
- Original Instructions: [link to AI Maestro message]
- Clarifications Received: [numbered list]
- Known Blockers: [list with status]
- Technical Decisions Made: [list with rationale]

## Critical Information
- User Requirements (IMMUTABLE): [exact requirements from RULE 14]
- Integration Points: [other agents/modules affected]
- Testing Requirements: [TDD verification checklist]

## Verification Requirements
The replacement agent MUST complete Instruction Verification Protocol:
1. Read and acknowledge this handoff
2. Confirm understanding of task requirements
3. Confirm understanding of completed work
4. Identify any missing information
5. Request clarification if needed

## Contact
- Orchestrator Session: [your session name]
- Failed Agent Last Contact: [timestamp]
- GitHub Project: [link]
- GitHub Issue: [link]
```

### Step 4: Reassign GitHub Project Tasks

Update kanban board to reflect the replacement:

```bash
/eoa-reassign-kanban-tasks \
  --from-agent implementer-1 \
  --to-agent implementer-2 \
  --handoff-url [URL to handoff doc]
```

This command:
- Updates GitHub issue assignee
- Adds comment linking to handoff document
- Preserves task UUID and history
- Updates project board labels (if using agent-specific labels)

### Step 5: Send Handoff to Replacement Agent

Send via AI Maestro:

Send a handoff message to the replacement agent using the `agent-messaging` skill:
- **Recipient**: `implementer-2` (the replacement agent)
- **Subject**: "Task Handoff from [failed_agent]"
- **Content**: "You are replacing [failed_agent] on task [task_id]. Full handoff document: [URL]. CRITICAL: Read entire handoff before starting work. User requirements are immutable (RULE 14). Acknowledge receipt and complete Instruction Verification Protocol."
- **Type**: `replacement_handoff`
- **Priority**: `high`

**Verify**: confirm message delivery.

### Step 6: Wait for Acknowledgment

The replacement agent MUST send acknowledgment confirming:
1. Handoff document received and read
2. Understanding of task requirements
3. Understanding of completed work
4. Any questions or clarifications needed

**Do NOT proceed** until acknowledgment received.

### Step 7: Confirm to ECOS

After replacement agent acknowledges:

Send a completion confirmation to ECOS using the `agent-messaging` skill:
- **Recipient**: `ecos-monitor`
- **Subject**: "Replacement Complete"
- **Content**: "Replacement protocol completed. New agent [replacement_agent_session] acknowledged and ready. Task UUID [task_uuid] preserved."
- **Type**: `completion`
- **Priority**: `normal`

**Verify**: confirm message delivery.

## Quick Command Reference

| Command | Purpose |
|---------|---------|
| `/eoa-generate-replacement-handoff` | Generate comprehensive handoff document |
| `/eoa-reassign-kanban-tasks` | Update GitHub Project assignments |
| `/eoa-verify-replacement-ready` | Check if replacement agent is ready |
| `/eoa-abort-replacement` | Cancel replacement (emergency only) |

## Critical Rules

### Rule 1: Preserve Task UUIDs

The replacement agent continues the **same task**, not a new one. Task UUID must be preserved across the handoff to maintain tracking and audit trail.

**Why**: GitHub Projects, AI Maestro logs, and orchestrator state files all reference task UUIDs. Changing the UUID breaks all tracking.

### Rule 2: Reset Instruction Verification

Even though the replacement agent receives context, it MUST go through the full Instruction Verification Protocol as if receiving a new task assignment.

**Why**: Context transfer is never perfect. Verification ensures the replacement agent actually understands what to do.

### Rule 3: Include ALL Context

The handoff document must contain everything the replacement agent needs to continue work without additional research.

**Minimum Required Context:**
- Original task instructions (verbatim)
- All clarifications received from orchestrator
- Complete list of files modified/created
- Test results and coverage status
- Technical decisions made and rationale
- Known blockers and their status
- Integration points with other agents

### Rule 4: Update Orchestrator State File

Track the replacement in `docs_dev/orchestration-state.json`:

```json
{
  "tasks": {
    "task-uuid-123": {
      "status": "in-progress",
      "assigned_agent": "implementer-2",
      "replacements": [
        {
          "timestamp": "2026-02-05T14:30:00Z",
          "from_agent": "implementer-1",
          "to_agent": "implementer-2",
          "reason": "context_exhaustion",
          "handoff_url": "docs_dev/handoff-implementer-1-to-2.md"
        }
      ]
    }
  }
}
```

### Rule 5: RULE 14 Applies Through Replacement

User requirements remain **absolutely immutable** through agent replacement. The handoff document MUST include:

```markdown
## IRON RULE: USER REQUIREMENTS ARE IMMUTABLE
- The user specified: [exact requirement from original instructions]
- You MUST implement exactly as specified
- You CANNOT substitute technologies
- You CANNOT reduce scope
- If you encounter issues, STOP and REPORT - do NOT work around them
```

## Emergency Procedures

### If Replacement Agent Also Fails

If the replacement agent also fails (crashes, exhausts context, etc.):

1. **STOP** - Do not attempt automatic re-replacement
2. **ALERT** user immediately via notification
3. **PRESERVE** all handoff documents and state files
4. **DOCUMENT** both failures in incident report
5. **WAIT** for user guidance before proceeding

**Why**: Two consecutive failures indicate a deeper issue (task too complex, requirements unclear, systemic problem). Automatic retry would likely fail again.

### If Handoff Information Incomplete

If the replacement agent reports missing critical information:

1. **STOP** work immediately
2. **Document** missing information in handoff addendum
3. **Attempt recovery** from GitHub comments, commit messages, CI logs
4. **If recovery impossible**: Escalate to user
5. **Do NOT** instruct replacement agent to "figure it out" or "start fresh"

### If Original Task Requirements Unclear

If replacement agent cannot understand what the failed agent was implementing:

1. **STOP** replacement handoff
2. **Re-analyze** original user requirements
3. **Create NEW** task instructions from scratch
4. **Treat as fresh assignment**, not a replacement
5. **Discard** incomplete work if it doesn't match requirements

## Audit Trail

Every replacement must be fully documented for audit:

**Documents to Preserve:**
- ECOS notification (original message)
- Handoff document with timestamp
- Replacement agent acknowledgment
- GitHub issue reassignment comment
- Orchestration state file update
- Completion confirmation to ECOS

**Storage Location:**
```
docs_dev/replacements/
├── [timestamp]-[failed_agent]-to-[replacement_agent]/
│   ├── ecos-notification.json
│   ├── handoff.md
│   ├── acknowledgment.json
│   └── state-diff.json
```

## Handoff Quality Checklist

Before sending handoff to replacement agent, verify:

- [ ] Task UUID preserved from original
- [ ] User requirements included verbatim (RULE 14)
- [ ] All completed work documented
- [ ] All remaining work itemized
- [ ] All technical decisions explained
- [ ] All blockers documented with status
- [ ] Integration points identified
- [ ] GitHub issue reassigned
- [ ] Orchestrator state file updated
- [ ] ECOS acknowledged
- [ ] Handoff URL accessible to replacement agent

## Context Transfer Best Practices

### DO Include

- **Verbatim requirements**: Exact user specifications
- **Decision rationale**: Why choices were made
- **Failed approaches**: What was tried and didn't work
- **Technical constraints**: Environment, dependencies, compatibility
- **Integration contracts**: APIs, interfaces, data formats
- **Test coverage status**: What's tested, what's not

### DO NOT Include

- **Assumptions**: If failed agent "probably meant to do X"
- **Workarounds**: Alternative approaches not approved by user
- **Speculation**: Guesses about what should happen next
- **Incomplete thoughts**: Half-written ideas or notes

## Success Criteria

Replacement handoff is successful when:

1. Replacement agent acknowledges receipt
2. Replacement agent confirms understanding
3. Replacement agent completes Instruction Verification Protocol
4. Replacement agent begins work without additional clarification requests
5. No duplicate work occurs (replacement continues from correct point)
6. Task UUID maintained throughout

## See Also

- [agent-onboarding.md](./agent-onboarding.md) - Initial agent assignment protocol
- [messaging-protocol.md](./messaging-protocol.md) - AI Maestro communication patterns
- [task-instruction-format.md](./task-instruction-format.md) - Instruction templates
