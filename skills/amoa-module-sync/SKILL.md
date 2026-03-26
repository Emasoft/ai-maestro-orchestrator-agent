---
name: amoa-module-sync
description: "Use when syncing modules with GitHub Issues or troubleshooting module state. Trigger with sync, issue, or module troubleshooting requests."
license: Apache-2.0
compatibility: Python 3.8+, PyYAML, gh CLI, AI Maestro.
metadata:
  author: Emasoft
  version: 1.0.0
user-invocable: false
context: fork
agent: amoa-main
---

# Module Sync and Troubleshooting Skill

## Overview

Synchronizes module state with GitHub Issues and provides troubleshooting for module management.

## Prerequisites

Orchestration Phase active, gh CLI authenticated, AI Maestro running.

## Output

Sync status reports, issue creation/update confirmations, troubleshooting guidance.

## Instructions

1. Identify sync or troubleshooting scenario
2. Run the appropriate procedure from the references below
3. Verify state consistency between local state file and GitHub Issues

Copy this checklist and track your progress:

- [ ] Identify sync or troubleshooting scenario
- [ ] Execute procedure and verify state consistency
- [ ] Confirm GitHub Issues match local state

Usage examples: [usage-examples.md](./references/usage-examples.md)
<!-- TOC: 1 Add new module mid-orchestration | 2 Reassign a blocked module | 3 Scripts reference for programmatic access -->

Issue sync: [github-issue-sync.md](./references/github-issue-sync.md)
<!-- TOC: 1 Issue creation format and labels | 2 Issue update synchronization | 3 Issue closure protocols | 4 Label conventions (module, priority:*, status:*) | 5 Manual sync when automation fails | 6 Troubleshooting sync issues -->

## Examples

**Input:** `Module auth-core has no GitHub Issue`
**Output:** Issue created, labels applied, state file updated with issue number.

**Input:** `State file shows 5 modules but only 3 GitHub Issues exist`
**Output:** Missing issues created, sync verified.

## Error Handling

Issue not created: run `gh auth login`. State corruption: see troubleshooting guide.

Guide: [troubleshooting.md](./references/troubleshooting.md)
<!-- TOC: 1 State file corruption recovery | 2 GitHub sync failure recovery | 3 Agent notification failures | 4 Module ID conflicts | 5 Force removal scenarios -->

## Resources

- [usage-examples.md](./references/usage-examples.md)
<!-- TOC: 1 Add new module mid-orchestration | 2 Reassign a blocked module | 3 Scripts reference for programmatic access -->
  - 1 Add New Module Mid-Orchestration
  - 2 Reassign Blocked Module
  - 3 Scripts Reference
- [github-issue-sync.md](./references/github-issue-sync.md)
<!-- TOC: 1 Issue creation format and labels | 2 Issue update synchronization | 3 Issue closure protocols | 4 Label conventions (module, priority:*, status:*) | 5 Manual sync when automation fails | 6 Troubleshooting sync issues -->
  - 6.1 Issue Creation Format and Labels
    - Automatic Issue Creation
    - Issue Title Format
    - Issue Body Format
  - Module: {module_name}
    - Description
    - Acceptance Criteria
    - Priority
    - Related
    - Labels Applied on Creation
    - Issue Creation Command
    - Capturing Issue Number
  - 6.2 Issue Update Synchronization
    - Triggering Updates
    - Name Change Sync
  - ...
- [troubleshooting.md](./references/troubleshooting.md)
<!-- TOC: 1 State file corruption recovery | 2 GitHub sync failure recovery | 3 Agent notification failures | 4 Module ID conflicts | 5 Force removal scenarios -->
  - 7.1 State File Corruption Recovery
    - Detecting Corruption
    - Common Corruption Causes
    - Recovery from Git
    - Recovery from Backup
    - Manual Reconstruction
    - Minimal Valid State File
  - 7.2 GitHub Sync Failure Recovery
    - Diagnosing Sync Failures
    - Issue Creation Failed
    - Issue Update Failed
    - Issue Closure Failed
    - Bulk Sync Recovery
  - 7.3 Agent Notification Failures
    - Diagnosing Notification Failures
  - ...
- [checklist-and-scripts.md](./references/checklist-and-scripts.md)
  - 1 Module Management Checklist
  - 2 Script Output Rules
