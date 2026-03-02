# Monorepo Toolchain Composition - Part 4: Best Practices

This part covers verification checklists, error recovery, best practices, and template metadata.

---

## Verification Checklist

```markdown
## Multi-Language Monorepo Verification

### Toolchain Installation
- [ ] Rust toolchain: `rustc --version`
- [ ] Node.js: `node --version`
- [ ] Python: `python --version`
- [ ] Cargo: `cargo --version`
- [ ] pnpm: `pnpm --version`
- [ ] uv: `uv --version`

### Workspace Discovery
- [ ] Rust packages: `cargo metadata --format-version 1`
- [ ] JS packages: `pnpm -r list`
- [ ] Python packages: `uv run python -c "import {{PACKAGE}}"`

### Cross-Language Dependencies
- [ ] Rust core builds: `cargo build -p core`
- [ ] Python bindings build: `cd python-workspace && uv run maturin develop`
- [ ] WASM builds: `wasm-pack build`
- [ ] JS can import WASM: Check imports in JS workspace

### Unified Verification
- [ ] Root verification passes: `./scripts/verify-all.sh`
- [ ] All language-specific verifications pass
- [ ] Build order correct (no missing dependencies)

### CI Integration
- [ ] Separate workflows per language
- [ ] Matrix builds for each language version
- [ ] Change detection triggers correct workflows
```

---

## Error Recovery

| Error | Cause | Fix |
|-------|-------|-----|
| Rust build fails to find Python | Python not in PATH | Install Python, add to PATH |
| Python can't import Rust module | Bindings not built | Run `maturin develop` |
| WASM build fails | wasm-pack not installed | `cargo install wasm-pack` |
| JS can't import WASM | Wrong target | Use `--target web` in wasm-pack |
| Cross-language version mismatch | Incompatible ABIs | Pin versions in workspace root |
| Tool not found | Wrong workspace | Check CWD before running commands |

---

## Best Practices

### DO
- Use language-separated workspaces for large projects
- Share configuration files via {{SHARED_CONFIG_DIR}}
- Document build order explicitly
- Use root-level scripts for orchestration
- Pin tool versions in workspace roots

### DON'T
- Mix package types in the same directory
- Duplicate configuration across workspaces
- Assume build order (document dependencies)
- Install language-specific tools globally
- Bypass root-level verification scripts

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

---

**Navigation:**
- [Back to Index](./MONOREPO_TOOLCHAIN_COMPOSITION.md)
- [Previous: Part 3 - Integration Patterns](./MONOREPO_TOOLCHAIN_COMPOSITION-part3-integration-patterns.md)
