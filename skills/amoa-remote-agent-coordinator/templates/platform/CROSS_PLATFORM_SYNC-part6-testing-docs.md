# Cross-Platform Synchronization: Testing and Documentation

This document covers testing synchronization and documentation management.

**Parent document**: [CROSS_PLATFORM_SYNC.md](./CROSS_PLATFORM_SYNC.md)

---

## Contents

1. [Shared Test Utilities](#shared-test-utilities)
2. [Platform-Specific Test Verification](#platform-specific-test-verification)
3. [Documentation Structure](#documentation-structure)
4. [Documentation Review Checklist](#documentation-review-checklist)
5. [Troubleshooting](#troubleshooting)

---

## Shared Test Utilities

```rust
// shared/test_utils/mod.rs
//! Test utilities shared across all platforms

use std::path::PathBuf;
use tempfile::TempDir;

pub struct TestFixture {
    pub temp_dir: TempDir,
}

impl TestFixture {
    pub fn new() -> Self {
        Self {
            temp_dir: TempDir::new().unwrap(),
        }
    }

    pub fn create_file(&self, name: &str, contents: &str) -> PathBuf {
        let path = self.temp_dir.path().join(name);
        std::fs::write(&path, contents).unwrap();
        path
    }
}
```

---

## Platform-Specific Test Verification

```bash
#!/bin/bash
# scripts/test-all-platforms.sh

set -e

echo "🧪 Running tests on all platforms..."

# Test macOS
echo ""
echo "Testing macOS..."
cd platform-macos
cargo test --all-features
cd ..

# Test Windows (if on Windows)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo ""
    echo "Testing Windows..."
    cd platform-windows
    cargo test --all-features
    cd ..
fi

# Test Linux (if on Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo ""
    echo "Testing Linux..."
    cd platform-linux
    cargo test --all-features
    cd ..
fi

echo ""
echo "✅ All platform tests passed"
```

---

## Documentation Structure

```
docs/
├── README.md                      # Main documentation
├── ARCHITECTURE.md                # Architecture overview (shared)
├── API.md                         # API reference (shared)
├── platform-specific/
│   ├── macos.md                   # macOS-specific guide
│   ├── windows.md                 # Windows-specific guide
│   └── linux.md                   # Linux-specific guide
└── migration-guides/
    ├── v1-to-v2.md                # Version migration guides
    └── breaking-changes.md
```

---

## Documentation Review Checklist

```yaml
documentation_review:
  on_feature_add:
    - [ ] Update API.md with new APIs
    - [ ] Update platform-specific docs if behavior differs
    - [ ] Add usage examples
    - [ ] Update feature parity matrix

  on_breaking_change:
    - [ ] Document what's changing
    - [ ] Provide migration guide
    - [ ] Update BREAKING_CHANGES.md
    - [ ] Update VERSION_MATRIX.yaml

  on_release:
    - [ ] Update CHANGELOG.md
    - [ ] Update version numbers in docs
    - [ ] Verify all links work
    - [ ] Regenerate API documentation
```

---

## Troubleshooting

### Sync Failures

**Problem**: Shared code has diverged between platforms
**Solution**: Run `./scripts/sync-shared-code.sh` to re-sync from canonical source

**Problem**: Version mismatch between platforms
**Solution**: Check VERSION_MATRIX.yaml and update platform versions to match

**Problem**: Feature parity test failing
**Solution**: Update feature_parity.yaml or implement missing features

### Build Failures

**Problem**: Build passes on one platform but fails on another
**Solution**: Check platform-specific dependencies and build configuration

**Problem**: Tests pass locally but fail in CI
**Solution**: Verify CI environment matches local environment (OS version, dependencies)

---

## Related Documentation

- [CROSS_PLATFORM_SYNC.md](./CROSS_PLATFORM_SYNC.md) - Main index
- [CROSS_PLATFORM_SYNC-part5-release.md](./CROSS_PLATFORM_SYNC-part5-release.md) - Release coordination
- [PLATFORM_MODULE_BASE.md](./PLATFORM_MODULE_BASE.md) - Base module template
- [MACOS_MODULE.md](./MACOS_MODULE.md) - macOS-specific configuration
- [WINDOWS_MODULE.md](./WINDOWS_MODULE.md) - Windows-specific configuration
- [LINUX_MODULE.md](./LINUX_MODULE.md) - Linux-specific configuration
