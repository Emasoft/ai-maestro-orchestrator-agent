# Windows Module Part 2: Build Configuration

This document covers Windows-specific build configuration, toolchains, and manifests.

**Parent document**: [WINDOWS_MODULE.md](./WINDOWS_MODULE.md)
**Previous**: [WINDOWS_MODULE-part1-dependencies.md](./WINDOWS_MODULE-part1-dependencies.md)

---

## Build Configuration (Windows)

### MSVC Toolchain

```yaml
build:
  compiler: "msvc"
  toolchain: "stable"
  msvc_version: "{{MSVC_VERSION}}"  # e.g., "19.38" (VS 2022)
  platform_toolset: "{{TOOLSET}}"   # v143 (VS 2022), v142 (VS 2019)

  optimization: "{{OPT_LEVEL}}"
  debug_symbols: {{DEBUG}}
  incremental: {{INCREMENTAL}}      # true for faster incremental builds
  whole_program_optimization: {{WPO}}  # true for link-time code generation
```

**Variables**:
- `{{MSVC_VERSION}}`: MSVC compiler version (e.g., "19.38" for VS 2022 17.8)
- `{{TOOLSET}}`: Platform toolset (v143 for VS 2022, v142 for VS 2019, v141 for VS 2017)
- `{{INCREMENTAL}}`: Enable incremental linking (faster debug builds)
- `{{WPO}}`: Whole program optimization / LTCG (slower builds, faster runtime)

### Target Configuration

```yaml
build:
  targets:
    # 64-bit (x64) - Most common
    - name: "{{MODULE_NAME}}-x64"
      triple: "x86_64-pc-windows-msvc"
      output: "target/x86_64-pc-windows-msvc/release/{{OUTPUT_NAME}}"
      type: "{{OUTPUT_TYPE}}"
      rustflags:
        - "-C target-feature=+crt-static"  # Static CRT
        - "-C link-arg=/SUBSYSTEM:{{SUBSYSTEM}}"

    # 32-bit (x86) - Legacy support
    - name: "{{MODULE_NAME}}-x86"
      triple: "i686-pc-windows-msvc"
      output: "target/i686-pc-windows-msvc/release/{{OUTPUT_NAME}}"
      type: "{{OUTPUT_TYPE}}"
      rustflags:
        - "-C target-feature=+crt-static"
        - "-C link-arg=/SUBSYSTEM:{{SUBSYSTEM}}"

    # ARM64 - Windows on ARM
    - name: "{{MODULE_NAME}}-arm64"
      triple: "aarch64-pc-windows-msvc"
      output: "target/aarch64-pc-windows-msvc/release/{{OUTPUT_NAME}}"
      type: "{{OUTPUT_TYPE}}"
      rustflags:
        - "-C target-feature=+crt-static"
        - "-C link-arg=/SUBSYSTEM:{{SUBSYSTEM}}"
```

**Output Types**:
- `dll`: Dynamic-link library (.dll)
- `lib`: Static library (.lib)
- `exe`: Executable (.exe)
- `cdylib`: C-compatible DLL for FFI

### Cargo Configuration

Create `.cargo/config.toml` for Windows-specific settings:

```toml
[target.x86_64-pc-windows-msvc]
rustflags = [
  "-C", "target-feature=+crt-static",
  "-C", "link-arg=/MANIFEST:EMBED",
  "-C", "link-arg=/MANIFESTINPUT:{{MANIFEST_FILE}}",
  {{#if WPO}}
  "-C", "link-arg=/LTCG",
  {{/if}}
  {{#if DEBUG}}
  "-C", "link-arg=/DEBUG:FULL",
  {{else}}
  "-C", "link-arg=/DEBUG:NONE",
  {{/if}}
]

[target.i686-pc-windows-msvc]
rustflags = [
  "-C", "target-feature=+crt-static",
  "-C", "link-arg=/MANIFEST:EMBED",
  "-C", "link-arg=/MANIFESTINPUT:{{MANIFEST_FILE}}",
]

[target.aarch64-pc-windows-msvc]
rustflags = [
  "-C", "target-feature=+crt-static",
  "-C", "link-arg=/MANIFEST:EMBED",
  "-C", "link-arg=/MANIFESTINPUT:{{MANIFEST_FILE}}",
]

[build]
jobs = {{BUILD_JOBS}}
target-dir = "target"
```

### Application Manifest

Create a manifest file for UAC, DPI awareness, and compatibility:

**File**: `{{MODULE_NAME}}.manifest`
```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <!-- Application Identity -->
  <assemblyIdentity
    version="{{VERSION}}.0.0"
    processorArchitecture="{{ARCH}}"
    name="{{COMPANY}}.{{MODULE_NAME}}"
    type="win32"
  />

  <!-- UAC Execution Level -->
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel
          level="{{UAC_LEVEL}}"
          uiAccess="false"
        />
      </requestedPrivileges>
    </security>
  </trustInfo>

  <!-- DPI Awareness (Windows 10+) -->
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true</dpiAware>
      <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2</dpiAwareness>
    </windowsSettings>
  </application>

  <!-- Supported OS Versions -->
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <!-- Windows 10 -->
      <supportedOS Id="{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}"/>
      <!-- Windows 11 -->
      <supportedOS Id="{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9b}"/>
    </application>
  </compatibility>

  <!-- Visual Styles -->
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
        type="win32"
        name="Microsoft.Windows.Common-Controls"
        version="6.0.0.0"
        processorArchitecture="*"
        publicKeyToken="6595b64144ccf1df"
        language="*"
      />
    </dependentAssembly>
  </dependency>
</assembly>
```

**UAC Levels**:
- `asInvoker`: Run with current user privileges (most common)
- `highestAvailable`: Run with highest privileges available to user
- `requireAdministrator`: Always require administrator privileges

### Resource File

Create a resource file for version information and icons:

**File**: `{{MODULE_NAME}}.rc`
```rc
#include <windows.h>

// Icon
IDI_ICON1 ICON "{{ICON_PATH}}"

// Version Information
VS_VERSION_INFO VERSIONINFO
FILEVERSION     {{FILE_VERSION_1}},{{FILE_VERSION_2}},{{FILE_VERSION_3}},{{FILE_VERSION_4}}
PRODUCTVERSION  {{PRODUCT_VERSION_1}},{{PRODUCT_VERSION_2}},{{PRODUCT_VERSION_3}},{{PRODUCT_VERSION_4}}
FILEFLAGSMASK   VS_FFI_FILEFLAGSMASK
FILEFLAGS       {{FILE_FLAGS}}
FILEOS          VOS_NT_WINDOWS32
FILETYPE        {{FILE_TYPE}}
FILESUBTYPE     VFT2_UNKNOWN
BEGIN
    BLOCK "StringFileInfo"
    BEGIN
        BLOCK "040904B0"  // English (US), Unicode
        BEGIN
            VALUE "CompanyName",      "{{COMPANY_NAME}}"
            VALUE "FileDescription",  "{{FILE_DESCRIPTION}}"
            VALUE "FileVersion",      "{{FILE_VERSION_STRING}}"
            VALUE "InternalName",     "{{INTERNAL_NAME}}"
            VALUE "LegalCopyright",   "{{COPYRIGHT}}"
            VALUE "OriginalFilename", "{{ORIGINAL_FILENAME}}"
            VALUE "ProductName",      "{{PRODUCT_NAME}}"
            VALUE "ProductVersion",   "{{PRODUCT_VERSION_STRING}}"
        END
    END
    BLOCK "VarFileInfo"
    BEGIN
        VALUE "Translation", 0x409, 1200  // English (US), Unicode
    END
END
```

**File Types**:
- `VFT_APP` (0x00000001): Application (.exe)
- `VFT_DLL` (0x00000002): Dynamic-link library (.dll)
- `VFT_STATIC_LIB` (0x00000007): Static library (.lib)

### Build Script

**File**: `build.rs`
```rust
fn main() {
    // Embed manifest
    #[cfg(target_os = "windows")]
    {
        embed_resource::compile("{{MODULE_NAME}}.rc");
    }

    // Link Windows libraries
    println!("cargo:rustc-link-lib=kernel32");
    println!("cargo:rustc-link-lib=user32");
    println!("cargo:rustc-link-lib=shell32");

    // Set subsystem
    println!("cargo:rustc-link-arg=/SUBSYSTEM:{{SUBSYSTEM}}");
}
```

---

**Next**: [WINDOWS_MODULE-part3-apis-testing.md](./WINDOWS_MODULE-part3-apis-testing.md) - Platform APIs and Testing
