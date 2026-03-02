---
name: extended-coordination-protocols
description: Extended coordination protocols for multi-agent scenarios including decision trees, mid-task updates, reassignment, blockers, multi-project coordination, and verification feedback.
---

# Extended Coordination Protocols

## Contents

- [1. Core Decision Trees](#1-core-decision-trees) - When deciding whether to escalate, reassign, retry, or handle directly
- [2. Mid-Task Updates](#2-mid-task-updates) - When relaying requirement changes or priority shifts to agents mid-task
- [3. Reassignment Communication](#3-reassignment-communication) - When reassigning tasks between agents due to failure or recovery
- [4. Blocker Reports](#4-blocker-reports) - When agents report blockers and the orchestrator must triage
- [5. Multi-Project Coordination](#5-multi-project-coordination) - When tasks span multiple projects with cross-dependencies
- [6. Verification Feedback (Loops 2-4)](#6-verification-feedback-loops-2-4) - When providing progressive feedback during the 4-verification-loop cycle

---

## 1. Core Decision Trees

**See [decision-trees-core.md](./decision-trees-core.md) for 7 core decision trees:**
- Escalate vs Retry — agent reports issue: retry count, severity, time elapsed
- Reassign vs Wait — agent unresponsive: time, task priority, available agents
- Conflicting Multi-Agent Responses — two agents give contradictory results
- Verification Loop Outcome — per-loop criteria for loops 1-4 + 5th decision
- Agent Recovery Decision — original recovered after replacement: keep vs revert
- Direct Handling vs Delegation — EOA handles vs delegates
- Post-Task Interview Escalation — REVISE cycle count before escalation

---

## 2. Mid-Task Updates

**See [mid-task-update-templates.md](./mid-task-update-templates.md) for:**
- ECOS Mid-Task Requirement Update to EOA + relay to agent
- Module Modification Notification + agent ACK
- Priority Change Notification + agent ACK
- EAMA user decision relay after immutable requirement escalation
- Decision tree: Minor (relay) / Major (pause, re-verify) / Breaking (stop, escalate)

---

## 3. Reassignment Communication

**See [reassignment-communication-templates.md](./reassignment-communication-templates.md) for:**
- Reassignment Notification to Old Agent + work-summary response
- Reassignment Assignment to New Agent (with context)
- Agent Recovery Decision Notification (both agents) + EOA response
- Decision tree: Old agent cooperates / unresponsive / disputes

---

## 4. Blocker Reports

**See [blocker-report-templates.md](./blocker-report-templates.md) for:**
- Agent Blocker Report to EOA (structured JSON: type, description, impact, workaround)
- EOA Triage Response (unblock/escalate/workaround)
- EOA Blocker Resolution Notification
- Decision tree: Technical (fix/reroute) / External (escalate) / Requirement (escalate to user)

---

## 5. Multi-Project Coordination

**See [multi-project-coordination-templates.md](./multi-project-coordination-templates.md) for:**
- Cross-Project Dependency Notification (EOA to EOA via ECOS)
- Cross-Project Status Request/Response
- Human Developer Assignment (GitHub issue format) + completion report
- Decision tree: Wait for dependency / Proceed independently / Escalate to ECOS

---

## 6. Verification Feedback (Loops 2-4)

**See [verification-feedback-templates.md](./verification-feedback-templates.md) for:**
- Loop 2-4 feedback templates with progressive focus areas
- Verification restart notification (after failed 5th attempt)
- Verification completion summary (audit trail of all loops)
- Decision tree: Issues found / No issues / Agent skipping / Endless loop
