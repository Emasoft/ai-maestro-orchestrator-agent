---
name: eoa-reassign-kanban-tasks
description: "Reassign GitHub Project kanban tasks from one agent to another"
argument-hint: "--from-agent <ID> --to-agent <ID> --project-id <ID> [--dry-run]"
allowed-tools: ["Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/eoa_reassign_kanban_tasks.py:*)"]
---

# Reassign Kanban Tasks Command

Reassign all GitHub Project tasks from a failed agent to a replacement agent. Updates issue assignees, labels, and adds audit comments for traceability.

## Usage

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_reassign_kanban_tasks.py" $ARGUMENTS
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--from-agent` | Yes | ID of the agent to reassign FROM |
| `--to-agent` | Yes | ID of the agent to reassign TO |
| `--project-id` | No | GitHub Project ID (auto-detected if not specified) |
| `--project-name` | No | GitHub Project name (alternative to ID) |
| `--dry-run` | No | Show what would be changed without making changes |
| `--handoff-url` | No | URL of handoff document to include in comments |
| `--reason` | No | Reason for reassignment (default: "agent_replacement") |

## When to Use

| Scenario | Use This Command |
|----------|------------------|
| After generating replacement handoff | Yes |
| Agent replaced by ECOS | Yes |
| Manual task redistribution | Yes |
| Load balancing between agents | Yes |
| Agent going offline | Yes |

## What This Command Does

### 1. Finds All Assigned Tasks

Searches for tasks assigned to the old agent:
- By GitHub username (if agent is human)
- By agent ID label (if using label-based assignment)
- By state file cross-reference

### 2. Updates Issue Assignees

For each issue:
```bash
gh issue edit $ISSUE --remove-assignee "@old-agent" --add-assignee "@new-agent"
```

### 3. Updates Labels

Changes assignment tracking labels:
```bash
gh issue edit $ISSUE --remove-label "assigned:old-agent" --add-label "assigned:new-agent" --add-label "reassigned"
```

### 4. Adds Audit Comments

Adds a comment to each issue documenting the reassignment:

```markdown
## Agent Reassignment Notice

| Field | Value |
|-------|-------|
| **Previous Agent** | @old-agent |
| **New Agent** | @new-agent |
| **Reason** | agent_replacement |
| **Timestamp** | 2026-01-31T14:30:00Z |

### Handoff Document
Full context for new agent (include the handoff document path here)

*Automated reassignment by EOA*
```

### 5. Logs Reassignment

Records all changes for audit:
- Issues updated
- Labels changed
- Comments added
- Timestamp

## Examples

### Standard Reassignment

```bash
# Reassign all tasks from implementer-1 to implementer-2
/eoa-reassign-kanban-tasks --from-agent implementer-1 --to-agent implementer-2

# Output:
# Reassigning tasks from implementer-1 to implementer-2
# - Issue #42: auth-core module -> reassigned
# - Issue #43: token-refresh -> reassigned
# Total: 2 issues reassigned
```

### With Project ID

```bash
# Specify project explicitly
/eoa-reassign-kanban-tasks --from-agent implementer-1 --to-agent implementer-2 --project-id 12345
```

### With Handoff URL

```bash
# Include handoff document link in comments
/eoa-reassign-kanban-tasks --from-agent implementer-1 --to-agent implementer-2 --handoff-url "https://github.com/owner/repo/issues/42#issuecomment-123456"
```

### Dry Run (Preview Changes)

```bash
# See what would be changed without making changes
/eoa-reassign-kanban-tasks --from-agent implementer-1 --to-agent implementer-2 --dry-run

# Output:
# [DRY RUN] Would reassign tasks from implementer-1 to implementer-2:
# - Issue #42: Would change assignee from @old to @new
# - Issue #43: Would change assignee from @old to @new
# No changes made.
```

### Custom Reason

```bash
# Specify custom reason for reassignment
/eoa-reassign-kanban-tasks --from-agent implementer-1 --to-agent implementer-2 --reason "load_balancing"
```

## What Gets Preserved

When reassigning, these are PRESERVED (not changed):

| Field | Preserved | Reason |
|-------|-----------|--------|
| Issue body | Yes | Requirements |
| Milestone | Yes | Deadline context |
| Priority labels | Yes | Work order |
| Status labels | Yes | Workflow state |
| Previous comments | Yes | Discussion history |
| Project column | Yes | Board position |

## What Gets Updated

| Field | Updated To | Reason |
|-------|------------|--------|
| Assignee | New agent | Ownership |
| `assigned:*` label | New agent ID | Tracking |
| `reassigned` label | Added | Audit trail |

## Handling Edge Cases

### Open Pull Requests

If the old agent has open PRs:

```
Note: PR #123 is open from old-agent's branch.
PR author cannot be changed. Options:
1. New agent continues on same branch
2. New agent creates new PR
3. Close old PR, create new one

Added comment to PR noting reassignment.
```

### Uncommitted Work

If old agent had uncommitted changes:

```
Warning: Uncommitted changes detected on branch feature/auth-core
Patch saved to: uncommitted_work.patch
Include in handoff document for new agent review.
```

### Conflicting Assignments

If new agent already has this task:

```
Warning: Issue #42 already has @new-agent as assignee
Skipping assignee change, updating labels only.
```

## Output

### Successful Reassignment

```
Reassignment Complete
=====================
From: implementer-1
To: implementer-2
Project: Auth System v2

Issues Reassigned:
- #42: auth-core module (in_progress)
- #43: token-refresh (pending)

Labels Updated: 2 issues
Comments Added: 2 issues
Audit Log: logs/reassignment-20260131T143000Z.yaml

State file updated: design/state.yaml
```

### Partial Success

```
Reassignment Partially Complete
================================
From: implementer-1
To: implementer-2

Succeeded:
- #42: auth-core module

Failed:
- #43: GitHub API rate limit exceeded

Retry failed issues with:
/eoa-reassign-kanban-tasks --from-agent implementer-1 --to-agent implementer-2 --issues "#43"
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| "No issues found" | No tasks assigned to old agent | Verify agent ID |
| "Agent not found" | Invalid agent ID | Check state file |
| "Rate limit" | GitHub API exhausted | Wait for reset, retry |
| "Permission denied" | Insufficient GitHub access | Re-authenticate |
| "Project not found" | Invalid project ID | Find correct ID |

## Verification

After reassignment, verify changes:

```bash
# Check no issues still assigned to old agent
gh issue list --assignee "@old-agent" --json number
# Should return empty

# Check issues now assigned to new agent
gh issue list --assignee "@new-agent" --label "reassigned"
# Should list reassigned issues
```

## Integration with Replacement Workflow

This command is typically used after generating a handoff:

```
1. /eoa-generate-replacement-handoff --failed-agent X --new-agent Y
   → Creates: handoff document

2. /eoa-reassign-kanban-tasks --from-agent X --to-agent Y --handoff-url URL
   → Updates: GitHub Issues

3. Send AI Maestro message to new agent with handoff using the `agent-messaging` skill
   → New agent begins work
```

## Related Commands

- `/eoa-generate-replacement-handoff` - Generate handoff document
- `/eoa-reassign-module` - Reassign a single module
- `/eoa-check-agents` - Monitor agent status
- `/eoa-orchestrator-status` - View all assignments

## Related Skills

- `eoa-agent-replacement` - Full replacement workflow
- `eoa-module-management` - Module operations
- `eoa-remote-agent-coordinator` - GitHub integration
