## Table of Contents
- Complete Orchestration Start - Full startup workflow
- Orchestrator Loop Usage - Loop start, status, cancel
- Monitoring During Implementation - Agent checking workflow

---

## Example 1: Complete Orchestration Start

```bash
# Step 1: Start orchestration with GitHub Project sync
/start-orchestration --project-id PVT_kwDOB1234567

# Step 2: Register AI agent
/register-agent ai implementer-1 --session helper-agent-generic

# Step 3: Assign first module
/assign-module auth-core implementer-1

# Step 4: Monitor progress
/orchestration-status --verbose
```

## Example 2: Orchestrator Loop Usage

```bash
# Start continuous task-driven development
/orchestrator-loop "Complete all authentication tasks" --max-iterations 50

# Check status
/orchestrator-status --verbose

# If needed, cancel
/cancel-orchestrator
```

## Example 3: Monitoring During Implementation

```bash
# Check all agents every 10-15 minutes
/check-agents

# Or check specific agent
/check-agents --agent implementer-1

# View orchestration status
/orchestration-status --modules-only
```
