# Monorepo Toolchain Composition - Part 2: Verification Scripts

This part covers the root-level scripts for setting up, verifying, and building all toolchains.

---

## Root-Level Verification Commands

### Setup All Toolchains

```bash
#!/bin/bash
# scripts/setup-all.sh - Install all language toolchains

set -e

log_info() { echo -e "\033[0;32m[INFO]\033[0m $*"; }

log_info "Setting up {{MONOREPO_NAME}} multi-language monorepo..."

# Setup Rust
if [ -d "{{RUST_WORKSPACE}}" ]; then
  log_info "Setting up Rust workspace..."
  cd {{RUST_WORKSPACE}}
  cargo fetch --workspace
  cd ..
fi

# Setup JavaScript/TypeScript
if [ -d "{{JS_WORKSPACE}}" ]; then
  log_info "Setting up JavaScript workspace..."
  cd {{JS_WORKSPACE}}
  pnpm install
  cd ..
fi

# Setup Python
if [ -d "{{PYTHON_WORKSPACE}}" ]; then
  log_info "Setting up Python workspace..."
  cd {{PYTHON_WORKSPACE}}
  uv sync
  cd ..
fi

log_info "All toolchains setup complete!"
```

### Verify All Toolchains

```bash
#!/bin/bash
# scripts/verify-all.sh - Run all verification checks

set -e

log_info() { echo -e "\033[0;32m[INFO]\033[0m $*"; }
log_error() { echo -e "\033[0;31m[ERROR]\033[0m $*"; }

FAILED=0

# Verify Rust
if [ -d "{{RUST_WORKSPACE}}" ]; then
  log_info "Verifying Rust workspace..."
  cd {{RUST_WORKSPACE}}

  log_info "  - Format check..."
  cargo fmt --check || FAILED=1

  log_info "  - Clippy..."
  cargo clippy --workspace --all-targets -- -D warnings || FAILED=1

  log_info "  - Tests..."
  cargo test --workspace || FAILED=1

  cd ..
fi

# Verify JavaScript/TypeScript
if [ -d "{{JS_WORKSPACE}}" ]; then
  log_info "Verifying JavaScript workspace..."
  cd {{JS_WORKSPACE}}

  log_info "  - Lint..."
  pnpm run lint || FAILED=1

  log_info "  - Type check..."
  pnpm run typecheck || FAILED=1

  log_info "  - Tests..."
  pnpm run test || FAILED=1

  cd ..
fi

# Verify Python
if [ -d "{{PYTHON_WORKSPACE}}" ]; then
  log_info "Verifying Python workspace..."
  cd {{PYTHON_WORKSPACE}}

  log_info "  - Format check..."
  uv run ruff format --check . || FAILED=1

  log_info "  - Lint..."
  uv run ruff check . || FAILED=1

  log_info "  - Type check..."
  uv run mypy . || FAILED=1

  log_info "  - Tests..."
  uv run pytest || FAILED=1

  cd ..
fi

if [ $FAILED -eq 0 ]; then
  log_info "All verifications passed!"
  exit 0
else
  log_error "Some verifications failed!"
  exit 1
fi
```

### Build All Workspaces

```bash
#!/bin/bash
# scripts/build-all.sh - Build all workspaces in dependency order

set -e

log_info() { echo -e "\033[0;32m[INFO]\033[0m $*"; }

# Build order matters if there are cross-language dependencies
# Example: Rust core → Python bindings → JS API client

# 1. Build Rust (generates native libraries)
if [ -d "{{RUST_WORKSPACE}}" ]; then
  log_info "Building Rust workspace..."
  cd {{RUST_WORKSPACE}}
  cargo build --workspace --release
  cd ..
fi

# 2. Build Python (may depend on Rust .so files)
if [ -d "{{PYTHON_WORKSPACE}}" ]; then
  log_info "Building Python workspace..."
  cd {{PYTHON_WORKSPACE}}
  uv run python -m build
  cd ..
fi

# 3. Build JavaScript (may depend on WASM from Rust)
if [ -d "{{JS_WORKSPACE}}" ]; then
  log_info "Building JavaScript workspace..."
  cd {{JS_WORKSPACE}}
  pnpm run build
  cd ..
fi

log_info "All builds complete!"
```

---

**Navigation:**
- [Back to Index](./MONOREPO_TOOLCHAIN_COMPOSITION.md)
- [Previous: Part 1 - Workspace Configuration](./MONOREPO_TOOLCHAIN_COMPOSITION-part1-workspace-configuration.md)
- [Next: Part 3 - Integration Patterns](./MONOREPO_TOOLCHAIN_COMPOSITION-part3-integration-patterns.md)
