# Remote Agent Templates

## Purpose

These templates provide **exact formats** for remote agents to use when responding to the orchestrator. Since remote agents do not have access to the orchestrator-agent skill, they must be taught response formats explicitly. These templates solve that problem.

---

## Templates

| Template | File | When Agent Uses It |
|----------|------|-------------------|
| ACK Response | `ack-response.md` | Immediately after receiving a task delegation |
| Completion Report | `completion-report.md` | When task is done (success or failure) |
| Status Update | `status-update.md` | At each checkpoint during work |
| Task Checklist | `task-checklist.md` | Throughout task execution to track progress |
| GitHub Projects | `github-projects-guide.md` | When updating issue status on GitHub |

---

## Usage

### In Task Delegations

Include references to these templates in every task delegation:

```markdown
## Response Templates

Download and follow these templates for responding:

- **ACK**: `templates/ack-response.md` - Use IMMEDIATELY after receiving this task
- **Progress**: `templates/status-update.md` - Use at each checkpoint
- **Completion**: `templates/completion-report.md` - Use when task is done
- **GitHub**: `templates/github-projects-guide.md` - Use for issue updates
```

### Agent Access

Remote agents can access these templates at:
```
skills/remote-agent-coordinator/templates/
```

---

## Quick Reference

### ACK Format
```
[ACK] {task_id} - {status}
Understanding: {1-line summary}
```

### Progress Format
```
[PROGRESS] {task_id} - Checkpoint {N}: {name}
Status: {ACTIVE|BLOCKED|PAUSED}
Progress: {%} complete
```

### Completion Format
```
[DONE] {task_id} - {brief_result}
## Summary
## Verification
## Artifacts
```

---

## Generating Ad-Hoc Skills

For complex tasks, use the generator script to create task-specific mini-skills:

```bash
python scripts/generate_agent_skill.py \
  --task-id GH-42 \
  --project "my-project" \
  --lang rust \
  --type feature \
  --templates all \
  --output ./agent-skills/
```

This creates a complete skill directory with:
- Tailored SKILL.md
- Relevant templates only
- Installation instructions

---

## Maintenance

When updating these templates:
1. Keep formats simple and unambiguous
2. Include examples for every format
3. Update SKILL.md references if paths change
4. Update task-instruction-format.md if templates change
