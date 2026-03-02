# Toolchain Integration: Language Detection & Platform

**Parent Document**: [TOOLCHAIN_INTEGRATION.md](./TOOLCHAIN_INTEGRATION.md)
**Part**: 2 of 3

---

## Language Detection Rules

### File Pattern → Language Mapping

**Detection Priority** (check in order):

1. **Manifest files** (most reliable):
   - `Cargo.toml` → Rust
   - `pyproject.toml` → Python
   - `package.json` → JavaScript/TypeScript
   - `go.mod` → Go
   - `mix.exs` → Elixir
   - `Gemfile` → Ruby

2. **Source file extensions** (fallback):
   - `*.rs` → Rust
   - `*.py` → Python
   - `*.ts`, `*.tsx` → TypeScript
   - `*.js`, `*.jsx` → JavaScript
   - `*.go` → Go
   - `*.ex`, `*.exs` → Elixir

3. **Build configuration** (legacy):
   - `Makefile` with `rustc` → Rust
   - `setup.py` → Python
   - `tsconfig.json` → TypeScript

### Multi-Language Projects

**Rule**: If project contains multiple languages, detect PRIMARY language (most source files) and SECONDARY languages.

**Example**:
- Project has 500 `.rs` files and 20 `.py` files
- **Primary**: Rust
- **Secondary**: Python
- **Toolchain**: Compile Rust toolchain + append Python toolchain section

### Mixed Language Toolchain Structure

```markdown
# Toolchain: xls-cross-platform (Mixed)

## Primary Language: Rust
[Full Rust toolchain configuration]

## Secondary Language: Python
[Minimal Python toolchain for build scripts]

## Integration Rules
- Rust code MUST pass all Rust toolchain checks
- Python scripts MUST pass basic linting (no type checking required for secondary)
- Build process uses both toolchains
```

---

## Toolchain Selection Matrix

| Project Type | Primary Language | Package Manager | Formatter | Linter | Type Checker | Test Runner | Checklist |
|--------------|------------------|-----------------|-----------|--------|--------------|-------------|-----------|
| **Pure Rust** | Rust 1.75+ | Cargo | rustfmt | clippy | - | cargo test | `rust-checklist.json` |
| **Pure Python** | Python 3.12+ | uv | ruff | ruff | mypy | pytest | `python-checklist.json` |
| **Pure JS** | Node 20+ | pnpm | prettier | eslint | - | vitest | `js-checklist.json` |
| **Pure TS** | Node 20+ | pnpm | prettier | eslint | tsc | vitest | `ts-checklist.json` |
| **Pure Go** | Go 1.21+ | go modules | gofmt | golangci-lint | - | go test | `go-checklist.json` |
| **Rust + Py** | Rust + Python | cargo + uv | Both | Both | mypy | Both | `mixed-rust-py-checklist.json` |
| **TS + Py** | TypeScript + Python | pnpm + uv | Both | Both | tsc + mypy | Both | `mixed-ts-py-checklist.json` |

### Checklist File Locations

All checklists are stored in:
```
templates/checklists/{language}-checklist.json
templates/checklists/mixed-{lang1}-{lang2}-checklist.json
```

---

## Platform-Specific Toolchain Extensions

### When to Include Platform Sections

**Rule**: Include platform-specific sections if:
1. Project targets multiple platforms (specified in spec)
2. Language has platform-specific tooling (e.g., Rust cross-compilation)
3. Tests require platform-specific setup

### Platform Section Structure

For each platform, append:

```markdown
## Platform: {{PLATFORM_NAME}}

### Platform-Specific Tools
- Cross-compiler: {{CROSS_COMPILER}}
- Platform SDK: {{PLATFORM_SDK}}

### Platform-Specific Build
```bash
{{PLATFORM_BUILD_CMD}}
```

### Platform-Specific Tests
```bash
{{PLATFORM_TEST_CMD}}
```

### Platform Checklist
- [ ] Platform SDK installed
- [ ] Cross-compilation works
- [ ] Platform-specific tests pass
```

### Example: Rust Cross-Platform Toolchain

```markdown
# Toolchain: xls-cross-platform (Rust)

## Core Toolchain
[Base Rust configuration]

## Platform: Linux (x86_64-unknown-linux-gnu)
- Target: x86_64-unknown-linux-gnu
- Build: `cargo build --target x86_64-unknown-linux-gnu`

## Platform: macOS (aarch64-apple-darwin)
- Target: aarch64-apple-darwin
- Build: `cargo build --target aarch64-apple-darwin`

## Platform: Windows (x86_64-pc-windows-msvc)
- Target: x86_64-pc-windows-msvc
- Build: `cargo build --target x86_64-pc-windows-msvc`
- Requires: Visual Studio Build Tools
```

---

## Integration Commands

### 1. Compile Toolchain for Remote Agent

**Command**:
```bash
python3 skills/remote-agent-coordinator/scripts/compile_toolchain.py \
  --language {LANGUAGE} \
  --version {VERSION} \
  --platforms {PLATFORM_LIST} \
  --project {PROJECT_NAME} \
  --task-id {TASK_ID} \
  --output {OUTPUT_PATH}
```

**Arguments**:
- `--language`: Primary language (rust, python, javascript, typescript, go, elixir, ruby)
- `--version`: Language version (e.g., 1.75, 3.12, 20)
- `--platforms`: Comma-separated platform list (linux, macos, windows, ios, android)
- `--project`: GitHub repo name
- `--task-id`: GitHub issue number (e.g., GH-42)
- `--output`: Output path for compiled toolchain file

**Output**: Fully compiled `TOOLCHAIN.md` with NO template variables remaining.

**Verification**: Script MUST verify no `{{...}}` remains in output.

---

### 2. Verify Toolchain Setup

**Command** (run by remote agent):
```bash
bash -c 'eval "$(grep -A 1000 "^verify_toolchain()" TOOLCHAIN.md | grep -B 1000 "^}")"'
```

**Better approach** (extract setup script first):
```bash
python3 scripts/extract_toolchain_script.py TOOLCHAIN.md > setup.sh
chmod +x setup.sh
./setup.sh
```

**Exit codes**:
- `0`: Toolchain ready
- `1`: Toolchain setup failed (check error output)
- `2`: Invalid toolchain file

---

### 3. Validate Language Mapping Files

**Command**:
```bash
python3 skills/remote-agent-coordinator/scripts/validate_language_mappings.py \
  --language {LANGUAGE}
```

**Checks**:
- All required variables defined
- Tool commands are valid
- Version numbers are valid
- Config files exist

---

### 4. Generate Language Mapping Template

**Command** (for adding new language support):
```bash
python3 skills/remote-agent-coordinator/scripts/generate_language_mapping.py \
  --language {NEW_LANGUAGE} \
  --output toolchain/languages/{NEW_LANGUAGE}.json
```

**Template structure**:
```json
{
  "language": "newlang",
  "default_version": "1.0.0",
  "package_manager": "pkg-manager",
  "tools": {
    "formatter": {"name": "fmt", "cmd": "fmt check", "config": "fmt.toml"},
    "linter": {"name": "lint", "cmd": "lint", "config": "lint.toml"},
    "type_checker": null,
    "test_runner": {"name": "test", "cmd": "test", "coverage_cmd": "test --coverage"}
  },
  "build_command": "build",
  "verify_all_cmd": "fmt check && lint && test"
}
```

---

## Toolchain Compilation Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Orchestrator: Detect Project Language                    │
│    → Analyze manifest files, file extensions               │
│    → Determine primary/secondary languages                 │
│    → Identify target platforms                             │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│ 2. Orchestrator: Load Language Mapping                      │
│    → Read toolchain/languages/{LANGUAGE}.json              │
│    → Load platform-specific values                         │
│    → Prepare substitution dictionary                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│ 3. Orchestrator: Compile Toolchain Template                 │
│    → Load BASE_TOOLCHAIN.md                                │
│    → Substitute all {{VARIABLE}} placeholders              │
│    → Append platform-specific sections                     │
│    → Embed verification checklist                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│ 4. Orchestrator: Validate Compiled Toolchain                │
│    → Check no template variables remain                    │
│    → Verify all commands are executable                    │
│    → Validate checklist format                             │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│ 5. Orchestrator: Send to Remote Agent                       │
│    → Include TOOLCHAIN.md in task handoff                  │
│    → Agent executes setup script                           │
│    → Agent reports verification results                    │
└─────────────────────────────────────────────────────────────┘
```

---

**Previous**: [Part 1 - Pipeline & Variables](./TOOLCHAIN_INTEGRATION-part1-pipeline-variables.md)
**Next**: [Part 3 - Operations & Reference](./TOOLCHAIN_INTEGRATION-part3-operations-reference.md)
