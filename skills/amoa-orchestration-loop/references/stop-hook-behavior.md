## Table of Contents
- Blocking conditions - When the stop hook prevents exit
- Completion signals - How to signal task completion
- Recovery behavior - Fail-safe and retry logic

---

## Blocking Conditions

The orchestrator stop hook (`amoa_orchestrator_stop_check.py`) enforces completion requirements:

- Plan Phase incomplete (requirements not documented, plan not approved)
- Orchestration Phase incomplete (modules not implemented)
- Pending tasks in any monitored source
- Instruction verification incomplete
- Config feedback requests unresolved
- Verification loops remaining (4 required after all tasks complete)

## Completion Signals

- Output `ALL_TASKS_COMPLETE` when all tasks genuinely done
- Output `<promise>YOUR_PHRASE</promise>` matching configured promise

## Recovery Behavior

- Fail-safe exit on unrecoverable errors (prevents user trap)
- Conservative blocking when task status cannot be determined
- Retry logic for transient failures
- Lock file cleanup for stale processes
