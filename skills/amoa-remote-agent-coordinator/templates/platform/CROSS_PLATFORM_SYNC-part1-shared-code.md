# Cross-Platform Synchronization: Shared Code

This document covers shared code synchronization strategies for cross-platform development.

**Parent document**: [CROSS_PLATFORM_SYNC.md](./CROSS_PLATFORM_SYNC.md)

---

## Contents

1. [Code Organization Structure](#code-organization-structure)
2. [Shared Code Linking Strategy](#shared-code-linking-strategy)
3. [Synchronization Rules](#synchronization-rules)
4. [Preventing Divergence](#preventing-divergence)

---

## Code Organization Structure

```
project-root/
├── shared/                        # Shared code (platform-agnostic)
│   ├── core/                      # Core business logic
│   │   ├── mod.rs
│   │   ├── types.rs
│   │   └── utils.rs
│   ├── api/                       # Public API definitions
│   │   ├── mod.rs
│   │   └── traits.rs
│   └── protocols/                 # Network protocols, data formats
│       ├── mod.rs
│       └── messages.rs
│
├── platform-macos/                # macOS-specific module
│   ├── Cargo.toml
│   ├── src/
│   │   ├── lib.rs
│   │   ├── platform/              # macOS implementations
│   │   │   ├── file_watcher.rs
│   │   │   └── system_apis.rs
│   │   └── shared/                # Symlink to ../shared
│   └── tests/
│
├── platform-windows/              # Windows-specific module
│   ├── Cargo.toml
│   ├── src/
│   │   ├── lib.rs
│   │   ├── platform/              # Windows implementations
│   │   │   ├── file_watcher.rs
│   │   │   └── system_apis.rs
│   │   └── shared/                # Symlink to ../shared
│   └── tests/
│
└── platform-linux/                # Linux-specific module
    ├── Cargo.toml
    ├── src/
    │   ├── lib.rs
    │   ├── platform/              # Linux implementations
    │   │   ├── file_watcher.rs
    │   │   └── system_apis.rs
    │   └── shared/                # Symlink to ../shared
    └── tests/
```

---

## Shared Code Linking Strategy

### Option 1: Symbolic Links (Recommended)

Create symlinks from platform modules to shared code:

```bash
#!/bin/bash
# Setup script for shared code symlinks

SHARED_DIR="$(pwd)/shared"

# Create symlinks for each platform
for platform in platform-macos platform-windows platform-linux; do
    ln -sf "$SHARED_DIR" "$platform/src/shared"
    echo "✅ Created symlink: $platform/src/shared -> $SHARED_DIR"
done
```

**Advantages**:
- Single source of truth for shared code
- Changes automatically visible to all platforms
- No manual synchronization needed
- Git tracks symlinks correctly

**Disadvantages**:
- Requires symlink support (issues on Windows without Developer Mode)
- Can be confusing for developers unfamiliar with symlinks

### Option 2: Git Subtree

Use git subtree to share code between repositories:

```bash
# Add shared code as subtree
git subtree add --prefix=platform-macos/src/shared shared main --squash

# Pull updates
git subtree pull --prefix=platform-macos/src/shared shared main --squash

# Push changes back to shared
git subtree push --prefix=platform-macos/src/shared shared main
```

**Advantages**:
- No symlink issues
- Full git history available
- Works on all platforms

**Disadvantages**:
- Manual synchronization required
- More complex git operations
- Potential for divergence

### Option 3: Cargo Workspace

Use Cargo workspace with path dependencies:

```toml
# Root Cargo.toml
[workspace]
members = [
    "shared",
    "platform-macos",
    "platform-windows",
    "platform-linux",
]

# Platform module Cargo.toml
[dependencies]
shared = { path = "../shared" }
```

**Advantages**:
- Native Cargo support
- Unified build system
- Easy dependency management

**Disadvantages**:
- All platforms must be in same repository
- Can't split platforms into separate repos

---

## Synchronization Rules

```yaml
sync:
  shared_code:
    # Core Business Logic
    - path: "shared/core"
      sync_to:
        - "platform-macos/src/shared/core"
        - "platform-windows/src/shared/core"
        - "platform-linux/src/shared/core"
      bidirectional: false  # Only shared -> platforms
      auto_sync: true
      review_required: true

    # Public API Definitions
    - path: "shared/api"
      sync_to:
        - "platform-macos/src/shared/api"
        - "platform-windows/src/shared/api"
        - "platform-linux/src/shared/api"
      bidirectional: false
      auto_sync: true
      review_required: true

    # Test Utilities
    - path: "shared/test_utils"
      sync_to:
        - "platform-macos/tests/shared"
        - "platform-windows/tests/shared"
        - "platform-linux/tests/shared"
      bidirectional: false
      auto_sync: true
      review_required: false
```

---

## Preventing Divergence

### Pre-commit Hook

Check shared code consistency before committing:

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Checking shared code synchronization..."

# Check if shared code has diverged
for platform in platform-macos platform-windows platform-linux; do
    if [ -L "$platform/src/shared" ]; then
        # It's a symlink, no divergence possible
        continue
    fi

    # Compare actual files
    if ! diff -r shared/ "$platform/src/shared/" > /dev/null 2>&1; then
        echo "❌ ERROR: Shared code diverged in $platform"
        echo "Run: ./scripts/sync-shared-code.sh"
        exit 1
    fi
done

echo "✅ Shared code is synchronized"
```

### CI Check for Synchronization

```yaml
# .github/workflows/check-sync.yml
name: Check Shared Code Sync

on: [push, pull_request]

jobs:
  check-sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check Shared Code Synchronization
        run: |
          ./scripts/check-shared-code-sync.sh
```

---

## Related Documentation

- [CROSS_PLATFORM_SYNC.md](./CROSS_PLATFORM_SYNC.md) - Main index
- [CROSS_PLATFORM_SYNC-part2-version-alignment.md](./CROSS_PLATFORM_SYNC-part2-version-alignment.md) - Version strategies
- [PLATFORM_MODULE_BASE.md](./PLATFORM_MODULE_BASE.md) - Base module template
