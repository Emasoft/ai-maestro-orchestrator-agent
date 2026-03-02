---
name: eoa-check-agents
description: "Poll all active remote agents for progress with MANDATORY questions"
argument-hint: "[--agent AGENT_ID]"
allowed-tools: ["Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/eoa_check_remote_agents.py:*)"]
---

# Check Agents Command

Poll all active remote agents for progress updates. Implements the MANDATORY Proactive Progress Polling Protocol.

## Usage

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_check_remote_agents.py" $ARGUMENTS
```

## Options

| Option | Description |
|--------|-------------|
| `--agent` | Poll only specific agent |

## MANDATORY: Proactive Progress Polling Protocol

**CRITICAL**: Every progress poll MUST include these 6 mandatory questions. This is NON-SKIPPABLE.

### Poll Message Template

```markdown
Subject: [POLL] Module: {module_name} - Progress Check #{poll_number}

## Status Request

Please provide:
1. **Current progress** (% complete, what's done)
2. **Next steps** (what you're working on now)

## MANDATORY Questions (Answer ALL)

3. **Are there any issues or problems?** (technical, environmental, dependencies)
4. **Is anything unclear?** (requirements, acceptance criteria, expected behavior)
5. **Any unforeseen difficulties?** (complexity higher than expected, missing info)
6. **Do you need anything from me?** (documentation, clarification, decisions)

If all is clear, respond: "No blockers. Proceeding as planned."

Expected response time: 5 minutes
```

## Why Mandatory Questions?

Remote agents may:
- Encounter unforeseen difficulties
- Have unclear requirements they didn't raise initially
- Be blocked but not proactively report it
- Discover issues requiring approach changes

**The orchestrator must ACTIVELY ASK** - never assume "no news is good news."

## Orchestrator Response Actions

Based on agent responses:

| Agent Response | Orchestrator Action |
|----------------|---------------------|
| Reports issue | Provide solution or delegate research |
| Something unclear | Provide clarification immediately |
| Unforeseen difficulty | Evaluate: adapt approach or reassign |
| Needs documentation | Create/provide detailed docs |
| Needs decision | Make decision or escalate to user |
| Higher complexity | Adjust approach, potentially split task |
| Blocked | Unblock immediately (highest priority) |

## Polling Frequency

- **Default**: Every 10-15 minutes
- **Blocked agent**: Every 5 minutes until unblocked
- **Near completion močno**: More frequent checks

## State File Tracking

```yaml
progress_polling:
  last_poll: "2026-01-08T16:30:00+00:00"
  poll_count: 3
  poll_history:
    - poll_number: 1
      timestamp: "2026-01-08T16:00:00+00:00"
      status: "in_progress"
      issues_reported: false
    - poll_number: 2
      timestamp: "2026-01-08T16:15:00+00:00"
      status: "in_progress"
      issues_reported: true
      issue_description: "Unclear token expiry"
      issue_resolved: true
      resolution: "Provided spec document"
  next_poll_due: "2026-01-08T16:45:00+00:00"
```

## Examples

```bash
# Poll all active agents
/check-agents

# Poll specific agent
/check-agents --agent implementer-1
```

## Output

```
Polling 2 active agents...

implementer-1 (auth-core):
  Progress: 60% - JWT implementation complete
  Issues: None reported
  Next poll: 15 minutes

implementer-2 (oauth-google):
  Progress: 30% - OAuth flow started
  Issues: "Unclear callback URL format"
  Action Required: Provide clarification

1 agent needs attention. Use the mandatory questions to follow up.
```

## Related Commands

- `/orchestration-status` - Full status view
- `/assign-module` - Assign modules
- `/reassign-module` - Change assignment
