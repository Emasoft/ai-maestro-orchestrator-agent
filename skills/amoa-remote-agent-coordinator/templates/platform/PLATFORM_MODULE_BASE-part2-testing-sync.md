# Platform Module Base Template - Part 2: Test Configuration & Cross-Platform Sync

This part covers test configuration and cross-platform synchronization rules.

---

## Test Configuration

### Unit Tests

```yaml
testing:
  unit:
    command: "{{UNIT_TEST_COMMAND}}"
    environment:
      {{ENV_VAR}}: "{{ENV_VALUE}}"
    timeout: {{TIMEOUT_SECONDS}}
    required_pass_rate: {{PASS_RATE}}  # 0.0 to 1.0
```

**Variables**:
- `{{UNIT_TEST_COMMAND}}`: Command to run unit tests (e.g., "cargo test")
- `{{ENV_VAR}}`: Environment variable name
- `{{ENV_VALUE}}`: Environment variable value
- `{{TIMEOUT_SECONDS}}`: Maximum test execution time in seconds
- `{{PASS_RATE}}`: Required pass rate (1.0 = 100%, 0.95 = 95%)

### Integration Tests

```yaml
testing:
  integration:
    command: "{{INTEGRATION_TEST_COMMAND}}"
    setup:
      - "{{SETUP_COMMAND}}"
    teardown:
      - "{{TEARDOWN_COMMAND}}"
    environment:
      {{ENV_VAR}}: "{{ENV_VALUE}}"
    timeout: {{TIMEOUT_SECONDS}}
```

### Platform-Specific Tests

Tests that only run on this platform:

```yaml
testing:
  platform_specific:
    - name: "{{TEST_NAME}}"
      command: "{{TEST_COMMAND}}"
      condition: "{{RUN_CONDITION}}"
      required: {{REQUIRED}}
```

**Example**:
```yaml
testing:
  platform_specific:
    - name: "macos-framework-test"
      command: "cargo test --test framework_integration"
      condition: "platform == 'macos'"
      required: true
```

---

## Cross-Platform Synchronization Rules

### Shared Code Locations

Define which code is shared across platforms:

```yaml
sync:
  shared_code:
    - path: "{{SHARED_PATH}}"
      sync_to:
        - "{{PLATFORM_1_PATH}}"
        - "{{PLATFORM_2_PATH}}"
      bidirectional: {{BIDIRECTIONAL}}
```

**Variables**:
- `{{SHARED_PATH}}`: Path to shared code (e.g., "src/core")
- `{{PLATFORM_1_PATH}}`: Path in first platform module
- `{{PLATFORM_2_PATH}}`: Path in second platform module
- `{{BIDIRECTIONAL}}`: Whether changes sync both ways (true/false)

### Version Alignment

```yaml
sync:
  version_alignment:
    strategy: "{{SYNC_STRATEGY}}"  # strict, relaxed, independent
    core_version: "{{CORE_VERSION}}"
    platform_suffix: "{{PLATFORM_SUFFIX}}"
```

**Sync Strategies**:
- `strict`: All platforms must have identical version numbers
- `relaxed`: Major.minor must match, patch can differ
- `independent`: Platforms can have completely different versions

**Example**:
```yaml
sync:
  version_alignment:
    strategy: "relaxed"
    core_version: "1.2.0"
    platform_suffix: "+macos.1"  # Final version: 1.2.0+macos.1
```

### Feature Parity Matrix

Track which features are available on each platform:

```yaml
sync:
  feature_parity:
    - feature: "{{FEATURE_NAME}}"
      status:
        macos: "{{STATUS}}"      # implemented, planned, not_supported
        windows: "{{STATUS}}"
        linux: "{{STATUS}}"
      notes: "{{FEATURE_NOTES}}"
```

**Example**:
```yaml
sync:
  feature_parity:
    - feature: "file_system_watching"
      status:
        macos: "implemented"
        windows: "implemented"
        linux: "implemented"
      notes: "Uses FSEvents on macOS, ReadDirectoryChangesW on Windows, inotify on Linux"

    - feature: "macos_metal_acceleration"
      status:
        macos: "implemented"
        windows: "not_supported"
        linux: "not_supported"
      notes: "Platform-specific GPU acceleration using Metal API"
```

---

**Previous**: [Part 1 - Module Identification, Dependencies & Build](./PLATFORM_MODULE_BASE-part1-identification-dependencies-build.md)

**Next**: [Part 3 - CI/CD, Metadata & Usage](./PLATFORM_MODULE_BASE-part3-cicd-metadata-usage.md)
