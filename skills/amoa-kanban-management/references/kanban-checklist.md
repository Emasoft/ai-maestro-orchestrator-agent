## Table of Contents
- [Step-by-Step Instructions](#step-by-step-instructions)
- [Pre-Flight Checklist](#pre-flight-checklist)
- [Board Setup Checklist](#board-setup-checklist)
- [Task Management Checklist](#task-management-checklist)

---

## Step-by-Step Instructions

Follow these steps to manage the kanban board:

1. **Before first use**: Verify OAuth scopes (see SKILL.md "Critical Pre-Flight Check")
2. **Creating a board**: Follow PROCEDURE 1 in [kanban-procedures.md](kanban-procedures.md)
3. **Adding columns**: ALWAYS use `gh-project-add-columns.py` (PROCEDURE 2)
4. **Moving items**: Follow PROCEDURE 3
5. **Syncing status**: Follow PROCEDURE 4

---

## Pre-Flight Checklist

- [ ] Verify gh CLI is installed (`which gh`)
- [ ] Verify gh is authenticated (`gh auth status`)
- [ ] Verify project scopes are present (`gh auth status 2>&1 | grep project`)
- [ ] If scopes missing, request human to run `gh auth refresh -h github.com -s project,read:project`

## Board Setup Checklist

- [ ] Create GitHub Project: `gh project create --owner Emasoft --title "<project>"`
- [ ] Add standard 8 columns using `gh-project-add-columns.py`
- [ ] Save project number to `.github/project.json`

## Task Management Checklist

- [ ] Create task issues with proper labels (`assign:*`, `priority:*`, `status:*`)
- [ ] Add issues to project board
- [ ] Move items between columns as status changes
- [ ] When moving to Done: check if issue was auto-closed before attempting `gh issue close`
