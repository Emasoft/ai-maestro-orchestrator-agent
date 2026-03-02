# Cross-Platform Synchronization: Version Alignment

This document covers version alignment strategies for cross-platform development.

**Parent document**: [CROSS_PLATFORM_SYNC.md](./CROSS_PLATFORM_SYNC.md)

---

## Contents

1. [Strict Alignment Strategy](#strategy-1-strict-alignment-recommended)
2. [Relaxed Alignment Strategy](#strategy-2-relaxed-alignment)
3. [Independent Versioning Strategy](#strategy-3-independent-versioning)
4. [Version Coordination File](#version-coordination-file)

---

## Strategy 1: Strict Alignment (Recommended)

All platforms must have identical version numbers:

```yaml
version_alignment:
  strategy: "strict"
  core_version: "1.2.3"

  platforms:
    macos:
      version: "1.2.3"
      status: "released"

    windows:
      version: "1.2.3"
      status: "released"

    linux:
      version: "1.2.3"
      status: "released"
```

**Use When**:
- Platforms share significant code
- Breaking changes affect all platforms
- Need to guarantee API compatibility

**Release Process**:
1. All platforms must pass tests
2. All platforms tagged with same version
3. All platforms released simultaneously

---

## Strategy 2: Relaxed Alignment

Major.minor must match, patch can differ:

```yaml
version_alignment:
  strategy: "relaxed"
  core_version: "1.2.0"

  platforms:
    macos:
      version: "1.2.1"
      status: "released"
      notes: "Hotfix for Metal GPU crash"

    windows:
      version: "1.2.0"
      status: "released"

    linux:
      version: "1.2.2"
      status: "released"
      notes: "Hotfix for inotify memory leak"
```

**Use When**:
- Platforms have platform-specific bugs
- Hotfixes needed for individual platforms
- API remains compatible across patches

**Constraints**:
- API breaking changes require major/minor bump
- All platforms must bump major/minor together
- Patch versions can be independent

---

## Strategy 3: Independent Versioning

Platforms can have completely different versions:

```yaml
version_alignment:
  strategy: "independent"
  core_version: "2.0.0"

  platforms:
    macos:
      version: "3.1.4"
      status: "released"
      maturity: "stable"

    windows:
      version: "2.8.0"
      status: "released"
      maturity: "stable"

    linux:
      version: "1.5.2"
      status: "beta"
      maturity: "beta"
```

**Use When**:
- Platforms are developed independently
- Different maturity levels across platforms
- Minimal shared code

**Constraints**:
- Must maintain compatibility matrix
- Clear documentation of platform differences
- Extra testing burden

---

## Version Coordination File

**File**: `VERSION_MATRIX.yaml`

```yaml
# Current Version Matrix
matrix_version: "2024.1"  # Matrix version for tracking

core:
  version: "1.2.0"
  release_date: "2024-01-15"

platforms:
  macos:
    version: "1.2.0"
    release_date: "2024-01-15"
    minimum_os: "10.15"
    architectures: ["x64", "arm64"]
    status: "stable"

  windows:
    version: "1.2.0"
    release_date: "2024-01-15"
    minimum_os: "10.0.19041"
    architectures: ["x64", "arm64"]
    status: "stable"

  linux:
    version: "1.2.0"
    release_date: "2024-01-15"
    minimum_kernel: "5.4"
    architectures: ["x64", "arm64", "armv7"]
    distributions: ["ubuntu", "debian", "fedora", "arch"]
    status: "stable"

compatibility:
  # Can macos 1.2.0 communicate with windows 1.1.0?
  - platform_a: "macos:1.2.0"
    platform_b: "windows:1.1.0"
    compatible: true
    notes: "Protocol v2 is backward compatible"

  - platform_a: "macos:1.2.0"
    platform_b: "linux:1.0.0"
    compatible: false
    notes: "Protocol v2 breaks compatibility with v1"
```

---

## Related Documentation

- [CROSS_PLATFORM_SYNC.md](./CROSS_PLATFORM_SYNC.md) - Main index
- [CROSS_PLATFORM_SYNC-part1-shared-code.md](./CROSS_PLATFORM_SYNC-part1-shared-code.md) - Shared code sync
- [CROSS_PLATFORM_SYNC-part3-feature-parity.md](./CROSS_PLATFORM_SYNC-part3-feature-parity.md) - Feature parity
