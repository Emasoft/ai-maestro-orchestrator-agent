# Agent Pre-Work Sync Checklist - Part 3: Environment & Registration

> This is Part 3 of the Agent Pre-Work Sync Checklist.
> See [AGENT_SYNC_CHECKLIST.md](./AGENT_SYNC_CHECKLIST.md) for the full index.

---

## 6. Local Environment Setup

### 6.1. Run Toolchain Setup Script
```bash
# Execute setup script from toolchain template
# Extract and run setup commands
awk '/## Setup Script/,/^## / {print}' "$TOOLCHAIN_PATH" | \
  grep -vE '^##' | \
  grep -vE '^```' | \
  grep -E '^[[:alnum:]]' > /tmp/setup-script.sh

chmod +x /tmp/setup-script.sh
bash /tmp/setup-script.sh

echo "Toolchain setup complete"
```

**Expected Output:**
- All tools installed successfully
- No error messages
- Environment ready

**If Failed:**
- Review error messages
- Check system requirements
- Request help from orchestrator
- Add issue to blocked state

### 6.2. Verify Tool Versions
```bash
# Extract required tools and versions from template
# Verify each tool is installed at correct version

# Example for Python
REQUIRED_PYTHON=$(awk '/python_version:/,/$/ {print $2}' "$TOOLCHAIN_PATH" | tr -d '"')
ACTUAL_PYTHON=$(python --version 2>&1 | cut -d' ' -f2)

if [ "$REQUIRED_PYTHON" == "$ACTUAL_PYTHON" ]; then
  echo "Python version matches: $ACTUAL_PYTHON"
else
  echo "Python version mismatch. Required: $REQUIRED_PYTHON, Actual: $ACTUAL_PYTHON"
  exit 1
fi

# Repeat for all required tools
```

**Expected Output:**
- All tool versions match requirements

**If Failed:**
- Install correct versions
- Update toolchain template if requirements changed
- Document version conflicts

### 6.3. Run Verification Commands
```bash
# Execute verification commands from toolchain template
awk '/## Verification/,/^## / {print}' "$TOOLCHAIN_PATH" | \
  grep -vE '^##' | \
  grep -vE '^```' | \
  grep -E '^[[:alnum:]]' > /tmp/verify-script.sh

chmod +x /tmp/verify-script.sh
bash /tmp/verify-script.sh

echo "Environment verification complete"
```

**Expected Output:**
- All verification checks pass
- No missing dependencies
- Build system works

**If Failed:**
- Review verification errors
- Fix missing dependencies
- Update toolchain if needed

**Checkpoint:**
- [ ] Toolchain setup script executed successfully
- [ ] All required tools installed at correct versions
- [ ] Verification commands pass
- [ ] Environment ready for development

---

## 7. Agent Registration

### 7.1. Register with Orchestrator

Use the `agent-messaging` skill to send a registration confirmation message to the orchestrator agent. The message should include:

- **Recipient**: `{{ORCHESTRATOR_AGENT}}`
- **Subject**: `Agent ready: {{TASK_ID}}`
- **Priority**: `normal`
- **Type**: `status`
- **Message body**: `Agent {{AGENT_NAME}} completed pre-work checklist and is ready to start task {{TASK_ID}}`
- **Metadata to include**: issue number (`{{ISSUE_NUMBER}}`), branch name (`$BRANCH_NAME`), platform (`{{PLATFORM}}`), session ID (`{{SESSION_ID}}`)

After sending, use the `agent-messaging` skill to verify the message was delivered successfully by checking sent messages.

**Expected Output:**
- Message delivered successfully via the AI Maestro messaging system (AMP)

**If Failed:**
- Verify the AI Maestro messaging system (AMP) is running and accessible
- Check orchestrator agent name is correct
- Use the `agent-messaging` skill to check connectivity

### 7.2. Update Issue Status to "In Progress"
```bash
# Update issue and project board
gh issue edit {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --remove-label "status:backlog" \
  --add-label "status:in-progress"

# Update project board
ITEM_ID=$(gh project item-list {{PROJECT_NUMBER}} \
  --owner {{GITHUB_OWNER}} \
  --format json | \
  jq -r ".items[] | select(.content.number == {{ISSUE_NUMBER}}) | .id")

STATUS_FIELD_ID=$(gh project field-list {{PROJECT_NUMBER}} \
  --owner {{GITHUB_OWNER}} \
  --format json | \
  jq -r '.[] | select(.name == "Status") | .id')

PROJECT_ID=$(gh project list --owner {{GITHUB_OWNER}} --format json | \
  jq -r ".projects[] | select(.number == {{PROJECT_NUMBER}}) | .id")

gh project item-edit \
  --project-id "$PROJECT_ID" \
  --id "$ITEM_ID" \
  --field-id "$STATUS_FIELD_ID" \
  --value "In Progress"

# Add start comment
gh issue comment {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --body "Agent **{{AGENT_NAME}}** started working on this task.

**Session:** {{SESSION_ID}}
**Branch:** \`$BRANCH_NAME\`
**Platform:** {{PLATFORM}}
**Started:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")"

echo "Issue status updated to In Progress"
```

**Expected Output:**
- Issue label changed to "status:in-progress"
- Project board updated
- Comment added to issue

**If Failed:**
- Check GitHub permissions
- Verify gh CLI authentication
- Review KANBAN_SYNC_PROTOCOL.md

**Checkpoint:**
- [ ] Registered with orchestrator
- [ ] Issue status updated to "In Progress"
- [ ] Project board synchronized
- [ ] Start comment added to issue

---

## Complete Checklist Summary

Copy this checklist to issue comments when starting work:

```markdown
## Pre-Work Checklist Complete

### GitHub
- [x] Issue exists and is accessible
- [x] Issue assigned to agent
- [x] Status label: status:in-progress
- [x] Priority label: priority:{{PRIORITY}}
- [x] Platform label: platform:{{PLATFORM}}
- [x] Type label: type:{{TYPE}}
- [x] Issue linked to project board
- [x] Project status: In Progress

### Toolchain
- [x] Toolchain template exists and valid
- [x] Setup script executed successfully
- [x] All tools installed: {{TOOL_LIST}}
- [x] Tool versions verified
- [x] Environment verification passed

### Development
- [x] Feature branch created: `{{BRANCH_NAME}}`
- [x] Branch pushed to remote
- [x] Local environment ready

### Synchronization
- [x] Registered with orchestrator
- [x] Issue status updated
- [x] Kanban board synchronized

**Ready to begin implementation.**

**Agent:** {{AGENT_NAME}}
**Session:** {{SESSION_ID}}
**Platform:** {{PLATFORM}}
**Started:** {{START_TIME}}
```

---

## Next Steps

Continue to [Part 4: Automation & Troubleshooting](./AGENT_SYNC_CHECKLIST-part4-automation-troubleshooting.md) for:
- Automation Script
- Troubleshooting Guide
- Post-Work Checklist
