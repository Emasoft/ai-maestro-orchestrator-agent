# RULE 14: User Requirements Are Immutable


## Contents

- [Table of Contents](#table-of-contents)
- [1. Core Principle](#1-core-principle)
  - [1.1 What Immutable Requirements Means](#11-what-immutable-requirements-means)
  - [1.2 Why This Rule Exists](#12-why-this-rule-exists)
- [2. Orchestration Requirement Enforcement](#2-orchestration-requirement-enforcement)
  - [2.1 At Project Start](#21-at-project-start)
- [Requirements](#requirements)
- [Notes](#notes)
  - [2.2 During Planning](#22-during-planning)
  - [2.3 During Execution](#23-during-execution)
  - [2.4 At Review](#24-at-review)
- [3. Orchestrator Forbidden Actions](#3-orchestrator-forbidden-actions)
  - [3.1 Actions That Violate RULE 14](#31-actions-that-violate-rule-14)
  - [3.2 Consequences of Violations](#32-consequences-of-violations)
- [4. Requirement Issue Workflow](#4-requirement-issue-workflow)
  - [4.1 When to Use This Workflow](#41-when-to-use-this-workflow)
  - [4.2 The Workflow Diagram](#42-the-workflow-diagram)
  - [4.3 Step-by-Step Process](#43-step-by-step-process)
- [5. Requirement Immutability Enforcement Points](#5-requirement-immutability-enforcement-points)
  - [5.1 By Phase](#51-by-phase)
  - [5.2 Evidence Required at Each Phase](#52-evidence-required-at-each-phase)
- [Troubleshooting](#troubleshooting)
  - [User Changes Requirements Mid-Project](#user-changes-requirements-mid-project)
  - [Requirements Conflict With Each Other](#requirements-conflict-with-each-other)
  - [Agent Delivers Something Different Than Required](#agent-delivers-something-different-than-required)
- [See Also](#see-also)

---

## Table of Contents

- 1. Core Principle
  - 1.1 What Immutable Requirements Means
  - 1.2 Why This Rule Exists
- 2. Orchestration Requirement Enforcement
  - 2.1 At Project Start
  - 2.2 During Planning
  - 2.3 During Execution
  - 2.4 At Review
- 3. Orchestrator Forbidden Actions
  - 3.1 Actions That Violate RULE 14
  - 3.2 Consequences of Violations
- 4. Requirement Issue Workflow
  - 4.1 When to Use This Workflow
  - 4.2 The Workflow Diagram
  - 4.3 Step-by-Step Process
- 5. Requirement Immutability Enforcement Points
  - 5.1 By Phase
  - 5.2 Evidence Required at Each Phase

---

## 1. Core Principle

### 1.1 What Immutable Requirements Means

User requirements cannot be changed, reduced, substituted, or interpreted differently without explicit user approval. The orchestrator MUST:

- Record requirements verbatim
- Treat requirements as constraints, not suggestions
- Halt when requirements conflict
- Escalate all ambiguities to the user

### 1.2 Why This Rule Exists

1. **User intent preservation** - The user knows what they want
2. **Scope creep prevention** - No unauthorized scope reduction
3. **Quality assurance** - Deliverables match expectations
4. **Trust maintenance** - User can rely on requirements being met
5. **Accountability** - Clear record of what was requested

---

## 2. Orchestration Requirement Enforcement

### 2.1 At Project Start

1. Create USER_REQUIREMENTS.md in project root
2. Record all user requirements verbatim
3. Mark the file as IMMUTABLE
4. Do not paraphrase or interpret requirements

**Template:**
```markdown
# USER REQUIREMENTS (IMMUTABLE)

Created: [DATE]
Source: User conversation

## Requirements

1. [VERBATIM REQUIREMENT 1]
2. [VERBATIM REQUIREMENT 2]
3. [VERBATIM REQUIREMENT 3]

## Notes

- These requirements are IMMUTABLE
- Any changes require explicit user approval
- Record user approval with timestamp if changes are made
```

### 2.2 During Planning

1. Verify plan matches requirements exactly
2. Flag any deviations BEFORE implementation begins
3. Escalate issues to user immediately
4. Do not proceed with plan that deviates from requirements

**Verification checklist:**
- [ ] Each requirement has corresponding plan item
- [ ] No plan items contradict requirements
- [ ] No requirements omitted from plan
- [ ] Technology choices match requirements

### 2.3 During Execution

1. Monitor remote agents for requirement compliance
2. Halt on detected violations
3. Report violations immediately to user
4. Do not approve work that violates requirements

**Monitoring checklist:**
- [ ] Agent deliverables match requirements
- [ ] No scope reduction without approval
- [ ] No technology substitutions without approval
- [ ] No feature omissions without approval

### 2.4 At Review

1. Verify implementation matches requirements
2. Reject PRs that deviate without user approval
3. Document compliance status for each requirement
4. Mark requirements as SATISFIED only when fully met

**Review checklist:**
- [ ] Each requirement verified in implementation
- [ ] Test coverage for each requirement
- [ ] Documentation matches requirements
- [ ] User acceptance criteria met

---

## 3. Orchestrator Forbidden Actions

### 3.1 Actions That Violate RULE 14

| Forbidden Action | Why It Violates RULE 14 |
|------------------|------------------------|
| Approving technology substitutions without user consent | Changes implementation from what user requested |
| Accepting reduced scope without user approval | Delivers less than what user requested |
| Auto-resolving requirement conflicts | Makes decisions without user input |
| Proceeding when requirements are ambiguous | Risks delivering wrong thing |
| Interpreting requirements liberally | May not match user intent |
| Assuming "close enough" is acceptable | Requirements are exact, not approximate |

### 3.2 Consequences of Violations

1. User receives incorrect deliverable
2. Trust is broken
3. Rework is required
4. Time and resources wasted
5. User may lose confidence in system

---

## 4. Requirement Issue Workflow

### 4.1 When to Use This Workflow

Use this workflow when:
- A requirement cannot be implemented as stated
- Requirements conflict with each other
- Technology constraints prevent exact implementation
- Requirements are ambiguous or unclear
- Cost/time exceeds expectations

### 4.2 The Workflow Diagram

```
User Requirement -> Feasibility Check -> Issue Found?
                                           | YES
                                           v
                              Generate Issue Report
                                           |
                                           v
                              Present to User
                                           |
                                           v
                              WAIT for Decision
                                           |
                                           v
                              Record Decision
                                           |
                                           v
                              Proceed with User's Choice
```

### 4.3 Step-by-Step Process

1. **Identify the issue** - Document exactly what the problem is
2. **Generate options** - Create 2-3 alternative approaches
3. **Present to user** - Explain the issue and options clearly
4. **WAIT for decision** - Do NOT proceed without user input
5. **Record decision** - Document user's choice with timestamp
6. **Update requirements** - If user approves change, update USER_REQUIREMENTS.md with approval record
7. **Proceed** - Continue with user's chosen approach

---

## 5. Requirement Immutability Enforcement Points

### 5.1 By Phase

| Phase | Enforcement Action |
|-------|-------------------|
| Planning | Verify plan matches requirements |
| Delegation | Include requirements in task instructions |
| Execution | Monitor for compliance |
| Review | Gate 0: Requirement compliance check |
| Closure | Verify all requirements met |

### 5.2 Evidence Required at Each Phase

| Phase | Evidence Required |
|-------|-------------------|
| Planning | Plan-to-requirements mapping document |
| Delegation | Requirements listed in task instructions |
| Execution | Agent reports referencing requirements |
| Review | Compliance checklist for each requirement |
| Closure | User sign-off on requirements satisfaction |

---

## Troubleshooting

### User Changes Requirements Mid-Project

1. Document the change request with timestamp
2. Update USER_REQUIREMENTS.md with new requirement
3. Mark previous requirement as SUPERSEDED (not deleted)
4. Update plan to accommodate new requirement
5. Notify all agents of requirement change

### Requirements Conflict With Each Other

1. Document the conflict clearly
2. Present both requirements to user
3. Ask user to clarify priority or modify one requirement
4. Record user's resolution decision
5. Update USER_REQUIREMENTS.md with resolution

### Agent Delivers Something Different Than Required

1. Do NOT approve the deliverable
2. Document the deviation
3. Present to user with options:
   - a) Reject and redo to match requirement
   - b) Accept deviation (requires requirement change)
4. Record user's decision
5. Proceed with user's choice

---

## See Also

- [orchestrator-guardrails.md](orchestrator-guardrails.md) - Orchestrator role boundaries
- [progress-monitoring.md](progress-monitoring.md) - Proactive monitoring protocol
- [verification-loops.md](verification-loops.md) - 4-verification-loops before PR
