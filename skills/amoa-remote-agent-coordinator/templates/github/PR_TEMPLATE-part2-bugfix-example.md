# PR Example: Bug Fix

This document provides a complete example of a bug fix PR for reference.

**Parent Document:** [PR_TEMPLATE.md](PR_TEMPLATE.md)

---

## Example: Platform Detection Bug Fix

```markdown
## Summary

Fixes platform detection bug where Docker containers running on macOS hosts were incorrectly identified as "macos" instead of "docker". The router now checks for the `ATLAS_PLATFORM_OVERRIDE` environment variable before detecting platform from host OS.

## Linked Issue

Closes #87

## Changes Made

### Core Changes
- Added `ATLAS_PLATFORM_OVERRIDE` environment variable support
- Updated platform detection to check override first
- Added validation for override values

### Files Modified
- `src/eoa/platform/detector.py` - Updated detection logic
- `src/eoa/config/environment.py` - Added override variable
- `tests/test_platform_detector.py` - Added override tests
- `docker/Dockerfile` - Set ATLAS_PLATFORM_OVERRIDE=docker
- `docs/platform-detection.md` - Updated documentation

## Toolchain Verification

**Platform Tested:** macos (Docker Desktop 4.26.1)
**Toolchain Template:** [templates/toolchains/macos-docker-debug.md](../toolchains/macos-docker-debug.md)

### Environment Used
```yaml
platform: macos
python_version: "3.12.1"
system_dependencies:
  - docker-desktop: 4.26.1
```

### Toolchain Verification Checklist

- [x] All required tools installed at correct versions
- [x] Environment setup script ran successfully
- [x] No missing dependencies reported
- [x] Build completed without errors
- [x] Tests ran in correct environment

## Test Results

### Unit Tests
```
test_platform_detector.py::test_override_variable PASSED
test_platform_detector.py::test_no_override PASSED
test_platform_detector.py::test_invalid_override PASSED
test_platform_detector.py::test_docker_override PASSED
```
- **Total:** 8
- **Passed:** 8
- **Failed:** 0
- **Skipped:** 0

### Integration Tests
```
test_routing_docker_macos.py::test_route_to_docker_on_macos PASSED
test_routing_docker_linux.py::test_route_to_docker_on_linux PASSED
```
- **Total:** 2
- **Passed:** 2
- **Failed:** 0
- **Skipped:** 0

### Platform-Specific Tests
- [x] Verified on macOS with Docker Desktop
- [x] Verified in Linux Docker container
- [x] Toolchain compatibility confirmed
- [x] Environment setup validated
- [x] No platform-specific failures

### Test Coverage
- **Coverage:** 96%
- **Coverage Report:** [View Coverage](https://coverage.example.com/pr/87)

## Breaking Changes

- [ ] No breaking changes

Existing behavior unchanged if `ATLAS_PLATFORM_OVERRIDE` is not set.

## Documentation Updates

- [x] README updated
- [x] API documentation updated
- [x] Code comments added
- [x] Toolchain template updated
- [x] CHANGELOG.md updated

## Review Checklist

### Code Quality
- [x] Code follows project style guidelines
- [x] No unnecessary code duplication
- [x] Functions are focused and single-purpose
- [x] Variable names are descriptive
- [x] Complex logic is commented
- [x] No debug code or commented-out blocks
- [x] No hardcoded secrets or credentials

### Testing
- [x] All new code has tests
- [x] All tests pass locally
- [x] All tests pass in CI
- [x] Edge cases covered (invalid override values)
- [x] Error handling tested
- [x] No flaky tests introduced

### Security
- [x] No sensitive data exposed
- [x] Input validation implemented (override value validation)
- [x] N/A - Authentication/authorization checked
- [x] Dependencies scanned for vulnerabilities
- [x] N/A - Secrets stored securely

### Performance
- [x] No performance regressions
- [x] Resource usage is reasonable
- [x] No memory leaks introduced
- [x] N/A - Database queries optimized

### Toolchain
- [x] Toolchain template accurate
- [x] All dependencies documented
- [x] Environment setup tested
- [x] Version constraints specified
- [x] Platform compatibility verified

## Deployment Notes

Update Docker startup scripts to set `ATLAS_PLATFORM_OVERRIDE=docker`.

### Deployment Checklist
- [x] N/A - Database migrations
- [x] Configuration changes documented
- [x] Environment variables updated (new ATLAS_PLATFORM_OVERRIDE)
- [x] Backwards compatibility maintained
- [x] N/A - Rollback plan (env var simply ignored if removed)

## Screenshots/Recordings

N/A

## Additional Context

The bug was caused by platform detection running inside Docker containers and detecting the host OS instead of recognizing it's running in a container. This is fixed by explicitly setting the platform via environment variable in the Dockerfile.

---

## For Reviewers

### Focus Areas
Please pay special attention to:
1. Validation logic for override values
2. Backwards compatibility with existing platform detection
3. Docker container startup script changes

### Testing Instructions
To test this PR locally:

```bash
# 1. Checkout PR
gh pr checkout 87

# 2. Setup environment
source templates/toolchains/macos-docker-debug.md

# 3. Run tests
uv run pytest tests/test_platform_detector.py -v

# 4. Test in Docker
docker build -t eoa-test .
docker run eoa-test python -c "from eoa.platform import get_platform; print(get_platform())"
# Should print: docker
```

### Questions for Reviewers
- Should we also support ATLAS_PLATFORM_OVERRIDE in the config file, or only as env var?
```

---

## Key Takeaways from This Example

1. **Root cause identified** - Clear explanation of why the bug occurred
2. **Backwards compatible** - Existing behavior preserved when env var not set
3. **Edge cases tested** - Invalid override values explicitly tested
4. **Deployment notes** - Clear instructions for updating Docker scripts
