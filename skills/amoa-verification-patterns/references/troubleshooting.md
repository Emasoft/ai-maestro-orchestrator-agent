# Troubleshooting


## Contents

- [Table of Contents](#table-of-contents)
- [10.1 Tests Pass Locally but Fail in CI/CD](#101-tests-pass-locally-but-fail-in-cicd)
- [10.2 Exit Code is 0 but Process Failed](#102-exit-code-is-0-but-process-failed)
- [10.3 Integration Test Fails with Timeout](#103-integration-test-fails-with-timeout)
- [10.4 E2E Test is Flaky](#104-e2e-test-is-flaky)
- [10.5 Verification Requires Access to Internal State](#105-verification-requires-access-to-internal-state)

---

## Table of Contents

- [10.1 Tests Pass Locally but Fail in CI/CD](#101-tests-pass-locally-but-fail-in-cicd)
  - 10.1.1 Cause: Environment differences
  - 10.1.2 Solution steps
- [10.2 Exit Code is 0 but Process Failed](#102-exit-code-is-0-but-process-failed)
  - 10.2.1 Cause: Incorrect exit code setting
  - 10.2.2 Solution steps
- [10.3 Integration Test Fails with Timeout](#103-integration-test-fails-with-timeout)
  - 10.3.1 Cause: Slow or unresponsive component
  - 10.3.2 Solution steps
- [10.4 E2E Test is Flaky](#104-e2e-test-is-flaky)
  - 10.4.1 Cause: Race conditions or async issues
  - 10.4.2 Solution steps
- [10.5 Verification Requires Access to Internal State](#105-verification-requires-access-to-internal-state)
  - 10.5.1 Cause: Cannot observe behavior externally
  - 10.5.2 Solution steps

---

## 10.1 Tests Pass Locally but Fail in CI/CD

**Cause**: Test environment is different locally vs CI/CD

**Solution**:
1. Check environment variables (are they set in CI/CD?)
2. Check paths (are absolute paths used instead of relative?)
3. Check external services (are they available in CI/CD?)
4. Check database state (is test database clean in CI/CD?)
5. Run the same test in the CI/CD environment to reproduce

---

## 10.2 Exit Code is 0 but Process Failed

**Cause**: Process did not set correct exit code

**Solution**:
1. Check the process code - does it call `sys.exit()` or `exit()`?
2. Check for unhandled exceptions (they may prevent exit code from being set)
3. Add explicit exit code at end of script
4. Test exit code directly: `python3 script.py; echo $?`

---

## 10.3 Integration Test Fails with Timeout

**Cause**: Component is slow or not responding

**Solution**:
1. Increase timeout value
2. Check if component is running: `curl http://localhost:8001` or equivalent
3. Check component logs for errors
4. Verify network connectivity between components
5. Run component in isolation to check if it works

---

## 10.4 E2E Test is Flaky

**Cause**: Test is not waiting for async operations or has race conditions

**Solution**:
1. Add explicit waits: `wait_for_element()` instead of immediate checks
2. Increase wait times (network can be slow)
3. Ensure clean state before test (database, files)
4. Run test multiple times to verify consistency
5. Check for timing-dependent code in the application

---

## 10.5 Verification Requires Access to Internal State

**Cause**: Cannot observe behavior from outside the system

**Solution**:
1. Add logging to the code being tested
2. Export state to file (JSON, CSV) and verify
3. Use a test database you can query
4. Use debug endpoints (only in test environment)
5. Use dependency injection to inject test doubles
