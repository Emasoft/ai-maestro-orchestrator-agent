# LSP Selection Guide - Part 2: LSP Selection Scripts

## LSP Selection Script

```bash
#!/usr/bin/env bash
# select_lsp.sh - Select and configure LSP server for project

set -euo pipefail

PROJECT_ROOT="${1:?Project root required}"
LANGUAGE="${2:-$(python3 detect_language.py "$PROJECT_ROOT")}"

echo "Detected language: $LANGUAGE"

# Select LSP server based on language
case "$LANGUAGE" in
  python)
    LSP_COMMAND="pylsp"
    LSP_ARGS="[]"
    INSTALL_CMD="pipx install python-lsp-server"
    ;;

  nodejs)
    LSP_COMMAND="typescript-language-server"
    LSP_ARGS='["--stdio"]'
    INSTALL_CMD="npm install -g typescript-language-server typescript"
    ;;

  rust)
    LSP_COMMAND="rust-analyzer"
    LSP_ARGS="[]"
    INSTALL_CMD="rustup component add rust-analyzer"
    ;;

  go)
    LSP_COMMAND="gopls"
    LSP_ARGS="[]"
    INSTALL_CMD="go install golang.org/x/tools/gopls@latest"
    ;;

  cpp)
    LSP_COMMAND="clangd"
    LSP_ARGS="[]"
    INSTALL_CMD="brew install llvm"  # or apt-get install clangd
    ;;

  java)
    LSP_COMMAND="jdtls"
    LSP_ARGS="[]"
    INSTALL_CMD="echo 'Download from https://download.eclipse.org/jdtls/'"
    ;;

  ruby)
    LSP_COMMAND="solargraph"
    LSP_ARGS='["stdio"]'
    INSTALL_CMD="gem install solargraph"
    ;;

  php)
    LSP_COMMAND="intelephense"
    LSP_ARGS='["--stdio"]'
    INSTALL_CMD="npm install -g intelephense"
    ;;

  csharp)
    LSP_COMMAND="omnisharp"
    LSP_ARGS="[]"
    INSTALL_CMD="echo 'Download from https://github.com/OmniSharp/omnisharp-roslyn'"
    ;;

  swift)
    LSP_COMMAND="sourcekit-lsp"
    LSP_ARGS="[]"
    INSTALL_CMD="echo 'Included with Swift toolchain'"
    ;;

  *)
    echo "Unknown language: $LANGUAGE"
    exit 1
    ;;
esac

# Check if LSP server is installed
if ! command -v "$LSP_COMMAND" &>/dev/null; then
  echo "LSP server '$LSP_COMMAND' not found"
  echo "Install with: $INSTALL_CMD"
  exit 1
fi

# Output LSP configuration
cat <<EOF
{
  "lspServers": {
    "$LANGUAGE": {
      "command": "$LSP_COMMAND",
      "args": $LSP_ARGS,
      "rootUri": "file://$PROJECT_ROOT"
    }
  }
}
EOF
```

Usage:
```bash
bash select_lsp.sh {{PROJECT_ROOT}}
# Output: JSON configuration for settings.json
```

## Integration with Toolchain Templates

The LSP selection integrates with toolchain templates:

```bash
# 1. Detect language
LANGUAGE=$(python3 detect_language.py {{PROJECT_ROOT}})

# 2. Select LSP server
LSP_CONFIG=$(bash select_lsp.sh {{PROJECT_ROOT}} $LANGUAGE)

# 3. Install LSP server (from references/lsp-installation-guide.md)
bash install_lsp.sh $LANGUAGE

# 4. Configure .claude/settings.json
echo "$LSP_CONFIG" | jq . > {{PROJECT_ROOT}}/.claude/lsp-config.json

# 5. Merge into settings.json
jq -s '.[0] * .[1]' \
  {{PROJECT_ROOT}}/.claude/settings.json \
  {{PROJECT_ROOT}}/.claude/lsp-config.json \
  > {{PROJECT_ROOT}}/.claude/settings.json.tmp
mv {{PROJECT_ROOT}}/.claude/settings.json.tmp {{PROJECT_ROOT}}/.claude/settings.json
```

## LSP Installation (Reference)

For detailed installation procedures, see: [../references/lsp-installation-guide.md](../references/lsp-installation-guide.md)

Quick reference script (calls install_lsp.py from references):

```bash
#!/usr/bin/env bash
# install_lsp_wrapper.sh

LANGUAGE="${1:?Language required}"
INSTALL_SCRIPT="../references/scripts/install_lsp.py"

if [[ ! -f "$INSTALL_SCRIPT" ]]; then
  echo "Error: install_lsp.py not found at $INSTALL_SCRIPT"
  exit 1
fi

python3 "$INSTALL_SCRIPT" --language "$LANGUAGE"
```

## LSP Plugin Configuration

After selecting LSP server, configure the LSP plugin.

See: [../references/lsp-plugin-template.md](../references/lsp-plugin-template.md) for complete plugin structure.

Quick setup:

```bash
#!/usr/bin/env bash
# setup-lsp-plugin.sh

PROJECT_ROOT="${1:?Project root required}"
LSP_COMMAND="${2:?LSP command required}"
LSP_ARGS="${3:-[]}"

PLUGIN_DIR="$PROJECT_ROOT/.claude/plugins/lsp-plugin"
mkdir -p "$PLUGIN_DIR/.claude-plugin"
mkdir -p "$PLUGIN_DIR/hooks"
mkdir -p "$PLUGIN_DIR/scripts"

# Create plugin.json
cat > "$PLUGIN_DIR/.claude-plugin/plugin.json" <<EOF
{
  "name": "lsp-plugin",
  "version": "1.0.0",
  "description": "LSP server integration",
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
    ],
    "SessionStop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\${CLAUDE_PLUGIN_ROOT}/scripts/stop-lsp.sh"
          }
        ]
      }
    ]
  }
}
EOF

# Create start-lsp.sh
cat > "$PLUGIN_DIR/scripts/start-lsp.sh" <<'EOF'
#!/usr/bin/env bash
LSP_COMMAND="{{LSP_COMMAND}}"
LSP_ARGS="{{LSP_ARGS}}"
PROJECT_ROOT="{{PROJECT_ROOT}}"

if command -v "$LSP_COMMAND" &>/dev/null; then
  echo "Starting LSP server: $LSP_COMMAND"
  # Start LSP in background (implementation depends on LSP server)
else
  echo "LSP server '$LSP_COMMAND' not found"
fi
EOF

chmod +x "$PLUGIN_DIR/scripts/start-lsp.sh"

echo "LSP plugin configured at $PLUGIN_DIR"
```

---

**Next**: [Part 3 - Configuration and Troubleshooting](./LSP_SELECTION_GUIDE-part3-config-troubleshooting.md)

**Previous**: [Part 1 - Language Detection](./LSP_SELECTION_GUIDE-part1-language-detection.md)

**Back to**: [LSP Selection Guide (Index)](./LSP_SELECTION_GUIDE.md)
