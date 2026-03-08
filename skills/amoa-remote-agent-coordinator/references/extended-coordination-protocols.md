---
name: extended-coordination-protocols
description: Multi-agent coordination protocols for decisions, updates, reassignment, and verification.
---

# Extended Coordination Protocols
## Contents
- Core decision trees
- Mid-task updates
- Reassignment communication
- Blocker reports
- Multi-project coordination
- Verification feedback (loops 2-4)

---

## 1. Core Decision Trees

**See [decision-trees-core.md](./decision-trees-core.md) for 7 core decision trees:**
<!-- TOC: 1. Escalate vs Retry Decision Tree | 2. Reassign vs Wait Decision Tree | 3. Conflicting Multi-Agent Responses Decision Tree | 4. Verification Loop Outcome Decision Tree | 5. Agent Recovery Decision Tree | 6. Direct Handling vs Delegation Decision Tree | 7. Post-Task Interview Escalation Decision Tree | Cross-References Between Trees -->
- Escalate vs Retry — agent reports issue: retry count, severity, time elapsed
- Reassign vs Wait — agent unresponsive: time, task priority, available agents
- Conflicting Multi-Agent Responses — two agents give contradictory results
- Verification Loop Outcome — per-loop criteria for loops 1-4 + 5th decision
- Agent Recovery Decision — original recovered after replacement: keep vs revert
- Direct Handling vs Delegation — AMOA handles vs delegates
- Post-Task Interview Escalation — REVISE cycle count before escalation

---

## 2. Mid-Task Updates

**See [mid-task-update-templates.md](./mid-task-update-templates.md) for:**
<!-- TOC: 1. AMCOS Mid-Task Requirement Update (AMCOS to AMOA) | 2. AMOA Acknowledgment of Requirement Update (AMOA to AMCOS) | 3. Module Modification Notification (AMOA to Agent) | 4. Priority Change Notification (AMOA to Agent) | 5. AMAMA User Decision Response (AMAMA to AMOA) | 6. Mid-Task Update Severity Decision Tree -->
- AMCOS Mid-Task Requirement Update to AMOA + relay to agent
- Module Modification Notification + agent ACK
- Priority Change Notification + agent ACK
- AMAMA user decision relay after immutable requirement escalation
- Decision tree: Minor (relay) / Major (pause, re-verify) / Breaking (stop, escalate)

---

## 3. Reassignment Communication

**See [reassignment-communication-templates.md](./reassignment-communication-templates.md) for:**
<!-- TOC: 1. Reassignment Notification to Old Agent (AMOA to Old Agent) | 2. Old Agent Work Summary Response (Old Agent to AMOA) | 3. Reassignment Assignment to New Agent (AMOA to New Agent) | 4. Agent Recovery Decision Notification (AMOA to Both Agents) | 5. AMOA Response to Agent Recovery Decision | 6. Reassignment Flow Decision Tree | See Also -->
- Reassignment Notification to Old Agent + work-summary response
- Reassignment Assignment to New Agent (with context)
- Agent Recovery Decision Notification (both agents) + AMOA response
- Decision tree: Old agent cooperates / unresponsive / disputes

---

## 4. Blocker Reports

**See [blocker-report-templates.md](./blocker-report-templates.md) for:**
<!-- TOC: 1. Agent Blocker Report (Agent to AMOA) | 2. AMOA Blocker Triage Response (AMOA to Agent) | 3. AMOA Blocker Resolution Notification (AMOA to Agent) | 4. Blocker Triage Decision Tree | 5. Blocker vs Bug Report Decision Guide -->
- Agent Blocker Report to AMOA (structured JSON: type, description, impact, workaround)
- AMOA Triage Response (unblock/escalate/workaround)
- AMOA Blocker Resolution Notification
- Decision tree: Technical (fix/reroute) / External (escalate) / Requirement (escalate to user)

---

## 5. Multi-Project Coordination

**See [multi-project-coordination-templates.md](./multi-project-coordination-templates.md) for:**
<!-- TOC: 1. Cross-Project Dependency Notification (AMOA to AMOA via AMCOS) | 2. Cross-Project Status Request (AMOA to AMCOS to Other AMOA) | 3. Cross-Project Status Response (Other AMOA to AMCOS to AMOA) | 4. Human Developer Task Assignment (AMOA to GitHub) | 5. Human Developer Completion Report (GitHub to AMOA) | 6. Cross-Project Conflict Decision Tree -->
- Cross-Project Dependency Notification (AMOA to AMOA via AMCOS)
- Cross-Project Status Request/Response
- Human Developer Assignment (GitHub issue format) + completion report
- Decision tree: Wait for dependency / Proceed independently / Escalate to AMCOS

---

## 6. Verification Feedback (Loops 2-4)

**See [verification-feedback-templates.md](./verification-feedback-templates.md) for:**
<!-- TOC: 1. Verification Loop 2 Feedback (AMOA sends to Agent) | 2. Verification Loop 3 Feedback (AMOA sends to Agent) | 3. Verification Loop 4 Feedback (AMOA sends to Agent) | 4. Verification Restart Notification (AMOA sends to Agent) | 5. Verification Completion Summary (AMOA sends to AMCOS) | 6. Verification Loop Outcome Decision Tree -->
- Loop 2-4 feedback templates with progressive focus areas
- Verification restart notification (after failed 5th attempt)
- Verification completion summary (audit trail of all loops)
- Decision tree: Issues found / No issues / Agent skipping / Endless loop
