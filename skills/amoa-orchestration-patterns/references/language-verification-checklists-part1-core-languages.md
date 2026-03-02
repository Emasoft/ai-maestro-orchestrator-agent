# Language-Specific Verification Checklists - Part 1: Core Languages


## Contents

- [Table of Contents](#table-of-contents)
- [Use-Case Quick Reference](#use-case-quick-reference)
- [Python Verification Checklist](#python-verification-checklist)
  - [Core Requirements](#core-requirements)
  - [Build and Distribution](#build-and-distribution)
  - [TDD Verification](#tdd-verification)
  - [Optional (Recommended)](#optional-recommended)
- [Go Verification Checklist](#go-verification-checklist)
  - [Core Requirements](#core-requirements)
  - [Build and Distribution](#build-and-distribution)
  - [TDD Verification](#tdd-verification)
  - [Optional (Recommended)](#optional-recommended)
- [JavaScript/TypeScript Verification Checklist](#javascripttypescript-verification-checklist)
  - [Core Requirements](#core-requirements)
  - [Package Management](#package-management)
  - [TDD Verification](#tdd-verification)
  - [Optional (Recommended)](#optional-recommended)
- [Rust Verification Checklist](#rust-verification-checklist)
  - [Core Requirements](#core-requirements)
  - [Build and Distribution](#build-and-distribution)
  - [TDD Verification](#tdd-verification)
  - [Optional (Recommended)](#optional-recommended)
- [Related Documents](#related-documents)

---

This document provides comprehensive verification checklists for core programming languages (Python, Go, JavaScript/TypeScript, Rust). Use these checklists to ensure code quality, build success, and release readiness before delegating tasks or accepting deliverables.

**Parent document:** [language-verification-checklists-index.md](./language-verification-checklists-index.md)

## Table of Contents

- [Use-Case Quick Reference](#use-case-quick-reference)
- [Python Verification Checklist](#python-verification-checklist)
  - Core Requirements
  - Build and Distribution
  - TDD Verification
  - Optional (Recommended)
- [Go Verification Checklist](#go-verification-checklist)
  - Core Requirements
  - Build and Distribution
  - TDD Verification
  - Optional (Recommended)
- [JavaScript/TypeScript Verification Checklist](#javascripttypescript-verification-checklist)
  - Core Requirements
  - Package Management
  - TDD Verification
  - Optional (Recommended)
- [Rust Verification Checklist](#rust-verification-checklist)
  - Core Requirements
  - Build and Distribution
  - TDD Verification
  - Optional (Recommended)

---

## Use-Case Quick Reference

**When to use this guide:**
- When verifying Python project quality → [Python Verification Checklist](#python-verification-checklist)
- If you need to validate Go builds → [Go Verification Checklist](#go-verification-checklist)
- When checking JavaScript/TypeScript quality → [JavaScript/TypeScript Verification Checklist](#javascripttypescript-verification-checklist)
- If Rust project needs validation → [Rust Verification Checklist](#rust-verification-checklist)
- When verifying Swift/iOS/macOS projects → See [Part 3: Swift and Universal](language-verification-checklists-part3-swift-and-universal.md)
- When verifying TDD compliance → See [Part 3: Universal TDD Verification](language-verification-checklists-part3-swift-and-universal.md#universal-tdd-verification)
- When delegating tasks and need quality requirements → See [Part 3: Usage in Orchestration](language-verification-checklists-part3-swift-and-universal.md#usage-in-orchestration)
- If mypy errors on third-party packages → See [Part 3: Troubleshooting](language-verification-checklists-part3-swift-and-universal.md#troubleshooting)
- When ESLint and Prettier conflict → See [Part 3: Troubleshooting](language-verification-checklists-part3-swift-and-universal.md#troubleshooting)
- If you need automation scripts for verification → See [Part 3: Automation Scripts](language-verification-checklists-part3-swift-and-universal.md#automation-scripts)
- For extended platforms (C#, Unity, Android, C++, Flutter, React Native, ML/AI, Embedded) → See [Part 2: Extended Platforms](language-verification-checklists-part2-extended-platforms.md)

---

## Python Verification Checklist

Use this checklist for Python projects, libraries, CLIs, and applications.

### Core Requirements
- [ ] **pyproject.toml** complete with all metadata
  - [ ] Project name, version, description
  - [ ] Authors and license
  - [ ] Dependencies with version constraints
  - [ ] Optional dependencies in extras
  - [ ] requires-python field specified
  - [ ] Build system configured (hatchling, setuptools, poetry)
- [ ] **Type hints** on all public functions and methods
  - [ ] Function signatures fully annotated
  - [ ] Return types specified
  - [ ] Complex types use typing module (List, Dict, Optional, Union, etc.)
- [ ] **mypy** passes with no errors
  - [ ] Run: `mypy src/ --strict` or `mypy src/`
  - [ ] Zero errors in output
  - [ ] mypy.ini or pyproject.toml configured
- [ ] **ruff check** passes
  - [ ] Run: `ruff check src/ tests/`
  - [ ] Zero violations
  - [ ] All rules enabled or explicitly excluded
- [ ] **ruff format** applied
  - [ ] Run: `ruff format src/ tests/`
  - [ ] All files formatted consistently
  - [ ] Line length configured (default 88 or custom)
- [ ] **pytest** passes with >80% coverage
  - [ ] Run: `pytest --cov=src --cov-report=term-missing`
  - [ ] All tests pass
  - [ ] Coverage >80% (ideally >90%)
  - [ ] Critical paths have tests
- [ ] **Python version** specified
  - [ ] requires-python in pyproject.toml
  - [ ] Compatible with target environments
- [ ] **Dependencies** pinned to compatible versions
  - [ ] Version constraints prevent breakage
  - [ ] No unbounded dependencies (avoid `package>=1.0`)
  - [ ] Lock file generated (requirements.txt, poetry.lock, uv.lock)
- [ ] **CLI entry point** defined (if CLI tool)
  - [ ] [project.scripts] section in pyproject.toml
  - [ ] Entry point tested manually
- [ ] **README.md** with installation and usage
  - [ ] Installation instructions
  - [ ] Usage examples
  - [ ] API documentation or links

### Build and Distribution
- [ ] **Build succeeds**: `uv build` or `python -m build`
- [ ] **Wheel created**: Check dist/ directory
- [ ] **Installation from wheel works**: `pip install dist/*.whl`

### TDD Verification
- [ ] RED commit exists with failing test
- [ ] GREEN commit exists with implementation
- [ ] RED commit precedes GREEN commit in history
- [ ] Test command passes after GREEN phase
- [ ] REFACTOR commits (if any) don't break tests

### Optional (Recommended)
- [ ] Pre-commit hooks configured
- [ ] GitHub Actions CI configured
- [ ] CHANGELOG.md maintained
- [ ] API documentation generated (Sphinx, mkdocs)

---

## Go Verification Checklist

Use this checklist for Go projects, CLIs, services, and libraries.

### Core Requirements
- [ ] **go.mod** with correct module path
  - [ ] Module path matches repository (github.com/user/repo)
  - [ ] Go version specified (go 1.21, go 1.22, etc.)
  - [ ] All dependencies listed
  - [ ] Indirect dependencies tracked
- [ ] **go build** succeeds for all target platforms
  - [ ] Run: `go build ./...`
  - [ ] Zero errors
  - [ ] Test cross-compilation: `GOOS=linux GOARCH=amd64 go build`
- [ ] **go test** passes with coverage
  - [ ] Run: `go test ./... -cover`
  - [ ] All tests pass
  - [ ] Coverage >80% for critical packages
  - [ ] Race detector passes: `go test -race ./...`
- [ ] **golangci-lint** passes
  - [ ] Run: `golangci-lint run`
  - [ ] Zero warnings or errors
  - [ ] .golangci.yml configured with strict rules
- [ ] **gofmt/goimports** applied
  - [ ] Run: `gofmt -s -w .` or `goimports -w .`
  - [ ] All files formatted
  - [ ] Imports organized
- [ ] **Cross-compilation** tested (GOOS/GOARCH)
  - [ ] Test builds for: linux/amd64, darwin/amd64, darwin/arm64, windows/amd64
  - [ ] Run: `GOOS=target GOARCH=arch go build`
- [ ] **goreleaser config** (if releasing binaries)
  - [ ] .goreleaser.yml configured
  - [ ] Test release: `goreleaser release --snapshot --clean`
  - [ ] Archives and checksums generated
- [ ] **README.md** with installation and usage
  - [ ] Installation instructions (go install, binary downloads)
  - [ ] Usage examples
  - [ ] API documentation or pkg.go.dev link

### Build and Distribution
- [ ] **Binary builds**: `go build -o bin/appname`
- [ ] **Binary runs**: `./bin/appname --help`
- [ ] **Install succeeds**: `go install ./...`

### TDD Verification
- [ ] RED commit exists with failing test
- [ ] GREEN commit exists with implementation
- [ ] RED commit precedes GREEN commit in history
- [ ] Test command passes after GREEN phase
- [ ] REFACTOR commits (if any) don't break tests

### Optional (Recommended)
- [ ] Makefile with common tasks
- [ ] GitHub Actions CI for multiple platforms
- [ ] Benchmark tests: `go test -bench=.`
- [ ] Module documentation in Go doc format

---

## JavaScript/TypeScript Verification Checklist

Use this checklist for JavaScript/TypeScript projects (Node.js, frontend, libraries).

### Core Requirements
- [ ] **package.json** complete
  - [ ] name, version, description
  - [ ] author, license
  - [ ] dependencies and devDependencies
  - [ ] scripts (build, test, lint, format)
  - [ ] main, module, types fields (if library)
  - [ ] engines specified (node version)
- [ ] **TypeScript strict mode** enabled
  - [ ] tsconfig.json has `"strict": true`
  - [ ] All compiler options configured
  - [ ] Include/exclude patterns set
- [ ] **tsc --noEmit** passes
  - [ ] Run: `tsc --noEmit`
  - [ ] Zero type errors
  - [ ] All .ts files type-safe
- [ ] **ESLint** passes
  - [ ] Run: `eslint src/ --ext .ts,.tsx,.js,.jsx`
  - [ ] Zero errors
  - [ ] .eslintrc configured with strict rules
- [ ] **Prettier** applied
  - [ ] Run: `prettier --write src/`
  - [ ] All files formatted
  - [ ] .prettierrc configured
- [ ] **vitest/jest** passes with coverage
  - [ ] Run: `vitest run --coverage` or `jest --coverage`
  - [ ] All tests pass
  - [ ] Coverage >80%
- [ ] **Build succeeds** (vite build, tsc)
  - [ ] Run: `npm run build` or `vite build` or `tsc`
  - [ ] dist/ or build/ directory created
  - [ ] No build errors
- [ ] **README.md** with installation and usage
  - [ ] Installation: `npm install package-name`
  - [ ] Usage examples
  - [ ] API documentation

### Package Management
- [ ] **pnpm** (preferred) or npm/yarn
  - [ ] pnpm-lock.yaml or package-lock.json committed
  - [ ] Dependencies installed: `pnpm install`
- [ ] **Peer dependencies** specified (if library)
- [ ] **Type definitions** included or referenced

### TDD Verification
- [ ] RED commit exists with failing test
- [ ] GREEN commit exists with implementation
- [ ] RED commit precedes GREEN commit in history
- [ ] Test command passes after GREEN phase
- [ ] REFACTOR commits (if any) don't break tests

### Optional (Recommended)
- [ ] Bundler configured (vite, webpack, rollup)
- [ ] GitHub Actions CI
- [ ] Husky pre-commit hooks
- [ ] Changeset or semantic-release configured

---

## Rust Verification Checklist

Use this checklist for Rust projects, CLIs, libraries, and services.

### Core Requirements
- [ ] **Cargo.toml** complete
  - [ ] [package] section with name, version, authors, edition
  - [ ] license, description, repository
  - [ ] [dependencies] with version constraints
  - [ ] [[bin]] sections for binaries
  - [ ] [lib] section for libraries
- [ ] **cargo build --release** succeeds
  - [ ] Run: `cargo build --release`
  - [ ] Zero errors
  - [ ] Binary in target/release/
- [ ] **cargo test** passes
  - [ ] Run: `cargo test`
  - [ ] All tests pass
  - [ ] Doc tests pass
  - [ ] Integration tests pass
- [ ] **cargo clippy** passes (no warnings)
  - [ ] Run: `cargo clippy -- -D warnings`
  - [ ] Zero warnings
  - [ ] All clippy lints satisfied
- [ ] **cargo fmt** applied
  - [ ] Run: `cargo fmt`
  - [ ] All files formatted
  - [ ] rustfmt.toml configured (optional)
- [ ] **Cross-compilation** tested
  - [ ] Install targets: `rustup target add x86_64-unknown-linux-gnu`
  - [ ] Build: `cargo build --target x86_64-unknown-linux-gnu`
  - [ ] Test common targets: linux, macOS, Windows
- [ ] **README.md** with installation and usage
  - [ ] Installation: `cargo install package-name`
  - [ ] Usage examples
  - [ ] Build instructions

### Build and Distribution
- [ ] **Optimized release build**: `cargo build --release`
- [ ] **Binary runs**: `./target/release/appname --help`
- [ ] **Crate publishes** (if library): `cargo publish --dry-run`

### TDD Verification
- [ ] RED commit exists with failing test
- [ ] GREEN commit exists with implementation
- [ ] RED commit precedes GREEN commit in history
- [ ] Test command passes after GREEN phase
- [ ] REFACTOR commits (if any) don't break tests

### Optional (Recommended)
- [ ] cargo-release for version management
- [ ] GitHub Actions CI for multiple platforms
- [ ] Benchmarks: `cargo bench`
- [ ] Documentation: `cargo doc --no-deps --open`

---

## Related Documents

- [Part 2: Extended Platforms](language-verification-checklists-part2-extended-platforms.md) - C#/.NET, Unity, Android, C/C++, Flutter, React Native, ML/AI, Embedded/IoT
- [Part 3: Swift and Universal](language-verification-checklists-part3-swift-and-universal.md) - Swift/iOS/macOS, TDD Verification, General Checklist, Automation Scripts, Troubleshooting
