# Document Storage Protocol - Part 5: Retention, Scripts & Integration

**Parent Document**: [DOCUMENT_STORAGE_PROTOCOL.md](./DOCUMENT_STORAGE_PROTOCOL.md)
**Version**: 2.0.0

---

## Retention Policies

### Remote Agent Retention

| Category | Retention | Archive Action |
|----------|-----------|----------------|
| tasks | Permanent | Never delete |
| specs | Until changed | Replace with new version |
| plans | Permanent | Never delete |
| sync | 30 days | Delete oldest beyond window |

### Orchestrator Retention

| Category | Retention | Archive Action |
|----------|-----------|----------------|
| agents/*/reports | Permanent | Never delete |
| agents/*/acks | 90 days | Move to `design/archive/` |
| agents/*/sync | 30 days | Delete oldest beyond window |
| sent/* | Permanent | Never delete |
| index/* | Permanent | Rebuild if corrupted |

---

## Scripts Reference

### Remote Agent Scripts

| Script | Purpose |
|--------|---------|
| `eoa_download.py <!-- TODO: Rename to eoa_download.py -->` | Download document to correct category |
| `eoa_verify.py <!-- TODO: Rename to eoa_verify.py -->` | Verify integrity and permissions |
| `eoa_lookup.py <!-- TODO: Rename to eoa_lookup.py -->` | Find documents by task ID |

### Orchestrator Scripts

| Script | Purpose |
|--------|---------|
| `eoa_orchestrator_download.py <!-- TODO: Rename to eoa_orchestrator_download.py -->` | Download to agent-specific folder |
| `eoa_index_rebuild.py <!-- TODO: Rename to eoa_index_rebuild.py -->` | Rebuild cross-agent search index |
| `eoa_agent_status.py <!-- TODO: Rename to eoa_agent_status.py -->` | Show document counts per agent |
| `eoa_search.py <!-- TODO: Rename to eoa_search.py -->` | Search across all agents |
| `eoa_cleanup.py <!-- TODO: Rename to eoa_cleanup.py -->` | Controlled cleanup with approval |

---

## Initialization

### Remote Agent Initialization

```bash
# Initialize storage structure
python3 scripts/eoa_download.py <!-- TODO: Rename to eoa_download.py --> init

# Creates:
# design/
# └── received/
#     ├── tasks/
#     ├── specs/
#     ├── plans/
#     └── sync/
```

### Orchestrator Initialization

```bash
# Initialize orchestrator storage
python3 scripts/eoa_orchestrator_init.py <!-- TODO: Rename to eoa_orchestrator_init.py -->

# Creates:
# design/
# ├── agents/
# │   └── .gitkeep
# ├── sent/
# │   └── .gitkeep
# └── index/
#     ├── by-task/
#     ├── by-agent/
#     ├── by-date/
#     └── by-category/
```

### Register New Agent

```bash
# When orchestrator first contacts a new agent
python3 scripts/eoa_register_agent.py <!-- TODO: Rename to eoa_register_agent.py --> \
  --name "helper-agent-macos-arm64" \
  --platform macos \
  --architecture arm64 \
  --session "session-uuid"

# Creates:
# design/agents/helper-agent-macos-arm64/
# ├── agent.json
# └── received/
#     ├── reports/
#     ├── acks/
#     └── sync/
```

---

## Integration with Delivery Protocol

This protocol extends `DOCUMENT_DELIVERY_PROTOCOL.md`:

### Remote Agent Flow (receiving from orchestrator)

1. **Orchestrator** uploads to GitHub, sends URL via AI Maestro
2. **Remote Agent** downloads to `design/received/{category}/{task_id}/`
3. **Remote Agent** locks files read-only
4. **Remote Agent** sends ACK with SHA256 hash

### Orchestrator Flow (receiving from agents)

1. **Remote Agent** uploads to GitHub, sends URL via AI Maestro
2. **Orchestrator** downloads to `design/agents/{agent-name}/received/{category}/{task_id}/`
3. **Orchestrator** locks files read-only
4. **Orchestrator** updates search indexes
5. **Orchestrator** sends ACK with SHA256 hash

---

**Previous**: [Part 4 - Operations](./DOCUMENT_STORAGE_PROTOCOL-part4-operations.md)

---

**Last Updated**: 2024-01-15
**Protocol Version**: 2.0.0
