# Pull Request Template with Toolchain Verification

This document provides the standard PR template for EOA projects with toolchain verification.

## Table of Contents

- [PR Title Format](#pr-title-format)
- [PR Body Template](#pr-body-template)

### Related Documents

For complete examples and automation:

- **[PR_TEMPLATE-part1-feature-example.md](PR_TEMPLATE-part1-feature-example.md)** - Complete feature implementation PR example
  - SSH key management implementation example
  - Full test results formatting
  - All checklist items completed

- **[PR_TEMPLATE-part2-bugfix-example.md](PR_TEMPLATE-part2-bugfix-example.md)** - Complete bug fix PR example
  - Platform detection bug fix example
  - Docker container override solution
  - Test coverage for edge cases

- **[PR_TEMPLATE-part3-cli-automation.md](PR_TEMPLATE-part3-cli-automation.md)** - CLI commands and automation
  - gh CLI command examples
  - Automated PR creation script
  - Troubleshooting common issues

---

## PR Title Format

```
[{{TASK_ID}}] {{TITLE}}
```

Example: `[EOA-001] Implement remote Docker agent deployment`

## PR Body Template

```markdown
## Summary

{{SUMMARY}}

## Linked Issue

Closes #{{ISSUE_NUMBER}}

## Changes Made

### Core Changes
- {{CHANGE_1}}
- {{CHANGE_2}}
- {{CHANGE_3}}

### Files Modified
- `{{FILE_1}}` - {{MODIFICATION_1}}
- `{{FILE_2}}` - {{MODIFICATION_2}}
- `{{FILE_3}}` - {{MODIFICATION_3}}

## Toolchain Verification

**Platform Tested:** {{PLATFORM}}
**Toolchain Template:** [Link]({{TOOLCHAIN_TEMPLATE_PATH}})

### Environment Used
```yaml
platform: {{PLATFORM}}
python_version: {{PYTHON_VERSION}}
node_version: {{NODE_VERSION}}
system_dependencies:
  - {{DEPENDENCY_1}}: {{VERSION_1}}
  - {{DEPENDENCY_2}}: {{VERSION_2}}
```

### Toolchain Verification Checklist

- [ ] All required tools installed at correct versions
- [ ] Environment setup script ran successfully
- [ ] No missing dependencies reported
- [ ] Build completed without errors
- [ ] Tests ran in correct environment

## Test Results

### Unit Tests
```
{{UNIT_TEST_RESULTS}}
```
- **Total:** {{TOTAL_UNIT_TESTS}}
- **Passed:** {{PASSED_UNIT_TESTS}}
- **Failed:** {{FAILED_UNIT_TESTS}}
- **Skipped:** {{SKIPPED_UNIT_TESTS}}

### Integration Tests
```
{{INTEGRATION_TEST_RESULTS}}
```
- **Total:** {{TOTAL_INTEGRATION_TESTS}}
- **Passed:** {{PASSED_INTEGRATION_TESTS}}
- **Failed:** {{FAILED_INTEGRATION_TESTS}}
- **Skipped:** {{SKIPPED_INTEGRATION_TESTS}}

### Platform-Specific Tests
- [ ] Verified on {{PLATFORM}}
- [ ] Toolchain compatibility confirmed
- [ ] Environment setup validated
- [ ] No platform-specific failures

### Test Coverage
- **Coverage:** {{COVERAGE_PERCENTAGE}}%
- **Coverage Report:** [Link]({{COVERAGE_REPORT_URL}})

## Breaking Changes

{{BREAKING_CHANGES}}

- [ ] No breaking changes
- [ ] Breaking changes documented
- [ ] Migration guide provided
- [ ] Changelog updated

## Documentation Updates

- [ ] README updated
- [ ] API documentation updated
- [ ] Code comments added/updated
- [ ] Toolchain template updated
- [ ] CHANGELOG.md updated

## Review Checklist

### Code Quality
- [ ] Code follows project style guidelines
- [ ] No unnecessary code duplication
- [ ] Functions are focused and single-purpose
- [ ] Variable names are descriptive
- [ ] Complex logic is commented
- [ ] No debug code or commented-out blocks
- [ ] No hardcoded secrets or credentials

### Testing
- [ ] All new code has tests
- [ ] All tests pass locally
- [ ] All tests pass in CI
- [ ] Edge cases covered
- [ ] Error handling tested
- [ ] No flaky tests introduced

### Security
- [ ] No sensitive data exposed
- [ ] Input validation implemented
- [ ] Authentication/authorization checked
- [ ] Dependencies scanned for vulnerabilities
- [ ] Secrets stored securely

### Performance
- [ ] No performance regressions
- [ ] Resource usage is reasonable
- [ ] No memory leaks introduced
- [ ] Database queries optimized (if applicable)

### Toolchain
- [ ] Toolchain template accurate
- [ ] All dependencies documented
- [ ] Environment setup tested
- [ ] Version constraints specified
- [ ] Platform compatibility verified

## Deployment Notes

{{DEPLOYMENT_NOTES}}

### Deployment Checklist
- [ ] Database migrations (if needed)
- [ ] Configuration changes documented
- [ ] Environment variables updated
- [ ] Backwards compatibility maintained
- [ ] Rollback plan documented

## Screenshots/Recordings

{{SCREENSHOTS}}

## Additional Context

{{ADDITIONAL_CONTEXT}}

---

## For Reviewers

### Focus Areas
Please pay special attention to:
1. {{FOCUS_AREA_1}}
2. {{FOCUS_AREA_2}}
3. {{FOCUS_AREA_3}}

### Testing Instructions
To test this PR locally:

```bash
# 1. Checkout PR
gh pr checkout {{PR_NUMBER}}

# 2. Setup environment using toolchain template
{{TOOLCHAIN_SETUP_COMMAND}}

# 3. Run tests
{{TEST_COMMAND}}

# 4. Verify functionality
{{VERIFICATION_COMMAND}}
```

### Questions for Reviewers
- {{QUESTION_1}}
- {{QUESTION_2}}
```

---

## Next Steps

See the related documents for:
- Complete examples: [Feature Example](PR_TEMPLATE-part1-feature-example.md), [Bug Fix Example](PR_TEMPLATE-part2-bugfix-example.md)
- CLI automation: [CLI and Automation](PR_TEMPLATE-part3-cli-automation.md)
