#!/usr/bin/env python3
"""Generate Ad-Hoc Skills for Remote Agents.

PURPOSE: Creates tailored, project-specific mini-skills for remote agents
to install locally when working on complex tasks.

USAGE:
  python generate_agent_skill.py --task-id GH-42 --project "xls-cross-platform" \
    --lang rust --type feature --output ./agent-skills/

  python generate_agent_skill.py --task-id GH-15 --project "my-app" \
    --lang python --type bugfix --templates ack,completion,checklist

OUTPUTS:
  Creates a directory with:
  - SKILL.md (main skill file for the agent)
  - templates/ (relevant templates for the task)
  - scripts/ (any helper scripts needed)

This allows orchestrators to generate lean, task-specific skills rather than
giving agents the full emasoft-orchestrator-agent skill.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# ==============================================================================
# TEMPLATES
# ==============================================================================

SKILL_MD_TEMPLATE = '''# {project_name} - {task_id} Agent Skill

## Purpose

This skill provides instructions for completing task **{task_id}** on the **{project_name}** project.

---

## Task Overview

| Field | Value |
|-------|-------|
| Task ID | `{task_id}` |
| Project | {project_name} |
| Language | {language} |
| Type | {task_type} |
| Generated | {timestamp} |

---

## Acknowledgment Protocol

**MANDATORY**: Before starting work, send an acknowledgment in this exact format:

```
[ACK] {task_id} - {{status}}
Understanding: {{1-line summary of what you will do}}
```

**Status options:**
- `RECEIVED` - Task received, will begin work immediately
- `CLARIFICATION_NEEDED` - Need more info (list your questions)
- `REJECTED` - Cannot accept task (explain why)
- `QUEUED` - Have prior tasks, will start after them

---

## Progress Updates

Send progress updates at each checkpoint:

```
[PROGRESS] {task_id} - Checkpoint {{N}}: {{checkpoint_name}}

Status: {{ACTIVE | BLOCKED | PAUSED}}
Progress: {{percentage}}% complete
Current: {{what you just finished}}
Next: {{what you will do next}}
```

---

## Completion Report

When done, send completion report:

```
[DONE] {task_id} - {{brief_result}}

## Summary
- {{what was accomplished}}

## Verification
{{command}} -> {{output}}

## Artifacts
- PR: {{url}}
- Branch: {{branch_name}}
```

---

## Git Workflow

### Branch Naming
```bash
git checkout -b feature/{task_id_lower}-{{description}}
```

### Commit Convention
```
feat({task_id}): {{description}}
fix({task_id}): {{description}}
test({task_id}): {{description}}
```

### PR Creation
```bash
gh pr create --title "feat({task_id}): {{description}}" \\
  --body "Closes #{issue_num}

## Summary
{{changes}}

## Verification
{{test output}}
"
```

---

## GitHub Issue Updates

```bash
# After ACK - move to In Progress
gh issue edit {issue_num} --add-label "status:in-progress"
gh issue comment {issue_num} --body "[ACK] Starting work."

# Progress update
gh issue comment {issue_num} --body "[PROGRESS] Checkpoint {{N}}: {{status}}"

# After PR created
gh issue edit {issue_num} --add-label "status:ai-review"
```

---

## Templates Included

{templates_list}

---

## Language-Specific Commands

{language_commands}

---

## Checklist

{checklist}

---

## Contact

Report issues or blockers to: `orchestrator-master`

Message format:
```
[BLOCKED] {task_id} - {{blocker description}}
Need: {{what you need to proceed}}
```
'''

LANGUAGE_COMMANDS = {
    "rust": """### Rust Commands

```bash
# Build
cargo build

# Test
cargo test

# Lint
cargo clippy -- -D warnings

# Format
cargo fmt

# Run
cargo run -- [args]

# Check (no build)
cargo check
```

### Verification Command
```bash
cargo test && cargo clippy -- -D warnings
```
""",
    "python": """### Python Commands

```bash
# Create virtual environment
uv venv --python 3.12
source .venv/bin/activate

# Install dependencies
uv pip install -e ".[dev]"

# Test
pytest tests/ -v

# Lint
ruff check src/ tests/

# Format
ruff format src/ tests/

# Type check
mypy src/
```

### Verification Command
```bash
pytest tests/ && ruff check src/ && mypy src/
```
""",
    "javascript": """### JavaScript/TypeScript Commands

```bash
# Install dependencies
pnpm install

# Test
pnpm test

# Lint
pnpm lint

# Format
pnpm format

# Build
pnpm build

# Type check (TypeScript)
pnpm typecheck
```

### Verification Command
```bash
pnpm test && pnpm lint && pnpm typecheck
```
""",
    "go": """### Go Commands

```bash
# Build
go build ./...

# Test
go test ./...

# Lint
golangci-lint run

# Format
go fmt ./...

# Vet
go vet ./...
```

### Verification Command
```bash
go test ./... && go vet ./... && golangci-lint run
```
""",
}

TASK_TYPE_CHECKLISTS = {
    "feature": """### Feature Implementation Checklist

- [ ] ACK sent with task ID
- [ ] Feature branch created: `feature/{task_id_lower}-description`
- [ ] Requirements understood from issue
- [ ] Core functionality implemented
- [ ] Tests written (unit + integration)
- [ ] All tests pass locally
- [ ] Linter passes
- [ ] Documentation updated
- [ ] PR created with "Closes #issue"
- [ ] Completion report sent
""",
    "bugfix": """### Bug Fix Checklist

- [ ] ACK sent with task ID
- [ ] Bug reproduced locally
- [ ] Root cause identified
- [ ] Fix branch created: `fix/{task_id_lower}-description`
- [ ] Fix implemented
- [ ] Regression test added
- [ ] All tests pass locally
- [ ] Linter passes
- [ ] PR created with "Fixes #issue"
- [ ] Completion report sent
""",
    "refactor": """### Refactoring Checklist

- [ ] ACK sent with task ID
- [ ] Refactor branch created: `refactor/{task_id_lower}-description`
- [ ] Scope defined - only touch what's needed
- [ ] Code restructured
- [ ] No functionality changed
- [ ] All existing tests pass
- [ ] Linter passes
- [ ] PR created with "Refactor: description"
- [ ] Completion report sent
""",
    "test": """### Test Writing Checklist

- [ ] ACK sent with task ID
- [ ] Test branch created: `test/{task_id_lower}-description`
- [ ] Code to test identified
- [ ] Unit tests written
- [ ] Edge cases covered
- [ ] Integration tests written (if applicable)
- [ ] All tests pass locally
- [ ] Coverage improved
- [ ] PR created with "test: add tests for X"
- [ ] Completion report sent
""",
    "docs": """### Documentation Checklist

- [ ] ACK sent with task ID
- [ ] Docs branch created: `docs/{task_id_lower}-description`
- [ ] Documentation scope identified
- [ ] Content written/updated
- [ ] Examples added
- [ ] Links verified
- [ ] Spelling/grammar checked
- [ ] PR created with "docs: update X"
- [ ] Completion report sent
""",
}


# ==============================================================================
# TEMPLATE FILES
# ==============================================================================

ACK_TEMPLATE = """# ACK Response Template

## Format

```
[ACK] {task_id} - {{status}}
Understanding: {{1-line summary}}
```

## Status Values

| Status | When to Use |
|--------|-------------|
| `RECEIVED` | Ready to start immediately |
| `CLARIFICATION_NEEDED` | Have questions |
| `REJECTED` | Cannot accept |
| `QUEUED` | Busy, will start later |

## Example

```
[ACK] {task_id} - RECEIVED
Understanding: Will implement the feature as specified in the issue
```
"""

COMPLETION_TEMPLATE = """# Completion Report Template

## Format

```
[DONE] {task_id} - {{brief_result}}

## Summary
- {{bullet points of work done}}

## Verification
{{command}} -> {{output}}

## Artifacts
- PR: {{url}}
- Branch: {{branch_name}}
- Files Changed: {{count}}
```

## Example

```
[DONE] {task_id} - Feature implemented with tests

## Summary
- Implemented core functionality
- Added 5 unit tests
- Updated documentation

## Verification
cargo test -> 15 passed, 0 failed

## Artifacts
- PR: https://github.com/org/repo/pull/42
- Branch: feature/{task_id_lower}-impl
- Files Changed: 4
```
"""

STATUS_TEMPLATE = """# Status Update Template

## Format

```
[PROGRESS] {task_id} - Checkpoint {{N}}: {{name}}

Status: {{ACTIVE | BLOCKED | PAUSED}}
Progress: {{percentage}}% complete
Current: {{what you finished}}
Next: {{what you will do}}
```

## Example

```
[PROGRESS] {task_id} - Checkpoint 2: Implementation

Status: ACTIVE
Progress: 60% complete
Current: Core logic implemented
Next: Writing tests
```

## Blocked Format

```
[PROGRESS] {task_id} - BLOCKED

Status: BLOCKED
Progress: 40% complete
Blocker: {{description}}
Need: {{what you need to proceed}}
```
"""

CHECKLIST_TEMPLATE = """# Task Checklist

## Pre-Work
- [ ] ACK sent with task ID
- [ ] Requirements understood
- [ ] Branch created

## Implementation
- [ ] Core functionality complete
- [ ] Code follows project style
- [ ] No TODO/FIXME markers

## Quality
- [ ] Linter passes
- [ ] Type checker passes
- [ ] No warnings

## Testing
- [ ] Tests written
- [ ] All tests pass
- [ ] Edge cases covered

## Completion
- [ ] PR created
- [ ] PR linked to issue
- [ ] Completion report sent
"""


# ==============================================================================
# GENERATOR
# ==============================================================================


def generate_skill(
    task_id: str,
    project: str,
    language: str,
    task_type: str,
    output_dir: Path,
    templates: list[str],
) -> dict[str, Any]:
    """Generate a complete ad-hoc skill for a remote agent."""

    # Create output directory
    skill_dir = output_dir / f"{task_id.lower()}-skill"
    templates_dir = skill_dir / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)

    # Extract issue number from task ID
    issue_num = "".join(c for c in task_id if c.isdigit()) or "0"

    # Prepare template variables
    vars_dict = {
        "task_id": task_id,
        "task_id_lower": task_id.lower().replace("-", "_"),
        "project_name": project,
        "language": language,
        "task_type": task_type,
        "timestamp": datetime.now().isoformat(),
        "issue_num": issue_num,
    }

    # Get language-specific commands
    lang_key = language.lower()
    if lang_key in ("typescript", "ts", "js"):
        lang_key = "javascript"
    language_commands = LANGUAGE_COMMANDS.get(lang_key, LANGUAGE_COMMANDS["python"])
    vars_dict["language_commands"] = language_commands

    # Get task type checklist
    checklist = TASK_TYPE_CHECKLISTS.get(task_type, TASK_TYPE_CHECKLISTS["feature"])
    checklist = checklist.format(**vars_dict)
    vars_dict["checklist"] = checklist

    # Generate templates list
    template_files = []
    if "ack" in templates or "all" in templates:
        template_files.append("- `templates/ack-response.md` - How to acknowledge task")
        (templates_dir / "ack-response.md").write_text(
            ACK_TEMPLATE.format(**vars_dict)
        )
    if "completion" in templates or "all" in templates:
        template_files.append("- `templates/completion-report.md` - How to report completion")
        (templates_dir / "completion-report.md").write_text(
            COMPLETION_TEMPLATE.format(**vars_dict)
        )
    if "status" in templates or "all" in templates:
        template_files.append("- `templates/status-update.md` - How to send progress updates")
        (templates_dir / "status-update.md").write_text(
            STATUS_TEMPLATE.format(**vars_dict)
        )
    if "checklist" in templates or "all" in templates:
        template_files.append("- `templates/task-checklist.md` - Checklist to track progress")
        (templates_dir / "task-checklist.md").write_text(CHECKLIST_TEMPLATE)

    vars_dict["templates_list"] = "\n".join(template_files) if template_files else "No templates included."

    # Generate main SKILL.md
    skill_content = SKILL_MD_TEMPLATE.format(**vars_dict)
    (skill_dir / "SKILL.md").write_text(skill_content)

    # Create README
    readme_content = f"""# {task_id} Agent Skill

This skill was auto-generated for task **{task_id}** on project **{project}**.

## Installation

Copy this directory to your local skills folder:

```bash
cp -r {skill_dir.name} ~/.claude/skills/
```

## Contents

- `SKILL.md` - Main skill file with all instructions
- `templates/` - Response templates for ACK, completion, status updates

## Usage

Read `SKILL.md` before starting work on the task.

Generated: {datetime.now().isoformat()}
"""
    (skill_dir / "README.md").write_text(readme_content)

    return {
        "skill_dir": str(skill_dir),
        "files_created": [
            str(skill_dir / "SKILL.md"),
            str(skill_dir / "README.md"),
        ] + [str(f) for f in templates_dir.glob("*.md")],
        "task_id": task_id,
        "project": project,
    }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate ad-hoc skills for remote agents"
    )
    parser.add_argument(
        "--task-id",
        required=True,
        help="Task ID (e.g., GH-42, issue-15)",
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Project name",
    )
    parser.add_argument(
        "--lang",
        default="python",
        choices=["python", "rust", "javascript", "typescript", "go"],
        help="Programming language",
    )
    parser.add_argument(
        "--type",
        default="feature",
        choices=["feature", "bugfix", "refactor", "test", "docs"],
        help="Task type",
    )
    parser.add_argument(
        "--templates",
        default="all",
        help="Comma-separated templates to include: ack,completion,status,checklist,all",
    )
    parser.add_argument(
        "--output",
        default="./agent-skills",
        help="Output directory",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )

    args = parser.parse_args()

    output_dir = Path(args.output)
    templates = [t.strip() for t in args.templates.split(",")]

    result = generate_skill(
        task_id=args.task_id,
        project=args.project,
        language=args.lang,
        task_type=args.type,
        output_dir=output_dir,
        templates=templates,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\nGenerated skill at: {result['skill_dir']}")
        print("\nFiles created:")
        for f in result["files_created"]:
            print(f"  - {f}")
        print("\nTo use, have the agent copy to ~/.claude/skills/")

    return 0


if __name__ == "__main__":
    sys.exit(main())
