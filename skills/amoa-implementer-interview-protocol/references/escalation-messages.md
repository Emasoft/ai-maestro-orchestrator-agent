# Escalation Message Templates

## Table of Contents

- [Design Issues → Architect](#design-issues--architect)
- [Immutable Requirement Issues → Manager → User](#immutable-requirement-issues--manager--user)
- [PROCEED Message](#proceed-message)
- [APPROVED Message](#approved-message)
- [REVISE Message](#revise-message)

## Design Issues → Architect

If implementer identifies design incompatibilities:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "orchestrator",
  "to": "architect",
  "subject": "Design Review Required: {TASK_ID}",
  "priority": "high",
  "content": {
    "type": "request",
    "message": "Implementer identified design issue. Task: {TASK_ID}. Issue: {DESCRIPTION}. Please review and advise.",
    "data": {
      "task_id": "{TASK_ID}",
      "implementer": "{AGENT_NAME}",
      "concern": "{IMPLEMENTER_CONCERN}",
      "design_doc": "{DESIGN_DOC_PATH}"
    }
  }
}
```

## Immutable Requirement Issues → Manager → User

If implementer identifies issues with USER requirements:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "orchestrator",
  "to": "assistant-manager",
  "subject": "User Decision Required: Requirement Issue",
  "priority": "urgent",
  "content": {
    "type": "approval_request",
    "message": "Implementer identified issue with immutable requirement. User decision required.",
    "data": {
      "task_id": "{TASK_ID}",
      "requirement_id": "REQ-XXX",
      "requirement_text": "{EXACT_USER_QUOTE}",
      "issue": "{IMPLEMENTER_CONCERN}",
      "options": [
        "A. Proceed as specified (accept risk)",
        "B. Modify requirement",
        "C. Cancel task"
      ]
    }
  }
}
```

**CRITICAL**: NEVER modify an immutable user requirement without explicit user approval obtained through the Manager.

## PROCEED Message

Only after satisfactory interview:

```markdown
## PROCEED: {TASK_ID}

Your understanding is confirmed. You may begin implementation.

**Reminders**:
- Follow the design document
- Respect immutable requirements (see FORBIDDEN section)
- Report blockers immediately
- Report completion when done (do NOT create PR yet)

Good luck!
```

## APPROVED Message

Only when ALL verification passes:

```markdown
## APPROVED: {TASK_ID}

Verification complete. You may now create the Pull Request.

**PR Requirements**:
- Title: [Type] {Brief description} (#{ISSUE_NUMBER})
- Link to issue: "Closes #{ISSUE_NUMBER}"
- Include test evidence in description
- Request review from appropriate reviewers

After PR creation, report the PR number to me.
Your responsibility ends when the PR is created.
The Integrator (EIA) will handle review and merge.
```

## REVISE Message

When issues found:

```markdown
## REVISE: {TASK_ID}

Verification found issues that must be addressed:

**Issues**:
1. {ISSUE_1}
2. {ISSUE_2}

**Required Actions**:
- {ACTION_1}
- {ACTION_2}

Do NOT create a PR until these are resolved.
Report `[DONE]` again when ready for re-verification.
```

## Decision Trees and Response Templates for Escalations

### Escalation Path Selection Decision Tree

```
Agent reports concern during interview that requires escalation
├─ What type of concern?
│   ├─ Design concern (architecture, patterns, component boundaries)
│   │   → Route to: ECOS → EAA (Architect Agent)
│   │   → Message type: "request", priority: "high"
│   │   → Include: agent's concern text, task context, affected components
│   │   → Expected response: architectural guidance or revised design
│   │   → Timeout: 30 min → If no response, send reminder
│   │
│   ├─ Requirement concern (ambiguous spec, contradictory requirements)
│   │   → Is it an immutable requirement (user-specified, cannot change)?
│   │   │   ├─ Yes → Route to: ECOS → EAMA → User
│   │   │   │         → Priority: "urgent" (blocks agent work)
│   │   │   │         → Include: exact ambiguity, proposed interpretations, impact of each
│   │   │   └─ No (flexible requirement) → EOA decides pragmatically
│   │   │       → Document decision rationale in task notes
│   │   │       → Inform agent of decision → Agent continues
│   │   │
│   └─ Capability concern (agent lacks tools/skills/access needed)
│       → Route to: ECOS
│       → Priority: "high"
│       → Include: what capability is needed, why, alternatives considered
│       → ECOS options: provide access / spawn specialized agent / adjust task scope
```

### EAA Response Template (Design Issue Resolution)

When EAA responds to a design escalation, EOA should expect this format and relay to the agent:

```json
{
  "type": "response",
  "message": "EAA has reviewed your design concern and provided guidance.",
  "data": {
    "original_concern": "<the concern text from agent>",
    "decision": "APPROVED | REVISED | INVESTIGATE",
    "guidance": "<EAA's architectural guidance text>",
    "revised_approach": "<if decision=REVISED, the new approach to follow>",
    "investigation_questions": "<if decision=INVESTIGATE, questions EAA needs answered>"
  }
}
```

### EAMA Response Template (Immutable Requirement Resolution)

When EAMA relays user's decision on an immutable requirement question:

```json
{
  "type": "response",
  "message": "User has provided a decision on the requirement question.",
  "data": {
    "original_question": "<the requirement ambiguity reported>",
    "user_decision": "<user's chosen interpretation or new requirement text>",
    "additional_context": "<any extra context the user provided>",
    "applies_to": ["<task_id_1>", "<task_id_2>"]
  }
}
```
