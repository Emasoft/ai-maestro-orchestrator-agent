---
name: eoa-generate-replacement-handoff
description: "Generate a comprehensive handoff document for a replacement agent"
argument-hint: "--failed-agent <ID> --new-agent <ID> [--include-tasks] [--include-context] [--partial] [--flag-gaps]"
allowed-tools: ["Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/eoa_generate_replacement_handoff.py:*)"]
---

# Generate Replacement Handoff Command

Generate a comprehensive handoff document when replacing a failed agent. Compiles all task context, requirements, progress, and communication history into a document for the replacement agent.

## Usage

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_generate_replacement_handoff.py" $ARGUMENTS
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--failed-agent` | Yes | ID of the agent being replaced |
| `--new-agent` | Yes | ID of the replacement agent |
| `--include-tasks` | No | Include full task details (default: true) |
| `--include-context` | No | Include communication history (default: true) |
| `--partial` | No | Generate even with incomplete data |
| `--flag-gaps` | No | Explicitly mark missing information |
| `--output` | No | Custom output filename |
| `--upload` | No | Auto-upload to GitHub issue |

## When to Use

| Scenario | Use This Command |
|----------|------------------|
| ECOS sends replacement notification | Yes |
| Agent becomes unresponsive | Yes |
| Manual agent replacement | Yes |
| Context loss recovery | Yes |
| Pre-emptive handoff preparation | Yes |

## What This Command Does

### 1. Compiles Task Context

Gathers from multiple sources:
- **State File**: Module assignments, task UUIDs, status
- **GitHub Issues**: Requirements, discussions, blockers
- **AI Maestro**: Communication history, clarifications
- **Design Docs**: Specifications, requirements

### 2. Analyzes Git State

Examines the failed agent's branch:
- Modified files
- Uncommitted changes
- Last commit (TDD phase)
- Commits ahead of main

### 3. Generates Handoff Document

Creates comprehensive handoff with:
- Task assignments and requirements
- Current progress with checkpoints
- Technical context (files, dependencies)
- Communication history (clarifications, decisions)
- Clear next steps for new agent
- Verification requirements

### 4. Optionally Uploads

With `--upload`:
- Uploads to relevant GitHub issue
- Returns URL for AI Maestro notification

## Handoff Document Structure

```markdown
# Agent Replacement Handoff

## Handoff Metadata
- From, To, Timestamp, Reason, Urgency

## RULE 14: USER REQUIREMENTS (IMMUTABLE)
- Exact user specifications

## Task Context
- All assigned tasks with full details
- Acceptance criteria

## Current Progress
- Completed steps
- In-progress work
- Pending steps

## Technical Context
- Modified files
- Git branch status
- Dependencies
- Build/test status

## Communication History
- Key clarifications
- Decisions made

## Blockers and Known Issues
- Active blockers
- Attempted solutions

## Next Steps
- Specific first action
- Continuation point

## Verification Requirements
- ACK format
- Required confirmations
```

## Examples

### Standard Replacement

```bash
# Generate full handoff
/eoa-generate-replacement-handoff --failed-agent implementer-1 --new-agent implementer-2 --include-tasks --include-context

# Output: replacement-handoff-implementer-1-to-implementer-2-20260131T143000Z.md
```

### Partial Handoff (Incomplete Data)

```bash
# Generate with gaps flagged
/eoa-generate-replacement-handoff --failed-agent implementer-1 --new-agent implementer-2 --partial --flag-gaps

# Output includes sections like:
# ## Technical Context
# **Git Analysis**: UNAVAILABLE (flagged as gap)
```

### Auto-Upload to GitHub

```bash
# Generate and upload
/eoa-generate-replacement-handoff --failed-agent implementer-1 --new-agent implementer-2 --upload

# Output: URL of uploaded handoff
# https://github.com/owner/repo/issues/42#issuecomment-123456
```

### Custom Output File

```bash
# Specify output filename
/eoa-generate-replacement-handoff --failed-agent implementer-1 --new-agent implementer-2 --output "urgent-handoff.md"
```

## Output Files

| File | Location | Content |
|------|----------|---------|
| Handoff document | `docs_dev/handoffs/` | Main handoff |
| Uncommitted patch | Same directory | Git patch if applicable |
| Context compilation | Same directory | Raw compiled data |

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| "Agent not found" | Invalid agent ID | Check state file for correct ID |
| "No assignments" | Agent has no tasks | Verify agent was assigned work |
| "State file missing" | State not initialized | Reconstruct from GitHub |
| "Git error" | Cannot access branch | Use `--partial --flag-gaps` |

## Integration with ECOS

This command is typically triggered by an ECOS replacement notification:

```
1. ECOS → EOA: Agent replacement required
2. EOA: /eoa-generate-replacement-handoff ...
3. EOA: /eoa-reassign-kanban-tasks ...
4. EOA → New Agent: Handoff document
5. New Agent → EOA: ACK
6. EOA → ECOS: Replacement complete
```

## Related Commands

- `/eoa-reassign-kanban-tasks` - Reassign GitHub Project cards
- `/eoa-check-agents` - Monitor agent status
- `/eoa-register-agent` - Register new agent

## Related Skills

- `eoa-agent-replacement` - Full replacement workflow
- `eoa-remote-agent-coordinator` - Agent registration and assignment
- `eoa-remote-agent-coordinator` - Remote agent communication
