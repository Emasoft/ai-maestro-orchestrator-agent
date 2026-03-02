# Toolchain Skills Matrix

## Overview

This matrix defines which Claude Code skills and plugins should be installed for each toolchain type. Use this as a reference when setting up project-specific `.claude/` configurations.

## Skills Installation Matrix

| Toolchain | Primary Language | Required Skills | Optional Skills | LSP Server | LSP Plugin |
|-----------|------------------|-----------------|-----------------|------------|------------|
| **python** | Python | `python-code-fixer`<br>`python-test-writer` | `dependency-management` | `pylsp` or `pyright` | ✓ |
| **nodejs** | JavaScript/TypeScript | `js-code-fixer`<br>`js-test-writer` | `dependency-management` | `typescript-language-server` | ✓ |
| **rust** | Rust | - | `dependency-management` | `rust-analyzer` | ✓ |
| **go** | Go | - | `dependency-management` | `gopls` | ✓ |
| **cpp** | C++ | - | `dependency-management` | `clangd` | ✓ |
| **java** | Java | - | `dependency-management` | `jdtls` | ✓ |
| **ruby** | Ruby | - | `dependency-management` | `solargraph` | ✓ |
| **php** | PHP | - | `dependency-management` | `intelephense` | ✓ |
| **csharp** | C# | - | `dependency-management` | `omnisharp` | ✓ |
| **swift** | Swift | - | `dependency-management` | `sourcekit-lsp` | ✓ |

## Detailed Skill Descriptions

### python-code-fixer

**Purpose**: Format, lint, and type-check Python code.

**Commands**:
- Format: `uv run ruff format --line-length=320`
- Lint: `uv run ruff check --fix`
- Type check: `uv run mypy`

**When to install**: All Python projects.

**Configuration**:
```json
{
  "skills": {
    "enabled": ["python-code-fixer"]
  },
  "projectSettings": {
    "formatCommand": "uv run ruff format --line-length=320 src/ tests/",
    "lintCommand": "uv run ruff check src/ tests/"
  }
}
```

### python-test-writer

**Purpose**: Generate and maintain pytest tests for Python code.

**Commands**:
- Generate tests: `uv run pytest --generate`
- Run tests: `uv run pytest tests/`

**When to install**: Python projects with test requirements.

**Configuration**:
```json
{
  "skills": {
    "enabled": ["python-test-writer"]
  },
  "projectSettings": {
    "testCommand": "uv run pytest tests/"
  }
}
```

### js-code-fixer

**Purpose**: Format, lint, and type-check JavaScript/TypeScript code.

**Commands**:
- Format: `pnpm format` (prettier)
- Lint: `pnpm lint` (eslint)
- Type check: `pnpm type-check` (tsc)

**When to install**: All JavaScript/TypeScript projects.

**Configuration**:
```json
{
  "skills": {
    "enabled": ["js-code-fixer"]
  },
  "projectSettings": {
    "formatCommand": "pnpm format",
    "lintCommand": "pnpm lint"
  }
}
```

### js-test-writer

**Purpose**: Generate and maintain tests for JavaScript/TypeScript code.

**Commands**:
- Generate tests: `pnpm test:generate`
- Run tests: `pnpm test`

**When to install**: JavaScript/TypeScript projects with test requirements.

**Configuration**:
```json
{
  "skills": {
    "enabled": ["js-test-writer"]
  },
  "projectSettings": {
    "testCommand": "pnpm test"
  }
}
```

### dependency-management

**Purpose**: Manage project dependencies and updates.

**Commands**: Toolchain-specific (pip, npm, cargo, go mod, etc.)

**When to install**: Optional for all projects where dependency management is critical.

**Configuration**:
```json
{
  "skills": {
    "enabled": ["dependency-management"]
  }
}
```

## LSP Server Matrix

See: [LSP_SELECTION_GUIDE.md](./LSP_SELECTION_GUIDE.md) for detailed LSP server installation and configuration.

### Python LSP Options

| LSP Server | Installation | Features | Recommendation |
|------------|--------------|----------|----------------|
| `pylsp` | `pipx install python-lsp-server` | Full-featured | General use |
| `pyright` | `npm install -g pyright` | Fast type checking | Type-heavy projects |

### JavaScript/TypeScript LSP

| LSP Server | Installation | Features | Recommendation |
|------------|--------------|----------|----------------|
| `typescript-language-server` | `npm install -g typescript-language-server` | Full TS support | All JS/TS projects |

### Other Languages

| Language | LSP Server | Installation |
|----------|------------|--------------|
| Rust | `rust-analyzer` | `rustup component add rust-analyzer` |
| Go | `gopls` | `go install golang.org/x/tools/gopls@latest` |
| C++ | `clangd` | `brew install llvm` or system package |
| Java | `jdtls` | Download from Eclipse JDT |
| Ruby | `solargraph` | `gem install solargraph` |
| PHP | `intelephense` | `npm install -g intelephense` |
| C# | `omnisharp` | Download from OmniSharp releases |
| Swift | `sourcekit-lsp` | Included with Xcode/Swift toolchain |

## Plugin Matrix

| Plugin | Purpose | Required for Toolchains | Installation |
|--------|---------|------------------------|--------------|
| `lsp-plugin` | LSP server integration | All toolchains | See [../references/lsp-plugin-template.md](../references/lsp-plugin-template.md) |
| `ai-maestro-messaging-hook` | Inter-agent messaging | Orchestrator only | See orchestrator config |

## Skill Installation Script

```bash
#!/usr/bin/env bash
# install-skills.sh - Install skills based on toolchain

TOOLCHAIN="{{TOOLCHAIN_TYPE}}"
PROJECT_ROOT="{{PROJECT_ROOT}}"
ORCHESTRATOR_SKILLS="{{ORCHESTRATOR_SKILLS_DIR}}"
SKILLS_DIR="$PROJECT_ROOT/.claude/skills"

mkdir -p "$SKILLS_DIR"

case "$TOOLCHAIN" in
  python)
    echo "Installing Python skills..."
    ln -sf "$ORCHESTRATOR_SKILLS/python-code-fixer" "$SKILLS_DIR/"
    ln -sf "$ORCHESTRATOR_SKILLS/python-test-writer" "$SKILLS_DIR/"
    echo "Installed: python-code-fixer, python-test-writer"
    ;;

  nodejs)
    echo "Installing JavaScript/TypeScript skills..."
    ln -sf "$ORCHESTRATOR_SKILLS/js-code-fixer" "$SKILLS_DIR/"
    ln -sf "$ORCHESTRATOR_SKILLS/js-test-writer" "$SKILLS_DIR/"
    echo "Installed: js-code-fixer, js-test-writer"
    ;;

  rust|go|cpp|java|ruby|php|csharp|swift)
    echo "No specific skills required for $TOOLCHAIN"
    echo "LSP server provides code intelligence"
    ;;

  *)
    echo "Unknown toolchain: $TOOLCHAIN"
    exit 1
    ;;
esac

# Optional: Install dependency-management for all
if [[ "{{INSTALL_DEPENDENCY_MANAGEMENT}}" == "true" ]]; then
  ln -sf "$ORCHESTRATOR_SKILLS/dependency-management" "$SKILLS_DIR/"
  echo "Installed: dependency-management"
fi

echo "Skills installation complete"
ls -la "$SKILLS_DIR"
```

## Usage Examples

### Example 1: Python Project Setup

```bash
# Set variables
export TOOLCHAIN_TYPE="python"
export PROJECT_ROOT="/home/user/my-python-app"
export ORCHESTRATOR_SKILLS_DIR="$HOME/.claude/skills"

# Install skills
bash install-skills.sh

# Verify installation
ls -la $PROJECT_ROOT/.claude/skills/
# Expected output:
# python-code-fixer -> /home/user/.claude/skills/python-code-fixer
# python-test-writer -> /home/user/.claude/skills/python-test-writer
```

### Example 2: TypeScript Project Setup

```bash
# Set variables
export TOOLCHAIN_TYPE="nodejs"
export PROJECT_ROOT="/home/user/my-web-app"
export ORCHESTRATOR_SKILLS_DIR="$HOME/.claude/skills"

# Install skills
bash install-skills.sh

# Verify installation
ls -la $PROJECT_ROOT/.claude/skills/
# Expected output:
# js-code-fixer -> /home/user/.claude/skills/js-code-fixer
# js-test-writer -> /home/user/.claude/skills/js-test-writer
```

### Example 3: Rust Project Setup

```bash
# Set variables
export TOOLCHAIN_TYPE="rust"
export PROJECT_ROOT="/home/user/my-rust-app"
export ORCHESTRATOR_SKILLS_DIR="$HOME/.claude/skills"

# Install skills (none required, uses LSP)
bash install-skills.sh

# Install LSP server
rustup component add rust-analyzer

# Verify LSP installation
which rust-analyzer
rust-analyzer --version
```

## Skill Selection Decision Tree

```
1. Identify primary language
   ├─ Python? → Install python-code-fixer, python-test-writer
   ├─ JavaScript/TypeScript? → Install js-code-fixer, js-test-writer
   └─ Other? → Skip language-specific skills, use LSP only

2. Identify secondary languages (if multi-language project)
   └─ Install skills for each language

3. Determine if dependency management needed
   ├─ Complex dependencies? → Install dependency-management
   └─ Simple dependencies? → Skip

4. Always install LSP plugin
   └─ Install and configure LSP server for primary language
```

## Multi-Language Projects

For projects with multiple languages, install skills for each language:

```json
{
  "projectSettings": {
    "name": "fullstack-app",
    "language": "multi",
    "toolchain": "multi"
  },
  "skills": {
    "enabled": [
      "python-code-fixer",
      "python-test-writer",
      "js-code-fixer",
      "js-test-writer",
      "dependency-management"
    ]
  },
  "lspServers": {
    "python": {
      "command": "pylsp",
      "rootUri": "file://{{PROJECT_ROOT}}/backend"
    },
    "typescript": {
      "command": "typescript-language-server",
      "args": ["--stdio"],
      "rootUri": "file://{{PROJECT_ROOT}}/frontend"
    }
  }
}
```

## Skill Update Policy

**Symlinked skills**: Automatically updated when orchestrator updates its skill library.

**Copied skills**: Must be manually updated or re-copied from orchestrator.

**Recommendation**: Use symlinks for standard skills to ensure agents always have latest versions.

## Verification

After installation, verify skills are accessible:

```bash
# List installed skills
ls -la {{PROJECT_ROOT}}/.claude/skills/

# Check skill structure
for skill in {{PROJECT_ROOT}}/.claude/skills/*/; do
  echo "Checking $skill"
  ls -la "$skill"
  cat "$skill/SKILL.md" | head -n 20
done

# Verify LSP servers
for lsp in pylsp pyright typescript-language-server rust-analyzer gopls clangd; do
  if which $lsp &>/dev/null; then
    echo "$lsp: INSTALLED ($(which $lsp))"
  else
    echo "$lsp: NOT INSTALLED"
  fi
done
```

## Related Files

- [PROJECT_CLAUDE_CONFIG.md](./PROJECT_CLAUDE_CONFIG.md) - Project .claude/ directory structure
- [LSP_SELECTION_GUIDE.md](./LSP_SELECTION_GUIDE.md) - LSP server selection and installation
- [AGENT_ENVIRONMENT_SETUP.md](./AGENT_ENVIRONMENT_SETUP.md) - Complete environment setup
- [../references/lsp-servers-overview.md](../references/lsp-servers-overview.md) - LSP server comparison
- [../references/lsp-installation-guide.md](../references/lsp-installation-guide.md) - LSP installation procedures
