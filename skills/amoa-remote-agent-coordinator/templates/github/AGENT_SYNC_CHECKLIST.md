# Agent Pre-Work Sync Checklist

## Overview

This checklist must be completed by remote agents BEFORE starting work on any task. It ensures proper synchronization with GitHub issue tracking, kanban board, and toolchain environment.

## Critical: Complete ALL Steps

**Do not skip any step.** Each step ensures critical infrastructure is in place for task execution and tracking.

---

## Table of Contents

This checklist is organized into 4 parts for easier navigation. Click each part to access detailed instructions.

### [Part 1: GitHub Issues & Labels](./AGENT_SYNC_CHECKLIST-part1-github-issues.md)

- **1. GitHub Issue Verification**
  - 1.1. Issue Exists - Verify issue is accessible
  - 1.2. Issue Assigned to Agent - Check/set assignee
- **2. Issue Labels Verification**
  - 2.1. Status Label Present - Verify status:* label exists
  - 2.2. Required Labels Present - Verify all required labels

### [Part 2: Project Board, Toolchain & Branch](./AGENT_SYNC_CHECKLIST-part2-project-toolchain.md)

- **3. Project Board Verification**
  - 3.1. Issue Linked to Project - Verify project linkage
  - 3.2. Project Status Set - Check/set project status
- **4. Toolchain Template Verification**
  - 4.1. Toolchain Template Exists - Locate template file
  - 4.2. Toolchain Template Valid - Verify required sections
- **5. Branch Creation**
  - 5.1. Create Feature Branch - Create with naming convention
  - 5.2. Verify Branch Protection - Test branch is pushable

### [Part 3: Environment & Registration](./AGENT_SYNC_CHECKLIST-part3-environment-registration.md)

- **6. Local Environment Setup**
  - 6.1. Run Toolchain Setup Script - Execute setup commands
  - 6.2. Verify Tool Versions - Check version compatibility
  - 6.3. Run Verification Commands - Validate environment
- **7. Agent Registration**
  - 7.1. Register with Orchestrator - Send ready message
  - 7.2. Update Issue Status to "In Progress" - Sync all systems
- **Complete Checklist Summary** - Copy-paste template for issue comments

### [Part 4: Automation & Troubleshooting](./AGENT_SYNC_CHECKLIST-part4-automation-troubleshooting.md)

- **Automation Script** - Full bash script `pre-work-checklist.sh`
- **Troubleshooting**
  - Checklist Step Fails - General resolution steps
  - Cannot Access Issue - GitHub auth troubleshooting
  - Toolchain Setup Fails - Environment setup issues
  - Branch Already Exists - Branch conflict resolution
  - Cannot Update Project Board - Project API issues
- **When Checklist Complete** - Next steps after sync
- **Post-Work Checklist** - Links to related protocols

---

## Quick Reference

### Environment Variables Required

| Variable | Description | Example |
|----------|-------------|---------|
| `GITHUB_OWNER` | Repository owner | `myorg` |
| `REPO_NAME` | Repository name | `myrepo` |
| `PROJECT_NUMBER` | GitHub Project number | `1` |
| `ISSUE_NUMBER` | Issue number for task | `42` |
| `TASK_ID` | Task identifier | `TASK-001` |
| `AGENT_NAME` | Your agent/session name | `dev-agent-1` |
| `SESSION_ID` | Current session ID | `session_20240115` |
| `PLATFORM` | Target platform | `linux`, `darwin`, `windows` |
| `AIMAESTRO_API` | AI Maestro API endpoint (AMP handles routing automatically) | Managed by AMP |
| `ORCHESTRATOR_AGENT` | Orchestrator agent name | `orchestrator-master` |

### Label Conventions

| Label Type | Format | Example |
|------------|--------|---------|
| Status | `status:*` | `status:backlog`, `status:in-progress` |
| Priority | `priority:*` | `priority:high`, `priority:low` |
| Platform | `platform:*` | `platform:linux`, `platform:macos` |
| Type | `type:*` | `type:feature`, `type:bugfix` |
| Toolchain | `toolchain:*` | `toolchain:python`, `toolchain:rust` |
| Assignment | `assign:*` | `assign:dev-1` |

### Branch Naming Convention

```
feature/{{TASK_ID}}-short-description
```

Examples:
- `feature/TASK-001-add-user-auth`
- `feature/BUG-042-fix-memory-leak`

### Project Board Statuses

| Status | When to Use |
|--------|-------------|
| Backlog | Issue created, not yet started |
| In Progress | Agent actively working |
| Review | Work complete, awaiting review |
| Done | Task fully completed |
| Blocked | Cannot proceed due to issue |

---

## Execution Order

Complete the checklist in this exact order:

1. **Verify GitHub Issue** (Part 1)
2. **Check Labels** (Part 1)
3. **Verify Project Board** (Part 2)
4. **Validate Toolchain** (Part 2)
5. **Create Branch** (Part 2)
6. **Setup Environment** (Part 3)
7. **Register with Orchestrator** (Part 3)

If any step fails, do NOT proceed. See [Part 4: Troubleshooting](./AGENT_SYNC_CHECKLIST-part4-automation-troubleshooting.md) for resolution steps.

---

## Related Documents

- [KANBAN_SYNC_PROTOCOL.md](./KANBAN_SYNC_PROTOCOL.md) - Status transition rules
- [ISSUE_TEMPLATE.md](./ISSUE_TEMPLATE.md) - Issue creation format
- [PR_TEMPLATE.md](./PR_TEMPLATE.md) - Pull request format
- [PROGRESS_UPDATE_TEMPLATE.md](./PROGRESS_UPDATE_TEMPLATE.md) - Progress reporting
