# Go Toolchain Template

Extends: `BASE_TOOLCHAIN.md`
Package Manager: go modules
Preferred for: CLI tools, system utilities, microservices, concurrent applications

---

## Quick Reference

| Component | Tool | Version | Install |
|-----------|------|---------|---------|
| Language | go | 1.22+ | brew/apt/winget |
| Package Manager | go mod | bundled | built-in |
| Formatter | go fmt | bundled | built-in |
| Linter | golangci-lint | latest | go install |
| Test Runner | go test | bundled | built-in |
| Race Detector | go test -race | bundled | built-in |
| Coverage | go test -cover | bundled | built-in |

---

## Variable Substitutions

```yaml
LANGUAGE: go
LANGUAGE_VERSION: "1.22"
LANGUAGE_CMD: go
LANGUAGE_VERSION_CMD: "go version"
LANGUAGE_INSTALL_CMD: |
  # macOS
  brew install go@1.22
  # Ubuntu/Debian
  sudo apt update && sudo apt install golang-1.22
  # Windows
  winget install GoLang.Go.1.22

PACKAGE_MANAGER: "go mod"
PACKAGE_MANAGER_VERSION: "bundled"
PACKAGE_MANAGER_INSTALL_CMD: "# Bundled with Go"
INSTALL_DEPS_CMD: "go mod download"

FORMATTER: "go fmt"
FORMATTER_CMD: "go fmt ./..."
FORMATTER_CONFIG: "# No config needed - standardized"

LINTER: golangci-lint
LINTER_CMD: "golangci-lint run ./..."
LINTER_CONFIG: ".golangci.yml"

TYPE_CHECKER: "go vet"
TYPE_CHECKER_CMD: "go vet ./..."
TYPE_CHECKER_CONFIG: "# Built-in static analysis"

TEST_RUNNER: "go test"
TEST_CMD: "go test ./... -v"
COVERAGE_CMD: "go test ./... -coverprofile=coverage.out -covermode=atomic"

BUILD_COMMAND: "go build -o bin/{{PROJECT_NAME}} ./cmd/{{PROJECT_NAME}}"
VERIFY_ALL_CMD: "go fmt ./... && go vet ./... && golangci-lint run ./... && go test ./... -race -cover"

CONFIG_FILES_LIST: "go.mod, go.sum, .golangci.yml"
```

---

## Part Files Index

This template is split into multiple files for better organization:

### Part 1: Setup Script
**File**: [GO_TOOLCHAIN-part1-setup.md](./GO_TOOLCHAIN-part1-setup.md)
- Complete bash setup script for Go toolchain
- Install Go 1.22+
- Configure GOPATH and GOBIN
- Initialize Go module
- Install development tools (golangci-lint)
- Create directory structure (cmd/, pkg/, internal/, test/)
- Create configuration files (.golangci.yml)
- Download dependencies
- Verify installation

### Part 2: CI/CD Configuration
**File**: [GO_TOOLCHAIN-part2-ci.md](./GO_TOOLCHAIN-part2-ci.md)
- go.mod template
- GitHub Actions CI workflow template
- Multi-platform matrix testing (ubuntu, macos, windows)
- Coverage job configuration
- Library requirements and violations

### Part 3: Patterns and Verification
**File**: [GO_TOOLCHAIN-part3-patterns.md](./GO_TOOLCHAIN-part3-patterns.md)
- Verification checklist for Go toolchain setup
- Common Go patterns for EOA Compliance
- Error handling patterns
- JSON handling patterns
- CLI structure with Cobra
- Testing patterns (table-driven tests)
- Template metadata

---

## Template Metadata

```yaml
template:
  name: GO_TOOLCHAIN
  version: 1.0.0
  eoa_compatible: true
  language: go
  language_version: "1.22+"
  requires:
    - git
    - curl
    - bash
  generates:
    - setup script
    - go.mod
    - .golangci.yml
    - verification checklist
    - GitHub Actions workflow
  parts:
    - GO_TOOLCHAIN-part1-setup.md
    - GO_TOOLCHAIN-part2-ci.md
    - GO_TOOLCHAIN-part3-patterns.md
```
