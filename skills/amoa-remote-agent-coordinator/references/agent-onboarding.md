# Agent Onboarding

## Overview

This document guides new agents (AI or human developers) through the process of joining an EOA (Emasoft Orchestrator Agent) coordinated project. Proper onboarding ensures:

- **Alignment** - Agent understands project architecture and methodology
- **Toolchain Readiness** - Development environment configured correctly
- **Communication Setup** - AI Maestro messaging configured
- **Quality Gates** - Agent can execute and pass project tests
- **Roster Registration** - Orchestrator knows agent capabilities and availability

**Purpose**: Transform a new agent from "unknown entity" to "productive team member" in a systematic, verifiable way.

**Critical Principle**: No agent receives real tasks until onboarding is complete and verified.

---

## Contents

**When starting agent onboarding** → [Onboarding Checklist](#onboarding-checklist)

**When setting up your development environment** → [Environment Setup](#environment-setup)

**When verifying agent capability through a test task** → [Verification Task](#verification-task)

**When learning required project knowledge** → [Required Reading List](#required-reading-list)

**When joining the project agent roster** → [Roster Registration](#roster-registration)

**When encountering setup or environment problems** → [Common Setup Issues](#common-setup-issues)

**When onboarding is complete** → [Next Steps After Onboarding](#next-steps-after-onboarding)

---

## Onboarding Checklist

Follow these steps in order. Mark each complete before proceeding:

### Phase 1: Knowledge Acquisition

- [ ] **Read `design/config/toolchain.md`** - Understand project build/test/deploy tools
- [ ] **Read `design/specs/architecture.md`** - Understand system design and component boundaries
- [ ] **Read `IRON_RULES.md`** - Understand orchestration rules and FAIL-FAST principle
- [ ] **Read `PROJECT_METHODOLOGY.md`** - Understand selected methodology (TDD, branch strategy, etc.)
- [ ] **Read `CONTRIBUTING.md`** - Understand PR format, code style, commit conventions

### Phase 2: Environment Setup

- [ ] **Clone repository** - `git clone <repo-url>`
- [ ] **Install toolchain dependencies** - Follow `design/config/toolchain.md`
- [ ] **Configure git identity** - Set name and email
- [ ] **Setup AI Maestro client** - Configure session name and API endpoint
- [ ] **Create development branch** - `git checkout -b onboarding/<agent-id>`
- [ ] **Run verification script** - `./scripts/verify-environment.sh`

### Phase 3: Verification Task

- [ ] **Receive verification task** - Simple feature to implement
- [ ] **Write tests first** - Following TDD methodology
- [ ] **Implement feature** - According to task specification
- [ ] **Run tests locally** - All tests must pass
- [ ] **Create PR** - Following project PR template
- [ ] **Send completion report** - Via AI Maestro message using the `agent-messaging` skill

### Phase 4: Registration

- [ ] **Register in agent roster** - Notify orchestrator via message
- [ ] **Subscribe to change notifications** - Configure notification preferences
- [ ] **Mark available** - Set status to "active"

**Completion Criteria**: Orchestrator confirms onboarding via approval message

---

## Environment Setup

### Prerequisites

**Required Tools** (verify in `design/config/toolchain.md`):
- Git 2.40+
- Programming language runtime (Python 3.11+, Node.js 18+, etc.)
- Package manager (uv, pnpm, cargo, etc.)
- Test runner (pytest, jest, cargo test, etc.)

**Optional Tools**:
- Docker (if project uses containers)
- Database client (if project uses databases)
- Pre-commit hooks manager

### Step-by-Step Setup

#### 1. Clone Repository

```bash
# Clone with all history
git clone <repository-url>
cd <repository-name>

# Configure git identity
git config user.name "<YourName>"
git config user.email "<your@email.com>"
```

#### 2. Install Dependencies

**Python Example** (adjust for your project):

```bash
# Create virtual environment
uv venv --python 3.12

# Activate environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install dependencies
uv sync
```

**JavaScript Example**:

```bash
# Install dependencies
pnpm install

# Build project
pnpm build
```

#### 3. Verify Installation

Run the environment verification script:

```bash
./scripts/verify-environment.sh
```

**Expected Output**:

```
✓ Git version: 2.42.0
✓ Python version: 3.12.1
✓ uv version: 0.5.13
✓ Dependencies installed: 42 packages
✓ Test runner available: pytest 8.0.0
✓ Pre-commit hooks: configured
✓ Environment: READY
```

#### 4. Setup AI Maestro Client

**Configure Session Name** (in `~/.claude/settings.json` or equivalent):

```json
{
  "aimaestro": {
    "api_url": "managed by AI Maestro AMP (handles routing automatically)",
    "agent_session_name": "dev-<agent-id>-<project>",
    "poll_interval": 10
  }
}
```

**Test Messaging**:

Check your inbox using the `agent-messaging` skill. It should show no unread messages after a fresh onboarding.

**Verify**: confirm inbox is empty (no unread messages).

#### 5. Run Sample Build/Test

**Build Project**:

```bash
# Python
uv run pytest tests/ -v

# JavaScript
pnpm test

# Rust
cargo test
```

**Expected Result**: All existing tests pass

---

## Verification Task

### Task Description

The orchestrator assigns a small, self-contained feature to verify:

1. **You understand the architecture** - Task touches core components
2. **You can write tests** - TDD approach required
3. **You follow methodology** - Commit format, branch naming, PR template
4. **You communicate correctly** - Report back via AI Maestro

### Sample Verification Task

**Task**: Add a `validate_email()` utility function

**Specification**:
- Input: String (potential email address)
- Output: Boolean (valid or invalid)
- Validation rules:
  - Must contain exactly one `@` symbol
  - Must have at least one character before `@`
  - Must have at least one `.` after `@`
  - Must have at least two characters after last `.`

**Files to Create/Modify**:
- `src/utils/validators.py` - Add function
- `tests/test_validators.py` - Add tests

**Test Requirements**:
1. Test valid email: `user@example.com`
2. Test invalid: missing `@`
3. Test invalid: multiple `@`
4. Test invalid: missing `.` in domain
5. Test invalid: domain too short after `.`

**Completion Criteria**:
- [ ] All 5 tests written BEFORE implementation
- [ ] All tests pass locally
- [ ] Branch pushed to origin
- [ ] PR created with description
- [ ] Completion report sent via AI Maestro

### Report Format

When verification task is complete, send this message:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "orchestrator-master",
  "subject": "Onboarding Verification Complete",
  "priority": "normal",
  "content": {
    "type": "completion-report",
    "task_id": "ONBOARDING",
    "agent_id": "dev-<agent-id>",
    "status": "success",
    "pr_url": "<github-pr-url>",
    "test_results": "5/5 tests pass",
    "notes": "No issues encountered"
  }
}
```

---

## Required Reading List

### Priority 1: Critical (Read FIRST)

1. **`IRON_RULES.md`** - FAIL-FAST principle, no workarounds
2. **`design/config/toolchain.md`** - Build/test/deploy commands
3. **`design/specs/architecture.md`** - System design overview

### Priority 2: Essential (Read BEFORE first task)

4. **`PROJECT_METHODOLOGY.md`** - TDD, branching, PR process
5. **`CONTRIBUTING.md`** - Code style, commit format
6. **`references/task-instruction-format.md`** - How to interpret task instructions
7. **`references/messaging-protocol.md`** - How to communicate via AI Maestro

### Priority 3: Important (Read DURING onboarding)

8. **`design/specs/api-contracts.md`** - Interface specifications
9. **`references/escalation-procedures.md`** - When to ask for help
10. **`references/change-notification-protocol.md`** - How to notify about changes

### Optional: Reference

11. **`references/overnight-operation.md`** - Autonomous overnight work
12. **`references/artifact-sharing-protocol.md`** - Sharing build artifacts

**Completion Criteria**: Can explain purpose of each document when asked

---

## Roster Registration

### Registration Message

After completing verification task, send registration message:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "orchestrator-master",
  "subject": "Agent Registration Request",
  "priority": "normal",
  "content": {
    "type": "registration",
    "agent_id": "dev-agent-5",
    "session_name": "libs-utils-developer",
    "capabilities": ["python", "pytest", "git"],
    "availability": "active",
    "timezone": "UTC-8",
    "working_hours": "09:00-17:00 weekdays",
    "max_concurrent_tasks": 1,
    "preferred_task_types": ["feature", "bugfix"],
    "onboarding_completed": true,
    "verification_pr": "<pr-url>"
  }
}
```

### Capability Tags

Use these standard tags:

**Languages**: `python`, `javascript`, `typescript`, `rust`, `go`, `java`
**Frameworks**: `react`, `vue`, `django`, `flask`, `fastapi`, `express`
**Testing**: `pytest`, `jest`, `mocha`, `cargo-test`
**Tools**: `git`, `docker`, `kubernetes`, `terraform`
**Specialties**: `frontend`, `backend`, `fullstack`, `devops`, `testing`

### Orchestrator Response

Orchestrator will reply with:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "dev-agent-5",
  "subject": "Registration Approved",
  "priority": "normal",
  "content": {
    "type": "registration-confirmation",
    "agent_id": "dev-agent-5",
    "roster_position": 5,
    "assigned_label": "dev-agent-5",
    "can_receive_tasks": true,
    "welcome_message": "Registration approved. You can now receive task assignments."
  }
}
```

### Updating Roster Status

**Change Availability**:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "orchestrator-master",
  "subject": "Status Update",
  "priority": "normal",
  "content": {
    "type": "status-update",
    "agent_id": "dev-agent-5",
    "availability": "busy|active|offline",
    "current_task": "GH-42",
    "estimated_completion": "2025-12-31T18:00:00Z"
  }
}
```

**Go Offline**:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "orchestrator-master",
  "subject": "Going Offline",
  "priority": "normal",
  "content": {
    "type": "status-update",
    "agent_id": "dev-agent-5",
    "availability": "offline",
    "reason": "End of working day",
    "return_time": "2025-12-31T09:00:00Z"
  }
}
```

---

## Common Setup Issues

### Troubleshooting Table

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Dependencies fail to install** | `uv sync` fails with errors | Check Python version (must be 3.11+), Clear cache: `uv cache clean`, Retry: `uv sync --reinstall` |
| **Tests fail on fresh clone** | Existing tests fail locally | Verify environment with `./scripts/verify-environment.sh`, Check database is running (if needed), Check environment variables in `.env.example` |
| **AI Maestro connection fails** | CLI returns error | Verify AI Maestro server is running using the `agent-messaging` skill health check, Check firewall settings, Verify session name in config matches format |
| **Git identity not set** | `git commit` fails with identity error | Set name: `git config user.name "YourName"`, Set email: `git config user.email "your@email.com"` |
| **Pre-commit hooks fail** | `git commit` blocked by hooks | Install pre-commit: `pip install pre-commit`, Setup hooks: `pre-commit install`, Run manually: `pre-commit run --all-files` |
| **Cannot push to remote** | `git push` fails with permission error | Verify SSH key added to GitHub, Verify branch permissions, Create branch with correct prefix: `feature/`, `bugfix/` |
| **Verification task unclear** | Don't understand what to implement | Send clarification request via AI Maestro, Reference `task-instruction-format.md`, Ask specific questions in message |
| **Tests pass locally, fail on CI** | PR shows test failures | Check CI logs for environment differences, Verify all dependencies in `requirements.txt`, Check for absolute paths in tests |
| **Message format rejected** | AI Maestro returns error | Verify JSON syntax: `content` must be object, not string, Check required fields: `to`, `subject`, `priority`, `content`, Use standard `type` values from protocol |
| **No response from orchestrator** | Sent message but no reply | Check your inbox using the `agent-messaging` skill, Verify orchestrator session is active, Wait up to 15 minutes, resend if needed |

### Getting Help

**If stuck during onboarding**:

1. **Check documentation** - Re-read relevant section in Required Reading List
2. **Search existing issues** - Someone may have had same problem
3. **Send clarification message** - Ask orchestrator specific question
4. **Escalate if blocked >1 hour** - Send escalation message using the `agent-messaging` skill

**Clarification Message Format**:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "orchestrator-master",
  "subject": "Onboarding Question: <topic>",
  "priority": "normal",
  "content": {
    "type": "clarification",
    "task_id": "ONBOARDING",
    "question": "Specific question here",
    "attempted_solutions": ["What I tried", "What happened"],
    "blocking": true
  }
}
```

---

## Next Steps After Onboarding

Once registration is approved:

1. **Set status to "active"** - You can now receive real tasks
2. **Monitor AI Maestro inbox** - Check every 10 minutes
3. **Read first task assignment** - When received
4. **Follow task-instruction-format** - Execute according to template
5. **Report progress regularly** - Every 1-2 hours for complex tasks
6. **Report completion** - Send completion-report when done

**Welcome to the team!**
