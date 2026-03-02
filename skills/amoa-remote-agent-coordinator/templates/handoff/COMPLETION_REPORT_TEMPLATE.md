# Task Completion Report: {{TASK_ID}}

**Extends**: [handoff-protocols.md](../../../eoa-agent-replacement/references/handoff-protocols.md)

---

## DELIVERY INSTRUCTIONS (DO NOT INCLUDE IN COMPILED OUTPUT)

**This template, once compiled, MUST be:**
1. **Saved to file**: `completion-report-{{TASK_ID}}.md`
2. **Uploaded to GitHub issue #{{ISSUE_NUMBER}}** as comment attachment
3. **Sent via AI Maestro** with document URL only (NOT full content)
4. **ACK not required** (informational delivery)

**Protocol Reference**: See [../protocols/DOCUMENT_DELIVERY_PROTOCOL.md](../protocols/DOCUMENT_DELIVERY_PROTOCOL.md)

**Message Format**:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "{{ORCHESTRATOR_SESSION}}",
  "subject": "task_completion",
  "priority": "high",
  "content": {
    "type": "document_delivery",
    "message": "Task {{TASK_ID}} complete. Full report: {{GITHUB_ISSUE_URL}}"
  }
}
```

---

## Task Summary

**Task ID**: `{{TASK_ID}}`
**Agent**: {{AGENT_NAME}} ({{AGENT_SESSION}})
**Completion Date**: {{COMPLETION_DATE}}
**Duration**: {{DURATION}}
**Status**: {{STATUS}}

---

## Toolchain Verification Results

**Toolchain**: {{TOOLCHAIN_TYPE}}
**Template Used**: [{{TOOLCHAIN_TEMPLATE_PATH}}]({{TOOLCHAIN_TEMPLATE_PATH}})

### Verification Command Results

```bash
# Full toolchain verification
$ {{VERIFY_ALL_CMD}}
{{VERIFY_ALL_OUTPUT}}
```

**Result**: {{VERIFY_ALL_RESULT}} ✅/❌

### Test Results

```bash
$ {{TEST_CMD}}
{{TEST_OUTPUT}}
```

**Result**: {{TEST_RESULT}} ✅/❌
**Tests Passed**: {{TESTS_PASSED}}/{{TESTS_TOTAL}}
**Coverage**: {{COVERAGE_PERCENTAGE}}%

### Format/Lint Results

```bash
$ {{FORMAT_CMD}}
{{FORMAT_OUTPUT}}

$ {{LINT_CMD}}
{{LINT_OUTPUT}}
```

**Format Result**: {{FORMAT_RESULT}} ✅/❌
**Lint Result**: {{LINT_RESULT}} ✅/❌

### Build Results

```bash
$ {{BUILD_CMD}}
{{BUILD_OUTPUT}}
```

**Build Result**: {{BUILD_RESULT}} ✅/❌

---

## Acceptance Criteria Checklist

{{ACCEPTANCE_CRITERIA_CHECKLIST}}

**All Criteria Met**: {{ALL_CRITERIA_MET}} ✅/❌

---

## Git & GitHub Integration

**Branch**: `{{BRANCH_NAME}}`
**Base Branch**: `{{BASE_BRANCH}}`
**Pull Request**: {{PR_URL}}
**Issue**: {{ISSUE_URL}}

### Commits
{{COMMIT_LIST}}

### PR Status
- **State**: {{PR_STATE}}
- **Checks**: {{CI_CHECKS_STATUS}}
- **Reviews**: {{REVIEWS_COUNT}}
- **Labels**: {{PR_LABELS}}

### Issue Updates
{{ISSUE_UPDATES_SUMMARY}}

---

## Files Modified

### Source Files
{{SOURCE_FILES_LIST}}

### Test Files
{{TEST_FILES_LIST}}

### Documentation Files
{{DOCS_FILES_LIST}}

### Configuration Files
{{CONFIG_FILES_LIST}}

---

## Definition of Done Verification

- [{{DOD_VERIFY_ALL}}] All acceptance criteria met
- [{{DOD_TOOLCHAIN}}] {{VERIFY_ALL_CMD}} passes
- [{{DOD_TESTS}}] Tests written and passing
- [{{DOD_FORMAT}}] Code formatted/linted
- [{{DOD_DOCS}}] Documentation updated
- [{{DOD_PR}}] PR created and linked
- [{{DOD_NO_BREAKING}}] No breaking changes

---

## Evidence Files

### Logs
- Verification log: `{{VERIFICATION_LOG_PATH}}`
- Test output: `{{TEST_LOG_PATH}}`
- Build log: `{{BUILD_LOG_PATH}}`

### Screenshots/Artifacts
{{ARTIFACTS_LIST}}

### Code Diffs
{{CODE_DIFF_SUMMARY}}

---

## Challenges & Solutions

### Challenges Encountered
{{CHALLENGES_ENCOUNTERED}}

### Solutions Applied
{{SOLUTIONS_APPLIED}}

### Toolchain Issues
{{TOOLCHAIN_ISSUES}}

---

## Lessons Learned

### What Went Well
{{WHAT_WENT_WELL}}

### What Could Be Improved
{{WHAT_COULD_BE_IMPROVED}}

### Toolchain Insights
{{TOOLCHAIN_INSIGHTS}}

### Recommendations for Future Tasks
{{RECOMMENDATIONS}}

---

## Dependencies & Side Effects

### New Dependencies Added
{{NEW_DEPENDENCIES}}

### Breaking Changes
{{BREAKING_CHANGES}}

### Migration Notes
{{MIGRATION_NOTES}}

### Side Effects
{{SIDE_EFFECTS}}

---

## Next Steps

{{NEXT_STEPS}}

### Follow-up Tasks
{{FOLLOW_UP_TASKS}}

### Related Issues to Update
{{RELATED_ISSUES_TO_UPDATE}}

---

## Orchestrator Sign-off

**Reviewed By**: {{ORCHESTRATOR_NAME}}
**Review Date**: {{REVIEW_DATE}}
**Sign-off Status**: {{SIGNOFF_STATUS}}
**Comments**: {{ORCHESTRATOR_COMMENTS}}

---

## Metrics

- **Lines of Code Added**: {{LOC_ADDED}}
- **Lines of Code Removed**: {{LOC_REMOVED}}
- **Files Changed**: {{FILES_CHANGED}}
- **Time to Complete**: {{TIME_TO_COMPLETE}}
- **Blockers Encountered**: {{BLOCKERS_COUNT}}
- **Iterations**: {{ITERATIONS_COUNT}}

---

**Report Version**: 1.0.0
**Generated**: {{REPORT_GENERATION_DATE}}
**Template**: [COMPLETION_REPORT_TEMPLATE.md](./COMPLETION_REPORT_TEMPLATE.md)
