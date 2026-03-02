# Start Orchestration Procedure

## Contents

- 1.1 When to start orchestration phase
- 1.2 Prerequisites verification checklist
- 1.3 Command syntax and options
- 1.4 Post-start agent registration workflow
- 1.5 GitHub Project integration setup

---

## 1.1 When to Start Orchestration Phase

Start the orchestration phase when:

1. **Plan Phase is complete**: All requirements have been documented in `USER_REQUIREMENTS.md` and the plan has been approved via `/approve-plan`.

2. **Modules are defined**: The approved plan contains a list of implementation modules with acceptance criteria.

3. **You have agents ready**: Either remote AI agents (via AI Maestro), local subagents, or human developers who will implement the modules.

4. **GitHub Project exists (optional)**: If you want Kanban synchronization, have the GitHub Project ID ready.

**Do NOT start orchestration phase when**:
- Plan Phase is still in progress
- Requirements are incomplete or unapproved
- No clear module breakdown exists

---

## 1.2 Prerequisites Verification Checklist

Before running `/start-orchestration`, verify:

**Plan Phase Files**:
```bash
# Check plan state file exists
test -f design/state/plan-phase.md && echo "Plan state exists" || echo "MISSING: Plan state"

# Check plan is approved
grep -q "plan_phase_complete: true" design/state/plan-phase.md && echo "Plan approved" || echo "Plan NOT approved"
```

**Execution State File**:
```bash
# Check execution state file exists (created by /approve-plan)
test -f design/state/exec-phase.md && echo "Exec state exists" || echo "MISSING: Exec state"
```

**Requirements Documentation**:
```bash
# Check USER_REQUIREMENTS.md exists
test -f USER_REQUIREMENTS.md && echo "Requirements doc exists" || echo "MISSING: USER_REQUIREMENTS.md"
```

If any check fails, complete Plan Phase first before starting orchestration.

---

## 1.3 Command Syntax and Options

### Basic Usage

```bash
/start-orchestration
```

This activates orchestration phase with default settings.

### With GitHub Project Sync

```bash
/start-orchestration --project-id PVT_kwDOBxxxxxx
```

**Option details**:

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--project-id` | String | No | GitHub Project ID for Kanban synchronization |

### Finding Your GitHub Project ID

To get your GitHub Project ID:

```bash
# List your GitHub Projects
gh project list

# Get project details including ID
gh project view <PROJECT_NUMBER> --format json
```

The Project ID looks like: `PVT_kwDOBxxxxxx`

---

## 1.4 Post-Start Agent Registration Workflow

After starting orchestration, follow this workflow:

### Step 1: Register AI Agents

For each remote AI agent that will help implement modules:

```bash
/register-agent ai <agent_id> --session <session_name>
```

**Example**:
```
/register-agent ai implementer-1 --session helper-agent-generic
/register-agent ai implementer-2 --session helper-agent-python
```

### Step 2: Register Human Developers (Optional)

For GitHub-based human contributors:

```bash
/register-agent human <agent_id> --github <username>
```

**Example**:
```
/register-agent human dev-alice --github alicedev
```

### Step 3: Assign Modules to Agents

Assign specific modules to registered agents:

```bash
/assign-module <module_id> <agent_id>
```

**Example**:
```
/assign-module auth-core implementer-1
/assign-module oauth-google implementer-2
```

### Step 4: Instruction Verification Protocol

**MANDATORY**: Before each agent starts work, execute the Instruction Verification Protocol:

1. Send detailed instructions to the agent via AI Maestro
2. Ask the agent to repeat back requirements in their own words
3. Verify understanding is correct
4. Authorize the agent to begin only after successful verification

This prevents misunderstandings that waste implementation time.

### Step 5: Begin Progress Polling

Set up regular polling every 10-15 minutes:

```bash
/check-agents
```

Use these MANDATORY questions in every poll:
- "What have you completed since last update?"
- "Are you blocked on anything?"
- "What is your estimated completion time?"

---

## 1.5 GitHub Project Integration Setup

### Overview

GitHub Project integration synchronizes module status with a Kanban board, enabling:
- Visual progress tracking
- Team collaboration
- Automatic status updates
- Issue linking

### Setup Steps

**Step 1**: Create or identify your GitHub Project

```bash
# Create new project
gh project create --title "My Implementation" --format json

# Or use existing project
gh project list
```

**Step 2**: Get the Project ID

```bash
gh project view <PROJECT_NUMBER> --format json | jq '.id'
```

**Step 3**: Start orchestration with project ID

```bash
/start-orchestration --project-id PVT_kwDOBxxxxxx
```

**Step 4**: Verify sync is enabled

```bash
/orchestration-status
```

Look for "GitHub Project:" in the output showing your project ID.

### What Gets Synced

When GitHub Project sync is enabled:

| Event | Action |
|-------|--------|
| Module created | Issue created in GitHub |
| Module assigned | Issue assigned to developer |
| Module in progress | Issue moved to "In Progress" column |
| Module complete | Issue moved to "Done" column |
| Module blocked | Issue labeled with "blocked" |

### Troubleshooting Sync Issues

If sync appears broken:

1. Verify `gh auth status` shows authenticated
2. Check Project ID is correct format (starts with `PVT_`)
3. Verify you have write access to the project
4. Check `design/logs/hook.log` for errors

---

## Script Implementation

The `/start-orchestration` command executes:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_start_orchestration.py" $ARGUMENTS
```

**Script behavior**:

1. Parses command-line arguments
2. Checks Plan Phase state file exists and is approved
3. Checks Execution Phase state file exists
4. Updates execution state to "executing"
5. Sets timestamp for `started_at`
6. If `--project-id` provided, enables GitHub sync
7. Displays success message with next steps

**Exit codes**:
- 0: Success (phase activated or already active)
- 1: Error (prerequisites not met)
