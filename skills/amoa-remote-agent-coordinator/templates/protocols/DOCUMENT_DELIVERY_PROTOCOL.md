# Document Delivery Protocol - Index

**Version:** 1.0
**Status:** MANDATORY
**Applies to:** All agents, orchestrators, and inter-agent communications

---

## Purpose

This protocol defines MANDATORY rules for sharing `.md` files between agents in the EOA (Emasoft Orchestrator Agent) system. It ensures context/token efficiency, maintains audit trails, and prevents message payload bloat.

---

## Table of Contents

This document is split into multiple parts for efficient loading. Read only the sections relevant to your current task.

### Part 1: Core Rules and Sender Process
**File:** [DOCUMENT_DELIVERY_PROTOCOL-part1-rules-sender.md](./DOCUMENT_DELIVERY_PROTOCOL-part1-rules-sender.md)

Contents:
- 1.1 Rule 1: NEVER Send .md Content Directly
- 1.2 Rule 2: Use GitHub Issue Comments
- 1.3 Delivery Process - Sender Steps
  - 1.3.1 Step 1: Create/Compile the .md File Locally
  - 1.3.2 Step 2: Upload to GitHub Issue as Comment Attachment
  - 1.3.3 Step 3: Get the Comment URL
  - 1.3.4 Step 4: Send AI Maestro Message with URL Only

**Read this when:** You need to send a document to another agent.

---

### Part 2: Recipient Process and ACK Requirements
**File:** [DOCUMENT_DELIVERY_PROTOCOL-part2-recipient-ack.md](./DOCUMENT_DELIVERY_PROTOCOL-part2-recipient-ack.md)

Contents:
- 2.1 Delivery Process - Recipient Steps
  - 2.1.1 Step 1: Receive AI Maestro Message
  - 2.1.2 Step 2: Download .md File from GitHub
  - 2.1.3 Step 3: Send ACK (MANDATORY)
  - 2.1.4 Step 4: Store in EOA Design Storage (MANDATORY)
  - 2.1.5 Step 5: Process the Document
- 2.2 ACK Requirements
  - 2.2.1 When ACK is MANDATORY
  - 2.2.2 When ACK is NOT Required

**Read this when:** You receive a document delivery message from another agent.

---

### Part 3: Orchestrator Enforcement
**File:** [DOCUMENT_DELIVERY_PROTOCOL-part3-orchestrator.md](./DOCUMENT_DELIVERY_PROTOCOL-part3-orchestrator.md)

Contents:
- 3.1 Validate Outgoing Messages (Python code)
- 3.2 Reject Invalid Messages
- 3.3 Track ACK Responses
- 3.4 Escalate Missing ACKs

**Read this when:** You are the orchestrator implementing protocol enforcement.

---

### Part 4: Message Examples and Document Types
**File:** [DOCUMENT_DELIVERY_PROTOCOL-part4-examples-types.md](./DOCUMENT_DELIVERY_PROTOCOL-part4-examples-types.md)

Contents:
- 4.1 Message Format Examples
  - 4.1.1 CORRECT: URL Only
  - 4.1.2 WRONG: Embedded Content
- 4.2 Document Types Table
- 4.3 Audit Trail
  - 4.3.1 Example Audit Chain

**Read this when:** You need to format a message correctly or understand document types.

---

### Part 5: Troubleshooting and Checklists
**File:** [DOCUMENT_DELIVERY_PROTOCOL-part5-troubleshooting.md](./DOCUMENT_DELIVERY_PROTOCOL-part5-troubleshooting.md)

Contents:
- 5.1 Troubleshooting
  - 5.1.1 Issue: Agent Did Not Receive Document
  - 5.1.2 Issue: GitHub Attachment Upload Failed
  - 5.1.3 Issue: Recipient Cannot Download Attachment
  - 5.1.4 Issue: ACK Timeout False Positive
- 5.2 Implementation Checklist
  - 5.2.1 Sender Checklist
  - 5.2.2 Recipient Checklist
  - 5.2.3 Orchestrator Checklist
- 5.3 Version History
- 5.4 Related Protocols
- 5.5 Storage Protocol Integration
- 5.6 Enforcement

**Read this when:** You encounter issues or need to verify implementation completeness.

---

## Quick Reference

| Role | Start With |
|------|------------|
| **Sender** | Part 1 (rules-sender) |
| **Recipient** | Part 2 (recipient-ack) |
| **Orchestrator** | Part 3 (orchestrator) |
| **Debugging** | Part 5 (troubleshooting) |

---

## Key Rules Summary

1. **NEVER** send .md content directly in messages (>500 chars = REJECTED)
2. **ALWAYS** upload to GitHub issue comment first
3. **ALWAYS** share via URL only
4. **ALWAYS** send ACK within 5 minutes for `document_delivery` type
5. **ALWAYS** store received documents in `design/received/` structure

---

## Related Protocols

- **DOCUMENT_STORAGE_PROTOCOL.md** - Standardized folder structure for downloaded documents (MANDATORY)
- **TASK_DELEGATION_PROTOCOL.md** - How to structure task delegation documents
- **PROGRESS_REPORTING_PROTOCOL.md** - How to format progress reports
- **GITHUB_INTEGRATION_PROTOCOL.md** - GitHub issue management guidelines

---

**END OF INDEX**
