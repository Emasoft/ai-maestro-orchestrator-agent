# Toolchain Integration: Pipeline & Variables

**Parent Document**: [TOOLCHAIN_INTEGRATION.md](./TOOLCHAIN_INTEGRATION.md)
**Part**: 1 of 3

---

## Pipeline Stage to Toolchain Mapping

| Pipeline Stage | Toolchain Actions | Required Checklist | Template Type |
|----------------|-------------------|-------------------|---------------|
| **Issue Creation** | None | N/A | N/A |
| **Design/Specification** | Detect language requirements | Language detection | `spec` |
| **Task Handoff (Setup)** | Compile and send toolchain | Toolchain verification | `toolchain` |
| **Code Implementation** | Use compiled toolchain | Development workflow | N/A |
| **Code Review** | Run toolchain verification | Verification checklist | `validation` |
| **Pre-Merge Validation** | Full toolchain validation | All platform checks | `validation` |
| **Testing** | Run test suite via toolchain | Test execution | `test_results` |
| **Release** | Cross-platform toolchain tests | Platform-specific tests | `release` |

---

## Toolchain Lifecycle in EOA

### Phase 1: Detection (Design/Specification Stage)

**When**: After spec generation, before task assignment
**Action**: Orchestrator analyzes project to determine required toolchains

**Detection Rules** (in priority order):

1. **Explicit spec requirement**: Language specified in `--lang` flag
2. **Project manifest detection**: Check for manifest files in project root
3. **File extension analysis**: Scan source directories for language patterns
4. **Fallback**: Ask user to clarify language requirements

**Output**: Language configuration object:
```json
{
  "primary_language": "rust",
  "secondary_languages": ["python"],
  "platforms": ["linux", "macos", "windows"],
  "requires_cross_compilation": true
}
```

---

### Phase 2: Compilation (Task Handoff Stage)

**When**: Before sending task to remote agent
**Action**: Orchestrator compiles BASE_TOOLCHAIN.md with language-specific values

**Steps**:
1. Load `BASE_TOOLCHAIN.md` template
2. Load language-specific value mappings from `toolchain/languages/{LANGUAGE}.json`
3. Substitute all `{{VARIABLE}}` placeholders
4. Append platform-specific sections if multiplatform
5. Embed verification checklist
6. Save compiled toolchain to agent workspace

**Command**:
```bash
python3 skills/remote-agent-coordinator/scripts/compile_toolchain.py \
  --language rust \
  --version 1.75 \
  --platforms linux,macos \
  --project xls-cross-platform \
  --task-id GH-42 \
  --output /tmp/agent-workspace/TOOLCHAIN.md
```

---

### Phase 3: Setup (Remote Agent)

**When**: Agent receives task
**Action**: Agent executes toolchain setup script

**Steps**:
1. Read compiled `TOOLCHAIN.md`
2. Extract setup script block
3. Execute setup script (install language, tools, dependencies)
4. Run verification checklist
5. Report success/failure to orchestrator

---

### Phase 4: Verification (Code Review & Pre-Merge Stages)

**When**: Before PR approval and before merge
**Action**: Run full toolchain verification

**Verification Levels**:

| Level | When | Commands | Must Pass |
|-------|------|----------|-----------|
| **Quick** | After code changes | Format check, lint | Yes |
| **Standard** | Before PR approval | Quick + type check + unit tests | Yes |
| **Full** | Before merge | Standard + integration tests + coverage | Yes |
| **Release** | Before release | Full + platform tests + benchmarks | Yes |

**Command**:
```bash
# Agent runs this automatically
{{VERIFY_ALL_CMD}}
```

---

## Variable Substitution Rules

### Core Variables (Required)

| Variable | Source | Example | Fallback |
|----------|--------|---------|----------|
| `{{LANGUAGE}}` | Detection phase | `rust` | **None** (must be explicit) |
| `{{LANGUAGE_VERSION}}` | Language mapping file | `1.75` | Latest stable |
| `{{PACKAGE_MANAGER}}` | Language mapping file | `cargo` | Language default |
| `{{PACKAGE_MANAGER_VERSION}}` | Language mapping file | `1.0.0` | Latest |
| `{{PROJECT_NAME}}` | GitHub repo name | `xls-cross-platform` | Directory name |
| `{{TASK_ID}}` | GitHub issue number | `GH-42` | `TASK-{timestamp}` |
| `{{TIMESTAMP}}` | Generation time | `2026-01-05T10:30:00Z` | Current UTC time |

### Tool Variables (Language-Specific)

| Variable | Source | Example (Rust) | Example (Python) |
|----------|--------|----------------|------------------|
| `{{FORMATTER}}` | Language mapping | `rustfmt` | `ruff` |
| `{{FORMATTER_CMD}}` | Language mapping | `cargo fmt --check` | `uv run ruff format --check` |
| `{{FORMATTER_CONFIG}}` | Language mapping | `rustfmt.toml` | `pyproject.toml` |
| `{{LINTER}}` | Language mapping | `clippy` | `ruff` |
| `{{LINTER_CMD}}` | Language mapping | `cargo clippy -- -D warnings` | `uv run ruff check` |
| `{{LINTER_CONFIG}}` | Language mapping | `Cargo.toml` | `pyproject.toml` |
| `{{TYPE_CHECKER}}` | Language mapping | `-` | `mypy` |
| `{{TYPE_CHECKER_CMD}}` | Language mapping | `-` | `uv run mypy --strict` |
| `{{TYPE_CHECKER_CONFIG}}` | Language mapping | `-` | `pyproject.toml` |
| `{{TEST_RUNNER}}` | Language mapping | `cargo test` | `pytest` |
| `{{TEST_CMD}}` | Language mapping | `cargo test` | `uv run pytest -v` |
| `{{COVERAGE_CMD}}` | Language mapping | `cargo tarpaulin` | `uv run pytest --cov` |
| `{{BUILD_COMMAND}}` | Language mapping | `cargo build --release` | `uv build` |

### Installation Variables (Platform-Specific)

| Variable | Source | Example (macOS) | Example (Linux) |
|----------|--------|-----------------|-----------------|
| `{{LANGUAGE_INSTALL_CMD}}` | Platform mapping | `brew install rust` | `curl --proto '=https' ... \| sh` |
| `{{PACKAGE_MANAGER_INSTALL_CMD}}` | Platform mapping | Bundled with Rust | Bundled with Rust |
| `{{DEV_TOOLS_INSTALL_CMD}}` | Platform mapping | `brew install ...` | `apt-get install ...` |
| `{{PREREQUISITE_CHECKS}}` | Platform mapping | `check_prerequisite brew "..."` | `check_prerequisite apt-get "..."` |

### Verification Variables

| Variable | Source | Example |
|----------|--------|---------|
| `{{VERIFY_ALL_CMD}}` | Language mapping | `cargo fmt --check && cargo clippy && cargo test` |
| `{{VERIFY_COMMANDS}}` | Generated from tool list | Multi-line verification script |
| `{{CONFIG_FILES_LIST}}` | Language mapping | `Cargo.toml, rustfmt.toml, clippy.toml` |

---

**Next**: [Part 2 - Language Detection & Platform](./TOOLCHAIN_INTEGRATION-part2-language-platform.md)
