# Task Checklist Template

## Purpose

This template provides a standard checklist format for remote agents to track their progress on delegated tasks.

---

## Standard Task Checklist

Copy and fill this checklist for each task:

```markdown
# Task: {TASK_ID}

## Pre-Work
- [ ] Received task delegation from orchestrator
- [ ] Sent ACK with status and understanding
- [ ] Understood all acceptance criteria
- [ ] Identified files/components to modify
- [ ] Created feature branch: `feature/{TASK_ID}-{description}`

## Implementation
- [ ] Researched existing codebase patterns
- [ ] Implemented core functionality
- [ ] Followed project code style
- [ ] Added inline comments where needed
- [ ] No TODO/FIXME markers left in code

## Quality
- [ ] Code compiles without warnings
- [ ] Linter passes (ruff/eslint/clippy)
- [ ] Type checker passes (mypy/tsc)
- [ ] No hardcoded values (use config/env)
- [ ] No security vulnerabilities introduced

## Testing
- [ ] Unit tests written for new code
- [ ] Tests verify behavior, not just build
- [ ] All tests pass locally
- [ ] Edge cases covered
- [ ] No skipped/ignored tests

## Verification
- [ ] Ran verification command: `{command}`
- [ ] Output matches expected: `{expected}`
- [ ] Manual testing completed
- [ ] Works on target platform(s)

## Documentation
- [ ] Code has docstrings/JSDoc
- [ ] README updated if needed
- [ ] CHANGELOG entry added
- [ ] API docs updated if applicable

## Git Workflow
- [ ] Commits are atomic and well-described
- [ ] Branch is up to date with main
- [ ] No merge conflicts
- [ ] Branch pushed to remote

## PR Creation
- [ ] PR title follows convention: `feat/fix/docs: description`
- [ ] PR body includes "Closes #{ISSUE_NUM}"
- [ ] PR body has summary of changes
- [ ] PR body has verification output
- [ ] Requested reviewers assigned

## Completion
- [ ] All checklist items complete
- [ ] Completion report written
- [ ] Report sent to orchestrator
- [ ] Issue status updated on GitHub
```

---

## Checklist by Task Type

### Feature Implementation

```markdown
# Feature: {TASK_ID}

## Requirements
- [ ] All acceptance criteria understood
- [ ] No clarification needed

## Implementation
- [ ] Feature logic implemented
- [ ] API endpoints created (if applicable)
- [ ] UI components created (if applicable)
- [ ] Database changes applied (if applicable)

## Integration
- [ ] Feature integrates with existing code
- [ ] No breaking changes to existing APIs
- [ ] Backward compatibility maintained

## Testing
- [ ] Unit tests: {count} tests written
- [ ] Integration tests: {count} tests written
- [ ] E2E tests: {count} tests written (if applicable)
- [ ] All tests pass

## Completion
- [ ] PR created: {url}
- [ ] Completion report sent
```

### Bug Fix

```markdown
# Bug Fix: {TASK_ID}

## Investigation
- [ ] Bug reproduced locally
- [ ] Root cause identified
- [ ] Fix approach documented

## Fix
- [ ] Bug fixed
- [ ] No regressions introduced
- [ ] Related issues checked

## Verification
- [ ] Bug no longer occurs
- [ ] Regression test added
- [ ] Edge cases tested

## Completion
- [ ] PR created: {url}
- [ ] Completion report sent
```

### Refactoring

```markdown
# Refactor: {TASK_ID}

## Planning
- [ ] Scope defined
- [ ] Affected files identified
- [ ] Risk assessment done

## Refactoring
- [ ] Code restructured
- [ ] No functionality changed
- [ ] Code style improved

## Verification
- [ ] All existing tests pass
- [ ] No new warnings/errors
- [ ] Performance not degraded

## Completion
- [ ] PR created: {url}
- [ ] Completion report sent
```

---

## Progress Reporting Format

Update orchestrator at each checkpoint:

```markdown
## Checklist Progress: {TASK_ID}

### Completed (10/15 items)
- [x] Pre-Work (5/5)
- [x] Implementation (4/5)
- [ ] Testing (1/3)
- [ ] PR (0/2)

### Current Focus
Implementing: Unit tests for auth module

### Blockers
None
```

---

## Failed Checklist Items

If an item cannot be completed:

```markdown
## Incomplete Items: {TASK_ID}

### Item: E2E tests written
**Status**: Cannot complete
**Reason**: E2E framework not set up in project
**Recommendation**: Skip for this task, create follow-up issue

### Item: Backward compatibility maintained
**Status**: Not applicable
**Reason**: This is a new feature with no existing API
```

---

## Checklist Submission

When all items complete:

1. Copy completed checklist to completion report
2. Highlight any skipped items with reason
3. Include PR URL
4. Send to orchestrator

```markdown
[DONE] {TASK_ID} - All checklist items complete

Checklist: 15/15 items complete
PR: {url}
Report: docs_dev/reports/{TASK_ID}_completion.md
```
