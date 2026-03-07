---
name: amoa-developer-communication
description: "Trigger with developer communication needs. Use when communicating with human developers in code reviews, issues, technical discussions, and status updates. Covers effective communication patterns."
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

- Understanding of code review processes
- Access to communication channels (GitHub, Slack, etc.)
- Familiarity with professional communication standards

## Output

| Field | Description | Format |
|-------|-------------|--------|
| Communication Type | PR comment, issue response, technical explanation, status update, etc. | String |
| Tone Assessment | Respectful, specific, constructive | Pass/Fail with notes |
| Blocking Status | Whether feedback is blocking or non-blocking | "Blocking" / "Non-blocking" |
| Message Content | The actual communication to send | Markdown |
| References | Links to relevant code, issues, or documentation | List of URLs |

## Instructions

1. **Identify the communication type** - PR comment, issue response, technical explanation, status update, or conflict resolution.
2. **Understand human-AI communication differences** - Human communication is natural language, warm, contextual, and async (unlike structured AI-to-AI templates). See: [references/key-principles.md](references/key-principles.md)
3. **Use the decision tree** to select the right reference document. See: [references/decision-tree.md](references/decision-tree.md)
4. **Apply key principles** - Assume good intent, be specific, separate blocking/non-blocking, acknowledge good work, provide context. See: [references/key-principles.md](references/key-principles.md)
5. **Draft your message** following the patterns in the relevant reference document.
6. **Run the pre-send checklist** to verify quality and professionalism. See: [references/tone-quick-reference.md](references/tone-quick-reference.md)
7. **Send and monitor** for responses or follow-up needs.

---

## Reference Documents

Full catalog with detailed contents listings: [references/reference-catalog.md](references/reference-catalog.md)

| Document | Use When |
|----------|----------|
| [pr-comment-writing.md](references/pr-comment-writing.md) | Writing code review comments on PRs |
| [issue-communication.md](references/issue-communication.md) | Responding to bug reports, feature requests, questions |
| [technical-explanation.md](references/technical-explanation.md) | Explaining architecture, design decisions, non-obvious code |
| [conflict-resolution.md](references/conflict-resolution.md) | Disagreeing with approaches or resolving technical disputes |
| [status-updates.md](references/status-updates.md) | Reporting progress, blockers, completion updates |
| [templates-for-humans.md](references/templates-for-humans.md) | Writing PRs, commits, release notes, migration guides |

Tone examples, communication examples, error handling, and pre-send checklist: [references/tone-quick-reference.md](references/tone-quick-reference.md)

---

## Error Handling

When communication fails or receives negative feedback, consult [references/conflict-resolution.md](references/conflict-resolution.md) for de-escalation patterns and [references/tone-quick-reference.md](references/tone-quick-reference.md) for the pre-send checklist to prevent recurrence.

## Examples

Practical examples for each communication type are embedded in the corresponding reference documents. Start with the operation runbooks (`references/op-*.md`) for step-by-step walkthroughs.

## Resources

- [Reference Catalog](references/reference-catalog.md) -- full index of all reference documents
- [Key Principles](references/key-principles.md) -- foundational communication guidelines
- [Decision Tree](references/decision-tree.md) -- selecting the right communication pattern

---

## Script Output Rules

All scripts invoked by this skill MUST follow the token-efficient output protocol:

1. **Verbose output** goes to a timestamped report file in `docs_dev/reports/`
2. **Stdout** emits only 2-3 lines: `[OK/ERROR] script_name - summary` + `Report: path`
3. Scripts accept `--output-dir` to override the default report directory
4. **EXCEPTION**: Scripts in `scripts/amoa_stop_check/` MUST output JSON to stdout (Claude Code hook requirement)
