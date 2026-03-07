## Table of Contents
- Output Types and Locations
- Step-by-Step Instructions
- Agent Types
- Stop Hook Enforcement
- File Structure
- Examples

---

## Output Types and Locations

| Output Type | Location | Description |
|-------------|----------|-------------|
| Plan Phase State | `.claude/orchestrator-plan-phase.local.md` | YAML frontmatter with requirements, modules, criteria |
| Orchestration State | `.claude/orchestrator-orchestration-phase.local.md` | YAML frontmatter with agent assignments, module status |
| Design Documents | `design/<platform>/` | Templates, handoffs, RDD files, specs |
| GitHub Issues | GitHub repository | Module issues created from approved plan |
| Claude Tasks | Claude Code session | Persistent task tracking across compacting |

---

## Step-by-Step Instructions

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

The stop hook (`amoa_orchestrator_stop_check.py`) is **phase-aware** and enforces:

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
