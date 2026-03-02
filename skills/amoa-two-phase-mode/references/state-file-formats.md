# State File Formats

Complete YAML frontmatter specifications for Two-Phase Mode state files.

## Contents

- 1. Plan Phase State File
  - 1.1 File location
  - 1.2 Complete YAML schema
  - 1.3 Field descriptions
- 2. Orchestration Phase State File
  - 2.1 File location
  - 2.2 Complete YAML schema
  - 2.3 Field descriptions
- 3. Agent Assignment Structure
  - 3.1 Assignment fields
  - 3.2 Instruction verification tracking
  - 3.3 Progress polling tracking
- 4. Module Status Structure
  - 4.1 Module fields
  - 4.2 Status values

---

## 1. Plan Phase State File

### 1.1 File location

```
design/state/plan-phase.md
```

This file is gitignored (`.local.md` suffix).

### 1.2 Complete YAML schema

```yaml
---
# Phase identification
phase: "planning"
plan_id: "plan-YYYYMMDD-HHMMSS"
status: "drafting|reviewing|approved"
created_at: "ISO 8601 timestamp"

# User Goal (immutable after creation)
goal: "User's project goal"
goal_locked: true

# Requirements Progress
requirements_file: "USER_REQUIREMENTS.md"
requirements_complete: false
requirements_sections:
  - name: "Functional Requirements"
    status: "pending|in-progress|complete"
  - name: "Non-Functional Requirements"
    status: "pending|in-progress|complete"
  - name: "Architecture Design"
    status: "pending|in-progress|complete"

# Module Breakdown
modules:
  - id: "module-id"
    name: "Module Name"
    description: "Module description"
    priority: "critical|high|medium|low"
    acceptance_criteria: "Criteria text"
    dependencies: ["other-module-id"]
    status: "planned|pending"
    github_issue: null

# Exit Criteria
plan_phase_complete: false
exit_criteria:
  - "USER_REQUIREMENTS.md complete"
  - "All modules defined with acceptance criteria"
  - "GitHub Issues created for all modules"
  - "User approved the plan"

# Modification History
modifications:
  - timestamp: "ISO timestamp"
    action: "add|modify|remove"
    target: "module-id or requirement"
    description: "What changed"
---

# Plan Phase Notes

[Markdown body for orchestrator notes]
```

### 1.3 Field descriptions

| Field | Type | Description |
|-------|------|-------------|
| `phase` | string | Always "planning" |
| `plan_id` | string | Unique identifier, format: plan-YYYYMMDD-HHMMSS |
| `status` | enum | drafting, reviewing, approved |
| `created_at` | ISO 8601 | When plan phase started |
| `goal` | string | User's project goal |
| `goal_locked` | boolean | Always true after creation |
| `requirements_file` | string | Path to USER_REQUIREMENTS.md |
| `requirements_complete` | boolean | All requirements documented |
| `requirements_sections` | array | Tracking per section |
| `modules` | array | Module breakdown |
| `plan_phase_complete` | boolean | All exit criteria met |
| `exit_criteria` | array | List of completion requirements |
| `modifications` | array | Change history |

---

## 2. Orchestration Phase State File

### 2.1 File location

```
design/state/exec-phase.md
```

This file is gitignored (`.local.md` suffix).

### 2.2 Complete YAML schema

```yaml
---
# Phase identification
phase: "orchestration"
plan_id: "plan-YYYYMMDD-HHMMSS"
status: "executing|verifying|complete"
started_at: "ISO 8601 timestamp"

# Link to Plan Phase
plan_file: "design/state/plan-phase.md"
requirements_file: "USER_REQUIREMENTS.md"

# Current Focus
current_module: "module-id or null"

# Module Execution Tracking
modules_status:
  - id: "auth-core"
    name: "Core Authentication"
    status: "pending|assigned|in-progress|ai-review|complete"
    assigned_to: "agent-id or null"
    github_issue: "#42"
    pr: "#45 or null"
    verification_loops: 0

# Remote Agent Registry
registered_agents:
  ai_agents:
    - agent_id: "implementer-1"
      session_name: "helper-agent-generic"
      assigned_by_user: true
      registered_at: "ISO timestamp"
  human_developers:
    - github_username: "dev-alice"
      assigned_by_user: true
      registered_at: "ISO timestamp"

# Active Assignments
active_assignments:
  - agent: "implementer-1"
    agent_type: "ai"
    module: "auth-core"
    github_issue: "#42"
    task_uuid: "uuid-string"
    assigned_at: "ISO timestamp"
    last_check: "ISO timestamp"
    status: "awaiting_verification|working|blocked|pending_pr"
    instruction_verification:
      status: "pending|awaiting_repetition|correcting|questioning|verified"
      repetition_received: false
      repetition_correct: false
      questions_asked: 0
      questions_answered: 0
      authorized_at: null
    progress_polling:
      last_poll: "ISO timestamp"
      poll_count: 0
      poll_history: []
      next_poll_due: "ISO timestamp"

# GitHub Project Sync
github_project_id: "PVT_xxx or null"
sync_enabled: true

# Completion Tracking
modules_completed: 0
modules_total: 2
all_modules_complete: false
verification_mode: false
verification_loops_remaining: 0

# Modification History
modifications:
  - timestamp: "ISO timestamp"
    action: "add|modify|remove|assign|reassign"
    target: "module-id"
    description: "What changed"
---

# Orchestration Phase Notes

[Markdown body for orchestrator notes]
```

### 2.3 Field descriptions

| Field | Type | Description |
|-------|------|-------------|
| `phase` | string | Always "orchestration" |
| `plan_id` | string | Links to plan phase |
| `status` | enum | executing, verifying, complete |
| `started_at` | ISO 8601 | When orchestration started |
| `plan_file` | string | Path to plan state file |
| `current_module` | string | Module currently being worked |
| `modules_status` | array | All modules with status |
| `registered_agents` | object | AI and human agents |
| `active_assignments` | array | Current assignments |
| `github_project_id` | string | GitHub Project ID |
| `sync_enabled` | boolean | GitHub sync active |
| `modules_completed` | integer | Count of complete modules |
| `modules_total` | integer | Total module count |
| `all_modules_complete` | boolean | All modules done |
| `verification_mode` | boolean | In final verification |
| `verification_loops_remaining` | integer | Loops left (max 4) |

---

## 3. Agent Assignment Structure

### 3.1 Assignment fields

```yaml
active_assignments:
  - agent: "implementer-1"           # Agent identifier
    agent_type: "ai"                 # ai or human
    module: "auth-core"              # Module ID
    github_issue: "#42"              # Linked issue
    task_uuid: "task-uuid-12345"     # Unique task ID
    assigned_at: "ISO timestamp"     # When assigned
    last_check: "ISO timestamp"      # Last status check
    status: "working"                # Current status
```

Assignment status values:

| Status | Description |
|--------|-------------|
| `awaiting_verification` | Instruction verification in progress |
| `working` | Agent is implementing |
| `blocked` | Agent reported blocker |
| `pending_pr` | Implementation done, awaiting PR |

### 3.2 Instruction verification tracking

```yaml
instruction_verification:
  status: "verified"
  repetition_received: true
  repetition_correct: true
  questions_asked: 2
  questions_answered: 2
  authorized_at: "2026-01-08T16:20:00+00:00"
```

Verification status values:

| Status | Description |
|--------|-------------|
| `pending` | Not started |
| `awaiting_repetition` | Waiting for agent summary |
| `correcting` | Sent corrections |
| `questioning` | Answering questions |
| `verified` | Authorized to proceed |

### 3.3 Progress polling tracking

```yaml
progress_polling:
  last_poll: "2026-01-08T16:30:00+00:00"
  poll_count: 3
  poll_history:
    - poll_number: 1
      timestamp: "2026-01-08T16:00:00+00:00"
      status: "responded"
      issues_reported: false
      clarifications_needed: false
    - poll_number: 2
      timestamp: "2026-01-08T16:15:00+00:00"
      status: "responded"
      issues_reported: true
      issue_description: "Token expiry unclear"
      issue_resolved: true
      resolution: "Provided spec document"
  next_poll_due: "2026-01-08T16:45:00+00:00"
```

---

## 4. Module Status Structure

### 4.1 Module fields

```yaml
modules_status:
  - id: "auth-core"                  # Unique identifier
    name: "Core Authentication"      # Human-readable name
    description: "Login/logout"      # Optional description
    priority: "high"                 # Priority level
    acceptance_criteria: "..."       # Completion criteria
    dependencies: ["other-module"]   # Dependencies
    status: "in-progress"             # Current status
    assigned_to: "implementer-1"     # Assigned agent
    github_issue: "#42"              # GitHub Issue number
    pr: "#45"                        # PR number (if created)
    verification_loops: 2            # Completed loops
```

### 4.2 Status values

| Status | Description |
|--------|-------------|
| `pending` | Not started, not assigned |
| `planned` | In plan, not yet assigned |
| `assigned` | Assigned but not started |
| `in-progress` | Agent is implementing |
| `ai-review` | Awaiting review |
| `complete` | Verified and merged |

---

## Parsing State Files

Both state files use YAML frontmatter format:

```python
def parse_frontmatter(file_path):
    content = file_path.read_text()
    if not content.startswith("---"):
        return {}, content

    end_index = content.find("---", 3)
    yaml_content = content[3:end_index].strip()
    body = content[end_index + 3:].strip()

    data = yaml.safe_load(yaml_content) or {}
    return data, body

def write_state_file(file_path, data, body):
    yaml_content = yaml.dump(data, default_flow_style=False)
    content = f"---\n{yaml_content}---\n\n{body}"
    file_path.write_text(content)
```
