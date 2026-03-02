# Team Registry Specification

**Version**: 1.1.0
**Last Updated**: 2026-02-07

This document specifies the format and location of team registries, agent contacts, and naming conventions.

---

## Overview

Every project team maintains a **Team Registry** file that contains:
- Team identification
- Agent roster with contact details
- Role assignments
- Communication addresses

This file is **git-tracked** and stored in the repository, ensuring all team members have access.

---

## File Location

```
<repository-root>/
└── .ai-maestro/
    └── team-registry.json
```

**Why `.ai-maestro/`**: This directory contains all AI Maestro agent system configuration for the project.

---

## Team Naming Convention

### Format

```
<repo-name>-<project-type>-team
```

### Components

| Component | Description | Examples |
|-----------|-------------|----------|
| `repo-name` | GitHub repository name (lowercase, hyphens) | `svgbbox`, `ai-maestro`, `myapp` |
| `project-type` | Descriptive keyword for the project type | `library`, `webapp`, `api`, `cli`, `mobile` |
| `team` | Literal suffix to identify as team name | `team` |

### Examples

| Repository | Project Type | Team Name |
|------------|--------------|-----------|
| `svgbbox` | Library | `svgbbox-library-team` |
| `ai-maestro` | Backend API | `ai-maestro-api-team` |
| `my-mobile-app` | Mobile App | `my-mobile-app-mobile-team` |
| `company-website` | Web App | `company-website-webapp-team` |

### Uniqueness Requirement

Team names must be **globally unique** across all projects managed by AMCOS. AMCOS maintains a master list of all team names to prevent collisions.

---

## Team Registry Format (team-registry.json)

```json
{
  "$schema": "https://emasoft.github.io/schemas/team-registry.v1.json",
  "version": "1.0.0",
  "team": {
    "name": "svgbbox-library-team",
    "project": {
      "repository": "https://github.com/Emasoft/svgbbox",
      "github_project": "https://github.com/orgs/Emasoft/projects/12",
      "created_by": "amama-assistant-manager",
      "created_at": "2026-02-03T10:00:00Z"
    },
    "created_by": "amcos-chief-of-staff",
    "created_at": "2026-02-03T10:30:00Z"
  },
  "agents": [
    {
      "name": "svgbbox-orchestrator",
      "role": "orchestrator",
      "plugin": "ai-maestro-orchestrator-agent",
      "host": "macbook-dev-01",
      "ai_maestro_address": "svgbbox-orchestrator",
      "status": "active",
      "assigned_at": "2026-02-03T10:30:00Z"
    },
    {
      "name": "svgbbox-architect",
      "role": "architect",
      "plugin": "ai-maestro-architect-agent",
      "host": "macbook-dev-01",
      "ai_maestro_address": "svgbbox-architect",
      "status": "active",
      "assigned_at": "2026-02-03T10:30:00Z"
    },
    {
      "name": "svgbbox-impl-01",
      "role": "implementer",
      "plugin": "ai-maestro-implementer-agent",
      "host": "macbook-dev-01",
      "ai_maestro_address": "svgbbox-impl-01",
      "status": "active",
      "assigned_at": "2026-02-03T10:35:00Z"
    },
    {
      "name": "svgbbox-impl-02",
      "role": "implementer",
      "plugin": "ai-maestro-implementer-agent",
      "host": "macbook-dev-02",
      "ai_maestro_address": "svgbbox-impl-02",
      "status": "active",
      "assigned_at": "2026-02-03T10:35:00Z"
    },
    {
      "name": "svgbbox-tester-01",
      "role": "tester",
      "plugin": "ai-maestro-tester-agent",
      "host": "macbook-dev-01",
      "ai_maestro_address": "svgbbox-tester-01",
      "status": "active",
      "assigned_at": "2026-02-03T10:40:00Z"
    }
  ],
  "shared_agents": [
    {
      "name": "ai-maestro-integrator",
      "role": "integrator",
      "plugin": "ai-maestro-integrator-agent",
      "host": "server-ci-01",
      "ai_maestro_address": "ai-maestro-integrator",
      "note": "Shared across multiple teams"
    }
  ],
  "organization_agents": [
    {
      "name": "amama-assistant-manager",
      "role": "manager",
      "plugin": "ai-maestro-assistant-manager-agent",
      "host": "macbook-main",
      "ai_maestro_address": "amama-assistant-manager",
      "note": "Organization-wide, not team-specific"
    },
    {
      "name": "amcos-chief-of-staff",
      "role": "chief-of-staff",
      "plugin": "ai-maestro-chief-of-staff",
      "host": "macbook-main",
      "ai_maestro_address": "amcos-chief-of-staff",
      "note": "Organization-wide, not team-specific"
    }
  ],
  "github_bot": {
    "username": "ai-maestro-bot",
    "type": "shared-bot-account",
    "note": "All GitHub operations use this account. Real agent identity tracked in commit messages and PR bodies."
  },
  "contacts_last_updated": "2026-02-03T10:45:00Z",
  "contacts_updated_by": "amcos-chief-of-staff"
}
```

---

## Field Definitions

### Team Section

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique team name (format: `<repo>-<type>-team`) |
| `project.repository` | string | Yes | GitHub repository URL |
| `project.github_project` | string | No | GitHub Projects board URL |
| `project.created_by` | string | Yes | Agent that created the project |
| `project.created_at` | ISO8601 | Yes | Project creation timestamp |
| `created_by` | string | Yes | Agent that created the team (always AMCOS) |
| `created_at` | ISO8601 | Yes | Team creation timestamp |

### Agent Entry

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique agent name |
| `role` | string | Yes | Agent role (see Role Types below) |
| `plugin` | string | Yes | Plugin name the agent uses |
| `host` | string | Yes | Host machine identifier |
| `ai_maestro_address` | string | Yes | Address for AI Maestro messaging |
| `status` | string | Yes | `active`, `hibernated`, `offline`, `terminated` |
| `assigned_at` | ISO8601 | Yes | When agent was assigned to team |
| `note` | string | No | Optional notes |

### Role Types

| Role | Plugin | Count per Team | Description |
|------|--------|----------------|-------------|
| `manager` | ai-maestro-assistant-manager-agent | 0 (org-wide) | User interface, approvals |
| `chief-of-staff` | ai-maestro-chief-of-staff | 0 (org-wide) | Agent lifecycle |
| `orchestrator` | ai-maestro-orchestrator-agent | **Exactly 1** | Task management, kanban, agent replacement, remote coordination, messaging templates |
| `architect` | ai-maestro-architect-agent | **Exactly 1** | Design documents |
| `integrator` | ai-maestro-integrator-agent | 1+ (can be shared) | PR review, merge, CI/CD pipeline, release management, quality gates, kanban sync |
| `implementer` | ai-maestro-implementer-agent | 1+ | Code implementation |
| `tester` | ai-maestro-tester-agent | 0+ | Testing, QA |
| `devops` | ai-maestro-devops-agent | 0+ | CI/CD, deployment |

---

## Agent Naming Convention

### Format

```
<team-prefix>-<role>[-<instance>]
```

### Components

| Component | Description | Examples |
|-----------|-------------|----------|
| `team-prefix` | Short form of repo name | `svgbbox`, `maestro`, `myapp` |
| `role` | Agent role identifier | `orchestrator`, `architect`, `impl`, `tester` |
| `instance` | Instance number (for multiple same-role agents) | `01`, `02`, `03` |

### Examples

| Team | Role | Instance | Agent Name |
|------|------|----------|------------|
| svgbbox-library-team | orchestrator | - | `svgbbox-orchestrator` |
| svgbbox-library-team | architect | - | `svgbbox-architect` |
| svgbbox-library-team | implementer | 1 | `svgbbox-impl-01` |
| svgbbox-library-team | implementer | 2 | `svgbbox-impl-02` |
| ai-maestro-api-team | tester | 1 | `maestro-tester-01` |

### Organization-Wide Agents (No Team Prefix)

| Agent | Name |
|-------|------|
| Manager | `amama-assistant-manager` |
| Chief of Staff | `amcos-chief-of-staff` |
| Shared Integrator | `ai-maestro-integrator` |

---

## How to Send Messages

Every agent can look up contact information from `team-registry.json`:

```python
import json

def get_agent_address(agent_name: str, registry_path: str = ".ai-maestro/team-registry.json") -> str:
    """Get AI Maestro address for an agent."""
    with open(registry_path, encoding="utf-8") as f:
        registry = json.load(f)

    # Check team agents
    for agent in registry["agents"]:
        if agent["name"] == agent_name:
            return agent["ai_maestro_address"]

    # Check shared agents
    for agent in registry.get("shared_agents", []):
        if agent["name"] == agent_name:
            return agent["ai_maestro_address"]

    # Check organization agents
    for agent in registry.get("organization_agents", []):
        if agent["name"] == agent_name:
            return agent["ai_maestro_address"]

    raise ValueError(f"Agent not found: {agent_name}")

# Example: Look up orchestrator address
address = get_agent_address("svgbbox-orchestrator")
# Returns: "svgbbox-orchestrator"

# Then use the `agent-messaging` skill to send a message to this address.
```

---

## Message Format with Agent Identity

All AI Maestro messages must include full agent identity. Send using the `agent-messaging` skill:

- **Sender**: The sending agent's name (e.g., `svgbbox-impl-01`)
- **Recipient**: The target agent's name looked up from the team registry (e.g., `svgbbox-orchestrator`)
- **Subject**: "[PROGRESS] Task #42: Login fix 80% complete"
- **Priority**: `normal`
- **Content**: Include the following fields:
  - `type`: `progress-report`
  - `message`: "Login fix implementation 80% complete. Running tests now."
  - `sender_identity`: A nested structure containing:
    - `name`: The sending agent's name (e.g., `svgbbox-impl-01`)
    - `role`: The agent's role (e.g., `implementer`)
    - `plugin`: The plugin name (e.g., `ai-maestro-implementer-agent`)
    - `host`: The host machine identifier (e.g., `macbook-dev-01`)
    - `team`: The team name (e.g., `svgbbox-library-team`)
  - `task_reference`: A nested structure containing:
    - `issue_number`: The GitHub issue number (e.g., 42)
    - `issue_url`: Full URL to the GitHub issue

**Verify**: confirm message delivery via the `agent-messaging` skill's sent messages feature.

---

## Git Commit Message Format

To track which agent made each commit:

```
Fix login validation bug

- Added email format validation
- Fixed password length check
- Added unit tests

Agent: svgbbox-impl-01
Role: implementer
Plugin: ai-maestro-implementer-agent
Host: macbook-dev-01
Team: svgbbox-library-team
GitHub-Bot: ai-maestro-bot
```

---

## PR Body Format

```markdown
## Summary
Fix login validation bug

## Changes
- Added email format validation
- Fixed password length check
- Added unit tests

## Testing
- [x] Unit tests pass
- [x] Integration tests pass

---
**Agent Identity**
| Field | Value |
|-------|-------|
| Agent | svgbbox-impl-01 |
| Role | implementer |
| Plugin | ai-maestro-implementer-agent |
| Host | macbook-dev-01 |
| Team | svgbbox-library-team |

*PR created via ai-maestro-bot (shared GitHub account)*
```

---

## AMCOS Responsibilities for Team Registry

1. **Create team-registry.json** when creating a new team
2. **Add agents** to the registry when assigning to team
3. **Update status** when agents hibernate/wake/terminate
4. **Commit and push** registry changes to GitHub
5. **Notify all team agents** when registry changes

### Registry Update Message

When AMCOS updates the registry, it sends a notification to all team agents using the `agent-messaging` skill:

- **Sender**: `amcos-chief-of-staff`
- **Recipient**: Each team agent (sent individually to all agents in the registry)
- **Subject**: "[REGISTRY UPDATE] Team contacts updated"
- **Priority**: `normal`
- **Content**: Include the following fields:
  - `type`: `registry-update`
  - `message`: "Team registry has been updated. Please pull latest changes."
  - `changes`: List of changes made, each with:
    - `action`: One of `added`, `removed`, or `status_change`
    - `agent`: The affected agent name
    - `new_status`: New status value (only for `status_change` actions)
  - `registry_commit`: The git commit hash of the registry update

**Verify**: confirm message delivery via the `agent-messaging` skill's sent messages feature.

---

## Validation Rules

1. **Team name must be unique** across all projects
2. **Agent name must be unique** within the team
3. **Exactly one orchestrator** per team
4. **Exactly one architect** per team
5. **At least one implementer** per team
6. **All agents must have valid AI Maestro addresses**
7. **Organization agents cannot be assigned to teams**

---

## Kanban System Reference

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

For full kanban workflow details, task routing rules, and code format rules, see **FULL_PROJECT_WORKFLOW.md**.

---

## Quick Reference: Who to Message

| When I need to... | Message this agent | Address lookup |
|-------------------|--------------------|----------------|
| Report task progress | Orchestrator | `registry.agents[role=orchestrator]` |
| Ask design questions | Architect | `registry.agents[role=architect]` |
| Submit PR for review | Integrator | `registry.shared_agents[role=integrator]` |
| Request approval | Manager | `registry.organization_agents[role=manager]` |
| Report agent issues | Chief of Staff | `registry.organization_agents[role=chief-of-staff]` |
| Message teammate | By name | `registry.agents[name=<name>]` |

---

**This specification must be followed by all agents. Deviations require Manager approval.**
