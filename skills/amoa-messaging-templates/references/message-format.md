## Table of Contents
- [Standard Message Structure](#standard-message-structure)
- [Sending Messages](#sending-messages)
- [Checking Inbox](#checking-inbox)

---

## Standard Message Structure

All AI Maestro messages use this format:

> **Note**: Use the `amp-send` CLI to send messages. The JSON structure below shows the message content.

```json
{
  "from": "<sender-agent-name>",
  "to": "<recipient-agent-name>",
  "subject": "<short-subject-line>",
  "priority": "high|normal|low",
  "content": {
    "type": "request|response|notification|acknowledgment",
    "message": "<human-readable-message>",
    "data": {
      "task_id": "<optional-task-identifier>",
      "pr_number": "<optional-pr-number>",
      "issue_number": "<optional-issue-number>",
      "status": "<optional-status>"
    }
  }
}
```

## Sending Messages

Send messages using the `amp-send` CLI. Provide the JSON payload as the body, with recipient, subject, priority, and content fields as described above.

## Checking Inbox

Check your inbox using `amp-inbox`. Retrieve all unread messages for your session and process the content of each message with `amp-read`.

**Verify**: confirm all messages are delivered or received as expected.
