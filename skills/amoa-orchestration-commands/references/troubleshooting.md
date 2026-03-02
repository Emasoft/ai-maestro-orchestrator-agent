# Troubleshooting

## Contents

- 6.1 Loop won't start - common causes
- 6.2 Stop hook not firing - debugging steps
- 6.3 Tasks showing as pending incorrectly
- 6.4 Lock file issues and stale locks
- 6.5 Concurrent execution conflicts
- 6.6 Verification mode stuck
- 6.7 Helper script failures

---

## 6.1 Loop Won't Start - Common Causes

### Error: "Orchestrator loop already active"

**Cause**: State file already exists from previous loop.

**Solution**:
```bash
# Check current state
cat design/state/loop.md

# If you want to restart fresh
rm design/state/loop.md
/orchestrator-loop "Your task"
```

### Error: "Plan Phase not found"

**Cause**: Trying to start orchestration without Plan Phase.

**Solution**:
```bash
# Start Plan Phase first
/start-planning

# After planning is complete
/approve-plan

# Then start orchestration
/start-orchestration
```

### Error: "Plan Phase not approved"

**Cause**: Plan exists but not approved.

**Solution**:
```bash
# Check plan status
cat design/state/plan-phase.md | head -20

# Complete and approve the plan
/approve-plan
```

### Error: "Orchestration Phase state file not found"

**Cause**: `/approve-plan` didn't create the execution state file.

**Solution**:
```bash
# Re-run plan approval
/approve-plan

# Verify file was created
ls -la design/state/exec-phase.md
```

### Script Not Found

**Cause**: Plugin not properly installed or path issue.

**Solution**:
```bash
# Check CLAUDE_PLUGIN_ROOT is set
echo $CLAUDE_PLUGIN_ROOT

# Verify script exists
ls -la "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_setup_orchestrator_loop.py"

# Check script is executable
chmod +x "${CLAUDE_PLUGIN_ROOT}/scripts/"*.py
```

---

## 6.2 Stop Hook Not Firing - Debugging Steps

### Step 1: Verify Hook is Registered

```bash
# Check hooks configuration in plugin
cat "${CLAUDE_PLUGIN_ROOT}/hooks/hooks.json"

# Look for Stop event
# Should see: "Stop": [{"hooks": [...]}]
```

### Step 2: Check State File Exists

```bash
# The hook only fires if state file exists
ls -la design/state/loop.md
```

If missing, the hook allows exit (no loop active).

### Step 3: Enable Debug Logging

```bash
# Set debug mode
export ORCHESTRATOR_DEBUG=1

# Try to stop Claude Code and check log
cat design/logs/hook.log
```

### Step 4: Check Hook Script

```bash
# Verify script exists and is executable
ls -la "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_orchestrator_stop_check.py <!-- TODO: Script not implemented -->"

# Test script manually
echo '{}' | python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_orchestrator_stop_check.py <!-- TODO: Script not implemented -->"
```

### Step 5: Check for Python Errors

```bash
# Look for Python syntax errors
python3 -m py_compile "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_orchestrator_stop_check.py <!-- TODO: Script not implemented -->"
```

### Common Hook Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| Hook not registered | Exit allowed immediately | Check hooks.json |
| Script not executable | Permission denied | `chmod +x` on scripts |
| Python version | Syntax errors | Requires Python 3.8+ |
| Missing dependencies | Import errors | Use stdlib only |

---

## 6.3 Tasks Showing as Pending Incorrectly

### Claude Tasks Incorrect

**Symptom**: Shows pending Claude Tasks that don't exist or are already done.

**Debugging**:
```bash
# Run task check manually
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_check_tasks.py <!-- TODO: Script not implemented -->"

# Check TaskList API access
# Verify TaskList API is available

# Check task status via TaskList API
# Use Claude Code TaskList to inspect pending tasks
```

**Common causes**:
- Old files with 'pending' status not cleaned up
- Case sensitivity issues (should be lowercase 'pending')
- Stale TaskList cache

### GitHub Tasks Incorrect

**Symptom**: Shows GitHub tasks that are done or shouldn't appear.

**Debugging**:
```bash
# Check gh auth
gh auth status

# List project items manually
gh project item-list <PROJECT_NUMBER>

# Check for filters
cat design/state/loop.md | grep github
```

**Common causes**:
- Wrong project ID
- Items in "Done" column but not closed
- Auth token expired

### Task File Incorrect

**Symptom**: Checklist items counted wrong.

**Debugging**:
```bash
# Check task file content
cat TODO.md

# Count manually
grep -c '^\s*-\s*\[ \]' TODO.md  # Pending
grep -c '^\s*-\s*\[x\]' TODO.md  # Done
```

**Common causes**:
- Non-standard checkbox format
- Nested lists
- Code blocks with checkbox-like content

### TODO List Incorrect

**Symptom**: Session TODO shows wrong count.

**Cause**: TodoWrite tool output in transcript may be stale.

**Solution**: The TODO list reads from transcript which updates in real-time. If count seems wrong, verify by checking your current TODO list in Claude Code.

---

## 6.4 Lock File Issues and Stale Locks

### Symptom: "Concurrent execution detected"

**Cause**: Lock file exists from previous process.

**Debugging**:
```bash
# Check lock file
cat design/locks/hook.lock

# Check if PID is alive
ps -p $(cat design/locks/hook.lock) || echo "Process dead"
```

**Solution**:
```bash
# If process is dead, remove stale lock
rm design/locks/hook.lock
```

### Symptom: Lock File Keeps Reappearing

**Cause**: Multiple hook invocations or concurrent Claude sessions.

**Solution**:
1. Close other Claude Code windows
2. Remove lock file
3. Try again with single session

### Lock Age Check

The hook checks lock age and takes over old locks:
- Lock < 60 seconds old: Won't take over
- Lock > 60 seconds old: Takes over (assumes stuck)

If you're testing rapidly, you may hit the 60-second threshold.

---

## 6.5 Concurrent Execution Conflicts

### Symptom: Multiple Loops Fighting

**Signs**:
- Iteration count jumping erratically
- Log shows multiple PIDs
- State file changing unexpectedly

**Cause**: Multiple Claude Code sessions with hooks.

**Solution**:
1. Identify all Claude Code processes:
   ```bash
   ps aux | grep claude
   ```
2. Close all but one
3. Remove lock and state files
4. Restart single session

### Symptom: Ralph Wiggum Conflict

**Warning in log**: "Both orchestrator-loop AND ralph-loop are active"

**Cause**: Both hooks running simultaneously.

**Solution**:
```bash
# Choose one - remove the other
rm .claude/ralph-loop.local.md    # Keep orchestrator
# OR
rm design/state/loop.md  # Keep Ralph
```

### Prevention

- Only run one loop type at a time
- Close other Claude Code sessions before starting loops
- Use separate project directories for different work

---

## 6.6 Verification Mode Stuck

### Symptom: Verification Loops Never End

**Possible causes**:
1. New tasks created during verification
2. State file not updating
3. Counter not decrementing

**Debugging**:
```bash
# Check verification state
grep "verification" design/state/loop.md

# Should show:
# verification_mode: true
# verification_remaining: N (decreasing each time)
```

**Solution if stuck**:
```bash
# Option 1: Manually decrement
# Edit design/state/loop.md
# Set verification_remaining: 0

# Option 2: Skip verification entirely
# Edit file:
# verification_mode: false
# verification_remaining: 0
```

### Symptom: Verification Restarting

**Cause**: New pending tasks found during verification loop resets the process.

**Solution**: Complete all tasks before entering verification mode. If tasks keep appearing, investigate why:
- Task files being created
- GitHub issues being opened
- Task file being modified

---

## 6.7 Helper Script Failures

### Task Check Script Failure

**Error**: "Task check script failed after 3 attempts"

**Debugging**:
```bash
# Test script directly
"${CLAUDE_PLUGIN_ROOT}/scripts/check-tasks.sh"

# Check it's executable
chmod +x "${CLAUDE_PLUGIN_ROOT}/scripts/check-tasks.sh"

# Check TaskList API access
# Verify TaskList API is available
```

**Recovery**: The hook will conservatively block exit. Manually verify tasks and output `ALL_TASKS_COMPLETE` if done.

### GitHub Check Script Failure

**Error**: "GitHub check script failed after 3 attempts"

**Debugging**:
```bash
# Check gh CLI
gh auth status

# Test script directly
"${CLAUDE_PLUGIN_ROOT}/scripts/check-github-projects.sh"

# Check for network issues
ping github.com
```

**Common causes**:
- gh not installed
- Auth token expired
- Network issues
- Rate limiting

### Script Timeout

**Error**: Script takes >10 seconds

**Cause**: Network latency or large data set.

**Solution**:
- Check network connectivity
- Reduce project scope
- Increase timeout in script (not recommended)

### JSON Parse Errors

**Error**: "script returned invalid JSON"

**Debugging**:
```bash
# Run script and inspect output
"${CLAUDE_PLUGIN_ROOT}/scripts/check-tasks.sh"

# Validate JSON
"${CLAUDE_PLUGIN_ROOT}/scripts/check-tasks.sh" | python3 -m json.tool
```

**Common causes**:
- Script printing extra output (debug messages)
- Error messages mixed with JSON
- Encoding issues

---

## General Debugging Workflow

### 1. Enable Debug Mode

```bash
export ORCHESTRATOR_DEBUG=1
```

### 2. Check Log File

```bash
tail -100 design/logs/hook.log
```

### 3. Verify State Files

```bash
cat design/state/loop.md
cat design/state/exec-phase.md
```

### 4. Test Scripts Individually

```bash
# Test each component
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_check_orchestrator_status.py <!-- TODO: Script not implemented -->" --verbose
```

### 5. Check for Errors in Claude Code

Look at Claude Code's output panel for any error messages.

### 6. Reset If Needed

```bash
# Nuclear option - complete reset
rm -f design/state/*.md
rm -f design/locks/hook.lock
rm -f design/logs/hook.log
```
