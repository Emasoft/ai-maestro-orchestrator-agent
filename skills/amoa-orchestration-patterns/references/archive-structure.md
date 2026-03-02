# Archive Structure Specification


## Contents

- [Overview](#overview)
- [Archive Location](#archive-location)
- [Directory Structure](#directory-structure)
- [File Descriptions](#file-descriptions)
  - [status.md](#statusmd)
  - [delegation-history.md](#delegation-historymd)
  - [messages/](#messages)
  - [artifacts/](#artifacts)
  - [metadata.json](#metadatajson)
- [Archive Trigger](#archive-trigger)
- [Archive Process](#archive-process)
- [Archive Retention](#archive-retention)
- [Searching Archives](#searching-archives)
- [Benefits of Structured Archives](#benefits-of-structured-archives)

## Overview

The orchestrator maintains a standardized archive structure for long-term storage of completed task records. This ensures traceability, audit compliance, and recovery capabilities.

## Archive Location

**Base Path:** `docs_dev/orchestration/archive/[task-uuid]/`

Each completed task receives its own subdirectory identified by the task's UUID.

## Directory Structure

```
archive/
└── [task-uuid]/
    ├── status.md                    # Final status file
    ├── delegation-history.md        # All delegation events
    ├── messages/                    # AI Maestro message transcripts
    │   ├── assignment.json          # Initial task assignment message
    │   ├── progress-updates.json    # All progress update messages
    │   └── completion.json          # Final completion message
    ├── artifacts/                   # Deliverables from agent
    │   ├── completion-report.md     # Agent's completion report
    │   ├── test-results.log         # Test execution results
    │   └── [other artifacts]        # Any other deliverables
    └── metadata.json                # Task metadata for indexing
```

## File Descriptions

### status.md
The final state of the task status file containing:
- Complete timeline
- Final progress percentage (100%)
- All progress updates chronologically
- Acceptance criteria with completion status
- Links to all artifacts
- Final notes and decisions

### delegation-history.md
Complete record of all delegation events including:
- Initial assignment
- Any retries or reassignments
- Status checks and updates
- Escalations (if any)
- Final completion acknowledgment

### messages/
Directory containing JSON exports of all AI Maestro messages related to the task:
- **assignment.json**: Original task assignment from ECOS/EAMA
- **progress-updates.json**: Array of all status update messages
- **completion.json**: Final completion report message

### artifacts/
Directory containing all deliverables produced by the assigned agent:
- **completion-report.md**: Detailed completion report
- **test-results.log**: Test execution logs
- Any code, configurations, or documentation produced
- Screenshots, diagrams, or other supporting materials

### metadata.json
Structured metadata for indexing and search capabilities:
```json
{
  "task_uuid": "uuid-string",
  "task_name": "Task name",
  "task_type": "implementation|review|fix|research",
  "priority": "normal|high|urgent",
  "received_at": "2026-02-04T10:00:00Z",
  "delegated_to": "agent-name",
  "completed_at": "2026-02-04T16:30:00Z",
  "duration_hours": 6.5,
  "archived_at": "2026-02-11T10:00:00Z",
  "outcome": "success|failed|partial",
  "attempts": 1,
  "github_issue_url": "https://github.com/...",
  "tags": ["feature", "backend", "api"]
}
```

## Archive Trigger

**Timing:** 7 days after task completion

**Automation:** Task archiving should be automated via scheduled job or manual cleanup process.

**Preconditions before archiving:**
- [ ] Task status is COMPLETED or FAILED (not IN_PROGRESS)
- [ ] All AI Maestro messages have been archived
- [ ] All artifacts have been collected
- [ ] GitHub issue is closed
- [ ] Task has been removed from active task log

## Archive Process

When archiving a completed task:

1. **Create archive directory**: `docs_dev/orchestration/archive/[task-uuid]/`
2. **Copy status file**: Move final status from `status/[task-uuid].md` to `archive/[task-uuid]/status.md`
3. **Export delegation history**: Extract delegation events from delegation-log.md
4. **Export messages**: Save AI Maestro message transcripts as JSON
5. **Collect artifacts**: Copy all deliverables from agent to artifacts/ subdirectory
6. **Generate metadata.json**: Create structured metadata file
7. **Update logs**: Remove task from active sections, add to archived section
8. **Clean up**: Remove temporary files, update references

## Archive Retention

**Retention Period:** Indefinite (archives are permanent record)

**Backup:** Archive directory should be included in project backups

**Accessibility:** Archives remain accessible for:
- Audit purposes
- Learning from past tasks
- Reference for similar future tasks
- Recovery from failures

## Searching Archives

Metadata files enable efficient searching by:
- Task type
- Agent name
- Date range
- Outcome
- Duration
- Tags

Future enhancement: Build search index from metadata.json files for quick lookups.

## Benefits of Structured Archives

1. **Traceability**: Complete audit trail of all work
2. **Recovery**: Can reconstruct task context if needed
3. **Learning**: Analyze patterns in task completion
4. **Reporting**: Generate metrics and insights
5. **Compliance**: Meet audit and governance requirements
6. **Knowledge Base**: Reference for similar future tasks
