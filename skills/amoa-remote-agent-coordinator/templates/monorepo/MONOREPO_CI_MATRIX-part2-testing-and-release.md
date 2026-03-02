# Monorepo CI/CD Matrix - Part 2: Testing, Release, and Verification

This part covers selective testing, cross-language integration tests, artifact collection, release workflows, and verification checklists.

**Parent document**: [MONOREPO_CI_MATRIX.md](MONOREPO_CI_MATRIX.md)

---

## Table of Contents

- Selective Testing Based on Changed Packages
- Cross-Language Integration Tests
- Artifact Collection and Release
  - Collect Artifacts from All Workspaces
  - Create GitHub Release
  - Publish to npm
  - Publish to PyPI
- Reusable Workflow Template
- Verification Checklist
- Error Recovery

---

## Selective Testing Based on Changed Packages

```yaml
# .github/workflows/ci-selective.yml
name: CI - Selective

on:
  pull_request:
    paths:
      - '{{RUST_WORKSPACE}}/packages/**'

jobs:
  detect-package-changes:
    runs-on: ubuntu-latest
    outputs:
      core_changed: ${{ steps.filter.outputs.core }}
      utils_changed: ${{ steps.filter.outputs.utils }}
      cli_changed: ${{ steps.filter.outputs.cli }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            core:
              - '{{RUST_WORKSPACE}}/packages/core/**'
            utils:
              - '{{RUST_WORKSPACE}}/packages/utils/**'
            cli:
              - '{{RUST_WORKSPACE}}/packages/cli/**'

  test-core:
    needs: detect-package-changes
    if: needs.detect-package-changes.outputs.core_changed == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - run: cargo test -p core
        working-directory: {{RUST_WORKSPACE}}

  test-utils:
    needs: detect-package-changes
    if: needs.detect-package-changes.outputs.utils_changed == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - run: cargo test -p utils
        working-directory: {{RUST_WORKSPACE}}

  test-cli:
    needs: detect-package-changes
    if: needs.detect-package-changes.outputs.cli_changed == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - run: cargo test -p cli
        working-directory: {{RUST_WORKSPACE}}
```

---

## Cross-Language Integration Tests

```yaml
# .github/workflows/ci-integration.yml
name: CI - Integration

on:
  pull_request:
    paths:
      - '{{RUST_WORKSPACE}}/packages/core/**'
      - '{{PYTHON_WORKSPACE}}/packages/bindings/**'
      - '{{JS_WORKSPACE}}/packages/wasm/**'

jobs:
  integration-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Build Rust core
      - name: Setup Rust
        uses: dtolnay/rust-toolchain@stable

      - name: Build Rust core
        run: cargo build --release -p core
        working-directory: {{RUST_WORKSPACE}}

      # Build Python bindings
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Build Python bindings
        run: |
          uv sync
          uv run maturin develop --release
        working-directory: {{PYTHON_WORKSPACE}}/packages/bindings

      # Test Python can import Rust
      - name: Test Python bindings
        run: uv run python -c "import xls_bindings; print(xls_bindings.process_xls('test.xls'))"
        working-directory: {{PYTHON_WORKSPACE}}

      # Build WASM
      - name: Install wasm-pack
        run: curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh

      - name: Build WASM
        run: wasm-pack build --target web
        working-directory: {{RUST_WORKSPACE}}/packages/wasm-bindings

      # Test JS can use WASM
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '22'

      - name: Setup pnpm
        uses: pnpm/action-setup@v4

      - name: Test WASM in JS
        run: |
          pnpm install
          pnpm run test:integration
        working-directory: {{JS_WORKSPACE}}
```

---

## Artifact Collection and Release

### Collect Artifacts from All Workspaces

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-rust:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - name: Build release
        run: cargo build --release --workspace
        working-directory: {{RUST_WORKSPACE}}
      - name: Upload binaries
        uses: actions/upload-artifact@v4
        with:
          name: rust-${{ matrix.os }}-${{ github.ref_name }}
          path: |
            {{RUST_WORKSPACE}}/target/release/xls-cli*
            !{{RUST_WORKSPACE}}/target/release/*.d

  build-js:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - name: Build packages
        run: |
          pnpm install
          pnpm run build
        working-directory: {{JS_WORKSPACE}}
      - name: Upload packages
        uses: actions/upload-artifact@v4
        with:
          name: js-packages-${{ github.ref_name }}
          path: {{JS_WORKSPACE}}/packages/*/dist

  build-python:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Build wheels
        run: |
          uv sync
          uv run maturin build --release
        working-directory: {{PYTHON_WORKSPACE}}/packages/bindings
      - name: Upload wheels
        uses: actions/upload-artifact@v4
        with:
          name: python-${{ matrix.os }}-${{ github.ref_name }}
          path: {{PYTHON_WORKSPACE}}/target/wheels/*.whl

  create-release:
    needs: [build-rust, build-js, build-python]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Download all artifacts
        uses: actions/download-artifact@v4
        with:
          path: artifacts/

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          files: artifacts/**/*
          draft: false
          prerelease: false
          generate_release_notes: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  publish-npm:
    needs: build-js
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          registry-url: 'https://registry.npmjs.org'
      - name: Publish to npm
        run: |
          pnpm install
          pnpm -r publish --access public --no-git-checks
        working-directory: {{JS_WORKSPACE}}
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}

  publish-pypi:
    needs: build-python
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    steps:
      - name: Download wheels
        uses: actions/download-artifact@v4
        with:
          pattern: python-*
          path: wheels/
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          packages-dir: wheels/
          password: ${{ secrets.PYPI_API_TOKEN }}
```

---

## Reusable Workflow Template

```yaml
# .github/workflows/_reusable-setup.yml
name: Reusable Setup

on:
  workflow_call:
    inputs:
      language:
        required: true
        type: string
      workspace:
        required: true
        type: string

jobs:
  setup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Rust
        if: inputs.language == 'rust'
        uses: dtolnay/rust-toolchain@stable

      - name: Setup Node
        if: inputs.language == 'javascript'
        uses: actions/setup-node@v4
        with:
          node-version: '22'

      - name: Setup Python
        if: inputs.language == 'python'
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: |
            ~/.cargo
            ~/.cache/pip
            node_modules
          key: ${{ inputs.language }}-${{ hashFiles(format('{0}/**/Cargo.lock', inputs.workspace), format('{0}/**/pnpm-lock.yaml', inputs.workspace)) }}
```

---

## Verification Checklist

```markdown
## CI/CD Verification

### Change Detection
- [ ] Filters configured for each workspace
- [ ] Package-level filters for selective testing
- [ ] Shared config changes trigger all workflows

### Matrix Builds
- [ ] Each language has matrix workflow
- [ ] Multiple OS tested: Linux, macOS, Windows
- [ ] Multiple versions tested: stable, latest

### Selective Testing
- [ ] Only changed packages tested
- [ ] Dependent packages re-tested
- [ ] Integration tests run when needed

### Artifacts
- [ ] Binaries collected per OS
- [ ] npm packages collected
- [ ] Python wheels collected per OS
- [ ] Artifacts uploaded to release

### Publishing
- [ ] npm publish on tag push
- [ ] PyPI publish on tag push
- [ ] GitHub Release created with artifacts
```

---

## Error Recovery

| Error | Cause | Fix |
|-------|-------|-----|
| No jobs run | Filters too restrictive | Check `paths` patterns |
| Matrix fails on Windows | Path separators | Use forward slashes |
| Cache miss | Wrong cache key | Use lockfile hash |
| Artifact upload fails | Path doesn't exist | Check build output path |
| Publish fails | Missing token | Add `NPM_TOKEN` or `PYPI_API_TOKEN` secret |

---

## Related Documents

- **Parent**: [MONOREPO_CI_MATRIX.md](MONOREPO_CI_MATRIX.md) - Template overview and variables
- **Part 1**: [MONOREPO_CI_MATRIX-part1-detection-and-matrix.md](MONOREPO_CI_MATRIX-part1-detection-and-matrix.md) - Change detection and matrix builds
