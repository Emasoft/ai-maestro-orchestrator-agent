## Table of Contents
- [Standard Message Structure](#standard-message-structure)
- [Sending Messages](#sending-messages)
- [Checking Inbox](#checking-inbox)

---

## Standard Message Structure

All AI Maestro messages use this format:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

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

Send messages using the `agent-messaging` skill. Provide the JSON payload with recipient, subject, priority, and content fields as described above.

## Checking Inbox

Check your inbox using the `agent-messaging` skill. Retrieve all unread messages for your session and process the content of each message.

**Verify**: confirm all messages are delivered or received as expected.
