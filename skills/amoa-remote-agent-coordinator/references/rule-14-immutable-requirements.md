# RULE 14: User Requirements Are Immutable


## Contents

- [Table of Contents](#table-of-contents)
- [1.0 Overview](#10-overview)
- [2.0 Mandatory Task Delegation Elements](#20-mandatory-task-delegation-elements)
  - [2.1 Requirement Reference Section](#21-requirement-reference-section)
- [User Requirements (IMMUTABLE)](#user-requirements-immutable)
  - [2.2 Forbidden Actions Block](#22-forbidden-actions-block)
- [FORBIDDEN (RULE 14 Violations)](#forbidden-rule-14-violations)
  - [2.3 Escalation Protocol Section](#23-escalation-protocol-section)
- [If Requirements Have Issues](#if-requirements-have-issues)
- [3.0 Task Template Requirements](#30-task-template-requirements)
  - [3.1 Updating All Task Delegation Templates](#31-updating-all-task-delegation-templates)
  - [3.2 Verification Checklist](#32-verification-checklist)
- [4.0 Violation Handling](#40-violation-handling)
  - [4.1 When Remote Agent Reports a Violation](#41-when-remote-agent-reports-a-violation)
  - [4.2 Requirement Issue Report Format](#42-requirement-issue-report-format)
- [Requirement Issue Report](#requirement-issue-report)
  - [Issue Description](#issue-description)
  - [Agent's Concern](#agents-concern)
  - [Options](#options)
  - [Recommendation](#recommendation)
  - [4.3 User Decision Workflow](#43-user-decision-workflow)

---

## Table of Contents

- 1.0 Overview
- 1.1 What RULE 14 means
- 1.2 Why user requirements cannot be changed
- 2.0 Mandatory Task Delegation Elements
- 2.1 Requirement Reference section
- 2.2 Forbidden Actions block
- 2.3 Escalation Protocol section
- 3.0 Task Template Requirements
- 3.1 Updating all task delegation templates
- 3.2 Verification checklist
- 4.0 Violation Handling
- 4.1 When remote agent reports a violation
- 4.2 Generating Requirement Issue Report
- 4.3 User decision workflow

---

## 1.0 Overview

User requirements are immutable. Remote agents and orchestrators CANNOT change, reduce, substitute, or "improve" beyond what the user explicitly requested.

---

## 2.0 Mandatory Task Delegation Elements

### 2.1 Requirement Reference Section

Every task delegation to remote agents MUST include:

```markdown
## User Requirements (IMMUTABLE)
- REQ-XXX: "[exact user quote]"
- These requirements CANNOT be changed without user approval
```

### 2.2 Forbidden Actions Block

```markdown
## FORBIDDEN (RULE 14 Violations)
- Do NOT substitute user-specified technologies
- Do NOT pivot to different architecture
- Do NOT reduce scope without user approval
- Do NOT "improve" beyond what user asked
```

### 2.3 Escalation Protocol Section

```markdown
## If Requirements Have Issues
1. STOP implementation
2. Report to orchestrator: "[ISSUE] REQ-XXX has problem: [details]"
3. WAIT for user decision
4. Do NOT proceed until user decides
```

---

## 3.0 Task Template Requirements

### 3.1 Updating All Task Delegation Templates

All task delegation templates MUST include the above sections. This applies to:
- Feature implementation tasks
- Bug fix tasks
- Refactoring tasks
- Documentation tasks
- Any other task type

### 3.2 Verification Checklist

Before sending any task delegation, verify:
- [ ] User requirements quoted exactly
- [ ] Requirement IDs assigned (REQ-XXX format)
- [ ] Forbidden actions block included
- [ ] Escalation protocol included
- [ ] No scope changes from original user request

---

## 4.0 Violation Handling

### 4.1 When Remote Agent Reports a Violation

If remote agent reports a RULE 14 violation:
1. Immediately halt the task
2. Generate Requirement Issue Report
3. Present to user
4. Resume only after user decision

### 4.2 Requirement Issue Report Format

```markdown
## Requirement Issue Report

**Task**: {task_id}
**Agent**: {agent_session_name}
**Requirement**: REQ-XXX

### Issue Description
{detailed description of why requirement is problematic}

### Agent's Concern
{what the agent identified as the problem}

### Options
A. Proceed as specified (accept risk)
B. Modify requirement to: {proposed modification}
C. Cancel task pending redesign

### Recommendation
{orchestrator's recommendation with reasoning}

Awaiting user decision.
```

### 4.3 User Decision Workflow

1. Present Requirement Issue Report to user
2. Wait for user decision (A, B, or C)
3. Document decision with timestamp
4. Update task instructions if B selected
5. Notify agent of outcome
6. Resume or cancel based on decision
