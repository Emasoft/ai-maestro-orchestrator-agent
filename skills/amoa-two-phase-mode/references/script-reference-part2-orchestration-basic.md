# Script Reference - Part 2: Orchestration Basic Scripts

This document covers Orchestration Phase scripts 2.1-2.8 (basic operations).

## Contents

- 2.1 eoa_start_orchestration.py - Initializing Orchestration Phase Mode
- 2.2 eoa_orchestration_status.py <!-- TODO: Script not implemented --> - Displaying Orchestration Phase progress
- 2.3 eoa_register_agent.py - Registering remote agents
- 2.4 eoa_assign_module.py - Assigning module to registered agent
- 2.5 eoa_modify_module.py - Modifying modules during orchestration
- 2.6 eoa_reassign_module.py - Reassigning module to different agent
- 2.7 eoa_check_remote_agents.py - Polling active AI agents for status
- 2.8 eoa_notify_agent.py <!-- TODO: Script not implemented --> - Sending AI Maestro message to specific agent

---

## 2.1 eoa_start_orchestration.py

**Purpose:** Initialize Orchestration Phase Mode.

**Location:** `scripts/eoa_start_orchestration.py`

**Usage:**
```bash
python3 eoa_start_orchestration.py
```

**Prerequisites:**
- Plan Phase complete (`plan_phase_complete: true`)

**Actions:**
1. Creates `design/state/exec-phase.md`
2. Copies modules from plan with GitHub issue links
3. Initializes agent registry
4. Sets status to "executing"

**Exit codes:**
- 0: Success
- 1: Plan Phase not complete

---

## 2.2 eoa_orchestration_status.py <!-- TODO: Script not implemented -->

**Purpose:** Display Orchestration Phase progress.

**Location:** `scripts/eoa_orchestration_status.py <!-- TODO: Script not implemented -->`

**Usage:**
```bash
python3 eoa_orchestration_status.py <!-- TODO: Script not implemented -->
python3 eoa_orchestration_status.py <!-- TODO: Script not implemented --> --json
```

**Output:**
- Module completion count
- Module status list
- Active assignments
- Verification status
- Poll schedule

**Exit codes:**
- 0: Success
- 1: Not in Orchestration Phase

---

## 2.3 eoa_register_agent.py

**Purpose:** Register remote agents (AI or human).

**Location:** `scripts/eoa_register_agent.py`

**Usage:**
```bash
python3 eoa_register_agent.py ai helper-agent-generic
python3 eoa_register_agent.py human dev-alice
```

**Arguments:**
- `type` (positional): `ai` or `human`
- `identifier` (positional): Session name or GitHub username

**Actions:**
1. Validates agent type
2. For AI: validates session exists via AI Maestro
3. Adds to registered_agents
4. Generates agent_id

**Exit codes:**
- 0: Success
- 1: Invalid type or identifier

---

## 2.4 eoa_assign_module.py

**Purpose:** Assign module to registered agent.

**Location:** `scripts/eoa_assign_module.py`

**Usage:**
```bash
python3 eoa_assign_module.py auth-core implementer-1
```

**Arguments:**
- `module-id` (positional): Module identifier
- `agent-id` (positional): Agent identifier

**Actions:**
1. Validates module exists and is pending
2. Validates agent is registered
3. Creates assignment record
4. Generates task UUID
5. Sends AI Maestro message (for AI agents)
6. Initializes instruction verification

**Exit codes:**
- 0: Success
- 1: Module or agent not found

---

## 2.5 eoa_modify_module.py

**Purpose:** Modify modules during orchestration.

**Location:** `scripts/eoa_modify_module.py`

**Usage:**
```bash
# Add module
python3 eoa_modify_module.py add --name "Module Name" --priority high

# Modify module
python3 eoa_modify_module.py modify <module-id> --add-criteria "New criteria"

# Remove module
python3 eoa_modify_module.py remove <module-id>

# Prioritize module
python3 eoa_modify_module.py prioritize <module-id> --priority critical
```

**Actions vary by subcommand** - see individual command documentation.

**Exit codes:**
- 0: Success
- 1: Error (module not found, invalid operation)

---

## 2.6 eoa_reassign_module.py

**Purpose:** Reassign module to different agent.

**Location:** `scripts/eoa_reassign_module.py`

**Usage:**
```bash
python3 eoa_reassign_module.py auth-core --to implementer-2
```

**Arguments:**
- `module-id` (positional): Module identifier
- `--to` (required): New agent identifier

**Actions:**
1. Validates module can be reassigned
2. Notifies old agent (AI Maestro message)
3. Updates assignment
4. Resets verification status
5. Notifies new agent

**Exit codes:**
- 0: Success
- 1: Cannot reassign (in-progress, etc.)

---

## 2.7 eoa_check_remote_agents.py

**Purpose:** Poll all active AI agents for status.

**Location:** `scripts/eoa_check_remote_agents.py`

**Usage:**
```bash
python3 eoa_check_remote_agents.py
```

**Actions:**
1. Gets all active AI assignments
2. Sends progress poll to each
3. Updates poll tracking

**Exit codes:**
- 0: Success (or no agents to poll)
- 1: AI Maestro connection error

---

## 2.8 eoa_notify_agent.py <!-- TODO: Script not implemented -->

**Purpose:** Send AI Maestro message to specific agent.

**Location:** `scripts/eoa_notify_agent.py <!-- TODO: Script not implemented -->`

**Usage:**
```bash
python3 eoa_notify_agent.py <!-- TODO: Script not implemented --> implementer-1 --subject "Subject" --message "Message body" --priority high
```

**Arguments:**
- `agent-id` (positional): Agent identifier
- `--subject` (required): Message subject
- `--priority` (optional): normal, high, urgent (default: normal)
- `--type` (optional): Message type (default: notification)

**Exit codes:**
- 0: Success
- 1: Agent not found or not AI type

---

**Navigation:**
- [Back to Script Reference Index](script-reference.md)
- [Previous: Plan Phase Scripts](script-reference-part1-plan-phase.md)
- [Next: Orchestration Advanced Scripts](script-reference-part3-orchestration-advanced.md)
