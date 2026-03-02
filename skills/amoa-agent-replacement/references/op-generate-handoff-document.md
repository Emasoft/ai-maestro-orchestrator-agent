---
procedure: support-skill
workflow-instruction: support
---

# Operation: Generate Handoff Document


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Create Document Header](#step-1-create-document-header)
  - [Step 2: Add Task Summary Section](#step-2-add-task-summary-section)
- [Task Summary](#task-summary)
  - [Step 3: Add Requirements Section](#step-3-add-requirements-section)
- [User Requirements (Reference)](#user-requirements-reference)
  - [From USER_REQUIREMENTS.md Section 3:](#from-user_requirementsmd-section-3)
  - [Acceptance Criteria:](#acceptance-criteria)
  - [Step 4: Add Progress Detail Section](#step-4-add-progress-detail-section)
- [Work Progress](#work-progress)
  - [Completed:](#completed)
  - [In Progress:](#in-progress)
  - [Not Started:](#not-started)
  - [Step 5: Add Technical Context Section](#step-5-add-technical-context-section)
- [Technical Context](#technical-context)
  - [Files Modified:](#files-modified)
  - [Branch:](#branch)
  - [Dependencies:](#dependencies)
  - [Architecture Notes:](#architecture-notes)
  - [Step 6: Add Communication History Section](#step-6-add-communication-history-section)
- [Communication History](#communication-history)
  - [Last 5 Messages:](#last-5-messages)
  - [Step 7: Add Next Steps Section](#step-7-add-next-steps-section)
- [Next Steps](#next-steps)
  - [Immediate (Resume Work):](#immediate-resume-work)
  - [After Validation Complete:](#after-validation-complete)
  - [Blocked On:](#blocked-on)
  - [Step 8: Add Verification Requirements](#step-8-add-verification-requirements)
- [Verification Requirements](#verification-requirements)
  - [Instruction Verification (IVP):](#instruction-verification-ivp)
  - [Step 9: Assemble Complete Document](#step-9-assemble-complete-document)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example](#example)
- [Task Summary](#task-summary)
- [User Requirements (Reference)](#user-requirements-reference)
- [Work Progress](#work-progress)
  - [Completed:](#completed)
  - [In Progress:](#in-progress)
  - [Not Started:](#not-started)
- [Technical Context](#technical-context)
- [Communication History](#communication-history)
- [Next Steps](#next-steps)
- [Verification](#verification)
- [Checklist](#checklist)

## When to Use

Use this operation after compiling context to create a comprehensive handoff document for the replacement agent.

## Prerequisites

- Context compilation complete (op-compile-task-context)
- Replacement agent identified
- Understanding of handoff document format

## Procedure

### Step 1: Create Document Header

```markdown
# Agent Handoff Document

**Date**: <timestamp>
**From Agent**: <failed_agent>
**To Agent**: <replacement_agent>
**Reason**: <failure_reason>
**Orchestrator**: <orchestrator_id>
```

### Step 2: Add Task Summary Section

```markdown
## Task Summary

| Task ID | Description | Status | Priority |
|---------|-------------|--------|----------|
| #42 | Implement auth module | 70% | high |
| #45 | Add rate limiting | 0% | normal |
```

### Step 3: Add Requirements Section

Copy from USER_REQUIREMENTS.md the relevant sections:

```markdown
## User Requirements (Reference)

### From USER_REQUIREMENTS.md Section 3:
- Authentication shall use JWT tokens
- Tokens shall expire after 24 hours
- Invalid tokens shall return 401 Unauthorized

### Acceptance Criteria:
- [ ] AC1: Valid tokens pass validation
- [ ] AC2: Expired tokens rejected
- [ ] AC3: Tampered tokens rejected
```

### Step 4: Add Progress Detail Section

```markdown
## Work Progress

### Completed:
- Token generation implemented (src/auth/token.py)
- Login endpoint created (src/auth/routes.py)
- 8 unit tests written

### In Progress:
- Token validation middleware (src/auth/validation.py) - 50% done
- Integration tests - not started

### Not Started:
- Rate limiting
- Documentation
```

### Step 5: Add Technical Context Section

```markdown
## Technical Context

### Files Modified:
- `src/auth/token.py` - Token generation
- `src/auth/routes.py` - Login endpoint
- `tests/unit/auth/test_token.py` - Token tests

### Branch:
- `feature/auth-42` - 3 commits ahead of main

### Dependencies:
- `jose` library for JWT
- `bcrypt` for password hashing

### Architecture Notes:
- Using middleware pattern for validation
- Tokens stored in Redis (connection in src/core/redis.py)
```

### Step 6: Add Communication History Section

```markdown
## Communication History

### Last 5 Messages:

1. **2024-01-15T14:30:00Z** - From orchestrator:
   > "Please prioritize token validation next"

2. **2024-01-15T14:00:00Z** - From implementer-1:
   > "Token generation complete. Starting validation."

[Include relevant Q&A, decisions, clarifications]
```

### Step 7: Add Next Steps Section

```markdown
## Next Steps

### Immediate (Resume Work):
1. Complete `validation.py` middleware (see line 45 TODO)
2. Add tests for validation edge cases
3. Run full test suite

### After Validation Complete:
4. Implement rate limiting (#45)
5. Update API documentation
6. Submit PR for review

### Blocked On:
- Issue #38 must merge first (auth config)
- API spec clarification needed (ask orchestrator)
```

### Step 8: Add Verification Requirements

```markdown
## Verification Requirements

Before marking any task complete, verify:

1. [ ] All acceptance criteria met
2. [ ] Tests passing (run: `pytest tests/unit/auth/ -v`)
3. [ ] Type checks pass (run: `mypy src/auth/`)
4. [ ] No linting errors (run: `ruff check src/auth/`)
5. [ ] Documentation updated

### Instruction Verification (IVP):
After receiving this handoff, please confirm:
- You understand the task requirements
- You have access to the repository
- You can run the test suite
- Send ACK to orchestrator with any questions
```

### Step 9: Assemble Complete Document

```python
# Using helper script
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_generate_replacement_handoff.py" \
  --failed-agent "implementer-1" \
  --new-agent "implementer-2" \
  --context-file "replacement-context.md" \
  --output "handoff-document.md"
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| Handoff Document | Markdown | Complete handoff in `handoff-document.md` |
| Task Count | Number | Number of tasks being handed off |
| Sections | Array | Sections included in document |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Context incomplete | Compilation missed data | Re-run context compilation |
| Requirements unclear | USER_REQUIREMENTS.md incomplete | Note gaps in handoff |
| No branch found | Agent worked without branch | Document this limitation |
| Communication history empty | Messages expired | Note context gap |

## Example

```markdown
# Agent Handoff Document

**Date**: 2024-01-15T15:30:00Z
**From Agent**: implementer-1
**To Agent**: implementer-2
**Reason**: Context loss recovery
**Orchestrator**: orchestrator-master

## Task Summary

| Task ID | Description | Status | Priority |
|---------|-------------|--------|----------|
| #42 | Implement JWT authentication | 70% | high |
| #45 | Add API rate limiting | 0% | normal |

## User Requirements (Reference)

From USER_REQUIREMENTS.md Section 3.2:
- System shall authenticate users via JWT tokens
- Tokens shall expire after 24 hours
- System shall return 401 for invalid/expired tokens

## Work Progress

### Completed:
- Token generation (src/auth/token.py) - DONE
- Login endpoint (src/auth/routes.py) - DONE
- 8/12 unit tests

### In Progress:
- Token validation middleware (50%)
  - File: src/auth/validation.py
  - TODO at line 45: "Complete signature verification"

### Not Started:
- Rate limiting (#45)
- API docs

## Technical Context

**Branch**: feature/auth-42 (3 commits ahead)
**Key Files**:
- src/auth/token.py - Token generation
- src/auth/validation.py - Validation (partial)
- tests/unit/auth/test_token.py - Tests

**Dependencies**: jose, bcrypt, redis

## Communication History

- Last report: "Token generation complete, starting validation"
- Orchestrator guidance: "Prioritize validation, rate limiting can wait"

## Next Steps

1. Complete validation.py (see TODO line 45)
2. Write remaining 4 tests
3. Run full suite: `pytest tests/unit/auth/ -v`
4. Then start #45 (rate limiting)

## Verification

Please confirm receipt and understanding. Send ACK with:
- Confirmation you can access repo
- Any questions about requirements
- Estimated completion time

---
**Generated by EOA Agent Replacement Protocol**
```

## Checklist

- [ ] Create document header with metadata
- [ ] Add task summary table
- [ ] Copy relevant user requirements
- [ ] Detail progress (completed, in-progress, not started)
- [ ] Document technical context (files, branches, deps)
- [ ] Include communication history
- [ ] Define clear next steps
- [ ] Add verification requirements
- [ ] Generate final document
