# Pull Request Status Report

## PR: {{PR_NUMBER}} - {{PR_TITLE}}
## Date: {{TIMESTAMP}}
## Agent: {{AGENT_NAME}}
## Repository: {{REPO_OWNER}}/{{REPO_NAME}}

---

## PR Metadata

**URL**: {{PR_URL}}
**Status**: {{PR_STATUS}}
**Author**: {{PR_AUTHOR}}
**Created**: {{PR_CREATED_AT}}
**Updated**: {{PR_UPDATED_AT}}
**Branch**: `{{SOURCE_BRANCH}}` → `{{TARGET_BRANCH}}`
**Commits**: {{COMMIT_COUNT}}
**Files Changed**: {{FILES_CHANGED}}
**Additions**: +{{ADDITIONS}} | **Deletions**: -{{DELETIONS}}

### Labels

{{PR_LABELS}}

### Linked Issues

{{LINKED_ISSUES}}

### Assignees

{{ASSIGNEES}}

### Reviewers

{{REVIEWERS}}

---

## Toolchain Verification

**Status**: {{TOOLCHAIN_STATUS}}

| Component | Required | Detected | Status |
|-----------|----------|----------|--------|
| {{LANG_NAME}} | {{LANG_REQUIRED}} | {{LANG_DETECTED}} | {{LANG_STATUS}} |
| Package Manager | {{PKG_REQUIRED}} | {{PKG_DETECTED}} | {{PKG_STATUS}} |
| Build Tool | {{BUILD_REQUIRED}} | {{BUILD_DETECTED}} | {{BUILD_STATUS}} |
| Linter | {{LINTER_REQUIRED}} | {{LINTER_DETECTED}} | {{LINTER_STATUS}} |
| Formatter | {{FORMATTER_REQUIRED}} | {{FORMATTER_DETECTED}} | {{FORMATTER_STATUS}} |
| Type Checker | {{TYPECHECKER_REQUIRED}} | {{TYPECHECKER_DETECTED}} | {{TYPECHECKER_STATUS}} |

### Toolchain Issues

{{TOOLCHAIN_ISSUES}}

---

## CI/CD Pipeline Status

**Overall Status**: {{CI_OVERALL_STATUS}}

### Workflow Runs

| Workflow | Status | Started | Duration | Conclusion |
|----------|--------|---------|----------|------------|
| {{WORKFLOW_1}} | {{WORKFLOW_1_STATUS}} | {{WORKFLOW_1_STARTED}} | {{WORKFLOW_1_DURATION}} | {{WORKFLOW_1_CONCLUSION}} |
| {{WORKFLOW_2}} | {{WORKFLOW_2_STATUS}} | {{WORKFLOW_2_STARTED}} | {{WORKFLOW_2_DURATION}} | {{WORKFLOW_2_CONCLUSION}} |
| {{WORKFLOW_3}} | {{WORKFLOW_3_STATUS}} | {{WORKFLOW_3_STARTED}} | {{WORKFLOW_3_DURATION}} | {{WORKFLOW_3_CONCLUSION}} |

### Job Details

| Job | Status | Steps Passed | Steps Failed | Duration |
|-----|--------|--------------|--------------|----------|
| {{JOB_1}} | {{JOB_1_STATUS}} | {{JOB_1_PASSED}} | {{JOB_1_FAILED}} | {{JOB_1_DURATION}} |
| {{JOB_2}} | {{JOB_2_STATUS}} | {{JOB_2_PASSED}} | {{JOB_2_FAILED}} | {{JOB_2_DURATION}} |
| {{JOB_3}} | {{JOB_3_STATUS}} | {{JOB_3_PASSED}} | {{JOB_3_FAILED}} | {{JOB_3_DURATION}} |

### Failed Jobs

{{FAILED_JOBS_DETAILS}}

### Check Runs

| Check | Status | Conclusion | Started | Completed |
|-------|--------|------------|---------|-----------|
| {{CHECK_1}} | {{CHECK_1_STATUS}} | {{CHECK_1_CONCLUSION}} | {{CHECK_1_STARTED}} | {{CHECK_1_COMPLETED}} |
| {{CHECK_2}} | {{CHECK_2_STATUS}} | {{CHECK_2_CONCLUSION}} | {{CHECK_2_STARTED}} | {{CHECK_2_COMPLETED}} |
| {{CHECK_3}} | {{CHECK_3_STATUS}} | {{CHECK_3_CONCLUSION}} | {{CHECK_3_STARTED}} | {{CHECK_3_COMPLETED}} |

---

## Review Status

**Review Decision**: {{REVIEW_DECISION}}
**Reviews Required**: {{REVIEWS_REQUIRED}}
**Reviews Approved**: {{REVIEWS_APPROVED}}
**Reviews Pending**: {{REVIEWS_PENDING}}
**Changes Requested**: {{CHANGES_REQUESTED}}

### Review Details

| Reviewer | Status | Submitted | Comments |
|----------|--------|-----------|----------|
| {{REVIEWER_1}} | {{REVIEWER_1_STATUS}} | {{REVIEWER_1_SUBMITTED}} | {{REVIEWER_1_COMMENTS}} |
| {{REVIEWER_2}} | {{REVIEWER_2_STATUS}} | {{REVIEWER_2_SUBMITTED}} | {{REVIEWER_2_COMMENTS}} |
| {{REVIEWER_3}} | {{REVIEWER_3_STATUS}} | {{REVIEWER_3_SUBMITTED}} | {{REVIEWER_3_COMMENTS}} |

### Review Comments Summary

**Total Comments**: {{TOTAL_COMMENTS}}
**Unresolved Threads**: {{UNRESOLVED_THREADS}}
**Resolved Threads**: {{RESOLVED_THREADS}}

#### Unresolved Comments

{{UNRESOLVED_COMMENTS_LIST}}

---

## Merge Readiness Checklist

### Required Checks
- [{{REQUIRED_CHECK_1}}] {{REQUIRED_CHECK_1_NAME}}
- [{{REQUIRED_CHECK_2}}] {{REQUIRED_CHECK_2_NAME}}
- [{{REQUIRED_CHECK_3}}] {{REQUIRED_CHECK_3_NAME}}
- [{{REQUIRED_CHECK_4}}] {{REQUIRED_CHECK_4_NAME}}
- [{{REQUIRED_CHECK_5}}] {{REQUIRED_CHECK_5_NAME}}

### Code Quality
- [{{QUALITY_CHECK_1}}] All tests passing
- [{{QUALITY_CHECK_2}}] Code coverage meets threshold ({{COVERAGE_THRESHOLD}}%)
- [{{QUALITY_CHECK_3}}] No linter errors
- [{{QUALITY_CHECK_4}}] Code formatted correctly
- [{{QUALITY_CHECK_5}}] Type checking passes

### Review Requirements
- [{{REVIEW_CHECK_1}}] Required reviews approved ({{REVIEWS_APPROVED}}/{{REVIEWS_REQUIRED}})
- [{{REVIEW_CHECK_2}}] No changes requested
- [{{REVIEW_CHECK_3}}] All review comments resolved

### Documentation
- [{{DOCS_CHECK_1}}] README updated (if needed)
- [{{DOCS_CHECK_2}}] CHANGELOG updated
- [{{DOCS_CHECK_3}}] API documentation current
- [{{DOCS_CHECK_4}}] Code comments adequate

### Branch Status
- [{{BRANCH_CHECK_1}}] Up to date with target branch
- [{{BRANCH_CHECK_2}}] No merge conflicts
- [{{BRANCH_CHECK_3}}] Commits squashed (if required)

### Security
- [{{SECURITY_CHECK_1}}] No secrets in commits
- [{{SECURITY_CHECK_2}}] Dependencies security scan passed
- [{{SECURITY_CHECK_3}}] No critical vulnerabilities

---

## Merge Blockers

**Total Blockers**: {{BLOCKER_COUNT}}

{{BLOCKER_LIST}}

---

## Merge Conflicts

**Conflicts**: {{CONFLICT_COUNT}}

{{CONFLICT_DETAILS}}

---

## PR Summary

**Overall Readiness**: {{OVERALL_READINESS}}
**Merge Recommendation**: {{MERGE_RECOMMENDATION}}

**Strengths**:
{{STRENGTHS_LIST}}

**Issues to Address**:
{{ISSUES_LIST}}

**Estimated Time to Merge**: {{TIME_TO_MERGE}}

---

## Actions Required

### For Agent
{{AGENT_ACTIONS}}

### For Reviewers
{{REVIEWER_ACTIONS}}

### For Maintainers
{{MAINTAINER_ACTIONS}}

---

## Recent Activity

| Time | Actor | Action | Details |
|------|-------|--------|---------|
| {{ACTIVITY_1_TIME}} | {{ACTIVITY_1_ACTOR}} | {{ACTIVITY_1_ACTION}} | {{ACTIVITY_1_DETAILS}} |
| {{ACTIVITY_2_TIME}} | {{ACTIVITY_2_ACTOR}} | {{ACTIVITY_2_ACTION}} | {{ACTIVITY_2_DETAILS}} |
| {{ACTIVITY_3_TIME}} | {{ACTIVITY_3_ACTOR}} | {{ACTIVITY_3_ACTION}} | {{ACTIVITY_3_DETAILS}} |

---

## Artifacts

**CI Logs**: {{CI_LOGS_URL}}
**Coverage Report**: {{COVERAGE_REPORT_URL}}
**Test Report**: {{TEST_REPORT_URL}}
**Build Artifacts**: {{BUILD_ARTIFACTS_URL}}

---

*Report generated by {{GENERATOR}} on {{TIMESTAMP}}*
