# Script Reference - Part 4: Modified Scripts

This document covers the modified scripts for Two-Phase Mode.

## Contents

- 3.1 eoa_orchestrator_stop_check.py <!-- TODO: Script not implemented --> - Phase-aware stop hook for completion enforcement

---

## 3.1 eoa_orchestrator_stop_check.py <!-- TODO: Script not implemented -->

**Purpose:** Phase-aware stop hook for completion enforcement.

**Location:** `scripts/eoa_orchestrator_stop_check.py <!-- TODO: Script not implemented -->`

**Modifications for Two-Phase Mode:**

### Plan Phase Checking

When in Plan Phase, the script:
1. Reads `design/state/plan-phase.md`
2. Blocks if `plan_phase_complete: false`
3. Shows missing exit criteria

### Orchestration Phase Checking

When in Orchestration Phase, the script:
1. Reads `design/state/exec-phase.md`
2. Blocks if any module not complete
3. Blocks if verification loops remaining
4. Shows incomplete modules list

### Output Format

The script outputs JSON with the following structure:

```json
{
  "decision": "block",
  "reason": "Plan Phase incomplete",
  "systemMessage": "Complete planning before stopping...",
  "outputToUser": "Plan Phase incomplete. Missing criteria: ..."
}
```

### Decision Values

| Decision | Meaning |
|----------|---------|
| `allow` | Orchestrator can stop (phase complete) |
| `block` | Orchestrator cannot stop (work remaining) |

### Stop Blocking Conditions

**Plan Phase blocks when:**
- `plan_phase_complete` is `false`
- USER_REQUIREMENTS.md does not exist
- No modules defined
- Modules missing acceptance criteria

**Orchestration Phase blocks when:**
- Any module status is not `complete`
- Verification loops > 0 remaining
- Active assignments pending completion

### Error Handling

The script handles these error conditions:
- State file not found (allows stop - not in Two-Phase Mode)
- Invalid YAML in state file (exit code 1)
- Missing required fields (reports in output)

**Exit codes:**
- 0: Hook executed (decision in JSON output)
- Non-zero: Error parsing state

---

**Navigation:**
- [Back to Script Reference Index](script-reference.md)
- [Previous: Orchestration Advanced Scripts](script-reference-part3-orchestration-advanced.md)
