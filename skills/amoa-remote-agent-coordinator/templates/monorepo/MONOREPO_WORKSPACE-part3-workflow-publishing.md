# Monorepo Workspace - Part 3: Workflow and Publishing

This part covers package development workflow, interdependency management, publishing strategies, and best practices.

**Parent document:** [MONOREPO_WORKSPACE.md](./MONOREPO_WORKSPACE.md)

---

## Table of Contents

- 3.1 Local Package Development Workflow
  - 3.1.1 Create New Package
  - 3.1.2 Configure Package
  - 3.1.3 Add to Workspace
  - 3.1.4 Verify Package Discovery
  - 3.1.5 Install Dependencies
  - 3.1.6 Build and Test
- 3.2 Package Interdependency Management
  - 3.2.1 Dependency Graph Example
  - 3.2.2 Build Order Determination
  - 3.2.3 Circular Dependency Prevention
- 3.3 Package Publishing Strategy
  - 3.3.1 Private Monorepo (Internal Only)
  - 3.3.2 Public Monorepo (Selective Publishing)
  - 3.3.3 Version Bumping
- 3.4 Verification Checklist
- 3.5 Error Recovery
- 3.6 Best Practices
- 3.7 Template Metadata

---

## 3.1 Local Package Development Workflow

### 3.1.1 Create New Package

```bash
# JavaScript/TypeScript
mkdir -p packages/{{PACKAGE_NAME}}
cd packages/{{PACKAGE_NAME}}
pnpm init

# Rust
cd packages
cargo new {{PACKAGE_NAME}} --lib  # or --bin for applications
```

### 3.1.2 Configure Package

Edit manifest file (package.json or Cargo.toml) with:
- Correct package name (scoped for JS/TS)
- Local dependencies
- Scripts/build configuration

### 3.1.3 Add to Workspace

For JavaScript/TypeScript, pnpm auto-discovers packages matching glob.

For Rust, add to root Cargo.toml:
```toml
[workspace]
members = [
    "packages/*",
    "packages/{{PACKAGE_NAME}}"  # Explicit if needed
]
```

### 3.1.4 Verify Package Discovery

```bash
# JavaScript/TypeScript
pnpm -r list

# Rust
cargo metadata --format-version 1 | jq '.workspace_members'
```

### 3.1.5 Install Dependencies

```bash
# JavaScript/TypeScript
pnpm install

# Rust
cargo fetch --workspace
```

### 3.1.6 Build and Test

```bash
# JavaScript/TypeScript
pnpm --filter {{PACKAGE_NAME}} build
pnpm --filter {{PACKAGE_NAME}} test

# Rust
cargo build -p {{PACKAGE_NAME}}
cargo test -p {{PACKAGE_NAME}}
```

---

## 3.2 Package Interdependency Management

### 3.2.1 Dependency Graph Example

```
apps/web → packages/ui → packages/core
                      ↘
                       packages/utils
apps/cli → packages/core
                     ↘
                      packages/utils
```

### 3.2.2 Build Order Determination

**JavaScript/TypeScript:** pnpm handles topological build order automatically.

**Rust:** Cargo builds dependencies first automatically.

**Manual Topological Sort (if needed):**
```bash
# packages/utils    (no deps)
# packages/core     (depends on utils)
# packages/ui       (depends on core, utils)
# apps/web          (depends on ui, core)

pnpm --filter utils build
pnpm --filter core build
pnpm --filter ui build
pnpm --filter web build
```

### 3.2.3 Circular Dependency Prevention

**DO NOT:**
```
package-a → package-b
package-b → package-a  # CIRCULAR!
```

**FIX:** Extract shared code into a third package:
```
package-a → package-shared
package-b → package-shared
```

---

## 3.3 Package Publishing Strategy

### 3.3.1 Private Monorepo (Internal Only)

```json
{
  "private": true  // Never published
}
```

### 3.3.2 Public Monorepo (Selective Publishing)

```json
{
  "publishConfig": {
    "access": "public",
    "registry": "https://registry.npmjs.org/"
  }
}
```

For Cargo:
```toml
[package]
publish = true  # or false to prevent publishing
```

### 3.3.3 Version Bumping

**JavaScript/TypeScript:**
```bash
# Bump single package
pnpm --filter {{PACKAGE_NAME}} version patch|minor|major

# Bump all packages (fixed versioning)
pnpm -r version patch|minor|major
```

**Rust:**
```bash
# Use cargo-workspaces
cargo install cargo-workspaces
cargo workspaces version patch|minor|major
```

---

## 3.4 Verification Checklist

```markdown
## Package Setup Verification

### Package Structure
- [ ] Package directory created: {{PARENT_WORKSPACE}}/{{PACKAGE_NAME}}
- [ ] Manifest file exists: package.json or Cargo.toml
- [ ] Source directory: src/
- [ ] Test directory: tests/

### Workspace Integration
- [ ] Package discovered by workspace: `{{LIST_PACKAGES_CMD}}`
- [ ] Local dependencies resolved
- [ ] No circular dependencies

### Build and Test
- [ ] Package builds successfully: `{{BUILD_CMD}}`
- [ ] Tests pass: `{{TEST_CMD}}`
- [ ] Linter passes: `{{LINT_CMD}}`
- [ ] Type checker passes: `{{TYPECHECK_CMD}}`

### CI Integration
- [ ] Change detection configured in CI
- [ ] Package-specific tests run on changes
- [ ] Artifacts published (if applicable)

### Documentation
- [ ] README.md exists
- [ ] CHANGELOG.md exists (if versioned)
- [ ] Public API documented
```

---

## 3.5 Error Recovery

| Error | Cause | Fix |
|-------|-------|-----|
| Package not found | Not in workspace glob | Add to workspace.members or check path |
| Dependency not resolved | Wrong local path | Verify relative path or workspace reference |
| Build fails with "can't find crate" | Missing dependency | Add to dependencies section |
| Circular dependency | A→B→A | Refactor into shared package |
| Version conflict | Multiple versions of dep | Use workspace dependency pinning |
| Type errors from local dep | Stale .d.ts files | Rebuild dependency: `pnpm --filter dep build` |

---

## 3.6 Best Practices

### DO
- Use workspace protocol for local deps: `workspace:*`
- Extend root configs (tsconfig, eslint)
- Keep packages focused and single-purpose
- Document public APIs thoroughly
- Version packages independently unless tightly coupled

### DON'T
- Duplicate configuration in every package
- Create circular dependencies
- Bypass root-level verification scripts
- Publish private packages accidentally
- Use absolute paths for local dependencies

---

## 3.7 Template Metadata

```yaml
template:
  name: MONOREPO_WORKSPACE
  version: 1.0.0
  eoa_compatible: true
  parent_template: MONOREPO_BASE
  requires:
    - monorepo workspace root
    - package manager
  generates:
    - package directory
    - manifest file
    - configuration files
    - CI triggers
  compatible_with:
    - pnpm-workspaces
    - cargo-workspace
    - nx
    - turborepo
```
