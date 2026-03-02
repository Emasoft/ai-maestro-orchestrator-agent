# Document Storage Protocol - Part 1: Remote Agent Storage

**Parent Document**: [DOCUMENT_STORAGE_PROTOCOL.md](./DOCUMENT_STORAGE_PROTOCOL.md)
**Version**: 2.0.0

---

## Storage Root Directory

Each remote agent stores downloaded documents under:

```
{{PROJECT_ROOT}}/design/received/
```

**Note**: The `design/` directory is gitignored and NOT committed.

---

## Category 1: Task Instructions (READ-ONLY)

Received task delegations and assignments from orchestrator.

```
design/received/tasks/
├── {{TASK_ID}}/
│   ├── delegation.md           # Original TASK_DELEGATION_TEMPLATE
│   ├── toolchain-spec.md       # Compiled toolchain template
│   ├── checklist.md            # Verification checklist
│   └── metadata.json           # Download timestamp, source URL, SHA256
```

**Retention**: Permanent (never delete)
**Access**: READ-ONLY after download

---

## Category 2: Specifications (READ-ONLY)

Toolchain specs, platform configs, and project templates.

```
design/received/specs/
├── toolchains/
│   ├── {{LANGUAGE}}_toolchain.md
│   └── metadata.json
├── platforms/
│   ├── {{PLATFORM}}_module.md
│   └── metadata.json
└── configs/
    ├── claude_config.md
    └── metadata.json
```

**Retention**: Until project toolchain changes
**Access**: READ-ONLY after download

---

## Category 3: Plans & Reviews (READ-ONLY)

Design documents, implementation plans, code reviews.

```
design/received/plans/
├── {{TASK_ID}}/
│   ├── design/
│   │   ├── YYYYMMDD_HHMMSS_design.md
│   │   └── metadata.json
│   ├── implementation/
│   │   ├── YYYYMMDD_HHMMSS_plan.md
│   │   └── metadata.json
│   └── reviews/
│       ├── YYYYMMDD_HHMMSS_review.md
│       └── metadata.json
```

**Retention**: Permanent (never delete)
**Access**: READ-ONLY after download

---

## Category 4: Sync Reports (READ-ONLY)

Cross-agent synchronization and project state reports.

```
design/received/sync/
├── YYYYMMDD_HHMMSS_project_sync.md
├── YYYYMMDD_HHMMSS_kanban_sync.md
└── metadata.json
```

**Retention**: 30 days rolling window
**Access**: READ-ONLY after download

---

**Next**: [Part 2 - Orchestrator Storage](./DOCUMENT_STORAGE_PROTOCOL-part2-orchestrator-storage.md)
