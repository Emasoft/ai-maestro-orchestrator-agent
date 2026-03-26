# Command Reference

Complete reference for all 16 Two-Phase Mode commands.

## Contents

- 1. Plan Phase Commands (6)
  - 1.1 /start-planning
  - 1.2 /planning-status
  - 1.3 /add-requirement
  - 1.4 /modify-requirement
  - 1.5 /remove-requirement
  - 1.6 /approve-plan
- 2. Orchestration Phase Commands (10)
  - 2.1 /start-orchestration
  - 2.2 /orchestration-status
  - 2.3 /register-agent
  - 2.4 /assign-module
  - 2.5 /add-module
  - 2.6 /modify-module
  - 2.7 /remove-module
  - 2.8 /prioritize-module
  - 2.9 /reassign-module
  - 2.10 /check-agents

---

## 1. Plan Phase Commands

### 1.1 /start-planning

**Purpose:** Enter Plan Phase Mode and begin requirements gathering.

**Syntax:**
```
/start-planning <goal>
```

**Arguments:**
- `goal` (required): The user's project goal (quoted string)

**Example:**
```
/start-planning "Implement user authentication with OAuth2 and session management"
```

**Actions:**
1. Creates `design/state/plan-phase.md`
2. Locks the user goal (immutable)
3. Initializes requirements tracking
4. Sets status to "drafting"

**Prerequisites:** Not in Plan Phase or Orchestration Phase

---

### 1.2 /planning-status

**Purpose:** Display current planning progress and requirements status.

**Syntax:**
```
/planning-status
```

**Arguments:** None

**Output:**
- Plan ID and status
- Requirements file status
- Sections completion progress
- Module breakdown with status
- Exit criteria checklist

**Prerequisites:** Must be in Plan Phase

---

### 1.3 /add-requirement

**Purpose:** Add a new requirement or module to the plan.

**Syntax:**
```
/add-requirement <description> [--module-name <name>] [--priority <level>]
```

**Arguments:**
- `description` (required): Requirement or module description
- `--module-name` (optional): Name for new module
- `--priority` (optional): critical, high, medium, low (default: medium)

**Example:**
```
/add-requirement "User profile management with avatar upload" --module-name "User Profile" --priority high
```

**Actions:**
1. Creates new module entry in state file
2. Updates requirements tracking
3. Updates exit criteria

**Prerequisites:** Must be in Plan Phase, plan not approved

---

### 1.4 /modify-requirement

**Purpose:** Modify an existing requirement or module.

**Syntax:**
```
/modify-requirement <module-id> [--add-criteria <text>] [--set-priority <level>] [--rename <name>]
```

**Arguments:**
- `module-id` (required): Module identifier
- `--add-criteria` (optional): Add acceptance criteria
- `--set-priority` (optional): Change priority
- `--rename` (optional): Change module name

**Example:**
```
/modify-requirement auth-core --add-criteria "Support 2FA authentication"
```

**Actions:**
1. Updates module in state file
2. Logs modification

**Prerequisites:** Must be in Plan Phase, module must exist

---

### 1.5 /remove-requirement

**Purpose:** Remove a requirement or module from the plan.

**Syntax:**
```
/remove-requirement <module-id>
```

**Arguments:**
- `module-id` (required): Module identifier

**Example:**
```
/remove-requirement legacy-api-support
```

**Restrictions:**
- Can only remove modules with status "pending" or "planned"
- Cannot remove if GitHub Issue already created

**Actions:**
1. Removes module from state file
2. Logs removal

**Prerequisites:** Must be in Plan Phase, module status must be pending/planned

---

### 1.6 /approve-plan

**Purpose:** Approve the plan and transition to Orchestration Phase.

**Syntax:**
```
/approve-plan
```

**Arguments:** None

**Actions:**
1. Validates all exit criteria met
2. Creates GitHub Issues for all modules
3. Sets `plan_phase_complete: true`
4. Outputs transition summary

**Validation checks:**
- USER_REQUIREMENTS.md exists and complete
- All modules have acceptance criteria
- At least one module defined

**Prerequisites:** Must be in Plan Phase, all exit criteria must be met

---

## 2. Orchestration Phase Commands

### 2.1 /start-orchestration

**Purpose:** Enter Orchestration Phase after plan approval.

**Syntax:**
```
/start-orchestration
```

**Arguments:** None

**Actions:**
1. Creates `design/state/exec-phase.md`
2. Copies modules from plan with GitHub issue links
3. Initializes agent registry
4. Sets status to "executing"

**Prerequisites:** Plan Phase must be complete (`plan_phase_complete: true`)

---

### 2.2 /orchestration-status

**Purpose:** Display orchestration progress and agent status.

**Syntax:**
```
/orchestration-status
```

**Arguments:** None

**Output:**
- Module completion progress
- Active assignments with status
- Verification status per agent
- Poll history summary
- Blocking issues
- Next poll due time

**Prerequisites:** Must be in Orchestration Phase

---

### 2.3 /register-agent

**Purpose:** Register a remote agent (AI or human) for task assignment.

**Syntax:**
```
/register-agent <type> <identifier>
```

**Arguments:**
- `type` (required): `ai` or `human`
- `identifier` (required): Session name (AI) or GitHub username (human)

**Examples:**
```
/register-agent ai helper-agent-generic
/register-agent human dev-alice
```

**Actions:**
1. Adds agent to registered_agents in state file
2. Validates AI agent session exists (for AI type)
3. Logs registration

**Prerequisites:** Must be in Orchestration Phase

---

### 2.4 /assign-module

**Purpose:** Assign a module to a registered agent.

**Syntax:**
```
/assign-module <module-id> <agent-id>
```

**Arguments:**
- `module-id` (required): Module identifier
- `agent-id` (required): Registered agent identifier

**Example:**
```
/assign-module auth-core implementer-1
```

**Actions:**
1. Creates active assignment record
2. Generates task UUID
3. Updates module status to "assigned"
4. Sends assignment message (for AI agents)
5. Initiates Instruction Verification Protocol

**Prerequisites:** Must be in Orchestration Phase, agent must be registered, module must be pending

---

### 2.5 /add-module

**Purpose:** Add a new module during orchestration.

**Syntax:**
```
/add-module <name> [--priority <level>] [--description <text>]
```

**Arguments:**
- `name` (required): Module name
- `--priority` (optional): Priority level
- `--description` (optional): Module description

**Example:**
```
/add-module "Password Reset Flow" --priority high
```

**Actions:**
1. Creates GitHub Issue
2. Adds to modules_status
3. Increments modules_total
4. Updates stop hook completion criteria

**Prerequisites:** Must be in Orchestration Phase

---

### 2.6 /modify-module

**Purpose:** Modify a module during orchestration.

**Syntax:**
```
/modify-module <module-id> [--add-criteria <text>] [--set-description <text>]
```

**Arguments:**
- `module-id` (required): Module identifier
- `--add-criteria` (optional): Add acceptance criteria
- `--set-description` (optional): Change description

**Example:**
```
/modify-module auth-core --add-criteria "Support remember-me checkbox"
```

**Actions:**
1. Updates module in state file
2. Updates GitHub Issue
3. Notifies assigned agent (if any)

**Prerequisites:** Must be in Orchestration Phase, module must exist

---

### 2.7 /remove-module

**Purpose:** Remove a module during orchestration.

**Syntax:**
```
/remove-module <module-id>
```

**Arguments:**
- `module-id` (required): Module identifier

**Restrictions:**
- Can only remove modules with status "pending"
- Cannot remove assigned or in-progress modules

**Actions:**
1. Closes GitHub Issue
2. Removes from modules_status
3. Decrements modules_total

**Prerequisites:** Must be in Orchestration Phase, module status must be pending

---

### 2.8 /prioritize-module

**Purpose:** Change module priority.

**Syntax:**
```
/prioritize-module <module-id> --priority <level>
```

**Arguments:**
- `module-id` (required): Module identifier
- `--priority` (required): critical, high, medium, low

**Example:**
```
/prioritize-module oauth-google --priority critical
```

**Actions:**
1. Updates module priority
2. Updates GitHub Issue labels

**Prerequisites:** Must be in Orchestration Phase, module must exist

---

### 2.9 /reassign-module

**Purpose:** Reassign a module to a different agent.

**Syntax:**
```
/reassign-module <module-id> --to <agent-id>
```

**Arguments:**
- `module-id` (required): Module identifier
- `--to` (required): New agent identifier

**Example:**
```
/reassign-module auth-core --to implementer-2
```

**Restrictions:**
- Only for modules with status "pending", "assigned", or "blocked"
- Cannot reassign "in-progress" modules

**Actions:**
1. Notifies old agent to stop
2. Updates assignment
3. Resets verification status
4. Notifies new agent

**Prerequisites:** Must be in Orchestration Phase, both module and new agent must exist

---

### 2.10 /check-agents

**Purpose:** Send progress polls to all active AI agents.

**Syntax:**
```
/check-agents
```

**Arguments:** None

**Actions:**
1. Identifies all active AI agent assignments
2. Sends progress poll with 6 mandatory questions to each
3. Updates poll tracking in state file

**Output:**
- List of agents polled
- Next poll due times

**Prerequisites:** Must be in Orchestration Phase, at least one active AI assignment
