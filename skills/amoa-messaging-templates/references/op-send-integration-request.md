# Operation: Send Integration Request

---
procedure: proc-request-pr-review
workflow-instruction: Step 20 - PR Review Request
operation-id: op-send-integration-request
---

## Purpose

Send a request from Orchestrator (EOA) to Integrator (EIA) for code integration or PR review.

## When to Use

- Requesting PR code review
- Requesting code quality assessment
- Requesting CI verification
- Requesting merge readiness check

## Prerequisites

- EOA has a PR number ready for integration/review
- EIA agent is available and running
- AI Maestro messaging system operational

## Steps

1. **Gather PR details**:
   - PR number
   - Repository (owner/repo)
   - Review type needed (code review, CI check, merge readiness)

2. **Prepare integration request message**:

   > **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

   ```json
   {
     "from": "eoa-main",
     "to": "eia-main",
     "subject": "Integration Request: PR #<number>",
     "priority": "high",
     "content": {
       "type": "request",
       "message": "Please perform <review_type> on PR #<number>",
       "data": {
         "pr_number": "<number>",
         "repo": "<owner/repo>",
         "review_type": "<code_review|ci_verification|merge_readiness>"
       }
     }
   }
   ```

3. **Send the message** using the `agent-messaging` skill with the prepared payload.

   **Verify**: confirm the message was delivered successfully.

4. **Log the request** in orchestration log

5. **Set polling schedule** to check for EIA response

## Output

| Field | Type | Description |
|-------|------|-------------|
| status | string | "sent" on success |
| message_id | string | Track this for response correlation |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| EIA not responding | Agent offline or hibernated | Check EIA status, escalate if needed |
| Invalid PR number | PR not found | Verify PR exists in repository |

## Example

Send an integration request using the `agent-messaging` skill:
- **Recipient**: `eia-main`
- **Subject**: "Integration Request: PR #456"
- **Content**: "Please perform code review and CI verification on PR #456"
- **Type**: `request`
- **Priority**: `high`
- **Data**: include `pr_number`, `repo`, and `review_type` fields

**Verify**: confirm message delivery.
