# Document Storage Protocol

**Version**: 2.0.0
**Status**: MANDATORY
**Applies To**: All agents (orchestrator and remote)

---

## Purpose

This protocol defines the standardized folder structure for storing downloaded .md files received via GitHub issue comment URLs. These folders serve as:

1. **Permanent Records** - Immutable archive of received instructions
2. **Verification Source** - Reference for task completion verification
3. **Audit Trail** - Historical record for dispute resolution
4. **Context Cache** - Quick reference without re-downloading
5. **Agent Tracking** - Orchestrator tracks all agents' documents separately

---

## Storage Architecture Overview

```
ORCHESTRATOR STORAGE (tracks ALL agents):
design/
├── agents/                          # Per-agent tracking (orchestrator only)
│   ├── {agent-full-name}/           # e.g., helper-agent-macos-arm64
│   │   └── received/                # Documents FROM this agent
│   │       ├── reports/
│   │       ├── acks/
│   │       └── sync/
│   └── {another-agent}/
│       └── received/
├── sent/                            # Documents SENT TO agents
│   ├── {agent-full-name}/
│   │   └── tasks/
│   │       └── {task_id}/
└── index/                           # Cross-agent search index
    ├── by-task/
    ├── by-agent/
    └── by-date/

REMOTE AGENT STORAGE (local to each agent):
design/
└── received/                        # Documents FROM orchestrator
    ├── tasks/
    ├── specs/
    ├── plans/
    └── sync/
```

---

## Table of Contents

This protocol is split into 5 parts for easier navigation:

### [Part 1: Remote Agent Storage](./DOCUMENT_STORAGE_PROTOCOL-part1-remote-agent-storage.md)

- Storage Root Directory
- Category 1: Task Instructions (READ-ONLY)
- Category 2: Specifications (READ-ONLY)
- Category 3: Plans & Reviews (READ-ONLY)
- Category 4: Sync Reports (READ-ONLY)

### [Part 2: Orchestrator Storage (Per-Agent Tracking)](./DOCUMENT_STORAGE_PROTOCOL-part2-orchestrator-storage.md)

- Orchestrator Storage Root
- Agent Folders
- Agent Metadata Schema (agent.json)
- Sent Documents Tracking
- Cross-Agent Search Index
- Index Schema: by-task/{task_id}.json

### [Part 3: Document Categories & Metadata](./DOCUMENT_STORAGE_PROTOCOL-part3-categories-metadata.md)

- Category: Reports (Orchestrator receives from agents)
- Category: Acknowledgments (Orchestrator receives from agents)
- Document Metadata Schema (metadata.json)

### [Part 4: Operations](./DOCUMENT_STORAGE_PROTOCOL-part4-operations.md)

- Read-Only Enforcement
  - Immediate Lock After Download
  - Directory Protection
  - Integrity Verification
- Environment Variables
  - Remote Agent Variables
  - Orchestrator Variables
- Orchestrator Lookup Commands
  - Find Documents by Agent
  - Find Documents by Task
  - Find Blockers Across All Agents
- Gitignore Configuration

### [Part 5: Retention, Scripts & Integration](./DOCUMENT_STORAGE_PROTOCOL-part5-retention-scripts-integration.md)

- Retention Policies
  - Remote Agent Retention
  - Orchestrator Retention
- Scripts Reference
  - Remote Agent Scripts
  - Orchestrator Scripts
- Initialization
  - Remote Agent Initialization
  - Orchestrator Initialization
  - Register New Agent
- Integration with Delivery Protocol
  - Remote Agent Flow
  - Orchestrator Flow

---

## Quick Reference

| Role | Storage Root | Primary Use |
|------|--------------|-------------|
| Remote Agent | `design/received/` | Store documents FROM orchestrator |
| Orchestrator | `design/agents/{name}/received/` | Store documents FROM each agent |
| Orchestrator | `design/sent/{name}/` | Track documents SENT TO each agent |
| Orchestrator | `design/index/` | Cross-agent search indexes |

---

## Key Principles

1. **READ-ONLY**: All downloaded documents are locked immediately after download
2. **NEVER COMMITTED**: The `design/` directory is gitignored
3. **INTEGRITY VERIFIED**: SHA256 hashes stored in metadata.json
4. **AGENT-SEPARATED**: Orchestrator tracks each agent's documents separately
5. **INDEXED**: Fast lookup by task, agent, date, or category

---

**Last Updated**: 2024-01-15
**Protocol Version**: 2.0.0
