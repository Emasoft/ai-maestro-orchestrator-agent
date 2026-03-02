# LSP Enforcement Checklist - Index


## Contents

- [Parts Overview](#parts-overview)
- [Quick Navigation by Task](#quick-navigation-by-task)
  - [Setting Up LSP](#setting-up-lsp)
  - [Installing Missing LSP Servers](#installing-missing-lsp-servers)
  - [Validating Agent Work](#validating-agent-work)
  - [Troubleshooting LSP Issues](#troubleshooting-lsp-issues)
  - [Enforcement Workflow](#enforcement-workflow)
- [Languages Covered](#languages-covered)

---

This checklist has been split into 3 parts for easier navigation and context efficiency.

## Parts Overview

| Part | File | Lines | Topics |
|------|------|-------|--------|
| 1 | [Setup and Core Remediation](lsp-enforcement-part1-setup-core-remediation.md) | ~350 | Preparation, verification, remediation for Python/TS/Rust/Go/Java/Kotlin/C++/C# |
| 2 | [Validation and General Troubleshooting](lsp-enforcement-part2-validation-general-troubleshooting.md) | ~400 | PHP/Ruby/HTML remediation, PR validation, enforcement, general troubleshooting |
| 3 | [Language-Specific Troubleshooting](lsp-enforcement-part3-language-troubleshooting.md) | ~380 | Go/Java/Kotlin/C++/C#/PHP/Ruby troubleshooting, cross-language issues |

## Quick Navigation by Task

### Setting Up LSP
- [Part 1: Preparation checklist](lsp-enforcement-part1-setup-core-remediation.md#when-preparing-to-assign-work-to-remote-agents)
- [Part 1: Verification checklist](lsp-enforcement-part1-setup-core-remediation.md#when-verifying-that-all-required-lsp-servers-are-installed)

### Installing Missing LSP Servers
- [Part 1: Core languages (Python/TS/Rust/Go/Java/Kotlin/C++/C#)](lsp-enforcement-part1-setup-core-remediation.md#when-lsp-verification-fails-for-any-language)
- [Part 2: Web languages (PHP/Ruby/HTML/CSS)](lsp-enforcement-part2-validation-general-troubleshooting.md#web-languages-remediation)

### Validating Agent Work
- [Part 2: LSP diagnostics check](lsp-enforcement-part2-validation-general-troubleshooting.md#when-validating-agents-work-before-pr-approval)
- [Part 2: Type safety verification](lsp-enforcement-part2-validation-general-troubleshooting.md#2-type-safety-verification)
- [Part 2: Quality gates](lsp-enforcement-part2-validation-general-troubleshooting.md#4-quality-gates)

### Troubleshooting LSP Issues
- [Part 2: General issues (server won't start, no diagnostics, performance)](lsp-enforcement-part2-validation-general-troubleshooting.md#when-lsp-features-fail-or-behave-unexpectedly)
- [Part 2: Python/TypeScript/Rust issues](lsp-enforcement-part2-validation-general-troubleshooting.md#language-specific-issues)
- [Part 3: Go/Java/Kotlin issues](lsp-enforcement-part3-language-troubleshooting.md#go-gopls-issues)
- [Part 3: C/C++/C# issues](lsp-enforcement-part3-language-troubleshooting.md#cc-clangd-issues)
- [Part 3: PHP/Ruby issues](lsp-enforcement-part3-language-troubleshooting.md#php-intelephense-issues)
- [Part 3: Cross-language issues](lsp-enforcement-part3-language-troubleshooting.md#cross-language-issues)

### Enforcement Workflow
- [Part 2: Enforcement requirements](lsp-enforcement-part2-validation-general-troubleshooting.md#when-enforcing-lsp-requirements-throughout-workflows)
- [Part 2: Rejection criteria](lsp-enforcement-part2-validation-general-troubleshooting.md#rejection-criteria)

## Languages Covered

All 11 languages supported by Claude Code LSP (December 2025):

| Language | LSP Server | Remediation | Troubleshooting |
|----------|-----------|-------------|-----------------|
| Python | pyright | [Part 1](lsp-enforcement-part1-setup-core-remediation.md#python-pyright-remediation) | [Part 2](lsp-enforcement-part2-validation-general-troubleshooting.md#python-pyright-issues) |
| TypeScript | typescript-language-server | [Part 1](lsp-enforcement-part1-setup-core-remediation.md#typescript-typescript-language-server-remediation) | [Part 2](lsp-enforcement-part2-validation-general-troubleshooting.md#typescript-issues) |
| Rust | rust-analyzer | [Part 1](lsp-enforcement-part1-setup-core-remediation.md#rust-rust-analyzer-remediation) | [Part 2](lsp-enforcement-part2-validation-general-troubleshooting.md#rust-rust-analyzer-issues) |
| Go | gopls | [Part 1](lsp-enforcement-part1-setup-core-remediation.md#go-gopls-remediation) | [Part 3](lsp-enforcement-part3-language-troubleshooting.md#go-gopls-issues) |
| Java | jdtls | [Part 1](lsp-enforcement-part1-setup-core-remediation.md#java-jdtls-remediation) | [Part 3](lsp-enforcement-part3-language-troubleshooting.md#java-jdtls-issues) |
| Kotlin | kotlin-language-server | [Part 1](lsp-enforcement-part1-setup-core-remediation.md#kotlin-kotlin-language-server-remediation) | [Part 3](lsp-enforcement-part3-language-troubleshooting.md#kotlin-issues) |
| C/C++ | clangd | [Part 1](lsp-enforcement-part1-setup-core-remediation.md#cc-clangd-remediation) | [Part 3](lsp-enforcement-part3-language-troubleshooting.md#cc-clangd-issues) |
| C# | OmniSharp/csharp-ls | [Part 1](lsp-enforcement-part1-setup-core-remediation.md#c-omnisharpcsharp-ls-remediation) | [Part 3](lsp-enforcement-part3-language-troubleshooting.md#c-omnisharp-issues) |
| PHP | Intelephense | [Part 2](lsp-enforcement-part2-validation-general-troubleshooting.md#php-intelephense-remediation) | [Part 3](lsp-enforcement-part3-language-troubleshooting.md#php-intelephense-issues) |
| Ruby | Solargraph | [Part 2](lsp-enforcement-part2-validation-general-troubleshooting.md#ruby-solargraph-remediation) | [Part 3](lsp-enforcement-part3-language-troubleshooting.md#ruby-solargraph-issues) |
| HTML/CSS | vscode-langservers-extracted | [Part 2](lsp-enforcement-part2-validation-general-troubleshooting.md#htmlcss-standalone-language-servers-remediation) | - |
