# Agent Communication Formats


## Contents

- [Table of Contents](#table-of-contents)
- [1. Message Format Overview](#1-message-format-overview)
  - [1.1 When sending messages between agents](#11-when-sending-messages-between-agents)
  - [1.2 Required fields for all messages](#12-required-fields-for-all-messages)
- [2. Status Report Formats](#2-status-report-formats)
  - [2.1 If reporting task completion](#21-if-reporting-task-completion)
  - [2.2 If reporting task failure](#22-if-reporting-task-failure)
  - [2.3 If reporting blockers](#23-if-reporting-blockers)
- [3. Request Formats](#3-request-formats)
  - [3.1 When requesting status updates](#31-when-requesting-status-updates)
  - [3.2 When requesting clarification](#32-when-requesting-clarification)
  - [3.3 When requesting resources](#33-when-requesting-resources)
- [4. Acknowledgment Formats](#4-acknowledgment-formats)
  - [4.1 If acknowledging task delegation](#41-if-acknowledging-task-delegation)
  - [4.2 If acknowledging message receipt](#42-if-acknowledging-message-receipt)
- [See Also](#see-also)

---

This document defines standardized message formats for inter-agent communication in the emasoft multi-agent system.

---

## Table of Contents

- 1. Message Format Overview
  - 1.1 When sending messages between agents
  - 1.2 Required fields for all messages
- 2. Status Report Formats
  - 2.1 If reporting task completion
  - 2.2 If reporting task failure
  - 2.3 If reporting blockers
- 3. Request Formats
  - 3.1 When requesting status updates
  - 3.2 When requesting clarification
  - 3.3 When requesting resources
- 4. Acknowledgment Formats
  - 4.1 If acknowledging task delegation
  - 4.2 If acknowledging message receipt

---

## 1. Message Format Overview

### 1.1 When sending messages between agents

All inter-agent messages MUST follow this structure:

```
[TYPE] identifier - brief_description
Details: (optional) additional_context
```

### 1.2 Required fields for all messages

| Field | Description | Required |
|-------|-------------|----------|
| TYPE | Message type (STATUS, REQUEST, ACK, etc.) | Yes |
| identifier | Task ID or message reference | Yes |
| description | Brief summary (< 50 chars) | Yes |
| Details | Additional context | No |

---

## 2. Status Report Formats

### 2.1 If reporting task completion

```
[DONE] task-id - result_summary
Details: docs_dev/report-filename.md
```

### 2.2 If reporting task failure

```
[FAILED] task-id - failure_reason
Blocker: specific_issue
Next: what_is_needed
```

### 2.3 If reporting blockers

```
[BLOCKED] task-id - blocker_description
Waiting on: dependency_or_resource
```

---

## 3. Request Formats

### 3.1 When requesting status updates

```
[REQUEST] task-id - status_update_needed
Context: why_status_is_needed
```

### 3.2 When requesting clarification

```
[CLARIFY] task-id - question
Options: [option1, option2, option3]
```

### 3.3 When requesting resources

```
[RESOURCE] resource-type - specific_request
Purpose: why_needed
```

---

## 4. Acknowledgment Formats

### 4.1 If acknowledging task delegation

```
[ACK] task-id - RECEIVED|QUEUED|REJECTED
Understanding: 1-line summary of task
```

### 4.2 If acknowledging message receipt

```
[ACK] message-ref - NOTED
Action: what_will_be_done
```

---

## See Also

- [inter-agent-protocols.md](inter-agent-protocols.md) - Communication protocols
- [templates-for-humans.md](templates-for-humans.md) - Human-facing templates
