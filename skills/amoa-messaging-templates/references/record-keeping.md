# Record-Keeping Standards

This document defines the standard directory structure, filename conventions, and log entry format for all emasoft plugins.

## Table of Contents

- [Directory Structure](#directory-structure)
- [Filename Conventions](#filename-conventions)
- [Log Entry Format](#log-entry-format)

---

## Directory Structure

Each plugin maintains records in `docs_dev/`:

```
docs_dev/
├── orchestration/          # EOA records
│   ├── task-log.md
│   ├── delegation-log.md
│   └── status/
├── integration/            # EIA records
│   ├── routing-log.md
│   ├── reports/
│   └── status/
├── design/                 # EAA records
│   ├── requirements-log.md
│   ├── adrs/
│   └── handoffs/
├── chief-of-staff/         # ECOS records
│   ├── agent-lifecycle.log
│   ├── approvals/
│   └── team-assignments.md
├── projects/               # EAMA records
│   ├── project-registry.md
│   └── user-interactions.md
└── reports/                # Shared reports
```

---

## Filename Conventions

Use these patterns for consistent file naming:

| Type | Pattern | Example |
|------|---------|---------|
| Timestamped | `<type>-YYYYMMDD-HHMMSS.<ext>` | `verification-20260204-143022.md` |
| Task-based | `<type>-<task-id>.<ext>` | `handoff-TASK-042.md` |
| PR-based | `<type>-pr<number>.<ext>` | `review-pr123.md` |
| Date-based | `<type>-YYYY-MM-DD.<ext>` | `approvals-2026-02-04.log` |

---

## Log Entry Format

Use this markdown format for log entries:

```markdown
## [TIMESTAMP] [AGENT] [ACTION]

**Task/Subject:** <description>
**Status:** <status>
**Details:** <brief-details>
**Output:** <file-path-if-any>

---
```

**Example:**

```markdown
## [2026-02-04 14:30:22] [orchestrator] [TASK_ASSIGNED]

**Task/Subject:** Implement authentication module
**Status:** assigned
**Details:** Assigned to implementer-1, priority: high
**Output:** docs_dev/handoffs/auth-core.md

---
```
