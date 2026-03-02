---
procedure: support-skill
workflow-instruction: support
---

# Operation: Compile Test Coverage Checklist


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Create Unit Test Section](#step-1-create-unit-test-section)
- [Unit Tests](#unit-tests)
  - [Step 2: Create Integration Test Section](#step-2-create-integration-test-section)
- [Integration Tests](#integration-tests)
  - [Step 3: Create Edge Case Section](#step-3-create-edge-case-section)
- [Edge Cases](#edge-cases)
  - [Step 4: Create Error Handling Section](#step-4-create-error-handling-section)
- [Error Handling](#error-handling)
  - [Step 5: Create Coverage Metrics Section](#step-5-create-coverage-metrics-section)
- [Coverage Metrics](#coverage-metrics)
  - [Step 6: Create Test Quality Section](#step-6-create-test-quality-section)
- [Test Quality](#test-quality)
  - [Step 7: Add RULE 14 Compliance Section](#step-7-add-rule-14-compliance-section)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
  - [Step 8: Assemble Complete Checklist](#step-8-assemble-complete-checklist)
- [Unit Tests](#unit-tests)
- [Integration Tests](#integration-tests)
- [Edge Cases](#edge-cases)
- [Error Handling](#error-handling)
- [Coverage Metrics](#coverage-metrics)
- [Test Quality](#test-quality)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example](#example)
- [Unit Tests](#unit-tests)
- [Integration Tests](#integration-tests)
- [Edge Cases](#edge-cases)
- [Error Handling](#error-handling)
- [Coverage Metrics](#coverage-metrics)
- [Test Quality](#test-quality)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
- [Checklist](#checklist)

## When to Use

Use this operation when you need to create a checklist that ensures comprehensive test coverage for a module or feature.

## Prerequisites

- Module or feature code complete or in progress
- Understanding of acceptance criteria
- Test framework configured (pytest, jest, etc.)

## Procedure

### Step 1: Create Unit Test Section

```markdown
## Unit Tests
- [ ] All public functions have tests
- [ ] All public methods have tests
- [ ] Each function's happy path tested
- [ ] Each function's error path tested
- [ ] Return values verified
- [ ] Side effects verified
```

### Step 2: Create Integration Test Section

```markdown
## Integration Tests
- [ ] Database interactions tested
- [ ] External API calls tested
- [ ] File system operations tested
- [ ] Message queue interactions tested
- [ ] Service-to-service calls tested
```

### Step 3: Create Edge Case Section

```markdown
## Edge Cases
- [ ] Null/None inputs handled
- [ ] Empty collections handled
- [ ] Boundary values tested (0, max, min)
- [ ] Unicode/special characters handled
- [ ] Very long inputs handled
- [ ] Concurrent access tested
```

### Step 4: Create Error Handling Section

```markdown
## Error Handling
- [ ] Invalid input raises appropriate error
- [ ] Network failures handled gracefully
- [ ] Timeout conditions tested
- [ ] Resource exhaustion handled
- [ ] Partial failure scenarios tested
```

### Step 5: Create Coverage Metrics Section

```markdown
## Coverage Metrics
- [ ] Line coverage >= 80%
- [ ] Branch coverage >= 75%
- [ ] Function coverage >= 90%
- [ ] Critical paths 100% covered
- [ ] No untested public APIs
```

### Step 6: Create Test Quality Section

```markdown
## Test Quality
- [ ] Tests are independent (no order dependency)
- [ ] Tests are deterministic (no random failures)
- [ ] Tests are fast (< 1s per test)
- [ ] Tests are readable (clear naming)
- [ ] Tests use appropriate assertions
- [ ] Tests clean up after themselves
```

### Step 7: Add RULE 14 Compliance Section

```markdown
## Requirement Compliance (RULE 14)
- [ ] USER_REQUIREMENTS.md exists and is current
- [ ] All user requirements addressed
- [ ] No technology substitutions without approval
- [ ] No scope reductions without approval
```

### Step 8: Assemble Complete Checklist

```markdown
# Test Coverage Checklist: <module-name>

**Generated**: <timestamp>
**Module**: <module-name>
**Test Framework**: <pytest/jest/etc>

## Unit Tests
[items from Step 1]

## Integration Tests
[items from Step 2]

## Edge Cases
[items from Step 3]

## Error Handling
[items from Step 4]

## Coverage Metrics
[items from Step 5]

## Test Quality
[items from Step 6]

## Requirement Compliance (RULE 14)
[items from Step 7]

---
**Target Coverage**: 80% overall, 90% for critical paths
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| Checklist | Markdown | Complete test coverage checklist |
| Coverage Target | Percentage | Required coverage levels |
| Test Categories | Array | Types of tests needed |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Cannot determine coverage | No coverage tool | Configure coverage tool (coverage.py, istanbul) |
| Too many test cases | Over-scoped module | Break module into smaller units |
| External dependencies | Cannot test in isolation | Use mocks for external services |

## Example

```markdown
# Test Coverage Checklist: auth-core

**Generated**: 2024-01-15T18:00:00Z
**Module**: auth-core
**Test Framework**: pytest

## Unit Tests
- [ ] test_login_success
- [ ] test_login_invalid_password
- [ ] test_login_user_not_found
- [ ] test_generate_token
- [ ] test_validate_token
- [ ] test_validate_expired_token
- [ ] test_refresh_token
- [ ] test_logout
- [ ] test_password_hash

## Integration Tests
- [ ] test_login_with_database
- [ ] test_token_storage_redis
- [ ] test_user_creation_flow
- [ ] test_concurrent_logins
- [ ] test_session_persistence

## Edge Cases
- [ ] test_empty_password (must reject)
- [ ] test_empty_username (must reject)
- [ ] test_very_long_password (2000+ chars)
- [ ] test_unicode_username
- [ ] test_special_chars_password
- [ ] test_max_login_attempts

## Error Handling
- [ ] test_database_connection_failure
- [ ] test_redis_timeout
- [ ] test_malformed_token
- [ ] test_clock_skew_token_validation
- [ ] test_concurrent_token_refresh

## Coverage Metrics
- [ ] Line coverage: target 85%, current: ___
- [ ] Branch coverage: target 80%, current: ___
- [ ] Function coverage: target 95%, current: ___
- [ ] login() function: 100%
- [ ] validate_token(): 100%

## Test Quality
- [x] Tests are independent
- [x] Tests use fixtures for setup
- [x] Tests use parametrize for variations
- [ ] Average test time: target < 0.5s
- [x] Clear test naming convention
- [x] Cleanup via fixtures

## Requirement Compliance (RULE 14)
- [ ] USER_REQUIREMENTS.md verified
- [ ] All auth requirements have tests
- [ ] Testing approved libraries
- [ ] Full feature coverage

---
**Target Coverage**: 85% overall, 100% for login/token functions
**Run Command**: `pytest tests/unit/auth/ -v --cov=src/auth`
```

## Checklist

- [ ] Identify all public functions/methods to test
- [ ] Create unit test items for each function
- [ ] Create integration test items
- [ ] Identify edge cases to test
- [ ] Create error handling test items
- [ ] Define coverage metrics targets
- [ ] Create test quality items
- [ ] Add RULE 14 compliance section
- [ ] Review for completeness
- [ ] Write tests according to checklist
