---
name: eoa-two-phase-mode
description: "Use when orchestrating complex projects. Trigger with multi-module or two-phase planning requests."
license: Apache-2.0
compatibility: Requires AI Maestro messaging system, GitHub CLI (gh), remote agents registered by user, and YAML frontmatter state files. Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 2.6.0
context: fork
user-invocable: false
agent: eoa-main
workflow-instruction: "Step 10"
procedure: "proc-decompose-design"
---

# Two-Phase Mode Skill

## Overview

Two-Phase Mode separates orchestration into two distinct phases:

## Prerequisites

- AI Maestro messaging system running
- GitHub CLI (gh) authenticated
- Remote agents registered by user
- Understanding of YAML frontmatter state files

## Output

| Output Type | Location | Description |
|-------------|----------|-------------|
| Plan Phase State | `.claude/orchestrator-plan-phase.local.md` | YAML frontmatter with requirements, modules, criteria |
| Orchestration State | `.claude/orchestrator-orchestration-phase.local.md` | YAML frontmatter with agent assignments, module status |
| Design Documents | `design/<platform>/` | Templates, handoffs, RDD files, specs |
| GitHub Issues | GitHub repository | Module issues created from approved plan |
| Claude Tasks | Claude Code session | Persistent task tracking across compacting |

## Instructions

1. **Understand the two phases**: Plan Phase (requirements) and Orchestration Phase (implementation).

   | Phase | Purpose | Activities | Exit Condition |
   |-------|---------|------------|----------------|
   | **Plan Phase** | Write requirements | Design specs, architecture, task breakdown | All requirements documented + user approval |
   | **Orchestration Phase** | Direct implementation | Coordinate remote agents module by module | All modules implemented + 4 verification loops |

2. **Start Plan Phase**: Use `/start-planning` command to create state file and begin requirements documentation.

3. **Document requirements**: Write USER_REQUIREMENTS.md, define architecture, break down modules, set acceptance criteria.

4. **Approve plan**: Use `/approve-plan` to transition to Orchestration Phase and create GitHub issues.

5. **Start Orchestration Phase**: Use `/start-orchestration` to initialize orchestration state file.

6. **Register agents**: Use `/register-agent` to register remote AI agents or human developers.

7. **Assign modules**: Use `/assign-module` to assign modules to registered agents.

8. **Verify instructions**: Execute Instruction Verification Protocol before authorizing implementation.

9. **Poll progress**: Use `/check-agents` every 10-15 minutes to actively poll implementers.

10. **Handle updates**: If requirements change, use Instruction Update Verification Protocol.

11. **Complete verification loops**: Each module requires 4 verification loops before completion.

12. **Exit when complete**: Stop hook ensures all modules are complete before allowing exit.

## Core Principle: Dynamic Flexibility with Completion Enforcement

The orchestrator enforces completion of CURRENT tasks while allowing dynamic modifications.

| Aspect | Behavior |
|--------|----------|
| **User can always** | Add features, change requirements, remove pending items |
| **System enforces** | All CURRENT tasks must complete before stopping |
| **Dynamic tracking** | Stop hook checks CURRENT state, not original state |

**How it works:** If user adds OAuth2 module, stop hook blocks until OAuth2 is ALSO complete. If user removes OAuth2 (before started), it's no longer tracked.

---

## Core Principle: Claude Tasks Scheduling (CRITICAL)

**MANDATORY**: All instructions must be immediately scheduled as Claude Tasks. This is non-negotiable.

| Principle | Description |
|-----------|-------------|
| **Immediate scheduling** | When receiving any instruction, create Claude Tasks FIRST before acting |
| **Persistence across compacting** | Claude Tasks persist via TaskList API, surviving context compacting |
| **Series closure** | Every task series ends with: verification checklist, archive record, commit |
| **Recovery capability** | Agents can recover state after compacting by reading Claude Tasks |

**Why this matters:** Claude Code context windows compact during long sessions. Without Claude Tasks, agents forget instructions and progress. Claude Code native Tasks provide persistent memory.

See [references/native-task-persistence.md](references/native-task-persistence.md) for complete documentation.

---

## Reference Files

### Plan Phase Workflow ([references/plan-phase-workflow.md](references/plan-phase-workflow.md))

Complete workflow for Plan Phase Mode.

| Section | Topics |
|---------|--------|
| 1. Entering Plan Phase | /start-planning command, state file initialization |
| 2. Planning Activities | User goals, USER_REQUIREMENTS.md, architecture, modules, acceptance criteria |
| 3. Modifying the Plan | /add-requirement, /modify-requirement, /remove-requirement |
| 4. Plan Phase Completion | Exit criteria checklist, /approve-plan, GitHub Issues creation |

**When to use:** Starting a new project, entering planning mode, modifying requirements.

---

### Orchestration Phase Workflow ([references/orchestration-phase-workflow.md](references/orchestration-phase-workflow.md))

Complete workflow for Orchestration Phase Mode.

| Section | Topics |
|---------|--------|
| 1. Entering Orchestration Phase | /start-orchestration command, state file structure |
| 2. Agent Registration | /register-agent, AI agents vs human developers, agent types |
| 3. Module Assignment | /assign-module, /reassign-module |
| 4. Monitoring Progress | /orchestration-status, /check-agents for polling |
| 5. Modifying During Orchestration | /add-module, /modify-module, /remove-module, /prioritize-module |
| 6. Completion and Exit | All modules complete criteria, 4-verification loops, stop hook |

**When to use:** After plan approval, during module implementation, managing remote agents.

**Prerequisite:** Plan Phase Workflow

---

### Instruction Verification Protocol ([references/instruction-verification-protocol.md](references/instruction-verification-protocol.md))

**MANDATORY** protocol before ANY remote agent begins implementation.

| Section | Topics |
|---------|--------|
| 1. Why This Protocol Exists | Reasons for misinterpretation, orchestrator responsibility |
| 2. The 8-Step Protocol Flow | Send assignment, request repetition, verify, answer questions, authorize |
| 3. Message Templates | Initial assignment, correction, question resolution, authorization |
| 4. Tracking Verification Status | State file fields, status values |
| 5. Failure Conditions | When NOT to authorize, action on failure |

**When to use:** After assigning a module, before authorizing implementation.

**Prerequisite:** Orchestration Phase Workflow

---

### Proactive Progress Polling Protocol ([references/proactive-progress-polling.md](references/proactive-progress-polling.md))

**MANDATORY** polling protocol with 6 required questions every 10-15 minutes.

| Section | Topics |
|---------|--------|
| 1. Why This Protocol Exists | Never assume "no news is good news", orchestrator MUST actively ask |
| 2. The 6 Mandatory Poll Questions | Progress, next steps, issues, unclear items, difficulties, needs |
| 3. Poll Message Template | Full template with all 6 questions |
| 4. Response Actions | Action table by response type, Adapt-or-Escalate decision tree |
| 5. Poll Tracking | State file polling fields, poll history structure |

**When to use:** Every 10-15 minutes during active implementation, when agent silent too long.

**Prerequisite:** Instruction Verification Protocol

---

### Instruction Update Verification Protocol ([references/instruction-update-verification-protocol.md](references/instruction-update-verification-protocol.md))

**MANDATORY** protocol whenever sending UPDATED instructions to an implementer who is ALREADY working.

| Section | Topics |
|---------|--------|
| 1. When This Protocol Applies | Triggers (requirement change, design update, spec clarification) |
| 2. The 5-Step Update Verification Flow | Send update, confirm receipt, assess feasibility, address concerns, authorize resume |
| 3. Message Templates | Update notification, feasibility request, concern resolution, resume auth |
| 4. Tracking Update Verification | State file fields, status values |
| 5. Special Cases | Minor clarifications, major design changes, user requirement changes |
| 6. Configuration Feedback Loop | When implementer needs config changes from orchestrator |

**When to use:** When sending any update mid-implementation, changing requirements, handling config feedback.

**Prerequisite:** Proactive Progress Polling Protocol

---

### State File Formats ([references/state-file-formats.md](references/state-file-formats.md))

Complete YAML frontmatter specifications for both phase state files.

| Section | Topics |
|---------|--------|
| 1. Plan Phase State File | Location, complete YAML schema, field descriptions |
| 2. Orchestration Phase State File | Location, complete YAML schema, field descriptions |
| 3. Agent Assignment Structure | Assignment fields, verification tracking, polling tracking |
| 4. Module Status Structure | Module fields, status values |

**When to use:** Creating/parsing state files, understanding structure, debugging state issues.

---

### Design Folder Structure ([references/design-folder-structure.md](references/design-folder-structure.md))

Standardized folder structure for design documents, templates, handoffs, and RDD files.

| Section | Topics |
|---------|--------|
| 1. Why a Standardized Structure | Git tracking, per-platform organization, single source of truth |
| 2. Folder Structure Specification | Root location (design/), per-platform structure, directory tree |
| 3. File Types and Locations | Templates, handoffs, RDD files, config files, specs |
| 4. Usage Workflow | Creating files, compiling templates, storing responses |
| 5. Git Tracking Rules | What to track, what to gitignore |
| 6. Multi-Platform Projects | Shared resources, platform-specific customization |

**When to use:** Setting up design folder, creating templates, compiling handoffs.

**Prerequisite:** Plan Phase Workflow

---

### Command Reference ([references/command-reference.md](references/command-reference.md))

Complete reference for all 16 Two-Phase Mode commands.

| Section | Commands |
|---------|----------|
| 1. Plan Phase Commands (6) | /start-planning, /planning-status, /add-requirement, /modify-requirement, /remove-requirement, /approve-plan |
| 2. Orchestration Phase Commands (10) | /start-orchestration, /orchestration-status, /register-agent, /assign-module, /add-module, /modify-module, /remove-module, /prioritize-module, /reassign-module, /check-agents |

**When to use:** Quick reference for command syntax and parameters.

---

### Script Reference ([references/script-reference.md](references/script-reference.md))

Complete reference for all Two-Phase Mode Python scripts.

| Section | Scripts |
|---------|---------|
| 1. Plan Phase Scripts (4) | eoa_start_planning.py, eoa_planning_status.py, eoa_modify_requirement.py, eoa_approve_plan.py |
| 2. Orchestration Phase Scripts (14) | eoa_start_orchestration.py, eoa_orchestration_status.py, eoa_register_agent.py, eoa_assign_module.py, eoa_modify_module.py, eoa_reassign_module.py, eoa_check_remote_agents.py, eoa_notify_agent.py, eoa_check_plan_phase.py, eoa_check_orchestration_phase.py, eoa_sync_github_issues.py, eoa_verify_instructions.py, eoa_poll_agent.py, eoa_update_verification.py |
| 3. Design & GitHub Scripts (5) | eoa_init_design_folders.py, eoa_compile_handoff.py, eoa_design_search.py, eoa_sync_kanban.py, eoa_create_module_issues.py |
| 4. Modified Scripts (1) | eoa_orchestrator_stop_check.py (phase-aware) |

**When to use:** Understanding script functionality, debugging, learning parameters.

---

### Claude Tasks Scheduling Principle ([references/native-task-persistence.md](references/native-task-persistence.md))

**CRITICAL** principle for all orchestrator and subagent operations.

| Section | Topics |
|---------|--------|
| 1. Why This Principle Exists | Context compacting problem, how Claude Tasks solve it |
| 2. The Claude Tasks Scheduling Rule | When to create Claude Tasks, what to include |
| 3. Task Series Structure | Action tasks, verification, archive, commit, series closure |
| 4. Commit Message Format | [SERIES-COMPLETE] format, required sections |
| 5. Subagent Claude Tasks Requirements | Orchestrator/subagent responsibilities, Claude Tasks location |
| 6. Integration with Stop Hook | How stop hook checks Claude Tasks, block conditions |

**When to use:** When receiving ANY instruction, spawning subagents, completing task series, recovering after compacting.

**Prerequisite:** None (CRITICAL - read first)

---

### Issue Handling Workflow ([references/issue-handling-workflow.md](references/issue-handling-workflow.md))

Complete workflow for handling implementer-reported issues.

| Section | Topics |
|---------|--------|
| 1. When to Trigger | AI Maestro messages, progress polls, code review, test failures |
| 2. Issue Categories | BUG, BLOCKER, QUESTION, ENHANCEMENT, CONFIG, INVESTIGATION |
| 3. Creating Issue Tasks | /create-issue-tasks command, eoa_create_issue_tasks.py <!-- TODO: Script not implemented --> |
| 4. Standard Task Workflow | Assessment, triage, investigation, test creation, GitHub workflow, resolution |
| 5. Category-Specific Workflows | BUG, BLOCKER, QUESTION, ENHANCEMENT, CONFIG, INVESTIGATION workflows |
| 6. Integration with Stop Hook | Issue task file checking, open issue blocking |

**When to use:** When implementer reports issue, poll reveals problem, code review finds bug, tests fail.

**Prerequisite:** Claude Tasks Scheduling Principle

---

### Workflow Diagram ([references/workflow-diagram.md](references/workflow-diagram.md))

Visual representation of the complete Two-Phase Mode workflow.

| Section | Topics |
|---------|--------|
| 1. Visual Workflow Overview | Complete ASCII flowchart from user goal to exit |
| 2. Phase Transitions | Transition triggers and conditions table |
| 3. Module Processing Loop | Per-module flowchart with all protocols |

**When to use:** Understanding the overall flow, visualizing phase transitions, seeing module loop.

---

### Quick Reference Checklist ([references/quick-reference-checklist.md](references/quick-reference-checklist.md))

Actionable checklists for all phases and operations.

| Section | Topics |
|---------|--------|
| 1. Plan Phase Checklist | All steps from /start-planning to /approve-plan |
| 2. Orchestration Phase Checklist | All steps from /start-orchestration to exit |
| 3. Module Completion Checklist | Assignment, verification, polling, updates, completion |
| 4. Exit Verification Checklist | Plan Phase and Orchestration Phase exit criteria |

**When to use:** As a quick reference while working, ensuring all steps completed.

---

### Troubleshooting ([references/troubleshooting.md](references/troubleshooting.md))

Solutions for common issues in Two-Phase Mode.

| Section | Topics |
|---------|--------|
| 1. Plan Phase Issues | Won't transition, validation fails, duplicate issues |
| 2. Orchestration Phase Issues | Stop hook blocks, module stuck, verification loops |
| 3. State File Issues | Corruption, YAML parse error, sync issues |
| 4. Communication Issues | Agent not responding, messages not delivered, notifications |
| 5. Stop Hook Issues | Not firing, allows exit incorrectly, blocks incorrectly |

**When to use:** When encountering errors, debugging issues, resolving problems.

---

## Agent Types

| Agent Type | Location | Assignment Method | Communication |
|------------|----------|-------------------|---------------|
| **Local Subagents** | Same Claude Code | Spawned by orchestrator | Direct (Task tool) |
| **Remote AI Agents** | Independent sessions | User-provided agent IDs | AI Maestro messages |
| **Human Developers** | GitHub | GitHub Project Kanban | GitHub notifications |

**Important:** Only user-provided agent IDs should be involved, NOT all agents on AI Maestro network.

---

## Stop Hook Enforcement

The stop hook (`eoa_orchestrator_stop_check.py`) is **phase-aware** and enforces:

| Phase | Blocks Exit If |
|-------|---------------|
| Plan Phase | `plan_phase_complete: false` |
| Orchestration Phase | Any module not complete |
| Orchestration Phase | Verification loops remaining > 0 |

**Dynamic enforcement:** Stop hook always checks CURRENT state. If user adds/removes modules, the new state is what gets enforced.

---

## File Structure

```
two-phase-mode/
├── SKILL.md                                    (this file)
├── README.md                                   (skill overview)
└── references/
    ├── plan-phase-workflow.md                  (Plan Phase details)
    ├── orchestration-phase-workflow.md         (Orchestration Phase details)
    ├── instruction-verification-protocol.md    (8-step initial verification)
    ├── instruction-update-verification-protocol.md  (5-step mid-impl updates)
    ├── proactive-progress-polling.md           (6 mandatory questions)
    ├── design-folder-structure.md              (design/ folder organization)
    ├── state-file-formats.md                   (YAML schemas)
    ├── command-reference.md                    (all 16 commands)
    ├── script-reference.md                     (all 16+ scripts)
    ├── native-task-persistence.md              (CRITICAL - task persistence via Claude Tasks)
    ├── issue-handling-workflow.md              (issue categories and workflows)
    ├── workflow-diagram.md                     (visual flowcharts)
    ├── quick-reference-checklist.md            (actionable checklists)
    └── troubleshooting.md                      (common issues and solutions)
```

---

## Next Steps

1. Start with [Plan Phase Workflow](references/plan-phase-workflow.md) to enter planning mode
2. After plan approval, read [Orchestration Phase Workflow](references/orchestration-phase-workflow.md)
3. **MANDATORY**: Read [Instruction Verification Protocol](references/instruction-verification-protocol.md) before assigning modules
4. **MANDATORY**: Read [Proactive Progress Polling](references/proactive-progress-polling.md) for monitoring
5. **MANDATORY**: Read [Instruction Update Verification Protocol](references/instruction-update-verification-protocol.md) before sending mid-implementation updates
6. Reference [State File Formats](references/state-file-formats.md) for state structure
7. Use [Command Reference](references/command-reference.md) for quick command lookup
8. Use [Script Reference](references/script-reference.md) for script details
9. See [Workflow Diagram](references/workflow-diagram.md) for visual overview
10. Keep [Quick Reference Checklist](references/quick-reference-checklist.md) handy during operations
11. Consult [Troubleshooting](references/troubleshooting.md) when issues arise

---

## Examples

### Example 1: Complete Two-Phase Workflow

```bash
# PLAN PHASE
/start-planning
# Document requirements in USER_REQUIREMENTS.md
# Define architecture and modules
/approve-plan

# ORCHESTRATION PHASE
/start-orchestration --project-id PVT_kwDOB1234567
/register-agent ai implementer-1 --session helper-agent-generic
/assign-module auth-core implementer-1
# Execute Instruction Verification Protocol
# Poll every 10-15 minutes with /check-agents
# After 4 verification loops, approve PR
```

### Example 2: Dynamic Module Addition

```bash
# User requests new feature during orchestration
/add-module "OAuth2 Support" --criteria "Google and GitHub OAuth" --priority high

# Stop hook now blocks until OAuth2 is ALSO complete
# Assign to available agent
/assign-module oauth2-support implementer-2
```

---

## Error Handling

See [Troubleshooting](references/troubleshooting.md) for complete solutions.

| Issue | Cause | Resolution |
|-------|-------|------------|
| Plan Phase won't transition | Requirements incomplete | Complete all required fields |
| Stop hook blocks exit | Modules incomplete | Finish all pending modules |
| Agent not responding | Connection issue | Check AI Maestro health |
| State file corrupt | YAML syntax error | Restore from git or recreate |

---

## Checklist

Copy this checklist and track your progress:

### Plan Phase
- [ ] Run `/start-planning` command
- [ ] Document user requirements in USER_REQUIREMENTS.md
- [ ] Define architecture and design
- [ ] Break down into modules with acceptance criteria
- [ ] Review plan with user
- [ ] Run `/approve-plan` to transition
- [ ] Verify GitHub issues created

### Orchestration Phase
- [ ] Run `/start-orchestration` command
- [ ] Register all remote agents with `/register-agent`
- [ ] Assign modules to agents with `/assign-module`
- [ ] Execute Instruction Verification Protocol for each module
- [ ] Poll agents every 10-15 minutes with `/check-agents`
- [ ] Handle any instruction updates with Update Verification Protocol
- [ ] Complete 4 verification loops per module
- [ ] Verify all modules marked complete
- [ ] Confirm stop hook allows exit

### Claude Tasks Scheduling
- [ ] Create Claude Tasks immediately when receiving instructions
- [ ] Include verification task in each series
- [ ] Include archive task in each series
- [ ] Include commit task with [SERIES-COMPLETE] format
- [ ] Verify Claude Tasks persist across compacting

---

## Resources

- [Workflow Diagram](./references/workflow-diagram.md)
- [Plan Phase Workflow](./references/plan-phase-workflow.md)
- [Orchestration Phase Workflow](./references/orchestration-phase-workflow.md)
- [Instruction Verification Protocol](./references/instruction-verification-protocol.md)
- [Instruction Update Verification Protocol](./references/instruction-update-verification-protocol.md)
- [Proactive Progress Polling](./references/proactive-progress-polling.md)
- [Native Task Persistence](./references/native-task-persistence.md)
- [Issue Handling Workflow](./references/issue-handling-workflow.md)
- [Command Reference](./references/command-reference.md)
- [Script Reference](./references/script-reference.md)
- [State File Formats](./references/state-file-formats.md)
- [Design Folder Structure](./references/design-folder-structure.md)
- [Quick Reference Checklist](./references/quick-reference-checklist.md)
- [Troubleshooting](./references/troubleshooting.md)
