# Instruction Update Verification Protocol - Part 1: Core Protocol


## Contents

- [1. When This Protocol Applies](#1-when-this-protocol-applies)
  - [1.1 Triggers for this protocol](#11-triggers-for-this-protocol)
  - [1.2 Distinction from Initial Verification](#12-distinction-from-initial-verification)
  - [1.3 Distinction from Regular Polling](#13-distinction-from-regular-polling)
- [2. The 5-Step Update Verification Flow](#2-the-5-step-update-verification-flow)
  - [2.1 Step 1: Send Update Notification](#21-step-1-send-update-notification)
  - [2.2 Step 2: Request Confirmation of Receipt](#22-step-2-request-confirmation-of-receipt)
  - [2.3 Step 3: Request Feasibility Assessment](#23-step-3-request-feasibility-assessment)
  - [2.4 Step 4: Address Concerns](#24-step-4-address-concerns)
  - [2.5 Step 5: Authorize Resume](#25-step-5-authorize-resume)
- [3. Message Templates](#3-message-templates)
  - [3.1 Update Notification Template](#31-update-notification-template)
- [PAUSE CURRENT WORK](#pause-current-work)
- [What Changed](#what-changed)
- [Why This Changed](#why-this-changed)
- [Impact on Your Work](#impact-on-your-work)
- [Invalidated Instructions](#invalidated-instructions)
- [Required Action](#required-action)
  - [3.2 Feasibility Assessment Request Template](#32-feasibility-assessment-request-template)
- [MANDATORY: Answer All Questions](#mandatory-answer-all-questions)
  - [3.3 Concern Resolution Template](#33-concern-resolution-template)
- [Your Concerns and My Responses](#your-concerns-and-my-responses)
- [Clarifications Provided](#clarifications-provided)
- [Configuration Changes Made](#configuration-changes-made)
- [Updated Understanding Check](#updated-understanding-check)
  - [3.4 Resume Authorization Template](#34-resume-authorization-template)
- [UPDATE VERIFICATION COMPLETE](#update-verification-complete)
- [Summary of Changes to Incorporate](#summary-of-changes-to-incorporate)
- [Invalidated Instructions (Reminder)](#invalidated-instructions-reminder)
- [Current Valid Instructions](#current-valid-instructions)
- [Resume Work](#resume-work)
- [4. Tracking Update Verification](#4-tracking-update-verification)
  - [4.1 State file fields](#41-state-file-fields)
  - [4.2 Status values](#42-status-values)

---

**Parent document:** [instruction-update-verification-protocol.md](instruction-update-verification-protocol.md)

This part covers:
- When this protocol applies
- The 5-step update verification flow
- Message templates
- Tracking update verification

---

## 1. When This Protocol Applies

### 1.1 Triggers for this protocol

This protocol is triggered when the orchestrator sends **ANY** of the following to an implementer who is already working:

| Trigger | Description | Example |
|---------|-------------|---------|
| **Requirement change** | Modification to acceptance criteria | "Add 2FA support to login" |
| **Design update** | Changed technical approach | "Use Redis instead of in-memory cache" |
| **Spec clarification** | Detailed expansion of ambiguous specs | "Token expiry means access token only" |
| **Scope adjustment** | Added or removed features | "Remove social login, add LDAP" |
| **Priority change** | Reordering of implementation priority | "Do auth before API, not after" |
| **Toolchain update** | Changed dependencies or tools | "Upgrade to library v3" |
| **Integration change** | Modified external interfaces | "New endpoint format from partner API" |

**Key distinction:** This is for MID-IMPLEMENTATION changes, not initial assignments.

### 1.2 Distinction from Initial Verification

| Protocol | When Used | Focus |
|----------|-----------|-------|
| **Instruction Verification Protocol** | Before work starts | Full understanding of original requirements |
| **Instruction UPDATE Verification Protocol** | During work | Understanding of CHANGES and their impact |

The initial verification establishes baseline understanding. This protocol ensures CHANGES are understood in context of ongoing work.

### 1.3 Distinction from Regular Polling

| Protocol | When Used | Focus |
|----------|-----------|-------|
| **Proactive Progress Polling** | Every 10-15 minutes | Status check, issue detection |
| **Instruction UPDATE Verification Protocol** | After sending updates | Verification of specific changes |

Regular polling is scheduled. This protocol is triggered by specific update events.

---

## 2. The 5-Step Update Verification Flow

```
ORCHESTRATOR                              IMPLEMENTER
     |                                         |
     |  1. Send Update Notification            |
     |  (What changed, why, impact)            |
     |---------------------------------------->|
     |                                         |
     |  2. Request Confirmation of Receipt     |
     |  "Please confirm you received this      |
     |   update and PAUSE current work"        |
     |---------------------------------------->|
     |                                         |
     |  3. Request Feasibility Assessment      |
     |  "Is this change clear and feasible?    |
     |   Do you need more info? Any concerns?" |
     |---------------------------------------->|
     |                                         |
     |  4. Implementer Responds                |
     |  (Clear/unclear, feasible/concerns)     |
     |<----------------------------------------|
     |                                         |
     |  If concerns: Address them (loop)       |
     |  If clear: Proceed to step 5            |
     |---------------------------------------->|
     |                                         |
     |  5. Authorize Resume                    |
     |  "You may resume with these changes"    |
     |---------------------------------------->|
     |                                         |
     |  Implementer Resumes Work               |
     |                                         |
```

### 2.1 Step 1: Send Update Notification

Send AI Maestro message using the `agent-messaging` skill with:
- **WHAT changed** - Specific requirements/design elements modified
- **WHY it changed** - Rationale for the change
- **IMPACT assessment** - What parts of current work are affected
- **INVALIDATION notice** - What previous instructions are superseded

**CRITICAL:** Include explicit statement that previous related instructions are INVALIDATED.

### 2.2 Step 2: Request Confirmation of Receipt

Require implementer to:
1. Acknowledge receipt of the update
2. PAUSE current work immediately
3. Review the changes before continuing

**DO NOT** let implementer continue with old instructions while processing update.

### 2.3 Step 3: Request Feasibility Assessment

Ask the implementer explicitly:
1. **Is this change clear?** (Do you understand what's being asked?)
2. **Is this feasible?** (Can you implement this with current resources/time?)
3. **Do you need more information?** (What's missing or unclear?)
4. **Any concerns?** (Technical issues, conflicts with other work, etc.)
5. **Any configuration needs?** (Do you need config changes from orchestrator?)

### 2.4 Step 4: Address Concerns

If implementer raises concerns:
1. **Technical concerns:** Provide solutions or adjust requirements
2. **Clarity concerns:** Explain in more detail with examples
3. **Feasibility concerns:** Negotiate scope or provide alternatives
4. **Configuration needs:** Integrate their requirements (see Part 2, Section 6)

**Loop until all concerns addressed.** Do not authorize resume with unresolved concerns.

### 2.5 Step 5: Authorize Resume

Send explicit authorization:
```
UPDATE VERIFICATION COMPLETE.
You may resume work with the following changes incorporated:
- [List specific changes]

Previous instruction for [X] is INVALIDATED.
New instruction is [Y].

Resume work.
```

---

## 3. Message Templates

### 3.1 Update Notification Template

```markdown
Subject: [UPDATE] Module: {module_name} - Requirement Change

## PAUSE CURRENT WORK

Please STOP what you are doing and read this update carefully.

## What Changed

**Previous:** {previous_requirement}
**New:** {new_requirement}

## Why This Changed

{rationale_for_change}

## Impact on Your Work

{assessment_of_affected_work}

## Invalidated Instructions

The following previous instructions are now INVALID:
- {invalidated_instruction_1}
- {invalidated_instruction_2}

## Required Action

1. Acknowledge receipt of this update
2. Review the changes
3. Reply with your feasibility assessment (see next section)

Do NOT continue with previous instructions until this update is verified.
```

### 3.2 Feasibility Assessment Request Template

```markdown
Subject: [UPDATE-VERIFY] Module: {module_name} - Feasibility Check

## MANDATORY: Answer All Questions

Please assess this update and answer ALL of the following:

1. **Is this change clear?**
   - Yes, I understand exactly what's being asked
   - Partially, I need clarification on: [specify]
   - No, I don't understand: [specify]

2. **Is this feasible with your current work?**
   - Yes, I can incorporate this change
   - Partially, but it requires: [specify impact]
   - No, because: [specify blockers]

3. **Do you need more information?**
   - No, I have everything I need
   - Yes, I need: [specify]

4. **Any concerns or conflicts?**
   - No concerns
   - Yes: [specify concerns]

5. **Do you need any configuration changes from me?**
   - No configuration needed
   - Yes, I need: [specify config requirements]

Reply with your assessment. Do NOT resume work until authorized.
```

### 3.3 Concern Resolution Template

```markdown
Subject: RE: [UPDATE-VERIFY] Module: {module_name} - Addressing Concerns

## Your Concerns and My Responses

**Concern 1:** {implementer_concern_1}
**Resolution:** {orchestrator_resolution_1}

**Concern 2:** {implementer_concern_2}
**Resolution:** {orchestrator_resolution_2}

## Clarifications Provided

{additional_clarifications}

## Configuration Changes Made

{config_changes_if_any}

## Updated Understanding Check

Please confirm:
1. Your concerns are resolved
2. You understand the updated requirements
3. You are ready to resume work

Reply with confirmation or additional concerns.
```

### 3.4 Resume Authorization Template

```markdown
Subject: [UPDATE-VERIFIED] Module: {module_name} - Resume Work

## UPDATE VERIFICATION COMPLETE

Your understanding is confirmed. You may resume work.

## Summary of Changes to Incorporate

- {change_1}
- {change_2}

## Invalidated Instructions (Reminder)

Do NOT follow these previous instructions:
- {invalidated_1}

## Current Valid Instructions

Follow these instructions instead:
- {current_valid_instruction_1}
- {current_valid_instruction_2}

## Resume Work

You may now continue implementation with these changes incorporated.

Next progress poll: 15 minutes.
```

---

## 4. Tracking Update Verification

### 4.1 State file fields

```yaml
active_assignments:
  - agent: "implementer-1"
    module: "auth-core"
    status: "working"
    instruction_updates:
      - update_id: "update-001"
        sent_at: "2026-01-08T17:30:00+00:00"
        type: "requirement_change"
        description: "Added 2FA support requirement"
        verification_status: "verified"
        receipt_confirmed: true
        feasibility_confirmed: true
        concerns_raised: 1
        concerns_resolved: 1
        resume_authorized_at: "2026-01-08T17:45:00+00:00"
      - update_id: "update-002"
        sent_at: "2026-01-08T18:00:00+00:00"
        type: "design_update"
        description: "Changed to Redis for caching"
        verification_status: "pending_feasibility"
        receipt_confirmed: true
        feasibility_confirmed: false
        concerns_raised: 0
        concerns_resolved: 0
        resume_authorized_at: null
```

### 4.2 Status values

| Status | Meaning | Next Action |
|--------|---------|-------------|
| `pending_receipt` | Update sent, awaiting confirmation | Wait for implementer ACK |
| `pending_feasibility` | Receipt confirmed, awaiting assessment | Wait for feasibility response |
| `resolving_concerns` | Concerns raised, addressing them | Provide resolutions |
| `verified` | All checks passed, resume authorized | Monitor progress |
| `rejected` | Implementer cannot implement change | Escalate or redesign |

---

**Continue to:** [Part 2: Special Cases and Troubleshooting](instruction-update-verification-protocol-part2-special-cases.md)
