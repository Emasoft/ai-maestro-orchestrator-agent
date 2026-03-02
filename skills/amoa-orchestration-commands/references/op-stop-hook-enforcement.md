---
procedure: support-skill
workflow-instruction: support
---

# Operation: Stop Hook Enforcement


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [How the Stop Hook Works](#how-the-stop-hook-works)
  - [Step 1: Hook Trigger Points](#step-1-hook-trigger-points)
  - [Step 2: Hook Script Execution](#step-2-hook-script-execution)
  - [Step 3: Blocking Conditions](#step-3-blocking-conditions)
  - [Step 4: Verification Mode](#step-4-verification-mode)
  - [Step 5: Hook Output Format](#step-5-hook-output-format)
  - [Step 6: Completion Signals](#step-6-completion-signals)
  - [Step 7: Fail-Safe Behavior](#step-7-fail-safe-behavior)
  - [Step 8: Debugging Stop Hook](#step-8-debugging-stop-hook)
- [Output](#output)
- [Error Handling](#error-handling)
- [Overriding the Hook](#overriding-the-hook)
- [Example](#example)
- [Checklist](#checklist)

## When to Use

Understand this operation to know how the orchestrator stop hook prevents premature exit and ensures task completion.

## Prerequisites

- Orchestrator loop active
- Understanding of hook mechanism
- Knowledge of completion requirements

## How the Stop Hook Works

### Step 1: Hook Trigger Points

The stop hook fires when:
1. Claude attempts to stop/complete the conversation
2. SubagentStop event occurs
3. User requests completion before tasks done

### Step 2: Hook Script Execution

The hook runs `eoa_orchestrator_stop_check.py`:

```bash
# Script path
${CLAUDE_PLUGIN_ROOT}/scripts/eoa_orchestrator_stop_check.py
```

### Step 3: Blocking Conditions

The hook blocks stop if ANY of these are true:

| Condition | Check | Blocking Message |
|-----------|-------|------------------|
| Plan incomplete | USER_REQUIREMENTS.md missing | "Complete Plan Phase first" |
| Plan not approved | status != approved | "Approve plan before stopping" |
| Tasks pending | Claude Tasks > 0 | "X Claude Tasks pending" |
| GitHub items open | Project items > 0 | "X GitHub items open" |
| Task file incomplete | Unchecked items > 0 | "X tasks in file incomplete" |
| TODO items | Session TODOs > 0 | "X TODO items remaining" |
| Verification pending | Loop < 4 | "Verification loop X/4" |
| IVP incomplete | Agents not verified | "Agent IVP pending" |
| Feedback pending | Config requests open | "Config feedback pending" |

### Step 4: Verification Mode

After all tasks complete, 4 verification loops required:

```
Loop 1: Initial verification - all tasks checked
Loop 2: Double-check - confirm still complete
Loop 3: Edge case review - verify no edge cases
Loop 4: Final confirmation - all systems verified

Only after Loop 4: ALL_TASKS_COMPLETE → Stop allowed
```

### Step 5: Hook Output Format

Hook communicates via JSON output:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "Stop",
    "permissionDecision": "deny",
    "permissionDecisionReason": "5 tasks pending in GitHub Projects"
  }
}
```

### Step 6: Completion Signals

The hook allows stop when:

**Signal 1: ALL_TASKS_COMPLETE**
```
ALL_TASKS_COMPLETE
```

**Signal 2: Completion Promise**
```
<promise>YOUR_CONFIGURED_PROMISE</promise>
```

### Step 7: Fail-Safe Behavior

The hook includes fail-safes:

| Scenario | Behavior |
|----------|----------|
| Unrecoverable error | Allow stop (don't trap user) |
| Cannot check tasks | Conservative block + log |
| Stale lock file | Clean up + continue |
| API timeout | Retry 3x then warn |

### Step 8: Debugging Stop Hook

```bash
# Check hook configuration
cat hooks/hooks.json | jq '.hooks.Stop'

# Manually run hook check
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/eoa_orchestrator_stop_check.py

# Check orchestrator log
tail -50 orchestrator.log | grep "STOP_HOOK"
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| Decision | String | "allow" or "deny" |
| Reason | String | Why stop was blocked/allowed |
| Pending Count | Number | Total pending tasks |
| Verification Loop | Number | Current verification loop (1-4) |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Hook not firing | Hook not configured | Check hooks.json |
| Always blocking | Task count error | Check task source APIs |
| Never blocking | Hook disabled | Verify hook registration |
| False positives | Stale task data | Refresh task sources |

## Overriding the Hook

**ONLY IN EMERGENCIES** - if genuinely stuck:

```bash
# Option 1: Cancel the loop
/cancel-orchestrator

# Option 2: Output completion signal
# (Only if truly complete)
echo "ALL_TASKS_COMPLETE"

# Option 3: Disable hook temporarily (DANGEROUS)
# Edit hooks.json to comment out Stop hook
# Remember to re-enable!
```

## Example

```bash
# Understanding hook behavior

# 1. Try to stop when tasks pending
/stop
# Output: "Stop blocked: 5 tasks pending in GitHub Projects"

# 2. Complete all tasks
# ... work until all tasks done ...

# 3. Try to stop again
/stop
# Output: "Stop blocked: Verification loop 1/4"

# 4. Wait for verification loops
# ... 4 loops run automatically ...

# 5. After verification complete
/stop
# Output: "Stop allowed: ALL_TASKS_COMPLETE"
```

## Checklist

- [ ] Understand hook trigger conditions
- [ ] Know blocking conditions
- [ ] Recognize verification mode
- [ ] Know completion signals
- [ ] Understand fail-safe behavior
- [ ] Know how to debug hook issues
- [ ] Know emergency override options (use sparingly)
