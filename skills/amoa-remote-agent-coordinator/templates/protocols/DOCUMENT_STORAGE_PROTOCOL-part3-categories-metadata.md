# Document Storage Protocol - Part 3: Document Categories & Metadata

**Parent Document**: [DOCUMENT_STORAGE_PROTOCOL.md](./DOCUMENT_STORAGE_PROTOCOL.md)
**Version**: 2.0.0

---

## Document Categories (Both Roles)

### Category: Reports (Orchestrator receives from agents)

```
design/agents/{agent-name}/received/reports/
├── {{TASK_ID}}/
│   ├── completion/
│   │   ├── YYYYMMDD_HHMMSS_completion.md
│   │   └── metadata.json
│   ├── verification/
│   │   ├── YYYYMMDD_HHMMSS_verification.md
│   │   └── metadata.json
│   ├── blockers/
│   │   ├── YYYYMMDD_HHMMSS_blocker.md
│   │   └── metadata.json
│   └── status/
│       ├── YYYYMMDD_HHMMSS_status.md
│       └── metadata.json
```

**Retention**: Permanent (never delete)
**Access**: READ-ONLY after download

---

### Category: Acknowledgments (Orchestrator receives from agents)

```
design/agents/{agent-name}/received/acks/
├── {{TASK_ID}}/
│   ├── YYYYMMDD_HHMMSS_ack.md
│   └── metadata.json
```

**Retention**: 90 days (auto-archive after task closure)
**Access**: READ-ONLY after download

---

## Metadata Schema

### Document Metadata (metadata.json)

Every downloaded file MUST have an accompanying `metadata.json`:

```json
{
  "schema_version": "2.0.0",
  "file_name": "completion.md",
  "category": "reports",
  "subcategory": "completion",
  "task_id": "GH-42",
  "source": {
    "type": "github_issue_comment",
    "url": "https://github.com/owner/repo/issues/42#issuecomment-123456",
    "issue_number": 42,
    "comment_id": 123456,
    "attachment_url": "https://github.com/owner/repo/files/..."
  },
  "download": {
    "timestamp": "2024-01-15T14:30:00Z",
    "agent": "helper-agent-macos-arm64",
    "sha256": "abc123...",
    "file_size_bytes": 4096
  },
  "sender": {
    "agent": "helper-agent-macos-arm64",
    "role": "remote",
    "via": "ai_maestro"
  },
  "receiver": {
    "agent": "orchestrator",
    "role": "orchestrator"
  },
  "ack_sent": true,
  "ack_timestamp": "2024-01-15T14:30:05Z"
}
```

---

**Previous**: [Part 2 - Orchestrator Storage](./DOCUMENT_STORAGE_PROTOCOL-part2-orchestrator-storage.md)
**Next**: [Part 4 - Operations](./DOCUMENT_STORAGE_PROTOCOL-part4-operations.md)
