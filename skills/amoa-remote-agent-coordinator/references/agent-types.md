# Agent Types Reference

This document describes the two types of agents that can be registered for module assignment: AI agents and human developers.

---

## Contents

- 4.1 AI Agents
  - 4.1.1 What are AI agents
  - 4.1.2 Communication via AI Maestro
  - 4.1.3 Session requirements
  - 4.1.4 Capabilities and limitations
  - 4.1.5 Best practices for AI agents
- 4.2 Human Developers
  - 4.2.1 Communication via GitHub
  - 4.2.2 Assignment via GitHub Projects
  - 4.2.3 Progress tracking via PRs/Issues
  - 4.2.4 Best practices for human developers
- 4.3 Comparing Agent Types
- 4.4 Choosing the Right Agent Type

---

## 4.1 AI Agents

### 4.1.1 What Are AI Agents

AI agents are independent Claude Code sessions running in separate terminal windows or tmux sessions. Each AI agent:

- Runs as a separate Claude Code instance
- Has its own context window and conversation
- Can execute code, run tests, create files
- Communicates via AI Maestro messaging system

**Key characteristic**: AI agents are autonomous but require explicit instructions and verification.

### 4.1.2 Communication via AI Maestro

AI Maestro is the inter-agent messaging system. Communication flow:

```
Orchestrator                    AI Agent
    |                               |
    |-- [Assignment Message] ------>|
    |                               |
    |<-- [Understanding Summary] ---|
    |                               |
    |-- [Authorization] ----------->|
    |                               |
    |-- [Progress Poll] ----------->|
    |                               |
    |<-- [Status Update] -----------|
    |                               |
```

**Message format**: Send a task assignment message using the `agent-messaging` skill:
- **Recipient**: the agent session name
- **Subject**: "[TASK] Module: auth-core"
- **Type**: `assignment`
- **Priority**: `high`

**Verify**: confirm message delivery.

### 4.1.3 Session Requirements

To use an AI agent:

1. **Session must be running**: The Claude Code session must be active
2. **AI Maestro hook installed**: The session must have AI Maestro hooks configured
3. **Session name known**: Must use the full session name (e.g., `helper-agent-generic`)

**Verify session is active**: Use the `agent-messaging` skill to query the agent registry and list all registered session names.

### 4.1.4 Capabilities and Limitations

**Capabilities**:
| Capability | Description |
|------------|-------------|
| Code execution | Can write, run, test code |
| File operations | Can create, edit, delete files |
| Git operations | Can commit, branch, push |
| Tool usage | Has access to configured tools |
| Research | Can search web, read docs |

**Limitations**:
| Limitation | Description |
|------------|-------------|
| Context window | Limited memory, may forget earlier context |
| No persistence | Session ends when closed |
| No visual | Cannot see screenshots, diagrams |
| Single task | Best with one focused task at a time |
| Verification needed | May misunderstand without explicit verification |

### 4.1.5 Best Practices for AI Agents

1. **Clear, detailed instructions**: Provide complete requirements
2. **Always verify understanding**: Use Instruction Verification Protocol
3. **One task at a time**: Don't overload with multiple assignments
4. **Frequent polling**: Check every 10-15 minutes
5. **Respond quickly to issues**: AI agents can get stuck without help
6. **Include all context**: Don't assume they remember previous conversations

---

## 4.2 Human Developers

### 4.2.1 Communication via GitHub

Human developers receive assignments and communicate through GitHub:

| Channel | Purpose |
|---------|---------|
| Issue assignment | Notify of new task |
| Issue comments | Discuss requirements, ask questions |
| Pull requests | Submit work for review |
| PR reviews | Receive feedback |
| @mentions | Get attention for urgent items |

**Communication flow**:
```
Orchestrator                    Human Developer
    |                               |
    |-- [GitHub Issue Assign] ----->|
    |                               |
    |<-- [Issue Comment] -----------|
    |                               |
    |-- [Reply Comment] ----------->|
    |                               |
    |<-- [Pull Request] ------------|
    |                               |
    |-- [PR Review] --------------->|
    |                               |
```

### 4.2.2 Assignment via GitHub Projects

If using GitHub Projects for project management:

1. **Create issue** for the module
2. **Assign issue** to the developer
3. **Move card** to "In Progress" column
4. **Add labels** (priority, type, module)

**GitHub Project integration**:
```bash
# Assign issue to developer
gh issue edit <ISSUE_NUMBER> --add-assignee <GITHUB_USERNAME>

# Add labels
gh issue edit <ISSUE_NUMBER> --add-label "in-progress,priority:high"
```

### 4.2.3 Progress Tracking via PRs/Issues

Track human developer progress through:

| Artifact | Tracking Method |
|----------|-----------------|
| Progress | Issue comments, Project card status |
| Work | Pull request commits |
| Questions | Issue comments, PR comments |
| Completion | PR merged, Issue closed |
| Blockers | Issue comments with "blocked" label |

**Progress poll for humans** (GitHub comment):
```markdown
## Progress Check

Hi @dev-alice, checking in on the auth-core module (#42).

- How's progress going?
- Any blockers or questions?
- ETA for first PR?

Thanks!
```

### 4.2.4 Best Practices for Human Developers

1. **Clear requirements in issue**: Include all specs in the GitHub issue
2. **Link to relevant docs**: Provide documentation links
3. **Set expectations**: Clear deadline and scope
4. **Be responsive**: Answer questions quickly
5. **Use async wisely**: Don't expect instant responses
6. **Track via GitHub**: Use labels, projects, milestones

---

## 4.3 Comparing Agent Types

| Aspect | AI Agents | Human Developers |
|--------|-----------|------------------|
| **Availability** | Instant (if session running) | Business hours, async |
| **Response time** | Seconds to minutes | Minutes to hours |
| **Verification** | Always required | Usually quicker |
| **Communication** | AI Maestro | GitHub |
| **Progress tracking** | Direct polling | Issue/PR activity |
| **Complexity handling** | Better with clear, scoped tasks | Better with ambiguous, creative tasks |
| **Supervision needed** | High (frequent polling) | Medium (daily check-ins) |
| **Cost** | API usage | Salary/contract |
| **Parallel work** | Can run many in parallel | Limited by team size |

---

## 4.4 Choosing the Right Agent Type

### Use AI Agents When:

- Task is well-defined with clear acceptance criteria
- Fast turnaround needed
- Task is repetitive or follows patterns
- Need parallel implementation of similar modules
- Continuous availability required

### Use Human Developers When:

- Task requires creative problem-solving
- Requirements are ambiguous or evolving
- Deep domain expertise needed
- Task involves user experience decisions
- Long-term project ownership required
- Complex debugging or architecture decisions

### Hybrid Approach

Often the best approach combines both:

```
Module: auth-core
├── JWT token generation (AI agent - well-defined)
├── OAuth integration (Human - needs expertise)
├── Unit tests (AI agent - repetitive)
└── Security review (Human - requires judgment)
```

Assign sub-components to the most suitable agent type.
