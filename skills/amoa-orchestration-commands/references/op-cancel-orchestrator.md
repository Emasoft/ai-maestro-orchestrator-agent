---
procedure: support-skill
workflow-instruction: support
---

# Operation: Cancel Orchestrator Loop


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Verify Loop is Active](#step-1-verify-loop-is-active)
  - [Step 2: Consider Alternatives](#step-2-consider-alternatives)
  - [Step 3: Execute Cancellation](#step-3-execute-cancellation)
  - [Step 4: Understand What Happens](#step-4-understand-what-happens)
  - [Step 5: Verify Cancellation](#step-5-verify-cancellation)
  - [Step 6: Clean Up Manually (if needed)](#step-6-clean-up-manually-if-needed)
  - [Step 7: Document Cancellation](#step-7-document-cancellation)
  - [Step 8: Handle Incomplete Work](#step-8-handle-incomplete-work)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example](#example)
- [Recovery After Cancellation](#recovery-after-cancellation)
- [Checklist](#checklist)

## When to Use

Use this operation when you need to manually stop an active orchestrator loop.

## Prerequisites

- Orchestrator loop is active
- Understanding of why cancellation is needed
- Awareness that tasks may be incomplete

## Procedure

### Step 1: Verify Loop is Active

```bash
# Check current loop status
/orchestrator-status

# Should show: Status: ACTIVE
```

### Step 2: Consider Alternatives

Before cancelling, consider:

| Situation | Alternative |
|-----------|-------------|
| Task stuck | Send prompt to agent |
| Agent unresponsive | Replace agent via ECOS |
| Wrong configuration | Adjust config, let loop continue |
| Max iterations reached | Increase limit |
| Genuine need to stop | Proceed with cancellation |

### Step 3: Execute Cancellation

```bash
# Cancel the orchestrator loop
/cancel-orchestrator
```

### Step 4: Understand What Happens

The command:
1. Checks if loop state file exists (`design/state/loop.md`)
2. Reads current iteration number for logging
3. Removes the state file to stop the loop
4. Removes lock file if present
5. Reports cancellation with iteration count

### Step 5: Verify Cancellation

```bash
# Check loop status
/orchestrator-status

# Should show: Status: INACTIVE or "No loop active"

# Verify state file removed
test -f design/state/loop.md && echo "WARNING: State file still exists"

# Verify lock file removed
test -f .claude/orchestrator.lock && echo "WARNING: Lock file still exists"
```

### Step 6: Clean Up Manually (if needed)

```bash
# If state file persists
rm design/state/loop.md

# If lock file persists
rm .claude/orchestrator.lock
```

### Step 7: Document Cancellation

```bash
# Add note to orchestrator log
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) CANCELLED by user - reason: <reason>" >> orchestrator.log

# Add comment to relevant GitHub issues
gh issue comment <ISSUE_NUM> --body "Orchestrator loop cancelled. Tasks may be incomplete."
```

### Step 8: Handle Incomplete Work

After cancellation:
1. Check agent assignments: `/orchestration-status`
2. Notify agents of pause
3. Save any partial progress
4. Decide next steps (resume later, reassign, etc.)

## Output

| Field | Type | Description |
|-------|------|-------------|
| Cancellation Status | String | "Orchestrator loop cancelled at iteration X" |
| Iteration at Cancel | Number | Loop iteration when cancelled |
| State File | String | Removed or error |
| Lock File | String | Removed or error |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "No loop active" | Loop not running | Nothing to cancel |
| "State file not found" | Already cancelled or never started | Check orchestrator.log |
| "Cannot remove state" | Permission issue | Remove manually |
| "Lock file stale" | Previous crash | Remove manually |

## Example

```bash
# Complete cancellation sequence

# 1. Check current status
/orchestrator-status
# Output: ACTIVE, Iteration 45/100, Pending: 8

# 2. Decide to cancel (e.g., need to pivot priorities)
/cancel-orchestrator
# Output: Orchestrator loop cancelled at iteration 45

# 3. Verify
/orchestrator-status
# Output: No active orchestrator loop

# 4. Clean up if needed
rm -f design/state/loop.md
rm -f .claude/orchestrator.lock

# 5. Document
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) CANCELLED - priority change" >> orchestrator.log

# 6. Notify agents using the agent-messaging skill:
# Recipient: each active agent
# Subject: "Orchestration Paused"
# Content: "Please save your progress. Orchestration paused."
# Type: pause_notification, Priority: high
```

## Recovery After Cancellation

To resume work later:

```bash
# 1. Review what was in progress
cat orchestrator.log | tail -20

# 2. Check task status
/orchestration-status

# 3. Restart loop when ready
/orchestrator-loop "Continue from previous state"
```

## Checklist

- [ ] Verify loop is active
- [ ] Consider alternatives before cancelling
- [ ] Run `/cancel-orchestrator` command
- [ ] Verify loop status shows inactive
- [ ] Remove state file if persists
- [ ] Remove lock file if persists
- [ ] Document cancellation reason
- [ ] Notify affected agents
- [ ] Handle incomplete work
- [ ] Plan resumption (if applicable)
