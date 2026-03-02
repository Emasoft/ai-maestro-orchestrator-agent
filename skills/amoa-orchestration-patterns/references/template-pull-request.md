---
name: template-pull-request
description: "Universal pull request template for orchestrator-created PRs, used when filing PRs via implementer agents."
---

# Universal Pull Request Template (Orchestrator Perspective)

## Table of Contents

- 1. When the Orchestrator Creates Pull Requests
  - 1.1 When to create a pull request directly versus delegating to an implementer
  - 1.2 Installing the template in a repository
  - 1.3 Choosing the correct base branch
- 2. Template Structure Overview
  - 2.1 Required sections every pull request must have
  - 2.2 Optional sections for specific change types
- 3. Description and Issue Linking
  - 3.1 Writing a clear pull request description
  - 3.2 Linking related issues with closing keywords
- 4. Type of Change Classification
  - 4.1 Standard change type checkboxes
  - 4.2 Area designation for large projects
- 5. Commit Message Format
  - 5.1 Conventional commits reminder
  - 5.2 Examples of well-formed commit messages
- 6. AI Disclosure Section
  - 6.1 Why AI disclosure matters for orchestrator-created PRs
  - 6.2 Testing level classification for AI-generated code
  - 6.3 Understanding attestation checkbox
- 7. General Review Checklist
  - 7.1 Sync and branch hygiene checks
  - 7.2 Code quality and focus checks
- 8. Platform Testing Checklist
  - 8.1 Windows, macOS, and Linux verification
  - 8.2 When platform testing is required versus optional
- 9. CI and Testing Requirements
  - 9.1 Mandatory CI gates
  - 9.2 Test coverage expectations for new code and bug fixes
- 10. Screenshots and Visual Changes
  - 10.1 Before and after comparison table
- 11. Feature Toggle Section
  - 11.1 How incomplete features are hidden behind toggles
  - 11.2 Toggle mechanism options
- 12. Breaking Changes Section
  - 12.1 Identifying breaking changes
  - 12.2 Migration instructions format
- 13. Complete Template (Ready to Copy)
- 14. Orchestrator Delegation Guidelines
  - 14.1 When the orchestrator should create the PR itself
  - 14.2 When the orchestrator should delegate PR creation to an implementer
  - 14.3 What the orchestrator must verify before merging a delegated PR

---

## 1. When the Orchestrator Creates Pull Requests

### 1.1 When to create a pull request directly versus delegating to an implementer

The orchestrator agent (EOA) uses this template in two scenarios:

**Scenario A: Orchestrator creates the PR directly.** This happens when:
- The change is a configuration-only update (CI files, project settings, dependency versions)
- The change is a template or documentation update that does not involve code logic
- The change was produced by a single implementer and needs no additional coordination

**Scenario B: Orchestrator delegates PR creation to an implementer.** This happens when:
- The change involves code implementation (the programmer agent should create the PR)
- Multiple implementers contributed to the change (one designated implementer creates the PR)
- The PR requires detailed technical description that the implementer knows best

In scenario B, the orchestrator provides the implementer with: the template, the target base branch, the related issue numbers, and any required reviewers. The implementer fills in the technical details.

### 1.2 Installing the template in a repository

Place the template file at `.github/PULL_REQUEST_TEMPLATE.md` in your repository root. GitHub automatically populates every new pull request with this template.

```
your-repo/
  .github/
    PULL_REQUEST_TEMPLATE.md   <-- place the template here
```

### 1.3 Choosing the correct base branch

| Situation | Base Branch | Example |
|-----------|-------------|---------|
| Normal feature or fix | `develop` (or your default integration branch) | Adding a new CLI command |
| Hotfix for production | `main` (or your production branch) | Critical security patch |
| Release preparation | `main` from a release branch | Merging `release/2.1.0` into `main` |

The orchestrator decides the base branch based on the task priority and release schedule.

---

## 2. Template Structure Overview

### 2.1 Required sections every pull request must have

Every pull request must include: Description, Type of Change, General Checklist, and CI/Testing Requirements. These are non-negotiable because they provide the minimum information a reviewer needs.

### 2.2 Optional sections for specific change types

The following sections are included in the template but may be marked "N/A" when not applicable: Screenshots (only for UI changes), Feature Toggle (only for incomplete features), Breaking Changes (only when public API or behavior changes), Platform Testing (only for code that touches OS-level functionality).

---

## 3. Description and Issue Linking

### 3.1 Writing a clear pull request description

The description must answer three questions:
1. What does this change do?
2. Why is this change needed?
3. How was this change tested?

Example of a good description written by the orchestrator:

```markdown
## Description

Implements retry logic for the HTTP client as specified in issue #42.
The programmer agent added exponential backoff with a maximum of 3 retries
for 5xx status codes. Integration tests confirm recovery after transient
server errors.

Task assignment: EPA-001 (programmer agent session svgbbox-programmer-001)
```

### 3.2 Linking related issues with closing keywords

Use GitHub closing keywords so the issue is automatically closed when the pull request merges:

```markdown
Closes #42
Fixes #108
Resolves #77
```

The orchestrator should always link the task issue that originated the work.

---

## 4. Type of Change Classification

### 4.1 Standard change type checkboxes

```markdown
- [ ] [BUG] Bug fix (non-breaking change that fixes an issue)
- [ ] [FEATURE] New feature (non-breaking change that adds functionality)
- [ ] [DOCS] Documentation only
- [ ] [REFACTOR] Refactoring (no functional changes, no API changes)
- [ ] [TEST] Tests (adding or updating tests only)
- [ ] [BUILD] Build or CI configuration change
- [ ] [PERF] Performance improvement
```

### 4.2 Area designation for large projects

```markdown
**Area**: <!-- e.g., core, cli, api, ui, auth, database -->
```

---

## 5. Commit Message Format

### 5.1 Conventional commits reminder

```
<type>(<scope>): <short summary>
```

### 5.2 Examples of well-formed commit messages

```
fix(http): retry on 5xx status codes with exponential backoff
feat(cli): add --dry-run flag to deploy command
docs(readme): update installation instructions for Windows
refactor(auth): extract token validation into separate module
test(api): add integration tests for user endpoint
```

---

## 6. AI Disclosure Section

### 6.1 Why AI disclosure matters for orchestrator-created PRs

When the orchestrator or any implementer agent produces code, the pull request must disclose AI involvement. This is especially important in the agent ecosystem because:
- All code produced by programmer agents (EPA) is AI-generated
- Reviewers need to know the testing level applied to the generated code
- The human owner must attest they understand the changes before merging

### 6.2 Testing level classification for AI-generated code

```markdown
## AI Disclosure

- [ ] This pull request includes AI-generated or AI-assisted code

If checked:
- **Tool used**: <!-- e.g., Claude Code (EPA agent), GitHub Copilot -->
- **Testing level**:
  - [ ] Untested -- AI output used as-is without manual verification
  - [ ] Lightly tested -- Ran basic scenarios, reviewed output
  - [ ] Fully tested -- Comprehensive testing, full understanding of all changes

- [ ] I understand what every line of this pull request does and how the underlying code works
```

### 6.3 Understanding attestation checkbox

For orchestrator-created PRs, the attestation checkbox means the human project owner (not the orchestrator agent) has reviewed and understood every change. The orchestrator should remind the human reviewer about this requirement.

---

## 7. General Review Checklist

### 7.1 Sync and branch hygiene checks

```markdown
## General Checklist

- [ ] My branch is up to date with the base branch (rebased or merged)
- [ ] I have tested these changes locally
- [ ] My changes follow the project's coding standards and style guide
```

### 7.2 Code quality and focus checks

```markdown
- [ ] This pull request is small and focused on a single concern
- [ ] I have not included unrelated changes or formatting-only diffs
- [ ] I have added or updated comments where the code is not self-explanatory
```

---

## 8. Platform Testing Checklist

### 8.1 Windows, macOS, and Linux verification

```markdown
## Platform Testing

- [ ] Tested on Windows
- [ ] Tested on macOS
- [ ] Tested on Linux
- [ ] N/A -- changes do not involve platform-specific behavior

> Reminder: Use platform abstractions (pathlib, os.path, shutil)
> instead of hardcoded paths or shell commands.
```

### 8.2 When platform testing is required versus optional

Platform testing is required when the change touches: file system operations, subprocess calls, environment variable usage, path construction, encoding-sensitive operations, or native library bindings. Platform testing is optional for: pure logic changes, documentation, test-only changes, or API-only changes that do not interact with the OS.

---

## 9. CI and Testing Requirements

### 9.1 Mandatory CI gates

```markdown
## CI / Testing

- [ ] All CI checks pass
- [ ] All existing tests pass without modification
```

### 9.2 Test coverage expectations for new code and bug fixes

```markdown
- [ ] New features include corresponding tests
- [ ] Bug fixes include a regression test that would have caught the bug
- [ ] No test has been disabled or skipped without explanation
```

---

## 10. Screenshots and Visual Changes

### 10.1 Before and after comparison table

```markdown
## Screenshots (if applicable)

| Before | After |
|--------|-------|
| <!-- paste screenshot --> | <!-- paste screenshot --> |
```

---

## 11. Feature Toggle Section

### 11.1 How incomplete features are hidden behind toggles

When a feature is merged before it is fully complete, it must be hidden behind a toggle so it does not affect users.

### 11.2 Toggle mechanism options

```markdown
## Feature Toggle

- [ ] Environment variable (e.g., `ENABLE_NEW_FEATURE=true`)
- [ ] Configuration file setting
- [ ] Runtime flag (e.g., `--experimental`)
- [ ] N/A -- feature is complete and ready for all users
```

---

## 12. Breaking Changes Section

### 12.1 Identifying breaking changes

A change is breaking if it modifies public API signatures, removes or renames exported functions or classes, changes configuration file format, alters CLI argument syntax, or changes default behavior that users depend on.

### 12.2 Migration instructions format

```markdown
## Breaking Changes

- [ ] Yes -- this pull request includes breaking changes
- [ ] No -- this pull request is backward compatible

If yes, describe the migration path:

**What changed**: <!-- e.g., renamed `get_user()` to `fetch_user()` -->
**Migration steps**:
1. <!-- Step-by-step instructions for consumers -->
2. <!-- Include code examples where helpful -->
```

---

## 13. Complete Template (Ready to Copy)

Copy the following into `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
> [!NOTE]
> Target branch: use `develop` for features and fixes, `main` for hotfixes only.

## Description

<!-- What does this change do? Why is it needed? How was it tested? -->

Closes #<!-- issue number -->

## Type of Change

- [ ] [BUG] Bug fix
- [ ] [FEATURE] New feature
- [ ] [DOCS] Documentation only
- [ ] [REFACTOR] Refactoring
- [ ] [TEST] Tests only
- [ ] [BUILD] Build or CI configuration
- [ ] [PERF] Performance improvement

**Area**: <!-- e.g., core, cli, api, ui -->

## AI Disclosure

- [ ] This pull request includes AI-generated or AI-assisted code

If checked:
- **Tool used**: <!-- e.g., Claude Code, GitHub Copilot -->
- **Testing level**:
  - [ ] Untested
  - [ ] Lightly tested
  - [ ] Fully tested
- [ ] I understand what every line of this PR does

## General Checklist

- [ ] Branch is up to date with base branch
- [ ] Tested locally
- [ ] Follows project coding standards
- [ ] Small and focused on a single concern
- [ ] Comments added where code is not self-explanatory

## Platform Testing

- [ ] Windows
- [ ] macOS
- [ ] Linux
- [ ] N/A

## CI / Testing

- [ ] All CI checks pass
- [ ] Existing tests pass
- [ ] New features include tests
- [ ] Bug fixes include regression tests

## Screenshots

| Before | After |
|--------|-------|
|        |       |

## Feature Toggle

- [ ] Environment variable
- [ ] Configuration setting
- [ ] Runtime flag
- [ ] N/A -- feature is complete

## Breaking Changes

- [ ] Yes (describe migration below)
- [ ] No

**Migration steps** (if breaking):
<!-- Steps here -->
```

---

## 14. Orchestrator Delegation Guidelines

### 14.1 When the orchestrator should create the PR itself

The orchestrator creates the PR directly when:
- The change is configuration-only (CI pipelines, linter settings, project metadata)
- The change is a documentation-only update
- The change was produced by a single task and needs no further technical elaboration
- The orchestrator has full context of the change and can describe it accurately

### 14.2 When the orchestrator should delegate PR creation to an implementer

The orchestrator delegates PR creation when:
- The change involves code that the implementer understands better
- Multiple files were changed and the implementer can describe the technical approach
- The PR description requires implementation-specific details (algorithm choices, performance considerations, trade-offs made)

When delegating, the orchestrator provides:
1. The base branch name
2. The issue numbers to link
3. The PR title (orchestrator decides the title)
4. Any required reviewers
5. A reference to this template

The implementer fills in the description, checks the appropriate boxes, and creates the PR.

### 14.3 What the orchestrator must verify before merging a delegated PR

Before approving a merge, the orchestrator verifies:
1. All CI checks pass (automated)
2. The integrator agent (EIA) has reviewed the code (if available)
3. The AI Disclosure section is filled out honestly
4. The human project owner has been notified for final approval
5. Breaking changes are documented with migration steps if applicable
