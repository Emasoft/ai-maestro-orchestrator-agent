---
procedure: proc-execute-task
workflow-instruction: Step 17 - Task Execution
operation: prepare-task-delegation
---

# Operation: Prepare Task Delegation


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Mandatory Elements](#mandatory-elements)
  - [1. ACK Instructions Block (at top of message)](#1-ack-instructions-block-at-top-of-message)
- [ACK PROTOCOL (MANDATORY)](#ack-protocol-mandatory)
  - [2. PR Notification Requirement](#2-pr-notification-requirement)
- [PR NOTIFICATION (MANDATORY)](#pr-notification-mandatory)
  - [3. Context Section](#3-context-section)
- [Context](#context)
  - [4. Scope Section](#4-scope-section)
- [Scope](#scope)
  - [DO](#do)
  - [DO NOT](#do-not)
  - [5. Interface Contract](#5-interface-contract)
- [Interface Contract](#interface-contract)
  - [6. Files in Scope](#6-files-in-scope)
- [Files to Modify](#files-to-modify)
  - [7. Test Requirements](#7-test-requirements)
- [Test Requirements](#test-requirements)
  - [8. Completion Criteria](#8-completion-criteria)
- [Completion Criteria](#completion-criteria)
- [Template Assembly](#template-assembly)
- [Success Criteria](#success-criteria)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Prepare complete task delegation instructions that include all required elements for remote agent execution.

## When to Use

- Before sending any task to a remote agent
- When creating new feature implementation tasks
- When assigning bug fixes to agents
- When delegating refactoring work

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| Task ID | GitHub issue number | Yes |
| Task description | Issue body | Yes |
| Agent assignment | Selected agent name | Yes |
| Acceptance criteria | Issue checklist | Yes |
| Related designs | design/ directory | If applicable |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| delegation_message | JSON | Complete task instruction message |
| files_in_scope | Array | List of files agent may modify |
| test_requirements | Array | Tests that must pass |

## Mandatory Elements

Every task delegation MUST include:

### 1. ACK Instructions Block (at top of message)

```markdown
## ACK PROTOCOL (MANDATORY)

When you receive this task:
1. Send an ACK message within 5 minutes
2. Include: task ID, your understanding, questions
3. Wait for confirmation before starting work

ACK Format:
[ACK] Task #<id> - <one-line summary of understanding>
Questions: <list or "none">
```

### 2. PR Notification Requirement

```markdown
## PR NOTIFICATION (MANDATORY)

Before creating a PR, you MUST:
1. Request PR permission via AI Maestro message
2. Wait for orchestrator approval (4-verification-loop)
3. Only create PR after receiving explicit approval
```

### 3. Context Section

```markdown
## Context

Problem: <what problem is being solved>
User requirement: <exact quote from user, if available>
Related issues: #<list of related issue numbers>
```

### 4. Scope Section

```markdown
## Scope

### DO
- <specific action 1>
- <specific action 2>

### DO NOT
- <forbidden action 1>
- <forbidden action 2>
- Modify files outside the listed scope
- Change any public API signatures without approval
```

### 5. Interface Contract

```markdown
## Interface Contract

Input: <what the code receives>
Output: <what the code produces>
Side effects: <any external effects>
```

### 6. Files in Scope

```markdown
## Files to Modify

- `src/module/file.py` - <what to change>
- `tests/test_file.py` - <tests to add/update>
```

### 7. Test Requirements

```markdown
## Test Requirements

- [ ] All existing tests pass
- [ ] New tests for <specific functionality>
- [ ] Test coverage for edge cases: <list>
```

### 8. Completion Criteria

```markdown
## Completion Criteria

Task is complete when:
- [ ] <criterion 1>
- [ ] <criterion 2>
- [ ] All tests pass
- [ ] PR approved and merged
```

## Template Assembly

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "orchestrator",
  "to": "<agent-name>",
  "subject": "Task Assignment: #<issue-number> - <title>",
  "priority": "normal",
  "content": {
    "type": "task",
    "message": "<assembled markdown with all sections above>",
    "data": {
      "task_id": "<issue-number>",
      "files_in_scope": ["<file1>", "<file2>"],
      "test_requirements": ["<test1>", "<test2>"],
      "completion_criteria": ["<criterion1>", "<criterion2>"]
    }
  }
}
```

## Success Criteria

- [ ] ACK instructions block included at top
- [ ] PR notification requirement included
- [ ] Context clearly explains the problem
- [ ] Scope has explicit DO and DO NOT lists
- [ ] Files in scope are specific paths
- [ ] Test requirements are concrete
- [ ] Completion criteria are verifiable

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Missing acceptance criteria | Issue not fully specified | Query architect for missing criteria |
| Scope unclear | Task too broad | Break into smaller tasks |
| Files conflict with other tasks | Concurrent assignments | Check assignment matrix first |

## Related Operations

- op-send-task-delegation
- op-enforce-verification-loops
