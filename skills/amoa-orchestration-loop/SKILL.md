---
name: amoa-orchestration-loop
description: "Use when running the orchestrator loop or managing stop hook behavior. Trigger with loop, stop hook, or state file requests. Loaded by ai-maestro-orchestrator-agent-main-agent"
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
<!-- TOC: 1 What the orchestrator loop does | 2 Task source monitoring and priority | 3 Iteration counting and max iterations | 4 Verification mode (4-loop quadruple-check) | 5 Completion signals (ALL_TASKS_COMPLETE) | 6 Stop hook behavior and blocking logic -->

See [stop-hook-behavior.md](references/stop-hook-behavior.md)
<!-- TOC: Blocking conditions - When the stop hook prevents exit | Completion signals - How to signal task completion | Recovery behavior - Fail-safe and retry logic -->

See [state-file-format.md](references/state-file-format.md)
<!-- TOC: 1 Loop state file format and fields | 2 Execution phase state file format | 3 Frontmatter field definitions | 4 How to manually edit state files | 5 State file corruption recovery -->

## Examples

**Input:** `/orchestrator-loop "Complete auth tasks" --max-iterations 50`
**Output:** Continuous processing started, monitoring all task sources.

More: [examples.md](references/examples.md)
<!-- TOC: Complete Orchestration Start - Full startup workflow | Orchestrator Loop Usage - Loop start, status, cancel | Monitoring During Implementation - Agent checking workflow -->

## Error Handling

See [troubleshooting.md](references/troubleshooting.md)
<!-- TOC: 1 Loop won't start - common causes | 2 Stop hook not firing - debugging steps | 3 Tasks showing as pending incorrectly | 4 Lock file issues and stale locks | 5 Concurrent execution conflicts | 6 Verification mode stuck | 7 Helper script failures | 8 Using /reload-plugins -->

## Resources

See reference files above for complete details on loop mechanics, state files, and troubleshooting.
