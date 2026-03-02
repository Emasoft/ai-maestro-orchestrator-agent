# Custom LSP Plugin Template


## Contents

- [Table of Contents](#table-of-contents)
- [When setting up a custom LSP plugin directory structure](#when-setting-up-a-custom-lsp-plugin-directory-structure)
- [When you need to configure a plugin with plugin.json](#when-you-need-to-configure-a-plugin-with-pluginjson)
- [When you want to use .lsp.json as an alternative configuration format](#when-you-want-to-use-lspjson-as-an-alternative-configuration-format)
- [When you need advanced configuration options (environment variables, initialization)](#when-you-need-advanced-configuration-options-environment-variables-initialization)
- [When you need to debug LSP server connection issues](#when-you-need-to-debug-lsp-server-connection-issues)
- [Official Documentation](#official-documentation)

---

## Table of Contents
1. When setting up a custom LSP plugin directory structure
2. When you need to configure a plugin with plugin.json
3. When you want to use .lsp.json as an alternative configuration format
4. When you need advanced configuration options (environment variables, initialization)
5. When you need to debug LSP server connection issues

## When setting up a custom LSP plugin directory structure
```
~/.claude/plugins/my-lsp/
├── .claude-plugin/
│   └── plugin.json
└── .lsp.json  (optional, alternative to inline)
```

## When you need to configure a plugin with plugin.json
```json
{
  "name": "my-language-lsp",
  "description": "LSP support for My Language",
  "version": "1.0.0",
  "lspServers": {
    "mylang": {
      "command": "mylang-lsp",
      "args": ["--stdio"],
      "extensionToLanguage": {
        ".ml": "mylang",
        ".mlt": "mylang"
      },
      "transport": "stdio",
      "restartOnCrash": true,
      "maxRestarts": 3,
      "startupTimeout": 10000,
      "shutdownTimeout": 5000
    }
  }
}
```

## When you want to use .lsp.json as an alternative configuration format
```json
{
  "mylang": {
    "command": "mylang-lsp",
    "args": ["--stdio"],
    "extensionToLanguage": {
      ".ml": "mylang"
    }
  }
}
```

## When you need advanced configuration options (environment variables, initialization)
```json
{
  "mylang": {
    "command": "mylang-lsp",
    "args": ["--stdio"],
    "extensionToLanguage": { ".ml": "mylang" },
    "env": {
      "MY_LSP_LOG": "debug"
    },
    "initializationOptions": {
      "typeCheckingMode": "strict"
    },
    "settings": {
      "mylang.analysis.autoSearchPaths": true
    }
  }
}
```

## When you need to debug LSP server connection issues
```json
{
  "loggingConfig": {
    "args": ["--log-level", "4"],
    "env": {
      "LSP_LOG": "-level verbose -file ${CLAUDE_PLUGIN_LSP_LOG_FILE}"
    }
  }
}
```

Enable with: claude --enable-lsp-logging
Logs at: ~/.claude/debug/

## Official Documentation

**Always refer to official documentation for the latest LSP server configurations.**

- [Claude Code LSP Servers Documentation](https://docs.anthropic.com/en/docs/claude-code/mcp#lsp-servers)
- [Claude Code Plugin System](https://docs.anthropic.com/en/docs/claude-code/plugins)
- [Plugin JSON Schema](https://docs.anthropic.com/en/docs/claude-code/plugins#plugin-structure)
- [Language Server Protocol Specification](https://microsoft.github.io/language-server-protocol/)

The official Anthropic documentation is the authoritative source for:
- Plugin structure and manifest format
- LSP configuration schema and fields
- Environment variables and logging options
- Plugin lifecycle and initialization
- Debugging and diagnostics procedures
