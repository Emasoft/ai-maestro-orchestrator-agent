# Context Compilation Workflow Reference

## Contents

- [2.1 Information Sources](#21-information-sources)
- [2.2 State File Extraction](#22-state-file-extraction)
- [2.3 GitHub Issue Collection](#23-github-issue-collection)
- [2.4 Communication History Retrieval](#24-communication-history-retrieval)
- [2.5 Git Branch Analysis](#25-git-branch-analysis)

---

## 2.1 Information Sources

When compiling context for a failed agent, gather information from these sources:

### Primary Sources (MUST check)

| Source | Location | Information Type |
|--------|----------|------------------|
| Orchestrator State File | `$CLAUDE_PROJECT_DIR/design/state.yaml` | Assignments, task UUIDs, status |
| GitHub Issues | Repository issue tracker | Requirements, discussions, blockers |
| AI Maestro History | AI Maestro API | All messages to/from agent |
| Design Documents | `$CLAUDE_PROJECT_DIR/design/` | Requirements, specifications |

### Secondary Sources (SHOULD check)

| Source | Location | Information Type |
|--------|----------|------------------|
| Agent's Git Branch | Repository branches | Modified files, commits |
| PR Comments | Repository PRs | Review feedback, discussions |
| Handoff Documents | `$CLAUDE_PROJECT_DIR/docs_dev/handoffs/` | Previous handoffs |
| Agent Reports | `$CLAUDE_PROJECT_DIR/docs_dev/` | Progress reports, completion reports |

### Tertiary Sources (MAY check)

| Source | Location | Information Type |
|--------|----------|------------------|
| Log Files | `$CLAUDE_PROJECT_DIR/logs/` | Execution history |
| Test Results | CI/CD logs | Test pass/fail history |
| Build Artifacts | Build output directories | Partial compilation results |

---

## 2.2 State File Extraction

Extract all information about the failed agent from the orchestrator state file.

### State File Location

```bash
STATE_FILE="$CLAUDE_PROJECT_DIR/design/state.yaml"
```

### Information to Extract

```yaml
# Find all entries related to failed agent
active_assignments:
  - agent: "implementer-1"  # Match this
    agent_type: "ai"
    module: "auth-core"
    github_issue: "#42"
    task_uuid: "task-uuid-12345"
    status: "in-progress"
    started: "2026-01-31T10:00:00Z"
    last_poll: "2026-01-31T14:00:00Z"
    instruction_verification:
      status: "verified"
      verified_at: "2026-01-31T10:05:00Z"
    progress:
      percentage: 60
      last_update: "2026-01-31T14:00:00Z"
      notes: "Core auth logic complete, working on token refresh"

registered_agents:
  - id: "implementer-1"  # Match this
    type: "ai"
    session: "helper-agent-generic"
    registered: "2026-01-31T09:00:00Z"
    capabilities: ["python", "typescript"]
```

### Extraction Script

```bash
#!/bin/bash
# Extract failed agent info from state file

AGENT_ID="$1"
STATE_FILE="$CLAUDE_PROJECT_DIR/design/state.yaml"

# Extract assignments
yq ".active_assignments[] | select(.agent == \"$AGENT_ID\")" "$STATE_FILE" > assignments.yaml

# Extract agent registration
yq ".registered_agents[] | select(.id == \"$AGENT_ID\")" "$STATE_FILE" > agent_info.yaml

# Extract modules
yq ".modules[] | select(.assigned_to == \"$AGENT_ID\")" "$STATE_FILE" > modules.yaml
```

---

## 2.3 GitHub Issue Collection

Collect all GitHub issues assigned to or involving the failed agent.

### Find Assigned Issues

```bash
# Find issues assigned to failed agent
gh issue list --assignee "@failed-agent-github-username" --json number,title,state,body,labels,comments

# Find issues with agent mentioned
gh issue list --search "mentions:failed-agent-github-username" --json number,title,state,body,labels,comments
```

### Information to Extract per Issue

| Field | Purpose |
|-------|---------|
| `number` | Issue reference for handoff |
| `title` | Task description |
| `body` | Full requirements and context |
| `labels` | Status, priority, type |
| `comments` | Discussion history, clarifications |
| `state` | Open/closed |
| `milestone` | Deadline context |

### Extract Issue Comments

```bash
# Get all comments on an issue
gh api repos/{owner}/{repo}/issues/{issue_number}/comments | jq '.[].body'
```

### Look for Specific Patterns in Comments

- Progress updates: Look for "Progress:", "Status:", "Update:"
- Blockers: Look for "Blocked:", "Issue:", "Problem:"
- Questions: Look for "Question:", "Clarification needed:"
- Decisions: Look for "Decision:", "Approved:", "Agreed:"

---

## 2.4 Communication History Retrieval

Retrieve all AI Maestro messages to/from the failed agent.

### Query Messages

Use the `agent-messaging` skill to retrieve:
- All messages **sent to** the failed agent session
- All messages **received from** the failed agent session

This provides the full bidirectional communication history for context compilation.

### Important Message Types to Extract

| Type | Relevance |
|------|-----------|
| `assignment` | Task assignments with requirements |
| `clarification` | Answers to agent questions |
| `approval` | Decisions approved |
| `poll_response` | Progress updates |
| `blocker_report` | Known issues |
| `completion_report` | Partial completion status |

### Build Communication Timeline

```bash
# Combine and sort by timestamp
jq -s 'sort_by(.timestamp)' messages_to.json messages_from.json > communication_timeline.json
```

### Extract Key Decisions

Look for messages with:
- `priority: high` or `priority: urgent`
- Subjects containing "clarification", "decision", "approval"
- Content containing requirement changes

---

## 2.5 Git Branch Analysis

Analyze the failed agent's git branch for work in progress.

### Find Agent's Branch

```bash
# Convention: branches named by agent
git branch -a | grep "$AGENT_ID"

# Or check state file for branch name
yq ".active_assignments[] | select(.agent == \"$AGENT_ID\") | .branch" "$STATE_FILE"
```

### Analyze Branch Status

```bash
# Checkout agent's branch
git checkout "$AGENT_BRANCH"

# List modified files
git diff --name-only main..."$AGENT_BRANCH"

# Check for uncommitted changes
git status --porcelain

# Count commits ahead of main
git rev-list --count main..."$AGENT_BRANCH"

# Show commit history
git log --oneline main..."$AGENT_BRANCH"
```

### Extract Important Information

| Information | Command | Purpose |
|-------------|---------|---------|
| Modified files | `git diff --name-only main...branch` | What was worked on |
| Last commit message | `git log -1 --format=%B` | Last completed work |
| Uncommitted changes | `git diff HEAD` | Work in progress |
| Commit sequence | `git log --oneline` | TDD verification (RED/GREEN) |

### Check for TDD Commits

```bash
# Verify TDD pattern
git log --oneline | grep -E "^[a-f0-9]+ (RED|GREEN|REFACTOR):"
```

If TDD commits present, note which phase the agent was in:
- Last commit was `RED:` = Agent was writing tests
- Last commit was `GREEN:` = Agent was implementing
- Last commit was `REFACTOR:` = Agent was cleaning up

### Handle Uncommitted Work

If there are uncommitted changes:

1. **Document** what files are modified
2. **Create patch** for new agent: `git diff > uncommitted_work.patch`
3. **Include patch** in handoff document
4. **Instruct** new agent to review and apply if appropriate

---

## Compilation Output Format

Compile all gathered information into a structured format:

```yaml
context_compilation:
  agent_id: "implementer-1"
  compiled_at: "2026-01-31T14:35:00Z"

  state_file:
    assignments:
      - module: "auth-core"
        status: "in-progress"
        progress: 60
    verification_status: "verified"

  github:
    assigned_issues:
      - number: 42
        title: "Implement auth-core module"
        labels: ["in-progress", "priority:high"]
        key_comments: ["Decision: Use JWT tokens", "Blocker: Rate limiting"]

  communication:
    messages_count: 15
    key_clarifications:
      - "Use RS256 algorithm for JWT signing"
      - "Refresh tokens expire after 7 days"
    blockers_reported:
      - "Rate limiting on auth API - workaround implemented"

  git:
    branch: "feature/auth-core-implementer-1"
    commits_ahead: 5
    modified_files:
      - "src/auth/core.py"
      - "src/auth/tokens.py"
      - "tests/test_auth.py"
    uncommitted_changes: true
    last_commit: "GREEN: implement token refresh logic"
    tdd_phase: "green"
```

---

## Troubleshooting

### State File Missing

If state file is not found:
1. Check alternative locations: `design/`, `docs_dev/`, project root
2. Reconstruct from GitHub Issues if possible
3. Flag gap in handoff document

### AI Maestro History Unavailable

If AI Maestro messages cannot be retrieved:
1. Check AI Maestro service is running
2. Try alternative API endpoints
3. Check if messages were archived
4. Flag gap in handoff document

### Git Branch Not Found

If agent's branch doesn't exist:
1. Check if work was done on main/master
2. Check for branches with alternative naming
3. Ask ECOS if agent ever committed
4. Flag gap in handoff document

---

**Version**: 1.0.0
**Last Updated**: 2026-02-02
