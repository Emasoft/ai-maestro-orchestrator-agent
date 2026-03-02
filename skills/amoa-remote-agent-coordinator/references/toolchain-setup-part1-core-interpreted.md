# Toolchain Setup Part 1: Core Setup and Interpreted Languages


## Contents

- [Purpose](#purpose)
- [Table of Contents](#table-of-contents)
- [Related References](#related-references)
- [1. Orchestrator Self-Setup](#1-orchestrator-self-setup)
  - [Orchestrator Required Tools](#orchestrator-required-tools)
- [2. Toolchain Selection by Language](#2-toolchain-selection-by-language)
- [3. Python Toolchain (uv-based)](#3-python-toolchain-uv-based)
  - [Setup Instructions for Remote Agent](#setup-instructions-for-remote-agent)
  - [Required Tools](#required-tools)
  - [Configuration Files](#configuration-files)
  - [Verification Commands](#verification-commands)
- [4. JavaScript/TypeScript Toolchain (bun-based)](#4-javascripttypescript-toolchain-bun-based)
  - [Setup Instructions for Remote Agent](#setup-instructions-for-remote-agent)
  - [Alternative: pnpm](#alternative-pnpm)
  - [Required Tools](#required-tools)
  - [Configuration Files](#configuration-files)
  - [Verification Commands](#verification-commands)
- [5. Ruby Toolchain](#5-ruby-toolchain)
  - [Setup Instructions for Remote Agent](#setup-instructions-for-remote-agent)
  - [Bundler Configuration](#bundler-configuration)
  - [Verification Commands](#verification-commands)
- [6. Bash/Shell Toolchain](#6-bashshell-toolchain)
  - [Setup Instructions for Remote Agent](#setup-instructions-for-remote-agent)
  - [Verification Commands](#verification-commands)
- [Quick Reference Table](#quick-reference-table)

---

## Purpose

This reference provides toolchain setup instructions for the orchestrator and interpreted languages (Python, JavaScript/TypeScript, Ruby, Bash). Remote agents do NOT have access to this skill, so the orchestrator must provide ALL toolchain requirements explicitly in each task delegation message.

---

## Table of Contents

1. [Orchestrator Self-Setup](#1-orchestrator-self-setup)
2. [Toolchain Selection by Language](#2-toolchain-selection-by-language)
3. [Python Toolchain (uv-based)](#3-python-toolchain-uv-based)
4. [JavaScript/TypeScript Toolchain (bun-based)](#4-javascripttypescript-toolchain-bun-based)
5. [Ruby Toolchain](#5-ruby-toolchain)
6. [Bash/Shell Toolchain](#6-bashshell-toolchain)

---

## Related References

- [Part 2: Compiled Languages](./toolchain-setup-part2-compiled.md) - Rust, Go, Swift, C/C++, Objective-C, C#, Java, Kotlin
- [Part 3: Mobile/Cross-Platform](./toolchain-setup-part3-mobile-crossplatform.md) - Android, React Native, Blazor, Cross-Platform Matrix, Delegation Templates

---

## 1. Orchestrator Self-Setup

The orchestrator must install these tools locally for skill validation and verification:

```bash
# Skills validation (Open Agent Skills Specification)
uv pip install skills-ref

# GitHub CLI (required for all projects)
brew install gh  # macOS
# or: sudo apt install gh  # Linux

# Verify installation
skills-ref --version 2>/dev/null || echo "skills-ref not installed"
gh --version
```

### Orchestrator Required Tools

| Tool | Purpose | Install Command |
|------|---------|-----------------|
| `skills-ref` | Validate skills against Open Spec | `uv pip install skills-ref` |
| `gh` | GitHub CLI operations | `brew install gh` |
| `jq` | JSON processing | `brew install jq` |
| `shellcheck` | Shell script linting | `brew install shellcheck` |
| `ruff` | Python linting | `uv pip install ruff` |

---

## 2. Toolchain Selection by Language

**PREFERRED toolchain managers** (in order of preference):

| Language | Preferred | Alternative |
|----------|-----------|-------------|
| Python | `uv` | `pip` + `venv` |
| Rust | `cargo` + `rustup` | - |
| JavaScript/TypeScript | `bun` | `pnpm`, `npm` |
| Go | `go mod` | - |
| Swift | `swift` + SPM | `xcodebuild` |
| C/C++ | `cmake` + `ninja` | `make` |
| Java | `gradle` | `maven` |
| Kotlin | `gradle` | `maven` |
| C# | `dotnet` | - |
| Ruby | `bundler` | - |

---

## 3. Python Toolchain (uv-based)

### Setup Instructions for Remote Agent

```bash
# Install uv (if not present)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version

# Create virtual environment
uv venv --python 3.12
source .venv/bin/activate

# Initialize project (if new)
uv init --python 3.12

# Install dependencies
uv pip install -e ".[dev]"
# OR from requirements
uv pip install -r requirements.txt
```

### Required Tools

```bash
# Linting and formatting
uv pip install ruff mypy

# Testing
uv pip install pytest pytest-cov

# Type stubs (as needed)
uv pip install types-requests types-PyYAML
```

### Configuration Files

**pyproject.toml** (minimal):
```toml
[project]
name = "project-name"
version = "0.1.0"
requires-python = ">=3.12"

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.12"
strict = true
```

### Verification Commands

```bash
# Format
uv run ruff format src/ tests/

# Lint
uv run ruff check src/ tests/

# Type check
uv run mypy src/

# Test
uv run pytest tests/ -v
```

---

## 4. JavaScript/TypeScript Toolchain (bun-based)

### Setup Instructions for Remote Agent

```bash
# Install bun (if not present)
curl -fsSL https://bun.sh/install | bash
source ~/.bashrc  # or restart shell

# Verify installation
bun --version

# Initialize project (if new)
bun init

# Install dependencies
bun install
```

### Alternative: pnpm

```bash
# Install pnpm
npm install -g pnpm

# Install dependencies
pnpm install
```

### Required Tools

```bash
# TypeScript
bun add -d typescript @types/node

# Linting
bun add -d eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin

# Testing
bun add -d vitest @vitest/coverage-v8

# Formatting
bun add -d prettier
```

### Configuration Files

**tsconfig.json**:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "outDir": "./dist",
    "declaration": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

**eslint.config.js**:
```javascript
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
);
```

### Verification Commands

```bash
# Type check
bun run tsc --noEmit

# Lint
bun run eslint src/

# Test
bun test

# Format
bun run prettier --write src/

# All checks
bun run tsc --noEmit && bun run eslint src/ && bun test
```

---

## 5. Ruby Toolchain

### Setup Instructions for Remote Agent

```bash
# Install rbenv
brew install rbenv ruby-build

# Install Ruby
rbenv install 3.3.0
rbenv global 3.3.0

# Verify
ruby --version

# Install Bundler
gem install bundler
```

### Bundler Configuration

**Gemfile**:
```ruby
source 'https://rubygems.org'

gem 'rake'
gem 'rspec', group: :test
gem 'rubocop', group: :development
```

### Verification Commands

```bash
# Install dependencies
bundle install

# Test
bundle exec rspec

# Lint
bundle exec rubocop

# Format
bundle exec rubocop -A

# All
bundle exec rspec && bundle exec rubocop
```

---

## 6. Bash/Shell Toolchain

### Setup Instructions for Remote Agent

```bash
# Install shellcheck
brew install shellcheck  # macOS
# or: sudo apt install shellcheck  # Linux

# Install shfmt
brew install shfmt  # macOS
# or: go install mvdan.cc/sh/v3/cmd/shfmt@latest

# Verify
shellcheck --version
shfmt --version
```

### Verification Commands

```bash
# Lint all shell scripts
find . -name "*.sh" -exec shellcheck {} \;

# Format
shfmt -w -i 2 scripts/

# Check syntax
bash -n script.sh

# All checks
find . -name "*.sh" -exec shellcheck {} \; && find . -name "*.sh" -exec bash -n {} \;
```

---

## Quick Reference Table

| Language | Install | Lint | Test | Format |
|----------|---------|------|------|--------|
| Python | `uv pip install -e ".[dev]"` | `uv run ruff check src/` | `uv run pytest tests/` | `uv run ruff format src/` |
| JS/TS | `bun install` | `bun run eslint src/` | `bun test` | `bun run prettier --write src/` |
| Ruby | `bundle install` | `bundle exec rubocop` | `bundle exec rspec` | `bundle exec rubocop -A` |
| Bash | N/A | `shellcheck script.sh` | `bash -n script.sh` | `shfmt -w -i 2 script.sh` |
