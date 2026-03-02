# Monorepo CI/CD Matrix Template

This template defines CI/CD workflows for monorepo projects with change detection, selective testing, matrix builds, and artifact collection.

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{MONOREPO_NAME}}` | Monorepo project name | `xls-platform` |
| `{{LANGUAGES}}` | Languages in monorepo | `["rust", "javascript", "python"]` |
| `{{RUST_WORKSPACE}}` | Rust workspace path | `rust-workspace/` |
| `{{JS_WORKSPACE}}` | JS workspace path | `js-workspace/` |
| `{{PYTHON_WORKSPACE}}` | Python workspace path | `python-workspace/` |
| `{{MATRIX_OS}}` | Target operating systems | `["ubuntu-latest", "macos-latest", "windows-latest"]` |
| `{{MATRIX_RUST_VERSION}}` | Rust versions to test | `["1.75", "stable"]` |
| `{{MATRIX_NODE_VERSION}}` | Node versions to test | `["20", "22"]` |
| `{{MATRIX_PYTHON_VERSION}}` | Python versions to test | `["3.12", "3.13"]` |
| `{{TASK_ID}}` | Associated task ID | `GH-42` |

---

## CI Workflow Structure

```
.github/workflows/
├── ci-root.yml              # Root-level checks (format, lint)
├── ci-rust.yml              # Rust workspace matrix
├── ci-javascript.yml        # JS workspace matrix
├── ci-python.yml            # Python workspace matrix
├── ci-integration.yml       # Cross-language integration tests
├── release.yml              # Multi-workspace release
└── _reusable-setup.yml      # Shared setup actions (DRY)
```

---

## Table of Contents

This template is split into multiple parts for easier consumption:

### Part 1: Change Detection and Matrix Builds

**File**: [MONOREPO_CI_MATRIX-part1-detection-and-matrix.md](MONOREPO_CI_MATRIX-part1-detection-and-matrix.md)

- **Change Detection with dorny/paths-filter**
  - Basic Change Detection - Setting up workspace-level filters
  - Package-Level Change Detection - Granular filtering per package
- **Matrix Builds per Language**
  - Rust Workspace Matrix - Multi-OS, multi-version Rust builds
  - JavaScript Workspace Matrix - Node.js matrix with pnpm
  - Python Workspace Matrix - Python matrix with uv and ruff

### Part 2: Testing, Release, and Verification

**File**: [MONOREPO_CI_MATRIX-part2-testing-and-release.md](MONOREPO_CI_MATRIX-part2-testing-and-release.md)

- **Selective Testing Based on Changed Packages** - Run only relevant tests
- **Cross-Language Integration Tests** - Test Rust-Python-JS interop
- **Artifact Collection and Release**
  - Collect Artifacts from All Workspaces
  - Create GitHub Release
  - Publish to npm
  - Publish to PyPI
- **Reusable Workflow Template** - DRY workflow setup
- **Verification Checklist** - CI/CD validation steps
- **Error Recovery** - Common issues and fixes
- **Template Metadata** - Version and dependencies

---

## Quick Start

1. **Set up change detection** (Part 1): Configure `dorny/paths-filter` to detect which workspaces changed
2. **Configure matrix builds** (Part 1): Set up per-language CI workflows with OS and version matrices
3. **Enable selective testing** (Part 2): Only test packages that actually changed
4. **Add integration tests** (Part 2): Test cross-language interop when relevant files change
5. **Configure release workflow** (Part 2): Collect artifacts and publish to registries

---

## Template Metadata

```yaml
template:
  name: MONOREPO_CI_MATRIX
  version: 1.0.0
  eoa_compatible: true
  parent_template: MONOREPO_BASE
  requires:
    - MONOREPO_BASE
    - GitHub Actions
  generates:
    - change detection workflows
    - matrix build workflows
    - integration test workflows
    - release workflows
  dependencies:
    - dorny/paths-filter@v3
    - actions/upload-artifact@v4
    - actions/download-artifact@v4
```
