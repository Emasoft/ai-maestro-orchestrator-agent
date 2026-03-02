# Script Reference - Part 1: Plan Phase Scripts

This document covers the 4 scripts used during Plan Phase.

## Contents

- 1.1 eoa_start_planning.py <!-- TODO: Script not implemented --> - Initializing Plan Phase Mode
- 1.2 eoa_planning_status.py <!-- TODO: Script not implemented --> - Displaying Plan Phase progress
- 1.3 eoa_modify_requirement.py <!-- TODO: Script not implemented --> - Adding, modifying, or removing requirements
- 1.4 eoa_approve_plan.py <!-- TODO: Script not implemented --> - Validating plan and creating GitHub Issues

---

## 1.1 eoa_start_planning.py <!-- TODO: Script not implemented -->

**Purpose:** Initialize Plan Phase Mode.

**Location:** `scripts/eoa_start_planning.py <!-- TODO: Script not implemented -->`

**Usage:**
```bash
python3 eoa_start_planning.py <!-- TODO: Script not implemented --> "User's project goal"
```

**Arguments:**
- `goal` (positional): The user's project goal

**Actions:**
1. Creates `design/state/plan-phase.md`
2. Initializes YAML frontmatter with goal
3. Sets up empty modules list
4. Defines exit criteria

**Exit codes:**
- 0: Success
- 1: Error (already in phase, invalid args)

---

## 1.2 eoa_planning_status.py <!-- TODO: Script not implemented -->

**Purpose:** Display Plan Phase progress.

**Location:** `scripts/eoa_planning_status.py <!-- TODO: Script not implemented -->`

**Usage:**
```bash
python3 eoa_planning_status.py <!-- TODO: Script not implemented -->
python3 eoa_planning_status.py <!-- TODO: Script not implemented --> --json
```

**Arguments:**
- `--json` (optional): Output as JSON

**Output:**
- Plan ID and status
- Goal
- Requirements status
- Modules list with status
- Exit criteria checklist

**Exit codes:**
- 0: Success
- 1: Not in Plan Phase

---

## 1.3 eoa_modify_requirement.py <!-- TODO: Script not implemented -->

**Purpose:** Add, modify, or remove requirements/modules.

**Location:** `scripts/eoa_modify_requirement.py <!-- TODO: Script not implemented -->`

**Usage:**
```bash
# Add requirement
python3 eoa_modify_requirement.py <!-- TODO: Script not implemented --> add --name "Module Name" --description "Description" --priority high

# Modify requirement
python3 eoa_modify_requirement.py <!-- TODO: Script not implemented --> modify <module-id> --add-criteria "New criteria"

# Remove requirement
python3 eoa_modify_requirement.py <!-- TODO: Script not implemented --> remove <module-id>
```

**Actions (add):**
1. Generates unique module ID
2. Adds to modules list
3. Updates state file

**Actions (modify):**
1. Finds module by ID
2. Updates specified fields
3. Logs modification

**Actions (remove):**
1. Validates module is pending
2. Removes from modules list
3. Logs removal

**Exit codes:**
- 0: Success
- 1: Error (module not found, invalid status)

---

## 1.4 eoa_approve_plan.py <!-- TODO: Script not implemented -->

**Purpose:** Validate plan and create GitHub Issues.

**Location:** `scripts/eoa_approve_plan.py <!-- TODO: Script not implemented -->`

**Usage:**
```bash
python3 eoa_approve_plan.py <!-- TODO: Script not implemented -->
python3 eoa_approve_plan.py <!-- TODO: Script not implemented --> --dry-run
```

**Arguments:**
- `--dry-run` (optional): Show what would be done without making changes

**Validation checks:**
1. USER_REQUIREMENTS.md exists
2. All modules have acceptance criteria
3. At least one module defined

**Actions:**
1. Creates GitHub Issue for each module
2. Updates modules with issue numbers
3. Sets `plan_phase_complete: true`

**Exit codes:**
- 0: Success
- 1: Validation failed
- 2: GitHub CLI error

---

**Navigation:**
- [Back to Script Reference Index](script-reference.md)
- [Next: Orchestration Basic Scripts](script-reference-part2-orchestration-basic.md)
