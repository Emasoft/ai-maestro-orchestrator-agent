---
procedure: proc-execute-task
workflow-instruction: Step 17 - Task Execution
operation: verify-aimaestro-availability
---

# Operation: Verify AI Maestro Availability

## Purpose

Verify that the AI Maestro messaging system is running and accessible before attempting task delegation.

## When to Use

- Before any task delegation to remote agents
- At session start when orchestrator begins work
- After network connectivity issues
- Before overnight autonomous operation

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| AI Maestro AMP | Messaging system | Yes (AMP handles routing automatically) |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| availability_status | Boolean | True if API is healthy |
| error_message | String | Error details if unavailable |

## Steps

### Step 1: Check API Health Endpoint

Use the `agent-messaging` skill to perform a health check on the AI Maestro service. Verify it returns a healthy status (HTTP 200).

**Verify**: confirm the health check response indicates the service is operational.

### Step 2: Verify Agent Registry Access

Use the `agent-messaging` skill to query the agent registry and list all registered agents. Verify at least one remote agent is registered.

**Verify**: confirm the agent count is greater than zero.

### Step 3: Test Message Send Capability

Optionally, send a self-test ping message using the `agent-messaging` skill:
- **Recipient**: your own session name (self-ping)
- **Subject**: "Health Check Ping"
- **Content**: "Self-test"
- **Type**: `ping`
- **Priority**: `low`

**Verify**: confirm the message was sent successfully.

## Success Criteria

- [ ] Health endpoint returns HTTP 200
- [ ] Agent registry is accessible
- [ ] At least one remote agent is registered (for delegation)

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Connection refused | AI Maestro not running | Start AI Maestro service |
| HTTP 500 | AI Maestro internal error | Check AI Maestro logs |
| No agents registered | Agents not onboarded | Complete agent onboarding first |

## Related Operations

- op-send-task-delegation
- op-poll-agent-progress
