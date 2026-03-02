# Agent Replacement Troubleshooting Reference

## Contents

- [7.1 ECOS Communication Failures](#71-ecos-communication-failures)
- [7.2 Context Compilation Failures](#72-context-compilation-failures)
- [7.3 Handoff Generation Failures](#73-handoff-generation-failures)
- [7.4 GitHub Integration Failures](#74-github-integration-failures)
- [7.5 New Agent Issues](#75-new-agent-issues)

---

## 7.1 ECOS Communication Failures

### 7.1.1 Notification Not Received

**Symptoms:**
- ECOS sent replacement notification but orchestrator did not receive it
- Agent failed but no replacement triggered

**Diagnostic Steps:**

Use the `agent-messaging` skill to:
- Check your inbox for messages with content type "agent_replacement"
- Perform a health check on the AI Maestro service
- Query the agent registry to verify your session is registered

**Solutions:**

| Cause | Solution |
|-------|----------|
| AI Maestro down | Restart AI Maestro service |
| Session not registered | Re-register orchestrator session |
| Message filtered | Check message filters, adjust if needed |
| Network issue | Verify localhost connectivity |

**Manual Recovery:**

Send a resend request using the `agent-messaging` skill:
- **Recipient**: `ecos-controller`
- **Subject**: "[EOA] Request: Resend Replacement Notification"
- **Content**: "Did not receive replacement notification for agent implementer-1. Please resend."
- **Type**: `request`, **Priority**: `high`

**Verify**: confirm message delivery.

### 7.1.2 Confirmation Not Delivered

**Symptoms:**
- Orchestrator sent confirmation but ECOS did not receive it
- ECOS keeps sending reminders

**Diagnostic Steps:**

Use the `agent-messaging` skill to:
- List sent messages and filter for "Replacement Complete" subjects
- Query the agent registry to verify the ECOS session exists

**Solutions:**

| Cause | Solution |
|-------|----------|
| Wrong ECOS session name | Use correct "ecos-controller" session |
| Message queue full | Wait and retry |
| ECOS offline | Wait for ECOS to come online |

---

## 7.2 Context Compilation Failures

### 7.2.1 State File Missing

**Symptoms:**
- Cannot find orchestrator state file
- No assignment records found

**Diagnostic Steps:**

```bash
# Check expected location
ls -la "$CLAUDE_PROJECT_DIR/design/state.yaml"

# Check alternative locations
find "$CLAUDE_PROJECT_DIR" -name "state.yaml" -o -name "*.state.yaml"

# Check if design directory exists
ls -la "$CLAUDE_PROJECT_DIR/design/"
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| State file deleted | Reconstruct from GitHub Issues |
| Wrong project directory | Verify CLAUDE_PROJECT_DIR |
| Never initialized | Create minimal state from known assignments |

**Manual Reconstruction:**

```bash
# Reconstruct state from GitHub
ISSUES=$(gh issue list --assignee "@failed-agent" --json number,title,state,labels)

# Create minimal state
cat > "$CLAUDE_PROJECT_DIR/design/state.yaml" << EOF
active_assignments:
$(echo "$ISSUES" | jq -r '.[] | "  - module: \"issue-" + (.number|tostring) + "\"\n    github_issue: \"#" + (.number|tostring) + "\"\n    status: \"unknown\""')
EOF
```

### 7.2.2 Git History Unavailable

**Symptoms:**
- Cannot access agent's git branch
- Cannot determine what files were modified

**Diagnostic Steps:**

```bash
# Check if git repo exists
git status

# List all branches
git branch -a

# Check remote connectivity
git remote -v
git ls-remote origin
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| Branch deleted | Check reflog: `git reflog` |
| Not a git repo | Skip git analysis, flag gap |
| Remote only | Fetch: `git fetch --all` |
| Network issue | Use cached data, flag gap |

**Workaround:**

```markdown
## Technical Context

**Git Analysis**: UNAVAILABLE
**Reason**: Could not access agent's branch

**Action for New Agent**:
1. Ask failed agent for any uncommitted work (if contactable)
2. Start from last known good commit on main
3. Reference GitHub Issue comments for progress hints
```

### 7.2.3 AI Maestro History Gaps

**Symptoms:**
- Cannot retrieve message history
- Missing clarifications or decisions

**Diagnostic Steps:**

Use the `agent-messaging` skill to:
- Test the AI Maestro API by retrieving the most recent message
- Check the total message count for your session

**Solutions:**

| Cause | Solution |
|-------|----------|
| Messages archived | Check archive location |
| Database issue | Restart AI Maestro |
| API changed | Update API calls |

**Workaround:**

```markdown
## Communication History

**AI Maestro History**: PARTIALLY AVAILABLE
**Gaps**: Messages before {{DATE}} unavailable

**Known Clarifications (from GitHub):**
- {{CLARIFICATION_FROM_ISSUE_COMMENTS}}

**Action for New Agent**:
If you encounter ambiguity not covered here, ask the orchestrator.
```

---

## 7.3 Handoff Generation Failures

### 7.3.1 Template Errors

**Symptoms:**
- Handoff generation script fails
- Template variables not substituted

**Diagnostic Steps:**

```bash
# Test template rendering
python3 -c "
from string import Template
t = Template(open('handoff_template.md').read())
print(t.safe_substitute({'AGENT_ID': 'test'}))
"
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| Missing template | Copy from skill references |
| Syntax error | Fix template syntax |
| Missing variable | Add default value |

### 7.3.2 Incomplete Data

**Symptoms:**
- Handoff missing sections
- Required fields empty

**Solutions:**

| Missing Data | Fallback |
|--------------|----------|
| Progress % | Use "unknown", flag for new agent |
| Last status | Quote last poll response if available |
| Checkpoint | Default to "beginning of task" |
| Files modified | State "unknown", instruct agent to explore |

**Partial Handoff Template:**

```markdown
## IMPORTANT: Incomplete Handoff

This handoff was generated with incomplete data. The following sections may be missing or inaccurate:

{{LIST_OF_GAPS}}

**New Agent Instructions:**
1. Acknowledge these gaps in your ACK
2. Investigate missing information
3. Report discoveries to orchestrator
4. Proceed with caution
```

---

## 7.4 GitHub Integration Failures

### 7.4.1 API Rate Limits

**Symptoms:**
- GitHub commands return rate limit error
- Cannot update issues

**Diagnostic Steps:**

```bash
# Check rate limit status
gh api rate_limit | jq '.rate'
```

**Solutions:**

| Remaining Requests | Action |
|--------------------|--------|
| 0 | Wait for reset (check `reset` timestamp) |
| < 10 | Prioritize critical operations |
| Normal | Continue |

**Workaround:**

```markdown
## GitHub Updates

**Issue Reassignment**: DELAYED
**Reason**: API rate limit exceeded
**Scheduled Retry**: {{RESET_TIME}}

**Manual Workaround**:
New agent should self-assign issue #{{NUMBER}} when possible.
```

### 7.4.2 Permission Denied

**Symptoms:**
- Cannot edit issues
- Cannot add comments

**Diagnostic Steps:**

```bash
# Check authentication
gh auth status

# Check repo permissions
gh api repos/{owner}/{repo} | jq '.permissions'
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| Token expired | Re-authenticate: `gh auth login` |
| Insufficient scope | Re-auth with correct scopes |
| Not collaborator | Request access or use user with access |

### 7.4.3 Project Not Found

**Symptoms:**
- Cannot find GitHub Project
- Project board operations fail

**Diagnostic Steps:**

```bash
# List projects
gh project list --owner OWNER

# Check project number
gh api graphql -f query='
query {
  organization(login: "OWNER") {
    projectsV2(first: 10) {
      nodes { number title }
    }
  }
}'
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| Wrong project ID | Find correct ID with list command |
| Project deleted | Skip project updates, document manually |
| Organization project | Use organization queries |

---

## 7.5 New Agent Issues

### 7.5.1 ACK Timeout

**Symptoms:**
- New agent does not acknowledge handoff
- Reminders not effective

**Diagnostic Steps:**

Use the `agent-messaging` skill to:
- Verify the new agent session (e.g., `helper-agent-2`) exists in the agent registry
- Check if the agent received the handoff message by listing messages sent to that agent

**Solutions:**

| Cause | Solution |
|-------|----------|
| Session not registered | Wait for agent to register |
| Agent crashed | Notify ECOS, request different agent |
| Message not read | Send urgent priority message |
| Agent offline | Wait or request different agent |

**Escalation Path:**

After 3 reminders, send an escalation using the `agent-messaging` skill:
- **Recipient**: `ecos-controller`
- **Subject**: "[EOA-ESCALATE] Replacement Agent Not Responding"
- **Content**: "Replacement agent helper-agent-2 has not acknowledged handoff after 3 reminders. Please provide alternative agent."
- **Type**: `escalation`, **Priority**: `urgent`
- **Data**: include `failed_original_agent`, `failed_replacement_agent`

**Verify**: confirm escalation delivery.

### 7.5.2 Requirements Confusion

**Symptoms:**
- New agent's ACK shows misunderstanding
- Questions indicate confusion about requirements

**Solutions:**

1. **Provide clarification immediately**
2. **Update handoff document** with clearer requirements
3. **Re-send handoff notification** with updated URL
4. **Schedule synchronous check-in** after agent starts

**Clarification Template:**

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "helper-agent-2",
  "subject": "[CLARIFICATION] Requirements for auth-core module",
  "priority": "high",
  "content": {
    "type": "clarification",
    "message": "Based on your questions, here are clarifications...",
    "clarifications": [
      {
        "question": "Your question here",
        "answer": "Clear answer",
        "reference": "See handoff section X"
      }
    ]
  }
}
```

### 7.5.3 Environment Setup Failures

**Symptoms:**
- New agent cannot set up required environment
- Build/test commands fail

**Solutions:**

| Issue | Solution |
|-------|----------|
| Missing dependencies | Provide explicit install commands |
| Wrong versions | Specify exact version requirements |
| Platform differences | Document platform-specific setup |
| Credentials needed | Provide secure credential sharing |

**Environment Setup Debug:**

```markdown
## Environment Verification

Run these commands and report any failures:

```bash
# Check Python version
python3 --version  # Expected: 3.8+

# Check dependencies
pip list | grep -E "PyYAML|requests"

# Check GitHub CLI
gh auth status

# Test AI Maestro connection
Use the agent-messaging skill to perform a health check on the AI Maestro service
```

If any fail, report the error output to the orchestrator.
```

---

## Emergency Procedures

### Complete System Failure

If multiple systems fail during replacement:

1. **Document current state** manually
2. **Preserve all handoff materials** locally
3. **Alert user** via all available channels
4. **Wait** for user guidance

### Data Loss Recovery

If critical data is lost:

1. **Check backups**: `ls $CLAUDE_PROJECT_DIR/design/*.bak*`
2. **Check git history**: `git log --all --full-history -- design/state.yaml`
3. **Reconstruct from GitHub**: Use issues/PRs as source of truth
4. **Document gaps**: Clearly flag what's unknown

---

**Version**: 1.0.0
**Last Updated**: 2026-02-02
