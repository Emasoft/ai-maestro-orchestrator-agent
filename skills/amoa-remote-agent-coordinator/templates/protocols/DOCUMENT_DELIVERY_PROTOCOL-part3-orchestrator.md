# Document Delivery Protocol - Part 3: Orchestrator Enforcement

**Parent:** [DOCUMENT_DELIVERY_PROTOCOL.md](./DOCUMENT_DELIVERY_PROTOCOL.md)

---

## 3.1 Validate Outgoing Messages

The orchestrator MUST enforce this protocol by validating all outgoing messages:

```python
def validate_outgoing_message(message):
    """
    Validate message doesn't contain raw .md content.

    Returns: (valid: bool, error: str)
    """
    content = message.get('content', {})

    # Check if content has type document_delivery
    if content.get('type') == 'document_delivery':
        # MUST have github_comment_url
        if 'github_comment_url' not in content:
            return False, "document_delivery requires github_comment_url"

        # MUST NOT have large markdown content
        if 'message' in content and len(content['message']) > 500:
            return False, "document_delivery must use URL, not embedded content"

        return True, None

    # For other message types, check for embedded markdown
    message_text = str(content.get('message', ''))

    # Detect markdown headers, lists, code blocks
    markdown_indicators = ['##', '###', '```', '- ', '* ', '1. ']
    markdown_count = sum(message_text.count(ind) for ind in markdown_indicators)

    # If >500 chars and multiple markdown elements, likely embedded doc
    if len(message_text) > 500 and markdown_count > 5:
        return False, "Message appears to contain embedded document. Use document_delivery protocol."

    return True, None
```

---

## 3.2 Reject Invalid Messages

```python
valid, error = validate_outgoing_message(message)
if not valid:
    raise ProtocolViolation(f"REJECTED: {error}")
```

---

## 3.3 Track ACK Responses

```python
def track_document_delivery(task_id, recipient, sent_time):
    """
    Track document delivery and expected ACK window.
    Note: ACK window is for operational tracking, not development deadlines.
    """
    delivery_tracking[task_id] = {
        'recipient': recipient,
        'sent_time': sent_time,
        'ack_expected_by': sent_time + timedelta(minutes=5),  # Operational window, not deadline
        'ack_received': False
    }

def process_ack(task_id):
    """
    Mark ACK as received.
    """
    if task_id in delivery_tracking:
        delivery_tracking[task_id]['ack_received'] = True
```

---

## 3.4 Escalate Missing ACKs

```python
def check_ack_timeouts():
    """
    Check for ACK timeouts and escalate.
    """
    now = datetime.now()

    for task_id, tracking in delivery_tracking.items():
        if not tracking['ack_received'] and now > tracking['ack_expected_by']:
            escalate_missing_ack(task_id, tracking['recipient'])

def escalate_missing_ack(task_id, recipient):
    """
    Escalate missing ACK to orchestrator.
    """
    print(f"⚠️ ESCALATION: No ACK received for {task_id} from {recipient}")

    # Send reminder
    send_message(
        to=recipient,
        subject=f"[REMINDER] ACK Required: {task_id}",
        priority="urgent",
        content={
            "type": "reminder",
            "task_id": task_id,
            "message": f"ACK not received for {task_id}. Please confirm document receipt."
        }
    )

    # Notify user/orchestrator
    notify_orchestrator(f"Agent {recipient} did not ACK document delivery for {task_id}")
```

---

**Previous:** [Part 2: Recipient Process and ACK Requirements](./DOCUMENT_DELIVERY_PROTOCOL-part2-recipient-ack.md)

**Next:** [Part 4: Message Examples and Document Types](./DOCUMENT_DELIVERY_PROTOCOL-part4-examples-types.md)
