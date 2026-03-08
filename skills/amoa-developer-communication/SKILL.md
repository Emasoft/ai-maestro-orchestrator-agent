---
name: amoa-developer-communication
description: "Use when communicating with human developers in code reviews and issues. Trigger with PR review or status update requests."
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  version: 1.0.0
  author: Emasoft
  tags: "communication, code-review, documentation, collaboration"
  audience: AI agents working with human developers
  prerequisites: None
context: fork
user-invocable: false
agent: amoa-main
---

# Developer Communication Skill

## Overview

This skill teaches effective communication with **human developers** across code reviews, issues, technical discussions, and status updates.

## Prerequisites

- Code review process familiarity
- Access to communication channels (GitHub, Slack, etc.)

## Output

- **Communication Type** (String) — PR comment, issue response, explanation, status update
- **Tone Assessment** (Pass/Fail) — Respectful, specific, constructive
- **Blocking Status** — "Blocking" or "Non-blocking"
- **Message Content** (Markdown) — The communication to send
- **References** (URL list) — Links to relevant code, issues, docs

## Instructions

1. **Identify the communication type** — PR comment, issue, explanation, status, or conflict.
2. **Understand human-AI communication differences** — See: [references/key-principles.md](references/key-principles.md)
   <!-- TOC: Assume Good Intent | Be Specific, Not Vague | Separate Blocking from Non-Blocking | Acknowledge Good Work | Provide Context for Your Feedback -->
3. **Use the decision tree** to select the right reference. See: [references/decision-tree.md](references/decision-tree.md)
   <!-- TOC: Decision Tree: Choosing Communication Type -->
4. **Apply key principles** — Assume good intent, be specific, separate blocking/non-blocking.
5. **Draft your message** following the relevant reference document patterns.
6. **Run the pre-send checklist**. See: [references/tone-quick-reference.md](references/tone-quick-reference.md)
   <!-- TOC: Examples of Constructive Communication | Error Handling in Communication | Pre-Send Checklist -->
7. **Send and monitor** for responses or follow-up needs.

Copy this checklist and track your progress:

- [ ] Identified communication type
- [ ] Selected reference document via decision tree
- [ ] Applied key principles (good intent, specific, blocking status)
- [ ] Drafted message following reference patterns
- [ ] Passed pre-send checklist
- [ ] Sent and monitoring for follow-up

---

## Error Handling

Consult [references/conflict-resolution.md](references/conflict-resolution.md) for de-escalation
<!-- TOC: Disagreeing Professionally | Offering Alternatives | Finding Compromise | Escalation Paths | When to Involve Maintainers -->
and [references/tone-quick-reference.md](references/tone-quick-reference.md) for the pre-send checklist.
<!-- TOC: Constructive Communication | Error Handling in Communication | Pre-Send Checklist -->

## Examples

**Input:** PR uses unsafe string concatenation for SQL queries.
**Output:** Non-blocking suggestion: "Consider parameterized queries to prevent SQL injection — e.g. `cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))`."

See `references/op-*.md` runbooks for more walkthroughs.

## Resources

- [reference-catalog.md](references/reference-catalog.md) — Full reference catalog
  <!-- TOC: PR Comment Writing | Issue Communication | Technical Explanation | Conflict Resolution | Status Updates | Templates for Humans -->
- [key-principles.md](references/key-principles.md) — Communication principles
  <!-- TOC: Assume Good Intent | Be Specific, Not Vague | Separate Blocking from Non-Blocking | Acknowledge Good Work | Provide Context -->
- [decision-tree.md](references/decision-tree.md) — Communication type selection
  <!-- TOC: Decision Tree: Choosing Communication Type -->
- [tone-quick-reference.md](references/tone-quick-reference.md) — Tone and pre-send checklist
  <!-- TOC: Constructive Communication | Error Handling in Communication | Pre-Send Checklist -->

## Script Output Rules

Scripts MUST: write verbose output to `docs_dev/reports/`, emit only `[OK/ERROR] name - summary` + `Report: path` to stdout. Exception: `scripts/amoa_stop_check/` outputs JSON (hook requirement).
