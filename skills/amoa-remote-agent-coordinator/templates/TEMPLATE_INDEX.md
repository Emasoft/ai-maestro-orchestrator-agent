# Template Index

Comprehensive index of all templates for coordinating remote agents across platforms, toolchains, and workflows.

---

## Quick Start

**How to use the template system**:

1. **Select toolchain template** - Choose language-specific toolchain (Python, Rust, JavaScript, etc.)
2. **Compile with variables** - Use `scripts/compile_template.py` to substitute project-specific values
3. **Send to agent with handoff template** - Use `handoff/TASK_DELEGATION_TEMPLATE.md` with compiled toolchain
4. **Agent reports back** - Agent uses `handoff/ACK_TEMPLATE.md`, `handoff/COMPLETION_REPORT_TEMPLATE.md`
5. **Verify completion** - Use `reports/VERIFICATION_REPORT.md` to confirm deliverables

---

## Template Categories

### Toolchain Templates

Templates defining language-specific development environments with LSP, formatter, linter, and build tools.

| File | Description |
|------|-------------|
| `toolchain/BASE_TOOLCHAIN.md` | Base template structure with all required variable placeholders for language toolchains |
| `toolchain/PYTHON_TOOLCHAIN.md` | Python development environment (uv, ruff, mypy, pytest, basedpyright LSP) |
| `toolchain/RUST_TOOLCHAIN.md` | Rust development environment (cargo, rustfmt, clippy, cargo-test, rust-analyzer LSP) |
| `toolchain/JAVASCRIPT_TOOLCHAIN.md` | JavaScript/TypeScript environment (pnpm, prettier, eslint, vitest, typescript-language-server) |
| `toolchain/GO_TOOLCHAIN.md` | Go development environment (go mod, gofmt, golangci-lint, go test, gopls LSP) |
| `toolchain/CPP_TOOLCHAIN.md` | C++ development environment (cmake, clang-format, clang-tidy, ctest, clangd LSP) |
| `toolchain/SWIFT_TOOLCHAIN.md` | Swift development environment (swift package manager, swift-format, swiftlint, sourcekit-lsp) |

**Related**: `TOOLCHAIN_INTEGRATION.md` - Integration guide for mixing multiple toolchains in monorepo

---

### Protocols (MANDATORY)

**All document delivery and storage MUST follow these protocols.**

| File | Description |
|------|-------------|
| `protocols/DOCUMENT_DELIVERY_PROTOCOL.md` | **MANDATORY**: Rules for sharing .md files via GitHub URLs only (never embed in messages) |
| `protocols/DOCUMENT_STORAGE_PROTOCOL.md` | **MANDATORY**: Standardized folder structure for downloaded documents with read-only enforcement |

**Key Delivery Rules**:
- NEVER send .md content directly in AI Maestro messages
- Upload to GitHub issue comment, share URL only
- ACK required for `document_delivery` type messages
- Orchestrator enforces with `scripts/enforce_delivery_protocol.py`

**Key Storage Rules**:
- All downloaded docs stored in `design/received/{category}/{task_id}/`
- Files set to READ-ONLY immediately after download (`chmod 444`)
- SHA256 hash stored in metadata.json for integrity verification
- Categories: `tasks`, `reports`, `acks`, `specs`, `plans`, `sync`
- Permanent, immutable record for verification and audit

---

### Platform Module Templates

Templates for defining cross-platform modules with platform-specific implementations.

| File | Description |
|------|-------------|
| `platform/PLATFORM_MODULE_BASE.md` | Base template for all platform modules defining common structure and interface |
| `platform/MACOS_MODULE.md` | macOS-specific module configuration (AppKit, Core Foundation, Xcode integration) |
| `platform/LINUX_MODULE.md` | Linux-specific module configuration (systemd, D-Bus, pkg-config, distro handling) |
| `platform/WINDOWS_MODULE.md` | Windows-specific module configuration (Win32 API, COM, Visual Studio integration) |
| `platform/CROSS_PLATFORM_SYNC.md` | Protocol for keeping platform modules synchronized across shared interfaces |

---

### Monorepo Templates

Templates for multi-language, multi-platform monorepo workspace configuration.

| File | Description |
|------|-------------|
| `monorepo/MONOREPO_BASE.md` | Base monorepo structure with workspace layout and dependency graph |
| `monorepo/MONOREPO_WORKSPACE.md` | Workspace configuration for package managers (cargo workspaces, pnpm workspaces, uv workspaces) |
| `monorepo/MONOREPO_TOOLCHAIN_COMPOSITION.md` | Multi-toolchain integration patterns (Rust + Python, JS + Swift, etc.) |
| `monorepo/MONOREPO_CI_MATRIX.md` | CI/CD matrix testing across platforms, languages, and module combinations |
| `monorepo/DOCKER_INTEGRATION.md` | Docker/containerization setup for monorepo builds and testing |

---

### Claude Code Configuration

Templates for configuring Claude Code agents with LSP servers, skills, and environment setup.

| File | Description |
|------|-------------|
| `claude-config/AGENT_ENVIRONMENT_SETUP.md` | Complete agent environment setup checklist (tools, LSP, skills, GitHub auth) |
| `claude-config/PROJECT_CLAUDE_CONFIG.md` | Project-level CLAUDE.md configuration with rules, workflows, and tooling |
| `claude-config/LSP_SELECTION_GUIDE.md` | Decision tree for selecting and configuring LSP servers by language/platform |
| `claude-config/TOOLCHAIN_SKILLS_MATRIX.md` | Mapping of toolchain templates to required Claude Code skills |

---

### Handoff Templates

Structured communication templates for task delegation and agent responses.

| File | Description |
|------|-------------|
| `handoff/TASK_DELEGATION_TEMPLATE.md` | Orchestrator sends task assignment with context, goals, templates, and verification criteria |
| `handoff/ACK_TEMPLATE.md` | Agent immediately acknowledges task receipt with understanding confirmation |
| `handoff/COMPLETION_REPORT_TEMPLATE.md` | Agent reports task completion with summary, verification, and artifact locations |
| `handoff/BLOCKER_REPORT_TEMPLATE.md` | Agent reports blockers requiring orchestrator intervention (missing deps, auth, conflicts) |

**Legacy templates** (now in handoff/):
- `ack-response.md` - Replaced by `handoff/ACK_TEMPLATE.md`
- `completion-report.md` - Replaced by `handoff/COMPLETION_REPORT_TEMPLATE.md`
- `status-update.md` - Replaced by checkpoint updates in COMPLETION_REPORT_TEMPLATE
- `task-checklist.md` - Now embedded in TASK_DELEGATION_TEMPLATE

---

### Report Templates

Standardized report formats for verification, status tracking, and synchronization.

| File | Description |
|------|-------------|
| `reports/TOOLCHAIN_SETUP_REPORT.md` | Agent confirms toolchain installation and LSP server configuration success |
| `reports/VERIFICATION_REPORT.md` | Orchestrator or agent verifies task deliverables match acceptance criteria |
| `reports/PROJECT_SYNC_REPORT.md` | Cross-agent synchronization report for monorepo state (commits, builds, tests) |
| `reports/PR_STATUS_REPORT.md` | Pull request status tracking (CI checks, review status, merge conflicts) |

---

### GitHub Integration

Templates for GitHub Projects (Kanban), issue tracking, and PR workflows.

| File | Description |
|------|-------------|
| `github/PROJECT_SETUP.md` | Initialize GitHub Projects board with columns, automation, and field definitions |
| `github/KANBAN_SYNC_PROTOCOL.md` | Protocol for agents to update issue status on GitHub Projects board |
| `github/ISSUE_TEMPLATE.md` | Structured issue format with acceptance criteria, dependencies, and agent assignments |
| `github/PR_TEMPLATE.md` | Pull request format with changes summary, testing, and linked issues |
| `github/AGENT_SYNC_CHECKLIST.md` | Checklist for agents to sync local work with GitHub (commit, push, update issue) |

**Related**: `github-projects-guide.md` - Complete guide for using GitHub Projects with remote agents

---

### Scripts

Utility scripts for template compilation, validation, and generation.

| File | Description |
|------|-------------|
| `scripts/compile_template.py` | Compile templates by substituting variables (e.g., `{{LANGUAGE}}` → `rust`) |
| `scripts/validate_templates.py` | Validate template syntax, check for undefined variables, verify file references |
| `../scripts/enforce_delivery_protocol.py` | **MANDATORY**: Enforce document delivery protocol - validates messages, tracks ACKs |

**Note**: The enforcement script is in the skill's main `scripts/` directory, not `templates/scripts/`.

---

## Related Resources

### LSP Configuration
- [../references/lsp-servers-overview.md](../references/lsp-servers-overview.md) - Comprehensive list of LSP servers by language
- [../references/lsp-installation-guide.md](../references/lsp-installation-guide.md) - Step-by-step LSP installation and troubleshooting
- [../references/lsp-plugin-template.md](../references/lsp-plugin-template.md) - Claude Code plugin template for LSP integration

### Handoff Protocols
- [../../shared/references/handoff-protocols.md](../../shared/references/handoff-protocols.md) - Detailed handoff protocol specifications

### Skill Documentation
- [../SKILL.md](../SKILL.md) - Remote agent coordinator skill main documentation
- [../references/task-instruction-format.md](../references/task-instruction-format.md) - How to structure task instructions

---

## Template Usage Patterns

### Pattern 1: Single-Language Project Setup

```bash
# 1. Select toolchain
python scripts/compile_template.py \
  --template toolchain/PYTHON_TOOLCHAIN.md \
  --vars project_name=my-app language_version=3.12 \
  --output toolchain-my-app.md

# 2. Create agent environment config
python scripts/compile_template.py \
  --template claude-config/AGENT_ENVIRONMENT_SETUP.md \
  --vars toolchain=toolchain-my-app.md \
  --output agent-setup.md

# 3. Delegate task with handoff template
python scripts/compile_template.py \
  --template handoff/TASK_DELEGATION_TEMPLATE.md \
  --vars task_id=GH-42 agent=dev-agent-1 toolchain=toolchain-my-app.md \
  --output task-delegation-GH-42.md

# 4. Send to agent (via AI Maestro or manual)
# Agent receives task, responds with ACK_TEMPLATE, then COMPLETION_REPORT_TEMPLATE
```

### Pattern 2: Monorepo Cross-Platform Setup

```bash
# 1. Create monorepo base
python scripts/compile_template.py \
  --template monorepo/MONOREPO_BASE.md \
  --vars project_name=xls-cross-platform \
  --output monorepo-base.md

# 2. Compile toolchain composition (Rust + Python)
python scripts/compile_template.py \
  --template monorepo/MONOREPO_TOOLCHAIN_COMPOSITION.md \
  --vars toolchains=rust,python \
  --output monorepo-toolchains.md

# 3. Set up platform modules
python scripts/compile_template.py \
  --template platform/MACOS_MODULE.md \
  --vars module_name=file-watcher arch=arm64 \
  --output platform-macos.md

python scripts/compile_template.py \
  --template platform/LINUX_MODULE.md \
  --vars module_name=file-watcher arch=x64 \
  --output platform-linux.md

# 4. Create GitHub Projects board
python scripts/compile_template.py \
  --template github/PROJECT_SETUP.md \
  --vars project_name=xls-cross-platform \
  --output github-setup.md

# 5. Delegate module tasks to platform-specific agents
# Each agent uses TASK_DELEGATION_TEMPLATE with platform-specific configs
```

### Pattern 3: Continuous Integration Setup

```bash
# 1. Create CI matrix for monorepo
python scripts/compile_template.py \
  --template monorepo/MONOREPO_CI_MATRIX.md \
  --vars platforms=macos,linux,windows toolchains=rust,python \
  --output ci-matrix.md

# 2. Validate all templates before delegation
python scripts/validate_templates.py --all

# 3. Agent reports back with PR_STATUS_REPORT
# Orchestrator verifies with VERIFICATION_REPORT
```

---

## Template Variable Reference

Common variables used across templates:

| Variable | Type | Example | Used In |
|----------|------|---------|---------|
| `{{PROJECT_NAME}}` | string | `xls-cross-platform` | All templates |
| `{{TASK_ID}}` | string | `GH-42` | Handoff, reports |
| `{{LANGUAGE}}` | enum | `rust`, `python`, `javascript` | Toolchain templates |
| `{{LANGUAGE_VERSION}}` | version | `1.75`, `3.12`, `20` | Toolchain templates |
| `{{PLATFORM}}` | enum | `macos`, `linux`, `windows` | Platform modules |
| `{{ARCH}}` | enum | `x64`, `arm64`, `universal` | Platform modules |
| `{{AGENT_NAME}}` | string | `dev-agent-macos` | Handoff templates |
| `{{TIMESTAMP}}` | ISO 8601 | `2024-01-15T14:30:00Z` | All templates |

---

## Validation

Before using compiled templates:

```bash
# Validate single template
python scripts/validate_templates.py --template toolchain/PYTHON_TOOLCHAIN.md

# Validate all templates
python scripts/validate_templates.py --all

# Validate compiled output
python scripts/validate_templates.py --compiled output/toolchain-my-app.md
```

Validation checks:
- All `{{variables}}` are defined in variable table
- File references point to existing files
- YAML/JSON blocks are syntactically valid
- Markdown structure is well-formed
- No circular references between templates

---

## Maintenance

### Adding New Templates

1. **Create template file** in appropriate category directory
2. **Add variable table** at top with all `{{placeholders}}`
3. **Add to this index** with one-line description
4. **Update validation rules** in `scripts/validate_templates.py`
5. **Add usage example** to relevant section above
6. **Update related resources** if cross-references added

### Updating Existing Templates

1. **Maintain backward compatibility** - don't remove existing variables
2. **Update version field** in template header
3. **Update this index** if description changes
4. **Update SKILL.md** if usage patterns change
5. **Test with compile_template.py** before committing

---

## Support

For template questions or issues:
1. Check [../SKILL.md](../SKILL.md) for usage documentation
2. See [../references/](../references/) for detailed guides
3. Run validation scripts to diagnose problems
4. Check [../README.md](../README.md) for skill overview

---

**Last Updated**: 2024-01-15
**Template Version**: 1.0.0
**Total Templates**: 42 files
