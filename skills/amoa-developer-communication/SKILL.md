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
  <!-- TOC: PR Comment Writing | Issue Communication | Technical Explanation | Conflict Resolution | Status Updates | Templates for Humans | 1 Writing constructive code review comments | 1.1 The praise-suggestion-question framework | 1.2 Balancing thoroughness with developer time | 2 Tone guidelines for professional reviews | 2.1 Avoiding pedantic or condescending language | 2.2 Using "we" instead of "you" | 3 When to request changes versus suggest | 3.1 Blocking issues that require changes | 3.2 Non-blocking suggestions and nits | 3.3 Praise-only approvals | 4 Acknowledging good code patterns | 5 Avoiding accusatory language | 5.1 Why "you" statements feel like attacks | 5.2 Reframing with "this" and "we" | 6 Examples of good versus bad comments | 1 Bug report response workflow | 1.1 Acknowledgment template | 1.2 Reproduction confirmation | 1.3 Investigation updates | 1.4 Resolution communication | 2 Feature request acknowledgment | 2.1 Thanking and validating the idea | 2.2 Setting scope expectations | 2.3 Linking to roadmap or discussions | 3 Asking clarifying questions | 3.1 One question at a time rule | 3.2 Providing response options | 3.3 Explaining why you need the information | 4 Setting expectations on timeline | 4.1 Never promise specific dates | 4.2 Using priority and milestone indicators | 4.3 Managing stale issues | 5 Closing issues gracefully | 5.1 Duplicate handling | 5.2 Won't-fix explanations | 5.3 Inviting future feedback | 1 Explaining technical decisions | 1.1 The context-decision-consequences format | 1.2 Acknowledging tradeoffs honestly | 1.3 Referencing alternatives considered | 2 Justifying architectural choices | 2.1 Connecting to requirements | 2.2 Explaining scalability and maintainability | 2.3 Addressing security implications | 3 Providing context for non-obvious code | 3.1 When comments are necessary | 3.2 Linking to issues or ADRs | 3.3 Explaining workarounds and technical debt | 4 Linking to relevant documentation | 4.1 Internal wiki and ADRs | 4.2 External specifications | 4.3 Code examples in the codebase | 5 Using code examples effectively | 5.1 Before/after comparisons | 5.2 Minimal reproducible examples | 5.3 Annotated code blocks | 1 Disagreeing professionally | 1.1 Separating the idea from the person | 1.2 Starting with understanding | 1.3 Using "I think" not "You're wrong" | 2 Offering alternatives | 2.1 The "Yes, and" technique | 2.2 Presenting options without attachment | 2.3 Showing concrete examples | 3 Finding compromise | 3.1 Identifying shared goals | 3.2 Proposing incremental solutions | 3.3 Time-boxing experiments | 4 Escalation paths | 4.1 When to bring in a third party | 4.2 Technical leads and architects | 4.3 Documenting the disagreement | 5 When to involve maintainers | 5.1 Stalled discussions | 5.2 Blocking PRs | 5.3 Community conduct issues | 1 Progress report format | 1.1 What was done (concrete deliverables) | 1.2 What's next (clear next steps) | 1.3 Blockers (actionable items) | 2 Blocker communication | 2.1 Describing the blocker clearly | 2.2 What you've tried | 2.3 What you need to unblock | 3 ETA setting and adjustment | 3.1 Ranges not points | 3.2 Early communication of delays | 3.3 Explaining scope changes | 4 Completion notification | 4.1 Summary of changes | 4.2 Testing performed | 4.3 What reviewers should focus on | 5 Post-mortem communication | 5.1 Blameless retrospective format | 5.2 What we learned | 5.3 Action items and owners | 1 Pull Request description template | 1.1 Summary section | 1.2 Changes section with bullets | 1.3 Testing section | 1.4 Screenshots for UI changes | 2 Commit message guidelines | 2.1 Conventional commits format | 2.2 Subject line rules | 2.3 Body content guidelines | 3 Release notes format | 3.1 User-facing language | 3.2 Grouping by type | 3.3 Linking to issues and PRs | 4 Breaking change communication | 4.1 Warning users in advance | 4.2 Deprecation notices | 4.3 Migration timeline | 5 Migration guide structure | 5.1 Before/after examples | 5.2 Step-by-step instructions | 5.3 Common issues and solutions -->
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
  <!-- TOC: Decision Tree: Choosing Communication Type -->
- [tone-quick-reference.md](references/tone-quick-reference.md)
  <!-- TOC: Communication Tone Quick Reference | Examples of Constructive Communication | Error Handling in Communication | Pre-Send Checklist -->
  - Examples of Constructive Communication
    - Example 1: Constructive Code Review Comment
    - Example 2: Acknowledging Good Work
  - Error Handling in Communication
  - Pre-Send Checklist
