---
name: lsp-plugin-template
description: Template configurations and integration patterns for connecting LSP servers to Claude Code plugins and remote agent systems
---

# LSP Plugin Template

## Purpose

This reference document provides template configurations for integrating LSP servers with Claude Code plugins and remote agent coordination systems. Use this guide when you need to:

- Create plugin configurations that leverage LSP capabilities
- Define LSP communication patterns for remote agents
- Set up bidirectional LSP message routing
- Configure LSP-based code intelligence for distributed workflows

> **TODO**: This is a stub file that needs complete plugin templates, configuration examples, and integration patterns for LSP-enabled agent coordination.

## Plugin Configuration Template

### Basic LSP Plugin Structure

```json
{
  "name": "lsp-integration-plugin",
  "version": "1.0.0",
  "description": "LSP integration for remote agent coordination",
  "lsp": {
    "servers": {
      "python": {
        "command": "pylsp",
        "args": [],
        "initializationOptions": {}
      }
    }
  }
}
```

### MCP Server Integration

Template for exposing LSP functionality through MCP:

```json
{
  "mcpServers": {
    "lsp-bridge": {
      "command": "lsp-mcp-bridge",
      "args": ["--server", "pylsp"],
      "env": {}
    }
  }
}
```

## Communication Patterns

### Request-Response Pattern

Standard LSP request/response handling for:
- `textDocument/completion`
- `textDocument/definition`
- `textDocument/references`

### Notification Pattern

Handling LSP notifications:
- `textDocument/didOpen`
- `textDocument/didChange`
- `textDocument/didSave`

## Integration Examples

### Remote Agent Code Analysis

Template for agents performing code analysis via LSP.

### Distributed Refactoring

Template for coordinating refactoring operations across multiple agents.

## Related References

- See [lsp-servers-overview.md](./lsp-servers-overview.md) for server selection
- See [lsp-installation-guide.md](./lsp-installation-guide.md) for installation steps
