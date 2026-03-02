# Monorepo Workspace - Part 2: Configuration and CI

This part covers TypeScript configuration, versioning strategies, and CI triggers for monorepo workspace packages.

**Parent document:** [MONOREPO_WORKSPACE.md](./MONOREPO_WORKSPACE.md)

---

## Table of Contents

- 2.1 TypeScript Configuration
  - 2.1.1 TypeScript References for local dependencies
- 2.2 Scoped Versioning Strategy
  - 2.2.1 Independent Versioning
  - 2.2.2 Fixed Versioning
  - 2.2.3 Version Synchronization
- 2.3 Package-Level CI Triggers
  - 2.3.1 Change Detection (GitHub Actions)

---

## 2.1 TypeScript Configuration

```json
// {{PARENT_WORKSPACE}}/{{PACKAGE_NAME}}/tsconfig.json
{
  "extends": "../../{{SHARED_CONFIG_DIR}}/tsconfig.base.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src",
    "composite": true,
    "declarationMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"],
  "references": [
    {{TSCONFIG_REFERENCES}}
  ]
}
```

### 2.1.1 TypeScript References for local dependencies

```json
"references": [
  { "path": "../core" },
  { "path": "../utils" }
]
```

---

## 2.2 Scoped Versioning Strategy

### 2.2.1 Independent Versioning

Each package has its own version, incremented independently:
```
packages/
├── core/         (v1.2.3)
├── utils/        (v2.0.1)
└── cli/          (v0.5.0)
```

Use when:
- Packages have different release cadences
- Breaking changes don't affect all packages
- Public API stability varies by package

### 2.2.2 Fixed Versioning

All packages share the same version, incremented together:
```
packages/
├── core/         (v1.0.0)
├── utils/        (v1.0.0)
└── cli/          (v1.0.0)
```

Use when:
- Packages are tightly coupled
- Coordinated releases required
- Single product with multiple entry points

### 2.2.3 Version Synchronization

For independent versioning with Cargo workspaces:
```toml
# Root Cargo.toml
[workspace.package]
version = "1.0.0"

# Package Cargo.toml
[package]
version.workspace = true  # Inherit root version
```

---

## 2.3 Package-Level CI Triggers

### 2.3.1 Change Detection (GitHub Actions)

```yaml
# .github/workflows/ci-packages.yml
name: CI - Packages

on:
  pull_request:
    paths:
      - 'packages/{{PACKAGE_NAME}}/**'
      - '{{SHARED_CONFIG_DIR}}/**'
      - 'pnpm-lock.yaml'
      - '.github/workflows/ci-packages.yml'

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      package_changed: ${{ steps.filter.outputs.package }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            package:
              - 'packages/{{PACKAGE_NAME}}/**'

  test-package:
    needs: detect-changes
    if: needs.detect-changes.outputs.package_changed == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup toolchain
        run: {{SETUP_TOOLCHAIN_CMD}}
      - name: Install dependencies
        run: {{INSTALL_DEPS_CMD}}
      - name: Run tests
        run: {{TEST_CMD}}
        working-directory: packages/{{PACKAGE_NAME}}
```

---

## Next Part

Continue to [Part 3: Workflow and Publishing](./MONOREPO_WORKSPACE-part3-workflow-publishing.md) for:
- Local package development workflow
- Package interdependency management
- Publishing strategy
- Verification checklist
- Error recovery
- Best practices
