# Verification Report

## Task: {{TASK_ID}}
## Date: {{TIMESTAMP}}
## Agent: {{AGENT_NAME}}
## Branch: {{BRANCH_NAME}}
## Commit: {{COMMIT_SHA}}

---

## Toolchain Verification

| Component | Expected | Actual | Status |
|-----------|----------|--------|--------|
| {{LANGUAGE}} | {{EXPECTED_LANG_VERSION}} | {{ACTUAL_LANG_VERSION}} | {{LANG_STATUS}} |
| Package Manager | {{EXPECTED_PKG_VERSION}} | {{ACTUAL_PKG_VERSION}} | {{PKG_STATUS}} |
| Linter | {{EXPECTED_LINTER_VERSION}} | {{ACTUAL_LINTER_VERSION}} | {{LINTER_STATUS}} |
| Formatter | {{EXPECTED_FORMATTER_VERSION}} | {{ACTUAL_FORMATTER_VERSION}} | {{FORMATTER_STATUS}} |
| Type Checker | {{EXPECTED_TYPECHECKER_VERSION}} | {{ACTUAL_TYPECHECKER_VERSION}} | {{TYPECHECKER_STATUS}} |

---

## Checklist Results by Category

### Build Verification
**Status**: {{BUILD_CATEGORY_STATUS}} | **Score**: {{BUILD_SCORE}}/{{BUILD_TOTAL}}

| Check | Status | Details |
|-------|--------|---------|
| {{BUILD_CHECK_1}} | {{BUILD_STATUS_1}} | {{BUILD_DETAILS_1}} |
| {{BUILD_CHECK_2}} | {{BUILD_STATUS_2}} | {{BUILD_DETAILS_2}} |
| {{BUILD_CHECK_3}} | {{BUILD_STATUS_3}} | {{BUILD_DETAILS_3}} |

### Code Quality
**Status**: {{QUALITY_CATEGORY_STATUS}} | **Score**: {{QUALITY_SCORE}}/{{QUALITY_TOTAL}}

| Check | Status | Details |
|-------|--------|---------|
| {{QUALITY_CHECK_1}} | {{QUALITY_STATUS_1}} | {{QUALITY_DETAILS_1}} |
| {{QUALITY_CHECK_2}} | {{QUALITY_STATUS_2}} | {{QUALITY_DETAILS_2}} |
| {{QUALITY_CHECK_3}} | {{QUALITY_STATUS_3}} | {{QUALITY_DETAILS_3}} |

### Testing
**Status**: {{TEST_CATEGORY_STATUS}} | **Score**: {{TEST_SCORE}}/{{TEST_TOTAL}}

| Check | Status | Details |
|-------|--------|---------|
| {{TEST_CHECK_1}} | {{TEST_STATUS_1}} | {{TEST_DETAILS_1}} |
| {{TEST_CHECK_2}} | {{TEST_STATUS_2}} | {{TEST_DETAILS_2}} |
| {{TEST_CHECK_3}} | {{TEST_STATUS_3}} | {{TEST_DETAILS_3}} |

### Documentation
**Status**: {{DOCS_CATEGORY_STATUS}} | **Score**: {{DOCS_SCORE}}/{{DOCS_TOTAL}}

| Check | Status | Details |
|-------|--------|---------|
| {{DOCS_CHECK_1}} | {{DOCS_STATUS_1}} | {{DOCS_DETAILS_1}} |
| {{DOCS_CHECK_2}} | {{DOCS_STATUS_2}} | {{DOCS_DETAILS_2}} |
| {{DOCS_CHECK_3}} | {{DOCS_STATUS_3}} | {{DOCS_DETAILS_3}} |

### Security
**Status**: {{SECURITY_CATEGORY_STATUS}} | **Score**: {{SECURITY_SCORE}}/{{SECURITY_TOTAL}}

| Check | Status | Details |
|-------|--------|---------|
| {{SECURITY_CHECK_1}} | {{SECURITY_STATUS_1}} | {{SECURITY_DETAILS_1}} |
| {{SECURITY_CHECK_2}} | {{SECURITY_STATUS_2}} | {{SECURITY_DETAILS_2}} |
| {{SECURITY_CHECK_3}} | {{SECURITY_STATUS_3}} | {{SECURITY_DETAILS_3}} |

---

## Test Results Summary

**Overall Status**: {{TEST_OVERALL_STATUS}}
**Total Tests**: {{TOTAL_TESTS}}
**Passed**: {{TESTS_PASSED}} ({{PASS_PERCENTAGE}}%)
**Failed**: {{TESTS_FAILED}}
**Skipped**: {{TESTS_SKIPPED}}
**Duration**: {{TEST_DURATION}}

### Test Breakdown by Module

| Module | Total | Passed | Failed | Skipped | Coverage |
|--------|-------|--------|--------|---------|----------|
| {{MODULE_1}} | {{MODULE_1_TOTAL}} | {{MODULE_1_PASSED}} | {{MODULE_1_FAILED}} | {{MODULE_1_SKIPPED}} | {{MODULE_1_COVERAGE}}% |
| {{MODULE_2}} | {{MODULE_2_TOTAL}} | {{MODULE_2_PASSED}} | {{MODULE_2_FAILED}} | {{MODULE_2_SKIPPED}} | {{MODULE_2_COVERAGE}}% |
| {{MODULE_3}} | {{MODULE_3_TOTAL}} | {{MODULE_3_PASSED}} | {{MODULE_3_FAILED}} | {{MODULE_3_SKIPPED}} | {{MODULE_3_COVERAGE}}% |

### Failed Tests

{{FAILED_TESTS_LIST}}

---

## Coverage Report

**Overall Coverage**: {{OVERALL_COVERAGE}}%
**Line Coverage**: {{LINE_COVERAGE}}%
**Branch Coverage**: {{BRANCH_COVERAGE}}%
**Function Coverage**: {{FUNCTION_COVERAGE}}%

### Coverage by File

| File | Lines | Branches | Functions | Coverage |
|------|-------|----------|-----------|----------|
| {{FILE_1}} | {{FILE_1_LINES}}% | {{FILE_1_BRANCHES}}% | {{FILE_1_FUNCTIONS}}% | {{FILE_1_COVERAGE}}% |
| {{FILE_2}} | {{FILE_2_LINES}}% | {{FILE_2_BRANCHES}}% | {{FILE_2_FUNCTIONS}}% | {{FILE_2_COVERAGE}}% |
| {{FILE_3}} | {{FILE_3_LINES}}% | {{FILE_3_BRANCHES}}% | {{FILE_3_FUNCTIONS}}% | {{FILE_3_COVERAGE}}% |

### Uncovered Critical Paths

{{UNCOVERED_PATHS_LIST}}

---

## Linter Results

**Status**: {{LINTER_STATUS}}
**Errors**: {{LINTER_ERRORS}}
**Warnings**: {{LINTER_WARNINGS}}
**Info**: {{LINTER_INFO}}

### Issues by Severity

| Severity | Count | Blocker |
|----------|-------|---------|
| Error | {{ERROR_COUNT}} | {{ERROR_BLOCKER}} |
| Warning | {{WARNING_COUNT}} | {{WARNING_BLOCKER}} |
| Info | {{INFO_COUNT}} | No |

### Top Issues

{{LINTER_TOP_ISSUES}}

---

## Formatter Results

**Status**: {{FORMATTER_STATUS}}
**Files Checked**: {{FORMATTER_FILES_CHECKED}}
**Files Formatted**: {{FORMATTER_FILES_FORMATTED}}
**Files with Issues**: {{FORMATTER_FILES_ISSUES}}

### Files Requiring Formatting

{{FORMATTER_FILES_LIST}}

---

## Type Checker Results

**Status**: {{TYPECHECKER_STATUS}}
**Files Checked**: {{TYPECHECKER_FILES_CHECKED}}
**Errors**: {{TYPECHECKER_ERRORS}}
**Warnings**: {{TYPECHECKER_WARNINGS}}

### Type Issues

| File | Line | Severity | Message |
|------|------|----------|---------|
| {{TYPE_FILE_1}} | {{TYPE_LINE_1}} | {{TYPE_SEVERITY_1}} | {{TYPE_MESSAGE_1}} |
| {{TYPE_FILE_2}} | {{TYPE_LINE_2}} | {{TYPE_SEVERITY_2}} | {{TYPE_MESSAGE_2}} |
| {{TYPE_FILE_3}} | {{TYPE_LINE_3}} | {{TYPE_SEVERITY_3}} | {{TYPE_MESSAGE_3}} |

---

## Verification Summary

**Overall Status**: {{VERIFICATION_OVERALL_STATUS}}
**Total Checks**: {{TOTAL_CHECKS}}
**Passed**: {{CHECKS_PASSED}}
**Failed**: {{CHECKS_FAILED}}
**Warnings**: {{CHECKS_WARNINGS}}

**Blockers**: {{BLOCKER_COUNT}}
{{BLOCKER_LIST}}

**Critical Issues**: {{CRITICAL_COUNT}}
{{CRITICAL_LIST}}

**Verification Duration**: {{VERIFICATION_DURATION}}

---

## Next Steps

{{NEXT_STEPS}}

---

## Artifacts

**Test Report**: {{TEST_REPORT_PATH}}
**Coverage Report**: {{COVERAGE_REPORT_PATH}}
**Linter Report**: {{LINTER_REPORT_PATH}}
**Type Checker Report**: {{TYPECHECKER_REPORT_PATH}}
**Full Log**: {{FULL_LOG_PATH}}

---

*Report generated by {{GENERATOR}} on {{TIMESTAMP}}*
