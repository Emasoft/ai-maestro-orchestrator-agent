# Instruction Update Verification Protocol


## Contents

- [Document Structure](#document-structure)
- [Quick Reference: Contents](#quick-reference-contents)
  - [Part 1: Core Protocol](#part-1-core-protocol)
  - [Part 2: Special Cases and Troubleshooting](#part-2-special-cases-and-troubleshooting)
- [Protocol Overview](#protocol-overview)
  - [Purpose](#purpose)
  - [Key Principle](#key-principle)
  - [When to Use](#when-to-use)
  - [The 5-Step Flow (Summary)](#the-5-step-flow-summary)
  - [Critical Rules](#critical-rules)
- [Related Documents](#related-documents)
- [Start Reading](#start-reading)

---

**MANDATORY**: This protocol MUST be executed whenever the orchestrator sends UPDATED instructions, design changes, or new requirements to an implementer who is ALREADY working on a task.

---

## Document Structure

This protocol is split into multiple parts for easier navigation:

| Part | File | Contents |
|------|------|----------|
| **Part 1** | [instruction-update-verification-protocol-part1-core-protocol.md](instruction-update-verification-protocol-part1-core-protocol.md) | Core protocol: triggers, 5-step flow, templates, tracking |
| **Part 2** | [instruction-update-verification-protocol-part2-special-cases.md](instruction-update-verification-protocol-part2-special-cases.md) | Special cases, config feedback, scripts, troubleshooting |

---

## Quick Reference: Contents

### Part 1: Core Protocol

**[instruction-update-verification-protocol-part1-core-protocol.md](instruction-update-verification-protocol-part1-core-protocol.md)**

- **1. When This Protocol Applies**
  - 1.1 Triggers for this protocol (requirement changes, design updates, scope adjustments, etc.)
  - 1.2 Distinction from Initial Verification (initial assignment vs. mid-implementation changes)
  - 1.3 Distinction from Regular Polling (scheduled checks vs. triggered updates)

- **2. The 5-Step Update Verification Flow**
  - 2.1 Step 1: Send Update Notification (what changed, why, impact, invalidations)
  - 2.2 Step 2: Request Confirmation of Receipt (implementer PAUSES work)
  - 2.3 Step 3: Request Feasibility Assessment (clear? feasible? concerns?)
  - 2.4 Step 4: Address Concerns (loop until all resolved)
  - 2.5 Step 5: Authorize Resume (explicit resume authorization)

- **3. Message Templates**
  - 3.1 Update Notification Template
  - 3.2 Feasibility Assessment Request Template
  - 3.3 Concern Resolution Template
  - 3.4 Resume Authorization Template

- **4. Tracking Update Verification**
  - 4.1 State file fields (YAML structure for tracking updates)
  - 4.2 Status values (pending_receipt, pending_feasibility, verified, etc.)

### Part 2: Special Cases and Troubleshooting

**[instruction-update-verification-protocol-part2-special-cases.md](instruction-update-verification-protocol-part2-special-cases.md)**

- **5. Special Cases**
  - 5.1 Minor clarifications (abbreviated flow with simple ACK)
  - 5.2 Major design changes (extended flow with impact analysis)
  - 5.3 User requirement changes (full re-verification with new assignment)

- **6. Configuration Feedback Loop**
  - 6.1 When implementer needs configuration changes
  - 6.2 Orchestrator integration of config feedback
  - 6.3 Template for config feedback request
  - 6.4 State file tracking for config requests

- **7. Script Usage**
  - Commands for `eoa_update_verification.py <!-- TODO: Script not implemented -->`
  - Send updates, record receipts, resolve concerns, authorize resume

- **8. Troubleshooting**
  - Implementer continues without acknowledging update
  - Implementer says change is not feasible
  - Too many updates fragmenting work
  - Implementer requests excessive configuration
  - Update verification taking too long
  - Conflicting updates sent

- **9. Integration with Other Protocols**
  - Links to Instruction Verification Protocol
  - Links to Proactive Progress Polling
  - Links to Change Notification Protocol

---

## Protocol Overview

### Purpose

This protocol ensures that when the orchestrator sends CHANGES to an implementer who is already working:

1. The implementer **receives** the update
2. The implementer **understands** what changed
3. The implementer **can implement** the changes
4. Any **concerns are resolved** before work continues
5. Work only **resumes with explicit authorization**

### Key Principle

**DO NOT** assume the implementer will automatically incorporate updates. Updates can be missed, misunderstood, or conflict with ongoing work. This protocol guarantees verification.

### When to Use

| Situation | Protocol to Use |
|-----------|-----------------|
| Assigning a NEW task | [Instruction Verification Protocol](instruction-verification-protocol.md) |
| Changing instructions for ONGOING task | **This protocol** |
| Regular status check | [Proactive Progress Polling](proactive-progress-polling.md) |

### The 5-Step Flow (Summary)

```
ORCHESTRATOR                              IMPLEMENTER
     |                                         |
     |  1. Send Update Notification            |
     |---------------------------------------->|
     |                                         |
     |  2. Request Confirmation of Receipt     |
     |---------------------------------------->|
     |                                         |
     |  3. Request Feasibility Assessment      |
     |---------------------------------------->|
     |                                         |
     |  4. Implementer Responds                |
     |<----------------------------------------|
     |                                         |
     |  If concerns: Address them (loop)       |
     |---------------------------------------->|
     |                                         |
     |  5. Authorize Resume                    |
     |---------------------------------------->|
     |                                         |
```

### Critical Rules

1. **PAUSE implementer work** before processing updates
2. **INVALIDATE explicitly** any superseded instructions
3. **DO NOT authorize resume** with unresolved concerns
4. **TRACK all updates** in state file for audit trail
5. **DOCUMENT in GitHub Issue** if escalation needed

---

## Related Documents

- [Instruction Verification Protocol](instruction-verification-protocol.md) - Initial task assignment verification
- [Proactive Progress Polling](proactive-progress-polling.md) - Regular status checks
- [Central Configuration](../../eoa-remote-agent-coordinator/references/central-configuration.md) - Config management

---

## Start Reading

**Start with:** [Part 1: Core Protocol](instruction-update-verification-protocol-part1-core-protocol.md)
