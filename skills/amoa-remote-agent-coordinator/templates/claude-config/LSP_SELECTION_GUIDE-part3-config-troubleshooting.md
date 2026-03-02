# LSP Selection Guide - Part 3: Configuration and Troubleshooting

## Per-Project Override Configuration

Projects can override the auto-detected LSP server:

### Override via .toolchain file

```bash
# Create .toolchain file
cat > {{PROJECT_ROOT}}/.toolchain <<EOF
python
EOF
```

### Override via settings.json

```json
{
  "projectSettings": {
    "language": "python",
    "languageOverride": true
  },
  "lspServers": {
    "python": {
      "command": "pyright",
      "args": ["--stdio"],
      "rootUri": "file://{{PROJECT_ROOT}}"
    }
  }
}
```

### Override via environment variable

```bash
export CLAUDE_LSP_OVERRIDE="pyright"
```

The override precedence (highest to lowest):
1. Environment variable: `CLAUDE_LSP_OVERRIDE`
2. settings.json with `languageOverride: true`
3. .toolchain file
4. Auto-detection

## Multi-Language Project LSP Configuration

For projects with multiple languages, configure multiple LSP servers:

```json
{
  "projectSettings": {
    "name": "fullstack-app",
    "language": "multi"
  },
  "lspServers": {
    "python": {
      "command": "pylsp",
      "args": [],
      "rootUri": "file://{{PROJECT_ROOT}}/backend",
      "workspaceFolder": "backend"
    },
    "typescript": {
      "command": "typescript-language-server",
      "args": ["--stdio"],
      "rootUri": "file://{{PROJECT_ROOT}}/frontend",
      "workspaceFolder": "frontend"
    },
    "rust": {
      "command": "rust-analyzer",
      "args": [],
      "rootUri": "file://{{PROJECT_ROOT}}/services",
      "workspaceFolder": "services"
    }
  }
}
```

## LSP Server Verification

After installation and configuration, verify the LSP server:

```bash
#!/usr/bin/env bash
# verify-lsp.sh

LSP_COMMAND="${1:?LSP command required}"

echo "Verifying LSP server: $LSP_COMMAND"

# Check if installed
if ! command -v "$LSP_COMMAND" &>/dev/null; then
  echo "ERROR: $LSP_COMMAND not found in PATH"
  exit 1
fi

echo "OK $LSP_COMMAND found at: $(which $LSP_COMMAND)"

# Check version
if $LSP_COMMAND --version &>/dev/null; then
  echo "OK Version: $($LSP_COMMAND --version)"
else
  echo "WARNING Could not determine version"
fi

# Test LSP initialization (language-specific)
case "$LSP_COMMAND" in
  pylsp|pyright|typescript-language-server)
    echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"rootUri":"file:///tmp"}}' | \
      $LSP_COMMAND --stdio 2>/dev/null | head -n 1
    if [[ $? -eq 0 ]]; then
      echo "OK LSP server responds to initialize request"
    else
      echo "WARNING LSP server did not respond (may be normal for some servers)"
    fi
    ;;
esac

echo "LSP verification complete"
```

Usage:
```bash
bash verify-lsp.sh pylsp
bash verify-lsp.sh typescript-language-server
```

## Troubleshooting

### LSP Server Not Found

**Problem**: `command not found: <lsp-server>`

**Solution**:
1. Verify installation: See [../references/lsp-installation-guide.md](../references/lsp-installation-guide.md)
2. Check PATH: `echo $PATH`
3. For language-specific package managers:
   - Python: `pipx list` or `pip list`
   - Node.js: `npm list -g --depth=0`
   - Rust: `rustup component list --installed`
   - Go: `ls $(go env GOPATH)/bin`

### LSP Server Not Starting

**Problem**: LSP server installed but not starting.

**Solution**:
1. Test manually: `<lsp-command> --stdio`
2. Check logs: `{{PROJECT_ROOT}}/.claude/plugins/lsp-plugin/logs/`
3. Verify configuration: `cat {{PROJECT_ROOT}}/.claude/settings.json | jq .lspServers`

### Wrong LSP Server Selected

**Problem**: Auto-detection selected wrong language/LSP server.

**Solution**:
1. Create `.toolchain` file with correct language
2. Override in settings.json with `languageOverride: true`
3. Set environment variable: `export CLAUDE_LSP_OVERRIDE="<lsp-command>"`

### Multiple Languages Conflict

**Problem**: Project has multiple languages, LSP servers conflict.

**Solution**:
1. Configure separate `rootUri` for each LSP server
2. Use `workspaceFolder` to isolate LSP servers
3. See "Multi-Language Project LSP Configuration" section above

---

**Previous**: [Part 2 - LSP Selection Scripts](./LSP_SELECTION_GUIDE-part2-selection-scripts.md)

**Back to**: [LSP Selection Guide (Index)](./LSP_SELECTION_GUIDE.md)
