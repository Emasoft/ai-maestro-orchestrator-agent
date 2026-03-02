# Document Storage Protocol - Part 2: Orchestrator Storage (Per-Agent Tracking)

**Parent Document**: [DOCUMENT_STORAGE_PROTOCOL.md](./DOCUMENT_STORAGE_PROTOCOL.md)
**Version**: 2.0.0

---

## Orchestrator Storage Root

The orchestrator tracks documents FROM ALL agents:

```
{{ORCHESTRATOR_PROJECT_ROOT}}/design/
```

## Agent Folders

Each agent has its own folder under `design/agents/`:

```
design/agents/
├── helper-agent-macos-arm64/        # Full agent name (required)
│   ├── agent.json                   # Agent metadata
│   └── received/                    # Documents FROM this agent
│       ├── reports/
│       │   └── {{TASK_ID}}/
│       │       ├── completion/
│       │       ├── verification/
│       │       ├── blockers/
│       │       └── status/
│       ├── acks/
│       │   └── {{TASK_ID}}/
│       └── sync/
├── helper-agent-linux-x64/
│   ├── agent.json
│   └── received/
├── helper-agent-windows/
│   ├── agent.json
│   └── received/
└── generic/                         # Default agent for unspecified sources
    ├── agent.json
    └── received/
```

---

## Agent Metadata Schema (agent.json)

Each agent folder contains metadata:

```json
{
  "schema_version": "2.0.0",
  "agent_name": "helper-agent-macos-arm64",
  "agent_type": "remote",
  "platform": "macos",
  "architecture": "arm64",
  "first_seen": "2024-01-15T10:00:00Z",
  "last_activity": "2024-01-15T14:30:00Z",
  "total_tasks_assigned": 15,
  "total_tasks_completed": 12,
  "total_documents_received": 47,
  "ai_maestro_session": "session-uuid-here"
}
```

---

## Sent Documents Tracking

The orchestrator also tracks documents SENT to each agent:

```
design/sent/
├── helper-agent-macos-arm64/
│   └── tasks/
│       └── GH-42/
│           ├── delegation.md        # Copy of sent delegation
│           ├── toolchain-spec.md    # Copy of sent toolchain
│           └── sent_metadata.json   # Delivery confirmation
├── helper-agent-linux-x64/
│   └── tasks/
└── all-agents/                      # Broadcast documents
    └── sync/
        └── YYYYMMDD_project_sync.md
```

---

## Cross-Agent Search Index

The orchestrator maintains search indexes:

```
design/index/
├── by-task/
│   └── GH-42.json                   # All agents working on GH-42
├── by-agent/
│   └── helper-agent-macos-arm64.json # All tasks for this agent
├── by-date/
│   └── 2024-01/
│       └── 15.json                  # All activity on Jan 15
└── by-category/
    ├── tasks.json
    ├── reports.json
    └── blockers.json
```

---

## Index Schema: by-task/{task_id}.json

```json
{
  "task_id": "GH-42",
  "created": "2024-01-15T10:00:00Z",
  "status": "in-progress",
  "assigned_agents": [
    {
      "agent": "helper-agent-macos-arm64",
      "assigned_at": "2024-01-15T10:00:00Z",
      "delegation_url": "https://github.com/...",
      "ack_received": true,
      "ack_timestamp": "2024-01-15T10:00:15Z"
    }
  ],
  "documents": [
    {
      "type": "delegation",
      "path": "design/sent/helper-agent-macos-arm64/tasks/GH-42/delegation.md",
      "timestamp": "2024-01-15T10:00:00Z"
    },
    {
      "type": "completion_report",
      "path": "design/agents/helper-agent-macos-arm64/received/reports/GH-42/completion/...",
      "timestamp": "2024-01-15T14:30:00Z"
    }
  ]
}
```

---

**Previous**: [Part 1 - Remote Agent Storage](./DOCUMENT_STORAGE_PROTOCOL-part1-remote-agent-storage.md)
**Next**: [Part 3 - Document Categories & Metadata](./DOCUMENT_STORAGE_PROTOCOL-part3-categories-metadata.md)
