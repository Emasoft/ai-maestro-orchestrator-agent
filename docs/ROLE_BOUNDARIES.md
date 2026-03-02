# AMCOS Role Boundaries

**CRITICAL: This document defines the strict boundaries between agent roles. Violating these boundaries breaks the system architecture.**

---

## Role Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                          USER                                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              AMAMA (Assistant Manager Agent)                      │
│              - User's sole interlocutor                          │
│              - Creates projects                                  │
│              - Approves AMCOS requests                            │
│              - Supervises all operations                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│      AMCOS       │ │      AMOA        │ │      AMIA        │
│ Chief of Staff  │ │  Orchestrator   │ │   Integrator    │
│                 │ │                 │ │                 │
│ PROJECT-        │ │ PROJECT-        │ │ PROJECT-        │
│ INDEPENDENT     │ │ LINKED          │ │ LINKED          │
│ (one per org)   │ │ (one per proj)  │ │ (one per proj)  │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

---

## AMCOS (Chief of Staff) - Responsibilities

### AMCOS CAN:
- ✅ Create agents (with AMAMA approval)
- ✅ Terminate agents (with AMAMA approval)
- ✅ Hibernate/wake agents (with AMAMA approval)
- ✅ Configure agents with skills and plugins
- ✅ Assign agents to project teams
- ✅ Handle handoff protocols between agents
- ✅ Monitor agent health and availability
- ✅ Replace failed agents (with AMAMA approval)
- ✅ Report agent performance to AMAMA

### AMCOS CANNOT:
- ❌ Create projects (AMAMA only)
- ❌ Assign tasks to agents (AMOA only)
- ❌ Manage GitHub Project kanban (AMOA only)
- ❌ Make architectural decisions (AMAA only)
- ❌ Perform code review (AMIA only)
- ❌ Communicate directly with user (AMAMA only)

### AMCOS Scope:
- **Project-independent**: One AMCOS manages agents across ALL projects
- **Team-agnostic**: Creates teams but doesn't manage their work
- **Infrastructure-focused**: Ensures agents exist and are configured

---

## AMOA (Orchestrator) - Responsibilities

### AMOA CAN:
- ✅ Assign tasks to agents
- ✅ Manage GitHub Project kanban for their project
- ✅ Track task progress
- ✅ Reassign tasks between agents
- ✅ Generate handoff documents
- ✅ Coordinate agent work within their project
- ✅ Request AMCOS to create/replace agents for their project

### AMOA CANNOT:
- ❌ Create agents directly (request via AMCOS)
- ❌ Configure agent skills/plugins (AMCOS only)
- ❌ Create projects (AMAMA only)
- ❌ Manage agents outside their project

### AMOA Scope:
- **Project-linked**: One AMOA per project
- **Task-focused**: Manages what agents DO, not what agents EXIST
- **Kanban owner**: Owns the GitHub Project board for their project

---

## AMAMA (Manager) - Responsibilities

### AMAMA CAN:
- ✅ Create projects
- ✅ Approve/reject AMCOS requests (agent create/terminate/etc.)
- ✅ Communicate with user
- ✅ Set strategic direction
- ✅ Override any agent decision
- ✅ Grant autonomous operation directives

### AMAMA CANNOT:
- ❌ Create agents directly (delegates to AMCOS)
- ❌ Assign tasks directly (delegates to AMOA)

### AMAMA Scope:
- **Organization-wide**: Oversees all projects and agents
- **User-facing**: Only agent that talks to user
- **Decision authority**: Final approval on all significant operations

---

## Interaction Patterns

### Creating an Agent for a Project

```
AMOA: "I need a frontend developer agent for Project X"
  │
  ▼
AMCOS: Receives request, prepares agent specification
  │
  ▼
AMCOS → AMAMA: "Request approval to spawn frontend-dev for Project X"
  │
  ▼
AMAMA: Approves (or rejects with reason)
  │
  ▼
AMCOS: Creates agent, configures skills, assigns to Project X team
  │
  ▼
AMCOS → AMOA: "Agent frontend-dev ready, assigned to your project"
  │
  ▼
AMOA: Assigns tasks from kanban to new agent
```

### Task Assignment

```
User/AMAMA: Creates GitHub issue in Project X
  │
  ▼
AMOA (Project X): Detects new issue, decides assignment
  │
  ▼
AMOA: Updates GitHub Project custom field "Assigned Agent"
AMOA: Sends AI Maestro notification to assigned agent
  │
  ▼
Agent: Receives task, begins work
```

### Agent Replacement

```
AMCOS: Detects agent-123 is unresponsive (terminal failure)
  │
  ▼
AMCOS → AMAMA: "Request approval to replace agent-123"
  │
  ▼
AMAMA: Approves
  │
  ▼
AMCOS: Creates replacement agent-456, configures it
  │
  ▼
AMCOS → AMOA: "agent-123 replaced by agent-456, generate handoff"
  │
  ▼
AMOA: Generates handoff document with task context
AMOA: Reassigns kanban tasks from agent-123 to agent-456
AMOA: Sends handoff to agent-456
```

---

## Summary Table

| Responsibility | AMAMA | AMCOS | AMOA | AMIA | AMAA |
|----------------|------|------|-----|-----|-----|
| Create projects | ✅ | ❌ | ❌ | ❌ | ❌ |
| Create agents | Approves | ✅ | Requests | ❌ | ❌ |
| Configure agents | ❌ | ✅ | ❌ | ❌ | ❌ |
| Assign agents to teams | ❌ | ✅ | ❌ | ❌ | ❌ |
| Assign tasks | ❌ | ❌ | ✅ | ❌ | ❌ |
| Manage kanban | ❌ | ❌ | ✅ | ❌ | ❌ |
| Code review | ❌ | ❌ | ❌ | ✅ | ❌ |
| Architecture | ❌ | ❌ | ❌ | ❌ | ✅ |
| Talk to user | ✅ | ❌ | ❌ | ❌ | ❌ |

---

**Document Version**: 1.0.0
**Last Updated**: 2026-02-02
**Author**: AMCOS Plugin Development
