# Swift Toolchain Template

Extends: `BASE_TOOLCHAIN.md`
Package Manager: SwiftPM (swift package manager)
Preferred for: iOS/macOS apps, cross-platform CLI tools, server-side Swift

---

## Quick Reference

| Component | Tool | Version | Install |
|-----------|------|---------|---------|
| Language | swift | 5.9+ | Xcode (macOS) / swiftly (Linux) |
| Package Manager | SwiftPM | bundled | - |
| Formatter | swift-format | latest | `swift package plugin --allow-writing-to-package-directory format` |
| Linter | swiftlint | 0.54+ | `brew install swiftlint` (macOS) |
| Test Runner | swift test | bundled | - |
| Build Tool | xcodebuild | bundled (macOS) | - |

---

## Document Structure

This template is split into multiple parts for easier navigation:

### Part 1: Setup & Variables
**File:** [SWIFT_TOOLCHAIN-part1-setup.md](./SWIFT_TOOLCHAIN-part1-setup.md)

Contents:
- Variable Substitutions (YAML configuration block)
- Complete Setup Script (Bash)
  - Platform detection (macOS/Linux)
  - Swift installation
  - Development tools installation (swiftlint, swift-format)
  - Verification steps
  - Config file generation (.swift-format, .swiftlint.yml)

### Part 2: Templates
**File:** [SWIFT_TOOLCHAIN-part2-templates.md](./SWIFT_TOOLCHAIN-part2-templates.md)

Contents:
- Package.swift Template (complete SwiftPM manifest)
- GitHub Actions CI Template
  - Build and test matrix (Ubuntu + macOS, Swift 5.9 + 5.10)
  - Lint job (SwiftLint)
  - Format check job
  - Code coverage job
- Library Requirements (MANDATORY)
- Violations list (what fails review)

### Part 3: Platform Guide
**File:** [SWIFT_TOOLCHAIN-part3-platform.md](./SWIFT_TOOLCHAIN-part3-platform.md)

Contents:
- Platform-Specific Guidance
  - iOS/macOS Native Apps (UIKit/SwiftUI)
  - Cross-Platform Swift (CLI/Server/Library)
- iOS Frameworks Quick Reference
- Cross-Platform Considerations
  - macOS (Intel + Apple Silicon universal binary)
  - Linux (system dependencies)
  - Windows (experimental)
- Verification Checklist
- Common Issues and Fixes
- Template Metadata

---

## Key Commands

| Action | Command |
|--------|---------|
| Build | `swift build -c release` |
| Test | `swift test --parallel` |
| Lint | `swiftlint lint --strict` |
| Format | `swift package plugin --allow-writing-to-package-directory format` |
| Format Check | `swift package plugin format --check` |
| Verify All | `swift build && swift test && swiftlint lint --strict` |
| Coverage | `swift test --enable-code-coverage` |

---

## Xcode Commands (iOS/macOS Apps)

| Action | Command |
|--------|---------|
| Build | `xcodebuild -scheme {{SCHEME_NAME}} -configuration Release` |
| Test | `xcodebuild test -scheme {{SCHEME_NAME}} -destination 'platform=iOS Simulator,name=iPhone 15'` |
| Archive | `xcodebuild archive -scheme {{SCHEME_NAME}} -archivePath build/{{PROJECT_NAME}}.xcarchive` |

---

## Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `Package.swift` | SwiftPM manifest | Project root |
| `.swift-format` | swift-format config | Project root |
| `.swiftlint.yml` | SwiftLint config | Project root |
| `.github/workflows/ci.yml` | CI workflow | `.github/workflows/` |

---

## Required Dependencies

### For CLI Applications

```swift
dependencies: [
    .package(url: "https://github.com/apple/swift-argument-parser.git", from: "1.3.0"),
    .package(url: "https://github.com/apple/swift-format.git", from: "509.0.0"),
    .package(url: "https://github.com/apple/swift-log.git", from: "1.5.0"),
]
```

### For Libraries

```swift
dependencies: [
    .package(url: "https://github.com/apple/swift-format.git", from: "509.0.0"),
    .package(url: "https://github.com/apple/swift-log.git", from: "1.5.0"),
]
```

---

## Template Metadata

```yaml
template:
  name: SWIFT_TOOLCHAIN
  version: 1.0.0
  eoa_compatible: true
  platforms:
    - macos
    - linux
    - ios
    - watchos
    - tvos
  requires:
    - swift: "5.9+"
    - xcode-clt (macOS)
    - swiftly (Linux)
  generates:
    - setup script (macOS + Linux)
    - Package.swift template
    - .swift-format config
    - .swiftlint.yml config
    - CI workflow with swift-actions/setup-swift@v2
  parts:
    - SWIFT_TOOLCHAIN-part1-setup.md
    - SWIFT_TOOLCHAIN-part2-templates.md
    - SWIFT_TOOLCHAIN-part3-platform.md
```
