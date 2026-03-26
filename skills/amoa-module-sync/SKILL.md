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
<!-- TOC: 1 Add New Module Mid-Orchestration | 2 Reassign Blocked Module | 3 Scripts Reference -->

Issue sync: [github-issue-sync.md](./references/github-issue-sync.md)
<!-- TOC: GitHub Issue Synchronization Reference | Issue Creation Format and Labels | Issue Update Synchronization | Issue Closure Protocols | Label Conventions | Manual Sync When Automation Fails | Troubleshooting Sync Issues | Sync State Diagram | Related Commands -->

## Examples

**Input:** `Module auth-core has no GitHub Issue`
**Output:** Issue created, labels applied, state file updated with issue number.

**Input:** `State file shows 5 modules but only 3 GitHub Issues exist`
**Output:** Missing issues created, sync verified.

## Error Handling

Issue not created: run `gh auth login`. State corruption: see troubleshooting guide.

Guide: [troubleshooting.md](./references/troubleshooting.md)
<!-- TOC: Module Management Troubleshooting Reference | State File Corruption Recovery | GitHub Sync Failure Recovery | Agent Notification Failures | Module ID Conflicts | Force Removal Scenarios | General Troubleshooting Checklist | Error Reference Table | Related Commands -->

## Resources

- [usage-examples.md](./references/usage-examples.md)
  <!-- TOC: 1 Add New Module Mid-Orchestration | 2 Reassign Blocked Module | 3 Scripts Reference -->
- [github-issue-sync.md](./references/github-issue-sync.md)
  <!-- TOC: GitHub Issue Synchronization Reference | Issue Creation Format and Labels | Issue Update Synchronization | Issue Closure Protocols | Label Conventions | Manual Sync When Automation Fails | Troubleshooting Sync Issues | Sync State Diagram | Related Commands -->
- [troubleshooting.md](./references/troubleshooting.md)
  <!-- TOC: Module Management Troubleshooting Reference | State File Corruption Recovery | GitHub Sync Failure Recovery | Agent Notification Failures | Module ID Conflicts | Force Removal Scenarios | General Troubleshooting Checklist | Error Reference Table | Related Commands -->
- [checklist-and-scripts.md](./references/checklist-and-scripts.md)
  <!-- TOC: Module management checklist | Script output rules and token-efficient protocol -->
