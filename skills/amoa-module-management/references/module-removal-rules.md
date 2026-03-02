# Module Removal Rules Reference

## Contents

- 3.1 Which modules can be removed (pending only)
- 3.2 Why in-progress modules cannot be removed
- 3.3 Removal process step by step
- 3.4 GitHub Issue closure with wontfix label
- 3.5 Alternatives to removal (scope reduction)
- 3.6 Error handling and recovery

---

## 3.1 Which Modules Can Be Removed

Module removal is restricted to prevent wasted work and maintain project integrity.

### Removal Eligibility by Status

| Status | Can Remove? | Reason |
|--------|-------------|--------|
| `pending` | Yes | Work has not started |
| `assigned` | No | Agent may have begun preparation |
| `in-progress` | No | Work is ongoing |
| `complete` | No | Work is finished and delivered |

### The Pending Status Requirement

A module is `pending` when:
- It exists in the plan
- No agent has been assigned
- `assigned_to` field is `null`
- `status` field is `pending`

**Pending modules are safe to remove because**:
- No resources have been invested
- No agent is expecting to work on it
- No partial implementation exists
- Clean removal with no orphans

### Command Validation

When `/remove-module` is executed, the script validates:

1. Module exists in state file
2. Module status is `pending`
3. No agent is assigned
4. (If --force not used) Confirmation requested

```python
# Validation logic
if module.get("status") in ("in-progress", "complete"):
    print("ERROR: Cannot remove module with status '{status}'")
    return False

if module.get("assigned_to") and not force:
    print("ERROR: Module is assigned to '{agent}'")
    return False
```

---

## 3.2 Why In-Progress Modules Cannot Be Removed

Removing an in-progress module would cause significant problems. This section explains why the restriction exists.

### Problems with Removing In-Progress Modules

| Problem | Description |
|---------|-------------|
| Wasted effort | Agent has invested time and resources |
| Orphaned code | Partial implementation may exist |
| Agent confusion | Agent expects to continue work |
| State inconsistency | Assignment records become invalid |
| Trust erosion | Agents lose confidence in orchestrator |

### Work Already Done

When a module is in-progress, the agent may have:
- Read and understood requirements
- Designed the implementation approach
- Written partial code
- Created branch and commits
- Started PR draft
- Requested clarifications

Removing the module discards all this work.

### The Correct Approach for In-Progress Modules

Instead of removing an in-progress module:

| Situation | Correct Action |
|-----------|----------------|
| Scope too large | Modify criteria to reduce scope |
| No longer needed | Let agent complete minimal viable version |
| Agent struggling | Reassign to different agent |
| Budget constraints | Communicate constraints, negotiate scope |

### Example: Scope Reduction Instead of Removal

**Bad approach** (removing in-progress module):
```bash
# This will fail
/remove-module oauth-google
# ERROR: Cannot remove module with status 'in-progress'
```

**Good approach** (reduce scope):
```bash
/modify-module oauth-google --criteria "Support Google OAuth only (skip auto-linking)"
```

---

## 3.3 Removal Process Step by Step

When a pending module is removed, the following steps occur.

### Step 1: Validate Removal

The script checks:
- Module exists
- Status is `pending`
- No agent assigned

If validation fails, error is returned and nothing changes.

### Step 2: Remove from State File

The module entry is deleted from `modules_status` array:

**Before**:
```yaml
modules_status:
  - id: "auth-core"
    status: "in-progress"
  - id: "oauth-facebook"      # Module to remove
    status: "pending"
  - id: "oauth-google"
    status: "pending"
```

**After**:
```yaml
modules_status:
  - id: "auth-core"
    status: "in-progress"
  - id: "oauth-google"
    status: "pending"
```

### Step 3: Update Module Count

The `modules_total` counter is decremented:

**Before**: `modules_total: 3`
**After**: `modules_total: 2`

### Step 4: Remove Active Assignments

Any assignment records for this module are removed (should be none for pending modules, but cleaned defensively):

```python
assignments = data.get("active_assignments", [])
data["active_assignments"] = [
    a for a in assignments
    if a.get("module") != module_id
]
```

### Step 5: Close GitHub Issue

The linked GitHub Issue is closed with:
- Comment: "Module removed from plan"
- Label: `wontfix` added

```bash
gh issue close {issue_num} -c "Module removed from plan"
```

### Step 6: Write Updated State

State file is saved with changes.

### Step 7: Return Success

Output confirms removal:
```
Removed module: oauth-facebook
  Closed GitHub Issue: #45
```

---

## 3.4 GitHub Issue Closure with Wontfix Label

When a module is removed, its linked GitHub Issue is automatically closed.

### Closure Process

1. Issue number extracted from `github_issue` field (e.g., "#45" -> "45")
2. Issue closed via `gh issue close` command
3. Comment added explaining closure
4. `wontfix` label applied (optional, depends on repo labels)

### Closure Comment

The comment added to the issue:
```
Module removed from plan
```

This comment provides:
- Record of why issue was closed
- Context for anyone viewing issue later
- Traceability from code to decision

### If Issue Closure Fails

If `gh issue close` fails:
- Warning displayed
- Module still removed from state
- Issue requires manual closure

**Manual closure**:
```bash
gh issue close 45 -c "Module removed from plan"
```

### Closed Issue Visibility

Closed issues remain visible in:
- Issue search (with `is:closed` filter)
- Issue history
- Project boards (closed column)

They are NOT visible in:
- Default issue list
- Open issue count

---

## 3.5 Alternatives to Removal (Scope Reduction)

Instead of removing a module, consider these alternatives that preserve work and maintain relationships.

### Alternative 1: Reduce Scope

Change acceptance criteria to a minimal viable version:

**Before**:
```yaml
acceptance_criteria: "Full OAuth with Google, Facebook, GitHub, and auto-linking"
```

**After**:
```bash
/modify-module oauth-all --criteria "Basic Google OAuth only"
```

Benefits:
- Agent can complete something
- GitHub Issue remains useful
- Progress is made

### Alternative 2: Lower Priority

Demote the module to low priority:

```bash
/prioritize-module oauth-facebook --priority low
```

Benefits:
- Module remains in plan
- Not removed, just delayed
- Can be picked up later

### Alternative 3: Split into Phases

Create a phase 1 module with reduced scope, phase 2 for future:

```bash
# Modify original to phase 1
/modify-module oauth-google --name "OAuth Phase 1" --criteria "Basic Google OAuth"

# Add phase 2 for later
/add-module "OAuth Phase 2" --criteria "Add Facebook and auto-linking" --priority low
```

### Alternative 4: Reassign

If the problem is the agent, not the module:

```bash
/reassign-module oauth-google --to implementer-2
```

### Decision Matrix

| Situation | Best Alternative |
|-----------|------------------|
| Module too big | Reduce scope |
| Module not urgent | Lower priority |
| Agent struggling | Reassign |
| Budget constraints | Reduce scope + lower priority |
| Feature cancelled entirely | Remove (if pending) |

---

## 3.6 Error Handling and Recovery

This section covers error scenarios and how to handle them.

### Error: Module Not Found

**Message**: `ERROR: Module '{module_id}' not found`

**Cause**: Wrong module ID used.

**Solution**: Use `/orchestration-status` to see correct module IDs:
```bash
/orchestration-status
# Lists all modules with their IDs
```

### Error: Status is In-Progress

**Message**: `ERROR: Cannot remove module with status 'in-progress'`

**Cause**: Trying to remove a module that has started.

**Solutions**:
1. Wait for completion
2. Reduce scope instead
3. Accept the sunk cost

### Error: Status is Complete

**Message**: `ERROR: Cannot remove module with status 'complete'`

**Cause**: Trying to remove finished work.

**Solution**: This is historical record; cannot and should not be removed.

### Error: Has Assignment

**Message**: `ERROR: Module is assigned to '{agent}'. Use --force to remove anyway`

**Cause**: Module has been assigned but not yet started.

**Solutions**:
1. Reassign module first, then remove
2. Use `--force` flag (with caution)

```bash
# Force removal (use with caution)
/remove-module oauth-google --force
```

### Error: GitHub Issue Not Closed

**Message**: `Warning: Could not close GitHub Issue #45`

**Cause**: `gh` CLI failed (auth issue, network issue, etc.)

**Solution**: Close manually:
```bash
gh issue close 45 -c "Module removed from plan"
```

### Error: State File Write Failed

**Message**: `ERROR: Failed to write state file: {error}`

**Cause**: File permission issue or disk full.

**Solutions**:
1. Check file permissions on `design/state/exec-phase.md`
2. Check disk space
3. Try again

### Recovery: Accidentally Removed Module

If a module was accidentally removed:

1. **State file recovery** - If git tracked, revert:
   ```bash
   git checkout -- design/state/exec-phase.md
   ```

2. **Re-add module** - Add it back manually:
   ```bash
   /add-module "Module Name" --criteria "Original criteria" --priority level
   ```

3. **Reopen GitHub Issue** - Reopen the closed issue:
   ```bash
   gh issue reopen 45
   ```

---

## Force Removal Flag

The `--force` flag bypasses certain safety checks.

### What --force Bypasses

| Check | Normal Behavior | With --force |
|-------|-----------------|--------------|
| Assigned agent | Error returned | Agent ignored, removal proceeds |
| Confirmation prompt | Prompt shown | Prompt skipped |

### What --force Does NOT Bypass

| Check | Behavior |
|-------|----------|
| Status check | In-progress and complete still blocked |
| Module existence | Must exist |

### When to Use --force

| Scenario | Appropriate? |
|----------|--------------|
| Agent assigned but hasn't started | Yes |
| Quick cleanup | Yes |
| Testing removal | Yes |
| Agent actively working | No |
| Want to remove complete module | No |

**Example**:
```bash
# Force remove assigned-but-not-started module
/remove-module oauth-facebook --force
```

---

## Related Commands

| Command | When to Use |
|---------|-------------|
| `/modify-module` | Reduce scope instead of removing |
| `/prioritize-module` | Demote instead of removing |
| `/reassign-module` | Change agent if that's the issue |
| `/orchestration-status` | Check module status and IDs |
