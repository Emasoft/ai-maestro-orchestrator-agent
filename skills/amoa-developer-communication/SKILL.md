---
name: amoa-developer-communication
description: "Use when communicating with human developers in code reviews and issues. Trigger with PR review or status update requests."
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
<!-- TOC: Conflict Resolution Guide | Disagreeing Professionally | Separating the Idea from the Person | Starting with Understanding | Using "I Think" Not "You're Wrong" | Offering Alternatives | The "Yes, And" Technique | Presenting Options Without Attachment | Showing Concrete Examples | Finding Compromise | Identifying Shared Goals | Proposing Incremental Solutions | Time-Boxing Experiments | Escalation Paths | When to Bring in a Third Party | Technical Leads and Architects | Documenting the Disagreement | When to Involve Maintainers | Stalled Discussions | Blocking PRs | Community Conduct Issues | Summary: Conflict Resolution Checklist -->
and [references/tone-quick-reference.md](references/tone-quick-reference.md)
<!-- TOC: Communication Tone Quick Reference | Examples of Constructive Communication | Example 1: Constructive Code Review Comment | Example 2: Acknowledging Good Work | Error Handling in Communication | Pre-Send Checklist -->

## Examples

**Input:** PR uses unsafe string concatenation for SQL queries.
**Output:** Non-blocking: "Consider parameterized queries — e.g. `cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))`."

See `references/op-*.md` for walkthroughs.

## Resources

- [reference-catalog.md](references/reference-catalog.md)
  <!-- TOC: PR Comment Writing | Issue Communication | Technical Explanation | Conflict Resolution | Status Updates | Templates for Humans -->
- [key-principles.md](references/key-principles.md)
  <!-- TOC: Assume Good Intent | Be Specific, Not Vague | Separate Blocking from Non-Blocking | Acknowledge Good Work | Provide Context -->
- [decision-tree.md](references/decision-tree.md)
  <!-- TOC: Decision Tree: Choosing Communication Type -->
- [tone-quick-reference.md](references/tone-quick-reference.md)
  <!-- TOC: Communication Tone Quick Reference | Examples of Constructive Communication | Example 1: Constructive Code Review Comment | Example 2: Acknowledging Good Work | Error Handling in Communication | Pre-Send Checklist -->

