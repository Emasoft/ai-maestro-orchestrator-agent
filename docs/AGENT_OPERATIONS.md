# AGENT_OPERATIONS.md - AMOA Orchestrator

> **Note**: This document is a local reference copy. Agent registration and capabilities should be verified against the AI Maestro agent registry API (`/api/sessions`) at runtime.

**Single Source of Truth for AI Maestro Orchestrator Agent (AMOA) Operations**

---

## 1. Session Naming Convention

### Format
```
amoa-<project>-<descriptive>
```

### Examples
- `amoa-svgbbox-orchestrator` - Orchestrator for svgbbox project
- `amoa-main-coordinator` - Main project coordinator
- `amoa-maestro-orchestrator` - AI Maestro system orchestrator

### Rules
- **Prefix**: All AMOA sessions MUST start with `amoa-`
- **Project**: Use kebab-case project identifier
- **Descriptive**: Role or scope (usually `orchestrator` or `coordinator`)
- **AI Maestro Identity**: Session name = registry identity for messaging
- **Chosen By**: AMCOS (Chief of Staff) when spawning the orchestrator

### Why This Matters
The session name is registered in AI Maestro's agent registry and becomes the messaging address for inter-agent communication. It must be unique and follow the `amoa-` prefix convention for role identification.

---

## 2. Plugin Paths

### Environment Variables

| Variable | Value | Usage |
|----------|-------|-------|
| `${CLAUDE_PLUGIN_ROOT}` | Points to `ai-maestro-orchestrator-agent/` | Use in scripts, hooks, skill references |
| `${CLAUDE_PROJECT_DIR}` | Points to `~/agents/<session-name>/` | Project root for the orchestrator instance |

### Local Plugin Path Structure
```
~/agents/<session-name>/.claude/plugins/ai-maestro-orchestrator-agent/
```

**Example**:
```
~/agents/amoa-svgbbox-orchestrator/.claude/plugins/ai-maestro-orchestrator-agent/
```

### How Plugin is Loaded
The AMOA instance is launched with `--plugin-dir` flag:
```bash
--plugin-dir ~/agents/$SESSION_NAME/.claude/plugins/ai-maestro-orchestrator-agent
```

This loads ONLY the ai-maestro-orchestrator-agent plugin into that Claude Code session.

---

## 3. Agent Directory Structure

### Complete Layout
```
~/agents/amoa-<project>-orchestrator/
├── .claude/
│   ├── plugins/
│   │   └── ai-maestro-orchestrator-agent/  ← Plugin loaded via --plugin-dir
│   │       ├── .claude-plugin/
│   │       │   └── plugin.json
│   │       ├── agents/
│   │       │   └── ai-maestro-orchestrator-agent-main-agent.md
│   │       ├── skills/
│   │       │   ├── amoa-orchestration-patterns/
│   │       │   ├── amoa-task-distribution/
│   │       │   └── ...
│   │       ├── hooks/
│   │       │   └── hooks.json
│   │       └── scripts/
│   └── settings.json  ← Session-specific settings
├── work/  ← Working directory for orchestrator tasks
└── logs/  ← Session logs
```

### Directory Purposes

| Directory | Purpose |
|-----------|---------|
| `.claude/plugins/` | Plugin installation location |
| `work/` | Temporary files, task breakdowns, kanban updates |
| `logs/` | Session activity logs, AI Maestro message logs |

---

## 4. How AMOA is Created

### AMCOS Spawns AMOA
AMCOS (Chief of Staff) spawns AMOA instances using the `ai-maestro-agents-management` skill to create a new agent session:

- **Session name**: `amoa-<project>-orchestrator`
- **Working directory**: `~/agents/<session-name>`
- **Task**: "Orchestrate tasks for <project>"
- **Plugin**: `ai-maestro-orchestrator-agent` (loaded via `--plugin-dir`)
- **Agent**: `ai-maestro-orchestrator-agent-main-agent`
- **Additional flags**: skip permissions for automation, enable Chrome DevTools MCP, add `/tmp` as working directory

**Verify**: confirm the agent session was created and is responsive.

### Pre-Spawn Setup
Before spawning, AMCOS must:
1. Copy the plugin to `~/agents/$SESSION_NAME/.claude/plugins/ai-maestro-orchestrator-agent/`
2. Register the session name in AI Maestro
3. Create initial task description
4. Set up working directories

---

## 5. Plugin Mutual Exclusivity

### Critical Rule: One Plugin Per Agent Instance

Each AMOA instance has **ONLY** the `ai-maestro-orchestrator-agent` plugin loaded.

**AMOA CANNOT access**:
- `ai-maestro-chief-of-staff-agent` (AMCOS) skills
- `ai-maestro-integrator-agent` (AMIA) skills
- `ai-maestro-architect-agent` (AMAA) skills
- `ai-maestro-assistant-manager-agent` (AMAMA) skills

### Why This Matters
Each plugin defines a **role boundary**. AMOA's job is to **orchestrate**, not to:
- Make architectural decisions (AMAA's job)
- Integrate and review code (AMIA's job)
- Coordinate multiple AMOA instances (AMCOS's job)
- Manage user communication (AMAMA's job)

### Cross-Role Communication
All cross-role communication happens via **AI Maestro messages**, not skill sharing.

**Example**:
```
AMOA needs architectural guidance
→ AMOA sends message to AMCOS
→ AMCOS delegates to AMAA
→ AMAA responds with architectural decision
→ AMCOS forwards to AMOA
→ AMOA distributes tasks based on architecture
```

---

## 6. Skill References

### How to Reference Skills in AMOA

**CORRECT** (reference by folder name):
```markdown
See skill: **amoa-orchestration-patterns**
See skill: **amoa-task-distribution**
See skill: **amoa-label-taxonomy**
```

**WRONG** (file paths):
```markdown
See ${CLAUDE_PLUGIN_ROOT}/skills/amoa-orchestration-patterns/SKILL.md  ← WRONG
See /path/to/skill/SKILL.md  ← WRONG
```

### Why Folder Names Only?
Claude Code's skill resolution system automatically finds skills by folder name within the loaded plugin. File paths can break if plugin location changes.

### Available AMOA Skills

| Skill Folder Name | Purpose |
|-------------------|---------|
| `amoa-agent-replacement` | Handling agent failures and replacement handoff |
| `amoa-checklist-compilation-patterns` | Compiling task checklists for implementers |
| `amoa-developer-communication` | Communicating with human developers |
| `amoa-github-action-integration` | CI/CD pipeline integration |
| `amoa-implementer-interview-protocol` | Pre-task and post-task agent interviews |
| `amoa-label-taxonomy` | GitHub label management and kanban column mapping |
| `amoa-messaging-templates` | AI Maestro message templates and protocols |
| `amoa-module-management` | Module lifecycle management |
| `amoa-orchestration-commands` | Core orchestration slash commands |
| `amoa-orchestration-patterns` | Task orchestration patterns and workflows |
| `amoa-progress-monitoring` | Monitoring implementer agent progress |
| `amoa-remote-agent-coordinator` | Coordinating remote AI agents |
| `amoa-task-distribution` | Distributing tasks to implementer agents |
| `amoa-two-phase-mode` | Two-phase planning and execution mode |
| `amoa-kanban-management` | GitHub Projects V2 kanban board management (create boards, add columns, move items) |
| `amoa-verification-patterns` | Code and deliverable verification patterns |

### NEVER Reference Other Plugins
```markdown
See skill: perfect-skill-suggester  ← WRONG (not loaded in AMOA)
See skill: amia-code-review  ← WRONG (AMIA plugin not loaded)
```

---

## 7. AI Maestro Communication

### Sending Messages from AMOA

#### To AMCOS (Chief of Staff)

Send a status message to AMCOS using the `agent-messaging` skill:
- **Recipient**: `amcos-chief-of-staff-one`
- **Subject**: "Task Status Update"
- **Content**: "Completed 3/5 tasks. Task #4 blocked on API dependency."
- **Type**: `status`
- **Priority**: `normal`

**Verify**: confirm message delivery.

#### To Implementer Agent

Send a task assignment message to an implementer using the `agent-messaging` skill:
- **Recipient**: `implementer-svgbbox-tests`
- **Subject**: "New Task Assignment"
- **Content**: "Implement unit tests for calculateBBox() function. See GitHub issue #42."
- **Type**: `task`
- **Priority**: `high`

**Verify**: confirm message delivery.

### Reading Messages (AMOA Inbox)

Check your inbox using the `agent-messaging` skill:
- **Check unread count**: query how many unread messages exist for your session
- **List unread messages**: retrieve all unread messages for your session
- **Mark as read**: mark a specific message as read by its message ID

**Verify**: confirm all unread messages have been processed.

### Message Priority Levels

| Priority | When to Use | Response Time |
|----------|-------------|---------------|
| `urgent` | Blocker, critical error, AMCOS directive | Immediate |
| `high` | Task assignment, deadline approaching | Within 5 minutes |
| `normal` | Status updates, progress reports | Within 15 minutes |
| `low` | FYI, non-actionable information | When convenient |

### Content Types

| Type | Purpose | Example |
|------|---------|---------|
| `task` | Task assignment | "Implement feature X" |
| `status` | Status update | "Completed 3/5 tasks" |
| `blocker` | Blocking issue | "API dependency missing" |
| `request` | Information request | "Need architectural guidance" |
| `report` | Detailed report | "Test results attached" |

---

## 8. AMOA Responsibilities

### Core Responsibilities

#### 1. Receive Tasks from AMCOS
- AMCOS sends task breakdown via AI Maestro message
- AMOA acknowledges receipt
- AMOA validates task structure and dependencies

#### 2. Distribute Tasks to Implementers
- Break down tasks into implementer-sized units
- Spawn implementer agents using the `ai-maestro-agents-management` skill
- Send task assignments via AI Maestro messages using the `agent-messaging` skill
- Ensure no conflicting tasks (e.g., two agents editing same file)

#### 3. Monitor Progress via Kanban
- Track task status using GitHub Projects labels
- Update kanban columns: `Todo`, `In Progress`, `AI Review`, `Human Review`, `Merge/Release`, `Done`, `Blocked`
- Identify stalled tasks
- Escalate blockers to AMCOS

#### 4. Report Status to AMCOS
- Send periodic status updates (every 30 minutes or on milestone)
- Report completed tasks
- Escalate blockers immediately
- Provide progress metrics (e.g., "3/5 tasks completed")

#### 5. Coordinate Implementers
- Prevent merge conflicts (assign non-overlapping files)
- Sequence dependent tasks
- Aggregate results from multiple implementers
- Trigger AMIA reviews when implementation complete

### What AMOA Does NOT Do

| AMOA Does NOT | Who Does It | Why |
|--------------|-------------|-----|
| Write production code | Implementer agents | AMOA orchestrates, doesn't implement |
| Review code for merge | AMIA | Code review is integrator's role |
| Make architectural decisions | AMAA | Architecture is architect's role |
| Coordinate multiple orchestrators | AMCOS | Chief of Staff coordinates orchestrators |
| Communicate with end users | AMAMA | Assistant Manager handles user comms |

### Workflow Pattern

```
AMCOS → [Task Breakdown] → AMOA
AMOA → [Subtask 1] → Implementer-A
AMOA → [Subtask 2] → Implementer-B
AMOA → [Subtask 3] → Implementer-C
    ↓ (monitor progress)
AMOA ← [Subtask 1 Done] ← Implementer-A
AMOA ← [Subtask 2 Done] ← Implementer-B
AMOA ← [Subtask 3 Blocked] ← Implementer-C
    ↓ (escalate blocker)
AMOA → [Blocker Report] → AMCOS
    ↓ (aggregate results)
AMOA → [Task Complete] → AMIA (for review)
```

---

## 9. Wake/Hibernate/Terminate

### Session Lifecycle Management

AMOA session lifecycle is managed by AMCOS using the `ai-maestro-agents-management` skill.

### Wake (Resume Session)

Use the `ai-maestro-agents-management` skill to wake the session `amoa-<project>-orchestrator`.

**When to wake**:
- New tasks assigned by AMCOS
- Implementer reports blocker
- Scheduled status check

**What happens**:
- Tmux session brought to foreground
- AMOA checks AI Maestro inbox
- AMOA resumes monitoring kanban

### Hibernate (Pause Session)

Use the `ai-maestro-agents-management` skill to hibernate the session `amoa-<project>-orchestrator`.

**When to hibernate**:
- All tasks distributed and in progress
- Waiting for implementer completions
- No active blockers

**What happens**:
- Tmux session detached (keeps running in background)
- AMOA continues monitoring via hooks
- AMOA can still receive AI Maestro messages

### Terminate (End Session)

Use the `ai-maestro-agents-management` skill to terminate the session `amoa-<project>-orchestrator`.

**When to terminate**:
- All tasks completed and reviewed
- Project milestone reached
- AMCOS issues termination directive

**What happens**:
- Tmux session killed
- AMOA sends final status report to AMCOS
- AI Maestro registry entry marked as terminated
- Working directory preserved at `~/agents/amoa-<project>-orchestrator/`

### Auto-Hibernate Feature

AMOA can auto-hibernate after distributing all tasks:

```bash
# In AMOA's configuration
AUTO_HIBERNATE_AFTER_DISTRIBUTION=true
AUTO_HIBERNATE_TIMEOUT=300  # 5 minutes of inactivity
```

This prevents AMOA from consuming resources while waiting for implementers.

---

## 10. Troubleshooting

### Common Issues

#### Issue: AMOA cannot access AMCOS skills
**Symptom**: `Skill 'amcos-strategic-planning' not found`
**Cause**: Plugin mutual exclusivity - AMOA doesn't have AMCOS plugin loaded
**Solution**: Use the `agent-messaging` skill to request AMCOS assistance

#### Issue: AI Maestro message not received
**Symptom**: Implementer didn't get task assignment
**Cause**: Wrong session name or API endpoint
**Solution**: Verify session name in registry, check AI Maestro connectivity using the `agent-messaging` skill

#### Issue: Kanban updates not reflected in GitHub
**Symptom**: Labels added but kanban column unchanged
**Cause**: GitHub Projects automation not configured
**Solution**: Check GitHub Projects automation rules, verify API token

#### Issue: Multiple implementers editing same file
**Symptom**: Merge conflicts
**Cause**: AMOA didn't check file ownership before assignment
**Solution**: Use `amoa-task-distribution` skill to prevent conflicts

#### Issue: AMOA session terminated unexpectedly
**Symptom**: Tmux session not found
**Cause**: System restart or manual kill
**Solution**: AMCOS recreates the session using the `ai-maestro-agents-management` skill

---

## Kanban Column System

All projects use the canonical **8-column kanban system** on GitHub Projects:

| Column | Code | Label |
|--------|------|-------|
| Backlog | `backlog` | `status:backlog` |
| Todo | `todo` | `status:todo` |
| In Progress | `in-progress` | `status:in-progress` |
| AI Review | `ai-review` | `status:ai-review` |
| Human Review | `human-review` | `status:human-review` |
| Merge/Release | `merge-release` | `status:merge-release` |
| Done | `done` | `status:done` |
| Blocked | `blocked` | `status:blocked` |

**Task routing**:
- Small tasks: In Progress → AI Review → Merge/Release → Done
- Big tasks: In Progress → AI Review → Human Review → Merge/Release → Done

---

## Wave 1-7 Skill Additions

The following skills were added to AMOA (2026-02-06 — 2026-02-07):

| Skill | Purpose |
|-------|---------|
| `amoa-agent-replacement` | Agent failure detection and replacement protocols |
| `amoa-remote-agent-coordinator` | Remote agent coordination and multi-host management |
| `amoa-messaging-templates` | Standardized AI Maestro message templates |
| `amoa-orchestration-patterns` | Task distribution, load balancing, dependency management |
| `amoa-module-management` | Module lifecycle and dependency tracking |

---

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `scripts/pre-push-hook.py` | Pre-push validation (manifest, hooks, lint, Unicode compliance) |
| `scripts/amoa_kanban_manager.py` | Kanban column management |
| `scripts/validate_plugin.py` | Plugin structure validation |
| `scripts/amoa_file_tracker.py` | File change tracking |
| `scripts/amoa_download.py` | Plugin download utility |
| `scripts/amoa_check_verification_status.py` | Verification status checking |
| `scripts/amoa_check_polling_due.py` | Polling schedule management |
| `scripts/amoa_stop_check/` | Stop condition evaluation (phase.py, tasks.py, utils.py) |

---

## Recent Changes (2026-03-06)

- Added `amoa-kanban-management` to Available AMOA Skills table
- Updated document version to 1.5.3 to match plugin.json

## Recent Changes (2026-02-07)

- Added 8-column canonical kanban system (unified from 5 conflicting systems)
- Added Wave 1-7 skills: agent-replacement, remote-coordinator, messaging-templates, orchestration-patterns, module-management
- Added Unicode compliance check (step 4) to pre-push hook
- Added `encoding="utf-8"` to all Python file operations
- Unified kanban column names to dash format (`in-progress`, `ai-review`, `merge-release`)
- Synchronized FULL_PROJECT_WORKFLOW.md, TEAM_REGISTRY_SPECIFICATION.md, ROLE_BOUNDARIES.md across all plugins

---

## 11. References

### Related Documentation

> **Cross-Plugin References**: Each AI Maestro agent plugin is installed independently. The following plugins have their own AGENT_OPERATIONS.md documenting their role-specific operations. Communication between plugins happens via the `agent-messaging` skill.

- **AMAA (Architect Agent)** - Architecture design, planning, and decision records. Plugin: `ai-maestro-architect-agent`
- **AMIA (Integrator Agent)** - Code review, quality gates, PR management. Plugin: `ai-maestro-integrator-agent`
- **AMCOS (Chief of Staff)** - Agent lifecycle management, coordination, and team registry. Plugin: `ai-maestro-chief-of-staff`
- **AMAMA (Assistant Manager)** - User communication and role routing. Plugin: `ai-maestro-assistant-manager-agent`

### External References
- [AI Maestro API Documentation](https://github.com/Emasoft/ai-maestro/blob/main/docs/API.md)
- [Claude Code Plugin System](https://docs.anthropic.com/claude/docs/plugins)
- [GitHub Projects API](https://docs.github.com/en/graphql/reference/objects#project)

---

**Document Version**: 1.5.3
**Last Updated**: 2026-03-08
**Maintained By**: claude-skills-factory
