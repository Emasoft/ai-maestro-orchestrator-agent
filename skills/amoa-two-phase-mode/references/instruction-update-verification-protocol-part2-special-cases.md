# Instruction Update Verification Protocol - Part 2: Special Cases and Troubleshooting


## Contents

- [5. Special Cases](#5-special-cases)
  - [5.1 Minor clarifications (abbreviated flow)](#51-minor-clarifications-abbreviated-flow)
- [Minor Clarification](#minor-clarification)
  - [5.2 Major design changes (extended flow)](#52-major-design-changes-extended-flow)
- [Additional Assessment for Major Change](#additional-assessment-for-major-change)
  - [5.3 User requirement changes (full re-verification)](#53-user-requirement-changes-full-re-verification)
- [FULL STOP](#full-stop)
- [User Decision](#user-decision)
- [New Requirements](#new-requirements)
- [6. Configuration Feedback Loop](#6-configuration-feedback-loop)
  - [6.1 When implementer needs configuration changes](#61-when-implementer-needs-configuration-changes)
  - [6.2 Orchestrator integration of config feedback](#62-orchestrator-integration-of-config-feedback)
  - [6.3 Template for config feedback request](#63-template-for-config-feedback-request)
- [Configuration Requirement](#configuration-requirement)
- [Configuration Provided](#configuration-provided)
- [Integration Notes](#integration-notes)
  - [6.4 State file tracking for config requests](#64-state-file-tracking-for-config-requests)
- [7. Script Usage](#7-script-usage)
- [8. Troubleshooting](#8-troubleshooting)
  - [Problem: Implementer Continues Without Acknowledging Update](#problem-implementer-continues-without-acknowledging-update)
  - [Problem: Implementer Says Change Is Not Feasible](#problem-implementer-says-change-is-not-feasible)
  - [Problem: Too Many Updates Fragmenting Work](#problem-too-many-updates-fragmenting-work)
  - [Problem: Implementer Requests Excessive Configuration](#problem-implementer-requests-excessive-configuration)
  - [Problem: Update Verification Taking Too Long](#problem-update-verification-taking-too-long)
  - [Problem: Conflicting Updates Sent](#problem-conflicting-updates-sent)
- [9. Integration with Other Protocols](#9-integration-with-other-protocols)

---

**Parent document:** [instruction-update-verification-protocol.md](instruction-update-verification-protocol.md)

This part covers:
- Special cases (minor clarifications, major changes, user requirement changes)
- Configuration feedback loop
- Script usage
- Troubleshooting
- Integration with other protocols

---

## 5. Special Cases

### 5.1 Minor clarifications (abbreviated flow)

For **minor clarifications** that don't change the fundamental requirement:
- Skip full feasibility assessment
- Request simple ACK: "Understood, will incorporate"
- Track as update but mark as "minor_clarification"

**Examples of minor clarifications:**
- Spelling out an acronym
- Confirming a specific value (e.g., "timeout is 30 seconds, not 30 minutes")
- Adding a small detail that doesn't change approach

**Template for minor clarifications:**
```markdown
Subject: [CLARIFICATION] Module: {module_name} - Quick Note

## Minor Clarification

{clarification_content}

Please reply with: "ACK - understood" to confirm.

No need to stop work for this - incorporate when you get to that part.
```

### 5.2 Major design changes (extended flow)

For **major design changes** that significantly alter the implementation:
- Require full feasibility assessment
- Request detailed impact analysis from implementer
- May require re-estimation of scope
- Consider if partial work should be discarded

**Examples of major design changes:**
- Changing database technology
- Switching authentication method
- Restructuring API endpoints
- Adding new integration dependency

**Additional questions for major changes:**
```markdown
## Additional Assessment for Major Change

6. **How much of your current work is affected?**
   - Percentage of work that needs revision: [X%]
   - Specific components affected: [list]

7. **Should any completed work be discarded?**
   - No, all work is still valid
   - Yes, these parts should be redone: [list]

8. **Revised scope assessment**
   - Original effort remaining: [estimate]
   - With this change: [new estimate]
```

### 5.3 User requirement changes (full re-verification)

For **user requirement changes** (core requirements modified by user decision):
- Treat as NEW task assignment
- Run FULL Instruction Verification Protocol (8 steps)
- Clear previous verification status
- Document that user authorized the change

**Template for user requirement changes:**
```markdown
Subject: [USER-CHANGE] Module: {module_name} - Core Requirement Modified

## FULL STOP

A core requirement has been changed by the user.

## User Decision

{user_decision_details}

## New Requirements

This is a significant change. You will receive new instructions through the standard Instruction Verification Protocol.

Please:
1. STOP all work immediately
2. Document your current progress
3. Wait for new assignment message

Your next message will be a fresh task assignment with full verification.
```

---

## 6. Configuration Feedback Loop

### 6.1 When implementer needs configuration changes

The implementer may discover during implementation that they need:
- Environment variables not provided
- API keys or credentials
- Tool configurations
- Dependency versions
- Build settings
- Test fixtures or data

**This is normal and expected.** The orchestrator must handle config feedback efficiently.

### 6.2 Orchestrator integration of config feedback

When implementer requests configuration:

1. **Receive request** - Implementer specifies what config is needed
2. **Validate request** - Is this a legitimate config need?
3. **Integrate config** - Add to central configuration (`design/config/`)
4. **Update templates** - Modify project templates if needed
5. **Send confirmation** - Provide config to implementer with documentation
6. **Track in state** - Record config addition for future reference

**Configuration integration flow:**

```
IMPLEMENTER                               ORCHESTRATOR
     |                                         |
     |  "I need config for X"                  |
     |---------------------------------------->|
     |                                         |
     |                    Validates request    |
     |                    Updates design/config|
     |                    Updates templates    |
     |                                         |
     |  "Config added. Details: [X]"           |
     |<----------------------------------------|
     |                                         |
     |  Implementer continues with config      |
     |                                         |
```

### 6.3 Template for config feedback request

**Implementer to Orchestrator:**
```markdown
Subject: [CONFIG-NEEDED] Module: {module_name} - Configuration Request

## Configuration Requirement

**What I need:** {description_of_config_need}

**Why I need it:** {rationale}

**Suggested format:**
```
{suggested_config_format}
```

**Blocking:** {yes_blocked|no_can_continue}

Please provide this configuration or advise on alternative approach.
```

**Orchestrator to Implementer:**
```markdown
Subject: RE: [CONFIG-NEEDED] Module: {module_name} - Configuration Provided

## Configuration Provided

**Request:** {what_was_requested}

**Provided:**
```
{config_content}
```

**Location:** Added to `design/config/{config_file}.md`

**Documentation:** {brief_explanation_of_config}

## Integration Notes

{any_notes_on_how_to_use_this_config}

Continue with implementation.
```

### 6.4 State file tracking for config requests

```yaml
config_feedback:
  - request_id: "config-001"
    module: "auth-core"
    agent: "implementer-1"
    requested_at: "2026-01-08T18:00:00+00:00"
    description: "Need Redis connection string"
    status: "provided"
    provided_at: "2026-01-08T18:05:00+00:00"
    config_file: "design/config/environment.md"
    config_key: "REDIS_URL"
  - request_id: "config-002"
    module: "auth-core"
    agent: "implementer-1"
    requested_at: "2026-01-08T18:30:00+00:00"
    description: "Need OAuth client credentials"
    status: "pending"
    provided_at: null
    config_file: null
    config_key: null
```

---

## 7. Script Usage

Use `eoa_update_verification.py <!-- TODO: Script not implemented -->` to manage update verification:

```bash
# Send update notification
python3 eoa_update_verification.py <!-- TODO: Script not implemented --> send implementer-1 --type requirement_change \
  --description "Added 2FA support"

# Record receipt confirmation
python3 eoa_update_verification.py <!-- TODO: Script not implemented --> record-receipt implementer-1 update-001

# Record feasibility assessment
python3 eoa_update_verification.py <!-- TODO: Script not implemented --> record-feasibility implementer-1 update-001 \
  --clear --feasible --no-concerns

# Record feasibility with concerns
python3 eoa_update_verification.py <!-- TODO: Script not implemented --> record-feasibility implementer-1 update-001 \
  --concerns "Need Redis credentials"

# Resolve concerns
python3 eoa_update_verification.py <!-- TODO: Script not implemented --> resolve-concerns implementer-1 update-001 \
  --resolution "Redis credentials provided in design/config"

# Authorize resume
python3 eoa_update_verification.py <!-- TODO: Script not implemented --> authorize-resume implementer-1 update-001

# View update history
python3 eoa_update_verification.py <!-- TODO: Script not implemented --> history implementer-1
```

---

## 8. Troubleshooting

### Problem: Implementer Continues Without Acknowledging Update

**Symptoms**: Progress report received but no update acknowledgment.

**Solution**:
1. Send STOP message immediately
2. Re-send update with explicit "HALT REQUIRED" header
3. Do NOT accept progress reports until update verified
4. If repeated, escalate as discipline issue
5. Document in GitHub Issue

### Problem: Implementer Says Change Is Not Feasible

**Symptoms**: Feasibility assessment returns "No, because..."

**Solution**:
1. Evaluate the blocker objectively
2. If blocker is valid:
   - Modify requirements if possible
   - Escalate to user if core requirement
   - Consider reassigning if agent lacks capability
3. If blocker is incorrect:
   - Provide counter-evidence
   - Offer technical guidance
   - May indicate agent doesn't have required skills

### Problem: Too Many Updates Fragmenting Work

**Symptoms**: Multiple updates sent before previous ones verified.

**Solution**:
1. Batch related updates into single message
2. Establish "update windows" - consolidate changes
3. Major updates should be rare (< 1 per module per day)
4. If frequent updates needed, requirements may be underspecified
5. Consider pausing implementation for spec stabilization

### Problem: Implementer Requests Excessive Configuration

**Symptoms**: Many config requests, feels like scope creep.

**Solution**:
1. Evaluate if requests are legitimate
2. If excessive:
   - Check if original spec was complete
   - Implementer may be over-engineering
   - May need clearer boundaries
3. If legitimate:
   - Improve central config documentation
   - Add to template for future modules
4. Track patterns - repeated requests indicate spec gaps

### Problem: Update Verification Taking Too Long

**Symptoms**: Multiple rounds of clarification, implementer stuck.

**Solution**:
1. Check if update is too complex for single message
2. Consider scheduling synchronous clarification session
3. Break update into smaller, incremental changes
4. If pattern continues, spec communication may need improvement
5. Document lessons learned for future updates

### Problem: Conflicting Updates Sent

**Symptoms**: Update A contradicts previously sent Update B.

**Solution**:
1. Immediately send CORRECTION notice
2. Clearly state which update is valid
3. Provide reconciled instructions
4. Apologize for confusion - this is orchestrator error
5. Review process to prevent future conflicts
6. Add reconciliation tracking to state file

---

## 9. Integration with Other Protocols

This protocol integrates with:

| Protocol | Integration Point |
|----------|------------------|
| **Instruction Verification Protocol** | User requirement changes trigger full re-verification |
| **Proactive Progress Polling** | Next poll scheduled after resume authorization |
| **Change Notification Protocol** | Toolchain updates trigger update verification |
| **Bug Reporting Protocol** | Bugs may trigger requirement updates |
| **Handoff Protocols** | Updates must follow ACK format |

---

**Related Documents:**
- [Instruction Verification Protocol](instruction-verification-protocol.md) - Initial task assignment verification
- [Proactive Progress Polling](proactive-progress-polling.md) - Regular status checks
- [Central Configuration](../../eoa-remote-agent-coordinator/references/central-configuration.md) - Config management

---

**Return to:** [Instruction Update Verification Protocol (Index)](instruction-update-verification-protocol.md)
