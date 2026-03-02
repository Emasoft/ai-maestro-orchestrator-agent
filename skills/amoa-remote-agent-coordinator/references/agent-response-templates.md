# Agent Response Templates


## Contents

- [Table of Contents](#table-of-contents)
- [1.0 Overview](#10-overview)
- [2.0 Available Templates](#20-available-templates)
  - [Template Reference Table](#template-reference-table)
- [3.0 Including Templates in Task Delegations](#30-including-templates-in-task-delegations)
  - [3.1 Template Reference Block Format](#31-template-reference-block-format)
- [Response Templates](#response-templates)
- [4.0 Generating Ad-Hoc Skills for Complex Tasks](#40-generating-ad-hoc-skills-for-complex-tasks)
  - [4.1 When to Generate a Mini-Skill](#41-when-to-generate-a-mini-skill)
  - [4.2 Using generate_agent_skill.py](#42-using-generate_agent_skillpy)
  - [4.3 Agent Installation Instructions](#43-agent-installation-instructions)

---

## Table of Contents

- 1.0 Overview
- 1.1 Why templates are necessary
- 1.2 When to reference templates in task delegations
- 2.0 Available Templates
- 2.1 ACK Response template
- 2.2 Completion Report template
- 2.3 Status Update template
- 2.4 Task Checklist template
- 2.5 GitHub Projects Guide
- 3.0 Including Templates in Task Delegations
- 3.1 Template reference block format
- 3.2 Example template reference section
- 4.0 Generating Ad-Hoc Skills for Complex Tasks
- 4.1 When to generate a mini-skill for agents
- 4.2 Using generate_agent_skill.py
- 4.3 Agent installation instructions

---

## 1.0 Overview

Remote agents need exact formats for responses. Templates ensure consistency across all agent communications.

---

## 2.0 Available Templates

### Template Reference Table

| Template | Path | Purpose |
|----------|------|---------|
| ACK Response | `templates/ack-response.md` | How to acknowledge task receipt |
| Completion Report | `templates/completion-report.md` | How to report task completion |
| Status Update | `templates/status-update.md` | How to send progress updates |
| Task Checklist | `templates/task-checklist.md` | Tracking progress on task items |
| GitHub Projects | `templates/github-projects-guide.md` | Updating issue status on GitHub |

---

## 3.0 Including Templates in Task Delegations

### 3.1 Template Reference Block Format

Include template references in EVERY task delegation:

```markdown
## Response Templates

Download and follow these templates for responding:

- **ACK**: `templates/ack-response.md` - Use IMMEDIATELY after receiving this task
- **Progress**: `templates/status-update.md` - Use at each checkpoint
- **Completion**: `templates/completion-report.md` - Use when task is done
- **GitHub**: `templates/github-projects-guide.md` - Use for issue updates
```

---

## 4.0 Generating Ad-Hoc Skills for Complex Tasks

### 4.1 When to Generate a Mini-Skill

For complex tasks, generate a tailored mini-skill for the agent. This is appropriate when:
- Task requires multiple files or components
- Task has complex acceptance criteria
- Agent needs project-specific context
- Task will take more than a few hours

### 4.2 Using generate_agent_skill.py

```bash
python scripts/generate_agent_skill.py \
  --task-id GH-42 \
  --project "my-project" \
  --lang rust \
  --type feature \
  --templates all \
  --output ./agent-skills/
```

This creates a complete skill directory the agent can install:
- `SKILL.md` - Task-specific instructions
- `templates/` - Response templates
- `README.md` - Installation instructions

### 4.3 Agent Installation Instructions

The agent installs the generated skill with:

```bash
cp -r gh-42-skill ~/.claude/skills/
```

See `scripts/generate_agent_skill.py` for full usage and options.
