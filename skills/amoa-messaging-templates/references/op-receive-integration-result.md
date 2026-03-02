# Operation: Receive Integration Result


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Steps](#steps)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example Response Format](#example-response-format)

---
procedure: proc-request-pr-review
workflow-instruction: Step 20 - PR Review Request
operation-id: op-receive-integration-result
---

## Purpose

Process integration/review results received from Integrator (EIA) after a review request.

## When to Use

- After sending integration request to EIA
- When polling reveals new message from EIA
- When inbox notification shows EIA response

## Prerequisites

- Integration request was previously sent to EIA
- Message from EIA received in inbox

## Steps

1. **Check inbox for EIA response** using the `agent-messaging` skill. Retrieve unread messages for your session and filter for messages from the EIA agent.

2. **Parse the response content**:
   - `content.type`: Should be "response"
   - `content.data.status`: "passed", "failed", "blocked"
   - `content.data.issues`: Array of issues found (if any)
   - `content.data.recommendation`: EIA's recommendation

3. **Handle by status**:

   | Status | Action |
   |--------|--------|
   | passed | Report to user, await merge decision |
   | failed | Delegate fixes to implementation subagent |
   | blocked | Escalate to user with details |

4. **Send acknowledgment** to EIA:

   > **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

   ```json
   {
     "from": "eoa-main",
     "to": "eia-main",
     "subject": "ACK: Integration Result PR #<number>",
     "priority": "low",
     "content": {
       "type": "acknowledgment",
       "message": "Received integration result for PR #<number>. Taking action: <action>."
     }
   }
   ```

5. **Log the result** in orchestration log

## Output

Parsed integration result with fields:
- `pr_number`: The reviewed PR
- `status`: passed/failed/blocked
- `issues`: List of issues (if any)
- `recommendation`: EIA's recommendation

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| No response | EIA still processing | Continue polling |
| Malformed response | Message format issue | Request clarification from EIA |
| Unknown status | Unexpected status value | Treat as "blocked" and escalate |

## Example Response Format

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "eia-main",
  "to": "eoa-main",
  "subject": "Integration Result: PR #456",
  "priority": "high",
  "content": {
    "type": "response",
    "message": "PR #456 code review complete. 2 issues found.",
    "data": {
      "pr_number": "456",
      "status": "failed",
      "issues": [
        "Missing error handling in process_data()",
        "Test coverage below 80% threshold"
      ],
      "recommendation": "delegate_fixes"
    }
  }
}
```
