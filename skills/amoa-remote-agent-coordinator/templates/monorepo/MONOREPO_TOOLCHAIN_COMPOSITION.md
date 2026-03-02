# Monorepo Toolchain Composition Template

This template defines how to combine multiple language toolchains within a single monorepo.
Use this for polyglot projects that require Rust + Python + JavaScript/TypeScript tooling.

---

## Table of Contents

This document is split into multiple parts for easier navigation:

### [Part 1: Workspace Configuration](./MONOREPO_TOOLCHAIN_COMPOSITION-part1-workspace-configuration.md)
- Combined Workspace Configuration
  - Rust Workspace (Cargo.toml)
  - JavaScript Workspace (package.json + pnpm-workspace.yaml)
  - Python Workspace (pyproject.toml with uv)
- Shared Toolchain Configuration
  - Rustfmt configuration
  - ESLint configuration
  - Ruff configuration

### [Part 2: Verification Scripts](./MONOREPO_TOOLCHAIN_COMPOSITION-part2-verification-scripts.md)
- Root-Level Verification Commands
  - Setup All Toolchains (scripts/setup-all.sh)
  - Verify All Toolchains (scripts/verify-all.sh)
  - Build All Workspaces (scripts/build-all.sh)

### [Part 3: Integration Patterns](./MONOREPO_TOOLCHAIN_COMPOSITION-part3-integration-patterns.md)
- Dependency Graph for Build Order
  - Build order example (XLS Platform)
  - Parallel build groups
- Cross-Language Integration Patterns
  - Pattern 1: Rust Core with Python Bindings (PyO3)
  - Pattern 2: Rust Core with WASM for Web (wasm-bindgen)
  - Pattern 3: Shared Configuration Files
- Per-Language vs Shared Tooling

### [Part 4: Best Practices](./MONOREPO_TOOLCHAIN_COMPOSITION-part4-best-practices.md)
- Verification Checklist
- Error Recovery
- Best Practices (DO and DON'T)
- Template Metadata

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{MONOREPO_NAME}}` | Monorepo project name | `xls-platform` |
| `{{PRIMARY_LANGUAGE}}` | Main language | `rust`, `javascript`, `python` |
| `{{SECONDARY_LANGUAGES}}` | Additional languages | `["python", "javascript"]` |
| `{{RUST_WORKSPACE}}` | Rust workspace path | `rust-workspace/` |
| `{{JS_WORKSPACE}}` | JS/TS workspace path | `js-workspace/` |
| `{{PYTHON_WORKSPACE}}` | Python workspace path | `python-workspace/` |
| `{{SHARED_CONFIG_DIR}}` | Shared configs location | `.config/` |
| `{{TASK_ID}}` | Current task ID | `GH-42` |

---

## Multi-Language Monorepo Structure

### Option 1: Language-Separated Workspaces

```
{{MONOREPO_NAME}}/
├── rust-workspace/
│   ├── Cargo.toml             # Rust workspace root
│   ├── packages/
│   │   ├── core/
│   │   └── utils/
│   └── apps/
│       └── cli/
├── js-workspace/
│   ├── package.json           # JS/TS workspace root
│   ├── pnpm-workspace.yaml
│   ├── packages/
│   │   ├── ui/
│   │   └── api-client/
│   └── apps/
│       └── web/
├── python-workspace/
│   ├── pyproject.toml         # Python workspace root (uv)
│   ├── packages/
│   │   └── bindings/
│   └── scripts/
├── {{SHARED_CONFIG_DIR}}/
│   ├── rustfmt.toml
│   ├── eslint.config.js
│   ├── ruff.toml
│   └── tsconfig.base.json
├── scripts/
│   ├── setup-all.sh
│   ├── verify-all.sh
│   ├── build-all.sh
│   └── test-all.sh
├── .github/
│   └── workflows/
│       ├── ci-rust.yml
│       ├── ci-js.yml
│       └── ci-python.yml
└── README.md
```

### Option 2: Mixed Workspace (Small Projects)

```
{{MONOREPO_NAME}}/
├── packages/
│   ├── rust-core/             # Rust package
│   │   ├── Cargo.toml
│   │   └── src/
│   ├── python-bindings/       # Python package
│   │   ├── pyproject.toml
│   │   └── src/
│   └── js-ui/                 # JavaScript package
│       ├── package.json
│       └── src/
├── Cargo.toml                 # Rust workspace root
├── package.json               # JS workspace root
├── pyproject.toml             # Python project root
└── scripts/
    └── verify-all.sh          # Orchestrates all toolchains
```

**Recommendation:** Use Option 1 for large projects (10+ packages per language).
Use Option 2 for small projects (3-5 total packages).

---

## Quick Reference

### Setup Commands

```bash
# Setup all toolchains
./scripts/setup-all.sh

# Verify all workspaces
./scripts/verify-all.sh

# Build all workspaces in dependency order
./scripts/build-all.sh
```

### Key Build Order Rule

When cross-language dependencies exist, build in this order:
1. **Rust Core** (no dependencies)
2. **Python Bindings + WASM Package** (depend on Rust)
3. **Python CLI + JS Web App** (depend on bindings)

---

## Template Metadata

```yaml
template:
  name: MONOREPO_TOOLCHAIN_COMPOSITION
  version: 1.0.0
  eoa_compatible: true
  parent_template: MONOREPO_BASE
  requires:
    - MONOREPO_BASE
    - language-specific toolchains
  generates:
    - multi-language workspace structure
    - unified verification scripts
    - shared configuration
    - build orchestration
  compatible_with:
    - cargo-workspace + pnpm-workspaces
    - cargo-workspace + uv-workspace
    - mixed-language monorepos
```
