# Platform Module Base Template - Part 1: Module Identification, Dependencies & Build

This part covers module identification, dependency declarations, and build configuration.

---

## Module Identification

```yaml
module:
  name: "{{MODULE_NAME}}"
  version: "{{MODULE_VERSION}}"
  platform: "{{PLATFORM_NAME}}"  # macos, windows, linux
  architecture: "{{ARCH}}"        # x64, arm64, universal
  type: "{{MODULE_TYPE}}"         # library, executable, plugin
```

**Variables**:
- `{{MODULE_NAME}}`: Unique module identifier (e.g., "file-watcher", "process-manager")
- `{{MODULE_VERSION}}`: Semantic version (e.g., "1.0.0")
- `{{PLATFORM_NAME}}`: Target platform (macos, windows, linux)
- `{{ARCH}}`: Target architecture (x64, arm64, universal)
- `{{MODULE_TYPE}}`: Build output type (library, executable, plugin)

---

## Dependency Declarations

### Shared Dependencies

Dependencies that are identical across all platforms:

```yaml
dependencies:
  shared:
    - name: "{{DEP_NAME}}"
      version: "{{DEP_VERSION}}"
      source: "{{DEP_SOURCE}}"  # npm, cargo, pip, system
      required: {{REQUIRED}}     # true, false
```

**Example**:
```yaml
dependencies:
  shared:
    - name: "serde"
      version: "1.0"
      source: "cargo"
      required: true
    - name: "tokio"
      version: "1.35"
      source: "cargo"
      required: true
```

### Platform-Specific Dependencies

Dependencies unique to this platform:

```yaml
dependencies:
  platform_specific:
    - name: "{{PLATFORM_DEP_NAME}}"
      version: "{{PLATFORM_DEP_VERSION}}"
      source: "{{PLATFORM_DEP_SOURCE}}"
      platform: "{{PLATFORM_NAME}}"
      arch: "{{ARCH}}"
      required: {{REQUIRED}}
      notes: "{{DEPENDENCY_NOTES}}"
```

**Example for macOS**:
```yaml
dependencies:
  platform_specific:
    - name: "cocoa"
      version: "0.25"
      source: "cargo"
      platform: "macos"
      arch: "universal"
      required: true
      notes: "Required for AppKit bindings"
```

---

## Build Configuration

### Compiler Settings

```yaml
build:
  compiler: "{{COMPILER}}"          # rustc, clang, msvc, gcc
  toolchain: "{{TOOLCHAIN}}"        # stable, nightly, specific version
  optimization: "{{OPT_LEVEL}}"     # 0, 1, 2, 3, s, z
  debug_symbols: {{DEBUG}}           # true, false

  flags:
    compile: "{{COMPILE_FLAGS}}"
    link: "{{LINK_FLAGS}}"
```

**Variables**:
- `{{COMPILER}}`: Compiler to use (rustc for Rust, clang for C/C++, msvc for Windows, gcc for Linux)
- `{{TOOLCHAIN}}`: Specific toolchain version if needed
- `{{OPT_LEVEL}}`: Optimization level (0=none, 3=max, s=size, z=minimal size)
- `{{DEBUG}}`: Whether to include debug symbols
- `{{COMPILE_FLAGS}}`: Additional compiler flags (space-separated)
- `{{LINK_FLAGS}}`: Additional linker flags (space-separated)

### Build Targets

```yaml
build:
  targets:
    - name: "{{TARGET_NAME}}"
      triple: "{{TARGET_TRIPLE}}"
      output: "{{OUTPUT_PATH}}"
      type: "{{OUTPUT_TYPE}}"        # bin, lib, dylib, staticlib
```

**Example**:
```yaml
build:
  targets:
    - name: "file-watcher-macos"
      triple: "aarch64-apple-darwin"
      output: "target/aarch64-apple-darwin/release/libfile_watcher.dylib"
      type: "dylib"
    - name: "file-watcher-macos-intel"
      triple: "x86_64-apple-darwin"
      output: "target/x86_64-apple-darwin/release/libfile_watcher.dylib"
      type: "dylib"
```

### Build Scripts

Pre-build, build, and post-build scripts:

```yaml
build:
  scripts:
    pre_build:
      - "{{PRE_BUILD_COMMAND}}"
    build:
      - "{{BUILD_COMMAND}}"
    post_build:
      - "{{POST_BUILD_COMMAND}}"
```

**Example**:
```yaml
build:
  scripts:
    pre_build:
      - "rustup target add aarch64-apple-darwin"
      - "rustup target add x86_64-apple-darwin"
    build:
      - "cargo build --release --target aarch64-apple-darwin"
      - "cargo build --release --target x86_64-apple-darwin"
    post_build:
      - "lipo -create -output target/universal/libfile_watcher.dylib target/aarch64-apple-darwin/release/libfile_watcher.dylib target/x86_64-apple-darwin/release/libfile_watcher.dylib"
```

---

**Next**: [Part 2 - Test Configuration & Cross-Platform Sync](./PLATFORM_MODULE_BASE-part2-testing-sync.md)
