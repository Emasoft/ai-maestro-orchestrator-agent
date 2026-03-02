# RULE 16: Orchestrator-Exclusive Communications (ABSOLUTE)


## Contents

- [Table of Contents](#table-of-contents)
- [1. Core Principle](#1-core-principle)
  - [1.1 What This Rule Means](#11-what-this-rule-means)
  - [1.2 Why This Rule Exists](#12-why-this-rule-exists)
- [2. Orchestrator-Exclusive Actions](#2-orchestrator-exclusive-actions)
  - [2.1 Actions ONLY the Orchestrator Can Perform](#21-actions-only-the-orchestrator-can-perform)
  - [2.2 Why Each Action is Exclusive](#22-why-each-action-is-exclusive)
- [3. Sub-Agent Restrictions](#3-sub-agent-restrictions)
  - [3.1 What Sub-Agents CANNOT Do](#31-what-sub-agents-cannot-do)
  - [3.2 What Sub-Agents CAN Do](#32-what-sub-agents-can-do)
- [4. Communication Flow](#4-communication-flow)
  - [4.1 Correct Communication Pattern](#41-correct-communication-pattern)
  - [4.2 Forbidden Communication Pattern](#42-forbidden-communication-pattern)
- [5. Practical Examples](#5-practical-examples)
  - [5.1 WRONG Approach (Sub-Agent Sends Messages)](#51-wrong-approach-sub-agent-sends-messages)
  - [5.2 CORRECT Approach (Sub-Agent Reports to Orchestrator)](#52-correct-approach-sub-agent-reports-to-orchestrator)
  - [5.3 CORRECT Approach (Sub-Agent Prepares Template)](#53-correct-approach-sub-agent-prepares-template)
- [6. Enforcement Mechanism](#6-enforcement-mechanism)
  - [6.1 What to Include in Sub-Agent Prompts](#61-what-to-include-in-sub-agent-prompts)
  - [6.2 What to Check Before Spawning Sub-Agents](#62-what-to-check-before-spawning-sub-agents)
- [7. Standardized Rules for Sub-Agent GitHub Interactions](#7-standardized-rules-for-sub-agent-github-interactions)
  - [7.1 When Sub-Agents Can Use GitHub](#71-when-sub-agents-can-use-github)
  - [7.2 Standardized Comment Format](#72-standardized-comment-format)
  - [7.3 Rules for Opening Bug Reports](#73-rules-for-opening-bug-reports)
  - [7.4 Rules for Issue Triage](#74-rules-for-issue-triage)
  - [7.5 What Sub-Agents CANNOT Do on GitHub](#75-what-sub-agents-cannot-do-on-github)
- [See Also](#see-also)

---

## Table of Contents

- 1. Core Principle
  - 1.1 What This Rule Means
  - 1.2 Why This Rule Exists
- 2. Orchestrator-Exclusive Actions
  - 2.1 Actions ONLY the Orchestrator Can Perform
  - 2.2 Why Each Action is Exclusive
- 3. Sub-Agent Restrictions
  - 3.1 What Sub-Agents CANNOT Do
  - 3.2 What Sub-Agents CAN Do
- 4. Communication Flow
  - 4.1 Correct Communication Pattern
  - 4.2 Forbidden Communication Pattern
- 5. Practical Examples
  - 5.1 WRONG Approach (Sub-Agent Sends Messages)
  - 5.2 CORRECT Approach (Sub-Agent Reports to Orchestrator)
- 6. Enforcement Mechanism
  - 6.1 What to Include in Sub-Agent Prompts
  - 6.2 What to Check Before Spawning Sub-Agents
- 7. Standardized Rules for Sub-Agent GitHub Interactions
  - 7.1 When Sub-Agents Can Use GitHub
  - 7.2 Standardized Comment Format
  - 7.3 Rules for Opening Bug Reports
  - 7.4 Rules for Issue Triage
  - 7.5 What Sub-Agents CANNOT Do on GitHub

---

## 1. Core Principle

### 1.1 What This Rule Means

**ONLY the orchestrator (main Claude) can:**
- Send direct messages to other agents via AI Maestro
- Receive and process direct messages from other agents via AI Maestro
- Commit changes to git repositories
- Push changes to remote repositories
- Publish releases or packages
- Send notifications to external systems (webhooks, Slack, email)

**Sub-agents MUST NOT:**
- Send any AI Maestro direct messages
- Read the AI Maestro inbox
- Commit any changes to git
- Push to any remote repository

**Sub-agents CAN (with standardized rules):**
- Comment on GitHub issues (as part of their workflow)
- Open bug reports on GitHub
- Answer and triage GitHub issues
- Update GitHub issue labels and status

**IMPORTANT DISTINCTION:**
| Communication Type | Sub-Agent Permission | Rationale |
|--------------------|---------------------|-----------|
| AI Maestro messages | **FORBIDDEN** | Direct inter-agent coordination requires orchestrator context |
| GitHub issue comments | **ALLOWED** (with rules) | Public, auditable, part of issue workflow |
| GitHub bug reports | **ALLOWED** (with rules) | Standardized format, linked to issues |
| GitHub issue triage | **ALLOWED** (with rules) | Follows issue management protocols |

### 1.2 Why This Rule Exists

1. **Single Point of Coordination** - One agent controls all external interactions
2. **Accountability** - Clear audit trail of who sent what
3. **Consistency** - All communications follow consistent formatting and protocols
4. **Safety** - Prevents accidental duplicate messages or conflicting commits
5. **Context Awareness** - Only the orchestrator has full project context

---

## 2. Orchestrator-Exclusive Actions

### 2.1 Actions ONLY the Orchestrator Can Perform

| Action | Description | Why Exclusive |
|--------|-------------|---------------|
| Send AI Maestro messages | Use the `agent-messaging` skill | Requires coordination context |
| Check AI Maestro inbox | Use the `agent-messaging` skill | Must process in priority order |
| `git commit` | Commit staged changes | Must track all commits |
| `git push` | Push to remote | Must coordinate with PR workflow |
| `gh pr create` | Create pull requests | Must track all PRs |
| `gh release create` | Publish releases | Must coordinate release timing |
| Notify external systems | Webhooks, Slack, email | Single source of notifications |

### 2.2 Why Each Action is Exclusive

| Action | Consequence if Sub-Agent Does It |
|--------|----------------------------------|
| Send AI Maestro messages | Duplicate/conflicting instructions to other agents |
| Check AI Maestro inbox | Messages processed out of order, missed coordination |
| `git commit` | Multiple commits for same change, messy history |
| `git push` | Force push conflicts, lost work |
| `gh pr create` | Multiple PRs for same feature, confusion |
| `gh release create` | Premature or duplicate releases |
| Notify external systems | Spam, duplicates, conflicting information |

---

## 3. Sub-Agent Restrictions

### 3.1 What Sub-Agents CANNOT Do

| FORBIDDEN | WHY |
|-----------|-----|
| Send AI Maestro messages | Orchestrator coordinates all agent communication |
| Read AI Maestro inbox | Orchestrator manages message processing |
| Run `git commit` | Orchestrator tracks all commits |
| Run `git push` | Orchestrator coordinates with remote |
| Run `gh pr create` | Orchestrator manages PR workflow |
| Send webhooks or notifications | Orchestrator controls external comms |
| Access external APIs for sending | Orchestrator is the gateway |

### 3.2 What Sub-Agents CAN Do

| ALLOWED | EXAMPLE | PURPOSE |
|---------|---------|---------|
| Prepare message templates | Write draft message to file | Orchestrator reviews and sends |
| Prepare commit messages | Write message to `.commit-message.txt` | Orchestrator commits with it |
| Customize checklists | Fill in task-specific checklist | Orchestrator sends to assignee |
| Design documents | Write spec to `docs/spec.md` | Orchestrator shares via message |
| Generate reports | Create `RESULTS.md` | Orchestrator extracts and sends |
| Draft PR descriptions | Write PR template to file | Orchestrator creates PR with it |
| Analyze code | Write analysis to report file | Orchestrator decides next action |
| Run tests | Execute and log results | Orchestrator reviews and reports |

---

## 4. Communication Flow

### 4.1 Correct Communication Pattern

```
USER REQUEST
    |
    v
ORCHESTRATOR (Main Claude)
    |
    +--> Spawns Sub-Agent with task
    |         |
    |         v
    |    SUB-AGENT works on task
    |         |
    |         +--> Writes results to file
    |         +--> Reports back to orchestrator (via Task tool return)
    |         |
    |    SUB-AGENT exits
    |         |
    v         v
ORCHESTRATOR receives sub-agent report
    |
    +--> Orchestrator reads result file (if needed)
    +--> Orchestrator sends AI Maestro message (if needed)
    +--> Orchestrator commits changes (if needed)
    +--> Orchestrator responds to user
```

### 4.2 Forbidden Communication Pattern

```
USER REQUEST
    |
    v
ORCHESTRATOR (Main Claude)
    |
    +--> Spawns Sub-Agent with task
              |
              v
         SUB-AGENT works on task
              |
              X--> Sub-agent sends AI Maestro message  <- FORBIDDEN
              X--> Sub-agent runs git commit           <- FORBIDDEN
              X--> Sub-agent runs git push             <- FORBIDDEN
              X--> Sub-agent calls external webhook    <- FORBIDDEN
```

---

## 5. Practical Examples

### 5.1 WRONG Approach (Sub-Agent Sends Messages)

```
Orchestrator spawns sub-agent:
  Task: "Implement auth module and notify helper-agent-generic when done"

Sub-agent:
  - Implements auth module
  - Sends external message via AI Maestro
  -> RULE 16 VIOLATION: Sub-agent sent external message
```

### 5.2 CORRECT Approach (Sub-Agent Reports to Orchestrator)

```
Orchestrator spawns sub-agent:
  Task: "Implement auth module. Return minimal report when complete."

Sub-agent:
  - Implements auth module
  - Returns: "[DONE] auth-module - Created src/auth/*, 5 files, all tests pass"

Orchestrator:
  - Receives sub-agent report
  - Decides to notify helper-agent-generic
  - Uses the agent-messaging skill to send the notification
  -> RULE 16 COMPLIANT: Only orchestrator sends external message
```

### 5.3 CORRECT Approach (Sub-Agent Prepares Template)

```
Orchestrator spawns sub-agent:
  Task: "Prepare delegation message for auth module implementation.
         Write template to docs_dev/auth-delegation-template.md.
         DO NOT send the message - return filepath only."

Sub-agent:
  - Researches requirements
  - Writes detailed delegation message to file
  - Returns: "[DONE] auth-delegation-template - docs_dev/auth-delegation-template.md"

Orchestrator:
  - Reads template file
  - Reviews and adjusts if needed
  - Sends via AI Maestro
  -> RULE 16 COMPLIANT: Sub-agent prepared, orchestrator sent
```

---

## 6. Enforcement Mechanism

### 6.1 What to Include in Sub-Agent Prompts

**ALWAYS include this in every sub-agent prompt:**

```
CONSTRAINTS:
- DO NOT send any AI Maestro messages
- DO NOT run git commit or git push
- DO NOT create PRs or releases
- DO NOT call external APIs for sending/posting
- ONLY report back to me (the orchestrator) with your results
- If you need to prepare content for external communication, write it to a file
```

### 6.2 What to Check Before Spawning Sub-Agents

Before spawning any sub-agent, verify:

1. **Task does NOT require external communication**
   - If it does: Split into "prepare" (sub-agent) and "send" (orchestrator)

2. **Task does NOT require git commits**
   - If it does: Sub-agent makes changes, orchestrator commits

3. **Task does NOT require PR creation**
   - If it does: Sub-agent prepares PR description, orchestrator creates PR

4. **Task does NOT require notifying other agents**
   - If it does: Sub-agent reports completion, orchestrator sends notification

---

## 7. Standardized Rules for Sub-Agent GitHub Interactions

Sub-agents CAN interact with GitHub issues/PRs as part of their workflow, but MUST follow these standardized rules.

### 7.1 When Sub-Agents Can Use GitHub

| Workflow | GitHub Action | Allowed | Example |
|----------|--------------|---------|---------|
| Bug investigation | Comment with findings | YES | "Investigated: root cause is X" |
| Code review | Comment on PR | YES | "Found issue at line 42" |
| Issue triage | Add labels | YES | Adding `bug`, `priority-high` |
| Bug discovery | Open new issue | YES | Standardized bug report |
| PR review | Request changes | YES | Using GitHub review feature |

### 7.2 Standardized Comment Format

All sub-agent GitHub comments MUST follow this format:

```markdown
**[AGENT: {agent-name}]** - {action-type}

{content}

---
*Automated comment by {agent-name} sub-agent*
```

**Example:**
```markdown
**[AGENT: bug-investigator]** - Investigation Complete

Root cause identified: Race condition in `sync_handler.py:142`

**Findings:**
- Thread A acquires lock, Thread B times out
- Missing retry logic after timeout
- Affects concurrent writes > 100/sec

**Suggested fix:** Add exponential backoff retry (see linked PR)

---
*Automated comment by bug-investigator sub-agent*
```

### 7.3 Rules for Opening Bug Reports

Sub-agents opening bug reports MUST:

1. **Use standardized template** (from issue templates)
2. **Include agent identifier** in title: `[AUTO] Bug: {description}`
3. **Link to parent issue** if investigating existing issue
4. **Add label** `auto-reported` for tracking
5. **NOT assign** to anyone (orchestrator assigns)

### 7.4 Rules for Issue Triage

Sub-agents triaging issues MUST:

1. **Only add labels** - never remove labels added by humans
2. **Only add comments** - never edit or delete existing comments
3. **Follow label hierarchy** defined in project settings
4. **Report triage decisions** back to orchestrator

### 7.5 What Sub-Agents CANNOT Do on GitHub

Even with GitHub access, sub-agents CANNOT:

| Action | Why Forbidden |
|--------|---------------|
| Close issues | Only orchestrator or humans close |
| Merge PRs | Orchestrator manages merge workflow |
| Delete comments | Audit trail must be preserved |
| Change issue assignees | Orchestrator manages assignments |
| Create releases | Orchestrator manages release workflow |
| Push to protected branches | Orchestrator coordinates with CI/CD |

---

## See Also

- [orchestrator-no-implementation.md](orchestrator-no-implementation.md) - RULE 15: No implementation by orchestrator
- [orchestrator-guardrails.md](orchestrator-guardrails.md) - Detailed role boundaries
- [agent-selection-guide.md](agent-selection-guide.md) - Which agent for which task
