# Templates for Human Communication

This document provides templates for all human-facing documentation. Each section is detailed in its own part file.

---

## Contents

- 6.1 Pull Request description template
  - 6.1.1 Summary section
  - 6.1.2 Changes section with bullets
  - 6.1.3 Testing section
  - 6.1.4 Screenshots for UI changes
- 6.2 Commit message guidelines
  - 6.2.1 Conventional commits format
  - 6.2.2 Subject line rules
  - 6.2.3 Body content guidelines
- 6.3 Release notes format
  - 6.3.1 User-facing language
  - 6.3.2 Grouping by type
  - 6.3.3 Linking to issues and PRs
- 6.4 Breaking change communication
  - 6.4.1 Warning users in advance
  - 6.4.2 Deprecation notices
  - 6.4.3 Migration timeline
- 6.5 Migration guide structure
  - 6.5.1 Before/after examples
  - 6.5.2 Step-by-step instructions
  - 6.5.3 Common issues and solutions

---

## Part Files

This content has been split into focused parts for easier reference:

### Part 1: PR Descriptions
**File**: [templates-for-humans-part1-pr-descriptions.md](templates-for-humans-part1-pr-descriptions.md)

**When to read**: When creating or reviewing pull requests.

**Contents**:
- 6.1.1 Summary section - Lead with what and why in plain language
- 6.1.2 Changes section with bullets - Break down changes into scannable points
- 6.1.3 Testing section - Document what testing was performed
- 6.1.4 Screenshots for UI changes - Visual documentation for UI work

---

### Part 2: Commit Messages
**File**: [templates-for-humans-part2-commit-messages.md](templates-for-humans-part2-commit-messages.md)

**When to read**: When writing commit messages or setting up commit conventions.

**Contents**:
- 6.2.1 Conventional commits format - Type/scope/subject structure
- 6.2.2 Subject line rules - 50 chars, imperative mood, no period
- 6.2.3 Body content guidelines - Explain the why, not just the what

---

### Part 3: Release Notes
**File**: [templates-for-humans-part3-release-notes.md](templates-for-humans-part3-release-notes.md)

**When to read**: When preparing release notes or changelogs.

**Contents**:
- 6.3.1 User-facing language - Translate technical changes into benefits
- 6.3.2 Grouping by type - Organize by features, fixes, breaking changes
- 6.3.3 Linking to issues and PRs - Connect notes to detailed information

---

### Part 4: Breaking Changes
**File**: [templates-for-humans-part4-breaking-changes.md](templates-for-humans-part4-breaking-changes.md)

**When to read**: When introducing breaking changes or deprecating features.

**Contents**:
- 6.4.1 Warning users in advance - Announce changes before they happen
- 6.4.2 Deprecation notices - Where and how to add warnings
- 6.4.3 Migration timeline - Give realistic milestones

---

### Part 5: Migration Guides
**File**: [templates-for-humans-part5-migration-guides.md](templates-for-humans-part5-migration-guides.md)

**When to read**: When writing migration guides or updating APIs.

**Contents**:
- 6.5.1 Before/after examples - Show exact transformations
- 6.5.2 Step-by-step instructions - Numbered steps with verification
- 6.5.3 Common issues and solutions - Anticipate and solve problems
- Complete PR Template - Copy-paste template for `.github/PULL_REQUEST_TEMPLATE.md`

---

## Quick Reference

### PR Description Essentials
1. Start with **Summary**: What and why in 1-2 sentences
2. List **Changes**: New features, modifications, removals, dependencies
3. Document **Testing**: Automated and manual verification
4. Add **Screenshots**: Before/after for UI changes

### Commit Message Essentials
```
<type>(<scope>): <subject>

<body - explain why>

<footer - related issues>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

### Release Notes Essentials
- Write for **users**, not developers
- Group by: Highlights, Features, Improvements, Bug Fixes, Breaking Changes
- Link to issues and PRs for details

### Breaking Change Essentials
1. **Warn early**: At least one release before removal
2. **Deprecate clearly**: Warnings in code, docs, API headers
3. **Provide timeline**: Dates and versions for each phase
4. **Guide migration**: Step-by-step with examples

---

## See Also

- [agent-communication-formats.md](agent-communication-formats.md) - Formats for inter-agent messages
- [inter-agent-protocols.md](inter-agent-protocols.md) - Communication protocols between agents
