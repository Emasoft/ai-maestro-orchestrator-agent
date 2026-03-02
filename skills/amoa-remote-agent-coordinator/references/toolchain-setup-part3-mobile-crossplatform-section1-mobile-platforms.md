# Toolchain Setup Part 3 Section 1: Mobile Platforms


## Contents

- [Purpose](#purpose)
- [Table of Contents](#table-of-contents)
- [1. Android Toolchain](#1-android-toolchain)
  - [Setup Instructions for Remote Agent](#setup-instructions-for-remote-agent)
  - [Gradle Configuration](#gradle-configuration)
  - [Verification Commands](#verification-commands)
- [2. React Native Toolchain](#2-react-native-toolchain)
  - [Setup Instructions for Remote Agent](#setup-instructions-for-remote-agent)
  - [Project Setup](#project-setup)
  - [Verification Commands](#verification-commands)
- [3. Blazor Toolchain](#3-blazor-toolchain)
  - [Setup Instructions for Remote Agent](#setup-instructions-for-remote-agent)
  - [Verification Commands](#verification-commands)
- [4. Cross-Platform Project Matrix](#4-cross-platform-project-matrix)
  - [Cross-Compilation Setup](#cross-compilation-setup)
  - [Python Cross-Platform](#python-cross-platform)
  - [Node.js Cross-Platform](#nodejs-cross-platform)
- [Related References](#related-references)

---

## Purpose

This section covers mobile development toolchains: Android, React Native, Blazor, and cross-platform build matrices. Remote agents do NOT have access to this skill, so the orchestrator must provide ALL toolchain requirements explicitly.

---

## Table of Contents

1. [Android Toolchain](#1-android-toolchain)
2. [React Native Toolchain](#2-react-native-toolchain)
3. [Blazor Toolchain](#3-blazor-toolchain)
4. [Cross-Platform Project Matrix](#4-cross-platform-project-matrix)

---

## 1. Android Toolchain

### Setup Instructions for Remote Agent

```bash
# Install Android Studio OR command line tools
# Download from: https://developer.android.com/studio

# Set environment variables
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools

# Accept licenses
yes | sdkmanager --licenses

# Install required SDK components
sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"
```

### Gradle Configuration

**build.gradle.kts** (app module):
```kotlin
plugins {
    id("com.android.application")
    kotlin("android")
}

android {
    namespace = "com.example.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.app"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
```

### Verification Commands

```bash
# Build debug APK
./gradlew assembleDebug

# Run tests
./gradlew test

# Lint
./gradlew lint

# All
./gradlew clean build test lint
```

---

## 2. React Native Toolchain

### Setup Instructions for Remote Agent

```bash
# Install Node.js (via bun or nvm)
curl -fsSL https://bun.sh/install | bash

# Install React Native CLI
bun add -g react-native-cli

# iOS (macOS only)
sudo gem install cocoapods

# Android (see Android Toolchain section)
```

### Project Setup

```bash
# Create new project
npx react-native init ProjectName --template react-native-template-typescript

# Install dependencies
cd ProjectName
bun install
cd ios && pod install && cd ..
```

### Verification Commands

```bash
# Type check
bun run tsc --noEmit

# Lint
bun run eslint src/

# Test
bun test

# Build iOS
npx react-native run-ios --configuration Release

# Build Android
npx react-native run-android --variant=release
```

---

## 3. Blazor Toolchain

### Setup Instructions for Remote Agent

```bash
# Install .NET SDK (see C# section in Part 2)
dotnet --version

# Create Blazor project
dotnet new blazorwasm -n ProjectName  # WebAssembly
# or
dotnet new blazorserver -n ProjectName  # Server-side
```

### Verification Commands

```bash
# Build
dotnet build

# Test
dotnet test

# Run
dotnet run

# Publish
dotnet publish -c Release
```

---

## 4. Cross-Platform Project Matrix

When delegating cross-platform projects, include this matrix in your task:

| Platform | Build Command | Test Command | Artifacts |
|----------|--------------|--------------|-----------|
| macOS-Intel | `cargo build --target x86_64-apple-darwin` | `cargo test` | `target/x86_64-apple-darwin/release/` |
| macOS-ARM | `cargo build --target aarch64-apple-darwin` | `cargo test` | `target/aarch64-apple-darwin/release/` |
| Windows | `cargo build --target x86_64-pc-windows-msvc` | `cargo test` | `target/x86_64-pc-windows-msvc/release/` |
| Linux-x64 | `cargo build --target x86_64-unknown-linux-gnu` | `cargo test` | `target/x86_64-unknown-linux-gnu/release/` |
| Linux-ARM | `cargo build --target aarch64-unknown-linux-gnu` | `cargo test` | `target/aarch64-unknown-linux-gnu/release/` |

### Cross-Compilation Setup

```bash
# Install cross-compilation targets
rustup target add x86_64-apple-darwin
rustup target add aarch64-apple-darwin
rustup target add x86_64-pc-windows-msvc
rustup target add x86_64-unknown-linux-gnu
rustup target add aarch64-unknown-linux-gnu

# Install cross (for Linux targets from macOS)
cargo install cross
```

### Python Cross-Platform

```bash
# Build wheels for multiple platforms
uv pip install build
python -m build

# For binary extensions, use cibuildwheel
uv pip install cibuildwheel
cibuildwheel --output-dir dist
```

### Node.js Cross-Platform

```bash
# Build for multiple platforms with pkg
bun add -g pkg
pkg . --targets node18-linux-x64,node18-macos-x64,node18-win-x64

# Or use nexe
bun add -g nexe
nexe src/index.js --target linux-x64
```

---

## Related References

- [Part 3 Index](./toolchain-setup-part3-mobile-crossplatform.md) - Main index for mobile/cross-platform
- [Part 3 Section 2](./toolchain-setup-part3-mobile-crossplatform-section2-templates-verification.md) - Templates and verification scripts
- [Part 1](./toolchain-setup-part1-core-interpreted.md) - Core setup, Python, JS/TS, Ruby, Bash
- [Part 2](./toolchain-setup-part2-compiled.md) - Rust, Go, Swift, C/C++, Objective-C, C#, Java, Kotlin
