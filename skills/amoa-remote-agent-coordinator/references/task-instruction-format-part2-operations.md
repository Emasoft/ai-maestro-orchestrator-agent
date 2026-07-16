# Task Instruction Format - Part 2: Operations

## Contents

- **[When reading project configuration](#when-reading-project-configuration)** - Understand config reference pattern
- **[When monitoring task progress](#when-monitoring-task-progress)** - Handle timeouts and progress updates
- **[When a task blocks or fails](#when-a-task-blocks-or-fails)** - Handle error states and escalation
- **[When integrating with other protocols](#when-integrating-with-other-protocols)** - Connect to related systems
- **[When reviewing a completed task](#when-reviewing-a-completed-task)** - See example of filled-in instruction

---

## When Reading Project Configuration

**CRITICAL**: Every task instruction MUST reference central configuration files so remote agents use the correct tools and settings.

### Configuration Reference Pattern

**Use reference-based approach** (NOT embedded config):

```markdown
## Project Config

**Configuration Location**: `design/config/`
**Config Version**: 2025-12-31T03:48:23Z

### Required Reading Before Starting Task

Agents MUST read these config files before beginning work:

1. **Toolchain**: `design/config/toolchain.md`
   - Python version, package manager, virtual environment
   - Quality tools (linter, formatter, type checker, test runner)
   - Commands for setup, quality checks, tests

2. **Standards**: `design/config/standards.md`
   - Naming conventions, documentation requirements
   - Type hints, error handling, testing requirements
   - File organization, import order

3. **Environment**: `design/config/environment.md`
   - Required environment variables (Git, AI Maestro, project-specific)
   - Environment file location and loading
   - CI/CD environment configuration

4. **Architecture**: `design/specs/architecture.md`
   - System overview and components
   - Data flow and deployment architecture

5. **Requirements**: `design/specs/requirements.md`
   - Feature specifications relevant to this task
   - Acceptance criteria

### How to Access Config

```bash
# Read toolchain configuration
cat design/config/toolchain.md

# Read code standards
cat design/config/standards.md

# Read environment variables spec
cat design/config/environment.md

# Read architecture docs
cat design/specs/architecture.md

# Read requirements for specific feature
cat design/specs/requirements.md | grep -A 20 "GH-{issue-number}"
```

### Config Snapshot

At task assignment, orchestrator provides:

```json
{
  "config_snapshot": {
    "version": "2025-12-31T03:48:23Z",
    "files": [
      "design/config/toolchain.md",
      "design/config/standards.md",
      "design/config/environment.md"
    ],
    "critical_settings": {
      "python_version": "3.12",
      "package_manager": "uv",
      "line_length": 88,
      "test_framework": "pytest"
    }
  }
}
```

**NOTE**: `critical_settings` is a MINIMAL inline summary. Agent MUST read full config files for complete details.

### Getting Secrets

Secrets are **NEVER** sent in task instructions. Agent must:
1. Check local `.env` file (see `design/config/environment.md` for required variables)
2. If missing, request from orchestrator via secure message
3. **NEVER** commit secrets to git
```

### Config Update Notification

When project config changes, orchestrator sends:

```json
{
  "type": "config-update",
  "changed_files": [
    "design/config/toolchain.md"
  ],
  "change_summary": "Updated ruff from 0.7.0 to 0.8.0",
  "new_version": "2025-12-31T04:15:00Z",
  "action_required": "Re-read design/config/toolchain.md before next task"
}
```

Agents MUST:
1. **Acknowledge** config update via echo acknowledgment protocol
2. **Re-read** changed config files
3. **Apply** new configuration
4. **Report conflicts** if current task cannot comply

---

## When Monitoring Task Progress

### Progress Update Requirements

Agents MUST send progress updates at regular intervals:

| Task Priority | Update Frequency | Timeout |
|--------------|-----------------|---------|
| `urgent` | Every 2 hours | 6 hours |
| `high` | Every 4 hours | 24 hours |
| `normal` | Every 8 hours | 72 hours |
| `low` | Daily | 7 days |

### Timeout Protocol

1. **At 50% of timeout**: Orchestrator sends status-request
2. **At 80% of timeout**: Orchestrator sends warning
3. **At 100% of timeout**: Task marked as stalled

### Timeout Flow

If task not completed within timeout:

1. Orchestrator sends timeout warning
2. Agent has 2 hours to either:
   - Complete task, OR
   - Send completion estimate with justification
3. IF no response:
   - Mark task as stalled
   - Reassign to different agent
   - Original agent must provide handoff notes

### Timeout Extension Request

```json
{
  "type": "timeout-extension-request",
  "task_id": "GH-42",
  "current_timeout": "2025-12-31T18:00:00Z",
  "requested_timeout": "2026-01-01T12:00:00Z",
  "reason": "Discovered architectural issue requiring refactor",
  "work_completed": "Authentication flow complete (60%)",
  "remaining_work": "Token refresh and error handling (40%)",
  "estimated_completion": "2026-01-01T10:00:00Z"
}
```

---

## When a Task Blocks or Fails

### Error States

Canonical copy: maintained in [task-instruction-format-part3-errors-integration.md](task-instruction-format-part3-errors-integration.md) §3.1 Error States — read that file for the full error states table (trigger, agent action, orchestrator action per state).

### Blocked Report Format

Canonical copy: maintained in [task-instruction-format-part3-errors-integration.md](task-instruction-format-part3-errors-integration.md) §3.2 Blocked Report Format — read that file for the blocked-report JSON message format and blocker types.

---

## When Integrating with Other Protocols

This format integrates with:

- `echo-acknowledgment-protocol.md` - Agent must acknowledge task before starting
- `messaging-protocol.md` - Use message schema for task transmission
- `test-report-format.md` - Test results format for completion report
- `artifact-sharing-protocol.md` - How to share build outputs
- `change-notification-protocol.md` - Receive config updates during task

### Protocol Flow

```
1. Orchestrator sends task (this format) via messaging-protocol
2. Agent acknowledges via echo-acknowledgment-protocol
3. Agent works on task, sends progress updates
4. Agent may receive change-notifications during work
5. Agent runs tests, generates test-report-format
6. Agent shares artifacts via artifact-sharing-protocol
7. Agent sends completion report (this format)
```

---

## When Reviewing a Completed Task

### Example Completed Instruction

Canonical copy: maintained in [task-instruction-format-part3-errors-integration.md](task-instruction-format-part3-errors-integration.md) §3.6 Example Completed Task — read that file for the full filled-in task instruction example (password reset flow, GH-42).

---

**See also**: [task-instruction-format-part1-core-template.md](task-instruction-format-part1-core-template.md) for the core task instruction template, ACK block, and response formats.
