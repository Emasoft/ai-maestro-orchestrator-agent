# Language-Specific Verification Checklists - Part 3: Swift and Universal Resources


## Contents

- [Table of Contents](#table-of-contents)
- [Swift/iOS/macOS Verification Checklist](#swiftiosmacos-verification-checklist)
  - [Core Requirements](#core-requirements)
  - [Swift Package Manager (SPM)](#swift-package-manager-spm)
  - [Optional (Recommended)](#optional-recommended)
- [Universal TDD Verification](#universal-tdd-verification)
  - [Check Commit Sequence](#check-commit-sequence)
  - [TDD Compliance Report](#tdd-compliance-report)
- [General Cross-Language Checklist](#general-cross-language-checklist)
- [Usage in Orchestration](#usage-in-orchestration)
  - [When Delegating Tasks](#when-delegating-tasks)
  - [When Reviewing Deliverables](#when-reviewing-deliverables)
  - [When Creating New Projects](#when-creating-new-projects)
- [Automation Scripts](#automation-scripts)
  - [Python](#python)
  - [Go](#go)
  - [JavaScript/TypeScript](#javascripttypescript)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Verification Failures](#verification-failures)
- [Related Documents](#related-documents)

---

This document provides the Swift/iOS/macOS verification checklist and universal resources applicable to all languages.

**Parent document:** [language-verification-checklists-index.md](./language-verification-checklists-index.md)

## Table of Contents

- [Swift/iOS/macOS Verification Checklist](#swiftiosmacos-verification-checklist)
  - Core Requirements
  - Swift Package Manager (SPM)
  - Optional (Recommended)
- [Universal TDD Verification](#universal-tdd-verification)
  - Check Commit Sequence
  - TDD Compliance Report
- [General Cross-Language Checklist](#general-cross-language-checklist)
- [Usage in Orchestration](#usage-in-orchestration)
  - When Delegating Tasks
  - When Reviewing Deliverables
  - When Creating New Projects
- [Automation Scripts](#automation-scripts)
- [Troubleshooting](#troubleshooting)

---

## Swift/iOS/macOS Verification Checklist

Use this checklist for Swift projects (iOS apps, macOS apps, SPM packages).

### Core Requirements
- [ ] **Xcode project** builds
  - [ ] Open .xcodeproj or .xcworkspace
  - [ ] Select scheme
  - [ ] Build (Cmd+B) succeeds
  - [ ] Zero warnings (fix or suppress intentionally)
- [ ] **All tests** pass
  - [ ] Run tests (Cmd+U)
  - [ ] XCTest unit tests pass
  - [ ] UI tests pass (if applicable)
  - [ ] Code coverage >80%
- [ ] **SwiftLint** passes
  - [ ] Install: `brew install swiftlint`
  - [ ] Run: `swiftlint` in project root
  - [ ] Zero violations
  - [ ] .swiftlint.yml configured
- [ ] **Code signing** configured
  - [ ] Team selected
  - [ ] Provisioning profiles configured
  - [ ] Capabilities enabled (if needed)
  - [ ] Signing certificate valid
- [ ] **README.md** with requirements
  - [ ] Xcode version requirement
  - [ ] iOS/macOS deployment target
  - [ ] Installation/setup instructions
  - [ ] Build and run instructions

### Swift Package Manager (SPM)
- [ ] **Package.swift** complete (if SPM package)
  - [ ] Platforms specified
  - [ ] Products defined (library, executable)
  - [ ] Dependencies listed
  - [ ] Targets configured
- [ ] **swift build** succeeds
  - [ ] Run: `swift build`
  - [ ] Zero errors
- [ ] **swift test** passes
  - [ ] Run: `swift test`
  - [ ] All tests pass

### Optional (Recommended)
- [ ] SwiftFormat applied
- [ ] GitHub Actions CI (macOS runner)
- [ ] Fastlane configured (for apps)
- [ ] App Store Connect metadata (for release)

---

## Universal TDD Verification

Use these commands to verify TDD compliance across all languages.

### Check Commit Sequence
```bash
# Verify TDD commits exist in correct order
git log --oneline --grep="^RED:" --grep="^GREEN:" --all-match

# List all TDD-related commits
git log --oneline | grep -E "^[a-f0-9]+ (RED|GREEN|REFACTOR):"

# Verify RED comes before GREEN
git log --oneline --reverse | grep -E "(RED|GREEN):" | head -5
```

### TDD Compliance Report
```bash
# Count TDD commits
echo "RED commits: $(git log --oneline --grep='^RED:' | wc -l)"
echo "GREEN commits: $(git log --oneline --grep='^GREEN:' | wc -l)"
echo "REFACTOR commits: $(git log --oneline --grep='^REFACTOR:' | wc -l)"
```

---

## General Cross-Language Checklist

Use this for all projects regardless of language.

- [ ] **Git repository** initialized
  - [ ] .gitignore configured for language
  - [ ] All files tracked or ignored appropriately
- [ ] **README.md** complete
  - [ ] Project description
  - [ ] Installation instructions
  - [ ] Usage examples
  - [ ] Contributing guidelines (if open source)
- [ ] **LICENSE** file present
  - [ ] MIT, Apache-2.0, GPL, or other
- [ ] **CI/CD** configured
  - [ ] GitHub Actions, GitLab CI, or other
  - [ ] Tests run on push/PR
  - [ ] Multi-platform testing (if applicable)
- [ ] **Versioning** scheme followed
  - [ ] SemVer (1.0.0, 1.1.0, 2.0.0)
  - [ ] Version bumped appropriately
- [ ] **CHANGELOG.md** updated
  - [ ] New version entry
  - [ ] Changes documented
- [ ] **Security** considerations
  - [ ] No secrets in code
  - [ ] Dependencies scanned (Dependabot, Snyk)
  - [ ] Security policies documented

---

## Usage in Orchestration

### When Delegating Tasks
Include the relevant checklist in your delegation prompt:

```
Before reporting completion, verify your work against the Python Verification Checklist:
[paste checklist here]

Report back with:
[DONE] task_name - all checklist items verified
or
[FAILED] task_name - checklist items failed: [list items]
```

### When Reviewing Deliverables
Use the checklist to audit agent work:

1. Read the checklist for the language
2. Run each verification command
3. Document any failures
4. Request fixes or re-delegate

### When Creating New Projects
Use the checklist as a project template:

1. Initialize project structure
2. Configure tools (linters, formatters, tests)
3. Verify all checklist items pass on empty project
4. Begin development

---

## Automation Scripts

Consider creating automation scripts in `scripts/` for common verification tasks:

### Python
```bash
#!/bin/bash
# verify-python.sh
set -e
mypy src/ --strict
ruff check src/ tests/
ruff format --check src/ tests/
pytest --cov=src --cov-report=term-missing --cov-fail-under=80
echo "All Python verifications passed"
```

### Go
```bash
#!/bin/bash
# verify-go.sh
set -e
go test ./... -race -cover
golangci-lint run
gofmt -l . | grep . && exit 1 || echo "All Go verifications passed"
```

### JavaScript/TypeScript
```bash
#!/bin/bash
# verify-js.sh
set -e
tsc --noEmit
eslint src/ --ext .ts,.tsx,.js,.jsx
prettier --check src/
vitest run --coverage
echo "All JS/TS verifications passed"
```

---

## Troubleshooting

### Common Issues

**Python: mypy errors on third-party packages**
- Solution: Add `ignore_missing_imports = True` in mypy.ini or use type stubs (`types-requests`, etc.)

**Go: golangci-lint too slow**
- Solution: Configure `.golangci.yml` to disable slow linters or use `--fast`

**JS/TS: ESLint and Prettier conflicts**
- Solution: Use `eslint-config-prettier` to disable conflicting ESLint rules

**Rust: clippy too strict**
- Solution: Allow specific lints in Cargo.toml: `#![allow(clippy::lint_name)]`

**Swift: SwiftLint warnings overwhelming**
- Solution: Configure `.swiftlint.yml` to disable rules incrementally, fix incrementally

### Verification Failures

When a checklist item fails:
1. Document the exact error message
2. Research the fix (docs, Stack Overflow, AI)
3. Apply the fix
4. Re-run verification
5. Update documentation if needed

---

## Related Documents

- [Part 1: Core Languages](language-verification-checklists-part1-core-languages.md) - Python, Go, JavaScript/TypeScript, Rust
- [Part 2: Extended Platforms](language-verification-checklists-part2-extended-platforms.md) - C#/.NET, Unity, Android, C/C++, Flutter, React Native, ML/AI, Embedded/IoT
