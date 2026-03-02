# Two-Phase Mode Skill

**Version**: 1.0.0
**For**: EOA (Emasoft Orchestrator Agent) Plugin v2.4.0+

## Overview

Two-Phase Mode implements a structured workflow for large-scale project orchestration:

| Phase | Purpose | Exit Condition |
|-------|---------|----------------|
| **Plan Phase** | Write requirements, design architecture, break down into modules | All requirements documented, user approved |
| **Orchestration Phase** | Direct remote agents to implement modules | All modules implemented, 4 verification loops |

## Key Features

- **Completion Enforcement**: Stop hook blocks exit until ALL current tasks complete
- **Dynamic Flexibility**: User can add/change/remove features at any time
- **Remote Agent Coordination**: AI agents (via AI Maestro) and human developers (via GitHub)
- **Instruction Verification Protocol**: Mandatory understanding verification before implementation
- **Proactive Progress Polling**: 6 mandatory questions every 10-15 minutes
- **3-Choice Response Rule**: Structured decision tree for handling implementer issues

## Directory Structure

```
two-phase-mode/
├── README.md              # This file
├── SKILL.md              # Main skill entry point
└── references/
    ├── plan-phase-workflow.md           # Plan Phase procedures
    ├── orchestration-phase-workflow.md  # Orchestration Phase procedures
    ├── instruction-verification-protocol.md  # Mandatory verification protocol
    ├── proactive-progress-polling.md    # Polling protocol + 3-choice rule
    ├── state-file-formats.md            # YAML state file specifications
    ├── command-reference.md             # All 16 commands
    └── script-reference.md              # All 17 scripts
```

## Commands Summary

### Plan Phase Commands (6)

| Command | Purpose |
|---------|---------|
| `/start-planning` | Enter Plan Phase Mode |
| `/planning-status` | View requirements progress |
| `/add-requirement` | Add requirement to plan |
| `/modify-requirement` | Change requirement |
| `/remove-requirement` | Remove pending requirement |
| `/approve-plan` | Transition to Orchestration Phase |

### Orchestration Phase Commands (10)

| Command | Purpose |
|---------|---------|
| `/start-orchestration` | Enter Orchestration Phase |
| `/orchestration-status` | View module/agent status |
| `/register-agent` | Register remote agent |
| `/assign-module` | Assign module to agent |
| `/add-module` | Add module mid-orchestration |
| `/modify-module` | Change module specs |
| `/remove-module` | Remove pending module |
| `/prioritize-module` | Change module priority |
| `/reassign-module` | Reassign to different agent |
| `/check-agents` | Poll all active agents |

## Scripts Summary

### Plan Phase Scripts (4)

- `eoa_start_planning.py` - Initialize Plan Phase <!-- TODO: Script not implemented -->
- `eoa_planning_status.py` - Display planning progress <!-- TODO: Script not implemented -->
- `eoa_modify_requirement.py` - Add/modify/remove requirements <!-- TODO: Script not implemented -->
- `eoa_approve_plan.py` - Validate plan, create GitHub Issues <!-- TODO: Script not implemented -->

### Orchestration Phase Scripts (13)

- `eoa_start_orchestration.py` - Initialize Orchestration Phase
- `eoa_orchestration_status.py` - Display orchestration progress <!-- TODO: Script not implemented -->
- `eoa_register_agent.py` - Register remote agent
- `eoa_assign_module.py` - Assign module to agent
- `eoa_modify_module.py` - Add/modify/remove/prioritize modules
- `eoa_reassign_module.py` - Reassign module to different agent
- `eoa_check_remote_agents.py` - Poll active AI agents
- `eoa_notify_agent.py` - Send AI Maestro message <!-- TODO: Script not implemented -->
- `eoa_check_plan_phase.py` - Check plan phase completion <!-- TODO: Script not implemented -->
- `eoa_check_orchestration_phase.py` - Check orchestration phase completion <!-- TODO: Script not implemented -->
- `eoa_sync_github_issues.py` - Sync with GitHub Issues <!-- TODO: Script not implemented -->
- `eoa_verify_instructions.py` - Instruction Verification Protocol
- `eoa_poll_agent.py` - Proactive Progress Polling

### Modified Scripts (1)

- `eoa_orchestrator_stop_check.py` - Phase-aware stop hook <!-- TODO: Script not implemented -->

## Quick Start

### Starting a New Project

```bash
# 1. Enter Plan Phase
/start-planning "Your project goal here"

# 2. Add requirements and modules
/add-requirement "Feature description" --module-name "Feature Name" --priority high

# 3. Check planning progress
/planning-status

# 4. When ready, approve plan (creates GitHub Issues)
/approve-plan

# 5. Enter Orchestration Phase
/start-orchestration

# 6. Register remote agents
/register-agent ai helper-agent-generic
/register-agent human dev-alice

# 7. Assign modules to agents
/assign-module auth-core implementer-1

# 8. Monitor progress
/orchestration-status
/check-agents
```

## Critical Protocols

### Instruction Verification Protocol (MANDATORY)

Before ANY remote agent begins implementation:
1. Send module assignment with specs
2. Request agent to repeat understanding
3. Verify repetition is correct
4. Request clarifying questions
5. Answer ALL questions
6. Authorize implementation

### 3-Choice Response Rule (MANDATORY)

When implementer reports an issue, orchestrator has EXACTLY 3 choices:

| Choice | When to Use | Action |
|--------|-------------|--------|
| **1. Explain** | Lack of understanding / unclear specs | Explain again with more detail |
| **2. Rewrite** | Unforeseen circumstances / orchestrator's requirements impossible | Write new requirements, full verification |
| **3. Escalate** | User's CORE REQUIREMENTS impossible | Stop, ask user, record decision |

Minor issues (regular bugs, code-level problems) are left to the implementer.

## State Files

| File | Phase |
|------|-------|
| `design/state/plan-phase.md` | Plan Phase |
| `design/state/exec-phase.md` | Orchestration Phase |

Both files use YAML frontmatter format and are gitignored (`.local.md` suffix).

## Related Documentation

- [SKILL.md](./SKILL.md) - Main skill entry point
- [Command Reference](./references/command-reference.md) - All 16 commands
- [Script Reference](./references/script-reference.md) - All 17 scripts
- [State File Formats](./references/state-file-formats.md) - YAML schemas

## Requirements

- EOA (Emasoft Orchestrator Agent) Plugin v2.4.0+
- AI Maestro messaging system (AMP) running (routing handled automatically)
- GitHub CLI (`gh`) installed and authenticated
- Python 3.8+ with PyYAML
