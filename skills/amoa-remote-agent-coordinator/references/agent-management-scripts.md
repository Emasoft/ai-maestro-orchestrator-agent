# Agent Management Scripts Reference

This document describes the Python automation scripts for agent management operations.

---

## Contents

- 1.0 Overview
- 2.0 Script 1: register_agent.py
  - 2.1 Purpose
  - 2.2 Usage
  - 2.3 Arguments
  - 2.4 Examples
- 3.0 Script 2: assign_module.py
  - 3.1 Purpose
  - 3.2 Usage
  - 3.3 Arguments
  - 3.4 Examples
- 4.0 Script 3: poll_agents.py
  - 4.1 Purpose
  - 4.2 Usage
  - 4.3 Arguments
  - 4.4 Examples
- 5.0 Script 4: generate_messages.py
  - 5.1 Purpose
  - 5.2 Usage
  - 5.3 Arguments
  - 5.4 Examples
- 6.0 Common Script Options
- 7.0 Script Dependencies
- 8.0 Integration with Commands

---

## 1.0 Overview

The agent management system includes Python automation scripts in the `scripts/` folder. These scripts provide programmatic access to agent management operations.

| Script | Purpose | Command Equivalent |
|--------|---------|-------------------|
| `register_agent.py` | Register agent programmatically | `/register-agent` |
| `assign_module.py` | Assign module with validation | `/assign-module` |
| `poll_agents.py` | Send poll messages to active agents | `/check-agents` |
| `generate_messages.py` | Generate message templates | N/A (utility) |

---

## 2.0 Script 1: register_agent.py

### 2.1 Purpose

Register a remote agent (AI or human) by updating state files and verifying prerequisites.

### 2.2 Usage

```bash
python scripts/register_agent.py <TYPE> <AGENT_ID> [OPTIONS]
```

### 2.3 Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `TYPE` | Yes | Agent type: `ai` or `human` |
| `AGENT_ID` | Yes | Unique identifier for the agent |
| `--session` | No | AI Maestro session name (AI agents only) |
| `--github-user` | No | GitHub username (human developers only) |
| `--capabilities` | No | Comma-separated list of capabilities |
| `--state-file` | No | Path to state file (default: `design/agents.yaml`) |

### 2.4 Examples

```bash
# Register AI agent
python scripts/register_agent.py ai implementer-1 \
  --session helper-agent-generic \
  --capabilities "python,testing"

# Register human developer
python scripts/register_agent.py human dev-alice \
  --github-user alice-dev \
  --capabilities "python,react,devops"

# Register with custom state file
python scripts/register_agent.py ai implementer-2 \
  --session helper-agent-python \
  --state-file custom/agents.yaml
```

**Output**:
```
✓ Agent 'implementer-1' registered successfully
  Type: ai
  Session: helper-agent-generic
  Status: available
```

---

## 3.0 Script 2: assign_module.py

### 3.1 Purpose

Assign a module to a registered agent with validation and message generation.

### 3.2 Usage

```bash
python scripts/assign_module.py <MODULE_ID> <AGENT_ID> [OPTIONS]
```

### 3.3 Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `MODULE_ID` | Yes | ID of the module to assign |
| `AGENT_ID` | Yes | ID of the registered agent |
| `--issue-url` | No | GitHub issue URL for this module |
| `--priority` | No | Priority level: `high`, `medium`, `low` |
| `--estimated-hours` | No | Estimated effort in hours |
| `--send-message` | No | Automatically send assignment message |
| `--state-file` | No | Path to state file |

### 3.4 Examples

```bash
# Basic assignment
python scripts/assign_module.py auth-core implementer-1

# Assignment with metadata
python scripts/assign_module.py auth-core implementer-1 \
  --issue-url "https://github.com/org/repo/issues/42" \
  --priority high \
  --estimated-hours 3

# Assignment with automatic message sending
python scripts/assign_module.py auth-core implementer-1 \
  --send-message \
  --issue-url "https://github.com/org/repo/issues/42"
```

**Output**:
```
✓ Module 'auth-core' assigned to 'implementer-1'
  Task UUID: task-a1b2c3d4
  Status: pending_verification
  GitHub Issue: #42

Next steps:
1. Execute Instruction Verification Protocol
2. Begin progress polling every 10-15 minutes

Assignment message:
[Message template displayed or sent]
```

---

## 4.0 Script 3: poll_agents.py

### 4.1 Purpose

Send progress poll messages to all active agents or a specific agent.

### 4.2 Usage

```bash
python scripts/poll_agents.py [OPTIONS]
```

### 4.3 Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--agent` | No | Poll only a specific agent |
| `--log-dir` | No | Directory for poll logs (default: `design/logs/polls/`) |
| `--questions` | No | Custom poll questions (JSON file path) |
| `--state-file` | No | Path to state file |

### 4.4 Examples

```bash
# Poll all active agents
python scripts/poll_agents.py

# Poll specific agent
python scripts/poll_agents.py --agent implementer-1

# Poll with custom log directory
python scripts/poll_agents.py --log-dir custom/logs/

# Poll with custom questions
python scripts/poll_agents.py --questions custom_poll.json
```

**Output**:
```
Polling active agents...

Agent: implementer-1 (auth-core)
  Poll sent: 2026-01-08T16:30:00+00:00
  Status: awaiting_response
  Log: design/logs/polls/poll_2026-01-08T163000_implementer-1.log

Agent: dev-alice (oauth-google)
  Poll sent: 2026-01-08T16:30:00+00:00
  GitHub comment: https://github.com/org/repo/issues/43#issuecomment-12345
  Log: design/logs/polls/poll_2026-01-08T163000_dev-alice.log

Polling complete. 2 agents polled.
```

---

## 5.0 Script 4: generate_messages.py

### 5.1 Purpose

Generate message templates for various agent communication scenarios.

### 5.2 Usage

```bash
python scripts/generate_messages.py <MESSAGE_TYPE> [OPTIONS]
```

### 5.3 Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `MESSAGE_TYPE` | Yes | Type: `assignment`, `poll`, `verification`, `completion` |
| `--agent` | No | Agent ID |
| `--module` | No | Module ID |
| `--task-uuid` | No | Task UUID |
| `--output` | No | Output file path |

### 5.4 Examples

```bash
# Generate assignment message
python scripts/generate_messages.py assignment \
  --agent implementer-1 \
  --module auth-core \
  --output message.md

# Generate poll message
python scripts/generate_messages.py poll \
  --agent implementer-1 \
  --task-uuid task-a1b2c3d4

# Generate verification request
python scripts/generate_messages.py verification \
  --agent implementer-1 \
  --module auth-core
```

**Output**:
```
Message generated successfully.
Type: assignment
Agent: implementer-1
Module: auth-core

Preview:
========================================
Subject: [TASK] Module: auth-core - UUID: task-a1b2c3d4

## Assignment
...
========================================

Saved to: message.md
```

---

## 6.0 Common Script Options

All scripts support these common options:

| Option | Description |
|--------|-------------|
| `--verbose` | Enable verbose output |
| `--dry-run` | Show what would be done without making changes |
| `--help` | Show help message |
| `--version` | Show script version |

**Examples**:

```bash
# Dry run to see what would happen
python scripts/assign_module.py auth-core implementer-1 --dry-run

# Verbose output for debugging
python scripts/poll_agents.py --verbose

# Show help
python scripts/register_agent.py --help
```

---

## 7.0 Script Dependencies

All scripts require:

- Python 3.8+
- PyYAML (`pip install pyyaml`)
- Requests (`pip install requests`)

Optional dependencies:

- GitHub CLI (`gh`) for GitHub operations
- AI Maestro running for message sending

**Installation**:

```bash
# Install dependencies
pip install -r requirements.txt

# Or using uv
uv pip install -r requirements.txt
```

---

## 8.0 Integration with Commands

The scripts implement the same logic as the CLI commands:

| Command | Script | Notes |
|---------|--------|-------|
| `/register-agent` | `register_agent.py` | Direct mapping |
| `/assign-module` | `assign_module.py` | Adds `--send-message` option |
| `/check-agents` | `poll_agents.py` | Adds logging and custom questions |

**When to use scripts vs commands**:

- **Use commands**: Interactive workflows, manual operations
- **Use scripts**: Automation, batch operations, CI/CD integration

**Example automation**:

```bash
#!/bin/bash
# Batch register multiple agents
for agent in implementer-{1..5}; do
  python scripts/register_agent.py ai "$agent" \
    --session "helper-agent-generic" \
    --capabilities "python,testing"
done
```

---

## Summary

The Python scripts provide:

1. **Programmatic access** to agent management operations
2. **Automation support** for batch operations
3. **Enhanced features** (dry-run, verbose, logging)
4. **Message generation** utilities

See script docstrings for detailed usage information:

```bash
python scripts/register_agent.py --help
python scripts/assign_module.py --help
python scripts/poll_agents.py --help
python scripts/generate_messages.py --help
```
