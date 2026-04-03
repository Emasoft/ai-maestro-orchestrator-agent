---
name: amoa-developer-communication
description: "Use when communicating with human developers in code reviews and issues. Trigger with PR review or status update requests. Loaded by ai-maestro-orchestrator-agent-main-agent"
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  version: 1.0.0
  author: Emasoft
context: fork
user-invocable: false
agent: amoa-main
---

# Developer Communication Skill

## Overview

Effective communication with human developers in code reviews, issues, and status updates.

## Prerequisites

Code review familiarity and access to communication channels.

## Output

Markdown message with communication type, tone assessment, blocking status, and reference links.

## Instructions

1. **Identify type** — PR comment, issue, explanation, status, or conflict.
2. **Review principles** in [references/key-principles.md](references/key-principles.md)
   <!-- TOC: Assume Good Intent | Be Specific, Not Vague | Separate Blocking from Non-Blocking | Acknowledge Good Work | Provide Context for Your Feedback -->
3. **Select reference** via [references/decision-tree.md](references/decision-tree.md)
   <!-- TOC: Decision Tree: Choosing Communication Type -->
4. **Draft message** following reference patterns.
5. **Run pre-send checklist** from [references/tone-quick-reference.md](references/tone-quick-reference.md)
   <!-- TOC: Communication Tone Quick Reference | Examples of Constructive Communication | Example 1: Constructive Code Review Comment | Example 2: Acknowledging Good Work | Error Handling in Communication | Pre-Send Checklist -->
6. **Send and monitor** for follow-up.

Copy this checklist and track your progress:

- [ ] Identified type and selected reference via decision tree
- [ ] Applied key principles (good intent, specific, blocking status)
- [ ] Drafted message and passed pre-send checklist
- [ ] Sent and monitoring for follow-up

## Error Handling

See [references/conflict-resolution.md](references/conflict-resolution.md)
<!-- TOC: 1 Disagreeing professionally | 1.1 Separating the idea from the person | 1.2 Starting with understanding | 1.3 Using "I think" not "You're wrong" | 2 Offering alternatives | 2.1 The "Yes, and" technique | 2.2 Presenting options without attachment | 2.3 Showing concrete examples | 3 Finding compromise | 3.1 Identifying shared goals | 3.2 Proposing incremental solutions | 3.3 Time-boxing experiments | 4 Escalation paths | 4.1 When to bring in a third party | 4.2 Technical leads and architects | 4.3 Documenting the disagreement | 5 When to involve maintainers | 5.1 Stalled discussions | 5.2 Blocking PRs | 5.3 Community conduct issues -->
and [references/tone-quick-reference.md](references/tone-quick-reference.md)
<!-- TOC: Communication Tone Quick Reference | Examples of Constructive Communication | Example 1: Constructive Code Review Comment | Example 2: Acknowledging Good Work | Error Handling in Communication | Pre-Send Checklist -->

## Examples

**Input:** PR uses unsafe string concatenation for SQL queries.
**Output:** Non-blocking: "Consider parameterized queries — e.g. `cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))`."

See `references/op-*.md` for walkthroughs.

## Resources

- [reference-catalog.md](references/reference-catalog.md)
    - PR Comment Writing
    - Issue Communication
    - Technical Explanation
    - Conflict Resolution
    - Status Updates
    - Templates for Humans
- [key-principles.md](references/key-principles.md)
    - 1. Assume Good Intent
    - 2. Be Specific, Not Vague
    - 3. Separate Blocking from Non-Blocking
    - 4. Acknowledge Good Work
    - 5. Provide Context for Your Feedback
- [decision-tree.md](references/decision-tree.md)
- [tone-quick-reference.md](references/tone-quick-reference.md)
  - Examples of Constructive Communication
    - Example 1: Constructive Code Review Comment
    - Example 2: Acknowledging Good Work
  - Error Handling in Communication
  - Pre-Send Checklist

