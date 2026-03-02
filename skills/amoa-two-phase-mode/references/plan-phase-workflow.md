# Plan Phase Workflow

## Contents

- 1. Entering Plan Phase
  - 1.1 Using /start-planning command
  - 1.2 State file initialization
- 2. Planning Activities
  - 2.1 Gathering user goals
  - 2.2 Creating USER_REQUIREMENTS.md
  - 2.3 Designing architecture
  - 2.4 Breaking down into modules
  - 2.5 Defining acceptance criteria
- 3. Modifying the Plan
  - 3.1 Adding requirements with /add-requirement
  - 3.2 Modifying requirements with /modify-requirement
  - 3.3 Removing requirements with /remove-requirement
- 4. Plan Phase Completion
  - 4.1 Exit criteria checklist
  - 4.2 Using /approve-plan to transition
  - 4.3 GitHub Issues creation

---

## 1. Entering Plan Phase

### 1.1 Using /start-planning command

To enter Plan Phase Mode, run:

```
/start-planning "Your project goal here"
```

**Example:**
```
/start-planning "Implement user authentication with OAuth2 and session management"
```

The command:
1. Creates the plan phase state file
2. Locks the user goal (immutable)
3. Initializes requirements tracking
4. Sets status to "drafting"

### 1.2 State file initialization

The command creates `design/state/plan-phase.md` with:

```yaml
---
phase: "planning"
plan_id: "plan-YYYYMMDD-HHMMSS"
status: "drafting"
created_at: "ISO timestamp"

goal: "Your project goal"
goal_locked: true

requirements_file: "USER_REQUIREMENTS.md"
requirements_complete: false
requirements_sections:
  - name: "Functional Requirements"
    status: "pending"
  - name: "Non-Functional Requirements"
    status: "pending"
  - name: "Architecture Design"
    status: "pending"

modules: []

plan_phase_complete: false
exit_criteria:
  - "USER_REQUIREMENTS.md complete"
  - "All modules defined with acceptance criteria"
  - "GitHub Issues created for all modules"
  - "User approved the plan"
---
```

---

## 2. Planning Activities

### 2.1 Gathering user goals

The orchestrator must:
1. Clarify any ambiguous aspects of the goal
2. Identify constraints (technical, timeline, budget)
3. Document assumptions
4. Confirm scope with user

**Important:** The goal is LOCKED once entered. Changes require explicit user approval via `/modify-requirement`.

### 2.2 Creating USER_REQUIREMENTS.md

Create a comprehensive requirements document at project root:

```markdown
# USER_REQUIREMENTS.md

## Project Goal
[Locked goal from /start-planning]

## Functional Requirements
- FR-001: [Requirement description]
- FR-002: [Requirement description]
...

## Non-Functional Requirements
- NFR-001: [Performance/security/etc requirement]
...

## Constraints
- [Technical constraints]
- [Timeline constraints]
...

## Assumptions
- [Documented assumptions]
...

## Out of Scope
- [Explicitly excluded items]
...
```

### 2.3 Designing architecture

Document the system architecture:
1. Component diagram
2. Data flow
3. Technology stack decisions
4. Integration points
5. Security considerations

### 2.4 Breaking down into modules

Each module represents an independently implementable unit:

```yaml
modules:
  - id: "auth-core"
    name: "Core Authentication"
    description: "User login, logout, session management"
    priority: "high"
    acceptance_criteria: "Users can login/logout, sessions persist"
    dependencies: []
    status: "planned"
  - id: "oauth-google"
    name: "Google OAuth2 Integration"
    description: "Google sign-in support"
    priority: "medium"
    acceptance_criteria: "Users can sign in with Google"
    dependencies: ["auth-core"]
    status: "pending"
```

### 2.5 Defining acceptance criteria

Each module MUST have:
1. **Clear success criteria** - Unambiguous completion conditions
2. **Testable conditions** - Can be verified programmatically
3. **No ambiguity** - Single interpretation possible

**Bad example:** "Authentication should work"
**Good example:** "Users can login with email/password, receive JWT token valid for 24h, and token refresh works"

---

## 3. Modifying the Plan

### 3.1 Adding requirements with /add-requirement

```
/add-requirement "New feature description" --module-name "Module Name" --priority high
```

This:
1. Creates new module in state file
2. Adds to requirements tracking
3. Updates exit criteria

### 3.2 Modifying requirements with /modify-requirement

```
/modify-requirement auth-core --add-criteria "Support 2FA authentication"
```

This:
1. Updates module acceptance criteria
2. Notifies if module already assigned (in orchestration phase)
3. Logs change in state file

### 3.3 Removing requirements with /remove-requirement

```
/remove-requirement legacy-api-support
```

**Restriction:** Can only remove modules with status "pending" or "planned" (not started).

---

## 4. Plan Phase Completion

### 4.1 Exit criteria checklist

Before running `/approve-plan`, verify:

- [ ] USER_REQUIREMENTS.md exists and is complete
- [ ] All functional requirements documented
- [ ] All non-functional requirements documented
- [ ] Architecture designed
- [ ] All modules defined with:
  - [ ] Clear acceptance criteria
  - [ ] Priority assigned
  - [ ] Dependencies identified
- [ ] User has reviewed and approved requirements

### 4.2 Using /approve-plan to transition

```
/approve-plan
```

The command:
1. Validates all exit criteria met
2. Creates GitHub Issues for all modules
3. Sets `plan_phase_complete: true`
4. Outputs summary of created issues

**If validation fails:** Command outputs which criteria are not met.

### 4.3 GitHub Issues creation

For each module, creates a GitHub Issue with:
- Title: `[Module] {module_name}`
- Body: Module description + acceptance criteria
- Labels: `module`, `priority-{priority}`, `status:todo`
- Links to plan ID

**Example Issue:**
```markdown
## Module: Core Authentication

### Description
Implementation of user login, logout, and session management.

### Acceptance Criteria
- [ ] Users can login with email/password
- [ ] Users receive JWT token valid for 24h
- [ ] Token refresh works correctly
- [ ] Logout invalidates session

### Priority
high

### Related
- Plan ID: plan-20260108-143022
- Module ID: auth-core
```

---

## Stop Hook Behavior

During Plan Phase, the stop hook blocks exit if:
- `plan_phase_complete: false` in state file

**Message shown:**
```
Plan Phase incomplete. Cannot exit.

Missing criteria:
- USER_REQUIREMENTS.md not complete
- 2 modules missing acceptance criteria

Run /planning-status for details.
```
