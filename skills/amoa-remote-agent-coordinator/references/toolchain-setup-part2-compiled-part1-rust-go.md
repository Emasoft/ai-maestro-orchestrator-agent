# Toolchain Setup Part 2 - Part 1: Rust and Go


## Contents

- [Purpose](#purpose)
- [Table of Contents](#table-of-contents)
- [1.1 Rust Toolchain (cargo-based)](#11-rust-toolchain-cargo-based)
  - [1.1.1 Setup Instructions for Remote Agent](#111-setup-instructions-for-remote-agent)
  - [1.1.2 Required Components](#112-required-components)
  - [1.1.3 Configuration Files](#113-configuration-files)
  - [1.1.4 Verification Commands](#114-verification-commands)
- [1.2 Go Toolchain](#12-go-toolchain)
  - [1.2.1 Setup Instructions for Remote Agent](#121-setup-instructions-for-remote-agent)
  - [1.2.2 Required Tools](#122-required-tools)
  - [1.2.3 Configuration Files](#123-configuration-files)
  - [1.2.4 Verification Commands](#124-verification-commands)
- [Related Parts](#related-parts)

---

## Purpose

This reference provides toolchain setup instructions for Rust and Go. Remote agents do NOT have access to this skill, so the orchestrator must provide ALL toolchain requirements explicitly in each task delegation message.

---

## Table of Contents

- 1.1 [Rust Toolchain (cargo-based)](#11-rust-toolchain-cargo-based)
  - 1.1.1 Setup instructions
  - 1.1.2 Required components
  - 1.1.3 Configuration files
  - 1.1.4 Verification commands
- 1.2 [Go Toolchain](#12-go-toolchain)
  - 1.2.1 Setup instructions
  - 1.2.2 Required tools
  - 1.2.3 Configuration files
  - 1.2.4 Verification commands

---

## 1.1 Rust Toolchain (cargo-based)

### 1.1.1 Setup Instructions for Remote Agent

```bash
# Install rustup (if not present)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Install stable toolchain
rustup default stable
rustup update

# Verify installation
rustc --version
cargo --version
```

### 1.1.2 Required Components

```bash
# Linting
rustup component add clippy

# Formatting
rustup component add rustfmt

# Code coverage (optional)
cargo install cargo-tarpaulin
```

### 1.1.3 Configuration Files

**Cargo.toml** (dependencies section):
```toml
[dependencies]
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
clap = { version = "4.0", features = ["derive"] }

[dev-dependencies]
assert_cmd = "2.0"
predicates = "3.0"
```

**clippy.toml** (optional):
```toml
msrv = "1.70"
```

### 1.1.4 Verification Commands

```bash
# Build
cargo build

# Test
cargo test

# Lint (strict)
cargo clippy -- -D warnings

# Format
cargo fmt

# All checks
cargo test && cargo clippy -- -D warnings && cargo fmt --check
```

---

## 1.2 Go Toolchain

### 1.2.1 Setup Instructions for Remote Agent

```bash
# Install Go (if not present)
# macOS:
brew install go

# Linux:
wget https://go.dev/dl/go1.22.0.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.22.0.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin

# Verify installation
go version
```

### 1.2.2 Required Tools

```bash
# Linting
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# Testing (built-in)
# go test is included
```

### 1.2.3 Configuration Files

**go.mod** (initialize):
```bash
go mod init github.com/owner/project
```

**.golangci.yml**:
```yaml
linters:
  enable:
    - gofmt
    - govet
    - errcheck
    - staticcheck
    - gosimple
    - ineffassign
```

### 1.2.4 Verification Commands

```bash
# Build
go build ./...

# Test
go test ./... -v

# Lint
golangci-lint run

# Format
go fmt ./...

# Vet
go vet ./...

# All checks
go test ./... && go vet ./... && golangci-lint run
```

---

## Related Parts

- [Index: Toolchain Setup Part 2](./toolchain-setup-part2-compiled.md) - Main index with all TOCs
- [Part 2: Swift, C/C++, Objective-C](./toolchain-setup-part2-compiled-part2-swift-cpp-objc.md)
- [Part 3: .NET and JVM Languages](./toolchain-setup-part2-compiled-part3-dotnet-jvm.md)
