## Table of Contents

- 1 Module entry YAML format
- 2 Assignment entry YAML format
- 3 Field descriptions and valid values

---

Module management commands modify the orchestration state file at `design/state/exec-phase.md`.

## 1 Module Entry Format

```yaml
modules_status:
  - id: "auth-core"           # Kebab-case identifier
    name: "Core Authentication"  # Display name
    status: "pending"         # pending|assigned|in-progress|complete
    assigned_to: null         # Agent ID or null
    github_issue: "#42"       # Linked issue number
    pr: null                  # Linked PR when complete
    verification_loops: 0     # Number of review cycles
    acceptance_criteria: "Support JWT and session tokens"
    priority: "high"          # critical|high|medium|low
```

## 2 Assignment Entry Format

```yaml
active_assignments:
  - agent: "implementer-1"
    agent_type: "ai"
    module: "auth-core"
    github_issue: "#42"
    task_uuid: "task-abc123def456"
    status: "pending_verification"
    instruction_verification:
      status: "awaiting_repetition"
      repetition_received: false
      repetition_correct: false
      questions_asked: 0
      questions_answered: 0
      authorized_at: null
```

## 3 Field Descriptions

| Field | Valid Values | Description |
|-------|-------------|-------------|
| status | pending, assigned, in-progress, complete | Module lifecycle state |
| priority | critical, high, medium, low | Urgency level |
| assigned_to | Agent ID or null | Current agent working on module |
| github_issue | Issue reference (e.g. "#42") | Linked GitHub Issue |
| pr | PR reference or null | Linked pull request when complete |
| verification_loops | Integer >= 0 | Number of review cycles completed |
