# Platform Module Base Template

This is the base template for all platform-specific modules. Each platform module (macOS, Windows, Linux) extends this template.

**This document is an index**. Content has been split into smaller parts for easier navigation and consumption.

---

## Table of Contents

### Part 1: Module Identification, Dependencies & Build

**File**: [PLATFORM_MODULE_BASE-part1-identification-dependencies-build.md](./PLATFORM_MODULE_BASE-part1-identification-dependencies-build.md)

**Contents**:
- Module Identification
  - Module YAML configuration schema
  - Variables: MODULE_NAME, MODULE_VERSION, PLATFORM_NAME, ARCH, MODULE_TYPE
- Dependency Declarations
  - Shared Dependencies across platforms
  - Platform-Specific Dependencies with examples for macOS
- Build Configuration
  - Compiler Settings (rustc, clang, msvc, gcc)
  - Build Targets with target triples and output types
  - Build Scripts (pre_build, build, post_build)

---

### Part 2: Test Configuration & Cross-Platform Sync

**File**: [PLATFORM_MODULE_BASE-part2-testing-sync.md](./PLATFORM_MODULE_BASE-part2-testing-sync.md)

**Contents**:
- Test Configuration
  - Unit Tests with environment variables and timeouts
  - Integration Tests with setup/teardown commands
  - Platform-Specific Tests with run conditions
- Cross-Platform Synchronization Rules
  - Shared Code Locations and bidirectional sync
  - Version Alignment strategies (strict, relaxed, independent)
  - Feature Parity Matrix for tracking platform support

---

### Part 3: CI/CD, Metadata & Usage

**File**: [PLATFORM_MODULE_BASE-part3-cicd-metadata-usage.md](./PLATFORM_MODULE_BASE-part3-cicd-metadata-usage.md)

**Contents**:
- CI/CD Integration
  - CI Matrix Configuration for platforms and architectures
  - GitHub Actions example with setup, build, test, package steps
- Module Metadata
  - Registration Information (author, maintainer, repository, license)
  - Compatibility Matrix with OS version ranges
- File Structure Template
  - Complete directory structure for platform modules
- Usage Instructions
  - Creating a New Platform Module (6 steps)
  - Updating an Existing Module (6 steps)
- Troubleshooting
  - Build Failures (compiler not found, missing dependencies, architecture mismatch)
  - Test Failures (timeouts, platform-specific failures)
  - Sync Issues (version mismatch, missing features)
- Template Validation Checklist
- Related Templates links

---

## Quick Reference

| Section | When to Read |
|---------|--------------|
| Part 1 - Identification | When creating a new module or defining dependencies |
| Part 1 - Build | When configuring compilers, targets, or build scripts |
| Part 2 - Testing | When setting up unit/integration tests |
| Part 2 - Sync | When managing cross-platform code sharing |
| Part 3 - CI/CD | When configuring GitHub Actions or CI pipelines |
| Part 3 - Metadata | When publishing or documenting a module |
| Part 3 - Usage | When creating or updating platform modules |
| Part 3 - Troubleshooting | When encountering build, test, or sync issues |

---

## Related Templates

- [MACOS_MODULE.md](./MACOS_MODULE.md) - macOS-specific module template
- [WINDOWS_MODULE.md](./WINDOWS_MODULE.md) - Windows-specific module template
- [LINUX_MODULE.md](./LINUX_MODULE.md) - Linux-specific module template
- [CROSS_PLATFORM_SYNC.md](./CROSS_PLATFORM_SYNC.md) - Synchronization rules and strategies
