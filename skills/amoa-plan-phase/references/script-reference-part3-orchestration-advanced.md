# Script Reference - Part 3: Orchestration Advanced Scripts

This document covers Orchestration Phase scripts 2.9-2.16 (advanced operations).

## Contents

- 2.9 amoa_check_plan_phase.py - Checking if Plan Phase is complete
- 2.10 amoa_check_orchestration_phase.py - Checking if Orchestration Phase is complete
- 2.11 amoa_sync_github_issues.py - Syncing modules with GitHub Issues
- 2.12 amoa_verify_instructions.py - Managing Instruction Verification Protocol
- 2.13 amoa_poll_agent.py - Sending MANDATORY progress poll
- 2.14 amoa_update_verification.py - Managing mid-implementation changes
- 2.15 amoa_init_design_folders.py - Initializing design folder structure
- 2.16 amoa_compile_handoff.py - Compiling template to handoff document

---

## 2.9 amoa_check_plan_phase.py
**Purpose:** Check if Plan Phase is complete.

**Location:** `scripts/amoa_check_plan_phase.py`

**Usage:**
```bash
python3 amoa_check_plan_phase.pypython3 amoa_check_plan_phase.py --json
```

**Output:**
- Whether in Plan Phase
- Completion status
- Missing exit criteria

**Exit codes:**
- 0: Complete or not in Plan Phase
- 1: Error parsing state file
- 2: Incomplete (used by stop hook)

---

## 2.10 amoa_check_orchestration_phase.py
**Purpose:** Check if Orchestration Phase is complete.

**Location:** `scripts/amoa_check_orchestration_phase.py`

**Usage:**
```bash
python3 amoa_check_orchestration_phase.pypython3 amoa_check_orchestration_phase.py --json
```

**Output:**
- Whether in Orchestration Phase
- Module completion count
- Verification loops remaining
- Blocking reasons

**Exit codes:**
- 0: Complete or not in Orchestration Phase
- 1: Error parsing state file
- 2: Incomplete (used by stop hook)

---

## 2.11 amoa_sync_github_issues.py
**Purpose:** Sync modules with GitHub Issues.

**Location:** `scripts/amoa_sync_github_issues.py`

**Usage:**
```bash
python3 amoa_sync_github_issues.pypython3 amoa_sync_github_issues.py --dry-run
```

**Actions:**
1. Creates issues for modules without issues
2. Updates labels for status changes
3. Closes issues for completed modules

**Exit codes:**
- 0: Success
- 1: GitHub CLI errors

---

## 2.12 amoa_verify_instructions.py

**Purpose:** Manage Instruction Verification Protocol.

**Location:** `scripts/amoa_verify_instructions.py`

**Usage:**
```bash
# Check status
python3 amoa_verify_instructions.py status <agent-id>

# Record repetition received
python3 amoa_verify_instructions.py record-repetition <agent-id> --correct
python3 amoa_verify_instructions.py record-repetition <agent-id>  # incorrect

# Record questions
python3 amoa_verify_instructions.py record-questions <agent-id> --count 2 --answered 2

# Authorize agent
python3 amoa_verify_instructions.py authorize <agent-id>
```

**Exit codes:**
- 0: Success
- 1: Error (agent not found, prerequisites not met)

---

## 2.13 amoa_poll_agent.py

**Purpose:** Send MANDATORY progress poll with 6 questions.

**Location:** `scripts/amoa_poll_agent.py`

**Usage:**
```bash
# Send poll
python3 amoa_poll_agent.py <agent-id>

# Record response
python3 amoa_poll_agent.py <agent-id> --record-response --issues "Issue description"
python3 amoa_poll_agent.py <agent-id> --record-response --issues "Issue" --resolved

# View history
python3 amoa_poll_agent.py <agent-id> --history
```

**Poll message includes ALL 6 mandatory questions.**

**Exit codes:**
- 0: Success
- 1: Error (agent not found, not working)

---

## 2.14 amoa_update_verification.py
**Purpose:** Manage Instruction Update Verification Protocol for mid-implementation changes.

**Location:** `scripts/amoa_update_verification.py`

**Usage:**
```bash
# Send update notification
python3 amoa_update_verification.py send <agent-id> \
  --type requirement_change \
  --description "Added OAuth2 scope requirements"

# Record receipt confirmation
python3 amoa_update_verification.py record-receipt <agent-id> <update-id>

# Record feasibility assessment
python3 amoa_update_verification.py record-feasibility <agent-id> <update-id> \
  --clear  # or --concerns "Concern description"

# Resolve concerns
python3 amoa_update_verification.py resolve-concerns <agent-id> <update-id> \
  --resolution "Provided additional config"

# Authorize resume
python3 amoa_update_verification.py authorize-resume <agent-id> <update-id>

# View update history
python3 amoa_update_verification.py history <agent-id>

# View pending updates
python3 amoa_update_verification.py pending
```

**Update types:**
- `requirement_change`: User requirement modification
- `design_update`: Architecture or design change
- `spec_clarification`: Clarification of existing specs
- `priority_change`: Module priority adjustment
- `scope_change`: Scope expansion or reduction
- `config_update`: Configuration file changes

**Verification status values:**
| Status | Meaning |
|--------|---------|
| `pending_receipt` | Update sent, awaiting confirmation |
| `awaiting_feasibility` | Receipt confirmed, awaiting assessment |
| `addressing_concerns` | Concerns raised, orchestrator responding |
| `ready_to_resume` | All concerns resolved |
| `resumed` | Agent authorized and resumed work |

**State file tracking:**
```yaml
active_assignments:
  - agent: "implementer-1"
    update_verification:
      pending_updates:
        - update_id: "upd-20260108-163022"
          type: "requirement_change"
          description: "Added OAuth2 scope requirements"
          sent_at: "2026-01-08T16:30:22+00:00"
          status: "awaiting_feasibility"
          receipt_confirmed: true
          feasibility_confirmed: false
          concerns_raised: 0
          concerns_resolved: 0
      update_history:
        - update_id: "upd-20260108-150000"
          type: "spec_clarification"
          status: "resumed"
          completed_at: "2026-01-08T15:15:00+00:00"
```

**Configuration feedback loop:**
When implementer needs configuration from orchestrator:
```bash
# Implementer requests config
python3 amoa_update_verification.py send orchestrator \
  --type config_request \
  --description "Need API keys for OAuth2 provider"

# Orchestrator provides config
python3 amoa_update_verification.py resolve-concerns <agent-id> <update-id> \
  --resolution "Config added to design/config/oauth2.env"
```

**Exit codes:**
- 0: Success
- 1: Error (agent not found, update not found, invalid status)

---

## 2.15 amoa_init_design_folders.py
**Purpose:** Initialize standardized design folder structure.

**Location:** `scripts/amoa_init_design_folders.py`

**Usage:**
```bash
# Initialize for single platform
python3 amoa_init_design_folders.py --platforms web

# Initialize for multiple platforms
python3 amoa_init_design_folders.py --platforms web ios android

# Initialize with custom root (default: design)
python3 amoa_init_design_folders.py --platforms web --root custom-design

# Skip template file creation
python3 amoa_init_design_folders.py --platforms web --no-templates
```

**Arguments:**
- `--platforms` (required): Platform names (e.g., web ios android)
- `--root` (optional): Root folder name (default: design)
- `--no-templates` (optional): Skip creating template files

**Actions:**
1. Creates `design/` root directory
2. Creates `designs/shared/` for cross-platform docs
3. Creates `designs/{platform}/templates/`, `specs/`, `rdd/` for each platform
4. Creates `config/shared/` and `config/{platform}/` folders
5. Creates `handoffs/` and `archive/` folders
6. Generates default template files
7. Creates shared architecture docs

**Created folder structure:**
```
design/
├── designs/
│   ├── shared/
│   │   ├── ARCHITECTURE.md
│   │   └── README.md
│   └── {platform}/
│       ├── templates/
│       │   ├── module-spec-template.md
│       │   ├── handoff-template.md
│       │   ├── rdd-template.md
│       │   └── test-plan-template.md
│       ├── specs/
│       └── rdd/
├── config/
│   ├── shared/
│   │   ├── env.example
│   │   └── .gitignore
│   └── {platform}/
├── handoffs/
└── archive/
```

**Exit codes:**
- 0: Success
- 1: Error (permission denied, OS error)

---

## 2.16 amoa_compile_handoff.py
**Purpose:** Compile template to handoff document for implementer.

**Location:** `scripts/amoa_compile_handoff.py`

**Usage:**
```bash
# Compile handoff for module assignment
python3 amoa_compile_handoff.py auth-core implementer-1 --platform web

# With custom template
python3 amoa_compile_handoff.py auth-core implementer-1 --platform web \
    --template custom-handoff-template.md

# Preview without saving
python3 amoa_compile_handoff.py auth-core implementer-1 --platform web --preview
```

**Arguments:**
- `module_id` (positional): Module identifier
- `agent_id` (positional): Agent identifier
- `--platform` (required): Platform name (e.g., web, ios, android)
- `--template` (optional): Custom template path
- `--preview` (optional): Preview without saving
- `--root` (optional): Design folder root (default: design)

**Template placeholders:**
| Placeholder | Filled With |
|-------------|-------------|
| `{{MODULE_NAME}}` | Module name from state |
| `{{MODULE_ID}}` | Module identifier |
| `{{AGENT_ID}}` | Assigned agent |
| `{{TASK_UUID}}` | Generated unique ID |
| `{{GITHUB_ISSUE}}` | Linked issue number |
| `{{ASSIGNED_AT}}` | Current timestamp |
| `{{ACCEPTANCE_CRITERIA}}` | From module data |
| `{{SPEC_PATH}}` | Path to spec file |
| `{{RDD_PATH}}` | Path to RDD file |

**Output:**
Compiled handoff saved to: `design/handoffs/{agent-id}/{module-id}-handoff.md`

**Exit codes:**
- 0: Success
- 1: Error (template not found, permission denied)

---

**Navigation:**
- [Back to Script Reference Index](script-reference.md)
- [Previous: Orchestration Basic Scripts](script-reference-part2-orchestration-basic.md)
- [Next: Modified Scripts](script-reference-part4-modified.md)
