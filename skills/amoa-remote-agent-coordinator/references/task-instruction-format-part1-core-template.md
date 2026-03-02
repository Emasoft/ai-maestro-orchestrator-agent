# Task Instruction Format - Part 1: Core Template

## Contents

- **[Overview](#overview)** - Critical principle: teach agents in every message
- **[Agent Response Templates](#agent-response-templates)** - Templates to link in task delegations
- **[Mandatory ACK Block](#mandatory-ack-block)** - Include this in EVERY task delegation
- **[When creating a new task instruction](#when-creating-a-new-task-instruction)** - Use this complete template
- **[Agent Response Instructions](#agent-response-instructions)** - How agents should respond at each stage
- **[Report Format](#report-format)** - JSON format for completion reports

---

## Overview

This document provides the complete template for task instructions sent to remote developer agents. Following this format ensures tasks are executed EXACTLY as planned with NO deviations.

**CRITICAL PRINCIPLE**: Remote agents DO NOT have access to the emasoft-orchestrator-agent skill. They do not know any protocols, formats, or expectations unless the orchestrator EXPLICITLY TEACHES them in each message. Every task delegation MUST include:
1. Complete instructions on HOW to respond
2. Template references the agent can download
3. Exact format for ACK, progress updates, and completion reports

---

## Agent Response Templates

Link these templates in EVERY task delegation so agents know exactly how to respond:

| Template | Path | When Agent Uses It |
|----------|------|-------------------|
| ACK Response | `templates/ack-response.md` | Immediately after receiving task |
| Progress Update | `templates/status-update.md` | At each checkpoint during work |
| Completion Report | `templates/completion-report.md` | When task is done or failed |
| Task Checklist | `templates/task-checklist.md` | Throughout task execution |
| GitHub Projects | `templates/github-projects-guide.md` | When updating issue status |

---

## Mandatory ACK Block

**EVERY task delegation MUST start with this block:**

```
================================================================================
ACKNOWLEDGMENT REQUIRED (MANDATORY)
================================================================================

Before starting work, you MUST reply with an acknowledgment in this exact format:

[ACK] {task_id} - {status}
Understanding: {1-line summary of what you will do}

Status options:
- RECEIVED - Task received, will begin work immediately
- CLARIFICATION_NEEDED - Need more info (list your questions)
- REJECTED - Cannot accept task (explain why)
- QUEUED - Have prior tasks, will start after them

Example:
[ACK] GH-42-password-reset - RECEIVED
Understanding: Will implement password reset flow with email tokens

DO NOT begin work until you have sent this acknowledgment.
================================================================================
```

## When Creating a New Task Instruction

```markdown
================================================================================
ACKNOWLEDGMENT REQUIRED (MANDATORY)
================================================================================

Before starting work, you MUST reply with an acknowledgment in this exact format:

[ACK] [TASK_ID] - {status}
Understanding: {1-line summary of what you will do}

Status options:
- RECEIVED - Task received, will begin work immediately
- CLARIFICATION_NEEDED - Need more info (list your questions)
- REJECTED - Cannot accept task (explain why)
- QUEUED - Have prior tasks, will start after them

Example:
[ACK] GH-42-feature - RECEIVED
Understanding: Will implement the feature as specified

DO NOT begin work until you have sent this acknowledgment.
================================================================================

# Task: [TASK_NAME]

## Metadata
- **Issue**: GH-[NUMBER]
- **Branch**: feature/[BRANCH_NAME]
- **Priority**: [low|normal|high|urgent]
- **Assigned To**: [AGENT_ID]
- **Assigned By**: orchestrator-master
- **Assigned At**: [TIMESTAMP]
- **Due By**: [TIMESTAMP or "N/A"]

---

## Context

### Problem Statement
[Clear explanation of what problem this task solves]

### Background
[Any relevant background information the developer needs]

### Related Issues
- GH-[related-1]: [brief description]
- GH-[related-2]: [brief description]

---

## Scope

### DO - What to Implement
1. [Specific action 1]
2. [Specific action 2]
3. [Specific action 3]

### DO NOT - Out of Scope
1. [Item explicitly out of scope 1]
2. [Item explicitly out of scope 2]
3. [Item explicitly out of scope 3]

### Boundaries
- **Start Point**: [where implementation begins]
- **End Point**: [where implementation ends]
- **Integration Points**: [how it connects to existing code]

---

## Interface Contract

### Inputs
```
[Input specification - parameters, types, constraints]
```

### Outputs
```
[Output specification - return values, side effects]
```

### Function Signatures (if applicable)
```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """
    [Docstring specification]
    """
    pass
```

### API Contract (if applicable)
```
Endpoint: POST /api/resource
Request Body:
{
  "field1": "string",
  "field2": 123
}
Response:
{
  "id": "uuid",
  "status": "created"
}
```

---

## Project Configuration

**Config Location**: `design/config/`
**Config Version**: [TIMESTAMP]

### Required Config Files
- `design/config/toolchain.md` - Tools, versions, commands
- `design/config/standards.md` - Code standards, naming, formatting
- `design/config/environment.md` - Environment variables
- `design/specs/architecture.md` - System architecture
- `design/specs/requirements.md` - Requirements for GH-[NUMBER]

**IMPORTANT**: Read ALL config files before starting. Do NOT rely on this summary alone.

### Critical Settings Summary
(Minimal inline context - full details in config files)
- **Python**: [version]
- **Package Manager**: [tool]
- **Line Length**: [number]
- **Test Framework**: [framework]

---

## Files to Modify

| File | Action | Changes |
|------|--------|---------|
| `src/path/file1.py` | MODIFY | Add function X, update function Y |
| `src/path/file2.py` | MODIFY | Import X, call X from existing function |
| `tests/test_file1.py` | CREATE | Unit tests for function X |
| `docs/api.md` | MODIFY | Document new endpoint |

### File-Specific Instructions

#### src/path/file1.py
- Add `function_x()` after line 42
- Update `existing_function()` to call `function_x()`
- Do NOT modify `other_function()` - out of scope

#### src/path/file2.py
- Import `function_x` from file1
- Call `function_x()` in the handler

---

## Test Requirements

### TDD Sequence
1. **FIRST**: Write failing tests
2. **SECOND**: Implement to pass tests
3. **THIRD**: Refactor with tests green

### Required Tests

#### Unit Tests
- [ ] `test_function_x_valid_input` - Happy path
- [ ] `test_function_x_invalid_input` - Error handling
- [ ] `test_function_x_edge_case_empty` - Empty input
- [ ] `test_function_x_edge_case_large` - Large input

#### Integration Tests
- [ ] `test_endpoint_creates_resource` - Full flow
- [ ] `test_endpoint_returns_error_on_invalid` - Error flow

### Coverage Requirement
- Minimum 80% coverage for new code
- All branches must be tested

---

## Completion Criteria

### Code Quality
- [ ] All new functions have docstrings
- [ ] Type hints on all function signatures
- [ ] No linting errors (run: `ruff check`)
- [ ] Formatted (run: `ruff format`)

### Testing
- [ ] All new tests pass locally
- [ ] All existing tests pass locally
- [ ] Coverage meets minimum threshold

### Git
- [ ] Changes committed to feature branch
- [ ] Branch pushed to origin
- [ ] Commit messages follow conventional format

### Pull Request
- [ ] PR created against main
- [ ] PR description follows template
- [ ] PR linked to GH-[NUMBER]

### Documentation
- [ ] Code comments explain "why" not "what"
- [ ] API docs updated if applicable
- [ ] README updated if applicable

---

## Constraints

### MUST Follow
- TDD - tests BEFORE code
- FAIL-FAST - no workarounds
- Conventional commits
- Project style guide

### MUST NOT Do
- Add dependencies without approval
- Modify files outside scope
- Create workarounds for blockers
- Skip tests "to save time"

---

## Escalation Rules

### Escalate Immediately If
- Security vulnerability discovered
- Architecture decision required
- Spec is ambiguous or contradictory
- Blocked for more than 2 hours

### How to Escalate
Send message to `orchestrator-master`:
```json
{
  "type": "escalation",
  "task_id": "GH-[NUMBER]",
  "escalation_type": "[type]",
  "description": "[details]"
}
```

---

## Agent Response Instructions

**THIS SECTION IS MANDATORY IN EVERY TASK DELEGATION**

### How to Respond at Each Stage

| Stage | Action Required | Template to Use |
|-------|-----------------|-----------------|
| Task Received | Send ACK within 5 minutes | `templates/ack-response.md` |
| Starting Work | Update issue to "In Progress" | `templates/github-projects-guide.md` |
| Checkpoint Reached | Send progress update | `templates/status-update.md` |
| Blocked | Send blocker report immediately | `templates/status-update.md` (BLOCKED section) |
| Task Complete | Send completion report | `templates/completion-report.md` |

### Response Format Quick Reference

**ACK (immediately after receiving task):**
```
[ACK] GH-42-feature - RECEIVED
Understanding: Will implement X with Y approach
```

**Progress Update (at each checkpoint):**
```
[PROGRESS] GH-42-feature - Checkpoint 2: Implementation

Status: ACTIVE
Progress: 60% complete
Current: Finished core logic
Next: Writing tests
```

**Completion Report (when done):**
```
[DONE] GH-42-feature - Feature implemented and tested

## Summary
- Implemented X
- Added Y tests
- Updated documentation

## Verification
cargo test -> 15 passed, 0 failed

## Artifacts
- PR: https://github.com/org/repo/pull/43
- Branch: feature/GH-42-feature
```

### GitHub Issue Updates

When updating GitHub issue status:

```bash
# Move to In Progress (after ACK)
gh issue edit [ISSUE_NUM] --add-label "status:in-progress"
gh issue comment [ISSUE_NUM] --body "[ACK] Starting work."

# Add progress update
gh issue comment [ISSUE_NUM] --body "[PROGRESS] Checkpoint 2: 60% complete"

# Move to AI Review (after PR created)
gh issue edit [ISSUE_NUM] --add-label "status:ai-review"
```

### Reporting Guidelines

1. **Keep summaries brief**: 1-2 lines to orchestrator, full details in report files
2. **Write detailed reports to files**: `docs_dev/reports/{TASK_ID}_completion.md`
3. **Include paths in messages**: "Report: docs_dev/reports/GH-42_completion.md"
4. **No verbose output**: Orchestrator needs summaries, not full logs

### Template Download Locations

Access these templates for exact response formats:
- ACK: `skills/remote-agent-coordinator/templates/ack-response.md`
- Status: `skills/remote-agent-coordinator/templates/status-update.md`
- Completion: `skills/remote-agent-coordinator/templates/completion-report.md`
- Checklist: `skills/remote-agent-coordinator/templates/task-checklist.md`
- GitHub: `skills/remote-agent-coordinator/templates/github-projects-guide.md`

---

## Report Format

When task is complete (success or blocked), send:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "orchestrator-master",
  "subject": "COMPLETE: GH-[NUMBER] [TASK_NAME]",
  "priority": "normal",
  "content": {
    "type": "completion-report",
    "task_id": "GH-[NUMBER]",
    "status": "success|blocked|failed",
    "pr_url": "https://github.com/owner/repo/pull/[PR_NUMBER]",
    "test_results": {
      "passed": 47,
      "failed": 0,
      "skipped": 2,
      "coverage": "87%"
    },
    "time_spent_hours": 3.5,
    "notes": "[Any issues, observations, or recommendations]",
    "checklist_completion": {
      "code_quality": true,
      "testing": true,
      "git": true,
      "pull_request": true,
      "documentation": true
    }
  }
}
```

---

**See also**: [task-instruction-format-part2-operations.md](task-instruction-format-part2-operations.md) for configuration reading, monitoring, error handling, and integration protocols.
