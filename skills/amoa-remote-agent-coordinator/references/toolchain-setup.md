# Toolchain Setup Reference Index


## Contents

- [Purpose](#purpose)
- [Document Structure](#document-structure)
- [Part 1: Core Setup and Interpreted Languages](#part-1-core-setup-and-interpreted-languages)
  - [Contents](#contents)
  - [When to Read Part 1](#when-to-read-part-1)
- [Part 2: Compiled Languages](#part-2-compiled-languages)
  - [Contents](#contents)
  - [When to Read Part 2](#when-to-read-part-2)
- [Part 3: Mobile/Cross-Platform and Templates](#part-3-mobilecross-platform-and-templates)
  - [Contents](#contents)
  - [When to Read Part 3](#when-to-read-part-3)
- [Quick Language Lookup](#quick-language-lookup)
- [Usage Pattern](#usage-pattern)

---

## Purpose

This index provides navigation to all toolchain setup documentation. The original monolithic document has been split into three focused parts for easier consumption and faster loading.

---

## Document Structure

| Part | Focus Area | Lines | File |
|------|------------|-------|------|
| 1 | Core Setup and Interpreted Languages | ~280 | [toolchain-setup-part1-core-interpreted.md](./toolchain-setup-part1-core-interpreted.md) |
| 2 | Compiled Languages | ~330 | [toolchain-setup-part2-compiled.md](./toolchain-setup-part2-compiled.md) |
| 3 | Mobile/Cross-Platform and Templates | ~350 | [toolchain-setup-part3-mobile-crossplatform.md](./toolchain-setup-part3-mobile-crossplatform.md) |

---

## Part 1: Core Setup and Interpreted Languages

**File**: [toolchain-setup-part1-core-interpreted.md](./toolchain-setup-part1-core-interpreted.md)

### Contents

1. **Orchestrator Self-Setup** - Tools the orchestrator needs locally
2. **Toolchain Selection by Language** - Quick reference for all language preferences
3. **Python Toolchain (uv-based)** - Setup, configuration, verification
4. **JavaScript/TypeScript Toolchain (bun-based)** - Setup, configuration, verification
5. **Ruby Toolchain** - Setup with bundler, verification
6. **Bash/Shell Toolchain** - shellcheck, shfmt, verification

### When to Read Part 1

- Setting up orchestrator environment
- Delegating Python, JavaScript, TypeScript, Ruby, or Bash tasks
- Quick reference for language toolchain preferences

---

## Part 2: Compiled Languages

**File**: [toolchain-setup-part2-compiled.md](./toolchain-setup-part2-compiled.md)

### Contents

1. **Rust Toolchain (cargo-based)** - rustup, clippy, rustfmt
2. **Go Toolchain** - go mod, golangci-lint
3. **Swift Toolchain** - Swift Package Manager, SwiftLint
4. **C/C++ Toolchain** - CMake, Ninja, clang-tidy
5. **Objective-C Toolchain** - Xcode, CocoaPods
6. **C# Toolchain (.NET)** - dotnet CLI
7. **Java Toolchain** - SDKMAN, Gradle
8. **Kotlin Toolchain** - Gradle with Kotlin DSL

### When to Read Part 2

- Delegating Rust, Go, Swift, C, C++, Objective-C, C#, Java, or Kotlin tasks
- Setting up compiled language build pipelines
- Configuring linting for compiled languages

---

## Part 3: Mobile/Cross-Platform and Templates

**File**: [toolchain-setup-part3-mobile-crossplatform.md](./toolchain-setup-part3-mobile-crossplatform.md)

### Contents

1. **Android Toolchain** - SDK Manager, Gradle configuration
2. **React Native Toolchain** - iOS and Android setup
3. **Blazor Toolchain** - .NET WebAssembly and Server
4. **Cross-Platform Project Matrix** - Build targets and commands
5. **Delegation Template with Toolchain** - Copy-paste templates
6. **Toolchain Verification Script** - Scripts to verify agent toolchains

### When to Read Part 3

- Delegating mobile development tasks
- Setting up cross-platform builds
- Need delegation templates with toolchain requirements
- Want to generate toolchain verification scripts

---

## Quick Language Lookup

| Language | Part | Section |
|----------|------|---------|
| Python | 1 | Section 3 |
| JavaScript/TypeScript | 1 | Section 4 |
| Ruby | 1 | Section 5 |
| Bash/Shell | 1 | Section 6 |
| Rust | 2 | Section 1 |
| Go | 2 | Section 2 |
| Swift | 2 | Section 3 |
| C/C++ | 2 | Section 4 |
| Objective-C | 2 | Section 5 |
| C# (.NET) | 2 | Section 6 |
| Java | 2 | Section 7 |
| Kotlin | 2 | Section 8 |
| Android | 3 | Section 1 |
| React Native | 3 | Section 2 |
| Blazor | 3 | Section 3 |

---

## Usage Pattern

1. **Check the language** you need to delegate
2. **Open the appropriate part** based on the lookup table
3. **Copy the setup instructions** into your delegation message
4. **Include verification commands** from the same section
5. **Use templates from Part 3** if you want a complete delegation format
