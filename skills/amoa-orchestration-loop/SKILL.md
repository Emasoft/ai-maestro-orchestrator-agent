---
name: amoa-orchestration-loop
description: "Use when running the orchestrator loop or managing stop hook behavior. Trigger with loop, stop hook, or state file requests."
license: Apache-2.0
compatibility: "Python 3.8+, PyYAML, GitHub CLI, AI Maestro."
metadata:
  author: Emasoft
  version: 1.0.0
user-invocable: false
context: fork
agent: amoa-main
---

# Orchestration Loop Skill

## Overview

Manages the orchestrator loop lifecycle, stop hook behavior, and state files during orchestration.

## Prerequisites

Orchestration Phase active, state file `design/state/exec-phase.md` exists.

## Output

Loop state reports, stop hook blocking reasons, state file updates.

## Instructions

1. Start loop with `/orchestrator-loop` for continuous task processing
2. Loop monitors task sources (Claude Tasks, GitHub Projects, task files, TODO list)
3. Uses 4-loop verification before allowing completion
4. Stop hook blocks exit when tasks pending; signal `ALL_TASKS_COMPLETE`

Copy this checklist and track your progress:

- [ ] Start loop with `/orchestrator-loop`
- [ ] Monitor via `/orchestration-status` every 10-15 min
- [ ] Cancel with `/cancel-orchestrator` when complete

See [orchestration-loop-mechanics.md](references/orchestration-loop-mechanics.md)
<!-- TOC: Orchestration Loop Mechanics | What the Orchestrator Loop Does | Loop Lifecycle | State File Structure | Task Source Monitoring and Priority | Iteration Counting and Max Iterations | Verification Mode (4-Loop Quadruple-Check) | Completion Signals (ALL_TASKS_COMPLETE) | Stop Hook Behavior and Blocking Logic -->

See [stop-hook-behavior.md](references/stop-hook-behavior.md)
<!-- TOC: Blocking Conditions | Completion Signals | Recovery Behavior -->

See [state-file-format.md](references/state-file-format.md)
<!-- TOC: State File Format | Loop State File Format and Fields | Execution Phase State File Format | Frontmatter Field Definitions | How to Manually Edit State Files | State File Corruption Recovery -->

## Examples

**Input:** `/orchestrator-loop "Complete auth tasks" --max-iterations 50`
**Output:** Continuous processing started, monitoring all task sources.

More: [examples.md](references/examples.md)
<!-- TOC: Example 1: Complete Orchestration Start | Example 2: Orchestrator Loop Usage | Example 3: Monitoring During Implementation -->

## Error Handling

See [troubleshooting.md](references/troubleshooting.md)
<!-- TOC: Troubleshooting | Loop Won't Start - Common Causes | Stop Hook Not Firing - Debugging Steps | Tasks Showing as Pending Incorrectly | Lock File Issues and Stale Locks | Concurrent Execution Conflicts | Verification Mode Stuck | Helper Script Failures | Using /reload-plugins | General Debugging Workflow -->

## Resources

See reference files above for complete details on loop mechanics, state files, and troubleshooting.
