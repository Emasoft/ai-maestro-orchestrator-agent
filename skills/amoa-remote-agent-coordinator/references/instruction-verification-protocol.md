# Instruction Verification Protocol Reference

This document describes the MANDATORY Instruction Verification Protocol that must be executed before any agent begins implementation.

---

## Contents

- 1.1 Why Verification is Mandatory
- 1.2 The 8-Step Verification Process
  - 1.2.1 Send assignment with verification request
  - 1.2.2 Agent repeats key requirements
  - 1.2.3 Verify repetition is correct
  - 1.2.4 Handle incorrect repetition
  - 1.2.5 Agent asks clarifying questions
  - 1.2.6 Answer all questions completely
  - 1.2.7 Confirm final understanding
  - 1.2.8 Authorize implementation
- 1.3 Verification Message Template
- 1.4 Common Verification Failures
- 1.5 State Tracking During Verification

---

## 1.1 Why Verification is Mandatory

**The Problem**: Remote agents (especially AI agents) may misunderstand requirements. If they begin implementation with incorrect understanding:
- Wasted effort on wrong implementation
- Need to redo work from scratch
- Delayed project timeline
- Potential conflicts with other modules

**The Solution**: Force the agent to demonstrate understanding BEFORE implementation by repeating requirements in their own words.

**Key Principle**: Never assume an agent understands. Always verify explicitly.

---

## 1.2 The 8-Step Verification Process

### 1.2.1 Send Assignment with Verification Request

When you send the assignment message using the `agent-messaging` skill, include the verification request:

```markdown
## MANDATORY: Instruction Verification

Before you begin implementation, please:

1. **Repeat the key requirements** in your own words (3-5 bullet points)
2. **List any questions** you have about the requirements
3. **Confirm your understanding** of the acceptance criteria

I will verify your understanding before authorizing implementation.

Reply with your understanding summary.
```

**Do NOT authorize implementation yet.** Wait for the agent's response.

### 1.2.2 Agent Repeats Key Requirements

The agent should respond with something like:

```markdown
## My Understanding

Based on the assignment, here are the key requirements:

1. Implement JWT token generation with RS256 algorithm
2. Token expiry should be configurable, default 1 hour
3. Include user ID and role in token payload
4. Provide a validate_token function that returns user info
5. Handle token expiry gracefully with clear error messages

## Questions

1. Should the token include the user's email address?
2. What should happen if the private key file is missing?

## Acceptance Criteria Understanding

- Unit tests for token generation and validation
- Integration test with mock user data
- Error handling for all edge cases
```

### 1.2.3 Verify Repetition is Correct

Compare the agent's summary against the actual requirements:

**Checklist:**
- [ ] All key requirements mentioned?
- [ ] No misunderstandings?
- [ ] No missing critical details?
- [ ] Acceptance criteria understood correctly?

If ALL checkboxes pass, proceed to step 1.2.5 (questions).

If ANY checkbox fails, proceed to step 1.2.4 (corrections).

### 1.2.4 Handle Incorrect Repetition

Send corrections:

```markdown
## Corrections Required

Your understanding has some issues:

**Incorrect:**
- "Token expiry should be configurable, default 1 hour"
- Actual: Default expiry is 24 hours, not 1 hour

**Missing:**
- You did not mention the refresh token functionality
- Refresh tokens are required with 7-day expiry

**Please revise your understanding and reply again.**
```

Wait for the agent to repeat requirements again. Do NOT proceed until correct.

### 1.2.5 Agent Asks Clarifying Questions

After correct repetition, the agent may have questions. This is good - it means they are thinking deeply.

Example questions:
- "Should the token include the user's email address?"
- "What should happen if the private key file is missing?"
- "Is there a specific error format you want for expired tokens?"

**You MUST answer ALL questions before authorizing implementation.**

### 1.2.6 Answer All Questions Completely

Provide complete, detailed answers:

```markdown
## Answers to Your Questions

**Q1: Should the token include the user's email address?**
A: No, do not include email in the token payload. Only include user_id and role. Email can be fetched separately if needed.

**Q2: What should happen if the private key file is missing?**
A: Raise a ConfigurationError with message "Private key file not found at {path}". The application should fail fast - do not fall back to a different algorithm.

**Q3: Is there a specific error format for expired tokens?**
A: Yes, use this format:
{
  "error": "token_expired",
  "message": "Token has expired",
  "expired_at": "<timestamp>"
}
```

### 1.2.7 Confirm Final Understanding

After answering questions, ask for final confirmation:

```markdown
## Final Confirmation Request

I have answered your questions. Please confirm:

1. Your understanding is now complete
2. You have no more questions
3. You are ready to begin implementation

Reply with: "Understanding confirmed. Ready to implement."
```

### 1.2.8 Authorize Implementation

Only after receiving confirmation:

```markdown
## Implementation Authorized

Your understanding is verified. You may begin implementation.

**Task UUID**: task-uuid-12345
**GitHub Issue**: #42
**Deadline**: 2 hours from now

I will check in every 10-15 minutes. Report any issues immediately.

Good luck!
```

Update the state file to reflect authorization:

```yaml
instruction_verification:
  status: "authorized"
  repetition_received: true
  repetition_correct: true
  questions_asked: 3
  questions_answered: 3
  authorized_at: "2026-01-08T16:00:00+00:00"
```

---

## 1.3 Verification Message Template

Complete template for the verification request portion of the assignment message:

```markdown
## MANDATORY: Instruction Verification

Before you begin implementation, you MUST complete the Instruction Verification Protocol.

### Step 1: Repeat Requirements

In your own words, summarize the key requirements (3-5 bullet points):
- What are you building?
- What are the key features?
- What are the constraints?

### Step 2: List Questions

List any questions you have:
- Requirements that are unclear
- Edge cases not covered
- Technical decisions needed

### Step 3: Confirm Acceptance Criteria

Restate the acceptance criteria in your own words.

---

**IMPORTANT**: I will verify your understanding before authorizing implementation. Do NOT begin coding until you receive explicit authorization.

Reply with your understanding summary.
```

---

## 1.4 Common Verification Failures

### Failure Type 1: Agent Starts Without Verification

**Symptom**: Agent says "I'll start implementing now" without repeating requirements.

**Response**:
```markdown
STOP. You have not completed the Instruction Verification Protocol.

Before you can begin implementation, you must:
1. Repeat the key requirements in your own words
2. List any questions you have
3. Wait for my authorization

Please provide your understanding summary now.
```

### Failure Type 2: Superficial Repetition

**Symptom**: Agent copies the requirements verbatim instead of paraphrasing.

**Response**:
```markdown
Your repetition appears to be a copy of the original requirements.

Please restate the requirements in YOUR OWN WORDS to demonstrate understanding. I need to verify you actually understand, not just copied.

Try again with a genuine paraphrase.
```

### Failure Type 3: Missing Key Requirements

**Symptom**: Agent's summary misses important requirements.

**Response**:
```markdown
Your summary is missing key requirements:

Missing:
- Refresh token functionality
- Error handling specifications
- Rate limiting requirements

Please revise your understanding to include these items.
```

### Failure Type 4: Misunderstood Requirements

**Symptom**: Agent states something incorrectly.

**Response**:
```markdown
Your understanding contains errors:

Incorrect: "Use HS256 algorithm"
Correct: "Use RS256 algorithm"

Incorrect: "Token expiry 1 hour"
Correct: "Token expiry 24 hours"

Please correct these and restate your understanding.
```

---

## 1.5 State Tracking During Verification

The state file tracks verification progress:

```yaml
active_assignments:
  - agent: "implementer-1"
    module: "auth-core"
    task_uuid: "task-uuid-12345"
    status: "pending_verification"
    instruction_verification:
      status: "awaiting_repetition"  # or "awaiting_corrections", "awaiting_answers", "authorized"
      repetition_received: false
      repetition_correct: false
      corrections_sent: 0
      questions_asked: 0
      questions_answered: 0
      authorized_at: null
```

### Status Progression

1. `awaiting_repetition` - Assignment sent, waiting for agent to repeat
2. `awaiting_corrections` - Agent's repetition was incorrect, corrections sent
3. `awaiting_answers` - Agent asked questions, waiting for answers to be provided
4. `authorized` - Understanding verified, implementation can begin

### Verification Metrics

Track for quality monitoring:
- `corrections_sent`: How many times corrections were needed (high = unclear requirements)
- `questions_asked`: How many questions agent had (some is good, too many = unclear requirements)
- Time from assignment to authorization

---

## Summary

The Instruction Verification Protocol ensures:

1. **No misunderstandings** - Agent proves understanding before starting
2. **No wasted effort** - Catch errors before implementation begins
3. **Clear communication** - All questions answered upfront
4. **Accountability** - Clear authorization moment

**Never skip this protocol.** The extra 5-10 minutes saves hours of rework.

---

## Verification

After completing instruction verification:

- [ ] **Verify**: confirm assignment message was delivered via the `agent-messaging` skill's sent messages feature
- [ ] **Verify**: confirm agent sent back instruction summary matching requirements
- [ ] **Verify**: confirm all agent questions were answered before PROCEED authorization
- [ ] **Verify**: confirm PROCEED or HOLD status was communicated to the agent
