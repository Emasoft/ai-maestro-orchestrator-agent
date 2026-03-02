# Toolchain Template System


## Contents

- [Table of Contents](#table-of-contents)
- [1.0 Overview](#10-overview)
  - [1.1 Purpose](#11-purpose)
  - [1.2 Key Benefits](#12-key-benefits)
- [2.0 Template Categories](#20-template-categories)
  - [2.1 Category Reference Table](#21-category-reference-table)
- [3.0 Using Templates](#30-using-templates)
  - [3.1 Template Customization with compile_template.py](#31-template-customization-with-compile_templatepy)
  - [3.2 Including Templates in Task Delegations](#32-including-templates-in-task-delegations)
- [Setup Instructions](#setup-instructions)
  - [3.3 Referencing Templates in Reports](#33-referencing-templates-in-reports)
- [Completion Report](#completion-report)
- [4.0 Template Index](#40-template-index)
  - [4.1 Where to Find All Templates](#41-where-to-find-all-templates)
  - [4.2 Placeholder Reference Guide](#42-placeholder-reference-guide)

---

## Table of Contents

- 1.0 Overview
- 1.1 Purpose of the template system
- 1.2 Key benefits
- 2.0 Template Categories
- 2.1 Category reference table
- 2.2 When to use each category
- 3.0 Using Templates
- 3.1 Template customization with compile_template.py
- 3.2 Including templates in task delegations
- 3.3 Referencing templates in reports
- 4.0 Template Index
- 4.1 Where to find all templates
- 4.2 Placeholder reference guide

---

## 1.0 Overview

### 1.1 Purpose

The Toolchain Template System provides pre-configured, customizable templates for rapid project setup, agent coordination, and consistent reporting across the EOA ecosystem. Instead of writing configurations from scratch, orchestrators use templates to generate task instructions, development environments, and integration points.

### 1.2 Key Benefits

- Reduces setup time from hours to minutes
- Ensures consistency across agents and projects
- Embeds project methodology requirements automatically
- Provides validated configurations for common scenarios

---

## 2.0 Template Categories

### 2.1 Category Reference Table

| Category | Purpose | Examples |
|----------|---------|----------|
| **Toolchain Templates** | Language-specific development configurations | Python, TypeScript, Rust toolchains with linting, testing, formatting |
| **Platform Module Templates** | Cross-platform development setups | macOS, Linux, Windows specific build configurations |
| **Monorepo Templates** | Workspace composition and multi-package projects | Cargo workspaces, npm workspaces, Python monorepos |
| **Claude Code Configuration** | Skills and plugins setup for agents | Custom skill installation, LSP configurations, hook setups |
| **Handoff Templates** | Task delegation formats | Task instruction templates, onboarding workflows, checkpoint reports |
| **Report Templates** | Status reporting formats | Completion reports, error reports, escalation messages |
| **GitHub Integration** | Kanban synchronization and project tracking | Issue templates, PR descriptions, project board automation |

---

## 3.0 Using Templates

### 3.1 Template Customization with compile_template.py

Use `compile_template.py` to generate customized configurations:

```bash
# Generate Python toolchain config for new agent
python scripts/compile_template.py \
  --template toolchain/python-advanced \
  --project my-project \
  --output design/agents/dev-agent-1/

# Generate handoff template for specific task
python scripts/compile_template.py \
  --template handoff/feature-implementation \
  --task-id GH-42 \
  --output tasks/gh-42/
```

The script replaces placeholders (e.g., `{{project_name}}`, `{{task_id}}`) with actual values and generates ready-to-use configuration files.

### 3.2 Including Templates in Task Delegations

Reference templates in task delegation messages to ensure agents have all necessary context:

```markdown
## Setup Instructions

Before starting this task, download and apply the following templates:

1. **Toolchain**: `design/templates/toolchain/typescript-react.json`
2. **Report Format**: `design/templates/reports/completion-report.md`
3. **GitHub Integration**: `design/templates/github/pr-description.md`

Apply with:
\`\`\`bash
python scripts/compile_template.py --template toolchain/typescript-react --output ./
\`\`\`
```

### 3.3 Referencing Templates in Reports

Agents use report templates to maintain consistency:

```markdown
## Completion Report

**Template**: `templates/reports/completion-report.md`
**Task**: GH-42
**Status**: SUCCESS

[Report follows template structure...]
```

---

## 4.0 Template Index

### 4.1 Where to Find All Templates

For the complete template catalog with descriptions, use cases, and customization options, see:

**[../templates/TEMPLATE_INDEX.md](../templates/TEMPLATE_INDEX.md)**

The index includes:
- Full list of all available templates
- Placeholder reference guide
- Customization examples
- Integration patterns
- Troubleshooting common issues

### 4.2 Placeholder Reference Guide

Common placeholders used in templates:

| Placeholder | Description | Example Value |
|-------------|-------------|---------------|
| `{{project_name}}` | Project identifier | `my-app` |
| `{{task_id}}` | GitHub issue number | `GH-42` |
| `{{agent_name}}` | Agent session name | `helper-agent-1` |
| `{{branch_name}}` | Git branch | `feature/auth` |
| `{{timestamp}}` | ISO 8601 timestamp | `2025-01-08T10:30:00Z` |
