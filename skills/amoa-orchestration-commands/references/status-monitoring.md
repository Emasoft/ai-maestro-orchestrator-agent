# Status Monitoring

## Contents

- 2.1 Understanding the orchestration status output
- 2.2 Reading module status indicators
- 2.3 Interpreting agent registry information
- 2.4 Tracking active assignments and polling
- 2.5 Using verbose mode for detailed diagnostics

---

## 2.1 Understanding the Orchestration Status Output

The `/orchestration-status` command displays a comprehensive view of implementation progress. The output is divided into sections:

### Output Structure

```
╔════════════════════════════════════════════════════════════════╗
║                 ORCHESTRATION PHASE STATUS                     ║
╠════════════════════════════════════════════════════════════════╣
║ Plan ID: plan-20260108-143022                                  ║
║ Status: executing                                              ║
║ Progress: 1/3 modules complete (33%)                           ║
╠════════════════════════════════════════════════════════════════╣
║ MODULE STATUS                                                  ║
╠════════════════════════════════════════════════════════════════╣
║ [✓] auth-core      #42  implementer-1  complete                ║
║ [→] oauth-google   #43  implementer-2  in-progress (Poll: 5m)  ║
║ [ ] auth-2fa       #44  -              pending                 ║
╠════════════════════════════════════════════════════════════════╣
║ REGISTERED AGENTS                                              ║
╠════════════════════════════════════════════════════════════════╣
║ AI Agents:                                                     ║
║   - implementer-1 (helper-agent-generic)                       ║
║   - implementer-2 (helper-agent-python)                        ║
║ Human Developers:                                              ║
║   - dev-alice (GitHub)                                         ║
╠════════════════════════════════════════════════════════════════╣
║ ACTIVE ASSIGNMENTS                                             ║
╠════════════════════════════════════════════════════════════════╣
║ oauth-google → implementer-2                                   ║
║   Status: working                                              ║
║   Instruction Verification: ✓ verified                         ║
║   Last Poll: 5 minutes ago                                     ║
║   Issues Reported: 0                                           ║
╚════════════════════════════════════════════════════════════════╝
```

### Header Section Fields

| Field | Description |
|-------|-------------|
| Plan ID | Unique identifier for the approved plan |
| Status | Current phase status: `pending`, `executing`, `complete` |
| Progress | Completion percentage (complete/total modules) |

### When to Run Status Check

- Every 10-15 minutes during active orchestration
- After assigning a new module
- When an agent reports completion
- When debugging stuck progress
- Before attempting to exit

---

## 2.2 Reading Module Status Indicators

### Status Icons

| Icon | Status | Meaning |
|------|--------|---------|
| `[ ]` | pending | Not yet assigned or started |
| `[→]` | in-progress | Being worked on by an agent |
| `[✓]` | complete | Implementation finished and verified |
| `[!]` | blocked | Agent stuck, needs intervention |
| `[?]` | awaiting | Waiting for verification or review |

### Module Line Format

```
║ [ICON] MODULE_ID    ISSUE#  AGENT         STATUS (POLL_INFO)  ║
```

**Fields**:
- `ICON`: Visual status indicator
- `MODULE_ID`: Unique module identifier from plan
- `ISSUE#`: GitHub issue number (if synced)
- `AGENT`: Assigned agent ID or `-` if unassigned
- `STATUS`: Text status (pending/in-progress/complete)
- `POLL_INFO`: Time since last poll (if in progress)

### Understanding Poll Timing

The `(Poll: Xm)` suffix shows time since last progress check:
- `(Poll: 5m)` - Polled 5 minutes ago, healthy
- `(Poll: 20m)` - Overdue for polling (should be every 10-15m)
- `(Poll: 1h)` - Severely overdue, may indicate stuck agent

---

## 2.3 Interpreting Agent Registry Information

### Agent Types

**AI Agents**: Remote Claude Code sessions coordinated via AI Maestro
```
AI Agents:
  - implementer-1 (helper-agent-generic)
  - implementer-2 (helper-agent-python)
```

Format: `AGENT_ID (SESSION_NAME)`

**Human Developers**: GitHub users assigned via Kanban
```
Human Developers:
  - dev-alice (GitHub)
```

Format: `AGENT_ID (GitHub)`

### Agent Capabilities

| Agent Type | Communication | Task Assignment | Progress Tracking |
|------------|---------------|-----------------|-------------------|
| AI Agent | AI Maestro | `/assign-module` | `/check-agents` |
| Human Dev | GitHub Issues | Kanban assign | GitHub notifications |

### When Registry is Empty

```
AI Agents: (none registered)
Human Developers: (none registered)
```

This means no agents have been registered yet. Use `/register-agent` to add agents before assigning modules.

---

## 2.4 Tracking Active Assignments and Polling

### Assignment Details

Each active assignment shows:

```
oauth-google → implementer-2
  Status: working
  Instruction Verification: ✓ verified
  Last Poll: 5 minutes ago
  Issues Reported: 0
  Next Poll Due: 10 minutes
```

### Assignment Fields

| Field | Description |
|-------|-------------|
| Module → Agent | Assignment mapping |
| Status | `assigned`, `working`, `review`, `complete` |
| Instruction Verification | Whether agent confirmed understanding |
| Last Poll | Time since last progress check |
| Issues Reported | Count of problems raised during polls |
| Next Poll Due | When next poll should occur |

### Instruction Verification States

| State | Icon | Meaning |
|-------|------|---------|
| pending | ` ` | Verification not started |
| awaiting_repetition | `?` | Waiting for agent to repeat requirements |
| verified | `✓` | Agent confirmed understanding |
| correcting | `!` | Misunderstanding detected, re-verifying |

**Critical**: Never let agents start work without `✓ verified` status!

### Polling Best Practices

1. **Poll every 10-15 minutes** - Not too often (interrupts), not too sparse (loses track)
2. **Use mandatory questions**:
   - "What have you completed since last update?"
   - "Are you blocked on anything?"
   - "What is your estimated completion time?"
3. **Track issues** - Document any problems reported
4. **Unblock quickly** - If agent reports blocker, address immediately

---

## 2.5 Using Verbose Mode for Detailed Diagnostics

### Enabling Verbose Output

```bash
/orchestration-status --verbose
```

Or short form:
```bash
/orchestration-status -v
```

### Additional Verbose Information

**Module Details**:
```
║ [✓] auth-core      #42  implementer-1  complete                ║
║     Criteria: Users can register with email and password        ║
║     PR: #55                                                     ║
```

Shows:
- Acceptance criteria for each module
- Pull request number if submitted

**Polling History**:
```
oauth-google → implementer-2
  ...
  Next Poll Due: 2026-01-09T11:45:00
  Poll History:
    - 10:30 - Started, no issues
    - 10:45 - 50% complete
    - 11:00 - Waiting for review
```

### Filtering Output

**Agents only**:
```bash
/orchestration-status --agents-only
```

Shows only registered agents section, useful for quick agent overview.

**Modules only**:
```bash
/orchestration-status --modules-only
```

Shows only module status section, useful for implementation tracking.

### Summary Messages

At the end of output, status provides context:

**Work remaining**:
```
2 modules remaining. Exit blocked until complete.
```

**Verification in progress**:
```
All modules complete. 3 verification loops remaining.
```

**All complete**:
```
✓ All work complete. Exit allowed.
```

---

## Orchestrator Status vs Orchestration Status

These are two different commands:

| Command | Purpose | State File |
|---------|---------|------------|
| `/orchestration-status` | Module/agent progress | `design/state/exec-phase.md` |
| `/orchestrator-status` | Loop state and tasks | `design/state/loop.md` |

Use **orchestration-status** when:
- Tracking module implementation progress
- Checking agent assignments
- Monitoring instruction verification

Use **orchestrator-status** when:
- Checking task sources (Claude Tasks, GitHub, etc.)
- Viewing iteration count
- Debugging stop hook behavior
