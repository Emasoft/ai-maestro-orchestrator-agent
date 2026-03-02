# Operation: Add Module Mid-Orchestration


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Command Syntax](#command-syntax)
- [Steps](#steps)
- [GitHub Issue Body Template](#github-issue-body-template)
- [Module: <NAME>](#module-name)
  - [Acceptance Criteria](#acceptance-criteria)
- [Output](#output)
- [Success Criteria](#success-criteria)
- [State File Entry](#state-file-entry)
- [Error Handling](#error-handling)
- [Validation Rules](#validation-rules)
- [Important Rules](#important-rules)
- [Next Operations](#next-operations)

## Metadata

| Field | Value |
|-------|-------|
| Operation ID | `op-add-module-midorchestration` |
| Procedure | `proc-update-tasks` |
| Workflow Step | Step 16 |
| Trigger | User requests new feature during orchestration |
| Actor | Orchestrator (EOA) |
| Command | `/add-module` |

---

## Purpose

Add a new module to the orchestration plan during the Execution Phase. This creates a new work unit that will be assigned to an implementer and tracked via GitHub Issue.

---

## Prerequisites

- Orchestration Phase is active
- Plan Phase completed and approved
- GitHub CLI (gh) authenticated
- AI Maestro running for notifications
- State file `design/state/exec-phase.md` exists

---

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Display name for the module (human-readable) |
| `criteria` | Yes | Acceptance criteria (what must be implemented) |
| `priority` | No | Priority level: critical, high, medium (default), low |

---

## Command Syntax

```bash
/add-module "<NAME>" --criteria "<CRITERIA_TEXT>" [--priority LEVEL]
```

**Examples**:

```bash
# Basic usage
/add-module "Two-Factor Auth" --criteria "Support TOTP and SMS verification"

# With priority
/add-module "Rate Limiting" --criteria "Implement 100 req/min per user" --priority critical

# Multi-criteria (newline-separated)
/add-module "User Profile" --criteria "Display name editing
Avatar upload
Email change with verification"
```

---

## Steps

1. **Validate inputs**:
   - Name is non-empty
   - Criteria is non-empty
   - Priority is valid if provided

2. **Generate module ID**:
   - Convert name to kebab-case
   - Ensure uniqueness in state file
   - Example: "Two-Factor Auth" -> "two-factor-auth"

3. **Create GitHub Issue**:
   ```bash
   gh issue create \
     --title "[Module] <NAME>" \
     --body "<CRITERIA_AND_METADATA>" \
     --label "module,priority-<LEVEL>,status:pending"
   ```

4. **Update state file** (`design/state/exec-phase.md`):
   ```yaml
   modules_status:
     - id: "<module_id>"
       name: "<NAME>"
       status: "pending"
       assigned_to: null
       github_issue: "#<ISSUE_NUMBER>"
       pr: null
       verification_loops: 0
       acceptance_criteria: "<CRITERIA>"
       priority: "<LEVEL>"
   ```

5. **Update stop hook** if applicable (add module to completion check)

6. **Log the addition** in orchestration log

---

## GitHub Issue Body Template

```markdown
## Module: <NAME>

**Priority**: <LEVEL>
**Status**: Pending assignment

### Acceptance Criteria

<CRITERIA_TEXT>

---

*This issue was created by the orchestrator. Do not close manually.*
*Linked module ID: <module_id>*
```

---

## Output

| Output | Format | Description |
|--------|--------|-------------|
| Module created | State file entry | YAML in exec-phase.md |
| GitHub Issue | Issue number | `#123` |
| Console confirmation | Text | "Module '<name>' created as #123" |

---

## Success Criteria

- Module entry exists in state file with correct data
- GitHub Issue created with correct labels
- Issue number recorded in state file
- Priority label matches specified priority

---

## State File Entry

```yaml
modules_status:
  - id: "two-factor-auth"
    name: "Two-Factor Auth"
    status: "pending"
    assigned_to: null
    github_issue: "#42"
    pr: null
    verification_loops: 0
    acceptance_criteria: "Support TOTP and SMS verification"
    priority: "high"
```

---

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Duplicate module ID | Name already exists | Append number suffix (-2, -3) |
| gh CLI not authenticated | Auth expired | Run `gh auth login` |
| State file not found | Wrong phase | Verify Orchestration Phase active |
| GitHub Issue creation fails | Network or permissions | Retry, check repository access |

---

## Validation Rules

1. **Name validation**:
   - 3-100 characters
   - No special characters except spaces and hyphens

2. **Criteria validation**:
   - Non-empty
   - At least 10 characters

3. **Priority validation**:
   - Must be: critical, high, medium, low
   - Defaults to medium if not specified

---

## Important Rules

1. **Every module gets an issue** - No exceptions
2. **Issue labels must match** - Priority and status labels synchronized
3. **ID is immutable** - Once created, module ID never changes
4. **Criteria can be updated** - Use `/modify-module` for changes

---

## Next Operations

After adding module:
- Assign to implementer: `/assign-module <module_id> --to <agent_id>`
- View all modules: `/orchestration-status`
- Modify if needed: `/modify-module <module_id> ...`
