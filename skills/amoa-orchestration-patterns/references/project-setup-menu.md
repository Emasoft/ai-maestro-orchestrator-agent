# Project Setup Interactive Menu - Index


## Contents

- [Overview](#overview)
- [Document Structure](#document-structure)
  - [[Part 1: Team, Repository & Release Configuration](project-setup-menu-part1-team-repo-release.md)](#part-1-team-repository-release-configurationproject-setup-menu-part1-team-repo-releasemd)
  - [[Part 2: Documentation & Quality Requirements](project-setup-menu-part2-docs-quality.md)](#part-2-documentation-quality-requirementsproject-setup-menu-part2-docs-qualitymd)
  - [[Part 3: Implementation & Troubleshooting](project-setup-menu-part3-implementation-troubleshooting.md)](#part-3-implementation-troubleshootingproject-setup-menu-part3-implementation-troubleshootingmd)
- [Quick Navigation by Use Case](#quick-navigation-by-use-case)
- [Storage Keys Reference](#storage-keys-reference)

---

## Overview

This document provides an index to the Project Setup Interactive Menu guide, which has been split into three parts for easier navigation and loading.

**CRITICAL RULE**: Never assume defaults. Always ask. Store responses in project memory for future reference.

---

## Document Structure

### [Part 1: Team, Repository & Release Configuration](project-setup-menu-part1-team-repo-release.md)

**Contents:**
- Overview and Use-Case Quick Reference
- Team Configuration
  - Question 1: Human Developers
  - Question 2: AI Remote Agents
  - Question 3: Access Permissions
- Repository Configuration
  - Question 4: Branch Protection
  - Question 5: Required Reviews
  - Question 6: CI Requirements
- Release Strategy
  - Question 7: Alpha-Only Development
  - Question 8: Package Publishing
  - Question 9: Versioning Scheme

**When to read:** Setting up team structure, configuring repository settings, defining release strategy

---

### [Part 2: Documentation & Quality Requirements](project-setup-menu-part2-docs-quality.md)

**Contents:**
- Documentation Strategy
  - Question 10: Continuous Documentation
  - Question 11: Deferred Documentation
- Quality Requirements
  - Question 12: Test Coverage Target
  - Question 13: Linting Strictness

**When to read:** Configuring documentation standards, setting quality gates and linting rules

---

### [Part 3: Implementation & Troubleshooting](project-setup-menu-part3-implementation-troubleshooting.md)

**Contents:**
- Menu Implementation
  - Using AskUserQuestion Tool
  - Interactive Flow Pattern
- Response Handling
  - Storage Location
  - Using Stored Configuration
  - Configuration Updates
- Troubleshooting
  - User Skips Setup
  - Conflicting Answers
  - Changed Mind Mid-Project
  - Missing Configuration File
- Best Practices
- Example Session

**When to read:** Implementing the setup menu, handling responses, debugging issues, seeing full example

---

## Quick Navigation by Use Case

| Use Case | Go To |
|----------|-------|
| Starting a new project | [Part 3 - Menu Implementation](project-setup-menu-part3-implementation-troubleshooting.md#menu-implementation) |
| Setting up AI agents | [Part 1 - Question 2](project-setup-menu-part1-team-repo-release.md#question-2-ai-remote-agents) |
| Configuring branch protection | [Part 1 - Question 4](project-setup-menu-part1-team-repo-release.md#question-4-branch-protection) |
| Setting CI requirements | [Part 1 - Question 6](project-setup-menu-part1-team-repo-release.md#question-6-ci-requirements) |
| Alpha-only development | [Part 1 - Question 7](project-setup-menu-part1-team-repo-release.md#question-7-alpha-only-development) |
| Package publishing | [Part 1 - Question 8](project-setup-menu-part1-team-repo-release.md#question-8-package-publishing) |
| Documentation standards | [Part 2 - Documentation Strategy](project-setup-menu-part2-docs-quality.md#documentation-strategy) |
| Test coverage targets | [Part 2 - Question 12](project-setup-menu-part2-docs-quality.md#question-12-test-coverage-target) |
| Linting configuration | [Part 2 - Question 13](project-setup-menu-part2-docs-quality.md#question-13-linting-strictness) |
| Configuration file format | [Part 3 - Storage Location](project-setup-menu-part3-implementation-troubleshooting.md#storage-location) |
| Using stored config | [Part 3 - Using Stored Configuration](project-setup-menu-part3-implementation-troubleshooting.md#using-stored-configuration) |
| User skipped setup | [Part 3 - Troubleshooting](project-setup-menu-part3-implementation-troubleshooting.md#user-skips-setup) |
| Configuration conflicts | [Part 3 - Conflicting Answers](project-setup-menu-part3-implementation-troubleshooting.md#conflicting-answers) |
| Full example session | [Part 3 - Example Session](project-setup-menu-part3-implementation-troubleshooting.md#example-session) |

---

## Storage Keys Reference

| Key | Description | Document |
|-----|-------------|----------|
| `team.human_developers` | Human developer count and usernames | Part 1 |
| `team.ai_agents` | AI agent configuration | Part 1 |
| `team.permissions` | Access restrictions | Part 1 |
| `repo.branch_protection` | Protected branch rules | Part 1 |
| `repo.required_reviews` | PR approval requirements | Part 1 |
| `repo.ci_requirements` | CI/CD check requirements | Part 1 |
| `release.alpha_only` | Alpha development strategy | Part 1 |
| `release.package_publishing` | Registry publishing config | Part 1 |
| `release.versioning` | Version scheme settings | Part 1 |
| `docs.continuous` | Auto-generated docs config | Part 2 |
| `docs.deferred` | Inline documentation standards | Part 2 |
| `quality.coverage` | Test coverage requirements | Part 2 |
| `quality.linting` | Linter configuration | Part 2 |
