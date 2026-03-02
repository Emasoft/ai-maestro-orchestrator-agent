# Cross-Platform Synchronization: Release Coordination

This document covers release coordination and breaking change management.

**Parent document**: [CROSS_PLATFORM_SYNC.md](./CROSS_PLATFORM_SYNC.md)

---

## Contents

1. [Coordinated Release Process](#coordinated-release-process)
2. [Automated Release Script](#automated-release-script)
3. [Breaking Change Policy](#breaking-change-policy)
4. [Breaking Change Process](#breaking-change-process)
5. [Breaking Change Example](#breaking-change-example)

---

## Coordinated Release Process

For **strict version alignment**:

```yaml
# RELEASE_CHECKLIST.md

## Pre-Release
- [ ] All platform modules pass CI tests
- [ ] Feature parity matrix reviewed and updated
- [ ] VERSION_MATRIX.yaml updated with new version
- [ ] CHANGELOG.md updated for all platforms
- [ ] Documentation updated

## Version Bump
- [ ] Bump shared/Cargo.toml version to {{NEW_VERSION}}
- [ ] Bump platform-macos/Cargo.toml to {{NEW_VERSION}}
- [ ] Bump platform-windows/Cargo.toml to {{NEW_VERSION}}
- [ ] Bump platform-linux/Cargo.toml to {{NEW_VERSION}}
- [ ] Commit with message: "Release v{{NEW_VERSION}}"

## Build & Test
- [ ] Build all platforms: ./scripts/build-all-platforms.sh
- [ ] Run all tests: ./scripts/test-all-platforms.sh
- [ ] Manual testing on each platform

## Tag & Release
- [ ] Create git tag: git tag -a v{{NEW_VERSION}} -m "Release v{{NEW_VERSION}}"
- [ ] Push tag: git push origin v{{NEW_VERSION}}
- [ ] CI automatically builds and creates GitHub Release
- [ ] Verify all platform artifacts are attached

## Post-Release
- [ ] Update latest release links in README
- [ ] Announce release on communication channels
- [ ] Monitor for issues in first 24 hours
```

---

## Automated Release Script

```bash
#!/bin/bash
# scripts/release.sh

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <new-version>"
    echo "Example: $0 1.3.0"
    exit 1
fi

NEW_VERSION="$1"

echo "🚀 Starting coordinated release for v$NEW_VERSION"

# Verify all tests pass
echo "Running tests on all platforms..."
./scripts/test-all-platforms.sh

# Update version in all Cargo.toml files
echo "Updating version numbers..."
for manifest in shared/Cargo.toml platform-*/Cargo.toml; do
    sed -i "s/^version = .*/version = \"$NEW_VERSION\"/" "$manifest"
    echo "  ✅ Updated $manifest"
done

# Update VERSION_MATRIX.yaml
echo "Updating VERSION_MATRIX.yaml..."
sed -i "s/core_version: .*/core_version: \"$NEW_VERSION\"/" VERSION_MATRIX.yaml
sed -i "s/version: .*/version: \"$NEW_VERSION\"/" VERSION_MATRIX.yaml

# Commit changes
git add -A
git commit -m "Release v$NEW_VERSION"

# Create tag
git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"

echo "✅ Release v$NEW_VERSION prepared"
echo ""
echo "Review the changes, then run:"
echo "  git push origin main"
echo "  git push origin v$NEW_VERSION"
```

---

## Breaking Change Policy

```yaml
breaking_changes:
  policy: "coordinated"  # all platforms must update together

  announcement:
    advance_notice_days: 30
    channels:
      - "GitHub Discussions"
      - "Release Notes"
      - "Documentation"

  migration_support:
    deprecation_period_days: 90
    compatibility_shim: true  # Provide compatibility layer during migration
```

---

## Breaking Change Process

1. **Announcement Phase** (Day 0):
   - Create GitHub Discussion announcing breaking change
   - Document what's changing and why
   - Provide migration guide
   - Update feature parity matrix with deprecation status

2. **Deprecation Phase** (Days 1-90):
   - Mark old API as `#[deprecated]` with migration instructions
   - Implement new API alongside old API
   - Provide compatibility shim if possible
   - Update tests to use new API

3. **Migration Phase** (Days 30-90):
   - Help users migrate via GitHub Issues
   - Collect feedback on new API
   - Make adjustments based on feedback

4. **Removal Phase** (Day 90):
   - Remove deprecated API
   - Bump major version (e.g., 1.x.x → 2.0.0)
   - Coordinate release across all platforms
   - Update documentation to remove old API references

---

## Breaking Change Example

**File**: `BREAKING_CHANGES.md`

```markdown
# Breaking Changes in v2.0.0

## File Watcher API Redesign

**Announced**: 2024-01-15
**Deprecated**: v1.8.0 (2024-01-15)
**Removed**: v2.0.0 (2024-04-15)

### What's Changing

The `FileWatcher::new()` constructor now requires an explicit event mask parameter.

### Before (Deprecated)

```rust
let watcher = FileWatcher::new("/path/to/watch")?;
```

### After (v2.0.0+)

```rust
use file_watcher::EventMask;

let watcher = FileWatcher::new(
    "/path/to/watch",
    EventMask::CREATE | EventMask::MODIFY | EventMask::DELETE
)?;
```

### Migration Guide

1. Update your code to use the new constructor
2. Specify which events you want to watch
3. Run tests to ensure everything works

### Platforms Affected

- ✅ macOS: v2.0.0
- ✅ Windows: v2.0.0
- ✅ Linux: v2.0.0

All platforms updated simultaneously.
```

---

## Related Documentation

- [CROSS_PLATFORM_SYNC.md](./CROSS_PLATFORM_SYNC.md) - Main index
- [CROSS_PLATFORM_SYNC-part4-cicd.md](./CROSS_PLATFORM_SYNC-part4-cicd.md) - CI/CD configuration
- [CROSS_PLATFORM_SYNC-part6-testing-docs.md](./CROSS_PLATFORM_SYNC-part6-testing-docs.md) - Testing and documentation
