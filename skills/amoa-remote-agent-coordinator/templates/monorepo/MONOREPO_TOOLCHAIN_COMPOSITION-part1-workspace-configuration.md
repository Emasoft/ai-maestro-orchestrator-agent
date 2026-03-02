# Monorepo Toolchain Composition - Part 1: Workspace Configuration

This part covers the configuration files for each language workspace in a multi-language monorepo.

---

## Combined Workspace Configuration

### Rust Workspace (Cargo.toml)

```toml
# {{RUST_WORKSPACE}}/Cargo.toml
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

[workspace.dependencies]
tokio = { version = "{{TOKIO_VERSION}}", features = ["full"] }
serde = { version = "{{SERDE_VERSION}}", features = ["derive"] }

# Python bindings (if using PyO3)
pyo3 = { version = "{{PYO3_VERSION}}", features = ["extension-module"] }

# WASM bindings (if targeting web)
wasm-bindgen = "{{WASM_BINDGEN_VERSION}}"
```

### JavaScript Workspace (package.json + pnpm-workspace.yaml)

```json
// {{JS_WORKSPACE}}/package.json
{
  "name": "{{MONOREPO_NAME}}-js",
  "version": "{{VERSION}}",
  "private": true,
  "workspaces": [
    "packages/*",
    "apps/*"
  ],
  "scripts": {
    "build": "pnpm -r build",
    "test": "pnpm -r test",
    "lint": "eslint .",
    "format": "prettier --write .",
    "typecheck": "pnpm -r typecheck",
    "verify": "pnpm run lint && pnpm run typecheck && pnpm run test"
  },
  "devDependencies": {
    "eslint": "{{ESLINT_VERSION}}",
    "prettier": "{{PRETTIER_VERSION}}",
    "typescript": "{{TS_VERSION}}",
    "vitest": "{{VITEST_VERSION}}"
  }
}
```

```yaml
# {{JS_WORKSPACE}}/pnpm-workspace.yaml
packages:
  - 'packages/*'
  - 'apps/*'
```

### Python Workspace (pyproject.toml with uv)

```toml
# {{PYTHON_WORKSPACE}}/pyproject.toml
[project]
name = "{{MONOREPO_NAME}}-python"
version = "{{VERSION}}"
requires-python = ">=3.12"

[tool.uv]
dev-dependencies = [
    "pytest>=8.0.0",
    "ruff>=0.8.0",
    "mypy>=1.0.0",
]

[tool.uv.workspace]
members = ["packages/*"]

[tool.ruff]
line-length = 320
target-version = "py312"
extend = "../../{{SHARED_CONFIG_DIR}}/ruff.toml"

[tool.mypy]
python_version = "3.12"
strict = true
```

---

## Shared Toolchain Configuration

### Rustfmt ({{SHARED_CONFIG_DIR}}/rustfmt.toml)

```toml
edition = "{{RUST_EDITION}}"
max_width = 100
hard_tabs = false
tab_spaces = 4
imports_granularity = "Crate"
group_imports = "StdExternalCrate"
```

### ESLint ({{SHARED_CONFIG_DIR}}/eslint.config.js)

```javascript
export default [
  {
    ignores: [
      '**/dist/**',
      '**/node_modules/**',
      '**/target/**',
      '**/__pycache__/**',
    ],
  },
  {
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
    },
    rules: {
      'no-unused-vars': 'error',
    },
  },
];
```

### Ruff ({{SHARED_CONFIG_DIR}}/ruff.toml)

```toml
line-length = 320
target-version = "py312"

[lint]
select = ["E", "F", "W", "I", "N", "UP"]
ignore = []

[format]
quote-style = "double"
indent-style = "space"
```

---

**Navigation:**
- [Back to Index](./MONOREPO_TOOLCHAIN_COMPOSITION.md)
- [Next: Part 2 - Verification Scripts](./MONOREPO_TOOLCHAIN_COMPOSITION-part2-verification-scripts.md)
