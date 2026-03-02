# Task Acknowledgment: {{TASK_ID}}

**Extends**: [handoff-protocols.md](../../../eoa-agent-replacement/references/handoff-protocols.md)

---

## DELIVERY INSTRUCTIONS (DO NOT INCLUDE IN COMPILED OUTPUT)

**This template is used ONLY for responding to `document_delivery` messages.**

**When to send ACK:**
- ✅ **YES**: When you receive a message with `"type": "document_delivery"` and `"subject": "document_delivery"`
- ❌ **NO**: For normal conversation messages, progress updates, or questions

**ACK is required for:**
- Task delegation documents
- Formal handoff documents
- Critical policy/protocol updates

**ACK is NOT required for:**
- Status updates
- Informal questions
- General chat messages
- Progress reports

**Protocol Reference**: See [../protocols/DOCUMENT_DELIVERY_PROTOCOL.md](../protocols/DOCUMENT_DELIVERY_PROTOCOL.md)

**This ACK, once compiled, MUST be:**
1. **Saved to file**: `ack-{{TASK_ID}}.md`
2. **Uploaded to GitHub issue #{{ISSUE_NUMBER}}** as comment (optional but recommended)
3. **Sent via AI Maestro** with brief summary (NOT full document)

**Message Format**:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "{{SENDER_SESSION}}",
  "subject": "ack_received",
  "priority": "normal",
  "content": {
    "type": "ack",
    "message": "ACK {{TASK_ID}} - Status: {{ACK_STATUS}}"
  }
}
```

---

## ACK Header

**Task ID**: `{{TASK_ID}}`
**Agent**: {{AGENT_NAME}} ({{AGENT_SESSION}})
**ACK Date**: {{ACK_DATE}}
**ACK Time**: {{ACK_TIME}}
**Response Time**: {{RESPONSE_TIME_MINUTES}} minutes

---

## Status: {{ACK_STATUS}}

✅ **ACCEPTED** - Task understood and accepted
⏸️ **NEEDS_CLARIFICATION** - Questions before proceeding
❌ **REJECTED** - Cannot accept task (see reason)

---

## Task Understanding

### Objectives Understood
{{OBJECTIVES_CONFIRMED}}

### Acceptance Criteria Understood
{{ACCEPTANCE_CRITERIA_CONFIRMED}}

### Toolchain Requirements Understood
**Toolchain**: {{TOOLCHAIN_TYPE}}
**Template**: [{{TOOLCHAIN_TEMPLATE_PATH}}]({{TOOLCHAIN_TEMPLATE_PATH}})

- [{{LANG_CHECK}}] Language: {{LANGUAGE}} {{LANGUAGE_VERSION}}
- [{{PKG_CHECK}}] Package Manager: {{PACKAGE_MANAGER}}
- [{{BUILD_CHECK}}] Build Tool: {{BUILD_TOOL}}
- [{{TEST_CHECK}}] Test Framework: {{TEST_FRAMEWORK}}
- [{{LINT_CHECK}}] Linter/Formatter: {{LINTER_FORMATTER}}

### Verification Commands Confirmed
- [{{VERIFY_CHECK}}] `{{VERIFY_ALL_CMD}}`
- [{{TEST_CHECK}}] `{{TEST_CMD}}`
- [{{FORMAT_CHECK}}] `{{FORMAT_CMD}}`
- [{{LINT_CHECK}}] `{{LINT_CMD}}`

---

## Environment Status

### Toolchain Availability
```bash
$ {{VERIFY_ALL_CMD}}
{{VERIFY_OUTPUT}}
```

**Status**: {{TOOLCHAIN_STATUS}} ✅/⚠️/❌

### Environment Checks
- [{{ENV_LANG}}] {{LANGUAGE}} {{LANGUAGE_VERSION}} installed
- [{{ENV_PKG}}] {{PACKAGE_MANAGER}} available
- [{{ENV_BUILD}}] {{BUILD_TOOL}} available
- [{{ENV_TEST}}] {{TEST_FRAMEWORK}} available
- [{{ENV_LINT}}] {{LINTER_FORMATTER}} available

### Repository Status
- [{{REPO_CLONE}}] Repository cloned/accessible
- [{{REPO_BRANCH}}] Base branch `{{BASE_BRANCH}}` checked out
- [{{REPO_DEPS}}] Dependencies installed
- [{{REPO_CLEAN}}] Working directory clean

---

## Task Scope (per RULE 13 - no time estimates)

**Start Date**: {{START_DATE}}
**Complexity**: {{COMPLEXITY_TIER}}
**Status**: In Progress

### Milestones
{{MILESTONE_LIST}}

---

## Questions / Clarifications Needed

{{QUESTIONS_LIST}}

### Blockers Identified
{{BLOCKERS_IDENTIFIED}}

### Assumptions Made
{{ASSUMPTIONS}}

---

## Communication Plan

**Progress Updates**: Every {{STATUS_UPDATE_FREQUENCY}}
**Update Channel**: Issue #{{ISSUE_NUMBER}}, {{COMMUNICATION_CHANNEL}}
**Blocker Escalation**: Immediate via [BLOCKER_REPORT_TEMPLATE.md](./BLOCKER_REPORT_TEMPLATE.md)

---

## Acceptance Confirmation

{{#if ACK_STATUS == "ACCEPTED"}}
✅ **I acknowledge receipt and accept this task.**

I understand:
- The task objectives and acceptance criteria
- The toolchain requirements and verification commands
- The git workflow and PR requirements
- The communication protocols
- The definition of done

I will:
- Follow the toolchain template at {{TOOLCHAIN_TEMPLATE_PATH}}
- Run verification commands before completion
- Create completion report using COMPLETION_REPORT_TEMPLATE.md
- Update issue #{{ISSUE_NUMBER}} with progress
- Report blockers immediately

**Signature**: {{AGENT_NAME}}
**Date**: {{ACK_DATE}}
{{/if}}

{{#if ACK_STATUS == "NEEDS_CLARIFICATION"}}
⏸️ **I need clarification before proceeding.**

See "Questions / Clarifications Needed" section above.

**Awaiting Response**: {{AWAITING_FROM}}
{{/if}}

{{#if ACK_STATUS == "REJECTED"}}
❌ **I cannot accept this task.**

**Reason**: {{REJECTION_REASON}}

**Suggested Alternative**: {{ALTERNATIVE_SUGGESTION}}
{{/if}}

---

## Next Actions

{{NEXT_ACTIONS}}

---

**ACK Version**: 1.0.0
**Template**: [ACK_TEMPLATE.md](./ACK_TEMPLATE.md)
**Received Task**: [TASK_DELEGATION: {{TASK_ID}}]({{TASK_DELEGATION_URL}})
