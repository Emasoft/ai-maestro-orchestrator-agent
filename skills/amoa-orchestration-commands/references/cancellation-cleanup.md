# Cancellation and Cleanup

## Contents

- 4.1 When to cancel vs let loop complete naturally
- 4.2 Cancellation procedure step-by-step
- 4.3 Cleanup of state files and locks
- 4.4 Recovery after unexpected termination

---

## 4.1 When to Cancel vs Let Loop Complete Naturally

### Let the Loop Complete Naturally When

1. **Tasks are genuinely complete** - Output `ALL_TASKS_COMPLETE` instead of cancelling
2. **Verification is in progress** - Let the 4 verification loops finish
3. **Only a few tasks remain** - Finish them rather than abandoning
4. **Work will resume soon** - The loop will pick up where you left off

### Cancel the Loop When

1. **Wrong project** - Started loop in wrong directory
2. **Configuration error** - Wrong task file or GitHub project
3. **Emergency** - User needs immediate exit for external reason
4. **Stuck state** - Loop is misbehaving and needs reset
5. **Testing complete** - Was testing loop behavior, not doing real work

### Consequences of Cancellation

| Action | Consequence |
|--------|-------------|
| Cancel | Pending tasks remain incomplete |
| Cancel | GitHub issues stay open |
| Cancel | Claude Tasks still pending |
| Cancel | Verification loops skipped |
| Cancel | No quality check performed |

**Warning**: Cancelling loses the orchestrator's tracking of what work was done. If you restart later, you'll need to manually assess completion status.

---

## 4.2 Cancellation Procedure Step-by-Step

### Method 1: Use the Cancel Command

```bash
/cancel-orchestrator
```

This command:
1. Checks if loop state file exists
2. Reads current iteration number
3. Removes the state file
4. Reports: "Cancelled orchestrator loop (was at iteration N)"

### Method 2: Manual Removal

If the command doesn't work, manually remove the state file:

```bash
# Check if loop is active
test -f design/state/loop.md && echo "Loop active" || echo "No loop"

# Read current state (optional)
cat design/state/loop.md

# Remove state file to cancel
rm design/state/loop.md
```

### Verification After Cancellation

After cancelling, verify:

```bash
# State file should be gone
test -f design/state/loop.md && echo "STILL EXISTS" || echo "Removed"

# No lock file should remain
test -f design/locks/hook.lock && echo "Lock exists - check below" || echo "Clean"

# Check log for cancellation entry
tail -5 design/logs/hook.log
```

---

## 4.3 Cleanup of State Files and Locks

### State Files

| File | Purpose | Safe to Delete |
|------|---------|----------------|
| `design/state/loop.md` | Loop state | Yes - cancels loop |
| `design/state/exec-phase.md` | Execution phase | **Caution** - loses phase tracking |
| `design/state/plan-phase.md` | Plan phase | **Caution** - loses plan approval |
| `design/logs/hook.log` | Debug logs | Yes - just logs |
| `design/locks/hook.lock` | Concurrency lock | Usually auto-cleaned |

### Lock File Cleanup

The lock file `design/locks/hook.lock` should be cleaned automatically, but may become stale if:
- Process crashed
- System shut down abruptly
- Bug in cleanup code

**To clean stale lock**:

```bash
# Check if lock file exists
ls -la design/locks/hook.lock

# Check if PID in lock is alive
cat design/locks/hook.lock  # Shows PID
ps -p $(cat design/locks/hook.lock) || echo "Process dead - safe to remove"

# Remove stale lock
rm design/locks/hook.lock
```

### Log File Management

The log file rotates automatically at 100KB. To manually clean:

```bash
# Clear current log
> design/logs/hook.log

# Remove old rotated log
rm design/logs/hook.log.old

# View recent entries
tail -50 design/logs/hook.log
```

### Full Cleanup (Reset Everything)

To completely reset orchestrator state:

```bash
# Remove all orchestrator state files
rm -f design/state/loop.md
rm -f design/state/exec-phase.md
rm -f design/state/plan-phase.md
rm -f design/locks/hook.lock
rm -f design/logs/hook.log
rm -f design/logs/hook.log.old
```

**Warning**: This loses all orchestration state. You'll need to start Plan Phase from scratch.

---

## 4.4 Recovery After Unexpected Termination

### Scenario: Claude Code Crashed

If Claude Code crashes while orchestrator loop was active:

1. **Check loop state file still exists**:
   ```bash
   cat design/state/loop.md
   ```

2. **Note the iteration count** - You'll resume from here

3. **Check for stale lock**:
   ```bash
   rm -f design/locks/hook.lock  # Safe - previous process is gone
   ```

4. **Restart Claude Code** - Loop will continue automatically when stop hook fires

### Scenario: System Reboot

After system reboot:

1. **State files persist** - Markdown files survive reboot

2. **Lock file may be stale** - Process that created it is gone
   ```bash
   rm -f design/locks/hook.lock
   ```

3. **Resume normally** - Start Claude Code and loop continues

### Scenario: State File Corrupted

If the state file has invalid YAML:

```bash
# Check if file is valid
head -20 design/state/loop.md

# If corrupted, remove and restart
rm design/state/loop.md
/orchestrator-loop "Resume my tasks"
```

**Symptoms of corruption**:
- Error: "No frontmatter found in state file"
- Error: "State file corrupted"
- Garbled content when viewing file

### Scenario: Loop Won't Cancel

If `/cancel-orchestrator` doesn't work:

1. **Check file permissions**:
   ```bash
   ls -la design/state/loop.md
   ```

2. **Try manual removal**:
   ```bash
   rm -f design/state/loop.md
   ```

3. **Check for race condition** - Hook might be recreating file
   ```bash
   # Kill any running hook processes
   ps aux | grep orchestrator
   ```

4. **Last resort - remove .claude directory lock**:
   ```bash
   rm -f design/locks/hook.lock
   rm -f design/state/loop.md
   ```

### Scenario: Two-Phase State Inconsistent

If execution phase says "complete" but loop is still active:

1. **Check both state files**:
   ```bash
   grep "status" design/state/exec-phase.md
   grep "all_modules_complete" design/state/exec-phase.md
   ```

2. **Sync them**:
   - If modules complete, cancel loop: `rm design/state/loop.md`
   - If modules incomplete, update exec phase status

### Preserving Work Before Cleanup

Before aggressive cleanup, preserve important state:

```bash
# Backup all state files
mkdir -p .claude/backup-$(date +%Y%m%d)
cp design/state/*.md .claude/backup-$(date +%Y%m%d)/

# Export log for debugging
cp design/logs/hook.log .claude/backup-$(date +%Y%m%d)/
```

Then proceed with cleanup knowing you can review what was happening.
