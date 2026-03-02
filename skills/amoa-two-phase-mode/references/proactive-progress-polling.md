# Proactive Progress Polling Protocol

**MANDATORY**: Every progress poll (10-15 minutes) MUST include all 6 questions.

## Contents

- 1. Why This Protocol Exists
  - 1.1 Never assume "no news is good news"
  - 1.2 Orchestrator must ACTIVELY ASK
- 2. The 6 Mandatory Poll Questions
  - 2.1 Question 1: Current progress
  - 2.2 Question 2: Next steps
  - 2.3 Question 3: Any issues or problems?
  - 2.4 Question 4: Anything unclear?
  - 2.5 Question 5: Unforeseen difficulties?
  - 2.6 Question 6: Need anything from me?
- 3. Poll Message Template
  - 3.1 Full template with all 6 questions
- 4. Response Actions
  - 4.1 Action table by response type
  - 4.2 Adapt-or-Escalate decision tree
- 5. Poll Tracking
  - 5.1 State file polling fields
  - 5.2 Poll history structure

---

## 1. Why This Protocol Exists

### 1.1 Never assume "no news is good news"

Remote agents may:
- Encounter unforeseen technical difficulties
- Have unclear requirements they didn't raise initially
- Be blocked but not proactively report it
- Discover issues that require changing the implementation approach
- Be making progress but in the wrong direction

**Silence does NOT mean everything is fine.**

### 1.2 Orchestrator must ACTIVELY ASK

The orchestrator is responsible for:
- Proactively checking in every 10-15 minutes
- Asking explicit questions about issues
- Detecting problems early
- Taking immediate action on reported issues

**WRONG approach:** Wait for agent to report problems
**CORRECT approach:** Ask explicitly about problems every poll

---

## 2. The 6 Mandatory Poll Questions

Every poll MUST include ALL of these questions:

### 2.1 Question 1: Current progress

```
1. **Current progress** (% complete, what's done)
```

Purpose: Understand where the agent is in the implementation.

### 2.2 Question 2: Next steps

```
2. **Next steps** (what you're working on now)
```

Purpose: Verify agent is on the right track.

### 2.3 Question 3: Any issues or problems?

```
3. **Are there any issues or problems?** (technical, environmental, dependencies)
```

Purpose: Detect technical blockers, environment issues, missing dependencies.

### 2.4 Question 4: Anything unclear?

```
4. **Is anything unclear?** (requirements, acceptance criteria, expected behavior)
```

Purpose: Detect requirement ambiguities or misunderstandings.

### 2.5 Question 5: Unforeseen difficulties?

```
5. **Any unforeseen difficulties?** (complexity higher than expected, missing info)
```

Purpose: Detect scope creep or underestimated complexity.

### 2.6 Question 6: Need anything from me?

```
6. **Do you need anything from me?** (documentation, clarification, decisions)
```

Purpose: Enable agent to request help proactively.

---

## 3. Poll Message Template

### 3.1 Full template with all 6 questions

```markdown
Subject: [POLL] Module: {module_name} - Progress Check #{poll_number}

## Status Request

Please provide:
1. **Current progress** (% complete, what's done)
2. **Next steps** (what you're working on now)

## MANDATORY Questions (Answer ALL)

3. **Are there any issues or problems?** (technical, environmental, dependencies)
4. **Is anything unclear?** (requirements, acceptance criteria, expected behavior)
5. **Any unforeseen difficulties?** (complexity higher than expected, missing info)
6. **Do you need anything from me?** (documentation, clarification, decisions)

If all is clear, respond: "No blockers. Proceeding as planned."

Expected response time: 5 minutes
```

**NEVER** send a poll without all 6 questions.

---

## 4. Response Actions

### 4.1 Action table by response type

| Agent Response | Orchestrator Action |
|----------------|---------------------|
| Reports issue | Provide solution or delegate research |
| Something unclear | Provide clarification immediately |
| Unforeseen difficulty | Evaluate: adapt approach or reassign |
| Needs documentation | Create/provide detailed docs |
| Needs decision | Make decision or escalate to user |
| Higher complexity | Adjust expectations, potentially split task |
| Blocked | Unblock immediately (highest priority) |
| "No blockers" | Acknowledge, schedule next poll |

### 4.2 The 3 Orchestrator Response Choices (MANDATORY RULE)

**CRITICAL:** When an implementer reports an unforeseen issue, the orchestrator has EXACTLY 3 possible responses. This rule MUST NEVER be skipped or violated.

#### Decision Tree

```
Agent reports unforeseen issue
         |
         v
What is the ROOT CAUSE of the issue?
         |
    +----+----+----+
    |         |         |
    v         v         v
CHOICE 1   CHOICE 2   CHOICE 3
```

#### Choice 1: Lack of Understanding (Orchestrator Explains)

**When to use:** Issue caused by:
- Lack of understanding of the specs
- Insufficiently detailed requirements
- Misinterpretation of acceptance criteria

**Action:**
1. Explain requirements again with more details
2. Clarify ambiguous points
3. Optionally provide expanded requirements documents
4. Let implementer continue

**Example:**
```
The issue you raised is due to unclear requirements on my part.

CLARIFICATION: When I said "token expiry", I meant the JWT access token,
not the refresh token. Access tokens expire in 15 minutes. Refresh tokens
expire in 7 days.

Please continue with this understanding.
```

---

#### Choice 2: Unforeseen Circumstances (Orchestrator Rewrites Requirements)

**When to use:** Issue caused by:
- Unforeseen circumstances NOT predicted in requirements
- Circumstances predicted but not planned by orchestrator
- Requirements WRITTEN BY ORCHESTRATOR found impossible to implement

**Action:**
1. STOP the implementer's current work
2. Write documentation for new requirements
3. Document the change of course with rationale
4. Create new plan superseding previous one
5. Hand new requirements to implementer using FULL verification protocol
6. Previous instructions are INVALIDATED

**Example:**
```
STOP CURRENT WORK.

After your report, I've determined that the original approach won't work.
I'm preparing updated requirements.

NEW REQUIREMENTS DOCUMENT: [see attached/linked]

CHANGES FROM PREVIOUS:
- Original: Use library X for OAuth
- New: Implement OAuth manually due to library incompatibility

This supersedes all previous instructions. Please wait for the new
assignment through the standard verification protocol.
```

---

#### Choice 3: Core Requirement Conflict (Escalate to User)

**When to use:** Issue caused by:
- Unforeseen circumstances not predicted/planned by USER
- Requirements WRITTEN DIRECTLY BY USER (marked as unchangeable CORE REQUIREMENTS)
- Core requirements found impossible to implement for any reason

**Action:**
1. STOP the implementer immediately
2. Document the issue clearly
3. Escalate to USER explicitly
4. Wait for USER's decision
5. Record USER's answer in state file (MANDATORY)
6. Only USER can decide to stay course or change core requirements

**Example to implementer:**
```
STOP WORK IMMEDIATELY.

You've encountered an issue with a CORE REQUIREMENT set by the user.
I cannot modify core requirements without user approval.

I am escalating this to the user now. Please standby.
```

**Example to user:**
```
ESCALATION: Core Requirement Conflict

Module: auth-core
Implementer: implementer-1

ISSUE: The implementer reports that the user-specified requirement
"All authentication must use SAML 2.0" conflicts with the also
user-specified requirement "Support mobile app authentication".
SAML 2.0 is not suitable for mobile apps.

OPTIONS:
A) Remove SAML 2.0 requirement, use OAuth2 for all auth
B) Keep SAML 2.0 for web, add OAuth2 for mobile (scope increase)
C) Other (please specify)

YOUR DECISION IS REQUIRED. Please respond with A, B, or C.
```

**Recording user decision (MANDATORY):**
```yaml
user_decisions:
  - timestamp: "2026-01-08T17:30:00+00:00"
    issue: "SAML vs OAuth for mobile"
    module: "auth-core"
    user_response: "B"
    recorded_verbatim: "Use B - keep SAML for web, add OAuth for mobile"
```

---

#### What the Orchestrator Does NOT Handle

**Minor issues are LEFT TO THE IMPLEMENTER:**
- Regular bugs that don't require architecture changes
- Code-level problems the implementer should solve
- Performance optimizations within existing design
- Test failures for implemented features
- Dependency version conflicts (unless structural)

**The orchestrator's time is precious.** Only the 3 cases above warrant orchestrator intervention. All other issues are the implementer's responsibility.

**Key principle:** Never leave an agent blocked on a structural issue. Take action immediately using one of the 3 choices. But do NOT waste orchestrator time on issues the implementer should solve independently.

---

## 5. Poll Tracking

### 5.1 State file polling fields

```yaml
active_assignments:
  - agent: "implementer-1"
    module: "auth-core"
    progress_polling:
      last_poll: "2026-01-08T16:30:00+00:00"
      poll_count: 3
      poll_history: [...]
      next_poll_due: "2026-01-08T16:45:00+00:00"
```

### 5.2 Poll history structure

```yaml
poll_history:
  - poll_number: 1
    timestamp: "2026-01-08T16:00:00+00:00"
    status: "responded"
    issues_reported: false
    clarifications_needed: false
  - poll_number: 2
    timestamp: "2026-01-08T16:15:00+00:00"
    status: "responded"
    issues_reported: true
    issue_description: "Unclear how auth tokens should expire"
    issue_resolved: true
    resolution: "Provided token expiry spec document"
  - poll_number: 3
    timestamp: "2026-01-08T16:30:00+00:00"
    status: "responded"
    issues_reported: false
    clarifications_needed: false
```

---

## Script Usage

Use `eoa_poll_agent.py` to manage polling:

```bash
# Send poll to specific agent
python3 eoa_poll_agent.py implementer-1

# Record poll response with issues
python3 eoa_poll_agent.py implementer-1 --record-response --issues "Token expiry unclear"

# Record poll response with issues resolved
python3 eoa_poll_agent.py implementer-1 --record-response --issues "Token expiry unclear" --resolved

# Record poll response with clarifications needed
python3 eoa_poll_agent.py implementer-1 --record-response --clarifications "Need edge case examples"

# View poll history
python3 eoa_poll_agent.py implementer-1 --history
```

---

## Polling Schedule

| Time Since Last Poll | Action |
|---------------------|--------|
| 0-10 min | Normal - no action needed |
| 10-15 min | Send progress poll |
| 15-20 min | Send urgent poll with reminder |
| 20+ min | Escalate - agent may be blocked or unresponsive |

**Best practice:** Set a timer for 15 minutes after each poll response. When timer fires, send next poll.

---

## Example Poll Exchange

**Orchestrator sends poll #3:**
```
Subject: [POLL] Module: auth-core - Progress Check #3

## Status Request

Please provide:
1. **Current progress** (% complete, what's done)
2. **Next steps** (what you're working on now)

## MANDATORY Questions (Answer ALL)

3. **Are there any issues or problems?**
4. **Is anything unclear?**
5. **Any unforeseen difficulties?**
6. **Do you need anything from me?**

If all is clear, respond: "No blockers. Proceeding as planned."
```

**Agent responds:**
```
1. Progress: 60% - Login endpoint complete, session management in progress
2. Next: Implementing token refresh logic

3. Issue: The token library has a different API than expected. Documentation shows v2 API but we have v3 installed.

4. Unclear: Should expired tokens return 401 or 403?

5. No unforeseen difficulties.

6. Need: Please clarify the HTTP status code for expired tokens.
```

**Orchestrator action:**
1. Answer question 4: "Use 401 for expired tokens with WWW-Authenticate header"
2. Resolve issue 3: "Use v3 API - here's the migration guide link"
3. Record poll response with issues resolved
4. Schedule next poll in 15 minutes

**Orchestrator responds:**
```
Subject: RE: [POLL] Module: auth-core - Answers

Thanks for the update.

**Q4 Answer:** Use HTTP 401 for expired tokens. Include WWW-Authenticate header with realm and error description.

**Issue 3 Resolution:** The v3 API is correct. Here's the migration guide: [link]. Key differences are in the refresh() method signature.

Continue with implementation. Next check-in: 15 minutes.
```
