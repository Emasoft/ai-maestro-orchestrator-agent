# Toolchain Setup Part 2 - Part 2: Swift, C/C++, and Objective-C


## Contents

- [Purpose](#purpose)
- [Table of Contents](#table-of-contents)
- [2.1 Swift Toolchain](#21-swift-toolchain)
  - [2.1.1 Setup Instructions for Remote Agent](#211-setup-instructions-for-remote-agent)
  - [2.1.2 Swift Package Manager](#212-swift-package-manager)
  - [2.1.3 Configuration Files](#213-configuration-files)
  - [2.1.4 Verification Commands](#214-verification-commands)
- [2.2 C/C++ Toolchain](#22-cc-toolchain)
  - [2.2.1 Setup Instructions for Remote Agent](#221-setup-instructions-for-remote-agent)
  - [2.2.2 CMake Configuration](#222-cmake-configuration)
  - [2.2.3 Build Commands](#223-build-commands)
  - [2.2.4 Linting](#224-linting)
- [2.3 Objective-C Toolchain](#23-objective-c-toolchain)
  - [2.3.1 Setup Instructions for Remote Agent](#231-setup-instructions-for-remote-agent)
  - [2.3.2 Build Commands](#232-build-commands)
  - [2.3.3 CocoaPods (if needed)](#233-cocoapods-if-needed)
- [Related Parts](#related-parts)

---

## Purpose

This reference provides toolchain setup instructions for Swift, C/C++, and Objective-C. Remote agents do NOT have access to this skill, so the orchestrator must provide ALL toolchain requirements explicitly in each task delegation message.

---

## Table of Contents

- 2.1 [Swift Toolchain](#21-swift-toolchain)
  - 2.1.1 Setup instructions
  - 2.1.2 Swift Package Manager
  - 2.1.3 Configuration files
  - 2.1.4 Verification commands
- 2.2 [C/C++ Toolchain](#22-cc-toolchain)
  - 2.2.1 Setup instructions
  - 2.2.2 CMake configuration
  - 2.2.3 Build commands
  - 2.2.4 Linting
- 2.3 [Objective-C Toolchain](#23-objective-c-toolchain)
  - 2.3.1 Setup instructions
  - 2.3.2 Build commands
  - 2.3.3 CocoaPods integration

---

## 2.1 Swift Toolchain

### 2.1.1 Setup Instructions for Remote Agent

```bash
# Swift is included with Xcode on macOS
xcode-select --install

# Verify installation
swift --version
```

### 2.1.2 Swift Package Manager

```bash
# Initialize package
swift package init --type executable  # or --type library

# Build
swift build

# Test
swift test
```

### 2.1.3 Configuration Files

**Package.swift**:
```swift
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "ProjectName",
    platforms: [.macOS(.v13), .iOS(.v16)],
    products: [
        .library(name: "ProjectName", targets: ["ProjectName"]),
    ],
    dependencies: [],
    targets: [
        .target(name: "ProjectName", dependencies: []),
        .testTarget(name: "ProjectNameTests", dependencies: ["ProjectName"]),
    ]
)
```

### 2.1.4 Verification Commands

```bash
# Build
swift build

# Test
swift test

# Format (SwiftFormat)
brew install swiftformat
swiftformat .

# Lint (SwiftLint)
brew install swiftlint
swiftlint

# All checks
swift build && swift test && swiftlint
```

---

## 2.2 C/C++ Toolchain

### 2.2.1 Setup Instructions for Remote Agent

```bash
# macOS (Xcode command line tools)
xcode-select --install

# Linux (GCC/Clang)
sudo apt install build-essential cmake ninja-build

# Verify
cmake --version
ninja --version
clang++ --version  # or g++ --version
```

### 2.2.2 CMake Configuration

**CMakeLists.txt** (minimal):
```cmake
cmake_minimum_required(VERSION 3.20)
project(ProjectName VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_executable(${PROJECT_NAME} src/main.cpp)

# Testing with CTest
enable_testing()
add_subdirectory(tests)
```

### 2.2.3 Build Commands

```bash
# Configure
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release

# Build
cmake --build build

# Test
ctest --test-dir build --output-on-failure

# Install (optional)
cmake --install build --prefix ./install
```

### 2.2.4 Linting

```bash
# clang-tidy
brew install llvm  # includes clang-tidy
clang-tidy src/*.cpp -- -std=c++20

# cppcheck
brew install cppcheck
cppcheck --enable=all src/
```

---

## 2.3 Objective-C Toolchain

### 2.3.1 Setup Instructions for Remote Agent

```bash
# Requires Xcode on macOS
xcode-select --install

# Verify
clang --version
```

### 2.3.2 Build Commands

```bash
# With Xcode project
xcodebuild -project Project.xcodeproj -scheme ProjectScheme build

# With workspace
xcodebuild -workspace Project.xcworkspace -scheme ProjectScheme build

# Clean build
xcodebuild clean build
```

### 2.3.3 CocoaPods (if needed)

```bash
# Install CocoaPods
sudo gem install cocoapods

# Install dependencies
pod install

# Build with workspace
xcodebuild -workspace Project.xcworkspace -scheme ProjectScheme build
```

---

## Related Parts

- [Index: Toolchain Setup Part 2](./toolchain-setup-part2-compiled.md) - Main index with all TOCs
- [Part 1: Rust and Go](./toolchain-setup-part2-compiled-part1-rust-go.md)
- [Part 3: .NET and JVM Languages](./toolchain-setup-part2-compiled-part3-dotnet-jvm.md)
