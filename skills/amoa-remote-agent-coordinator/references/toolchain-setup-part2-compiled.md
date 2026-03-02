# Toolchain Setup Part 2: Compiled Languages


## Contents

- [Purpose](#purpose)
- [Table of Contents](#table-of-contents)
  - [Part 1: Rust and Go](#part-1-rust-and-go)
  - [Part 2: Swift, C/C++, and Objective-C](#part-2-swift-cc-and-objective-c)
  - [Part 3: .NET and JVM Languages](#part-3-net-and-jvm-languages)
- [Related References](#related-references)
- [Quick Navigation by Use Case](#quick-navigation-by-use-case)

---

## Purpose

This reference provides toolchain setup instructions for compiled languages (Rust, Go, Swift, C/C++, Objective-C, C#, Java, Kotlin). Remote agents do NOT have access to this skill, so the orchestrator must provide ALL toolchain requirements explicitly in each task delegation message.

---

## Table of Contents

This document is split into multiple parts for easier consumption:

### Part 1: Rust and Go
**File**: [toolchain-setup-part2-compiled-part1-rust-go.md](./toolchain-setup-part2-compiled-part1-rust-go.md)

- 1.1 Rust Toolchain (cargo-based)
  - 1.1.1 Setup instructions (rustup installation)
  - 1.1.2 Required components (clippy, rustfmt, cargo-tarpaulin)
  - 1.1.3 Configuration files (Cargo.toml, clippy.toml)
  - 1.1.4 Verification commands (build, test, lint, format)
- 1.2 Go Toolchain
  - 1.2.1 Setup instructions (go installation on macOS/Linux)
  - 1.2.2 Required tools (golangci-lint)
  - 1.2.3 Configuration files (go.mod, .golangci.yml)
  - 1.2.4 Verification commands (build, test, lint, format, vet)

### Part 2: Swift, C/C++, and Objective-C
**File**: [toolchain-setup-part2-compiled-part2-swift-cpp-objc.md](./toolchain-setup-part2-compiled-part2-swift-cpp-objc.md)

- 2.1 Swift Toolchain
  - 2.1.1 Setup instructions (Xcode installation)
  - 2.1.2 Swift Package Manager usage
  - 2.1.3 Configuration files (Package.swift)
  - 2.1.4 Verification commands (build, test, format, lint)
- 2.2 C/C++ Toolchain
  - 2.2.1 Setup instructions (Xcode/GCC/Clang)
  - 2.2.2 CMake configuration (CMakeLists.txt)
  - 2.2.3 Build commands (configure, build, test, install)
  - 2.2.4 Linting (clang-tidy, cppcheck)
- 2.3 Objective-C Toolchain
  - 2.3.1 Setup instructions (Xcode)
  - 2.3.2 Build commands (xcodebuild)
  - 2.3.3 CocoaPods integration

### Part 3: .NET and JVM Languages
**File**: [toolchain-setup-part2-compiled-part3-dotnet-jvm.md](./toolchain-setup-part2-compiled-part3-dotnet-jvm.md)

- 3.1 C# Toolchain (.NET)
  - 3.1.1 Setup instructions (dotnet SDK)
  - 3.1.2 Project setup (console, classlib, xunit)
  - 3.1.3 Verification commands (restore, build, test, format)
- 3.2 Java Toolchain
  - 3.2.1 Setup instructions (SDKMAN, Gradle)
  - 3.2.2 Gradle configuration (build.gradle.kts)
  - 3.2.3 Verification commands
- 3.3 Kotlin Toolchain
  - 3.3.1 Setup instructions (SDKMAN)
  - 3.3.2 Gradle with Kotlin configuration
  - 3.3.3 Verification commands
- 3.4 Quick Reference Table (all compiled languages)

---

## Related References

- [Part 1: Core Setup and Interpreted Languages](./toolchain-setup-part1-core-interpreted.md) - Orchestrator setup, Python, JS/TS, Ruby, Bash
- [Part 3: Mobile/Cross-Platform](./toolchain-setup-part3-mobile-crossplatform.md) - Android, React Native, Blazor, Cross-Platform Matrix, Delegation Templates

---

## Quick Navigation by Use Case

| If you need to... | Read this part |
|-------------------|----------------|
| Set up Rust/Cargo project | Part 1: Rust section |
| Set up Go project | Part 1: Go section |
| Set up Swift/SPM project | Part 2: Swift section |
| Set up CMake/C++ project | Part 2: C/C++ section |
| Set up Xcode Objective-C project | Part 2: Objective-C section |
| Set up .NET/C# project | Part 3: C# section |
| Set up Java/Gradle project | Part 3: Java section |
| Set up Kotlin project | Part 3: Kotlin section |
| Quick command reference for all languages | Part 3: Quick Reference Table |
