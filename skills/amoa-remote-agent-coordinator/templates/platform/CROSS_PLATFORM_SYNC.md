# Cross-Platform Synchronization Rules

This document defines how platform-specific modules share code, maintain version alignment, and ensure feature parity across macOS, Windows, and Linux.

**Read [PLATFORM_MODULE_BASE.md](./PLATFORM_MODULE_BASE.md) first** - This document extends the synchronization concepts introduced there.

---

## Contents

This document is split into multiple parts for easier navigation:

| Part | Topic | Description |
|------|-------|-------------|
| [Part 1](./CROSS_PLATFORM_SYNC-part1-shared-code.md) | Shared Code Synchronization | Code organization, linking strategies, sync rules, preventing divergence |
| [Part 2](./CROSS_PLATFORM_SYNC-part2-version-alignment.md) | Version Alignment Strategies | Strict, relaxed, and independent versioning approaches |
| [Part 3](./CROSS_PLATFORM_SYNC-part3-feature-parity.md) | Feature Parity Matrix | Tracking feature implementation status across platforms |
| [Part 4](./CROSS_PLATFORM_SYNC-part4-cicd.md) | CI/CD Matrix Configuration | Multi-platform build and test workflows |
| [Part 5](./CROSS_PLATFORM_SYNC-part5-release.md) | Release Coordination | Release process, scripts, breaking change management |
| [Part 6](./CROSS_PLATFORM_SYNC-part6-testing-docs.md) | Testing & Documentation | Test utilities, documentation structure, troubleshooting |

---

## Part 1: Shared Code Synchronization

**File**: [CROSS_PLATFORM_SYNC-part1-shared-code.md](./CROSS_PLATFORM_SYNC-part1-shared-code.md)

### Topics Covered

- **Code Organization Structure** - Directory layout for shared and platform-specific code
- **Shared Code Linking Strategy** - Three options:
  - Option 1: Symbolic Links (Recommended)
  - Option 2: Git Subtree
  - Option 3: Cargo Workspace
- **Synchronization Rules** - YAML configuration for sync behavior
- **Preventing Divergence** - Pre-commit hooks and CI checks

### When to Read

Read this section when:
- Setting up a new cross-platform project
- Deciding how to share code between platforms
- Troubleshooting code divergence issues

---

## Part 2: Version Alignment Strategies

**File**: [CROSS_PLATFORM_SYNC-part2-version-alignment.md](./CROSS_PLATFORM_SYNC-part2-version-alignment.md)

### Topics Covered

- **Strategy 1: Strict Alignment** - All platforms must have identical versions
- **Strategy 2: Relaxed Alignment** - Major.minor must match, patch can differ
- **Strategy 3: Independent Versioning** - Platforms have completely different versions
- **Version Coordination File** - VERSION_MATRIX.yaml format and usage

### When to Read

Read this section when:
- Deciding on a versioning strategy for your project
- Planning a release that affects multiple platforms
- Documenting version compatibility between platforms

---

## Part 3: Feature Parity Matrix

**File**: [CROSS_PLATFORM_SYNC-part3-feature-parity.md](./CROSS_PLATFORM_SYNC-part3-feature-parity.md)

### Topics Covered

- **Feature Parity Matrix** - YAML format for tracking features across platforms:
  - Core Features (must be implemented on all platforms)
  - Platform-Specific Features (optional)
  - Experimental Features (not guaranteed to work)
- **Feature Status Definitions** - implemented, in-progress, planned, not_supported, not_applicable
- **Generating Feature Parity Report** - Script to create markdown tables

### When to Read

Read this section when:
- Adding a new feature and need to track implementation status
- Reviewing which features are available on each platform
- Creating release notes or documentation

---

## Part 4: CI/CD Matrix Configuration

**File**: [CROSS_PLATFORM_SYNC-part4-cicd.md](./CROSS_PLATFORM_SYNC-part4-cicd.md)

### Topics Covered

- **Multi-Platform Build Matrix** - GitHub Actions workflow for building on:
  - macOS (Intel and ARM)
  - Windows (x64 and x86)
  - Linux (glibc and musl)
- **Platform-Specific Test Suites** - Separate workflow for platform-specific tests

### When to Read

Read this section when:
- Setting up CI/CD for a cross-platform project
- Adding a new build target or platform
- Debugging CI failures on specific platforms

---

## Part 5: Release Coordination

**File**: [CROSS_PLATFORM_SYNC-part5-release.md](./CROSS_PLATFORM_SYNC-part5-release.md)

### Topics Covered

- **Coordinated Release Process** - Checklist for synchronized releases
- **Automated Release Script** - Bash script for version bumping and tagging
- **Breaking Change Policy** - Announcement and migration support requirements
- **Breaking Change Process** - Four phases: Announcement, Deprecation, Migration, Removal
- **Breaking Change Example** - Template for documenting breaking changes

### When to Read

Read this section when:
- Preparing a new release
- Planning a breaking change that affects all platforms
- Creating migration documentation for users

---

## Part 6: Testing & Documentation

**File**: [CROSS_PLATFORM_SYNC-part6-testing-docs.md](./CROSS_PLATFORM_SYNC-part6-testing-docs.md)

### Topics Covered

- **Shared Test Utilities** - Rust code for platform-agnostic test fixtures
- **Platform-Specific Test Verification** - Script to run tests on current platform
- **Documentation Structure** - Recommended folder layout for docs
- **Documentation Review Checklist** - What to update when adding features, breaking changes, or releases
- **Troubleshooting** - Common sync and build failures with solutions

### When to Read

Read this section when:
- Writing tests that need to work across platforms
- Updating documentation after a change
- Debugging sync or build failures

---

## Quick Reference

### Key Files

| File | Purpose |
|------|---------|
| `VERSION_MATRIX.yaml` | Track versions and compatibility across platforms |
| `feature_parity.yaml` | Track feature implementation status |
| `BREAKING_CHANGES.md` | Document breaking changes and migration guides |
| `CHANGELOG.md` | Release notes for all platforms |

### Key Scripts

| Script | Purpose |
|--------|---------|
| `scripts/sync-shared-code.sh` | Re-sync shared code from canonical source |
| `scripts/check-shared-code-sync.sh` | Verify shared code hasn't diverged |
| `scripts/test-all-platforms.sh` | Run tests on all platforms |
| `scripts/build-all-platforms.sh` | Build for all platforms |
| `scripts/release.sh` | Prepare a coordinated release |
| `scripts/generate-feature-report.sh` | Generate feature parity markdown |

### Version Alignment Decision Tree

```
Do platforms share significant code?
├── Yes → Use Strict Alignment
│         (All platforms same version)
│
└── No → Do platforms have similar maturity?
         ├── Yes → Use Relaxed Alignment
         │         (Same major.minor, different patch)
         │
         └── No → Use Independent Versioning
                  (Maintain compatibility matrix)
```

---

## Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| Shared code diverged | Run `./scripts/sync-shared-code.sh` |
| Version mismatch | Update VERSION_MATRIX.yaml |
| Feature parity test failing | Update feature_parity.yaml or implement missing features |
| Build fails on one platform | Check platform-specific dependencies |
| Tests pass locally, fail in CI | Verify CI environment matches local |

---

## Related Documentation

- [PLATFORM_MODULE_BASE.md](./PLATFORM_MODULE_BASE.md) - Base module template
- [MACOS_MODULE.md](./MACOS_MODULE.md) - macOS-specific configuration
- [WINDOWS_MODULE.md](./WINDOWS_MODULE.md) - Windows-specific configuration
- [LINUX_MODULE.md](./LINUX_MODULE.md) - Linux-specific configuration
