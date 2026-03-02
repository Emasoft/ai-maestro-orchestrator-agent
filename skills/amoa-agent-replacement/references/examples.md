# Agent Replacement Examples

## Table of Contents

- [Example 1: Standard Replacement Flow](#example-1-standard-replacement-flow)
- [Example 2: Emergency Replacement with Partial Context](#example-2-emergency-replacement-with-partial-context)

## Use-Case TOC

- When doing a standard replacement → [Example 1](#example-1-standard-replacement-flow)
- When context compilation fails → [Example 2](#example-2-emergency-replacement-with-partial-context)

---

## Example 1: Standard Replacement Flow

```bash
# ECOS notification received for implementer-1 failing
# Step 1: Compile context
/eoa-generate-replacement-handoff --failed-agent implementer-1 --new-agent implementer-2 --include-tasks --include-context

# Step 2: Reassign kanban
/eoa-reassign-kanban-tasks --from-agent implementer-1 --to-agent implementer-2 --project-id 12345

# Step 3: Verify replacement
# - Check AI Maestro for ACK from implementer-2
# - Verify state file updated
# - Confirm ECOS notified
```

---

## Example 2: Emergency Replacement with Partial Context

```bash
# Context compilation partially failed (git history unavailable)
# Generate partial handoff with gaps flagged
/eoa-generate-replacement-handoff --failed-agent implementer-1 --new-agent implementer-2 --partial --flag-gaps

# Instruct new agent to report discovered context
# Monitor first status report closely
```
