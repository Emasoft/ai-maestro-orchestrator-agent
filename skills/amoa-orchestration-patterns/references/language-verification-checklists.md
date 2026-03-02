# Language-Specific Verification Checklists


## Contents

- [Quick Navigation](#quick-navigation)
- [Cross-Language Resources](#cross-language-resources)
- [Documents](#documents)
  - [Part 1: Core Languages](#part-1-core-languages)
  - [Part 2: Extended Platforms](#part-2-extended-platforms)
  - [Part 3: Swift and Universal Resources](#part-3-swift-and-universal-resources)
- [When to Use Each Checklist](#when-to-use-each-checklist)

---

This document has been split into multiple parts for easier navigation. Use the index below to find the checklist you need.

## Quick Navigation

| Language/Platform | Document |
|-------------------|----------|
| Python | [Part 1](language-verification-checklists-part1-core-languages.md#python-verification-checklist) |
| Go | [Part 1](language-verification-checklists-part1-core-languages.md#go-verification-checklist) |
| JavaScript/TypeScript | [Part 1](language-verification-checklists-part1-core-languages.md#javascripttypescript-verification-checklist) |
| Rust | [Part 1](language-verification-checklists-part1-core-languages.md#rust-verification-checklist) |
| Swift/iOS/macOS | [Part 3](language-verification-checklists-part3-swift-and-universal.md#swiftiosmacos-verification-checklist) |
| C#/.NET | [Part 2](language-verification-checklists-part2-extended-platforms.md#cnet-verification-checklist) |
| Unity | [Part 2](language-verification-checklists-part2-extended-platforms.md#unity-verification-checklist) |
| Android | [Part 2](language-verification-checklists-part2-extended-platforms.md#android-verification-checklist) |
| C/C++ | [Part 2](language-verification-checklists-part2-extended-platforms.md#cc-verification-checklist) |
| Flutter | [Part 2](language-verification-checklists-part2-extended-platforms.md#flutter-verification-checklist) |
| React Native | [Part 2](language-verification-checklists-part2-extended-platforms.md#react-native-verification-checklist) |
| ML/AI (PyTorch, HuggingFace) | [Part 2](language-verification-checklists-part2-extended-platforms.md#mlai-verification-checklist-pytorch-huggingface) |
| Embedded/IoT | [Part 2](language-verification-checklists-part2-extended-platforms.md#embeddediot-verification-checklist) |

## Cross-Language Resources

| Resource | Document |
|----------|----------|
| Universal TDD Verification | [Part 3](language-verification-checklists-part3-swift-and-universal.md#universal-tdd-verification) |
| General Cross-Language Checklist | [Part 3](language-verification-checklists-part3-swift-and-universal.md#general-cross-language-checklist) |
| Usage in Orchestration | [Part 3](language-verification-checklists-part3-swift-and-universal.md#usage-in-orchestration) |
| Automation Scripts | [Part 3](language-verification-checklists-part3-swift-and-universal.md#automation-scripts) |
| Troubleshooting | [Part 3](language-verification-checklists-part3-swift-and-universal.md#troubleshooting) |

## Documents

### Part 1: Core Languages
**File**: [language-verification-checklists-part1-core-languages.md](language-verification-checklists-part1-core-languages.md)

**Contents**:
- Python Verification Checklist
- Go Verification Checklist
- JavaScript/TypeScript Verification Checklist
- Rust Verification Checklist

### Part 2: Extended Platforms
**File**: [language-verification-checklists-part2-extended-platforms.md](language-verification-checklists-part2-extended-platforms.md)

**Contents**:
- C#/.NET Verification Checklist
- Unity Verification Checklist
- Android Verification Checklist (Kotlin, Jetpack Compose)
- C/C++ Verification Checklist (CMake)
- Flutter Verification Checklist
- React Native Verification Checklist
- ML/AI Verification Checklist (PyTorch, HuggingFace)
- Embedded/IoT Verification Checklist
- How to extend this document with new languages

### Part 3: Swift and Universal Resources
**File**: [language-verification-checklists-part3-swift-and-universal.md](language-verification-checklists-part3-swift-and-universal.md)

**Contents**:
- Swift/iOS/macOS Verification Checklist
- Universal TDD Verification
- General Cross-Language Checklist
- Usage in Orchestration (delegating, reviewing, creating projects)
- Automation Scripts (Python, Go, JS/TS)
- Troubleshooting common issues

## When to Use Each Checklist

**Use Part 1 when:**
- Working with mainstream backend/system languages (Python, Go, Rust)
- Developing web applications (JavaScript/TypeScript)

**Use Part 2 when:**
- Working with Microsoft ecosystem (C#/.NET)
- Developing games (Unity)
- Building Android mobile apps (Kotlin, Compose)
- Working with systems programming (C/C++)
- Building cross-platform mobile apps (Flutter, React Native)
- Working on machine learning projects (PyTorch, HuggingFace)
- Developing for embedded systems (Arduino, PlatformIO)

**Use Part 3 when:**
- Building Apple ecosystem apps (Swift/iOS/macOS)
- Need TDD verification across any language
- Delegating tasks to agents and need quality gates
- Setting up automation scripts for verification
- Troubleshooting common verification issues
