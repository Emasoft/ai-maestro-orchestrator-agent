# Design Folder Structure - Part 3: Usage Workflow and Git Tracking

Workflow for creating, compiling, and tracking design files.

## Contents

- 4. Usage Workflow
  - 4.1 Creating design files during Plan Phase
  - 4.2 Compiling templates for implementers
  - 4.3 Storing implementer responses
- 5. Git Tracking Rules
  - 5.1 What to track
  - 5.2 What to gitignore

---

## 4. Usage Workflow

### 4.1 Creating design files during Plan Phase

During `/start-planning`:

1. Create `design/` folder structure
2. Create platform-specific subfolders
3. Create templates in `designs/{platform}/templates/`
4. Create shared architecture docs in `designs/shared/`

```bash
# Script creates structure automatically
python3 eoa_start_planning.py <!-- TODO: Script not implemented --> "Build auth system"

# Creates:
# design/requirements/shared/
# design/requirements/web/templates/
# design/requirements/web/specs/
# design/requirements/web/rdd/
# design/config/
# design/handoffs/
```

### 4.2 Compiling templates for implementers

During `/assign-module`:

1. Load template from `designs/{platform}/templates/`
2. Fill all placeholders with module-specific data
3. Save compiled handoff to `handoffs/{agent-id}/`
4. Include handoff path in assignment message

```python
def compile_handoff(module_id, agent_id, platform):
    template_path = f"design/requirements/{platform}/templates/handoff-template.md"
    template = load_template(template_path)

    compiled = template.format(
        MODULE_NAME=module.name,
        REQUIREMENTS_LIST=module.requirements,
        ACCEPTANCE_CRITERIA=module.criteria,
        AGENT_ID=agent_id,
        TASK_UUID=generate_uuid(),
        GITHUB_ISSUE=module.github_issue
    )

    handoff_path = f"design/handoffs/{agent_id}/{module_id}-handoff.md"
    save_file(handoff_path, compiled)
    return handoff_path
```

### 4.3 Storing implementer responses

When implementers provide feedback or request config:

1. Configuration requests stored in `config/{platform}/`
2. Design questions added to spec files as comments
3. Handoff updates trigger re-compilation

---

## 5. Git Tracking Rules

### 5.1 What to track

**ALWAYS track in git**:
- All `design/requirements/` contents
- All `design/config/` contents (except secrets)
- All `design/handoffs/` contents
- All `design/archive/` contents

### 5.2 What to gitignore

**Add to .gitignore**:
```gitignore
# Actual secrets (not .example files)
design/config/**/*.env
!design/config/**/*.env.example

# Temporary compilation files
design/.tmp/

# Local orchestrator state (separate from design docs)
design/state/*.md
```

**IMPORTANT**: Design documents are NOT the same as orchestrator state files.
- Design docs (`design/`) = tracked by git
- State files (`.claude/*.local.md`) = gitignored
