# Toolchain Setup Part 3 Section 2: Templates and Verification


## Contents

- [Purpose](#purpose)
- [Table of Contents](#table-of-contents)
- [1. Delegation Template with Toolchain](#1-delegation-template-with-toolchain)
- [Toolchain Setup (RUN FIRST)](#toolchain-setup-run-first)
- [Task Details](#task-details)
- [Verification Commands](#verification-commands)
- [Completion Criteria](#completion-criteria)
- [2. Python Task Template](#2-python-task-template)
- [Toolchain Setup (RUN FIRST)](#toolchain-setup-run-first)
- [Verification Commands](#verification-commands)
- [3. JavaScript/TypeScript Task Template](#3-javascripttypescript-task-template)
- [Toolchain Setup (RUN FIRST)](#toolchain-setup-run-first)
- [Verification Commands](#verification-commands)
- [4. Toolchain Verification Script Generator](#4-toolchain-verification-script-generator)
  - [Generic Verification Script Generator](#generic-verification-script-generator)
  - [Usage](#usage)
- [5. Quick Reference: Delegation Checklist](#5-quick-reference-delegation-checklist)
- [Related References](#related-references)

---

## Purpose

This section provides delegation templates with toolchain requirements and verification scripts. When delegating tasks, ALWAYS include toolchain setup to ensure remote agents have proper environment.

---

## Table of Contents

1. [Delegation Template with Toolchain](#1-delegation-template-with-toolchain)
2. [Python Task Template](#2-python-task-template)
3. [JavaScript/TypeScript Task Template](#3-javascripttypescript-task-template)
4. [Toolchain Verification Script Generator](#4-toolchain-verification-script-generator)
5. [Quick Reference: Delegation Checklist](#5-quick-reference-delegation-checklist)

---

## 1. Delegation Template with Toolchain

When delegating tasks, ALWAYS include toolchain setup. Example:

```
Subject: [TASK] GH-42: Implement Feature X

## Toolchain Setup (RUN FIRST)

Before starting, verify your toolchain:

```bash
# Required tools
rustc --version  # Expected: 1.75+
cargo --version
cargo clippy --version

# If missing, install:
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup component add clippy rustfmt
```

## Task Details
[... task description ...]

## Verification Commands

After implementation, run ALL of these:
```bash
cargo build && cargo test && cargo clippy -- -D warnings
```

## Completion Criteria
- [ ] All verification commands pass
- [ ] PR created with "Closes #42"
- [ ] Tests verify actual behavior (not just exit codes)
```

---

## 2. Python Task Template

```
Subject: [TASK] GH-XX: Python Feature

## Toolchain Setup (RUN FIRST)

```bash
# Required tools
uv --version  # Expected: 0.4+
python --version  # Expected: 3.12+

# If missing, install:
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Verification Commands

```bash
uv run ruff check src/ tests/
uv run mypy src/
uv run pytest tests/ -v
```
```

---

## 3. JavaScript/TypeScript Task Template

```
Subject: [TASK] GH-XX: JS/TS Feature

## Toolchain Setup (RUN FIRST)

```bash
# Required tools
bun --version  # Expected: 1.0+

# If missing, install:
curl -fsSL https://bun.sh/install | bash
bun install
```

## Verification Commands

```bash
bun run tsc --noEmit && bun run eslint src/ && bun test
```
```

---

## 4. Toolchain Verification Script Generator

The orchestrator should verify remote agent toolchain before delegating:

### Generic Verification Script Generator

```bash
# Generate toolchain check for remote agent
generate_toolchain_check() {
  local lang="$1"

  case "$lang" in
    rust)
      cat << 'EOF'
#!/bin/bash
echo "=== Rust Toolchain Verification ==="

check_tool() {
  local name="$1"
  local cmd="$2"
  if $cmd --version &>/dev/null; then
    echo "[OK] $name: $($cmd --version 2>&1 | head -1)"
  else
    echo "[MISSING] $name - install required"
    return 1
  fi
}

MISSING=0
check_tool "Rust" rustc || ((MISSING++))
check_tool "Cargo" cargo || ((MISSING++))
check_tool "Clippy" "cargo clippy" || ((MISSING++))

if [ $MISSING -gt 0 ]; then
  echo ""
  echo "Missing $MISSING tool(s). Install with:"
  echo "  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
  echo "  rustup component add clippy rustfmt"
  exit 1
fi

echo ""
echo "All tools verified. Ready to proceed."
EOF
      ;;

    python)
      cat << 'EOF'
#!/bin/bash
echo "=== Python Toolchain Verification ==="

check_tool() {
  local name="$1"
  local cmd="$2"
  if $cmd --version &>/dev/null; then
    echo "[OK] $name: $($cmd --version 2>&1 | head -1)"
  else
    echo "[MISSING] $name - install required"
    return 1
  fi
}

MISSING=0
check_tool "uv" uv || ((MISSING++))
check_tool "Python" python3 || ((MISSING++))
check_tool "ruff" ruff || ((MISSING++))

if [ $MISSING -gt 0 ]; then
  echo ""
  echo "Missing $MISSING tool(s). Install with:"
  echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
  echo "  uv pip install ruff mypy"
  exit 1
fi

echo ""
echo "All tools verified. Ready to proceed."
EOF
      ;;

    javascript|typescript)
      cat << 'EOF'
#!/bin/bash
echo "=== JavaScript/TypeScript Toolchain Verification ==="

check_tool() {
  local name="$1"
  local cmd="$2"
  if $cmd --version &>/dev/null; then
    echo "[OK] $name: $($cmd --version 2>&1 | head -1)"
  else
    echo "[MISSING] $name - install required"
    return 1
  fi
}

MISSING=0
check_tool "Bun" bun || ((MISSING++))
check_tool "TypeScript" tsc || ((MISSING++))

if [ $MISSING -gt 0 ]; then
  echo ""
  echo "Missing $MISSING tool(s). Install with:"
  echo "  curl -fsSL https://bun.sh/install | bash"
  echo "  bun add -d typescript"
  exit 1
fi

echo ""
echo "All tools verified. Ready to proceed."
EOF
      ;;

    go)
      cat << 'EOF'
#!/bin/bash
echo "=== Go Toolchain Verification ==="

check_tool() {
  local name="$1"
  local cmd="$2"
  if $cmd version &>/dev/null || $cmd --version &>/dev/null; then
    echo "[OK] $name: $($cmd version 2>&1 | head -1)"
  else
    echo "[MISSING] $name - install required"
    return 1
  fi
}

MISSING=0
check_tool "Go" go || ((MISSING++))
check_tool "golangci-lint" golangci-lint || ((MISSING++))

if [ $MISSING -gt 0 ]; then
  echo ""
  echo "Missing $MISSING tool(s). Install with:"
  echo "  brew install go"
  echo "  go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest"
  exit 1
fi

echo ""
echo "All tools verified. Ready to proceed."
EOF
      ;;

    *)
      echo "Unknown language: $lang"
      echo "Supported: rust, python, javascript, typescript, go"
      return 1
      ;;
  esac
}
```

### Usage

Include the appropriate verification script in every task delegation:

```bash
# Generate and include in delegation message
generate_toolchain_check rust > /tmp/verify-toolchain.sh

# Or inline in the message
echo "Run this first to verify your toolchain:"
echo '```bash'
generate_toolchain_check python
echo '```'
```

---

## 5. Quick Reference: Delegation Checklist

Before delegating any task, ensure you include:

1. **Toolchain verification commands** - What tools are needed and how to check
2. **Installation instructions** - How to install missing tools
3. **Project setup commands** - How to initialize/configure the project
4. **Verification commands** - Commands to run after implementation
5. **Completion criteria** - Clear success conditions

| Language | Verify | Install | Build | Lint | Test |
|----------|--------|---------|-------|------|------|
| Rust | `rustc --version` | `rustup` | `cargo build` | `cargo clippy` | `cargo test` |
| Python | `uv --version` | `curl astral.sh/uv` | N/A | `ruff check` | `pytest` |
| JS/TS | `bun --version` | `curl bun.sh` | `tsc` | `eslint` | `bun test` |
| Go | `go version` | `brew install go` | `go build` | `golangci-lint` | `go test` |
| Android | `sdkmanager --version` | SDK Manager | `./gradlew build` | `./gradlew lint` | `./gradlew test` |
| React Native | `bun --version` | `curl bun.sh` | `npx react-native build` | `eslint` | `bun test` |

---

## Related References

- [Part 3 Index](./toolchain-setup-part3-mobile-crossplatform.md) - Main index for mobile/cross-platform
- [Part 3 Section 1](./toolchain-setup-part3-mobile-crossplatform-section1-mobile-platforms.md) - Android, React Native, Blazor, cross-compilation
- [Part 1](./toolchain-setup-part1-core-interpreted.md) - Core setup, Python, JS/TS, Ruby, Bash
- [Part 2](./toolchain-setup-part2-compiled.md) - Rust, Go, Swift, C/C++, Objective-C, C#, Java, Kotlin
