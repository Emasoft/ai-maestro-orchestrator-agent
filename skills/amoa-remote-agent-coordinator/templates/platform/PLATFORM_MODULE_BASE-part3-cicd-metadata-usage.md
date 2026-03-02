# Platform Module Base Template - Part 3: CI/CD, Metadata & Usage

This part covers CI/CD integration, module metadata, file structure, usage instructions, and troubleshooting.

---

## CI/CD Integration

### CI Matrix Configuration

```yaml
ci:
  matrix:
    platform: "{{PLATFORM_NAME}}"
    architecture: ["{{ARCH_1}}", "{{ARCH_2}}"]
    rust_version: ["{{RUST_VERSION}}"]

  steps:
    setup:
      - "{{SETUP_STEP}}"
    build:
      - "{{BUILD_STEP}}"
    test:
      - "{{TEST_STEP}}"
    package:
      - "{{PACKAGE_STEP}}"
```

**Example for GitHub Actions**:
```yaml
ci:
  matrix:
    platform: "macos"
    architecture: ["x64", "arm64"]
    rust_version: ["stable"]

  steps:
    setup:
      - "rustup target add x86_64-apple-darwin"
      - "rustup target add aarch64-apple-darwin"
    build:
      - "cargo build --release --target x86_64-apple-darwin"
      - "cargo build --release --target aarch64-apple-darwin"
    test:
      - "cargo test --release --target $(rustc -vV | grep host | cut -d' ' -f2)"
    package:
      - "lipo -create -output universal/{{MODULE_NAME}} target/x86_64-apple-darwin/release/{{MODULE_NAME}} target/aarch64-apple-darwin/release/{{MODULE_NAME}}"
```

---

## Module Metadata

### Registration Information

```yaml
metadata:
  author: "{{AUTHOR}}"
  maintainer: "{{MAINTAINER}}"
  repository: "{{REPO_URL}}"
  license: "{{LICENSE}}"
  description: "{{DESCRIPTION}}"
  keywords: ["{{KEYWORD_1}}", "{{KEYWORD_2}}"]
```

### Compatibility Matrix

```yaml
metadata:
  compatibility:
    min_os_version: "{{MIN_OS_VERSION}}"
    max_os_version: "{{MAX_OS_VERSION}}"
    tested_versions:
      - "{{TESTED_VERSION_1}}"
      - "{{TESTED_VERSION_2}}"
```

**Example**:
```yaml
metadata:
  compatibility:
    min_os_version: "10.15"  # Catalina
    max_os_version: "14.2"   # Sonoma
    tested_versions:
      - "13.5"  # Ventura
      - "14.0"  # Sonoma
      - "14.2"  # Sonoma
```

---

## File Structure Template

```
{{MODULE_NAME}}-{{PLATFORM_NAME}}/
├── Cargo.toml                    # Rust package manifest
├── build.rs                      # Build script
├── README.md                     # Platform-specific README
├── src/
│   ├── lib.rs                    # Main library entry point
│   ├── platform/                 # Platform-specific implementations
│   │   └── {{PLATFORM_NAME}}.rs
│   └── shared/                   # Shared code (symlinked)
│       └── core.rs
├── tests/
│   ├── unit/
│   │   └── {{TEST_NAME}}.rs
│   └── integration/
│       └── {{TEST_NAME}}.rs
├── benches/                      # Benchmarks
│   └── {{BENCH_NAME}}.rs
├── examples/                     # Usage examples
│   └── {{EXAMPLE_NAME}}.rs
└── .cargo/
    └── config.toml               # Cargo configuration
```

---

## Usage Instructions

### Creating a New Platform Module

1. **Copy this template** to a new file named `{{MODULE_NAME}}_{{PLATFORM_NAME}}.md`

2. **Replace all template variables** with actual values:
   - Use find/replace for `{{VARIABLE}}` patterns
   - Ensure all paths are correct for your project structure
   - Verify dependency versions are current

3. **Extend with platform-specific details**:
   - Add platform-specific build requirements
   - Document platform-specific APIs used
   - List platform-specific limitations

4. **Create the module directory structure** as shown above

5. **Implement the module** following the configuration

6. **Test on the target platform** before marking as complete

### Updating an Existing Module

1. **Update version numbers** in module identification section

2. **Review dependency versions** and update if needed

3. **Check feature parity matrix** and update status

4. **Run tests** to ensure compatibility

5. **Update CI/CD configuration** if build steps changed

6. **Document breaking changes** in README.md

---

## Troubleshooting

### Build Failures

**Problem**: Compiler not found
**Solution**: Ensure toolchain is installed and in PATH. For Rust: `rustup default stable`

**Problem**: Missing dependencies
**Solution**: Run pre-build scripts to install platform-specific dependencies

**Problem**: Architecture mismatch
**Solution**: Verify `{{TARGET_TRIPLE}}` matches your system. Use `rustc -vV | grep host` to check

### Test Failures

**Problem**: Tests timeout on CI
**Solution**: Increase `{{TIMEOUT_SECONDS}}` or optimize test performance

**Problem**: Platform-specific tests fail
**Solution**: Ensure `{{RUN_CONDITION}}` correctly identifies the platform

### Sync Issues

**Problem**: Version mismatch between platforms
**Solution**: Check `version_alignment.strategy` and ensure core versions match

**Problem**: Feature missing on platform
**Solution**: Check `feature_parity` matrix and implement or mark as `not_supported`

---

## Template Validation

Before using this template, validate that:

- [ ] All `{{VARIABLE}}` placeholders are replaced
- [ ] Dependency versions are current and compatible
- [ ] Build commands work on target platform
- [ ] Test commands execute successfully
- [ ] CI/CD matrix includes all required platforms
- [ ] File structure matches project layout
- [ ] Documentation is complete and accurate

---

## Related Templates

- [MACOS_MODULE.md](./MACOS_MODULE.md) - macOS-specific module template
- [WINDOWS_MODULE.md](./WINDOWS_MODULE.md) - Windows-specific module template
- [LINUX_MODULE.md](./LINUX_MODULE.md) - Linux-specific module template
- [CROSS_PLATFORM_SYNC.md](./CROSS_PLATFORM_SYNC.md) - Synchronization rules and strategies

---

**Previous**: [Part 2 - Test Configuration & Cross-Platform Sync](./PLATFORM_MODULE_BASE-part2-testing-sync.md)
