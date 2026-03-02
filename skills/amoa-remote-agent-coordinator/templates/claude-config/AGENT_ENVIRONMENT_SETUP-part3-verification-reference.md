# Agent Environment Setup - Part 3: Verification & Reference

## Phase 5: Environment Verification

### 5.1 Comprehensive Verification Script

```bash
#!/usr/bin/env bash
# verify-environment.sh - Comprehensive environment verification

set -euo pipefail

PROJECT_ROOT="${1:?Project root required}"
TOOLCHAIN="${2:-$(python3 detect_language.py "$PROJECT_ROOT")}"

echo "========================================="
echo "Environment Verification"
echo "========================================="
echo "Project: $PROJECT_ROOT"
echo "Toolchain: $TOOLCHAIN"
echo ""

ERRORS=0

# Check 1: Toolchain installed
echo "1. Checking toolchain..."
case "$TOOLCHAIN" in
  python)
    if command -v python3 &>/dev/null && (command -v uv &>/dev/null || command -v pip &>/dev/null); then
      echo "   ✓ Python toolchain installed"
    else
      echo "   ✗ Python toolchain missing"
      ((ERRORS++))
    fi
    ;;
  nodejs)
    if command -v node &>/dev/null && (command -v pnpm &>/dev/null || command -v npm &>/dev/null); then
      echo "   ✓ Node.js toolchain installed"
    else
      echo "   ✗ Node.js toolchain missing"
      ((ERRORS++))
    fi
    ;;
  rust)
    if command -v rustc &>/dev/null && command -v cargo &>/dev/null; then
      echo "   ✓ Rust toolchain installed"
    else
      echo "   ✗ Rust toolchain missing"
      ((ERRORS++))
    fi
    ;;
  go)
    if command -v go &>/dev/null; then
      echo "   ✓ Go toolchain installed"
    else
      echo "   ✗ Go toolchain missing"
      ((ERRORS++))
    fi
    ;;
  cpp)
    if command -v g++ &>/dev/null || command -v clang++ &>/dev/null; then
      echo "   ✓ C++ toolchain installed"
    else
      echo "   ✗ C++ toolchain missing"
      ((ERRORS++))
    fi
    ;;
esac

# Check 2: LSP server installed
echo "2. Checking LSP server..."
LSP_CONFIG=$(jq -r ".lspServers.\"$TOOLCHAIN\".command" "$PROJECT_ROOT/.claude/settings.json" 2>/dev/null || echo "")
if [[ -n "$LSP_CONFIG" ]] && command -v "$LSP_CONFIG" &>/dev/null; then
  echo "   ✓ LSP server installed: $LSP_CONFIG ($(which $LSP_CONFIG))"
else
  echo "   ✗ LSP server missing or not configured"
  ((ERRORS++))
fi

# Check 3: Skills installed
echo "3. Checking Claude Code skills..."
if [[ -d "$PROJECT_ROOT/.claude/skills" ]]; then
  SKILL_COUNT=$(find "$PROJECT_ROOT/.claude/skills" -mindepth 1 -maxdepth 1 -type d -o -type l | wc -l)
  if [[ $SKILL_COUNT -gt 0 ]]; then
    echo "   ✓ Skills installed: $SKILL_COUNT"
    ls -1 "$PROJECT_ROOT/.claude/skills" | sed 's/^/     - /'
  else
    echo "   ⚠ No skills installed (may be normal for some toolchains)"
  fi
else
  echo "   ✗ Skills directory missing"
  ((ERRORS++))
fi

# Check 4: .claude/ directory structure
echo "4. Checking .claude/ directory..."
if [[ -d "$PROJECT_ROOT/.claude" ]]; then
  echo "   ✓ .claude/ directory exists"

  if [[ -f "$PROJECT_ROOT/.claude/settings.json" ]]; then
    echo "   ✓ settings.json exists"
    if jq empty "$PROJECT_ROOT/.claude/settings.json" 2>/dev/null; then
      echo "   ✓ settings.json is valid JSON"
    else
      echo "   ✗ settings.json is invalid JSON"
      ((ERRORS++))
    fi
  else
    echo "   ✗ settings.json missing"
    ((ERRORS++))
  fi

  if [[ -d "$PROJECT_ROOT/.claude/plugins/lsp-plugin" ]]; then
    echo "   ✓ LSP plugin directory exists"
  else
    echo "   ✗ LSP plugin directory missing"
    ((ERRORS++))
  fi
else
  echo "   ✗ .claude/ directory missing"
  ((ERRORS++))
fi

# Check 5: Commands configured
echo "5. Checking configured commands..."
TEST_CMD=$(jq -r '.projectSettings.testCommand' "$PROJECT_ROOT/.claude/settings.json" 2>/dev/null || echo "")
BUILD_CMD=$(jq -r '.projectSettings.buildCommand' "$PROJECT_ROOT/.claude/settings.json" 2>/dev/null || echo "")
if [[ -n "$TEST_CMD" ]]; then
  echo "   ✓ Test command: $TEST_CMD"
else
  echo "   ⚠ Test command not configured"
fi
if [[ -n "$BUILD_CMD" ]]; then
  echo "   ✓ Build command: $BUILD_CMD"
else
  echo "   ⚠ Build command not configured"
fi

# Summary
echo ""
echo "========================================="
if [[ $ERRORS -eq 0 ]]; then
  echo "✓ Environment verification PASSED"
  echo "All required components are installed and configured"
  exit 0
else
  echo "✗ Environment verification FAILED"
  echo "Found $ERRORS error(s) - see above for details"
  exit 1
fi
```

### 5.2 Quick Verification Checklist

```bash
# Quick verification commands
cat > {{PROJECT_ROOT}}/verify-quick.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

echo "Quick Environment Check"
echo "======================="

# Toolchain
which python3 || which node || which rustc || which go || which g++ || echo "No toolchain found"

# LSP
which pylsp || which pyright || which typescript-language-server || which rust-analyzer || which gopls || which clangd || echo "No LSP found"

# Skills
ls -1 ./.claude/skills/ 2>/dev/null || echo "No skills directory"

# Settings
cat ./.claude/settings.json | jq . 2>/dev/null || echo "Invalid or missing settings.json"

echo "======================="
echo "Done"
EOF

chmod +x {{PROJECT_ROOT}}/verify-quick.sh
```

## Complete Setup Script

Combine all phases into a single automated setup script:

```bash
#!/usr/bin/env bash
# complete-setup.sh - Complete agent environment setup

set -euo pipefail

PROJECT_ROOT="${1:?Project root required}"
ORCHESTRATOR_SKILLS="${2:-$HOME/.claude/skills}"

cd "$PROJECT_ROOT"

echo "========================================="
echo "Agent Environment Setup"
echo "========================================="
echo "Project: $PROJECT_ROOT"
echo "Orchestrator skills: $ORCHESTRATOR_SKILLS"
echo ""

# Phase 1: Detect and install toolchain
echo "[Phase 1] Installing toolchain..."
TOOLCHAIN=$(python3 detect_language.py "$PROJECT_ROOT")
echo "Detected toolchain: $TOOLCHAIN"
bash ../toolchain/install-scripts/install_${TOOLCHAIN}.sh
echo ""

# Phase 2: Install LSP server
echo "[Phase 2] Installing LSP server..."
python3 ../references/scripts/install_lsp.py --language "$TOOLCHAIN"
LSP_COMMAND=$(bash select_lsp.sh "$PROJECT_ROOT" | jq -r ".lspServers.\"$TOOLCHAIN\".command")
echo "Installed LSP: $LSP_COMMAND"
echo ""

# Phase 3: Install Claude Code skills
echo "[Phase 3] Installing Claude Code skills..."
bash install-skills.sh "$TOOLCHAIN" "$PROJECT_ROOT" "$ORCHESTRATOR_SKILLS"
echo ""

# Phase 4: Configure .claude/ directory
echo "[Phase 4] Configuring .claude/ directory..."
bash setup-claude-config.sh "$PROJECT_ROOT" "$TOOLCHAIN" "$LSP_COMMAND"
echo ""

# Phase 5: Verify environment
echo "[Phase 5] Verifying environment..."
bash verify-environment.sh "$PROJECT_ROOT" "$TOOLCHAIN"
echo ""

echo "========================================="
echo "Setup complete!"
echo "Agent environment ready for: $PROJECT_ROOT"
echo "========================================="
```

Usage:
```bash
bash complete-setup.sh {{PROJECT_ROOT}} {{ORCHESTRATOR_SKILLS_DIR}}
```

## Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `{{PROJECT_ROOT}}` | Project root directory | `/home/user/project` |
| `{{PROJECT_NAME}}` | Project name | `my-app` |
| `{{TOOLCHAIN_TYPE}}` | Toolchain identifier | `python`, `nodejs` |
| `{{LSP_COMMAND}}` | LSP server command | `pylsp` |
| `{{LSP_ARGS}}` | LSP server arguments | `["--stdio"]` |
| `{{ORCHESTRATOR_SKILLS_DIR}}` | Orchestrator skills path | `~/.claude/skills` |
| `{{TEST_COMMAND}}` | Test command | `uv run pytest` |
| `{{BUILD_COMMAND}}` | Build command | `uv build` |
| `{{FORMAT_COMMAND}}` | Format command | `uv run ruff format` |
| `{{LINT_COMMAND}}` | Lint command | `uv run ruff check` |

## Troubleshooting

### Toolchain Installation Fails

**Problem**: Toolchain installation script fails or hangs.

**Solution**:
1. Check network connectivity
2. Verify package manager works: `apt update` or `brew update`
3. Install manually following toolchain-specific guides
4. Check system requirements (disk space, permissions)

### LSP Server Not Found After Installation

**Problem**: LSP server installed but not in PATH.

**Solution**:
1. Source shell profile: `source ~/.bashrc` or `source ~/.zshrc`
2. Check installation location:
   - Python: `pipx list`
   - Node.js: `npm list -g --depth=0`
   - Rust: `rustup component list --installed`
3. Add to PATH manually if needed

### Skills Symlinks Broken

**Problem**: Skill symlinks point to non-existent directories.

**Solution**:
1. Verify orchestrator skills exist: `ls -la {{ORCHESTRATOR_SKILLS_DIR}}`
2. Remove broken symlinks: `find .claude/skills -xtype l -delete`
3. Re-run skill installation: `bash install-skills.sh`

### settings.json Invalid

**Problem**: settings.json has syntax errors.

**Solution**:
1. Validate JSON: `jq . .claude/settings.json`
2. Check for trailing commas, unquoted strings
3. Regenerate from template: `bash setup-claude-config.sh`

## Related Files

- [PROJECT_CLAUDE_CONFIG.md](./PROJECT_CLAUDE_CONFIG.md) - .claude/ directory template
- [TOOLCHAIN_SKILLS_MATRIX.md](./TOOLCHAIN_SKILLS_MATRIX.md) - Skills per toolchain
- [LSP_SELECTION_GUIDE.md](./LSP_SELECTION_GUIDE.md) - LSP server selection
- [../toolchain/TOOLCHAIN_DETECTION.md](../toolchain/TOOLCHAIN_DETECTION.md) - Language detection
- [../toolchain/TOOLCHAIN_INSTALLATION.md](../toolchain/TOOLCHAIN_INSTALLATION.md) - Toolchain install
- [../references/lsp-installation-guide.md](../references/lsp-installation-guide.md) - LSP install guide
- [../references/lsp-plugin-template.md](../references/lsp-plugin-template.md) - LSP plugin structure

---

**Previous**: [Part 2 - Skills & Project Configuration](./AGENT_ENVIRONMENT_SETUP-part2-skills-config.md)

**Back to Index**: [AGENT_ENVIRONMENT_SETUP.md](./AGENT_ENVIRONMENT_SETUP.md)
