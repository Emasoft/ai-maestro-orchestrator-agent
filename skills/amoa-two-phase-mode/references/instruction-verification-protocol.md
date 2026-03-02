# Instruction Verification Protocol

**MANDATORY**: This protocol MUST be executed before ANY remote agent begins implementation.

## Contents

- 1. Why This Protocol Exists
  - 1.1 Reasons for misinterpretation
  - 1.2 Orchestrator proactive responsibility
- 2. The 8-Step Protocol Flow
  - 2.1 Step 1: Send Module Assignment
  - 2.2 Step 2: Request Instruction Repetition
  - 2.3 Step 3: Agent Repeats Understanding
  - 2.4 Step 4: Verify Repetition Correct
  - 2.5 Step 5: Request Clarifying Questions
  - 2.6 Step 6: Agent Asks Questions
  - 2.7 Step 7: Answer ALL Questions
  - 2.8 Step 8: Authorize Implementation
- 3. Message Templates
  - 3.1 Initial Assignment Template
  - 3.2 Correction Message Template
  - 3.3 Question Resolution Template
  - 3.4 Authorization Template
- 4. Tracking Verification Status
  - 4.1 State file fields
  - 4.2 Status values and meanings
- 5. Failure Conditions
  - 5.1 When to NOT authorize
  - 5.2 Action on failure

---

## 1. Why This Protocol Exists

### 1.1 Reasons for misinterpretation

Remote agents may misinterpret instructions due to:
- **Ambiguous wording** in specifications
- **Missing context** from earlier planning
- **Different assumptions** about implementation approach
- **Incomplete understanding** of acceptance criteria
- **Technical jargon** interpreted differently

### 1.2 Orchestrator proactive responsibility

The orchestrator must be **PROACTIVE** in ensuring understanding, not passive.

**WRONG approach:** Send task, wait for results, fix misunderstandings later
**CORRECT approach:** Verify understanding BEFORE implementation starts

---

## 2. The 8-Step Protocol Flow

```
ORCHESTRATOR                              REMOTE AGENT
     |                                         |
     |  1. Send Module Assignment              |
     |  (GitHub Issue + specs + UUID)          |
     |---------------------------------------->|
     |                                         |
     |  2. Request Instruction Repetition      |
     |  "Please repeat the key requirements    |
     |   in your own words (3-5 bullet points)"|
     |---------------------------------------->|
     |                                         |
     |  3. Agent Repeats Understanding         |
     |<----------------------------------------|
     |                                         |
     |  4. VERIFY: Is repetition correct?      |
     |     - If YES: Proceed to step 5         |
     |     - If NO: Send corrections, go to 2  |
     |---------------------------------------->|
     |                                         |
     |  5. Request Clarifying Questions        |
     |  "Do you have any questions about       |
     |   the requirements or acceptance        |
     |   criteria before starting?"            |
     |---------------------------------------->|
     |                                         |
     |  6. Agent Asks Questions (if any)       |
     |<----------------------------------------|
     |                                         |
     |  7. Answer ALL Questions                |
     |  (Do not proceed until resolved)        |
     |---------------------------------------->|
     |                                         |
     |  8. Confirm Understanding               |
     |  "Confirmed. You may begin              |
     |   implementation."                      |
     |---------------------------------------->|
     |                                         |
     |  Agent Begins Work                      |
     |                                         |
```

### 2.1 Step 1: Send Module Assignment

Send AI Maestro message using the `agent-messaging` skill with:
- Module name and description
- GitHub Issue link
- Task UUID for tracking
- Requirements summary
- Acceptance criteria

### 2.2 Step 2: Request Instruction Repetition

Include in assignment message:
```
Before you begin implementation, please:
1. Repeat the key requirements in your own words (3-5 bullet points)
2. List any questions you have about the requirements
3. Confirm your understanding of the acceptance criteria
```

### 2.3 Step 3: Agent Repeats Understanding

Agent responds with their understanding. Wait for this response before proceeding.

### 2.4 Step 4: Verify Repetition Correct

Compare agent's summary against original specs:
- **If correct:** Proceed to step 5
- **If incorrect:** Send corrections, return to step 2

Common misunderstandings:
- Wrong scope (too broad or too narrow)
- Missing key requirements
- Incorrect technical approach
- Wrong priority order

### 2.5 Step 5: Request Clarifying Questions

After confirming understanding, ask:
```
Do you have any questions about the requirements or acceptance criteria before starting?
```

### 2.6 Step 6: Agent Asks Questions

Agent may ask:
- Technical implementation questions
- Clarification on acceptance criteria
- Questions about edge cases
- Questions about dependencies

### 2.7 Step 7: Answer ALL Questions

Answer every question completely. Do NOT proceed until:
- All questions answered
- Agent confirms no more questions
- Agent confirms understanding

### 2.8 Step 8: Authorize Implementation

Send authorization message:
```
Your understanding is verified. You may begin implementation.
```

Update agent status to "working".

---

## 3. Message Templates

### 3.1 Initial Assignment Template

```markdown
Subject: [TASK] Module: {module_name} - UUID: {task_uuid}

## Assignment

You have been assigned to implement: **{module_name}**

GitHub Issue: {issue_url}
Task UUID: {task_uuid}

## Requirements Summary

{requirements_summary}

## Acceptance Criteria

{acceptance_criteria_list}

## MANDATORY: Instruction Verification

Before you begin implementation, please:

1. **Repeat the key requirements** in your own words (3-5 bullet points)
2. **List any questions** you have about the requirements
3. **Confirm your understanding** of the acceptance criteria

I will verify your understanding before authorizing implementation.

Reply with your understanding summary.
```

### 3.2 Correction Message Template

```markdown
Subject: RE: [TASK] Module: {module_name} - CORRECTION NEEDED

Your understanding summary has some issues:

**Incorrect**: {what_was_wrong}
**Correct**: {what_it_should_be}

Please revise your understanding and confirm again.
```

### 3.3 Question Resolution Template

```markdown
Subject: RE: [TASK] Module: {module_name} - Question Answers

Your questions and my answers:

Q1: {agent_question_1}
A1: {orchestrator_answer_1}

Q2: {agent_question_2}
A2: {orchestrator_answer_2}

Do you have any follow-up questions?
```

### 3.4 Authorization Template

```markdown
Subject: RE: [TASK] Module: {module_name} - AUTHORIZED TO PROCEED

Your understanding is verified. You may begin implementation.

**Reminders:**
- Report progress every 15 minutes
- Ask questions immediately if you encounter blockers
- Do NOT create PR until all tests pass
- Follow the 4-verification-loop protocol for PR requests

Begin work now.
```

---

## 4. Tracking Verification Status

### 4.1 State file fields

```yaml
active_assignments:
  - agent: "implementer-1"
    agent_type: "ai"
    module: "auth-core"
    github_issue: "#42"
    task_uuid: "task-uuid-12345"
    status: "working"
    instruction_verification:
      status: "verified"
      repetition_received: true
      repetition_correct: true
      questions_asked: 2
      questions_answered: 2
      authorized_at: "2026-01-08T16:20:00+00:00"
```

### 4.2 Status values and meanings

| Status | Meaning | Next Action |
|--------|---------|-------------|
| `pending` | Assignment sent, awaiting response | Wait for agent response |
| `awaiting_repetition` | Waiting for agent to repeat understanding | Send reminder if >10 min |
| `correcting` | Misunderstanding detected, sent corrections | Wait for revised understanding |
| `questioning` | Agent asked questions, orchestrator answering | Answer all questions |
| `verified` | Understanding confirmed, authorized to proceed | Monitor progress |

---

## 5. Failure Conditions

### 5.1 When to NOT authorize

**Do NOT authorize implementation if:**
- Agent cannot correctly repeat key requirements after 3 attempts
- Agent refuses to participate in verification protocol
- Agent begins work before authorization
- Agent cannot confirm understanding of acceptance criteria

### 5.2 Action on failure

If verification fails:

1. **Document failure** in GitHub Issue:
   ```
   Verification failed for {agent_id}:
   - Attempt 1: {issue}
   - Attempt 2: {issue}
   - Attempt 3: {issue}
   Reassigning to different agent.
   ```

2. **Reassign module** to different agent:
   ```
   /reassign-module {module_id} --to {new_agent_id}
   ```

3. **Notify user** of assignment change

4. **Start fresh** with new agent (full protocol again)

---

## Script Usage

Use `eoa_verify_instructions.py` to manage verification:

```bash
# Check verification status
python3 eoa_verify_instructions.py status implementer-1

# Record that agent repeated correctly
python3 eoa_verify_instructions.py record-repetition implementer-1 --correct

# Record that agent repeated incorrectly
python3 eoa_verify_instructions.py record-repetition implementer-1

# Record questions asked/answered
python3 eoa_verify_instructions.py record-questions implementer-1 --count 2 --answered 2

# Authorize agent to proceed
python3 eoa_verify_instructions.py authorize implementer-1
```

---

## 6. Troubleshooting

### Problem: Agent Refuses to Repeat Instructions

**Symptoms**: Agent says "I understand" but won't provide bullet-point summary.

**Solution**:
1. Explain that repetition is MANDATORY for quality assurance
2. Provide example of what a good repetition looks like
3. If agent continues refusing, document and reassign task
4. Some agents may need explicit format template to follow

### Problem: Agent Repeats Instructions But Gets Key Details Wrong

**Symptoms**: Agent's summary misses critical requirements or has wrong priorities.

**Solution**:
1. Quote the specific incorrect parts
2. Provide correct interpretation with emphasis
3. Ask agent to repeat ONLY the corrected parts
4. If 3 corrections needed, reassess if agent is right fit for task
5. Consider if original spec is ambiguous - may need clarification

### Problem: Agent Asks Too Many Questions

**Symptoms**: Agent sends 10+ questions, some seem unnecessary.

**Solution**:
1. Answer all questions - don't skip any
2. For questions that seem obvious, provide brief answer + context
3. If questions reveal fundamental misunderstanding, go back to repetition step
4. Group related questions in response for clarity
5. If pattern continues, spec may need more detail

### Problem: Agent Asks No Questions

**Symptoms**: Agent says "no questions" but task is complex.

**Solution**:
1. This MAY be fine if agent truly understands
2. Ask probing questions: "How will you handle X edge case?"
3. If agent can't answer probes, they didn't fully understand
4. Consider asking about specific technical challenges
5. Better to discover gaps now than during implementation

### Problem: Agent Starts Work Before Authorization

**Symptoms**: Agent reports progress but verification was not completed.

**Solution**:
1. Immediately send STOP message
2. Require agent to complete verification before continuing
3. Review any work done - may need to be discarded if based on wrong understanding
4. Document incident in GitHub Issue
5. If repeated, consider reassigning to more disciplined agent

### Problem: Verification Takes Too Long

**Symptoms**: Multiple rounds of correction/questions, no progress.

**Solution**:
1. Evaluate if task is too complex for single agent
2. Consider breaking into smaller, clearer subtasks
3. Check if spec has ambiguities causing confusion
4. If agent fundamentally misaligned, reassign sooner rather than later
5. Set maximum 3 correction rounds before reassignment

### Problem: Agent Understanding Changes After Authorization

**Symptoms**: During implementation, agent reveals they understood differently.

**Solution**:
1. Pause implementation immediately
2. Identify the discrepancy
3. Determine if work done so far is salvageable
4. Run abbreviated verification on misunderstood parts
5. Update spec if it was genuinely unclear
6. Document for future task assignments
