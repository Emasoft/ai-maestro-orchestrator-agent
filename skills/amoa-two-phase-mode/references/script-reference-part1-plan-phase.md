# Script Reference - Part 1: Plan Phase Scripts

This document covers the 4 scripts used during Plan Phase.

## Contents

- 1.1 amoa_start_planning.py - Initializing Plan Phase Mode
- 1.2 amoa_planning_status.py - Displaying Plan Phase progress
- 1.3 amoa_modify_requirement.py - Adding, modifying, or removing requirements
- 1.4 amoa_approve_plan.py - Validating plan and creating GitHub Issues

---

## 1.1 amoa_start_planning.py
**Purpose:** Initialize Plan Phase Mode.

**Location:** `scripts/amoa_start_planning.py`

**Usage:**
```bash
python3 amoa_start_planning.py "User's project goal"
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

## 1.2 amoa_planning_status.py
**Purpose:** Display Plan Phase progress.

**Location:** `scripts/amoa_planning_status.py`

**Usage:**
```bash
python3 amoa_planning_status.pypython3 amoa_planning_status.py --json
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

## 1.3 amoa_modify_requirement.py
**Purpose:** Add, modify, or remove requirements/modules.

**Location:** `scripts/amoa_modify_requirement.py`

**Usage:**
```bash
# Add requirement
python3 amoa_modify_requirement.py add --name "Module Name" --description "Description" --priority high

# Modify requirement
python3 amoa_modify_requirement.py modify <module-id> --add-criteria "New criteria"

# Remove requirement
python3 amoa_modify_requirement.py remove <module-id>
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

## 1.4 amoa_approve_plan.py
**Purpose:** Validate plan and create GitHub Issues.

**Location:** `scripts/amoa_approve_plan.py`

**Usage:**
```bash
python3 amoa_approve_plan.pypython3 amoa_approve_plan.py --dry-run
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
