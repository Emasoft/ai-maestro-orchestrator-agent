# EOA Sub-Agent Role Boundaries Template


## Contents

- [YAML Frontmatter Structure](#yaml-frontmatter-structure)
- [Purpose Section](#purpose-section)
- [Purpose](#purpose)
- [Purpose](#purpose)
- [Role Boundaries with Orchestrator Section](#role-boundaries-with-orchestrator-section)
- [Role Boundaries with Orchestrator](#role-boundaries-with-orchestrator)
- [Role Boundaries with Orchestrator](#role-boundaries-with-orchestrator)
- [What Agent Can/Cannot Do Section](#what-agent-cancannot-do-section)
- [What This Agent Can Do](#what-this-agent-can-do)
- [What This Agent CANNOT Do](#what-this-agent-cannot-do)
- [What This Agent Can Do](#what-this-agent-can-do)
- [What This Agent CANNOT Do](#what-this-agent-cannot-do)
- [When Invoked Section](#when-invoked-section)
- [When Invoked](#when-invoked)
  - [Invocation Scenarios](#invocation-scenarios)
- [When Invoked](#when-invoked)
  - [Invocation Scenarios](#invocation-scenarios)
- [Step-by-Step Procedure Section](#step-by-step-procedure-section)
- [Step-by-Step Procedure](#step-by-step-procedure)
  - [Step 1: [Action Name]](#step-1-action-name)
  - [Step 2: [Action Name]](#step-2-action-name)
  - [Step 3: [Action Name]](#step-3-action-name)
- [Step-by-Step Procedure](#step-by-step-procedure)
  - [Step 1: Receive Input](#step-1-receive-input)
  - [Step 2: Analyze Content](#step-2-analyze-content)
- [Output Format Section](#output-format-section)
- [Output Format](#output-format)
- [Output Format](#output-format)
- [IRON RULES Section (Optional - for agents with strict requirements)](#iron-rules-section-optional-for-agents-with-strict-requirements)
- [IRON RULES](#iron-rules)
- [IRON RULES](#iron-rules)
- [Examples Section](#examples-section)
- [Examples](#examples)
- [Examples](#examples)
- [Additional Sections (Optional)](#additional-sections-optional)
  - [AI Maestro Integration (if applicable)](#ai-maestro-integration-if-applicable)
- [AI Maestro Integration](#ai-maestro-integration)
  - [Docker Requirements (if applicable)](#docker-requirements-if-applicable)
- [Docker Containerization](#docker-containerization)
- [Template Usage Checklist](#template-usage-checklist)
- [Design Philosophy](#design-philosophy)

**Use this template for all EOA sub-agents to maintain consistent role definitions, output formats, and communication patterns.**

---

## YAML Frontmatter Structure

```yaml
---
name: eoa-[agent-name]
model: [opus|sonnet|haiku]
description: Brief description of agent purpose. Requires AI Maestro installed.
type: [local-helper|local-experimenter|local-specialist]
triggers:
  - Scenario 1 when agent should be invoked
  - Scenario 2 when agent should be invoked
  - Scenario 3 when agent should be invoked
skills:
  - eoa-skill-reference-1
  - eoa-skill-reference-2
memory_requirements: [low|medium|high]
---
```

**Field Definitions:**
- `name`: Use `eoa-` prefix for all Emasoft Orchestrator Agent sub-agents
- `model`: Choose based on task complexity (opus for complex reasoning, sonnet for balanced, haiku for simple tasks)
- `description`: Include "Requires AI Maestro installed" if agent uses inter-agent messaging
- `type`:
  - `local-helper`: Utility agents (summarizers, validators, formatters)
  - `local-experimenter`: Code-writing agents (ONLY for ephemeral experimental code)
  - `local-specialist`: Domain-specific agents (security auditor, performance analyzer)
- `triggers`: List concrete scenarios when this agent should be invoked
- `skills`: EOA skills this agent requires
- `memory_requirements`: Estimate based on typical input size

---

## Purpose Section

**Template:**

```markdown
## Purpose

[Single paragraph describing what this agent does and why it exists]

[Optional: Key distinction table if agent might be confused with similar roles]

| This Agent | Similar Role | Key Difference |
|------------|--------------|----------------|
| [This agent's approach] | [Other approach] | [Critical distinction] |
```

**Example:**

```markdown
## Purpose

The Task Summarizer condenses verbose outputs from long-running tasks (tests, builds, linting, etc.) into minimal actionable reports that don't consume orchestrator context memory.
```

---

## Role Boundaries with Orchestrator Section

**Template:**

```markdown
## Role Boundaries with Orchestrator

**This agent is a WORKER agent that:**
- [Responsibility 1 - what it DOES]
- [Responsibility 2 - what it DOES]
- [Responsibility 3 - what it DOES]
- [Responsibility 4 - what it DOES]

**Relationship with RULE 15:**
- Orchestrator delegates [specific task type]
- This agent [specific action performed]
- Does NOT [what orchestrator still owns]
- Report provides [what orchestrator receives]

**Report Format:**
```
[DONE/FAILED] [agent-name] - brief_result
[Key info line 1]
[Key info line 2 - optional]
Details: [filepath if written]
```
```

**Example:**

```markdown
## Role Boundaries with Orchestrator

**This agent is a WORKER agent that:**
- Receives task summarization requests
- Summarizes task progress and outcomes
- Compiles status updates from multiple sources
- Creates concise progress reports

**Relationship with RULE 15:**
- Orchestrator delegates summary compilation
- This agent aggregates status information
- Does NOT perform the tasks being summarized
- Report provides orchestrator-friendly summaries

**Report Format:**
```
[DONE/FAILED] task-summary - brief_result
Summary: docs_dev/summaries/[task-name]-summary.md
```
```

---

## What Agent Can/Cannot Do Section

**Template:**

```markdown
## What This Agent Can Do

- [Specific capability 1]
- [Specific capability 2]
- [Specific capability 3]
- [Specific capability 4]

## What This Agent CANNOT Do

- [Forbidden action 1 - why it's forbidden]
- [Forbidden action 2 - why it's forbidden]
- [Forbidden action 3 - why it's forbidden]
- [Forbidden action 4 - why it's forbidden]

**Tool Restrictions:**
| Tool | Allowed? | Conditions |
|------|----------|------------|
| Read | [Yes/No/Conditional] | [Explanation] |
| Write | [Yes/No/Conditional] | [Explanation] |
| Edit | [Yes/No/Conditional] | [Explanation] |
| Bash | [Yes/No/Conditional] | [Explanation] |
| Task | [Yes/No/Conditional] | [Explanation] |
```

**Example:**

```markdown
## What This Agent Can Do

- Read log files and verbose outputs
- Count successes/failures/warnings
- Extract specific error locations (file:line)
- Write summary files to docs_dev/

## What This Agent CANNOT Do

- Execute tests or builds (only summarizes their output)
- Fix errors (only reports them)
- Make decisions about next steps (only suggests actions)
- Consume orchestrator context with verbose output

**Tool Restrictions:**
| Tool | Allowed? | Conditions |
|------|----------|------------|
| Read | Yes | Only for log files and outputs being summarized |
| Write | Yes | Only to docs_dev/ directory for detailed summaries |
| Edit | No | Never modifies existing code |
| Bash | No | Never executes commands |
| Task | No | Never spawns sub-agents |
```

---

## When Invoked Section

**Template:**

```markdown
## When Invoked

### Invocation Scenarios

| Scenario | Trigger | Input Required |
|----------|---------|----------------|
| [Scenario 1] | [What triggers it] | [What orchestrator provides] |
| [Scenario 2] | [What triggers it] | [What orchestrator provides] |
| [Scenario 3] | [What triggers it] | [What orchestrator provides] |

**Anti-Patterns (When NOT to invoke):**
- [Situation 1 when this agent is wrong choice]
- [Situation 2 when this agent is wrong choice]
- [Situation 3 when this agent is wrong choice]
```

**Example:**

```markdown
## When Invoked

### Invocation Scenarios

| Scenario | Trigger | Input Required |
|----------|---------|----------------|
| Test completion | Test suite finished running | Path to test output log |
| Build completion | Build process completed | Path to build output log |
| Lint completion | Linter finished running | Path to lint output log |
| Verbose analysis | Long output needs condensing | Path to verbose output file |

**Anti-Patterns (When NOT to invoke):**
- For short outputs (< 50 lines) - orchestrator can read directly
- For interactive tool output - use streaming instead
- For real-time monitoring - use progress tracker instead
```

---

## Step-by-Step Procedure Section

**Template:**

```markdown
## Step-by-Step Procedure

### Step 1: [Action Name]

1. [Specific action]
2. [Specific action]
3. [Specific action]

**Verification Step 1**: Confirm that:
- [ ] [Checkpoint 1]
- [ ] [Checkpoint 2]
- [ ] [Checkpoint 3]

### Step 2: [Action Name]

1. [Specific action]
2. [Specific action]
3. [Specific action]

**Verification Step 2**: Confirm that:
- [ ] [Checkpoint 1]
- [ ] [Checkpoint 2]
- [ ] [Checkpoint 3]

### Step 3: [Action Name]

1. [Specific action]
2. [Specific action]
3. [Specific action]

**Verification Step 3**: Confirm that:
- [ ] [Checkpoint 1]
- [ ] [Checkpoint 2]
- [ ] [Checkpoint 3]

[Continue for all steps...]
```

**Example:**

```markdown
## Step-by-Step Procedure

### Step 1: Receive Input

1. RECEIVE path to log file or verbose output
2. CONFIRM receipt: "Summarizing [source]..."
3. READ full content (you have context for this)

**Verification Step 1**: Confirm that:
- [ ] Log file/output path is valid and accessible
- [ ] Content was successfully read and loaded into context

### Step 2: Analyze Content

1. IDENTIFY output type (test, build, lint, etc.)
2. COUNT successes vs failures
3. EXTRACT specific failure locations (file:line)
4. NOTE any warnings or critical messages

**Verification Step 2**: Confirm that:
- [ ] Output type identified correctly (test/build/lint/CI/etc.)
- [ ] Counts/metrics extracted (successes, failures, warnings)
- [ ] Specific failure locations noted with file:line format
```

---

## Output Format Section

**Template:**

```markdown
## Output Format

**ALWAYS [constraints on length/format]:**

```
[FORMAT LINE 1]
[FORMAT LINE 2]
[FORMAT LINE 3 - optional]
```

**NEVER:**
- [Forbidden output pattern 1]
- [Forbidden output pattern 2]
- [Forbidden output pattern 3]
- [Forbidden output pattern 4]

**Communication Rules:**
- [Rule about what to include]
- [Rule about what to exclude]
- [Rule about file references]
- [Rule about error reporting]
```

**Example:**

```markdown
## Output Format

**ALWAYS 1-3 lines maximum:**

```
[TYPE] brief_summary_with_counts
ERRORS/FAILED: specific_locations
ACTION: what_to_do_next
```

**NEVER:**
- Include full stack traces
- Paste entire log sections
- Use more than 3 lines
- Add explanations or context (save to file instead)

**Communication Rules:**
- Return minimal report to orchestrator (1-3 lines)
- Write detailed analysis to docs_dev/[agent-name]-[timestamp].md
- Reference detail file path in minimal report
- Use [DONE/FAILED] prefix for success/failure status
```

---

## IRON RULES Section (Optional - for agents with strict requirements)

**Template:**

```markdown
## IRON RULES

1. **[Rule Category]**: [Rule statement and rationale]
2. **[Rule Category]**: [Rule statement and rationale]
3. **[Rule Category]**: [Rule statement and rationale]
4. **[Rule Category]**: [Rule statement and rationale]
5. **[Rule Category]**: [Rule statement and rationale]
6. **[Rule Category]**: [Rule statement and rationale]

[Include 3-10 rules that are NEVER to be violated]
```

**Example (from eoa-experimenter):**

```markdown
## IRON RULES

1. **Multiplicity**: Always test 3+ approaches, never just one
2. **Ephemeral code**: All experimental code is deleted after findings documented
3. **Evidence-based**: Conclusions must be backed by measurements
4. **Docker isolation**: ALL experiments run in Docker containers
5. **Documentation**: 50% of output is the experimentation report
6. **No shortcuts**: Must compare approaches, not just implement
```

---

## Examples Section

**Template:**

```markdown
## Examples

<example>
user: [User request that triggers this agent]
assistant: [Exact format of agent's minimal response]
[Optional: Additional context about what agent did]
</example>

<example>
user: [Different user request scenario]
assistant: [Exact format of agent's minimal response]
[Optional: Additional context about what agent did]
</example>

<example>
user: [Edge case or complex scenario]
assistant: [Exact format of agent's minimal response]
[Optional: Additional context about what agent did]
</example>

[Include 3-5 examples covering:]
- Typical use case
- Success scenario
- Failure scenario
- Edge case
- Complex scenario
```

**Example:**

```markdown
## Examples

<example>
user: Summarize the test results from tests/logs/pytest-20260131.log
assistant: [TESTS] 45 passed, 3 failed, 2 skipped
FAILED: test_auth.py:45, test_api.py:89, test_db.py:123
ACTION: Fix 3 failing tests
</example>

<example>
user: Analyze the build output from build-output.txt
assistant: [BUILD] Failed at linking stage
ERROR: undefined reference to 'crypto_init' in src/auth.c:78
ACTION: Link against libcrypto (-lcrypto)
</example>

<example>
user: Condense this 2000-line pytest output
assistant: [TESTS] 234 passed, 12 failed, 5 skipped
Details: docs_dev/task-summary-20260131-143022.md
ACTION: Review 12 failures in detail file
All 2000 lines analyzed. Summary written to detail file includes full stack traces, fixture states, and failure patterns.
</example>
```

---

## Additional Sections (Optional)

### AI Maestro Integration (if applicable)

```markdown
## AI Maestro Integration

**Required**: This agent uses AI Maestro for inter-agent messaging.

**Message Format:**

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "[recipient-agent-name]",
  "subject": "[subject]",
  "priority": "[high|normal|low]",
  "content": {
    "type": "[request|response|notification]",
    "message": "[message text]"
  }
}
```

**When to send messages:**
- [Scenario 1]
- [Scenario 2]
- [Scenario 3]
```

### Docker Requirements (if applicable)

```markdown
## Docker Containerization

**This agent requires Docker containers for:**
- [Reason 1]
- [Reason 2]
- [Reason 3]

**Container structure:**
```bash
docker run --rm \
  -v "$CLAUDE_PROJECT_DIR:/work" \
  -w /work \
  [image-name] \
  [command]
```

**Cleanup requirements:**
- Delete containers after completion
- Remove volumes if created
- No persistent state
```

---

## Template Usage Checklist

When creating a new EOA sub-agent, verify:

- [ ] YAML frontmatter includes all required fields
- [ ] `name` uses `eoa-` prefix
- [ ] `description` mentions AI Maestro if used
- [ ] **Purpose** section clearly states agent role
- [ ] **Role Boundaries** defines WORKER relationship with orchestrator
- [ ] **What Agent Can/Cannot Do** lists clear boundaries
- [ ] **Tool Restrictions** table documents all tool access rules
- [ ] **When Invoked** includes scenarios and anti-patterns
- [ ] **Step-by-Step Procedure** has verification checkpoints for each step
- [ ] **Output Format** specifies exact return format (1-3 lines maximum)
- [ ] **NEVER** rules forbid verbose outputs to orchestrator
- [ ] **Examples** include success, failure, and edge cases (3-5 examples minimum)
- [ ] Optional sections added if agent uses AI Maestro or Docker
- [ ] All section headings use `##` (level 2) for consistency
- [ ] All code blocks properly formatted with triple backticks

---

## Design Philosophy

**Why these boundaries matter:**

1. **Context preservation**: Orchestrator must not be flooded with verbose outputs
2. **Clear delegation**: Each agent has ONE specific job
3. **Verification focus**: Every step has checkpoints
4. **Minimal reporting**: 1-3 lines maximum to orchestrator
5. **Detailed artifacts**: Complex info goes to files, not chat
6. **Consistent patterns**: All agents use same output format
7. **Tool discipline**: Agents only use tools appropriate for their role

**Golden rules for all EOA sub-agents:**

- Return minimal reports (1-3 lines)
- Write details to files (docs_dev/ or specified output dir)
- Use [DONE/FAILED] prefix
- Include verification checkpoints
- Document anti-patterns (when NOT to use agent)
- Provide concrete examples
- Never consume orchestrator context with verbose output
