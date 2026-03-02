# Toolchain Setup Part 3: Mobile/Cross-Platform and Templates


## Contents

- [Purpose](#purpose)
- [Table of Contents](#table-of-contents)
  - [Section 1: Mobile Platforms](#section-1-mobile-platforms)
  - [Section 2: Templates and Verification](#section-2-templates-and-verification)
- [Related References](#related-references)
- [Quick Summary](#quick-summary)
  - [When to Read Section 1 (Mobile Platforms)](#when-to-read-section-1-mobile-platforms)
  - [When to Read Section 2 (Templates and Verification)](#when-to-read-section-2-templates-and-verification)
- [Key Principle](#key-principle)

---

## Purpose

This reference provides toolchain setup instructions for mobile development (Android, React Native), cross-platform frameworks (Blazor), cross-compilation matrix, and delegation templates. Remote agents do NOT have access to this skill, so the orchestrator must provide ALL toolchain requirements explicitly in each task delegation message.

---

## Table of Contents

This document is split into sections for easier navigation:

### Section 1: Mobile Platforms
**File**: [toolchain-setup-part3-mobile-crossplatform-section1-mobile-platforms.md](./toolchain-setup-part3-mobile-crossplatform-section1-mobile-platforms.md)

Contents:
- 1. Android Toolchain
  - 1.1 Setup Instructions for Remote Agent
  - 1.2 Gradle Configuration
  - 1.3 Verification Commands
- 2. React Native Toolchain
  - 2.1 Setup Instructions for Remote Agent
  - 2.2 Project Setup
  - 2.3 Verification Commands
- 3. Blazor Toolchain
  - 3.1 Setup Instructions for Remote Agent
  - 3.2 Verification Commands
- 4. Cross-Platform Project Matrix
  - 4.1 Build Matrix Table
  - 4.2 Cross-Compilation Setup (Rust targets)
  - 4.3 Python Cross-Platform (wheels, cibuildwheel)
  - 4.4 Node.js Cross-Platform (pkg, nexe)

### Section 2: Templates and Verification
**File**: [toolchain-setup-part3-mobile-crossplatform-section2-templates-verification.md](./toolchain-setup-part3-mobile-crossplatform-section2-templates-verification.md)

Contents:
- 1. Delegation Template with Toolchain (Rust example)
- 2. Python Task Template
- 3. JavaScript/TypeScript Task Template
- 4. Toolchain Verification Script Generator
  - 4.1 Generic Verification Script Generator function
  - 4.2 Rust verification script
  - 4.3 Python verification script
  - 4.4 JavaScript/TypeScript verification script
  - 4.5 Go verification script
  - 4.6 Usage examples
- 5. Quick Reference: Delegation Checklist
  - 5.1 Required elements for every delegation
  - 5.2 Language quick reference table

---

## Related References

- [Part 1: Core Setup and Interpreted Languages](./toolchain-setup-part1-core-interpreted.md) - Orchestrator setup, Python, JS/TS, Ruby, Bash
- [Part 2: Compiled Languages](./toolchain-setup-part2-compiled.md) - Rust, Go, Swift, C/C++, Objective-C, C#, Java, Kotlin

---

## Quick Summary

### When to Read Section 1 (Mobile Platforms)

Read Section 1 when you need to:
- Set up Android development environment for a remote agent
- Configure React Native projects with iOS and Android support
- Work with Blazor WebAssembly or Server-side projects
- Cross-compile Rust, Python, or Node.js for multiple platforms

### When to Read Section 2 (Templates and Verification)

Read Section 2 when you need to:
- Create a task delegation message with proper toolchain requirements
- Generate a toolchain verification script for remote agents
- Reference the quick delegation checklist
- Look up verify/install/build/lint/test commands for any language

---

## Key Principle

**Remote agents do NOT have access to these skill documents.** The orchestrator must:

1. **Include toolchain verification commands** in every task delegation
2. **Provide installation instructions** for missing tools
3. **Specify exact verification commands** to run after implementation
4. **Define clear completion criteria** including required checks

Never assume the remote agent knows how to set up their environment. Always provide explicit instructions.
