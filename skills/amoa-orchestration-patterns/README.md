# Orchestration Patterns Skill

## Overview

This skill teaches orchestrators how to coordinate work among multiple developers and agents using proven orchestration patterns. It provides comprehensive guidance on task decomposition, agent selection, project setup, and quality verification across multiple programming languages.

## What This Skill Covers

- **Task Complexity Classification**: Evaluate tasks to determine appropriate planning investment
- **Agent Selection**: Choose the right specialized agent for each task based on language, domain, and capabilities
- **Project Setup**: Conduct interactive setup to establish project parameters, team configuration, and quality standards
- **Language Verification**: Ensure code quality, build success, and release readiness with language-specific checklists

## When to Use This Skill

Use this skill when you need to:
- Coordinate work among multiple developers or task agents
- Break down complex goals into parallelizable tasks
- Select appropriate specialized agents for delegation
- Set up a new project with proper configuration
- Verify code quality before commits or releases
- Handle blocked tasks and escalation procedures
- Integrate and verify multi-agent work results

## File Structure

```
orchestration-patterns/
├── SKILL.md                                    # Main skill guide (start here)
├── README.md                                   # This file
└── references/
    ├── task-complexity-classifier.md          # Task complexity assessment methodology
    ├── agent-selection-guide.md               # Specialized agent selection guide
    ├── project-setup-menu.md                  # Interactive project configuration questionnaire
    └── language-verification-checklists.md    # Language-specific quality verification checklists
```

## Quick Start

1. **Read SKILL.md first** - It provides the overview and reading order
2. **Start with Task Complexity Classifier** - Learn to evaluate task complexity
3. **Study Agent Selection Guide** - Understand which agents handle which tasks
4. **Run Project Setup Menu** - Before any project work, establish configuration
5. **Apply Language Verification Checklists** - When reviewing deliverables or before commits

## Key Files

### SKILL.md (Main Guide)
The main entry point for this skill. Provides:
- Core orchestration concepts
- Five-phase workflow (decomposition → assignment → monitoring → escalation → verification)
- Reading order for reference documents
- Quick reference checklist for orchestration work
- Usage examples

### references/task-complexity-classifier.md
Teaches how to classify tasks as Simple, Medium, or Complex to determine appropriate planning investment.

**Use when:**
- Deciding if a task needs planning
- Evaluating task scope and dependencies
- Determining how many agents are needed

### references/agent-selection-guide.md
Comprehensive guide to selecting the right specialized agent for each task.

**Use when:**
- Delegating tasks to agents
- Choosing between language-specific agents (Python, JS, Go, Rust)
- Selecting search agents (hound, SERENA, context)
- Avoiding common agent selection anti-patterns

### references/project-setup-menu.md
Interactive questionnaire for establishing project configuration before any work begins.

**Use when:**
- Starting a new project
- Missing or corrupted configuration
- Understanding team structure and workflow
- Setting up release strategy and quality standards

### references/language-verification-checklists.md
Language-specific checklists for verifying code quality, builds, and release readiness.

**Use when:**
- Verifying Python/Go/JavaScript/TypeScript/Rust projects
- Delegating tasks with quality requirements
- Reviewing agent deliverables
- Preparing for commits or releases

## Core Principles

1. **Never Block the Orchestrator** - Delegate all long-running tasks to agents
2. **One Task Per Agent** - Clear task boundaries prevent confusion and conflicts
3. **Minimal Status Reports** - Request 1-2 line updates only (e.g., "[DONE] task-name - result")
4. **Early Escalation** - Identify blocks at first checkpoint; escalate immediately
5. **Clear Success Criteria** - Each task must have unambiguous completion conditions

## Prerequisites

To use this skill effectively, ensure you have:
1. Multiple developers or task agents available for parallel work
2. A way to track task status (GitHub issues, task lists, or similar)
3. Clear task definitions with success criteria
4. A communication channel for status updates and escalations

## Workflow Overview

The orchestration workflow follows these main phases:

1. **Phase 1: Task Decomposition** - Break down the goal into independent, parallelizable tasks
2. **Phase 2: Task Assignment** - Assign tasks to developers with clear instructions
3. **Phase 3: Progress Monitoring** - Track task completion and identify blocks
4. **Phase 4: Escalation & Unblocking** - Handle blocked tasks and escalate when needed
5. **Phase 5: Integration & Verification** - Combine results and verify completion

## Important Notes

- **Progressive Discovery**: This skill uses progressive discovery - start with SKILL.md and follow the reading order
- **Language-Specific**: Different verification checklists for Python, Go, JavaScript/TypeScript, Rust, and Swift
- **Configuration-Driven**: Project setup creates `.claude/project-config.json` that guides all orchestration decisions
- **Quality-Focused**: Emphasizes code quality, test coverage, and build verification at every step

## License

Apache-2.0

## Version

1.0.0

## Author

Anthropic

## Compatibility

Requires:
- Multiple developers or task agents
- Task tracking system (GitHub issues or similar)
- Clear task definitions with success criteria
- Communication channel for status updates
