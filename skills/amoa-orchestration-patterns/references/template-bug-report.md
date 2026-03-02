---
name: template-bug-report
description: "Universal bug report YAML form for GitHub Issues, used by the orchestrator when filing bugs discovered during task execution."
---

# Universal Bug Report Issue Template (Orchestrator Perspective)

## Table of Contents

- 1. When the Orchestrator Files Bug Reports
  - 1.1 When to file a bug report directly versus delegating
  - 1.2 Installing the bug report form in a repository
  - 1.3 How GitHub Issue YAML forms work
- 2. YAML Form Syntax Overview
  - 2.1 Top-level fields (name, description, labels, assignees)
  - 2.2 Body field types (input, textarea, dropdown, checkboxes, markdown)
  - 2.3 Validation attributes (required, placeholder, render)
- 3. Template Fields Explained
  - 3.1 Duplicate check checkbox
  - 3.2 Area dropdown for module classification
  - 3.3 Operating system dropdown
  - 3.4 Version input field
  - 3.5 "What happened?" description textarea
  - 3.6 Steps to reproduce textarea
  - 3.7 Expected behavior textarea
  - 3.8 Logs and screenshots textarea with code rendering
- 4. Auto-Labeling Strategy
  - 4.1 Default labels for bug reports
  - 4.2 How labels integrate with triage workflows
- 5. Orchestrator Bug Reporting Guidelines
  - 5.1 When the orchestrator files bug reports itself
  - 5.2 When the orchestrator delegates bug reporting
  - 5.3 How to write high-quality bug reports from agent observations
  - 5.4 Adding task context to bug reports
- 6. Complete YAML Template (Ready to Copy)
- 7. Customization Notes
  - 7.1 Adding project-specific fields
  - 7.2 Modifying the area dropdown for your project

---

## 1. When the Orchestrator Files Bug Reports

### 1.1 When to file a bug report directly versus delegating

The orchestrator agent (EOA) encounters bugs in two ways:

**Scenario A: Orchestrator discovers the bug during task coordination.** This happens when:
- An implementer agent reports a blocker caused by existing code
- Test results reveal a failure in code that was not modified by the current task
- Integration testing between modules reveals a pre-existing defect

In this scenario, the orchestrator files the bug report directly because it has the context of how the bug was discovered and its impact on the current work.

**Scenario B: An implementer discovers the bug during implementation.** This happens when:
- The programmer agent encounters unexpected behavior in a dependency or adjacent module
- A code review by the integrator agent reveals a bug in existing code (not introduced by the PR)

In this scenario, the orchestrator can delegate the bug filing to the agent that discovered it, because that agent has the most detailed context about the reproduction steps and technical details.

### 1.2 Installing the bug report form in a repository

Place the YAML file at `.github/ISSUE_TEMPLATE/bug_report.yml` in your repository:

```
your-repo/
  .github/
    ISSUE_TEMPLATE/
      bug_report.yml   <-- place the template here
```

### 1.3 How GitHub Issue YAML forms work

GitHub Issue forms use YAML to define structured fields. Each field in the YAML `body` array becomes an input element in the browser form. When submitted, GitHub renders the responses as formatted markdown in the issue body.

Key field types:
- `type: input` -- single-line text field
- `type: textarea` -- multi-line text area
- `type: dropdown` -- selection menu
- `type: checkboxes` -- list of checkboxes
- `type: markdown` -- static instructional text (not user input)

---

## 2. YAML Form Syntax Overview

### 2.1 Top-level fields

```yaml
name: Bug Report
description: Report a bug or unexpected behavior
labels: ["bug", "backlog"]
assignees: []
```

- `name` -- displayed in the template chooser
- `description` -- shown below the name in the chooser
- `labels` -- automatically applied to every issue created with this template
- `assignees` -- GitHub usernames to auto-assign (usually left empty)

### 2.2 Body field types

Each entry in the `body` array has a `type` and `attributes` object:

```yaml
# Single-line text
- type: input
  id: version
  attributes:
    label: "Version"
    placeholder: "e.g., 2.1.0"
  validations:
    required: true

# Multi-line text
- type: textarea
  id: description
  attributes:
    label: "What happened?"
  validations:
    required: true

# Dropdown
- type: dropdown
  id: os
  attributes:
    label: "Operating System"
    options:
      - macOS
      - Windows
      - Linux
  validations:
    required: true

# Checkboxes
- type: checkboxes
  id: checks
  attributes:
    label: "Pre-submission"
    options:
      - label: "I searched existing issues"
        required: true
```

### 2.3 Validation attributes

The `render` attribute on textarea fields tells GitHub to format the content as a specific language:

```yaml
- type: textarea
  id: logs
  attributes:
    label: "Logs"
    render: shell
```

This wraps pasted text in a code block with shell syntax highlighting automatically.

---

## 3. Template Fields Explained

### 3.1 Duplicate check checkbox

```yaml
- type: checkboxes
  id: duplicate-check
  attributes:
    label: "Pre-submission checklist"
    options:
      - label: "I have searched existing issues and confirmed this is not a duplicate"
        required: true
```

For orchestrator-filed bugs, this checkbox reminds the orchestrator to search existing issues before creating a new one. Duplicate bug reports waste triage time.

### 3.2 Area dropdown for module classification

```yaml
- type: dropdown
  id: area
  attributes:
    label: "Area"
    description: "Which part of the project is affected?"
    options:
      - Core library
      - CLI interface
      - API server
      - Documentation
      - Build system
      - Tests
      - Other
  validations:
    required: true
```

### 3.3 Operating system dropdown

```yaml
- type: dropdown
  id: operating-system
  attributes:
    label: "Operating System"
    options:
      - macOS
      - Windows 10
      - Windows 11
      - Ubuntu / Debian
      - Fedora / RHEL
      - Arch Linux
      - Other Linux
      - Not applicable
  validations:
    required: true
```

### 3.4 Version input field

```yaml
- type: input
  id: version
  attributes:
    label: "Version"
    description: "Run your-tool --version or check package.json / pyproject.toml"
    placeholder: "e.g., 3.2.1"
  validations:
    required: true
```

### 3.5 "What happened?" description textarea

```yaml
- type: textarea
  id: what-happened
  attributes:
    label: "What happened?"
    description: "Describe the bug clearly."
    placeholder: "When I run X, Y happens instead of Z..."
  validations:
    required: true
```

### 3.6 Steps to reproduce textarea

```yaml
- type: textarea
  id: steps-to-reproduce
  attributes:
    label: "Steps to reproduce"
    description: "Provide exact steps so a maintainer can reproduce the issue."
    placeholder: |
      1. Install version X
      2. Run command Y with arguments Z
      3. Observe error message in terminal
  validations:
    required: true
```

### 3.7 Expected behavior textarea

```yaml
- type: textarea
  id: expected-behavior
  attributes:
    label: "Expected behavior"
    description: "What did you expect to happen instead?"
  validations:
    required: true
```

### 3.8 Logs and screenshots textarea with code rendering

```yaml
- type: textarea
  id: logs
  attributes:
    label: "Relevant log output or screenshots"
    render: shell
  validations:
    required: false
```

---

## 4. Auto-Labeling Strategy

### 4.1 Default labels for bug reports

```yaml
labels: ["bug", "backlog"]
```

### 4.2 How labels integrate with triage workflows

After filing, the orchestrator or a maintainer should:
1. Remove `backlog` after review
2. Add priority label (e.g., `priority-high`, `priority-low`)
3. Add area label if different from the dropdown selection
4. Assign to a milestone if applicable

---

## 5. Orchestrator Bug Reporting Guidelines

### 5.1 When the orchestrator files bug reports itself

The orchestrator files bugs directly when:
- The bug was discovered during task coordination (not during implementation)
- The bug blocks multiple implementers or multiple tasks
- The bug is in infrastructure (CI, build system, deployment) rather than application code
- The orchestrator has clearer context about the bug's impact on the project schedule

### 5.2 When the orchestrator delegates bug reporting

The orchestrator delegates bug filing when:
- An implementer discovered the bug and has detailed reproduction steps
- The bug requires deep technical knowledge to describe accurately
- The implementer already has the error logs and can paste them directly

When delegating, the orchestrator provides:
1. The repository where the issue should be filed
2. The labels to apply (in addition to auto-labels)
3. The milestone to assign (if applicable)
4. Any related issue numbers to cross-reference

### 5.3 How to write high-quality bug reports from agent observations

When an implementer agent reports a blocker, the orchestrator translates the agent's technical observation into a structured bug report:

Example of an agent observation:
```
BLOCKED: Function parse_config() in src/config.py raises UnicodeDecodeError
when the config file contains non-ASCII characters on Windows. The function
uses open() without encoding parameter.
```

Translated into the bug report format:
```
What happened: parse_config() raises UnicodeDecodeError when reading configuration
files that contain non-ASCII characters (e.g., accented names, CJK characters)
on Windows systems.

Steps to reproduce:
1. Create a config.yml file containing non-ASCII characters (e.g., "name: Rene")
2. Run the application on Windows
3. The application crashes with UnicodeDecodeError at src/config.py line 42

Expected behavior: The application should read the config file correctly regardless
of the characters it contains.

Root cause (if known): open() in parse_config() does not specify encoding="utf-8",
so Python uses the Windows system encoding (cp1252) which cannot decode UTF-8 bytes.
```

### 5.4 Adding task context to bug reports

When the orchestrator files a bug discovered during task execution, it should add context about the task:

```markdown
**Discovery context**: This bug was found during task EPA-042 (implement user
profile export). The programmer agent was blocked because the export function
calls parse_config() which fails on Windows test runners.

**Impact**: Blocks task EPA-042 and potentially any other task that reads
configuration files on Windows.
```

This context helps maintainers prioritize the bug relative to ongoing work.

---

## 6. Complete YAML Template (Ready to Copy)

Copy the following into `.github/ISSUE_TEMPLATE/bug_report.yml`:

```yaml
name: Bug Report
description: Report a bug or unexpected behavior
labels: ["bug", "backlog"]
assignees: []
body:
  - type: checkboxes
    id: duplicate-check
    attributes:
      label: "Pre-submission checklist"
      options:
        - label: "I have searched existing issues and confirmed this is not a duplicate"
          required: true

  - type: dropdown
    id: area
    attributes:
      label: "Area"
      description: "Which part of the project is affected?"
      options:
        - Core library
        - CLI interface
        - API server
        - Documentation
        - Build system
        - Tests
        - Other
    validations:
      required: true

  - type: dropdown
    id: operating-system
    attributes:
      label: "Operating System"
      options:
        - macOS
        - Windows 10
        - Windows 11
        - Ubuntu / Debian
        - Fedora / RHEL
        - Arch Linux
        - Other Linux
        - Not applicable
    validations:
      required: true

  - type: input
    id: version
    attributes:
      label: "Version"
      description: "Run your-tool --version or check package.json / pyproject.toml"
      placeholder: "e.g., 3.2.1"
    validations:
      required: true

  - type: textarea
    id: what-happened
    attributes:
      label: "What happened?"
      description: "Describe the bug clearly. What did you observe?"
      placeholder: "When I run X, Y happens instead of Z..."
    validations:
      required: true

  - type: textarea
    id: steps-to-reproduce
    attributes:
      label: "Steps to reproduce"
      description: "Provide exact steps so a maintainer can reproduce the issue."
      placeholder: |
        1. Install version X
        2. Run command Y with arguments Z
        3. Observe error message in terminal
    validations:
      required: true

  - type: textarea
    id: expected-behavior
    attributes:
      label: "Expected behavior"
      description: "What did you expect to happen instead?"
      placeholder: "I expected the command to complete successfully and output..."
    validations:
      required: true

  - type: textarea
    id: logs
    attributes:
      label: "Relevant log output or screenshots"
      description: "Paste terminal output, error messages, or attach screenshots."
      render: shell
    validations:
      required: false
```

---

## 7. Customization Notes

### 7.1 Adding project-specific fields

Insert additional fields in the `body` array. For example, add a "Browser" dropdown for web projects or a "Device" input for mobile projects.

### 7.2 Modifying the area dropdown for your project

Replace the generic area options with your project's actual module names:

```yaml
options:
  - Authentication
  - Payment processing
  - Email notifications
  - Admin dashboard
  - REST API
  - GraphQL API
```
