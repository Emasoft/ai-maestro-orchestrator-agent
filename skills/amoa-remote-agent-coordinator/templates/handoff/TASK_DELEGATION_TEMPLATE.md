# Task Delegation: {{TASK_ID}}

**Extends**: [handoff-protocols.md](../../../eoa-agent-replacement/references/handoff-protocols.md)

---

## DELIVERY INSTRUCTIONS (DO NOT INCLUDE IN COMPILED OUTPUT)

**This template, once compiled, MUST be:**
1. **Saved to file**: `task-delegation-{{TASK_ID}}.md`
2. **Uploaded to GitHub issue #{{ISSUE_NUMBER}}** as comment attachment
3. **Sent via AI Maestro** with document URL only (NOT full content)
4. **ACK required** from recipient within {{ACK_TIMEOUT}} minutes

**Protocol Reference**: See [../protocols/DOCUMENT_DELIVERY_PROTOCOL.md](../protocols/DOCUMENT_DELIVERY_PROTOCOL.md)

**Message Format**:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "{{AGENT_SESSION}}",
  "subject": "document_delivery",
  "priority": "high",
  "content": {
    "type": "document_delivery",
    "message": "Task delegation document ready. View: {{GITHUB_ISSUE_URL}}"
  }
}
```

---

## Task Overview

**Task ID**: `{{TASK_ID}}`
**Priority**: {{PRIORITY}}
**Estimated Effort**: {{EFFORT_ESTIMATE}}
**Assigned To**: {{AGENT_NAME}} ({{AGENT_SESSION}})
**Delegated By**: {{ORCHESTRATOR_NAME}}
**Date**: {{DELEGATION_DATE}}

---

## Toolchain Context

**Toolchain Type**: {{TOOLCHAIN_TYPE}}
**Template Reference**: [{{TOOLCHAIN_TEMPLATE_PATH}}]({{TOOLCHAIN_TEMPLATE_PATH}})

### Environment Requirements
- **Language**: {{LANGUAGE}} {{LANGUAGE_VERSION}}
- **Package Manager**: {{PACKAGE_MANAGER}}
- **Build Tool**: {{BUILD_TOOL}}
- **Test Framework**: {{TEST_FRAMEWORK}}
- **Linter/Formatter**: {{LINTER_FORMATTER}}

### Verification Commands
```bash
# Verify all toolchain components
{{VERIFY_ALL_CMD}}

# Run tests
{{TEST_CMD}}

# Format/Lint
{{FORMAT_CMD}}
{{LINT_CMD}}
```

---

## Task Description

{{TASK_DESCRIPTION}}

### Objectives
{{OBJECTIVES}}

### Context
{{CONTEXT}}

---

## TDD Requirements (MANDATORY)

**This task MUST follow Test-Driven Development. Code-first development will be REJECTED.**

### The TDD Cycle

1. **RED Phase** - Write failing test FIRST
   - Write test that documents intended behavior
   - Run test and verify it FAILS
   - Commit with message: `RED: test for [feature-name]`

2. **GREEN Phase** - Write minimum code to pass
   - Implement only what's needed to pass the test
   - Run test and verify it PASSES
   - Commit with message: `GREEN: implement [feature-name]`

3. **REFACTOR Phase** - Improve code quality
   - Clean up code while maintaining behavior
   - Run tests and verify they still PASS
   - Commit with message: `REFACTOR: improve [feature-name]`

### TDD Commit Pattern Required

Your PR MUST contain commits in this sequence:
```
RED: test for feature X
GREEN: implement feature X
REFACTOR: improve feature X (optional)
```

**CRITICAL**: GREEN commits without preceding RED commits = TDD violation = REJECTED

### TDD Verification Evidence

In your completion report, include:
```
TDD Verification:
- RED commit: [SHA] - test for [feature]
- GREEN commit: [SHA] - implement [feature]
- Test command: [command] → PASSED
```

---

### Files to Modify
{{FILES_TO_MODIFY}}

### Dependencies
{{DEPENDENCIES}}

---

## Acceptance Criteria

{{ACCEPTANCE_CRITERIA}}

### Definition of Done
- [ ] All acceptance criteria met
- [ ] TDD cycle followed (RED → GREEN → REFACTOR commits present)
- [ ] {{VERIFY_ALL_CMD}} passes
- [ ] Tests written and passing ({{TEST_CMD}})
- [ ] Code formatted/linted ({{FORMAT_CMD}}, {{LINT_CMD}})
- [ ] Documentation updated
- [ ] PR created and linked
- [ ] No breaking changes to existing functionality

---

## Git Workflow

**Branch**: `{{BRANCH_NAME}}`
**Base Branch**: `{{BASE_BRANCH}}`
**Issue**: #{{ISSUE_NUMBER}}
**Labels**: {{LABELS}}

### Git Commands
```bash
# Create feature branch
git checkout -b {{BRANCH_NAME}}

# Commit strategy
git add {{FILES}}
git commit -m "{{COMMIT_MESSAGE_TEMPLATE}}"

# Push and create PR
git push -u origin {{BRANCH_NAME}}
gh pr create --title "{{PR_TITLE}}" --body "{{PR_BODY}}" --label "{{LABELS}}"
```

---

## Verification Checklist

Before marking complete, ensure:

- [ ] Toolchain verification: `{{VERIFY_ALL_CMD}}`
- [ ] Tests pass: `{{TEST_CMD}}`
- [ ] Code formatted: `{{FORMAT_CMD}}`
- [ ] Code linted: `{{LINT_CMD}}`
- [ ] Build succeeds: `{{BUILD_CMD}}`
- [ ] Documentation updated
- [ ] COMPLETION_REPORT.md created
- [ ] PR linked to issue #{{ISSUE_NUMBER}}

### TDD Sequence Verification
```bash
# Verify RED commit exists before GREEN commit
git log --oneline | grep -E "^[a-f0-9]+ (RED|GREEN|REFACTOR):"
```

---

## Communication Protocol

### Acknowledgment Required
Reply with ACK using [ACK_TEMPLATE.md](./ACK_TEMPLATE.md) within {{ACK_TIMEOUT}} minutes.

### Progress Updates
- Update issue #{{ISSUE_NUMBER}} with progress comments
- Report blockers immediately using [BLOCKER_REPORT_TEMPLATE.md](./BLOCKER_REPORT_TEMPLATE.md)
- Provide status updates every {{STATUS_UPDATE_FREQUENCY}}

### Completion Report
Upon completion, submit [COMPLETION_REPORT_TEMPLATE.md](./COMPLETION_REPORT_TEMPLATE.md) with:
- Verification results
- PR link
- Evidence files
- Lessons learned

---

## Resources

**Toolchain Template**: {{TOOLCHAIN_TEMPLATE_PATH}}
**Handoff Protocols**: [handoff-protocols.md](../../../eoa-agent-replacement/references/handoff-protocols.md)
**Project Documentation**: {{PROJECT_DOCS_PATH}}
**Related Issues**: {{RELATED_ISSUES}}

---

## Notes

{{ADDITIONAL_NOTES}}

---

**Template Version**: 1.0.0
**Last Updated**: {{TEMPLATE_UPDATE_DATE}}
