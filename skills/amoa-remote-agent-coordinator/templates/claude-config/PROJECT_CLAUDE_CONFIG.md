# Project-Level Claude Code Configuration Template

## Overview

This template configures the `.claude/` directory structure for a remote project workspace, enabling Claude Code agents to work with project-specific skills, plugins, and LSP servers.

## Directory Structure

```
{{PROJECT_ROOT}}/.claude/
├── settings.json          # Project-specific Claude Code settings
├── skills/                # Project-specific skills (symlinked or copied)
│   ├── python-code-fixer/ # (if Python project)
│   ├── js-code-fixer/     # (if JavaScript/TypeScript project)
│   └── ...
├── plugins/               # Project-specific plugins
│   └── lsp-plugin/        # LSP server integration
└── CLAUDE.md              # Project instructions (optional override)
```

## Template: settings.json

```json
{
  "agentOptions": {
    "contextWindowSize": {{CONTEXT_WINDOW_SIZE:-200000}},
    "maxTokens": {{MAX_TOKENS:-8192}},
    "temperature": {{TEMPERATURE:-0.7}}
  },
  "projectSettings": {
    "name": "{{PROJECT_NAME}}",
    "language": "{{PRIMARY_LANGUAGE}}",
    "toolchain": "{{TOOLCHAIN_TYPE}}",
    "testCommand": "{{TEST_COMMAND}}",
    "buildCommand": "{{BUILD_COMMAND}}",
    "formatCommand": "{{FORMAT_COMMAND}}",
    "lintCommand": "{{LINT_COMMAND}}"
  },
  "lspServers": {
    "{{PRIMARY_LANGUAGE}}": {
      "command": "{{LSP_COMMAND}}",
      "args": {{LSP_ARGS:-[]}},
      "rootUri": "{{PROJECT_ROOT}}"
    }
  },
  "skills": {
    "enabled": {{ENABLED_SKILLS:-[]}},
    "disabled": {{DISABLED_SKILLS:-[]}}
  },
  "plugins": {
    "enabled": {{ENABLED_PLUGINS:-[]}},
    "disabled": {{DISABLED_PLUGINS:-[]}}
  }
}
```

## Skills Installation

Project-specific skills should be symlinked or copied from the orchestrator's skill library:

```bash
# Symlink approach (preferred - always up to date)
ln -s {{ORCHESTRATOR_SKILLS_DIR}}/{{SKILL_NAME}} {{PROJECT_ROOT}}/.claude/skills/{{SKILL_NAME}}

# Copy approach (isolated - won't receive updates)
cp -r {{ORCHESTRATOR_SKILLS_DIR}}/{{SKILL_NAME}} {{PROJECT_ROOT}}/.claude/skills/{{SKILL_NAME}}
```

**Recommendation**: Use symlinks for standard skills, copy for customized project-specific skills.

## Plugins Installation

### LSP Plugin Template

See: [../references/lsp-plugin-template.md](../references/lsp-plugin-template.md) for complete LSP plugin structure.

LSP plugin directory structure:
```
{{PROJECT_ROOT}}/.claude/plugins/lsp-plugin/
├── .claude-plugin/
│   └── plugin.json
├── hooks/
│   └── hooks.json
└── scripts/
    ├── start-lsp.sh
    ├── stop-lsp.sh
    └── query-lsp.sh
```

The plugin.json should reference the LSP server configured in settings.json.

## Integration with Toolchain Selection

The `.claude/settings.json` file integrates with toolchain templates:

1. **Toolchain Detection**: Read from `{{PROJECT_ROOT}}/.toolchain` or auto-detect
2. **Skill Selection**: Install skills based on [TOOLCHAIN_SKILLS_MATRIX.md](./TOOLCHAIN_SKILLS_MATRIX.md)
3. **LSP Selection**: Configure LSP based on [LSP_SELECTION_GUIDE.md](./LSP_SELECTION_GUIDE.md)
4. **Environment Setup**: Complete setup using [AGENT_ENVIRONMENT_SETUP.md](./AGENT_ENVIRONMENT_SETUP.md)

## Example Configurations

### Python Project

```json
{
  "projectSettings": {
    "name": "my-python-app",
    "language": "python",
    "toolchain": "python",
    "testCommand": "uv run pytest tests/",
    "buildCommand": "uv build",
    "formatCommand": "uv run ruff format --line-length=320 src/ tests/",
    "lintCommand": "uv run ruff check src/ tests/"
  },
  "lspServers": {
    "python": {
      "command": "pylsp",
      "args": [],
      "rootUri": "file://{{PROJECT_ROOT}}"
    }
  },
  "skills": {
    "enabled": ["python-code-fixer", "python-test-writer"]
  }
}
```

### JavaScript/TypeScript Project

```json
{
  "projectSettings": {
    "name": "my-web-app",
    "language": "typescript",
    "toolchain": "nodejs",
    "testCommand": "pnpm test",
    "buildCommand": "pnpm build",
    "formatCommand": "pnpm format",
    "lintCommand": "pnpm lint"
  },
  "lspServers": {
    "typescript": {
      "command": "typescript-language-server",
      "args": ["--stdio"],
      "rootUri": "file://{{PROJECT_ROOT}}"
    }
  },
  "skills": {
    "enabled": ["js-code-fixer", "js-test-writer"]
  }
}
```

### Rust Project

```json
{
  "projectSettings": {
    "name": "my-rust-app",
    "language": "rust",
    "toolchain": "rust",
    "testCommand": "cargo test",
    "buildCommand": "cargo build --release",
    "formatCommand": "cargo fmt",
    "lintCommand": "cargo clippy"
  },
  "lspServers": {
    "rust": {
      "command": "rust-analyzer",
      "args": [],
      "rootUri": "file://{{PROJECT_ROOT}}"
    }
  },
  "skills": {
    "enabled": []
  }
}
```

## Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `{{PROJECT_ROOT}}` | Absolute path to project root | `/home/user/projects/my-app` |
| `{{PROJECT_NAME}}` | Project name | `my-app` |
| `{{PRIMARY_LANGUAGE}}` | Main programming language | `python`, `typescript`, `rust` |
| `{{TOOLCHAIN_TYPE}}` | Toolchain identifier | `python`, `nodejs`, `rust`, `go`, `cpp` |
| `{{TEST_COMMAND}}` | Command to run tests | `uv run pytest tests/` |
| `{{BUILD_COMMAND}}` | Command to build project | `uv build` |
| `{{FORMAT_COMMAND}}` | Command to format code | `uv run ruff format` |
| `{{LINT_COMMAND}}` | Command to lint code | `uv run ruff check` |
| `{{LSP_COMMAND}}` | LSP server executable | `pylsp`, `typescript-language-server` |
| `{{LSP_ARGS}}` | LSP server arguments | `["--stdio"]` |
| `{{ORCHESTRATOR_SKILLS_DIR}}` | Path to orchestrator skills | `~/.claude/skills` |
| `{{ENABLED_SKILLS}}` | List of enabled skills | `["python-code-fixer"]` |
| `{{ENABLED_PLUGINS}}` | List of enabled plugins | `["lsp-plugin"]` |
| `{{CONTEXT_WINDOW_SIZE}}` | Agent context window | `200000` |
| `{{MAX_TOKENS}}` | Max output tokens | `8192` |
| `{{TEMPERATURE}}` | Sampling temperature | `0.7` |

## Setup Script

A setup script should be provided to initialize the `.claude/` directory:

```bash
#!/usr/bin/env bash
# setup-claude-config.sh

PROJECT_ROOT="{{PROJECT_ROOT}}"
TOOLCHAIN="{{TOOLCHAIN_TYPE}}"
ORCHESTRATOR_SKILLS="{{ORCHESTRATOR_SKILLS_DIR}}"

# Create directory structure
mkdir -p "$PROJECT_ROOT/.claude/skills"
mkdir -p "$PROJECT_ROOT/.claude/plugins"

# Copy settings template
cat > "$PROJECT_ROOT/.claude/settings.json" <<EOF
{
  "projectSettings": {
    "name": "{{PROJECT_NAME}}",
    "language": "{{PRIMARY_LANGUAGE}}",
    "toolchain": "$TOOLCHAIN"
  }
}
EOF

# Symlink skills based on toolchain
case "$TOOLCHAIN" in
  python)
    ln -s "$ORCHESTRATOR_SKILLS/python-code-fixer" "$PROJECT_ROOT/.claude/skills/"
    ln -s "$ORCHESTRATOR_SKILLS/python-test-writer" "$PROJECT_ROOT/.claude/skills/"
    ;;
  nodejs)
    ln -s "$ORCHESTRATOR_SKILLS/js-code-fixer" "$PROJECT_ROOT/.claude/skills/"
    ln -s "$ORCHESTRATOR_SKILLS/js-test-writer" "$PROJECT_ROOT/.claude/skills/"
    ;;
esac

echo "Claude Code configuration initialized at $PROJECT_ROOT/.claude/"
```

## Verification

After setup, verify the configuration:

```bash
# Check directory structure
ls -la {{PROJECT_ROOT}}/.claude/

# Verify settings.json syntax
cat {{PROJECT_ROOT}}/.claude/settings.json | jq .

# Check skill symlinks
ls -la {{PROJECT_ROOT}}/.claude/skills/

# Verify LSP server is installed and accessible
which {{LSP_COMMAND}}
{{LSP_COMMAND}} --version
```

## Troubleshooting

### Skills Not Found

**Problem**: Claude Code cannot find project-specific skills.

**Solution**:
1. Verify symlinks: `ls -la {{PROJECT_ROOT}}/.claude/skills/`
2. Check orchestrator skills exist: `ls -la {{ORCHESTRATOR_SKILLS_DIR}}/`
3. Re-run setup script

### LSP Server Not Starting

**Problem**: LSP server fails to start or connect.

**Solution**:
1. Verify LSP installed: `which {{LSP_COMMAND}}`
2. Test LSP manually: `{{LSP_COMMAND}} {{LSP_ARGS}}`
3. Check logs: `{{PROJECT_ROOT}}/.claude/plugins/lsp-plugin/logs/`
4. See: [LSP_SELECTION_GUIDE.md](./LSP_SELECTION_GUIDE.md) for troubleshooting

### Settings Not Applied

**Problem**: Changes to settings.json not taking effect.

**Solution**:
1. Validate JSON syntax: `jq . {{PROJECT_ROOT}}/.claude/settings.json`
2. Restart Claude Code agent
3. Check for global settings override in `~/.claude/settings.json`

## Related Files

- [TOOLCHAIN_SKILLS_MATRIX.md](./TOOLCHAIN_SKILLS_MATRIX.md) - Skill selection per toolchain
- [LSP_SELECTION_GUIDE.md](./LSP_SELECTION_GUIDE.md) - LSP server selection guide
- [AGENT_ENVIRONMENT_SETUP.md](./AGENT_ENVIRONMENT_SETUP.md) - Complete agent setup
- [../references/lsp-plugin-template.md](../references/lsp-plugin-template.md) - LSP plugin structure
