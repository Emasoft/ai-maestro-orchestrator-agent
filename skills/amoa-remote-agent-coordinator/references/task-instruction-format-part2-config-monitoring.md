# Task Instruction Format - Part 2: Config and Monitoring

## Contents

- **[2.1 Configuration Reference Pattern](#21-configuration-reference-pattern)** - Use reference-based approach
- **[2.2 Required Reading Before Starting](#22-required-reading-before-starting)** - Config files to read
- **[2.3 How to Access Config](#23-how-to-access-config)** - Commands to read config files
- **[2.4 Config Snapshot Format](#24-config-snapshot-format)** - JSON format for config reference
- **[2.5 Getting Secrets](#25-getting-secrets)** - Secure secrets handling
- **[2.6 Config Update Notifications](#26-config-update-notifications)** - Handling config changes
- **[2.7 Progress Update Requirements](#27-progress-update-requirements)** - Update frequency by priority
- **[2.8 Timeout Protocol](#28-timeout-protocol)** - Timeout flow and handling
- **[2.9 Timeout Extension Request](#29-timeout-extension-request)** - Requesting more time

---

## 2.1 Configuration Reference Pattern

**CRITICAL**: Every task instruction MUST reference central configuration files so remote agents use the correct tools and settings.

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
```

---

## 2.2 Required Reading Before Starting

Every task instruction should list the required config files:

| Config File | Contains | Read When |
|-------------|----------|-----------|
| `design/config/toolchain.md` | Python version, package manager, linter, formatter | ALWAYS before starting |
| `design/config/standards.md` | Code style, naming, documentation requirements | ALWAYS before writing code |
| `design/config/environment.md` | Environment variables, secrets location | Before any setup |
| `design/specs/architecture.md` | System design, component relationships | When touching multiple files |
| `design/specs/requirements.md` | Feature specs, acceptance criteria | When implementing features |

---

## 2.3 How to Access Config

Include these commands in task instructions:

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

---

## 2.4 Config Snapshot Format

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

---

## 2.5 Getting Secrets

Secrets are **NEVER** sent in task instructions. Agent must:

1. Check local `.env` file (see `design/config/environment.md` for required variables)
2. If missing, request from orchestrator via secure message
3. **NEVER** commit secrets to git

### Secret Request Format

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "orchestrator-master",
  "subject": "SECRET_REQUEST: GH-42",
  "priority": "high",
  "content": {
    "type": "secret-request",
    "task_id": "GH-42",
    "secrets_needed": [
      "DATABASE_URL",
      "API_KEY"
    ],
    "reason": "Required for integration testing"
  }
}
```

---

## 2.6 Config Update Notifications

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

### Agent Response to Config Updates

Agents MUST:
1. **Acknowledge** config update via echo acknowledgment protocol
2. **Re-read** changed config files
3. **Apply** new configuration
4. **Report conflicts** if current task cannot comply

### Config Update Acknowledgment

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "orchestrator-master",
  "subject": "CONFIG_ACK: toolchain.md update",
  "content": {
    "type": "config-update-ack",
    "version": "2025-12-31T04:15:00Z",
    "status": "applied",
    "notes": "Upgraded ruff, re-ran linting"
  }
}
```

---

## 2.7 Progress Update Requirements

Agents MUST send progress updates at regular intervals:

| Task Priority | Update Frequency | Timeout |
|--------------|-----------------|---------|
| `urgent` | Every 2 hours | 6 hours |
| `high` | Every 4 hours | 24 hours |
| `normal` | Every 8 hours | 72 hours |
| `low` | Daily | 7 days |

### Progress Update Format

```
[PROGRESS] GH-42-feature - Checkpoint 2: Implementation

Status: ACTIVE
Progress: 60% complete
Current: Finished core logic
Next: Writing tests
ETA: 2 hours
```

### Checkpoint Definitions

| Checkpoint | Description | Expected Progress |
|------------|-------------|-------------------|
| 1: Setup | Environment ready, config read | 10% |
| 2: Analysis | Code reviewed, plan confirmed | 20% |
| 3: Tests Written | TDD - failing tests exist | 40% |
| 4: Implementation | Code passes tests | 70% |
| 5: Cleanup | Linting, formatting, docs | 85% |
| 6: PR Created | Ready for review | 95% |
| 7: Complete | Merged or approved | 100% |

---

## 2.8 Timeout Protocol

### Timeout Warning Sequence

1. **At 50% of timeout**: Orchestrator sends status-request
2. **At 80% of timeout**: Orchestrator sends warning
3. **At 100% of timeout**: Task marked as stalled

### Status Request Message

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "[agent-id]",
  "subject": "STATUS_REQUEST: GH-42",
  "priority": "high",
  "content": {
    "type": "status-request",
    "task_id": "GH-42",
    "timeout_percentage": 50,
    "message": "Please send progress update"
  }
}
```

### Timeout Warning Message

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "[agent-id]",
  "subject": "TIMEOUT_WARNING: GH-42",
  "priority": "urgent",
  "content": {
    "type": "timeout-warning",
    "task_id": "GH-42",
    "timeout_at": "2025-12-31T18:00:00Z",
    "time_remaining": "4 hours",
    "action_required": "Complete task or request extension"
  }
}
```

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

---

## 2.9 Timeout Extension Request

When agent needs more time:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "orchestrator-master",
  "subject": "EXTENSION_REQUEST: GH-42",
  "priority": "high",
  "content": {
    "type": "timeout-extension-request",
    "task_id": "GH-42",
    "current_timeout": "2025-12-31T18:00:00Z",
    "requested_timeout": "2026-01-01T12:00:00Z",
    "reason": "Discovered architectural issue requiring refactor",
    "work_completed": "Authentication flow complete (60%)",
    "remaining_work": "Token refresh and error handling (40%)",
    "estimated_completion": "2026-01-01T10:00:00Z"
  }
}
```

### Extension Decision Criteria

Orchestrator grants extension if:
- Agent has made meaningful progress
- Reason is legitimate (not poor planning)
- New estimate is reasonable
- No higher-priority tasks need this agent

### Extension Response

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "[agent-id]",
  "subject": "EXTENSION_GRANTED: GH-42",
  "content": {
    "type": "extension-response",
    "task_id": "GH-42",
    "decision": "granted",
    "new_timeout": "2026-01-01T12:00:00Z",
    "notes": "Approved 18-hour extension. Next update expected in 4 hours."
  }
}
```

---

## Navigation

- **Index**: [task-instruction-format.md](task-instruction-format.md)
- **Previous**: [Part 1: Task Template](task-instruction-format-part1-template.md)
- **Next**: [Part 3: Errors and Integration](task-instruction-format-part3-errors-integration.md)
