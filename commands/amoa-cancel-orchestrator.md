---
name: eoa-cancel-orchestrator
description: "Cancel active orchestrator loop"
allowed-tools: ["Bash(test -f .claude/orchestrator-loop.local.md:*)", "Bash(rm .claude/orchestrator-loop.local.md)", "Read(.claude/orchestrator-loop.local.md)"]
hide-from-slash-command-tool: "true"
---

# Cancel Orchestrator Loop

First check if an orchestrator loop is active:

```!
test -f .claude/orchestrator-loop.local.md && echo "FOUND_LOOP=true" || echo "FOUND_LOOP=false"
```

Check the output above:

1. **If FOUND_LOOP=false**:
   - Say "No active orchestrator loop found."

2. **If FOUND_LOOP=true**:
   - Read the state file to get current iteration: `.claude/orchestrator-loop.local.md`
   - Extract the iteration number from the `iteration:` line
   - Remove the state file: `rm .claude/orchestrator-loop.local.md`
   - Report: "Cancelled orchestrator loop (was at iteration N)" where N is the iteration value
