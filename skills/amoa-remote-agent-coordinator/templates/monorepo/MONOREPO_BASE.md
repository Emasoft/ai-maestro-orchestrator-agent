# Monorepo Base Structure Template

This template defines the foundational structure for monorepo projects managed by EOA orchestrator.
Use this as the base for all monorepo compositions before applying workspace-specific templates.

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{MONOREPO_NAME}}` | Monorepo project name | `xls-platform` |
| `{{MONOREPO_TYPE}}` | Monorepo tool | `pnpm-workspaces`, `cargo-workspace`, `nx`, `turborepo` |
| `{{ROOT_LANGUAGE}}` | Primary language | `javascript`, `rust`, `mixed` |
| `{{WORKSPACE_GLOB}}` | Workspace path pattern | `packages/*`, `apps/*`, `libs/*` |
| `{{SHARED_CONFIG_DIR}}` | Shared configs location | `.config/`, `config/` |
| `{{TASK_ID}}` | Current task ID | `GH-42` |
| `{{TIMESTAMP}}` | Generation timestamp | `2026-01-05T15:16:43Z` |

---

## Root Directory Structure

```
{{MONOREPO_NAME}}/
├── packages/              # Shared libraries and components
│   ├── package-a/
│   ├── package-b/
│   └── ...
├── apps/                  # Application endpoints
│   ├── app-x/
│   ├── app-y/
│   └── ...
├── libs/                  # Language-specific libraries (optional)
│   ├── rust-libs/
│   ├── python-libs/
│   └── ...
├── {{SHARED_CONFIG_DIR}}  # Shared toolchain configs
│   ├── eslint.config.js
│   ├── tsconfig.base.json
│   ├── rustfmt.toml
│   └── ...
├── scripts/               # Root-level automation scripts
│   ├── setup.sh
│   ├── verify-all.sh
│   └── ...
├── .github/
│   └── workflows/
│       ├── ci-root.yml
│       ├── ci-packages.yml
│       └── ...
├── {{MONOREPO_CONFIG}}    # Workspace definition file
├── .gitignore
├── README.md
└── CLAUDE.md
```

---

## Workspace Definition Template

### pnpm Workspaces (JavaScript/TypeScript)

```yaml
# pnpm-workspace.yaml
packages:
  - 'packages/*'
  - 'apps/*'
```

```json
// package.json (root)
{
  "name": "{{MONOREPO_NAME}}",
  "version": "0.1.0",
  "private": true,
  "workspaces": [
    "packages/*",
    "apps/*"
  ],
  "scripts": {
    "build": "pnpm -r build",
    "test": "pnpm -r test",
    "lint": "pnpm -r lint",
    "format": "pnpm -r format",
    "verify": "pnpm -r verify",
    "clean": "pnpm -r clean"
  },
  "devDependencies": {
    "eslint": "{{ESLINT_VERSION}}",
    "prettier": "{{PRETTIER_VERSION}}",
    "typescript": "{{TS_VERSION}}"
  }
}
```

### Cargo Workspace (Rust)

```toml
# Cargo.toml (root)
[workspace]
members = [
    "packages/*",
    "apps/*"
]
resolver = "2"

[workspace.package]
version = "{{VERSION}}"
edition = "{{RUST_EDITION}}"
authors = ["{{AUTHOR}}"]
license = "{{LICENSE}}"

[workspace.dependencies]
# Shared dependencies
tokio = { version = "{{TOKIO_VERSION}}", features = ["full"] }
serde = { version = "{{SERDE_VERSION}}", features = ["derive"] }

[profile.dev]
opt-level = 0

[profile.release]
opt-level = 3
lto = true
```

### Mixed Language (Cargo + pnpm)

```
{{MONOREPO_NAME}}/
├── rust-workspace/        # Cargo workspace root
│   ├── Cargo.toml
│   └── packages/
├── js-workspace/          # pnpm workspace root
│   ├── package.json
│   ├── pnpm-workspace.yaml
│   └── packages/
├── scripts/
│   └── verify-all.sh      # Runs both Rust and JS verification
└── .github/workflows/
    └── ci-mixed.yml       # Matrix builds for both languages
```

---

## Shared Toolchain Configuration

### ESLint (JavaScript/TypeScript)

```javascript
// {{SHARED_CONFIG_DIR}}/eslint.config.js
export default [
  {
    ignores: ['**/dist/**', '**/node_modules/**', '**/coverage/**'],
  },
  {
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
    },
    rules: {
      'no-unused-vars': 'error',
      'no-console': 'warn',
    },
  },
];
```

### TypeScript

```json
// {{SHARED_CONFIG_DIR}}/tsconfig.base.json
{
  "compilerOptions": {
    "target": "{{TS_TARGET}}",
    "module": "{{TS_MODULE}}",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "composite": true
  }
}
```

### Rustfmt

```toml
# {{SHARED_CONFIG_DIR}}/rustfmt.toml
edition = "{{RUST_EDITION}}"
max_width = 100
hard_tabs = false
tab_spaces = 4
use_small_heuristics = "Default"
```

---

## Root-Level Scripts

### Setup Script

```bash
#!/bin/bash
# scripts/setup.sh - Monorepo setup for {{MONOREPO_NAME}}
# Task: {{TASK_ID}}

set -e

log_info() { echo -e "\033[0;32m[INFO]\033[0m $*"; }
log_error() { echo -e "\033[0;31m[ERROR]\033[0m $*"; }

log_info "Setting up {{MONOREPO_NAME}} monorepo..."

# Install root dependencies
{{SETUP_ROOT_DEPS_CMD}}

# Install workspace dependencies
{{SETUP_WORKSPACE_DEPS_CMD}}

# Verify installation
{{VERIFY_INSTALLATION_CMD}}

log_info "Setup complete! Run 'npm run verify' or 'cargo test --workspace'"
```

### Verification Script

```bash
#!/bin/bash
# scripts/verify-all.sh - Run all verification checks

set -e

log_info() { echo -e "\033[0;32m[INFO]\033[0m $*"; }

log_info "Running monorepo verification..."

# Format check
log_info "Checking formatting..."
{{FORMAT_CHECK_CMD}}

# Lint check
log_info "Running linter..."
{{LINT_CMD}}

# Type check (if applicable)
log_info "Type checking..."
{{TYPE_CHECK_CMD}}

# Build all packages
log_info "Building all packages..."
{{BUILD_ALL_CMD}}

# Run all tests
log_info "Running tests..."
{{TEST_ALL_CMD}}

log_info "All checks passed!"
```

---

## EOA Pipeline Labels for Monorepo

In addition to standard EOA labels, monorepos use workspace-specific labels:

| Label | Color | Description |
|-------|-------|-------------|
| `workspace:packages` | `#006B75` | Affects shared packages |
| `workspace:apps` | `#7057FF` | Affects applications |
| `workspace:libs` | `#008672` | Affects language-specific libs |
| `workspace:root` | `#E99695` | Affects root configuration |
| `workspace:all` | `#B60205` | Affects multiple workspaces |

---

## Pipeline Stages for Monorepo

```yaml
stages:
  - setup
  - lint
  - typecheck
  - build
  - test
  - integration
  - publish

workflow:
  1. setup: Install dependencies (root + all workspaces)
  2. lint: Run linters on all packages (parallel)
  3. typecheck: Run type checkers (parallel)
  4. build: Build packages in dependency order
  5. test: Run unit tests (parallel)
  6. integration: Run integration tests
  7. publish: Publish changed packages
```

---

## Branch Naming Convention

```
feature/{{TASK_ID}}-workspace-name-description
fix/{{TASK_ID}}-workspace-name-description
refactor/{{TASK_ID}}-workspace-name-description

Examples:
feature/GH-42-packages-core-add-logger
fix/GH-43-apps-web-fix-routing
refactor/GH-44-libs-rust-split-utils
```

---

## Dependency Management

### Local Package References (pnpm)

```json
// packages/app/package.json
{
  "name": "@{{MONOREPO_NAME}}/app",
  "dependencies": {
    "@{{MONOREPO_NAME}}/core": "workspace:*",
    "@{{MONOREPO_NAME}}/utils": "workspace:^"
  }
}
```

### Local Package References (Cargo)

```toml
# packages/app/Cargo.toml
[dependencies]
core = { path = "../core" }
utils = { path = "../utils", version = "{{VERSION}}" }
```

---

## Verification Checklist

```markdown
## Monorepo Setup Verification

### Root Configuration
- [ ] Workspace definition file exists: {{MONOREPO_CONFIG}}
- [ ] Root package manager installed: {{PACKAGE_MANAGER}}
- [ ] Shared config directory created: {{SHARED_CONFIG_DIR}}
- [ ] Root scripts executable: `chmod +x scripts/*.sh`

### Workspace Discovery
- [ ] All workspaces discovered: `{{LIST_WORKSPACES_CMD}}`
- [ ] No broken workspace references
- [ ] Local dependencies resolved

### Toolchain Verification
- [ ] Root-level formatter works: `{{FORMAT_CHECK_CMD}}`
- [ ] Root-level linter works: `{{LINT_CMD}}`
- [ ] All packages build: `{{BUILD_ALL_CMD}}`
- [ ] All tests pass: `{{TEST_ALL_CMD}}`

### EOA Compliance
- [ ] Workspace labels created in GitHub
- [ ] CI workflow uses change detection
- [ ] Branch naming includes workspace scope
```

---

## Error Recovery

| Error | Cause | Fix |
|-------|-------|-----|
| Workspace not found | Path mismatch | Check glob pattern in workspace config |
| Circular dependency | A depends on B, B depends on A | Refactor into shared package |
| Version conflict | Multiple versions of same dep | Use workspace dependency resolution |
| Build order error | Building before dependencies | Use topological build order |
| Cache corruption | Stale lock files | Delete lock files, reinstall |

---

## Cross-Platform Notes

### Windows
- Use forward slashes in glob patterns
- May need Git Bash or WSL for shell scripts
- Check line endings (LF vs CRLF)

### macOS/Linux
- Ensure scripts have execute permission: `chmod +x scripts/*.sh`
- Use `realpath` or `readlink -f` for absolute paths

---

## Template Metadata

```yaml
template:
  name: MONOREPO_BASE
  version: 1.0.0
  eoa_compatible: true
  requires:
    - git
    - bash
    - package_manager (language-specific)
  generates:
    - workspace definition
    - root configuration
    - shared toolchain configs
    - setup scripts
    - verification scripts
  compatible_with:
    - pnpm-workspaces
    - cargo-workspace
    - nx
    - turborepo
    - lerna
```
