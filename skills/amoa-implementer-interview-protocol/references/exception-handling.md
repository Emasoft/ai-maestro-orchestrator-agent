# Exception Handling

## 1. Implementer Disagrees with Requirements

If implementer believes requirements are wrong:

1. Document the disagreement
2. Escalate per escalation-messages.md
3. WAIT for resolution
4. Do NOT allow implementation to proceed with unapproved changes

## 2. Architect Recommends Design Change

If architect approves a design change:

1. Update the design document
2. Re-interview implementer with new design
3. Document the change in the issue

## 3. User Approves Requirement Change

If user approves changing an immutable requirement:

1. Document the approval with timestamp
2. Update the requirement document
3. Update the task with new requirement
4. Re-interview implementer
5. Proceed with updated requirements

## 4. Implementer Never Acknowledges

**Cause**: Agent unresponsive or offline

**Solution**:
1. Send reminder after 5 minutes
2. Check AI Maestro agent status
3. Escalate to **eoa-progress-monitoring**
4. Consider reassignment if no response after 3 attempts

## 5. Implementer Misunderstands Task

**Cause**: Unclear requirements or insufficient context

**Solution**:
1. Clarify requirements
2. Update handoff document
3. Re-send interview questions
4. Verify understanding before approving PROCEED

## 6. Implementer Has Design Concerns

**Cause**: Architectural incompatibility

**Solution**:
1. Escalate to Architect (EAA) for review
2. Follow escalation-messages.md templates
3. Wait for architect decision
4. Update design if needed

## 7. Implementer Reports Incomplete Work

**Cause**: Rushed or blocked during implementation

**Solution**:
1. Send REVISE with specific missing items
2. Use post-task verification questions
3. Do NOT approve PR until complete

## 8. Tests Fail in Post-Task Interview

**Cause**: Code doesn't meet acceptance criteria

**Solution**:
1. Send REVISE message
2. Require passing tests before PR approval
3. Re-verify after fixes

## 9. Implementer Creates PR Before Approval

**Cause**: Protocol violation

**Solution**:
1. Remind implementer of protocol
2. Review PR manually (do not auto-merge)
3. Update process training if pattern repeats
