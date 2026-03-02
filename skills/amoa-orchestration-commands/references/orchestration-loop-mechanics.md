# Orchestration Loop Mechanics

## Contents

- 3.1 What the orchestrator loop does
- 3.2 Task source monitoring and priority
- 3.3 Iteration counting and max iterations
- 3.4 Verification mode (4-loop quadruple-check)
- 3.5 Completion signals (ALL_TASKS_COMPLETE)
- 3.6 Stop hook behavior and blocking logic

---

## 3.1 What the Orchestrator Loop Does

The orchestrator loop is a continuous task-driven development loop that:

1. **Monitors multiple task sources** - Claude Tasks, GitHub Projects, task files, TODO list
2. **Prevents premature exit** - Blocks Claude from stopping until all tasks complete
3. **Feeds prompts back** - Reminds Claude of pending work when trying to stop
4. **Tracks progress** - Counts iterations and logs activity
5. **Enforces verification** - Requires 4 verification loops after tasks complete

### Loop Lifecycle

```
START
  |
  v
[Create State File] --> design/state/loop.md
  |
  v
[Work on Tasks]
  |
  v
[Try to Stop] ---> [Stop Hook Fires]
  |                    |
  |                    v
  |               [Check All Task Sources]
  |                    |
  |            +-------+-------+
  |            |               |
  |            v               v
  |       [Tasks Pending]  [All Complete]
  |            |               |
  |            v               v
  |       [Block Exit]    [Enter Verification Mode]
  |            |               |
  |            v               v
  +<-----[Feed Prompt]    [4 Verification Loops]
                               |
                               v
                          [Allow Exit]
```

### State File Structure

The loop state is stored in `design/state/loop.md`:

```yaml
---
iteration: 5
max_iterations: 100
completion_promise: "null"
task_file: "null"
check_tasks: true
check_github: true
github_project_id: ""
started_at: 2026-01-09T10:30:00+00:00
verification_mode: false
verification_remaining: 0
---

Initial task prompt goes here...
```

---

## 3.2 Task Source Monitoring and Priority

The orchestrator monitors 4 task sources. Priority is determined by the orchestrator based on urgency and impact.

### Source 1: Claude Tasks (Personal Tasks)

**Location**: Claude Code TaskList API
**Format**: Tasks with 'pending' or 'in-progress' status
**Purpose**: Personal orchestrator tasks

**Detection**:
```bash
# Checked by check-tasks.sh helper script
# Returns JSON: {"pending_count": N, "exists": true, "tasks": [...]}
```

**Priority**: High - these are tasks you defined for yourself

### Source 2: GitHub Projects (Team Tasks)

**Location**: GitHub API
**Format**: Project items not in "Done" status
**Purpose**: Team collaboration, shared backlog

**Detection**:
```bash
# Checked by check-github-projects.sh helper script
# Returns JSON: {"pending_count": N, "available": true, "tasks": [...]}
```

**Priority**: High - these affect team members waiting for your work

### Source 3: Task File (Markdown Checklist)

**Location**: User-specified path via `--task-file`
**Format**: Markdown checklist with `- [ ]` (pending) or `- [~]` (in progress)
**Purpose**: Session-specific task lists, sprint checklists

**Detection**:
```python
# Regex patterns
pending = r"^\s*-\s*\[ \]"      # Unchecked boxes
in_progress = r"^\s*-\s*\[~\]"  # Tilde for in-progress
```

**Priority**: Medium - user-defined for current session

### Source 4: Claude TODO List (Session)

**Location**: Claude's transcript JSON
**Format**: TodoWrite tool output with `status: pending` or `status: in-progress`
**Purpose**: Session-level tracking in Claude Code

**Detection**:
```python
# Searches transcript for latest todos array
# Counts items with status "pending" or "in-progress"
```

**Priority**: Normal - may include transient session tasks

### Prioritization Strategy

When multiple sources have pending tasks:

1. **Critical blockers first** - Tasks blocking other agents
2. **GitHub Project items** - Team dependencies
3. **Claude Tasks** - Self-assigned priorities
4. **Session TODO items** - Current session flow

---

## 3.3 Iteration Counting and Max Iterations

### How Iterations Work

Each time the stop hook fires and blocks exit, the iteration counter increments:

```python
# In stop hook
next_iteration = iteration + 1
update_state_file(state_file_path, {"iteration": next_iteration})
```

### Max Iterations (Escalation Threshold)

**Important**: Max iterations is NOT an auto-exit trigger!

Per RULE 13 (no time-boxing), reaching max iterations triggers an **escalation**, not an exit:

```
ORCHESTRATOR ESCALATION - ITERATION THRESHOLD REACHED

The orchestrator has completed 100 iterations without finishing all tasks.
This is NOT an automatic exit - per RULE 13, there are no deadlines or time limits.

REQUIRED ACTION:
1. Review all task sources manually
2. If ALL tasks are truly complete, output: ALL_TASKS_COMPLETE
3. If tasks remain, continue working on them
4. The orchestrator will NOT auto-exit based on iteration count
```

### Configuring Max Iterations

```bash
# Default: 100 iterations
/orchestrator-loop "My task"

# Custom limit: 50 iterations
/orchestrator-loop "My task" --max-iterations 50

# Unlimited (0 = no escalation)
/orchestrator-loop "My task" --max-iterations 0
```

### Why Not Auto-Exit?

Quality over speed. The orchestrator must complete ALL tasks regardless of iteration count because:
- Tasks may be genuinely complex
- External blockers may cause delays
- Auto-exit could leave incomplete work

---

## 3.4 Verification Mode (4-Loop Quadruple-Check)

### What Verification Mode Does

When all task sources show 0 pending tasks, the orchestrator enters a mandatory 4-loop verification phase before allowing exit.

**Purpose**: Prevent premature exit with:
- Unreviewed errors
- Missing elements
- Poor quality solutions
- Incomplete documentation

### Verification Loop Process

**Loop 1**: Initial comprehensive review
**Loop 2**: Second pass focusing on edge cases
**Loop 3**: Third pass checking documentation
**Loop 4**: Final confirmation

In each loop, examine:
- Errors and missing elements
- Wrong references and TDD violations
- Inconsistent naming and incongruences
- Redundant or duplicated parts
- Incomplete planning
- Risks without safeguards
- Workarounds instead of proper fixes
- Outdated documentation

### Verification Loop Prompt

Each verification loop presents this prompt:

```
VERIFICATION LOOP N of 4 - MANDATORY REVIEW BEFORE EXIT

All task sources show 0 pending tasks. However, before allowing exit,
the orchestrator must complete 4 verification loops to quadruple-check
the quality and correctness of all changes made.

Examine your changes in depth...

IMPORTANT (RULE 0 COMPLIANT): The orchestrator does NOT fix issues directly.
Instead:
1. IDENTIFY all issues found during this review
2. DOCUMENT them in a verification report
3. DELEGATE fixing to remote agents via AI Maestro (for code issues)
4. Track delegated fixes until completion
5. Re-verify in next loop that issues are resolved
```

### State During Verification

```yaml
verification_mode: true
verification_remaining: 3  # Decrements each loop
```

### Exiting Verification Mode

Exit is allowed only when:
- `verification_remaining` reaches 0
- All 4 loops have completed
- No new tasks were created during verification

---

## 3.5 Completion Signals (ALL_TASKS_COMPLETE)

### How to Signal Completion

When all tasks are genuinely complete, output this exact text:

```
ALL_TASKS_COMPLETE
```

The stop hook detects this in your output and allows exit.

### Completion Promise Alternative

You can configure a custom completion phrase:

```bash
/orchestrator-loop --completion-promise "SPRINT COMPLETE"
```

Then output:
```
<promise>SPRINT COMPLETE</promise>
```

**Critical requirement**: The promise statement must be **completely and unequivocally TRUE**. Do NOT output false statements to exit the loop.

### Detection Logic

```python
# In stop hook
if "ALL_TASKS_COMPLETE" in last_output:
    info("ALL_TASKS_COMPLETE marker detected")
    return True

if completion_promise != "null":
    promise_match = re.search(r"<promise>(.*?)</promise>", last_output)
    if promise_match and promise_match.group(1) == completion_promise:
        return True
```

---

## 3.6 Stop Hook Behavior and Blocking Logic

### When the Stop Hook Fires

The stop hook fires whenever Claude attempts to stop (end conversation).

### Decision Flow

```
STOP ATTEMPT
    |
    v
[Check Two-Phase Mode]
    |
    +---> Plan Phase incomplete? ---> BLOCK (phase prompt)
    |
    +---> Orchestration Phase incomplete? ---> BLOCK (phase prompt)
    |
    +---> Verification incomplete? ---> BLOCK (verification prompt)
    |
    +---> Config feedback pending? ---> BLOCK (feedback prompt)
    |
    v
[Check orchestrator-loop.local.md exists]
    |
    No ---> ALLOW EXIT
    |
    Yes
    |
    v
[Check completion signals]
    |
    Found ---> Delete state file, ALLOW EXIT
    |
    v
[Check all task sources]
    |
    v
[Sum pending counts]
    |
    0 pending ---> Enter/continue verification mode
    |
    >0 pending ---> BLOCK EXIT, feed continuation prompt
```

### Block Output Format

When blocking exit, the hook outputs JSON:

```json
{
  "decision": "block",
  "reason": "ORCHESTRATOR CONTINUATION - DO NOT STOP\n\n...",
  "systemMessage": "Orchestrator iteration 5/100 | 3 pending tasks across 2 sources"
}
```

### Recovery Behaviors

**Fail-safe exit**: On unrecoverable errors, allows exit to not trap user
```python
def fail_safe_exit(reason):
    error(f"Fail-safe exit triggered: {reason}")
    cleanup()
    sys.exit(0)
```

**Conservative blocking**: When task status uncertain, blocks exit to be safe
```python
def conservative_block_exit(reason):
    # Cannot determine task status - block exit
    output = {
        "decision": "block",
        "reason": "TASK CHECK FAILED - manually verify and output ALL_TASKS_COMPLETE"
    }
```

### Coexistence with Ralph Wiggum

If both orchestrator-loop and ralph-loop state files exist, a warning is issued:
```
WARNING: Both orchestrator-loop AND ralph-loop are active simultaneously!
This may cause conflicts. Consider using only one at a time.
```
