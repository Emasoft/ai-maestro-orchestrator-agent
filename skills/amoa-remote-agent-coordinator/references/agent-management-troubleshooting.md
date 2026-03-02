# Troubleshooting Reference

This document covers common issues and solutions for agent management commands.

---

## Contents

- 8.1 Registration Issues
  - 8.1.1 AI Maestro session not found
  - 8.1.2 Duplicate agent ID
  - 8.1.3 Invalid agent type
- 8.2 Assignment Issues
  - 8.2.1 Module not found
  - 8.2.2 Agent not registered
  - 8.2.3 Agent overloaded
  - 8.2.4 Message delivery failed
- 8.3 Polling Issues
  - 8.3.1 No response from agent
  - 8.3.2 Agent reports being blocked
  - 8.3.3 Progress stalled
- 8.4 Communication Issues
  - 8.4.1 AI Maestro connection failed
  - 8.4.2 GitHub API errors
  - 8.4.3 Message format errors
- 8.5 State File Issues
- 8.6 Recovery Procedures

---

## 8.1 Registration Issues

### 8.1.1 AI Maestro Session Not Found

**Symptom**:
```
Error: Session 'helper-agent-generic' not found in AI Maestro.
```

**Causes**:
1. Session is not running
2. Session name is misspelled
3. AI Maestro service is down
4. Session recently started, not yet registered

**Solutions**:

1. **Verify session is running**: Use the `agent-messaging` skill to query the agent registry and list all registered session names.

2. **Check for typos**:
   - Session names are case-sensitive
   - Use full name (e.g., `helper-agent-generic` not `generic`)

3. **Restart AI Maestro if needed**: Use the `agent-messaging` skill to perform a health check on the AI Maestro service.

4. **Wait and retry**:
   - New sessions may take a few seconds to register
   - Wait 10 seconds and try again

### 8.1.2 Duplicate Agent ID

**Symptom**:
```
Error: Agent ID 'implementer-1' already exists.
```

**Causes**:
1. Agent was already registered
2. Using same ID for different session

**Solutions**:

1. **Check existing registrations**:
   ```bash
   /orchestration-status
   ```

2. **Use different ID**:
   ```bash
   /register-agent ai implementer-2 --session helper-agent-python
   ```

3. **Deregister old agent** (if it's no longer valid):
   - Edit state file manually
   - Remove agent from `registered_agents`

### 8.1.3 Invalid Agent Type

**Symptom**:
```
Error: Invalid agent type 'bot'. Must be 'ai' or 'human'.
```

**Solution**:
Only use `ai` or `human`:
```bash
/register-agent ai implementer-1 --session helper-agent-generic
/register-agent human dev-alice
```

---

## 8.2 Assignment Issues

### 8.2.1 Module Not Found

**Symptom**:
```
Error: Module 'auth-core' not found in decomposed modules.
```

**Causes**:
1. Module decomposition not done yet
2. Module name misspelled
3. Module was renamed

**Solutions**:

1. **Check available modules**:
   ```bash
   /orchestration-status
   ```

2. **Run decomposition first**:
   ```bash
   /decompose-modules
   ```

3. **Verify module name**:
   - Module names are case-sensitive
   - Check the exact name in the decomposition output

### 8.2.2 Agent Not Registered

**Symptom**:
```
Error: Agent 'implementer-1' is not registered.
```

**Solution**:
Register the agent first:
```bash
/register-agent ai implementer-1 --session helper-agent-generic
```

### 8.2.3 Agent Overloaded

**Symptom**:
```
Error: Agent 'implementer-1' already has an active assignment (oauth-google).
```

**Solutions**:

1. **Wait for completion**:
   - Check progress with `/check-agents --agent implementer-1`
   - Wait until current assignment completes

2. **Assign to different agent**:
   ```bash
   /assign-module auth-core implementer-2
   ```

3. **Reassign current task**:
   ```bash
   /reassign-module oauth-google implementer-2
   /assign-module auth-core implementer-1
   ```

### 8.2.4 Message Delivery Failed

**Symptom**:
```
Error: Failed to deliver assignment message to 'implementer-1'.
AI Maestro error: Connection refused.
```

**Causes**:
1. AI Maestro service is down
2. Network issues
3. Session disconnected after registration

**Solutions**:

1. **Check AI Maestro service**: Use the `agent-messaging` skill to perform a health check.

2. **Verify session is still active**: Use the `agent-messaging` skill to query the agent registry and check if the session (e.g., `helper-agent-generic`) is registered and active.

3. **Retry assignment**:
   - Wait a moment and try again
   - If persistent, ask user to restart the session

---

## 8.3 Polling Issues

### 8.3.1 No Response from Agent

**Symptom**:
Agent does not respond to progress poll within expected time.

**Escalation timeline**:
| Time | Action |
|------|--------|
| 5 min | Send reminder |
| 10 min | Send urgent follow-up |
| 15 min | Try alternative communication |
| 20 min | Mark as unresponsive |
| 30 min | Consider reassignment |

**Solutions**:

1. **Send reminder**:
   ```markdown
   Subject: [URGENT] No response to progress poll

   I sent a progress poll 10 minutes ago and haven't received a response.
   Please respond immediately with your status.
   ```

2. **Check session status**: Use the `agent-messaging` skill to query the agent registry and check the status of the specific session.

3. **Consider reassignment** if unresponsive for >30 minutes

### 8.3.2 Agent Reports Being Blocked

**Symptom**:
Agent response: "I'm blocked because..."

**Actions**:

1. **Increase polling frequency** to every 5 minutes
2. **Provide immediate assistance**:
   - Answer questions
   - Provide missing information
   - Make decisions
3. **If you cannot unblock**:
   - Escalate to user
   - Consider reassignment

### 8.3.3 Progress Stalled

**Symptom**:
Agent reports same progress percentage multiple times.

**Investigation**:

1. **Ask directly**:
   ```markdown
   I notice progress has been at 40% for the last 2 polls.
   Is there an issue? Please be specific about any blockers.
   ```

2. **Look for hidden blockers**:
   - Agent may not recognize they're blocked
   - Ask about specific difficulties

3. **Consider scope issues**:
   - Maybe task is more complex than estimated
   - Consider splitting the module

---

## 8.4 Communication Issues

### 8.4.1 AI Maestro Connection Failed

**Symptom**:
```
Error: Cannot connect to AI Maestro messaging system
```

**Solutions**:

1. **Check if service is running**: Use the `agent-messaging` skill to perform a health check on the AI Maestro service.

2. **Restart AI Maestro** (ask user):
   ```bash
   # User should run this in the AI Maestro terminal
   npm start  # or appropriate command
   ```

3. **Check port**:
   - Default port is 23000
   - Check if something else is using it

### 8.4.2 GitHub API Errors

**Symptom**:
```
Error: GitHub API error: 403 Forbidden
```

**Causes**:
1. Authentication failed
2. Rate limit exceeded
3. Insufficient permissions

**Solutions**:

1. **Re-authenticate**:
   ```bash
   gh auth login
   ```

2. **Check rate limit**:
   ```bash
   gh api rate_limit
   ```

3. **Verify permissions**:
   ```bash
   gh repo view --json permissions
   ```

### 8.4.3 Message Format Errors

**Symptom**:
```
Error: Invalid message format
```

**Common mistakes**:
1. Content not properly structured as JSON
2. Missing required fields
3. Wrong content type structure

**Correct format**:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "helper-agent-generic",
  "subject": "[TASK] Module: auth-core",
  "priority": "high",
  "content": {
    "type": "assignment",
    "message": "..."
  }
}
```

---

## 8.5 State File Issues

### Corrupted State File

**Symptom**:
```
Error: Failed to parse state file. Invalid YAML.
```

**Solution**:
1. Backup current state file
2. Check for YAML syntax errors
3. Fix or restore from backup

### Missing State File

**Symptom**:
```
Error: State file not found.
```

**Solution**:
```bash
/init-orchestration
```

### Inconsistent State

**Symptom**:
Module shows as "assigned" but agent shows as "available".

**Solution**:
1. Manually reconcile state file
2. Update both module status and agent status to match
3. Verify with `/orchestration-status`

---

## 8.6 Recovery Procedures

### Recovery: Reset Agent Assignment

```yaml
# 1. Update agent status
registered_agents:
  ai_agents:
    - agent_id: "implementer-1"
      status: "available"
      current_assignment: null

# 2. Update module status
modules:
  auth-core:
    status: "pending"
    assigned_to: null

# 3. Remove from active assignments
active_assignments:
  # Remove the assignment entry
```

### Recovery: Clean Failed Assignment

1. Mark assignment as failed in state file
2. Notify agent assignment is cancelled
3. Reset agent status to available
4. Reset module status to pending
5. Retry assignment or assign to different agent

### Recovery: Reset Polling State

```yaml
polling:
  poll_count: 0
  last_poll: null
  next_poll_due: "now"
```

---

## Summary

Most issues fall into categories:
1. **Connection issues** - Check services are running
2. **State inconsistencies** - Manually reconcile state file
3. **Agent issues** - Verify sessions, consider reassignment
4. **Format issues** - Check message/command formats

When in doubt:
1. Check `/orchestration-status` for current state
2. Verify services are running
3. Escalate to user if unable to resolve
