# Monorepo CI/CD Matrix - Part 1: Change Detection and Matrix Builds

This part covers setting up change detection with dorny/paths-filter and configuring matrix builds for Rust, JavaScript, and Python workspaces.

**Parent document**: [MONOREPO_CI_MATRIX.md](MONOREPO_CI_MATRIX.md)

---

## Table of Contents

- Change Detection with dorny/paths-filter
  - Basic Change Detection - Setting up workspace-level filters
  - Package-Level Change Detection - Granular filtering per package
- Matrix Builds per Language
  - Rust Workspace Matrix - Multi-OS, multi-version Rust builds
  - JavaScript Workspace Matrix - Node.js matrix with pnpm
  - Python Workspace Matrix - Python matrix with uv and ruff

---

## Change Detection with dorny/paths-filter

### Basic Change Detection

```yaml
# .github/workflows/ci-root.yml
name: CI - Root

on:
  pull_request:
    paths:
      - '**'
  push:
    branches: [main, develop]

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      rust_changed: ${{ steps.filter.outputs.rust }}
      js_changed: ${{ steps.filter.outputs.js }}
      python_changed: ${{ steps.filter.outputs.python }}
      shared_config_changed: ${{ steps.filter.outputs.shared_config }}
    steps:
      - uses: actions/checkout@v4

      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            rust:
              - '{{RUST_WORKSPACE}}/**'
            js:
              - '{{JS_WORKSPACE}}/**'
            python:
              - '{{PYTHON_WORKSPACE}}/**'
            shared_config:
              - '.config/**'
              - 'scripts/**'
              - '.github/workflows/**'

      - name: Summary
        run: |
          echo "Rust changed: ${{ steps.filter.outputs.rust }}"
          echo "JS changed: ${{ steps.filter.outputs.js }}"
          echo "Python changed: ${{ steps.filter.outputs.python }}"
```

### Package-Level Change Detection

```yaml
# Detect changes per package for selective testing
- uses: dorny/paths-filter@v3
  id: filter-packages
  with:
    filters: |
      rust_core:
        - '{{RUST_WORKSPACE}}/packages/core/**'
      rust_utils:
        - '{{RUST_WORKSPACE}}/packages/utils/**'
      js_ui:
        - '{{JS_WORKSPACE}}/packages/ui/**'
      js_api:
        - '{{JS_WORKSPACE}}/packages/api-client/**'
      python_bindings:
        - '{{PYTHON_WORKSPACE}}/packages/bindings/**'
```

---

## Matrix Builds per Language

### Rust Workspace Matrix

```yaml
# .github/workflows/ci-rust.yml
name: CI - Rust

on:
  pull_request:
    paths:
      - '{{RUST_WORKSPACE}}/**'
      - '.github/workflows/ci-rust.yml'

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      rust_changed: ${{ steps.filter.outputs.rust }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            rust:
              - '{{RUST_WORKSPACE}}/**'

  test-rust:
    needs: detect-changes
    if: needs.detect-changes.outputs.rust_changed == 'true'
    strategy:
      fail-fast: false
      matrix:
        os: {{MATRIX_OS}}
        rust: {{MATRIX_RUST_VERSION}}
    runs-on: ${{ matrix.os }}
    defaults:
      run:
        working-directory: {{RUST_WORKSPACE}}
    steps:
      - uses: actions/checkout@v4

      - name: Setup Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: ${{ matrix.rust }}
          components: rustfmt, clippy

      - name: Cache Cargo
        uses: Swatinem/rust-cache@v2
        with:
          workspaces: {{RUST_WORKSPACE}}

      - name: Format check
        run: cargo fmt --check

      - name: Clippy
        run: cargo clippy --workspace --all-targets -- -D warnings

      - name: Build
        run: cargo build --workspace --all-targets

      - name: Test
        run: cargo test --workspace

      - name: Upload artifacts
        if: matrix.os == 'ubuntu-latest' && matrix.rust == 'stable'
        uses: actions/upload-artifact@v4
        with:
          name: rust-binaries-${{ github.sha }}
          path: |
            {{RUST_WORKSPACE}}/target/release/*
            !{{RUST_WORKSPACE}}/target/release/*.d
            !{{RUST_WORKSPACE}}/target/release/deps
          retention-days: 7
```

### JavaScript Workspace Matrix

```yaml
# .github/workflows/ci-javascript.yml
name: CI - JavaScript

on:
  pull_request:
    paths:
      - '{{JS_WORKSPACE}}/**'
      - '.github/workflows/ci-javascript.yml'

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      js_changed: ${{ steps.filter.outputs.js }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            js:
              - '{{JS_WORKSPACE}}/**'

  test-javascript:
    needs: detect-changes
    if: needs.detect-changes.outputs.js_changed == 'true'
    strategy:
      fail-fast: false
      matrix:
        os: {{MATRIX_OS}}
        node: {{MATRIX_NODE_VERSION}}
    runs-on: ${{ matrix.os }}
    defaults:
      run:
        working-directory: {{JS_WORKSPACE}}
    steps:
      - uses: actions/checkout@v4

      - name: Setup pnpm
        uses: pnpm/action-setup@v4
        with:
          version: 9

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: 'pnpm'
          cache-dependency-path: '{{JS_WORKSPACE}}/pnpm-lock.yaml'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Lint
        run: pnpm run lint

      - name: Type check
        run: pnpm run typecheck

      - name: Build
        run: pnpm run build

      - name: Test
        run: pnpm run test

      - name: Upload artifacts
        if: matrix.os == 'ubuntu-latest' && matrix.node == '22'
        uses: actions/upload-artifact@v4
        with:
          name: js-dist-${{ github.sha }}
          path: {{JS_WORKSPACE}}/packages/*/dist
          retention-days: 7
```

### Python Workspace Matrix

```yaml
# .github/workflows/ci-python.yml
name: CI - Python

on:
  pull_request:
    paths:
      - '{{PYTHON_WORKSPACE}}/**'
      - '.github/workflows/ci-python.yml'

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      python_changed: ${{ steps.filter.outputs.python }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            python:
              - '{{PYTHON_WORKSPACE}}/**'

  test-python:
    needs: detect-changes
    if: needs.detect-changes.outputs.python_changed == 'true'
    strategy:
      fail-fast: false
      matrix:
        os: {{MATRIX_OS}}
        python: {{MATRIX_PYTHON_VERSION}}
    runs-on: ${{ matrix.os }}
    defaults:
      run:
        working-directory: {{PYTHON_WORKSPACE}}
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install dependencies
        run: uv sync

      - name: Format check
        run: uv run ruff format --check .

      - name: Lint
        run: uv run ruff check .

      - name: Type check
        run: uv run mypy .

      - name: Test
        run: uv run pytest --cov=. --cov-report=xml

      - name: Upload coverage
        if: matrix.os == 'ubuntu-latest' && matrix.python == '3.12'
        uses: codecov/codecov-action@v4
        with:
          file: {{PYTHON_WORKSPACE}}/coverage.xml
          flags: python
```

---

## Next Steps

Continue to [Part 2: Testing, Release, and Verification](MONOREPO_CI_MATRIX-part2-testing-and-release.md) for:
- Selective testing based on changed packages
- Cross-language integration tests
- Artifact collection and release workflows
- Reusable workflow templates
- Verification checklist
