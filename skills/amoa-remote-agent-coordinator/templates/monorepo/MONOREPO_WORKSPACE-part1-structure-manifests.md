# Monorepo Workspace - Part 1: Structure and Manifests

This part covers package directory structure and manifest templates for monorepo workspace packages.

**Parent document:** [MONOREPO_WORKSPACE.md](./MONOREPO_WORKSPACE.md)

---

## Table of Contents

- 1.1 Template Variables
- 1.2 Package Directory Structure
  - 1.2.1 JavaScript/TypeScript Package
  - 1.2.2 Rust Package
- 1.3 Package Manifest Templates
  - 1.3.1 JavaScript/TypeScript (package.json)
  - 1.3.2 Local Dependencies Format (pnpm)
  - 1.3.3 Rust (Cargo.toml)
  - 1.3.4 Local Dependencies Format (Cargo)

---

## 1.1 Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{PACKAGE_NAME}}` | Package name (scoped) | `@monorepo/core`, `core` |
| `{{PACKAGE_TYPE}}` | Package type | `library`, `application`, `cli-tool` |
| `{{LANGUAGE}}` | Package language | `rust`, `javascript`, `typescript` |
| `{{PARENT_WORKSPACE}}` | Parent workspace path | `packages/`, `apps/` |
| `{{LOCAL_DEPS}}` | Local package dependencies | `["@monorepo/utils"]` |
| `{{EXTERNAL_DEPS}}` | External dependencies | `["tokio", "serde"]` |
| `{{VERSION}}` | Package version | `0.1.0` |
| `{{TASK_ID}}` | Associated task ID | `GH-42` |

---

## 1.2 Package Directory Structure

### 1.2.1 JavaScript/TypeScript Package

```
{{PARENT_WORKSPACE}}/{{PACKAGE_NAME}}/
├── src/
│   ├── index.ts           # Main entry point
│   ├── lib/               # Library code
│   └── types/             # Type definitions
├── tests/
│   ├── unit/
│   └── integration/
├── dist/                  # Build output (gitignored)
├── package.json           # Package manifest
├── tsconfig.json          # Extends root tsconfig
├── eslint.config.js       # Extends root eslint (optional)
├── README.md
└── CHANGELOG.md
```

### 1.2.2 Rust Package

```
{{PARENT_WORKSPACE}}/{{PACKAGE_NAME}}/
├── src/
│   ├── lib.rs             # Library entry (for libraries)
│   ├── main.rs            # Binary entry (for apps)
│   └── modules/
├── tests/
│   ├── unit.rs
│   └── integration.rs
├── benches/               # Benchmarks
├── examples/              # Example usage
├── target/                # Build output (gitignored)
├── Cargo.toml             # Package manifest
├── README.md
└── CHANGELOG.md
```

---

## 1.3 Package Manifest Templates

### 1.3.1 JavaScript/TypeScript (package.json)

```json
{
  "name": "{{PACKAGE_NAME}}",
  "version": "{{VERSION}}",
  "description": "{{DESCRIPTION}}",
  "type": "module",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "types": "./dist/index.d.ts"
    }
  },
  "files": [
    "dist",
    "README.md",
    "CHANGELOG.md"
  ],
  "scripts": {
    "build": "tsc --build",
    "clean": "rm -rf dist",
    "test": "vitest run",
    "test:watch": "vitest",
    "lint": "eslint src",
    "format": "prettier --write src",
    "typecheck": "tsc --noEmit",
    "verify": "npm run lint && npm run typecheck && npm run test"
  },
  "dependencies": {
    {{LOCAL_DEPS_JSON}},
    {{EXTERNAL_DEPS_JSON}}
  },
  "devDependencies": {
    "@types/node": "{{NODE_TYPES_VERSION}}",
    "typescript": "workspace:*",
    "vitest": "workspace:*",
    "eslint": "workspace:*",
    "prettier": "workspace:*"
  },
  "publishConfig": {
    "access": "{{PUBLISH_ACCESS}}"
  }
}
```

### 1.3.2 Local Dependencies Format (pnpm)

```json
"dependencies": {
  "@monorepo/core": "workspace:*",
  "@monorepo/utils": "workspace:^"
}
```

- `workspace:*` - Always use current version
- `workspace:^` - Use compatible version range

### 1.3.3 Rust (Cargo.toml)

```toml
# {{PARENT_WORKSPACE}}/{{PACKAGE_NAME}}/Cargo.toml

[package]
name = "{{PACKAGE_NAME}}"
version = "{{VERSION}}"
edition = "{{RUST_EDITION}}"
authors = ["{{AUTHOR}}"]
description = "{{DESCRIPTION}}"
license = "{{LICENSE}}"
repository = "{{REPO_URL}}"
readme = "README.md"

# For libraries only
[lib]
name = "{{PACKAGE_NAME}}"
path = "src/lib.rs"

# For binaries only
[[bin]]
name = "{{BINARY_NAME}}"
path = "src/main.rs"

[dependencies]
# Local workspace dependencies
{{LOCAL_DEPS_TOML}}

# External dependencies
{{EXTERNAL_DEPS_TOML}}

[dev-dependencies]
criterion = "{{CRITERION_VERSION}}"

[features]
default = []
{{FEATURES}}
```

### 1.3.4 Local Dependencies Format (Cargo)

```toml
[dependencies]
core = { path = "../core", version = "{{VERSION}}" }
utils = { path = "../utils", version = "{{VERSION}}" }
```

---

## Next Part

Continue to [Part 2: Configuration and CI](./MONOREPO_WORKSPACE-part2-config-ci.md) for:
- TypeScript configuration
- Scoped versioning strategy
- Package-level CI triggers
