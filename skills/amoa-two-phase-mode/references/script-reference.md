# Script Reference


## Contents

- [Overview](#overview)
- [Part 1: Plan Phase Scripts](#part-1-plan-phase-scripts)
- [Part 2: Orchestration Basic Scripts](#part-2-orchestration-basic-scripts)
- [Part 3: Orchestration Advanced Scripts](#part-3-orchestration-advanced-scripts)
- [Part 4: Design & GitHub Scripts](#part-4-design-github-scripts)
- [Part 5: Modified Scripts](#part-5-modified-scripts)
- [Quick Reference: Exit Codes](#quick-reference-exit-codes)
- [Quick Reference: Script Locations](#quick-reference-script-locations)

---

Complete reference for all Two-Phase Mode Python scripts.

This document serves as an index to the detailed script documentation.

---

## Overview

Two-Phase Mode includes **24 scripts** organized into four categories:

| Category | Script Count | Purpose |
|----------|--------------|---------|
| Plan Phase | 4 | Planning and requirements management |
| Orchestration Phase | 16 | Execution and agent coordination |
| Design & GitHub Scripts | 5 | Design documents and GitHub integration |
| Modified Scripts | 1 | Phase-aware stop hook |

---

## Part 1: Plan Phase Scripts

**File:** [script-reference-part1-plan-phase.md](script-reference-part1-plan-phase.md)

Scripts for managing the Plan Phase:

- **1.1 eoa_start_planning.py** <!-- TODO: Script not implemented --> - Initializing Plan Phase Mode
  - Creates orchestrator-plan-phase.local.md
  - Sets up YAML frontmatter with goal
  - Defines exit criteria

- **1.2 eoa_planning_status.py** <!-- TODO: Script not implemented --> - Displaying Plan Phase progress
  - Shows plan ID, status, goal
  - Lists modules with status
  - Displays exit criteria checklist

- **1.3 eoa_modify_requirement.py** <!-- TODO: Script not implemented --> - Adding, modifying, or removing requirements
  - Add: generates module ID, adds to list
  - Modify: updates fields, logs changes
  - Remove: validates pending status first

- **1.4 eoa_approve_plan.py** <!-- TODO: Script not implemented --> - Validating plan and creating GitHub Issues
  - Validates USER_REQUIREMENTS.md exists
  - Creates GitHub Issue per module
  - Sets plan_phase_complete: true

---

## Part 2: Orchestration Basic Scripts

**File:** [script-reference-part2-orchestration-basic.md](script-reference-part2-orchestration-basic.md)

Basic orchestration operations (2.1-2.8):

- **2.1 eoa_start_orchestration.py** - Initializing Orchestration Phase Mode
  - Requires plan_phase_complete: true
  - Copies modules from plan with issue links
  - Initializes agent registry

- **2.2 eoa_orchestration_status.py** <!-- TODO: Script not implemented --> - Displaying Orchestration Phase progress
  - Module completion count
  - Active assignments and verification status

- **2.3 eoa_register_agent.py** - Registering remote agents
  - Supports AI and human agents
  - Validates AI sessions via AI Maestro

- **2.4 eoa_assign_module.py** - Assigning module to registered agent
  - Creates assignment record with task UUID
  - Sends AI Maestro message for AI agents
  - Initializes instruction verification

- **2.5 eoa_modify_module.py** - Modifying modules during orchestration
  - Add, modify, remove, prioritize subcommands

- **2.6 eoa_reassign_module.py** - Reassigning module to different agent
  - Notifies old and new agents
  - Resets verification status

- **2.7 eoa_check_remote_agents.py** - Polling active AI agents for status
  - Gets all active AI assignments
  - Sends progress poll to each

- **2.8 eoa_notify_agent.py** <!-- TODO: Script not implemented --> - Sending AI Maestro message to specific agent
  - Supports priority levels: normal, high, urgent

---

## Part 3: Orchestration Advanced Scripts

**File:** [script-reference-part3-orchestration-advanced.md](script-reference-part3-orchestration-advanced.md)

Advanced orchestration operations (2.9-2.16):

- **2.9 eoa_check_plan_phase.py** <!-- TODO: Script not implemented --> - Checking if Plan Phase is complete
  - Used by stop hook
  - Exit code 2 = incomplete

- **2.10 eoa_check_orchestration_phase.py** <!-- TODO: Script not implemented --> - Checking if Orchestration Phase is complete
  - Checks module completion and verification loops
  - Used by stop hook

- **2.11 eoa_sync_github_issues.py** <!-- TODO: Script not implemented --> - Syncing modules with GitHub Issues
  - Creates, updates, and closes issues

- **2.12 eoa_verify_instructions.py** - Managing Instruction Verification Protocol
  - Status, record-repetition, record-questions, authorize subcommands

- **2.13 eoa_poll_agent.py** - Sending MANDATORY progress poll
  - Includes all 6 mandatory questions
  - Record response and view history

- **2.14 eoa_update_verification.py** <!-- TODO: Script not implemented --> - Managing mid-implementation changes
  - Update types: requirement_change, design_update, spec_clarification, etc.
  - 5-stage verification: pending_receipt -> awaiting_feasibility -> addressing_concerns -> ready_to_resume -> resumed

- **2.15 eoa_init_design_folders.py** - Initializing design folder structure
  - Creates design/ with requirements/, memory/, handoffs/, config/, archive/
  - Generates templates for each platform
  - Creates index.yaml for tracking documents

- **2.16 eoa_compile_handoff.py** - Compiling template to handoff document
  - Reads module spec from design/requirements/
  - Includes context from design/memory/
  - Outputs to design/handoffs/{agent-id}/

---

## Part 4: Design & GitHub Scripts

Scripts for design document management and GitHub integration:

- **4.1 eoa_init_design_folders.py** - Initialize design folder structure
  - Creates design/memory/, design/handoffs/, design/requirements/
  - Creates template files in each folder
  - Initializes index.yaml for tracking documents
  - Usage: `python3 eoa_init_design_folders.py --platforms web ios android`

- **4.2 eoa_compile_handoff.py** - Compile handoff document for agent
  - Reads module specification from design/requirements/
  - Reads relevant context from design/memory/
  - Generates compiled handoff in design/handoffs/{agent-id}/
  - Usage: `python3 eoa_compile_handoff.py auth-core implementer-1 --platform web`

- **4.3 eoa_design_search.py** - Search design documents
  - Search by UUID, type, status, or keyword
  - Supports all design/*/ subfolders
  - Returns structured results
  - Usage: `python3 eoa_design_search.py --keyword "auth" --type requirements`

- **4.4 eoa_sync_kanban.py** - Sync modules with GitHub Projects kanban
  - Reads active modules from orchestration state
  - Creates/updates GitHub Project items for each module
  - Updates item status based on module status
  - Usage: `python3 eoa_sync_kanban.py --project-id PVT_kwDOBxxxxxx --create-missing`

- **4.5 eoa_create_module_issues.py** - Create GitHub issues for modules
  - Reads module specifications from state file
  - Creates GitHub issue for each module
  - Updates module with issue number
  - Usage: `python3 eoa_create_module_issues.py --all --project-id PVT_kwDOBxxxxxx`

---

## Part 5: Modified Scripts

**File:** [script-reference-part4-modified.md](script-reference-part4-modified.md)

Scripts modified for Two-Phase Mode:

- **3.1 eoa_orchestrator_stop_check.py** <!-- TODO: Script not implemented --> - Phase-aware stop hook
  - Plan Phase: blocks if plan_phase_complete: false
  - Orchestration Phase: blocks if modules incomplete or verification loops remaining
  - Output format: JSON with decision, reason, systemMessage, outputToUser

---

## Quick Reference: Exit Codes

| Exit Code | Meaning |
|-----------|---------|
| 0 | Success |
| 1 | Error (various - see specific script) |
| 2 | Incomplete (used by stop hook scripts) |

---

## Quick Reference: Script Locations

All scripts are located in the `scripts/` directory:

```
scripts/
├── eoa_start_planning.py           # TODO: Script not implemented
├── eoa_planning_status.py          # TODO: Script not implemented
├── eoa_modify_requirement.py       # TODO: Script not implemented
├── eoa_approve_plan.py             # TODO: Script not implemented
├── eoa_start_orchestration.py
├── eoa_orchestration_status.py     # TODO: Script not implemented
├── eoa_register_agent.py
├── eoa_assign_module.py
├── eoa_modify_module.py
├── eoa_reassign_module.py
├── eoa_check_remote_agents.py
├── eoa_notify_agent.py             # TODO: Script not implemented
├── eoa_check_plan_phase.py         # TODO: Script not implemented
├── eoa_check_orchestration_phase.py # TODO: Script not implemented
├── eoa_sync_github_issues.py       # TODO: Script not implemented
├── eoa_verify_instructions.py
├── eoa_poll_agent.py
├── eoa_update_verification.py      # TODO: Script not implemented
├── eoa_init_design_folders.py      # Design folder initialization
├── eoa_compile_handoff.py          # Handoff document compilation
├── eoa_design_search.py            # Design document search
├── eoa_sync_kanban.py              # GitHub Projects kanban sync
├── eoa_create_module_issues.py     # GitHub issue creation for modules
└── eoa_orchestrator_stop_check.py  # TODO: Script not implemented
```
