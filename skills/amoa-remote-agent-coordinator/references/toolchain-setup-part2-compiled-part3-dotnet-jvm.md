# Toolchain Setup Part 2 - Part 3: .NET and JVM Languages


## Contents

- [Purpose](#purpose)
- [Table of Contents](#table-of-contents)
- [3.1 C# Toolchain (.NET)](#31-c-toolchain-net)
  - [3.1.1 Setup Instructions for Remote Agent](#311-setup-instructions-for-remote-agent)
  - [3.1.2 Project Setup](#312-project-setup)
  - [3.1.3 Verification Commands](#313-verification-commands)
- [3.2 Java Toolchain](#32-java-toolchain)
  - [3.2.1 Setup Instructions for Remote Agent](#321-setup-instructions-for-remote-agent)
  - [3.2.2 Gradle Configuration](#322-gradle-configuration)
  - [3.2.3 Verification Commands](#323-verification-commands)
- [3.3 Kotlin Toolchain](#33-kotlin-toolchain)
  - [3.3.1 Setup Instructions for Remote Agent](#331-setup-instructions-for-remote-agent)
  - [3.3.2 Gradle with Kotlin](#332-gradle-with-kotlin)
  - [3.3.3 Verification Commands](#333-verification-commands)
- [3.4 Quick Reference Table](#34-quick-reference-table)
- [Related Parts](#related-parts)

---

## Purpose

This reference provides toolchain setup instructions for C# (.NET), Java, and Kotlin. Remote agents do NOT have access to this skill, so the orchestrator must provide ALL toolchain requirements explicitly in each task delegation message.

---

## Table of Contents

- 3.1 [C# Toolchain (.NET)](#31-c-toolchain-net)
  - 3.1.1 Setup instructions
  - 3.1.2 Project setup
  - 3.1.3 Verification commands
- 3.2 [Java Toolchain](#32-java-toolchain)
  - 3.2.1 Setup instructions
  - 3.2.2 Gradle configuration
  - 3.2.3 Verification commands
- 3.3 [Kotlin Toolchain](#33-kotlin-toolchain)
  - 3.3.1 Setup instructions
  - 3.3.2 Gradle with Kotlin
  - 3.3.3 Verification commands
- 3.4 [Quick Reference Table](#34-quick-reference-table)

---

## 3.1 C# Toolchain (.NET)

### 3.1.1 Setup Instructions for Remote Agent

```bash
# Install .NET SDK
# macOS:
brew install dotnet

# Linux:
wget https://dot.net/v1/dotnet-install.sh
chmod +x dotnet-install.sh
./dotnet-install.sh --channel 8.0

# Verify
dotnet --version
```

### 3.1.2 Project Setup

```bash
# Create new project
dotnet new console -n ProjectName
dotnet new classlib -n ProjectName.Lib
dotnet new xunit -n ProjectName.Tests

# Add to solution
dotnet new sln -n ProjectName
dotnet sln add ProjectName/ProjectName.csproj
dotnet sln add ProjectName.Tests/ProjectName.Tests.csproj
```

### 3.1.3 Verification Commands

```bash
# Restore dependencies
dotnet restore

# Build
dotnet build

# Test
dotnet test

# Format
dotnet format

# All checks
dotnet build && dotnet test
```

---

## 3.2 Java Toolchain

### 3.2.1 Setup Instructions for Remote Agent

```bash
# Install Java (SDKMAN recommended)
curl -s "https://get.sdkman.io" | bash
source ~/.sdkman/bin/sdkman-init.sh
sdk install java 21-tem

# Install Gradle
sdk install gradle

# Verify
java --version
gradle --version
```

### 3.2.2 Gradle Configuration

**build.gradle.kts**:
```kotlin
plugins {
    java
    application
}

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(21))
    }
}

repositories {
    mavenCentral()
}

dependencies {
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.0")
}

tasks.test {
    useJUnitPlatform()
}
```

### 3.2.3 Verification Commands

```bash
# Build
gradle build

# Test
gradle test

# Check (includes lint)
gradle check

# All
gradle clean build test
```

---

## 3.3 Kotlin Toolchain

### 3.3.1 Setup Instructions for Remote Agent

```bash
# Install Kotlin (via SDKMAN)
sdk install kotlin

# Verify
kotlin -version
kotlinc -version
```

### 3.3.2 Gradle with Kotlin

**build.gradle.kts**:
```kotlin
plugins {
    kotlin("jvm") version "1.9.22"
    application
}

kotlin {
    jvmToolchain(21)
}

dependencies {
    testImplementation(kotlin("test"))
}

tasks.test {
    useJUnitPlatform()
}
```

### 3.3.3 Verification Commands

```bash
# Build
gradle build

# Test
gradle test

# Lint (ktlint)
gradle ktlintCheck

# All
gradle clean build test
```

---

## 3.4 Quick Reference Table

| Language | Install | Build | Lint | Test | Format |
|----------|---------|-------|------|------|--------|
| Rust | `rustup` | `cargo build` | `cargo clippy -- -D warnings` | `cargo test` | `cargo fmt` |
| Go | `brew install go` | `go build ./...` | `golangci-lint run` | `go test ./...` | `go fmt ./...` |
| Swift | `xcode-select --install` | `swift build` | `swiftlint` | `swift test` | `swiftformat .` |
| C/C++ | `cmake + ninja` | `cmake --build build` | `clang-tidy src/*.cpp` | `ctest` | N/A |
| Obj-C | `xcode-select --install` | `xcodebuild build` | N/A | `xcodebuild test` | N/A |
| C# | `dotnet` | `dotnet build` | N/A | `dotnet test` | `dotnet format` |
| Java | `sdk install java` | `gradle build` | `gradle check` | `gradle test` | N/A |
| Kotlin | `sdk install kotlin` | `gradle build` | `gradle ktlintCheck` | `gradle test` | N/A |

---

## Related Parts

- [Index: Toolchain Setup Part 2](./toolchain-setup-part2-compiled.md) - Main index with all TOCs
- [Part 1: Rust and Go](./toolchain-setup-part2-compiled-part1-rust-go.md)
- [Part 2: Swift, C/C++, Objective-C](./toolchain-setup-part2-compiled-part2-swift-cpp-objc.md)
