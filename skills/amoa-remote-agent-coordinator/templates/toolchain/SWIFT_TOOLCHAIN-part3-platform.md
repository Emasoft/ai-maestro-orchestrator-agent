# Swift Toolchain - Part 3: Platform Guide

**Parent Document:** [SWIFT_TOOLCHAIN.md](./SWIFT_TOOLCHAIN.md)

---

## Platform-Specific Guidance

### iOS/macOS Native Apps (UIKit/SwiftUI)

Use Xcode projects (`.xcodeproj`/`.xcworkspace`) instead of SwiftPM for apps with:
- Storyboards/XIBs
- Asset catalogs
- Core Data models
- App-specific configuration (entitlements, Info.plist)

**Build command:**
```bash
xcodebuild -scheme {{SCHEME_NAME}} -configuration Release -sdk iphoneos
```

**Test command:**
```bash
xcodebuild test -scheme {{SCHEME_NAME}} -destination 'platform=iOS Simulator,name=iPhone 15'
```

**Required frameworks:**
- UIKit (iOS/tvOS) or AppKit (macOS)
- SwiftUI (modern declarative UI)
- Combine (reactive programming)
- Foundation (base utilities)

### Cross-Platform Swift (CLI/Server/Library)

Use SwiftPM (`Package.swift`) for:
- Command-line tools
- Server-side Swift (Vapor, Hummingbird)
- Cross-platform libraries
- Linux deployment

**Platform-agnostic code:**
```swift
#if os(macOS)
import AppKit
#elseif os(Linux)
import Foundation
#endif
```

**Avoid platform-specific APIs:**
- Use Foundation instead of UIKit/AppKit when possible
- Test on both macOS and Linux in CI
- Use `#if` directives sparingly

---

## iOS Frameworks Quick Reference

| Framework | Purpose | Import |
|-----------|---------|--------|
| Foundation | Base utilities, JSON, networking | `import Foundation` |
| UIKit | iOS UI framework | `import UIKit` |
| SwiftUI | Declarative UI | `import SwiftUI` |
| Combine | Reactive programming | `import Combine` |
| CoreData | Persistence | `import CoreData` |
| CoreLocation | GPS/location | `import CoreLocation` |
| AVFoundation | Audio/video | `import AVFoundation` |
| Network | Low-level networking | `import Network` |

---

## Cross-Platform Considerations

### macOS (Intel + Apple Silicon)
```bash
# Build universal binary
swift build -c release --arch arm64 --arch x86_64
```

### Linux
```bash
# Install system dependencies (Ubuntu/Debian)
apt-get install -y libsqlite3-dev libssl-dev libz-dev

# Build
swift build -c release
```

### Windows
Swift on Windows is experimental. Use macOS or Linux for production builds.

---

## Verification Checklist

```markdown
## Swift Toolchain Verification - {{TASK_ID}}

### Installation
- [ ] swift installed: `swift --version` shows 5.9+
- [ ] SwiftPM available: `swift package --version`
- [ ] swiftlint installed (macOS): `swiftlint version`
- [ ] Xcode CLT installed (macOS): `xcode-select -p`

### Configuration
- [ ] .swift-format exists with EOA standard config
- [ ] .swiftlint.yml exists with EOA standard config
- [ ] Package.swift has swift-argument-parser (for CLI)
- [ ] Package.swift has swift-format plugin

### Verification Commands Pass
- [ ] `swift build` - compiles without errors
- [ ] `swift test` - all tests pass
- [ ] `swiftlint lint --strict` - no violations (macOS)
- [ ] `swift package plugin format --check` - formatting correct

### CI/CD
- [ ] .github/workflows/ci.yml exists
- [ ] Uses `swift-actions/setup-swift@v2`
- [ ] Matrix includes: ubuntu-latest, macos-latest
- [ ] Tests run on multiple Swift versions (5.9, 5.10)
- [ ] Lint and format jobs configured

### Platform-Specific
- [ ] If iOS/macOS app: uses Xcode project (not SwiftPM)
- [ ] If CLI/library: uses Package.swift
- [ ] Platform minimum versions declared in Package.swift
- [ ] Cross-platform code tested on Linux (if applicable)

### Code Quality
- [ ] No force unwrapping (`!`) in production code
- [ ] No force try (`try!`) in production code
- [ ] No `print()` for structured output (use Codable/Logger)
- [ ] Uses Codable for JSON serialization
- [ ] Uses ArgumentParser for CLI argument parsing

### EOA Compliance
- [ ] Labels configured in GitHub
- [ ] Branch follows convention: `feature/{{TASK_ID}}-*`
- [ ] Commits follow convention: `feat({{TASK_ID}}): *`
```

---

## Common Issues and Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| `xcode-select: error` | Xcode CLT not installed | Run `xcode-select --install` |
| `swiftly: command not found` | swiftly not in PATH (Linux) | Source: `source ~/.local/share/swiftly/env.sh` |
| `swiftlint: command not found` | SwiftLint not installed | `brew install swiftlint` (macOS only) |
| `Package.swift: error` | Swift version mismatch | Update `swift-tools-version` comment |
| `.build` permission denied | Cache corruption | `rm -rf .build && swift build` |
| Import not found | Missing dependency | Add to `dependencies` in Package.swift |
| Force unwrap in tests | Test code violation | Use `XCTUnwrap()` instead of `!` |

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
```

---

**Previous:** [Part 2 - Templates](./SWIFT_TOOLCHAIN-part2-templates.md)
