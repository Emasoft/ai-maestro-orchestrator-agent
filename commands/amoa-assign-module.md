---
name: eoa-assign-module
description: "Assign a module to a registered agent with Instruction Verification Protocol"
argument-hint: "<MODULE_ID> <AGENT_ID>"
allowed-tools: ["Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/eoa_assign_module.py:*)"]
---

# Assign Module Command

Assign a module to a registered agent and initiate the Instruction Verification Protocol.

## Usage

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_assign_module.py" $ARGUMENTS
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `MODULE_ID` | Yes | ID of the module to assign |
| `AGENT_ID` | Yes | ID of the registered agent |

## What This Command Does

1. **Validates Assignment**
   - Module exists and is pending
   - Agent is registered
   - Agent is not overloaded

2. **Creates Assignment Record**
   - Links module to agent
   - Generates task UUID
   - Sets initial status

3. **Sends Assignment Message** (AI agents)
   - Sends via AI Maestro using the `agent-messaging` skill
   - Includes GitHub Issue link
   - Includes task UUID
   - Requests instruction repetition

4. **Updates GitHub Issue** (human agents)
   - Assigns issue to developer
   - Updates labels

## MANDATORY: Instruction Verification Protocol

**CRITICAL**: Before ANY agent begins implementation, you MUST execute the Instruction Verification Protocol:

```
1. Send assignment with verification request
2. Agent repeats key requirements (3-5 bullet points)
3. Verify repetition is correct
4. If incorrect: send corrections, repeat step 2
5. Agent asks clarifying questions
6. Answer ALL questions
7. Confirm understanding
8. Authorize implementation
```

The assignment message automatically includes the verification request.

## Assignment Message Template (AI Agents)

```markdown
Subject: [TASK] Module: {module_name} - UUID: {task_uuid}

## Assignment

You have been assigned to implement: **{module_name}**

GitHub Issue: {issue_url}
Task UUID: {task_uuid}

## Requirements Summary

{requirements_summary}

## Acceptance Criteria

{acceptance_criteria}

## MANDATORY: Instruction Verification

Before you begin implementation, please:

1. **Repeat the key requirements** in your own words (3-5 bullet points)
2. **List any questions** you have about the requirements
3. **Confirm your understanding** of the acceptance criteria

I will verify your understanding before authorizing implementation.

Reply with your understanding summary.
```

## State File Update

```yaml
active_assignments:
  - agent: "implementer-1"
    agent_type: "ai"
    module: "auth-core"
    github_issue: "#42"
    task_uuid: "task-uuid-12345"
    status: "pending_verification"
    instruction_verification:
      status: "awaiting_repetition"
      repetition_received: false
      repetition_correct: false
      questions_asked: 0
      questions_answered: 0
      authorized_at: null
```

## Examples

```bash
# Assign module to AI agent
/assign-module auth-core implementer-1

# Assign module to human developer
/assign-module oauth-google dev-alice
```

## Next Steps After Assignment

1. Wait for agent to respond with understanding summary
2. Verify the understanding is correct
3. Answer any questions
4. Authorize implementation when verified
5. Begin progress polling (10-15 min intervals)

## Related Commands

- `/register-agent` - Register agents first
- `/orchestration-status` - View assignments
- `/check-agents` - Poll agent progress
- `/reassign-module` - Change assignment
