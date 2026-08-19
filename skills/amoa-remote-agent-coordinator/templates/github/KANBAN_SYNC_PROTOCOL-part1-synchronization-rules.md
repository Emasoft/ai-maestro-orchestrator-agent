# Kanban Synchronization Protocol - Part 1: Synchronization Rules

This document contains the agent synchronization rules for updating GitHub issue status and kanban board positions.

**Parent document:** [KANBAN_SYNC_PROTOCOL.md](./KANBAN_SYNC_PROTOCOL.md)

---

## Agent Synchronization Rules

### Rule 1: Update Status When Starting Work

**When:** Agent begins working on an assigned task

**Actions:**
```bash
# 1. Update issue label
gh issue edit {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --remove-label "status:backburner" \
  --add-label "status:dev"

# 2. Move card on kanban
gh project item-edit \
  --project-id {{PROJECT_ID}} \
  --id {{ITEM_ID}} \
  --field-id {{STATUS_FIELD_ID}} \
  --value "Dev"

# 3. Add comment to issue
gh issue comment {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --body "🤖 Agent **{{AGENT_NAME}}** started working on this task.

**Session:** {{SESSION_ID}}
**Platform:** {{PLATFORM}}
**Started:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
```

**Required Fields:**
- Issue must be assigned to agent
- Toolchain template must be specified
- All required tools must be verified available

### Rule 2: Update Status When Blocked

**When:** Agent encounters blocking issue (missing dependency, external service down, unclear requirements)

**Actions:**
```bash
# 1. Update issue labels
gh issue edit {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --remove-label "status:dev" \
  --add-label "status:blocked"

# 2. Keep in "Dev" column but add blocked indicator
gh issue comment {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --body "⚠️ Agent **{{AGENT_NAME}}** is blocked.

**Blocker:** {{BLOCKER_DESCRIPTION}}
**Impact:** {{IMPACT_DESCRIPTION}}
**Needs:** {{REQUIRED_ACTION}}

cc @{{ORCHESTRATOR_OWNER}}"

# 3. Notify orchestrator via AI Maestro messaging system (AMP)
# Use amp-send to send a high-priority alert to the orchestrator agent,
# with subject "Agent blocked: {{TASK_ID}}" and message body containing the agent name,
# task ID, and blocker description. The message type should be "alert" and priority "high".
```

**Required Fields:**
- Clear description of blocker
- What is needed to unblock
- Estimated impact on timeline

### Rule 3: Update Status When Unblocked

**When:** Blocker is resolved and agent can resume work

**Actions:**
```bash
# 1. Update issue labels
gh issue edit {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --remove-label "status:blocked" \
  --add-label "status:dev"

# 2. Add comment
gh issue comment {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --body "✅ Agent **{{AGENT_NAME}}** unblocked and resuming work.

**Resolved:** {{RESOLUTION_DESCRIPTION}}
**Resumed:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
```

### Rule 4: Update Status When Creating PR

**When:** Agent creates pull request for review

**Actions:**
```bash
# 1. Update issue label — this is the ASSIGNEE's own dev->testing move.
#    The assignee never adds status:ai_review directly; the TEST RUNNER moves
#    status:testing -> status:ai_review on pass, or back to status:dev on fail.
gh issue edit {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --remove-label "status:dev" \
  --add-label "status:testing"

# 2. Move card on kanban
gh project item-edit \
  --project-id {{PROJECT_ID}} \
  --id {{ITEM_ID}} \
  --field-id {{STATUS_FIELD_ID}} \
  --value "Testing"

# 3. Link PR to issue (automatic if PR body contains "Closes #{{ISSUE_NUMBER}}")

# 4. Add comment with PR link
gh issue comment {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --body "🔍 Agent **{{AGENT_NAME}}** completed implementation and opened PR for review.

**Pull Request:** #{{PR_NUMBER}}
**Test Results:** {{TEST_SUMMARY}}
**Coverage:** {{COVERAGE}}%

Ready for review!"
```

**Required Fields Before Transition:**
- [ ] All acceptance criteria met
- [ ] All tests passing locally
- [ ] Code formatted and linted
- [ ] Documentation updated
- [ ] Toolchain verified
- [ ] PR created with proper template

### Rule 5: Update Status When Tests Fail

**When:** Tests fail during implementation or CI

**Actions:**
```bash
# 1. The TEST RUNNER moves the issue back: status:testing -> status:dev
gh issue edit {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --remove-label "status:testing" \
  --add-label "status:dev"

# 2. Add comment with failure details
gh issue comment {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --body "❌ Tests failed for task {{TASK_ID}}.

**Failed Tests:** {{FAILED_COUNT}}/{{TOTAL_COUNT}}
**Agent:** {{AGENT_NAME}}
**Log:** [View Log]({{LOG_URL}})

Agent is investigating and fixing failures."

# 3. Do NOT move to "AI Review" — this only happens after status:testing passes
# 4. Fix issues and re-run tests
# 5. When fixed, proceed with Rule 4
```

### Rule 6: Update Status When PR Approved and Merged

**When:** Pull request is approved and merged (usually by orchestrator or human reviewer)

**Transition flow:**
- Standard tasks: `status:ai_review` → `status:publish` → `status:complete`
- Big/critical tasks: `status:ai_review` → `status:human_review` → `status:publish` → `status:complete`

**Actions (Step 1 - Move to Publish after approval):**
```bash
# 1. Update issue label
gh issue edit {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --remove-label "status:ai_review" \
  --add-label "status:publish"

# 2. Move card on kanban
gh project item-edit \
  --project-id {{PROJECT_ID}} \
  --id {{ITEM_ID}} \
  --field-id {{STATUS_FIELD_ID}} \
  --value "Publish"
```

**Actions (Step 2 - Move to Complete after merge):**
```bash
# 1. Update issue label
gh issue edit {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --remove-label "status:publish" \
  --add-label "status:complete"

# 2. Move card on kanban
gh project item-edit \
  --project-id {{PROJECT_ID}} \
  --id {{ITEM_ID}} \
  --field-id {{STATUS_FIELD_ID}} \
  --value "Complete"

# 3. Close issue
gh issue close {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --comment "✅ Completed and merged in PR #{{PR_NUMBER}}.

**Merged:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**Duration:** {{ACTUAL_DURATION}}
**Agent:** {{AGENT_NAME}}"
```

**For big/critical tasks, add an intermediate human-review step:**
```bash
# After AI review passes, move to human review before merge
gh issue edit {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --remove-label "status:ai_review" \
  --add-label "status:human_review"

gh project item-edit \
  --project-id {{PROJECT_ID}} \
  --id {{ITEM_ID}} \
  --field-id {{STATUS_FIELD_ID}} \
  --value "Human Review"

# After human approval, proceed to publish (Step 1 above)
```

**Required Fields Before Transition:**
- [ ] PR approved by reviewer
- [ ] All CI checks passing
- [ ] No merge conflicts
- [ ] Branch up to date with base

### Rule 7: Handle PR Changes Requested

**When:** Reviewer requests changes on PR

**Actions:**
```bash
# 1. Update labels
gh issue edit {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --remove-label "status:ai_review" \
  --add-label "status:dev"

# 2. Move back to "Dev"
gh project item-edit \
  --project-id {{PROJECT_ID}} \
  --id {{ITEM_ID}} \
  --field-id {{STATUS_FIELD_ID}} \
  --value "Dev"

# 3. Add comment
gh issue comment {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --body "🔄 Changes requested on PR #{{PR_NUMBER}}.

Agent **{{AGENT_NAME}}** is addressing reviewer feedback.

**Requested Changes:**
{{REVIEWER_FEEDBACK}}"

# 4. Address feedback
# 5. When ready, return to Rule 4
```
