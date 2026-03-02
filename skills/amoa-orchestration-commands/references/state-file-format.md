# State File Format

## Contents

- 5.1 Loop state file format and fields
- 5.2 Execution phase state file format
- 5.3 Frontmatter field definitions
- 5.4 How to manually edit state files
- 5.5 State file corruption recovery

---

## 5.1 Loop State File Format and Fields

**File**: `design/state/loop.md`

**Purpose**: Tracks the orchestrator loop state, iterations, and task monitoring configuration.

### Full Example

```yaml
---
iteration: 5
max_iterations: 100
completion_promise: "SPRINT COMPLETE"
task_file: "TODO.md"
check_tasks: true
check_github: true
github_project_id: "PVT_kwDOB1234567"
started_at: 2026-01-09T10:30:00+00:00
verification_mode: false
verification_remaining: 0
---

Complete all pending authentication tasks.

Priority:
1. Fix login bug
2. Add 2FA support
3. Update tests
```

### Field Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `iteration` | Integer | 1 | Current iteration count |
| `max_iterations` | Integer | 100 | Escalation threshold (0=unlimited) |
| `completion_promise` | String | "null" | Promise phrase for completion |
| `task_file` | String | "null" | Path to markdown task file |
| `check_tasks` | Boolean | true | Whether to check Claude Tasks |
| `check_github` | Boolean | true | Whether to check GitHub Projects |
| `github_project_id` | String | "" | Specific GitHub Project ID |
| `started_at` | ISO 8601 | - | When loop was started |
| `verification_mode` | Boolean | false | In verification phase |
| `verification_remaining` | Integer | 0 | Verification loops remaining |

### Body Content

The content after the YAML frontmatter (`---`) contains:
- Initial task prompt
- User notes
- Task descriptions

This content is displayed in `/orchestrator-status` as "Current Task".

---

## 5.2 Execution Phase State File Format

**File**: `design/state/exec-phase.md`

**Purpose**: Tracks orchestration phase progress, modules, agents, and assignments.

### Full Example

```yaml
---
phase: orchestration
plan_id: plan-20260108-143022
status: executing
started_at: 2026-01-09T11:00:00+00:00
github_project_id: "PVT_kwDOB1234567"
sync_enabled: true
modules_total: 3
modules_completed: 1
all_modules_complete: false
verification_mode: false
verification_loops_remaining: 4
modules_status:
  - id: auth-core
    status: complete
    github_issue: "#42"
    assigned_to: implementer-1
    pr: "#55"
    acceptance_criteria: "Users can register with email and password"
  - id: oauth-google
    status: in-progress
    github_issue: "#43"
    assigned_to: implementer-2
  - id: auth-2fa
    status: pending
    github_issue: "#44"
registered_agents:
  ai_agents:
    - agent_id: implementer-1
      session_name: helper-agent-generic
      registered_at: 2026-01-09T11:05:00+00:00
    - agent_id: implementer-2
      session_name: helper-agent-python
      registered_at: 2026-01-09T11:10:00+00:00
  human_developers:
    - agent_id: dev-alice
      github_username: alicedev
active_assignments:
  - module: oauth-google
    agent: implementer-2
    status: working
    instruction_verification:
      status: verified
      authorized_at: 2026-01-09T11:15:00+00:00
    progress_polling:
      last_poll: 2026-01-09T11:30:00+00:00
      next_poll_due: 2026-01-09T11:45:00+00:00
      poll_history:
        - timestamp: 2026-01-09T11:30:00+00:00
          issues_reported: 0
          notes: "50% complete"
---

# Orchestration Phase: plan-20260108-143022

## Status

**EXECUTING** - Implementation in progress

## Modules

3 modules to implement.

## Active Instructions

1. Register remote agents with `/register-agent`
2. Assign modules with `/assign-module`
...
```

### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `phase` | String | Always "orchestration" |
| `plan_id` | String | Reference to approved plan |
| `status` | String | `pending`, `executing`, `complete` |
| `started_at` | ISO 8601 | When phase started |
| `github_project_id` | String | GitHub Project for sync |
| `sync_enabled` | Boolean | Whether GitHub sync active |
| `modules_total` | Integer | Total module count |
| `modules_completed` | Integer | Completed module count |
| `all_modules_complete` | Boolean | True when all done |
| `verification_mode` | Boolean | In verification phase |
| `verification_loops_remaining` | Integer | Remaining verification loops |

### modules_status Array

Each module entry:

| Field | Type | Description |
|-------|------|-------------|
| `id` | String | Module identifier |
| `status` | String | `pending`, `in-progress`, `complete`, `blocked` |
| `github_issue` | String | Issue number like "#42" |
| `assigned_to` | String | Agent ID or null |
| `pr` | String | PR number when submitted |
| `acceptance_criteria` | String | What defines completion |

### registered_agents Object

Contains two arrays:

**ai_agents**:
| Field | Type | Description |
|-------|------|-------------|
| `agent_id` | String | Unique identifier |
| `session_name` | String | AI Maestro session |
| `registered_at` | ISO 8601 | Registration timestamp |

**human_developers**:
| Field | Type | Description |
|-------|------|-------------|
| `agent_id` | String | Unique identifier |
| `github_username` | String | GitHub handle |

### active_assignments Array

Each assignment:

| Field | Type | Description |
|-------|------|-------------|
| `module` | String | Module ID |
| `agent` | String | Agent ID |
| `status` | String | `assigned`, `working`, `review`, `complete` |
| `instruction_verification` | Object | Verification state |
| `progress_polling` | Object | Polling history |

---

## 5.3 Frontmatter Field Definitions

### Boolean Fields

Boolean fields accept these values:
- `true` / `false` (YAML native)
- `"true"` / `"false"` (string quotes)

The stop hook normalizes all to string comparison for safety.

### String Fields

String fields with special values:
- `"null"` - Represents unset/disabled
- `""` - Empty string, different from null
- Actual values should be quoted if they contain special characters

### Date/Time Fields

All timestamps use ISO 8601 format with timezone:
```
2026-01-09T10:30:00+00:00
```

The `+00:00` suffix indicates UTC. Local time zones are supported:
```
2026-01-09T10:30:00-08:00  # Pacific time
```

### Integer Fields

Integer fields:
- No quotes needed: `iteration: 5`
- 0 often means "unlimited" or "disabled"
- Negative values are invalid

---

## 5.4 How to Manually Edit State Files

### When to Edit Manually

- Reset stuck iteration count
- Fix corrupted field
- Force completion status for testing
- Adjust verification remaining count

### Safe Editing Procedure

1. **Stop Claude Code** - Prevent race conditions

2. **Backup the file**:
   ```bash
   cp design/state/loop.md design/state/loop.md.bak
   ```

3. **Edit with text editor**:
   ```bash
   nano design/state/loop.md
   # or
   vim design/state/loop.md
   ```

4. **Validate YAML syntax**:
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('design/state/loop.md').read())"
   ```

5. **Restart Claude Code**

### Common Manual Edits

**Reset iteration count**:
```yaml
iteration: 1
```

**Skip verification mode**:
```yaml
verification_mode: false
verification_remaining: 0
```

**Force all modules complete**:
```yaml
all_modules_complete: true
modules_completed: 3  # Match modules_total
```

**Change task sources**:
```yaml
check_tasks: false
check_github: true
```

### Warning: Field Consistency

Some fields must be consistent:
- `modules_completed` should match count of modules with `status: complete`
- `all_modules_complete: true` requires all modules to have `status: complete`
- Inconsistencies may cause unexpected behavior

---

## 5.5 State File Corruption Recovery

### Symptoms of Corruption

- Error: "No frontmatter found in state file"
- Error: "State file corrupted (no frontmatter)"
- Error: "Failed to read state file"
- YAML parse errors in log

### Diagnostic Commands

```bash
# Check file exists and is readable
ls -la design/state/loop.md

# Check file starts with ---
head -1 design/state/loop.md

# Validate YAML
python3 -c "
import yaml
with open('design/state/loop.md') as f:
    content = f.read()
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            yaml.safe_load(content[3:end])
            print('YAML valid')
        else:
            print('No closing ---')
    else:
        print('Missing opening ---')
"
```

### Recovery Steps

**Step 1: Backup corrupted file**
```bash
cp design/state/loop.md design/state/loop.corrupted
```

**Step 2: Try to extract valid content**
```bash
# View the file
cat design/state/loop.md

# Check for obvious issues:
# - Missing --- markers
# - Invalid YAML syntax
# - Binary garbage
```

**Step 3: Fix or recreate**

If fixable (minor syntax issue):
```bash
# Edit to fix
nano design/state/loop.md
```

If too corrupted, recreate:
```bash
# Remove corrupted file
rm design/state/loop.md

# Start fresh loop
/orchestrator-loop "Resume my tasks"
```

### Common Corruption Causes

| Cause | Prevention |
|-------|------------|
| Concurrent writes | Lock file should prevent |
| Disk full | Monitor disk space |
| Process killed during write | Uses atomic replace |
| Manual edit errors | Validate YAML after editing |
| Encoding issues | Always use UTF-8 |

### Atomic Write Protection

The stop hook uses atomic writes to prevent corruption:

```python
# Write to temp file first
temp_path = Path(f"{state_file_path}.tmp.{os.getpid()}")
temp_path.write_text(content, encoding="utf-8")

# Atomic replace
temp_path.replace(state_file_path)
```

If you see `.tmp.NNNN` files, a write was interrupted:
```bash
# Clean up temp files
rm -f .claude/*.tmp.*
```
