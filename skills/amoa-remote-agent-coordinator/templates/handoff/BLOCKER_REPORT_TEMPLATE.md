# Blocker Report: {{TASK_ID}}

**Extends**: [handoff-protocols.md](../../../eoa-agent-replacement/references/handoff-protocols.md)

---

## DELIVERY INSTRUCTIONS (DO NOT INCLUDE IN COMPILED OUTPUT)

**This template, once compiled, MUST be:**
1. **Saved to file**: `blocker-report-{{TASK_ID}}-{{BLOCKER_ID}}.md`
2. **Uploaded to GitHub issue #{{ISSUE_NUMBER}}** as comment attachment
3. **Sent via AI Maestro** with document URL only (NOT full content)
4. **ACK not required** but **response expected** (critical escalation)

**Protocol Reference**: See [../protocols/DOCUMENT_DELIVERY_PROTOCOL.md](../protocols/DOCUMENT_DELIVERY_PROTOCOL.md)

**Message Format**:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "{{ORCHESTRATOR_SESSION}}",
  "subject": "blocker_escalation",
  "priority": "critical",
  "content": {
    "type": "document_delivery",
    "message": "🚨 BLOCKER on {{TASK_ID}} - {{BLOCKER_TYPE}} - Details: {{GITHUB_ISSUE_URL}}"
  }
}
```

---

## Blocker Summary

**Task ID**: `{{TASK_ID}}`
**Agent**: {{AGENT_NAME}} ({{AGENT_SESSION}})
**Report Date**: {{REPORT_DATE}}
**Priority**: {{BLOCKER_PRIORITY}} 🔴/🟡/🟢
**Status**: {{BLOCKER_STATUS}}

---

## Blocker Details

### Type
{{BLOCKER_TYPE}}

**Categories**:
- [ ] Toolchain Issue (dependency, version, configuration)
- [ ] Environment Issue (permissions, missing tools, system)
- [ ] Code Issue (bug, design flaw, technical debt)
- [ ] Knowledge Gap (unclear requirements, missing context)
- [ ] External Dependency (API, service, third-party)
- [ ] Git/GitHub Issue (merge conflict, permissions, CI)
- [ ] Resource Issue (disk space, memory, CPU)
- [ ] Other: {{OTHER_TYPE}}

### Description
{{BLOCKER_DESCRIPTION}}

### Impact
{{BLOCKER_IMPACT}}

**Severity**:
- **Critical**: Task completely blocked, cannot proceed
- **High**: Major impediment, significant workaround needed
- **Medium**: Partial block, can continue with limitations
- **Low**: Minor issue, minimal impact on progress

**Current Severity**: {{BLOCKER_SEVERITY}}

---

## Toolchain Context

**Toolchain**: {{TOOLCHAIN_TYPE}}
**Template**: [{{TOOLCHAIN_TEMPLATE_PATH}}]({{TOOLCHAIN_TEMPLATE_PATH}})

### Environment State
```bash
$ {{VERIFY_ALL_CMD}}
{{VERIFY_OUTPUT}}
```

**Verification Status**: {{VERIFICATION_STATUS}} ✅/❌

### Specific Tool Issues

#### Language/Runtime
```bash
$ {{LANGUAGE}} --version
{{LANGUAGE_VERSION_OUTPUT}}
```
**Issue**: {{LANGUAGE_ISSUE}}

#### Package Manager
```bash
$ {{PACKAGE_MANAGER}} --version
{{PACKAGE_MANAGER_VERSION_OUTPUT}}
```
**Issue**: {{PACKAGE_MANAGER_ISSUE}}

#### Build Tool
```bash
$ {{BUILD_TOOL}} --version
{{BUILD_TOOL_VERSION_OUTPUT}}
```
**Issue**: {{BUILD_TOOL_ISSUE}}

#### Test Framework
```bash
$ {{TEST_CMD}}
{{TEST_ERROR_OUTPUT}}
```
**Issue**: {{TEST_FRAMEWORK_ISSUE}}

#### Linter/Formatter
```bash
$ {{LINT_CMD}}
{{LINT_ERROR_OUTPUT}}
```
**Issue**: {{LINTER_ISSUE}}

---

## Error Details

### Error Message
```
{{ERROR_MESSAGE}}
```

### Stack Trace
```
{{STACK_TRACE}}
```

### Logs
**Log Files**:
- {{LOG_FILE_1}}
- {{LOG_FILE_2}}
- {{LOG_FILE_N}}

**Relevant Log Excerpt**:
```
{{LOG_EXCERPT}}
```

---

## Reproduction Steps

1. {{STEP_1}}
2. {{STEP_2}}
3. {{STEP_3}}
...

**Minimal Reproduction**:
```bash
{{REPRODUCTION_COMMANDS}}
```

**Expected Result**: {{EXPECTED_RESULT}}
**Actual Result**: {{ACTUAL_RESULT}}

---

## Investigation Performed

### Debugging Steps Taken
{{DEBUGGING_STEPS}}

### Resources Consulted
{{RESOURCES_CONSULTED}}

### Attempted Solutions
{{ATTEMPTED_SOLUTIONS}}

### Why They Failed
{{WHY_FAILED}}

---

## Toolchain-Specific Diagnostics

### Dependency Tree
```bash
$ {{PACKAGE_MANAGER}} list/tree
{{DEPENDENCY_TREE}}
```

### Configuration Files
**Files Checked**:
- {{CONFIG_FILE_1}}
- {{CONFIG_FILE_2}}
- {{CONFIG_FILE_N}}

**Issues Found**: {{CONFIG_ISSUES}}

### Version Conflicts
{{VERSION_CONFLICTS}}

### Environment Variables
```bash
$ env | grep {{RELEVANT_ENV_VARS}}
{{ENV_VARS_OUTPUT}}
```

---

## Escalation Path

### Level 1: Self-Resolution Attempted ✅
{{SELF_RESOLUTION_ATTEMPTS}}

### Level 2: Documentation/Community
- [ ] Official documentation consulted
- [ ] Stack Overflow/GitHub issues searched
- [ ] Community forums checked

**Findings**: {{COMMUNITY_FINDINGS}}

### Level 3: Orchestrator Escalation 🚨
**Escalating to**: {{ORCHESTRATOR_NAME}}
**Reason**: {{ESCALATION_REASON}}

**Requested Action**:
{{REQUESTED_ACTION}}

---

## Proposed Solutions

### Option 1: {{SOLUTION_1_TITLE}}
**Description**: {{SOLUTION_1_DESC}}
**Pros**: {{SOLUTION_1_PROS}}
**Cons**: {{SOLUTION_1_CONS}}
**Effort**: {{SOLUTION_1_EFFORT}}
**Risk**: {{SOLUTION_1_RISK}}

### Option 2: {{SOLUTION_2_TITLE}}
**Description**: {{SOLUTION_2_DESC}}
**Pros**: {{SOLUTION_2_PROS}}
**Cons**: {{SOLUTION_2_CONS}}
**Effort**: {{SOLUTION_2_EFFORT}}
**Risk**: {{SOLUTION_2_RISK}}

### Option 3: {{SOLUTION_3_TITLE}}
**Description**: {{SOLUTION_3_DESC}}
**Pros**: {{SOLUTION_3_PROS}}
**Cons**: {{SOLUTION_3_CONS}}
**Effort**: {{SOLUTION_3_EFFORT}}
**Risk**: {{SOLUTION_3_RISK}}

**Recommended Solution**: {{RECOMMENDED_SOLUTION}}

---

## Workaround Available?

{{#if WORKAROUND_AVAILABLE}}
✅ **Yes - Temporary workaround available**

**Workaround**:
{{WORKAROUND_DESCRIPTION}}

**Limitations**:
{{WORKAROUND_LIMITATIONS}}

**Can Task Continue?**: {{CAN_CONTINUE_WITH_WORKAROUND}}
{{else}}
❌ **No workaround - Task blocked**

**Alternative Approach Possible?**: {{ALTERNATIVE_APPROACH}}
{{/if}}

---

## Timeline Impact

**Original Completion Estimate**: {{ORIGINAL_ESTIMATE}}
**Blocker Identified**: {{BLOCKER_IDENTIFIED_DATE}}
**Time Lost**: {{TIME_LOST}}
**New Completion Estimate**: {{NEW_ESTIMATE}}

**Delay**: {{DELAY_DURATION}}

---

## Help Required

### Specific Assistance Needed
{{ASSISTANCE_NEEDED}}

### Questions for Orchestrator
{{QUESTIONS_FOR_ORCHESTRATOR}}

### Resources Needed
{{RESOURCES_NEEDED}}

### Permissions Needed
{{PERMISSIONS_NEEDED}}

---

## Resolution

{{#if BLOCKER_RESOLVED}}
✅ **RESOLVED**

**Resolution Date**: {{RESOLUTION_DATE}}
**Resolved By**: {{RESOLVED_BY}}
**Solution Applied**: {{SOLUTION_APPLIED}}
**Time to Resolve**: {{TIME_TO_RESOLVE}}

**Lessons Learned**:
{{LESSONS_LEARNED}}

**Prevention Measures**:
{{PREVENTION_MEASURES}}
{{else}}
⏳ **UNRESOLVED - Awaiting action**

**Status**: {{BLOCKER_CURRENT_STATUS}}
**Next Steps**: {{BLOCKER_NEXT_STEPS}}
**Expected Resolution**: {{EXPECTED_RESOLUTION}}
{{/if}}

---

## Follow-up Actions

- [ ] {{ACTION_1}}
- [ ] {{ACTION_2}}
- [ ] {{ACTION_3}}

**Assigned To**: {{FOLLOWUP_ASSIGNED_TO}}
**Due Date**: {{FOLLOWUP_DUE_DATE}}

---

## Related Issues

**GitHub Issues**: {{GITHUB_ISSUES_LIST}}
**Related Blockers**: {{RELATED_BLOCKERS_LIST}}
**Upstream Issues**: {{UPSTREAM_ISSUES_LIST}}

---

## Attachments

### Evidence Files
- {{EVIDENCE_FILE_1}}
- {{EVIDENCE_FILE_2}}
- {{EVIDENCE_FILE_N}}

### Screenshots
{{SCREENSHOTS_LIST}}

### Debug Outputs
{{DEBUG_OUTPUTS_LIST}}

---

**Report Version**: 1.0.0
**Template**: [BLOCKER_REPORT_TEMPLATE.md](./BLOCKER_REPORT_TEMPLATE.md)
**Task Reference**: [TASK_DELEGATION: {{TASK_ID}}]({{TASK_DELEGATION_URL}})
