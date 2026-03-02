# Swift Toolchain - Part 2: Templates

**Parent Document:** [SWIFT_TOOLCHAIN.md](./SWIFT_TOOLCHAIN.md)

---

## Package.swift Template

```swift
// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "{{PROJECT_NAME}}",
    platforms: [
        .macOS(.v13),    // macOS Ventura+
        .iOS(.v16),      // iOS 16+
        .watchOS(.v9),   // watchOS 9+
        .tvOS(.v16)      // tvOS 16+
    ],
    products: [
        // Products define the executables and libraries a package produces, making them visible to other packages.
        .library(
            name: "{{PROJECT_NAME}}",
            targets: ["{{PROJECT_NAME}}"]),
        .executable(
            name: "{{PROJECT_NAME}}-cli",
            targets: ["{{PROJECT_NAME}}CLI"]),
    ],
    dependencies: [
        // Dependencies declare other packages that this package depends on.

        // JSON serialization (Foundation/Codable is built-in, no external dep needed)

        // CLI argument parsing (MANDATORY for CLI apps)
        .package(url: "https://github.com/apple/swift-argument-parser.git", from: "1.3.0"),

        // Code formatting plugin
        .package(url: "https://github.com/apple/swift-format.git", from: "509.0.0"),

        // Logging
        .package(url: "https://github.com/apple/swift-log.git", from: "1.5.0"),

        // Testing utilities (optional)
        // .package(url: "https://github.com/pointfreeco/swift-snapshot-testing.git", from: "1.15.0"),
    ],
    targets: [
        // Targets are the basic building blocks of a package, defining a module or a test suite.
        // Targets can depend on other targets in this package and products from dependencies.
        .target(
            name: "{{PROJECT_NAME}}",
            dependencies: [
                .product(name: "Logging", package: "swift-log"),
            ]),
        .executableTarget(
            name: "{{PROJECT_NAME}}CLI",
            dependencies: [
                "{{PROJECT_NAME}}",
                .product(name: "ArgumentParser", package: "swift-argument-parser"),
            ]),
        .testTarget(
            name: "{{PROJECT_NAME}}Tests",
            dependencies: ["{{PROJECT_NAME}}"]),
    ]
)
```

---

## GitHub Actions CI Template

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  SWIFT_VERSION: "5.9"

jobs:
  build:
    name: Build and Test
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest]
        swift: ["5.9", "5.10"]

    steps:
      - uses: actions/checkout@v4

      - name: Setup Swift
        uses: swift-actions/setup-swift@v2
        with:
          swift-version: ${{ matrix.swift }}

      - name: Cache SwiftPM
        uses: actions/cache@v4
        with:
          path: .build
          key: ${{ runner.os }}-spm-${{ hashFiles('**/Package.resolved') }}
          restore-keys: |
            ${{ runner.os }}-spm-

      - name: Resolve dependencies
        run: swift package resolve

      - name: Build
        run: swift build --verbose

      - name: Run tests
        run: swift test --parallel --verbose

  lint:
    name: Lint
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Swift
        uses: swift-actions/setup-swift@v2
        with:
          swift-version: "5.9"

      - name: Install SwiftLint
        run: brew install swiftlint

      - name: Run SwiftLint
        run: swiftlint lint --strict

  format:
    name: Format Check
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Swift
        uses: swift-actions/setup-swift@v2
        with:
          swift-version: "5.9"

      - name: Check formatting
        run: |
          swift package plugin --allow-writing-to-package-directory format --lint
          git diff --exit-code

  coverage:
    name: Code Coverage
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Swift
        uses: swift-actions/setup-swift@v2
        with:
          swift-version: "5.9"

      - name: Run tests with coverage
        run: swift test --enable-code-coverage

      - name: Generate coverage report
        run: |
          xcrun llvm-cov export \
            .build/debug/{{PROJECT_NAME}}PackageTests.xctest/Contents/MacOS/{{PROJECT_NAME}}PackageTests \
            -instr-profile .build/debug/codecov/default.profdata \
            -format="lcov" > coverage.lcov

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: coverage.lcov
```

---

## Library Requirements (MANDATORY)

| Purpose | Library | Usage |
|---------|---------|-------|
| JSON | Foundation/Codable (built-in) | `JSONEncoder()`, `JSONDecoder()` |
| CLI | swift-argument-parser | `@main struct CLI: ParsableCommand` |
| HTTP | URLSession (built-in) | `URLSession.shared.data(from:)` |
| Async | Swift Concurrency (built-in) | `async`/`await`, `Task` |
| Logging | swift-log | `Logger(label: "com.example.app")` |
| File I/O | Foundation (built-in) | `FileManager`, `Data`, `String` |

**VIOLATIONS (will fail review):**
- Force unwrapping (`!`) in production code
- Force try (`try!`) in production code
- `print()` for structured output (use `JSONEncoder` or `Logger`)
- Implicitly unwrapped optionals (`T!`) except for IBOutlets
- Manual JSON string formatting instead of Codable
- Manual argument parsing without ArgumentParser (for CLI apps)

---

**Previous:** [Part 1 - Setup](./SWIFT_TOOLCHAIN-part1-setup.md)
**Next:** [Part 3 - Platform Guide](./SWIFT_TOOLCHAIN-part3-platform.md)
