# Two-Phase Mode Troubleshooting

## Contents

- 1. Plan Phase Issues
- 2. Orchestration Phase Issues
- 3. State File Issues
- 4. Communication Issues
- 5. Stop Hook Issues

---

## 1. Plan Phase Issues

### Issue: Plan Phase won't transition to Orchestration Phase

**Cause**: Exit criteria not met - some requirements incomplete or modules undefined.

**Solution**:
1. Run `/planning-status` to see which criteria are incomplete
2. Complete all requirement sections in USER_REQUIREMENTS.md
3. Ensure all modules have acceptance criteria defined
4. Run `/approve-plan` again

### Issue: USER_REQUIREMENTS.md validation fails

**Cause**: Missing required sections or malformed content.

**Solution**:
1. Check that all required sections exist (Overview, Functional Requirements, Non-Functional Requirements, Modules)
2. Ensure each module has: name, description, acceptance criteria
3. Validate markdown formatting

### Issue: /approve-plan creates duplicate GitHub Issues

**Cause**: Previous partial execution or manual issue creation.

**Solution**:
1. Check existing GitHub Issues with project labels
2. Close or delete duplicates
3. Re-run `/approve-plan` with `--skip-existing` flag if available
4. Or manually link existing issues in state file

---

## 2. Orchestration Phase Issues

### Issue: Stop hook blocks exit during Orchestration Phase

**Cause**: Modules still pending or verification loops remaining.

**Solution**:
1. Run `/orchestration-status` to see pending modules
2. Check GitHub Project for unfinished issues
3. Complete all assigned modules or reassign blocked ones
4. After all modules complete, pass 4 verification loops

### Issue: Module stuck in "in-progress" status

**Cause**: Agent not responding or work blocked.

**Solution**:
1. Run `/check-agents` to poll agent status
2. Check AI Maestro messages for agent responses
3. If blocked, use `/reassign-module` to different agent
4. Update state file manually if needed

### Issue: Verification loops not incrementing

**Cause**: Verification criteria not met or state not updated.

**Solution**:
1. Ensure agent submitted PR for review
2. Run verification (tests, lint, type check)
3. Record verification result in state file
4. Increment loop counter after each verification

---

## 3. State File Issues

### Issue: State file corruption or missing

**Cause**: Manual editing or interrupted session.

**Solution**:
1. Check `design/state/plan-phase.md` exists
2. Check `design/state/exec-phase.md` exists
3. If corrupted, backup and recreate with `/start-planning` or `/start-orchestration`
4. Recover module status from GitHub Issues

### Issue: State file YAML parse error

**Cause**: Invalid YAML syntax in frontmatter.

**Solution**:
1. Validate YAML syntax online or with `yq`
2. Check for:
   - Missing quotes around special characters
   - Improper indentation
   - Unclosed brackets/braces
3. Fix syntax and retry operation

### Issue: State file out of sync with GitHub Issues

**Cause**: Manual changes on GitHub or failed sync.

**Solution**:
1. Run `eoa_sync_github_issues.py <!-- TODO: Script not implemented -->` to sync state
2. Resolve conflicts (state file is authoritative)
3. Update GitHub Issues to match state if needed

---

## 4. Communication Issues

### Issue: Remote agent not responding to assignments

**Cause**: AI Maestro messaging issue or agent offline.

**Solution**:
1. Verify AI Maestro is accessible using the `agent-messaging` skill health check
2. Check agent is registered: `/orchestration-status`
3. Retry assignment with `/assign-module`
4. If persistent, reassign to different agent: `/reassign-module`

### Issue: AI Maestro messages not delivered

**Cause**: Network issue, agent not listening, or queue full.

**Solution**:
1. Check AI Maestro server is running
2. Verify target agent session name is correct
3. Check the message queue using the `agent-messaging` skill to list messages for the target agent
4. Retry message with higher priority

### Issue: Human developer not receiving GitHub notifications

**Cause**: GitHub notification settings or assignment issue.

**Solution**:
1. Verify developer is assigned to GitHub Issue
2. Check developer's GitHub notification settings
3. Use @mention in issue comments
4. Send direct communication outside GitHub if urgent

---

## 5. Stop Hook Issues

### Issue: Stop hook not firing

**Cause**: Hook not configured or script not executable.

**Solution**:
1. Verify hook is in settings.json or plugin hooks.json
2. Check script is executable: `chmod +x eoa_orchestrator_stop_check.py <!-- TODO: Script not implemented -->`
3. Run script manually to test: `python eoa_orchestrator_stop_check.py <!-- TODO: Script not implemented -->`
4. Check hook event type is "Stop"

### Issue: Stop hook allows exit when it shouldn't

**Cause**: State file not found or incorrect phase detection.

**Solution**:
1. Verify state files exist in correct locations
2. Check phase detection logic in script
3. Ensure module statuses are correctly set
4. Run `/orchestration-status` to verify state

### Issue: Stop hook blocks exit incorrectly

**Cause**: Stale state or false positive.

**Solution**:
1. Run `/orchestration-status` to see actual state
2. If all modules are truly complete, update state file
3. Clear any stuck "in-progress" modules
4. Re-run stop hook to verify

---

## Related References

- [State File Formats](state-file-formats.md) - YAML schema documentation
- [Command Reference](command-reference.md) - All available commands
- [Script Reference](script-reference.md) - Script troubleshooting
