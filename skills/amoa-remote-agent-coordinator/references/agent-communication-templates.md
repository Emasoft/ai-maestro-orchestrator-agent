# Agent Communication Templates Reference

This document provides message templates for communicating with AI agents via AI Maestro.

---

## Contents

- 6.1 AI Agent Assignment Message Template
- 6.2 AI Agent Verification Request Template
- 6.3 AI Agent Progress Poll Template
- 6.4 AI Agent Issue Response Template
- 6.5 AI Agent Completion Acknowledgment Template
- 6.6 AI Agent Reassignment Notification Template
- 6.7 AI Agent Urgent Message Template
- 6.8 Message Priority Guidelines

---

## 6.1 AI Agent Assignment Message Template

Use this template when assigning a module to an AI agent.

```markdown
Subject: [TASK] Module: {module_name} - UUID: {task_uuid}

## Assignment

You have been assigned to implement: **{module_name}**

GitHub Issue: {issue_url}
Task UUID: {task_uuid}
Priority: {priority}

## Module Description

{module_description}

## Requirements Summary

{requirements_list}

## Acceptance Criteria

{acceptance_criteria}

## Dependencies

{dependencies_or_none}

## Estimated Effort

{estimated_hours} hours

## MANDATORY: Instruction Verification

Before you begin implementation, please:

1. **Repeat the key requirements** in your own words (3-5 bullet points)
2. **List any questions** you have about the requirements
3. **Confirm your understanding** of the acceptance criteria

I will verify your understanding before authorizing implementation.

Reply with your understanding summary.
```

**Variables to fill**:
- `{module_name}`: Name of the module (e.g., "auth-core")
- `{task_uuid}`: Generated task UUID (e.g., "task-a1b2c3d4")
- `{issue_url}`: GitHub issue URL
- `{priority}`: high, medium, low
- `{module_description}`: Brief description
- `{requirements_list}`: Numbered requirements
- `{acceptance_criteria}`: Checkbox list
- `{dependencies_or_none}`: Dependencies or "None"
- `{estimated_hours}`: Estimated hours

---

## 6.2 AI Agent Verification Request Template

Use when agent's initial understanding needs correction.

```markdown
Subject: [CORRECTION] Module: {module_name} - UUID: {task_uuid}

## Corrections Required

Your understanding has some issues that need correction:

{corrections_list}

## Please Revise

Please provide a revised understanding summary addressing these corrections.

Do NOT begin implementation until your understanding is verified.
```

**Variables to fill**:
- `{module_name}`: Module name
- `{task_uuid}`: Task UUID
- `{corrections_list}`: List of corrections needed

**Example corrections_list**:
```markdown
**Incorrect:**
- You stated "1 hour expiry" but the requirement is "24 hours expiry"

**Missing:**
- You did not mention the refresh token requirement
- Error handling specification was not included

**Misunderstood:**
- The token should use RS256, not HS256
```

---

## 6.3 AI Agent Progress Poll Template

Use for regular progress checks (every 10-15 minutes).

```markdown
Subject: [POLL] Module: {module_name} - Progress Check #{poll_number}

## Status Request

Please provide your current status:

1. **Current progress**: What percentage complete? What specific items are done?
2. **Next steps**: What are you working on right now?

## MANDATORY Questions (Answer ALL)

3. **Are there any issues or problems?**
   - Technical issues (code not working, tests failing)
   - Environmental problems (dependencies, configuration)
   - Dependency issues (waiting on other modules)

4. **Is anything unclear?**
   - Requirements ambiguity
   - Acceptance criteria questions
   - Expected behavior uncertainty

5. **Any unforeseen difficulties?**
   - Complexity higher than expected
   - Missing information discovered
   - Approach not working as planned

6. **Do you need anything from me?**
   - Documentation needed
   - Clarification required
   - Decision needed from orchestrator/user
   - Resources or access required

---

If all is clear with no blockers, reply:
"Progress: {X}%. No blockers. Proceeding as planned."

Expected response time: 5 minutes
Task UUID: {task_uuid}
```

**Variables to fill**:
- `{module_name}`: Module name
- `{poll_number}`: Sequential poll number
- `{task_uuid}`: Task UUID

---

## 6.4 AI Agent Issue Response Template

Use when responding to an issue reported by the agent.

```markdown
Subject: [RESPONSE] Module: {module_name} - Issue Resolution

## Regarding Your Issue

You reported: "{issue_summary}"

## Resolution

{resolution_details}

## Additional Context

{additional_context_if_any}

## Next Steps

{next_steps}

---

Please confirm you can proceed with this resolution.
If you have further questions, ask now.

Task UUID: {task_uuid}
```

**Variables to fill**:
- `{module_name}`: Module name
- `{issue_summary}`: Brief summary of reported issue
- `{resolution_details}`: The solution or clarification
- `{additional_context_if_any}`: Supporting information
- `{next_steps}`: What agent should do next
- `{task_uuid}`: Task UUID

---

## 6.5 AI Agent Completion Acknowledgment Template

Use when agent reports completion.

```markdown
Subject: [ACK] Module: {module_name} - Completion Received

## Completion Acknowledged

Thank you for completing the implementation of **{module_name}**.

## Verification

I will now verify:
- [ ] All acceptance criteria met
- [ ] Code review passed
- [ ] Tests passing
- [ ] Documentation complete
- [ ] GitHub issue updated

## Next Steps

{next_steps}

I will update you on verification results shortly.

Task UUID: {task_uuid}
```

**Variables to fill**:
- `{module_name}`: Module name
- `{next_steps}`: What happens after verification
- `{task_uuid}`: Task UUID

---

## 6.6 AI Agent Reassignment Notification Template

Use when reassigning a module from one agent to another.

```markdown
Subject: [REASSIGN] Module: {module_name} - Task Reassigned

## Reassignment Notice

The module **{module_name}** has been reassigned.

**Reason**: {reassignment_reason}

## For Previous Agent ({previous_agent})

Please:
1. Stop work on this module
2. Provide summary of work completed
3. Note any important findings or issues
4. Push any work in progress to a branch

## For New Agent ({new_agent})

You have been assigned this module. Details will follow in a separate assignment message.

Task UUID: {task_uuid}
```

**Variables to fill**:
- `{module_name}`: Module name
- `{reassignment_reason}`: Why reassignment is happening
- `{previous_agent}`: Previous agent ID
- `{new_agent}`: New agent ID
- `{task_uuid}`: Task UUID

---

## 6.7 AI Agent Urgent Message Template

Use for urgent communications requiring immediate attention.

```markdown
Subject: [URGENT] Module: {module_name} - Immediate Attention Required

## URGENT

{urgent_message}

## Required Action

{required_action}

## Deadline

{deadline}

---

Please respond immediately.

Task UUID: {task_uuid}
```

**Variables to fill**:
- `{module_name}`: Module name
- `{urgent_message}`: The urgent message
- `{required_action}`: What agent must do
- `{deadline}`: When action is needed by
- `{task_uuid}`: Task UUID

---

## 6.8 Message Priority Guidelines

### Priority Levels

| Priority | Use When | Subject Prefix |
|----------|----------|----------------|
| `urgent` | Blocking issues, immediate action needed | `[URGENT]` |
| `high` | Task assignments, important updates | `[TASK]`, `[POLL]` |
| `normal` | Regular updates, acknowledgments | `[ACK]`, `[INFO]` |
| `low` | FYI messages, non-critical info | `[FYI]` |

### Subject Prefixes

| Prefix | Meaning |
|--------|---------|
| `[TASK]` | New task assignment |
| `[POLL]` | Progress check |
| `[CORRECTION]` | Understanding needs correction |
| `[RESPONSE]` | Response to agent's question |
| `[ACK]` | Acknowledgment |
| `[REASSIGN]` | Reassignment notice |
| `[URGENT]` | Immediate attention required |
| `[INFO]` | Informational message |
| `[FYI]` | For your information |

### Sending Messages via AI Maestro

Send messages using the `agent-messaging` skill with these fields:
- **Recipient**: the target agent session name
- **Subject**: subject line with appropriate prefix (e.g., `[TASK]`, `[PROGRESS]`, etc.)
- **Priority**: `normal`, `high`, or `urgent`
- **Content type**: the message type identifier
- **Message**: the message body text

**Verify**: confirm message delivery.

**Content types**:
- `assignment` - New task assignment
- `poll` - Progress poll
- `response` - Response to query
- `acknowledgment` - Acknowledging completion
- `notification` - General notification
- `urgent` - Urgent communication

---

## Decision Trees for Agent Communication

### Reassignment Decision Tree

When EOA needs to reassign a task from one agent to another, follow this decision tree:

```
Reassignment trigger (agent failure / agent overloaded / conflict detected)
├─ Is original agent still responsive?
│   ├─ Yes → Send Reassignment Notification to original agent (template 6.6)
│   │         ├─ Agent ACKs and sends work summary within 5 min
│   │         │   → Compile handoff context (work summary + original task + files touched)
│   │         │   → Select new agent (check availability, no file conflicts)
│   │         │   → Send Reassignment Assignment to new agent with full context
│   │         │   → Update kanban: old agent removed, new agent assigned
│   │         └─ Agent does not ACK within 5 min → Treat as unresponsive
│   │             → Compile context from last known state (kanban, commit history)
│   │             → Select new agent → Send assignment with partial context
│   │             → Flag to ECOS that original agent is unresponsive
│   └─ No (agent crashed/terminated) → Request ECOS for replacement agent
│       → Compile context from kanban + commit history + task description
│       → Wait for ECOS to spawn replacement
│       → Send fresh Task Assignment to replacement with compiled context
```

### Issue Response Decision Tree

When an agent reports an issue during implementation, follow this decision tree:

```
Agent reports issue (bug found / design question / requirement ambiguity)
├─ What type of issue?
│   ├─ Bug in existing code → Is it blocking the current task?
│   │   ├─ Yes (blocking) → Can agent work around it temporarily?
│   │   │   ├─ Yes → Instruct agent to document workaround and continue
│   │   │   │         → Create separate bug issue on GitHub
│   │   │   └─ No → Escalate to ECOS as blocker → Pause agent's task
│   │   └─ No (non-blocking) → Log issue → Create GitHub issue → Agent continues
│   ├─ Design question → Does EOA have authority to decide?
│   │   ├─ Yes (minor design choice) → Provide guidance → Agent continues
│   │   └─ No (architectural decision) → Escalate to ECOS for EAA review
│   │       → Pause affected subtask → Continue other subtasks if possible
│   └─ Requirement ambiguity → Is it an immutable requirement?
│       ├─ Yes → Escalate to ECOS → ECOS routes to EAMA → Wait for user decision
│       └─ No → Make pragmatic decision → Document decision rationale → Agent continues
```
