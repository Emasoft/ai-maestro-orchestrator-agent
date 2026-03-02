# Document Delivery Protocol - Part 1: Core Rules and Sender Process

**Parent:** [DOCUMENT_DELIVERY_PROTOCOL.md](./DOCUMENT_DELIVERY_PROTOCOL.md)

---

## 1.1 Rule 1: NEVER Send .md Content Directly

- `.md` files MUST NOT be included in AI Maestro message body
- Violates context/token efficiency
- BLOCKED by orchestrator validation
- Any message containing >500 characters of markdown content will be REJECTED

**Rationale:** Full documents consume excessive tokens in message payloads and agent context windows. GitHub issue comments provide persistent storage with URLs for efficient reference.

---

## 1.2 Rule 2: Use GitHub Issue Comments

All documents (`.md` files) MUST be:

1. Uploaded as attachment to a GitHub issue comment
2. Shared via URL to that comment

**Benefits:**
- Persistent audit trail
- Version control via GitHub
- Efficient token usage (URL vs. full content)
- Centralized document storage
- Issue-based context grouping

---

## 1.3 Delivery Process - Sender

The sender follows this four-step process:

### 1.3.1 Step 1: Create/Compile the .md File Locally

```bash
# Generate the document from template (if applicable)
python compile_template.py --template TEMPLATE.md --config config.json --output compiled.md

# Or create directly
cat > task-delegation-GH-42.md <<'EOF'
# Task Delegation: GH-42
...document content...
EOF
```

### 1.3.2 Step 2: Upload to GitHub Issue as Comment Attachment

```bash
# Upload document as attachment to issue comment
gh issue comment {{ISSUE_NUMBER}} --body "$(cat <<'EOF'
## Document: {{DOCUMENT_TYPE}}
Task: {{TASK_ID}}
Timestamp: {{TIMESTAMP}}

**Download attached file:** `{{FILENAME}}`

This document contains: {{BRIEF_DESCRIPTION}}
EOF
)" --attach compiled.md
```

**Template Variables:**
- `{{ISSUE_NUMBER}}` - GitHub issue number for this task/topic
- `{{DOCUMENT_TYPE}}` - Type: TASK_DELEGATION, PROGRESS_REPORT, COMPLETION_REPORT, etc.
- `{{TASK_ID}}` - Unique task identifier (e.g., GH-42)
- `{{TIMESTAMP}}` - ISO 8601 timestamp (e.g., 2026-01-05T15:30:00Z)
- `{{FILENAME}}` - Document filename (e.g., task-delegation-GH-42.md)
- `{{BRIEF_DESCRIPTION}}` - One-line summary of document contents

### 1.3.3 Step 3: Get the Comment URL

```bash
# Retrieve the URL of the just-created comment
COMMENT_URL=$(gh issue view {{ISSUE_NUMBER}} --json comments --jq '.comments[-1].url')
```

### 1.3.4 Step 4: Send AI Maestro Message with URL Only

Send a document delivery notification using the `agent-messaging` skill:
- **Recipient**: `{{RECIPIENT}}` (full agent session name)
- **Subject**: "[DOC] {{DOCUMENT_TYPE}} - {{TASK_ID}}"
- **Content**: JSON with `type` ("document_delivery"), `task_id`, `document_type`, `github_comment_url`, `filename`, `requires_ack` (true)
- **Type**: `notification`
- **Priority**: `high`

**Verify**: confirm message delivery.

**Additional Variables:**
- `{{RECIPIENT}}` - Full agent session name (e.g., libs-svg-svgbbox)
- AI Maestro AMP messaging (handles routing automatically)

---

**Next:** [Part 2: Recipient Process and ACK Requirements](./DOCUMENT_DELIVERY_PROTOCOL-part2-recipient-ack.md)
