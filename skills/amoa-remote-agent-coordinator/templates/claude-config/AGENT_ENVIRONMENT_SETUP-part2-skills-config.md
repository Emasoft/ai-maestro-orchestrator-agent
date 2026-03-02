# Agent Environment Setup - Part 2: Skills & Project Configuration

## Phase 3: Claude Code Skills Installation

### 3.1 Determine Required Skills

Reference: [TOOLCHAIN_SKILLS_MATRIX.md](./TOOLCHAIN_SKILLS_MATRIX.md)

Based on toolchain, determine which skills to install:

| Toolchain | Required Skills |
|-----------|-----------------|
| python | python-code-fixer, python-test-writer |
| nodejs | js-code-fixer, js-test-writer |
| rust | (none - LSP only) |
| go | (none - LSP only) |
| cpp | (none - LSP only) |

### 3.2 Install Skills

```bash
#!/usr/bin/env bash
# Phase 3: Install skills

PROJECT_ROOT="{{PROJECT_ROOT}}"
TOOLCHAIN="{{TOOLCHAIN_TYPE}}"
ORCHESTRATOR_SKILLS="{{ORCHESTRATOR_SKILLS_DIR}}"

# Create skills directory
mkdir -p "$PROJECT_ROOT/.claude/skills"

# Install skills based on toolchain
case "$TOOLCHAIN" in
  python)
    ln -sf "$ORCHESTRATOR_SKILLS/python-code-fixer" "$PROJECT_ROOT/.claude/skills/"
    ln -sf "$ORCHESTRATOR_SKILLS/python-test-writer" "$PROJECT_ROOT/.claude/skills/"
    echo "Installed: python-code-fixer, python-test-writer"
    ;;

  nodejs)
    ln -sf "$ORCHESTRATOR_SKILLS/js-code-fixer" "$PROJECT_ROOT/.claude/skills/"
    ln -sf "$ORCHESTRATOR_SKILLS/js-test-writer" "$PROJECT_ROOT/.claude/skills/"
    echo "Installed: js-code-fixer, js-test-writer"
    ;;

  *)
    echo "No language-specific skills required for $TOOLCHAIN"
    ;;
esac
```

### 3.3 Verify Skills

```bash
# List installed skills
ls -la {{PROJECT_ROOT}}/.claude/skills/

# Check skill structure
for skill in {{PROJECT_ROOT}}/.claude/skills/*/; do
  if [[ -f "$skill/SKILL.md" ]]; then
    echo "✓ Valid skill: $(basename $skill)"
  else
    echo "✗ Invalid skill: $(basename $skill) (missing SKILL.md)"
  fi
done
```

## Phase 4: Project Configuration

### 4.1 Create .claude/ Directory Structure

Reference: [PROJECT_CLAUDE_CONFIG.md](./PROJECT_CLAUDE_CONFIG.md)

```bash
#!/usr/bin/env bash
# Phase 4: Configure .claude/ directory

PROJECT_ROOT="{{PROJECT_ROOT}}"
mkdir -p "$PROJECT_ROOT/.claude/skills"
mkdir -p "$PROJECT_ROOT/.claude/plugins/lsp-plugin/.claude-plugin"
mkdir -p "$PROJECT_ROOT/.claude/plugins/lsp-plugin/hooks"
mkdir -p "$PROJECT_ROOT/.claude/plugins/lsp-plugin/scripts"
```

### 4.2 Generate settings.json

```bash
#!/usr/bin/env bash
# Generate settings.json

TOOLCHAIN="{{TOOLCHAIN_TYPE}}"
PROJECT_NAME="{{PROJECT_NAME}}"
LSP_COMMAND="{{LSP_COMMAND}}"
LSP_ARGS="{{LSP_ARGS}}"

cat > {{PROJECT_ROOT}}/.claude/settings.json <<EOF
{
  "agentOptions": {
    "contextWindowSize": 200000,
    "maxTokens": 8192,
    "temperature": 0.7
  },
  "projectSettings": {
    "name": "$PROJECT_NAME",
    "language": "$TOOLCHAIN",
    "toolchain": "$TOOLCHAIN",
    "testCommand": "$(get_test_command $TOOLCHAIN)",
    "buildCommand": "$(get_build_command $TOOLCHAIN)",
    "formatCommand": "$(get_format_command $TOOLCHAIN)",
    "lintCommand": "$(get_lint_command $TOOLCHAIN)"
  },
  "lspServers": {
    "$TOOLCHAIN": {
      "command": "$LSP_COMMAND",
      "args": $LSP_ARGS,
      "rootUri": "file://$PROJECT_ROOT"
    }
  },
  "skills": {
    "enabled": $(get_enabled_skills $TOOLCHAIN)
  },
  "plugins": {
    "enabled": ["lsp-plugin"]
  }
}
EOF

# Helper functions
get_test_command() {
  case "$1" in
    python) echo "uv run pytest tests/" ;;
    nodejs) echo "pnpm test" ;;
    rust) echo "cargo test" ;;
    go) echo "go test ./..." ;;
    cpp) echo "ctest" ;;
    *) echo "echo 'No test command configured'" ;;
  esac
}

get_build_command() {
  case "$1" in
    python) echo "uv build" ;;
    nodejs) echo "pnpm build" ;;
    rust) echo "cargo build --release" ;;
    go) echo "go build ./..." ;;
    cpp) echo "cmake --build build" ;;
    *) echo "echo 'No build command configured'" ;;
  esac
}

get_format_command() {
  case "$1" in
    python) echo "uv run ruff format --line-length=320 src/ tests/" ;;
    nodejs) echo "pnpm format" ;;
    rust) echo "cargo fmt" ;;
    go) echo "gofmt -w ." ;;
    cpp) echo "clang-format -i **/*.cpp **/*.h" ;;
    *) echo "echo 'No format command configured'" ;;
  esac
}

get_lint_command() {
  case "$1" in
    python) echo "uv run ruff check src/ tests/" ;;
    nodejs) echo "pnpm lint" ;;
    rust) echo "cargo clippy" ;;
    go) echo "golangci-lint run" ;;
    cpp) echo "clang-tidy **/*.cpp" ;;
    *) echo "echo 'No lint command configured'" ;;
  esac
}

get_enabled_skills() {
  case "$1" in
    python) echo '["python-code-fixer", "python-test-writer"]' ;;
    nodejs) echo '["js-code-fixer", "js-test-writer"]' ;;
    *) echo '[]' ;;
  esac
}
```

### 4.3 Configure LSP Plugin

Reference: [../references/lsp-plugin-template.md](../references/lsp-plugin-template.md)

```bash
#!/usr/bin/env bash
# Configure LSP plugin

PLUGIN_DIR="{{PROJECT_ROOT}}/.claude/plugins/lsp-plugin"
LSP_COMMAND="{{LSP_COMMAND}}"

# Create plugin.json
cat > "$PLUGIN_DIR/.claude-plugin/plugin.json" <<EOF
{
  "name": "lsp-plugin",
  "version": "1.0.0",
  "description": "LSP server integration for $LSP_COMMAND",
  "author": "orchestrator",
  "type": "plugin"
}
EOF

# Create hooks.json
cat > "$PLUGIN_DIR/hooks/hooks.json" <<EOF
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\${CLAUDE_PLUGIN_ROOT}/scripts/start-lsp.sh"
          }
        ]
      }
    ]
  }
}
EOF

# Create start-lsp.sh
cat > "$PLUGIN_DIR/scripts/start-lsp.sh" <<'SCRIPT'
#!/usr/bin/env bash
set -euo pipefail

LSP_COMMAND="{{LSP_COMMAND}}"
PROJECT_ROOT="{{PROJECT_ROOT}}"

if command -v "$LSP_COMMAND" &>/dev/null; then
  echo "[LSP] Starting $LSP_COMMAND for $PROJECT_ROOT"
  # LSP server management (implementation varies)
else
  echo "[LSP] Warning: $LSP_COMMAND not found"
fi
SCRIPT

chmod +x "$PLUGIN_DIR/scripts/start-lsp.sh"

echo "LSP plugin configured at $PLUGIN_DIR"
```

### 4.4 Create Project-Specific CLAUDE.md

```bash
#!/usr/bin/env bash
# Create project-specific CLAUDE.md

cat > {{PROJECT_ROOT}}/CLAUDE.md <<EOF
# Project: {{PROJECT_NAME}}

## Toolchain
- Language: {{TOOLCHAIN_TYPE}}
- Build: {{BUILD_COMMAND}}
- Test: {{TEST_COMMAND}}
- Format: {{FORMAT_COMMAND}}
- Lint: {{LINT_COMMAND}}

## LSP Server
- Command: {{LSP_COMMAND}}
- Args: {{LSP_ARGS}}

## Claude Code Skills
$(ls {{PROJECT_ROOT}}/.claude/skills/)

## Development Commands

### Testing
\`\`\`bash
{{TEST_COMMAND}}
\`\`\`

### Building
\`\`\`bash
{{BUILD_COMMAND}}
\`\`\`

### Formatting
\`\`\`bash
{{FORMAT_COMMAND}}
\`\`\`

### Linting
\`\`\`bash
{{LINT_COMMAND}}
\`\`\`

## Project Structure
\`\`\`
$(tree -L 2 {{PROJECT_ROOT}})
\`\`\`
EOF
```

---

**Previous**: [Part 1 - Toolchain & LSP Installation](./AGENT_ENVIRONMENT_SETUP-part1-toolchain-lsp.md)

**Next**: [Part 3 - Verification & Reference](./AGENT_ENVIRONMENT_SETUP-part3-verification-reference.md)
