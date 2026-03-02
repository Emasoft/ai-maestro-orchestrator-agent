# Document Delivery Protocol - Part 2: Recipient Process and ACK Requirements

**Parent:** [DOCUMENT_DELIVERY_PROTOCOL.md](./DOCUMENT_DELIVERY_PROTOCOL.md)

---

## 2.1 Delivery Process - Recipient

The recipient follows this five-step process:

### 2.1.1 Step 1: Receive AI Maestro Message

The recipient's inbox watcher detects a message with `type: document_delivery`.

### 2.1.2 Step 2: Download .md File from GitHub

```bash
# Extract comment URL from message
COMMENT_URL=$(echo "$MESSAGE_CONTENT" | jq -r '.github_comment_url')

# Download the attachment from GitHub comment
gh api "$COMMENT_URL" --jq '.body' > temp_comment.txt

# Extract attachment URL and download
# (GitHub CLI handles authentication automatically)
gh issue view {{ISSUE_NUMBER}} --json comments --jq '.comments[] | select(.url == "'$COMMENT_URL'") | .attachments[0].url' | xargs curl -L -o {{FILENAME}}
```

**Alternative (if direct download link):**
```bash
curl -L -H "Authorization: token $GITHUB_TOKEN" \
  "{{ATTACHMENT_URL}}" \
  -o {{FILENAME}}
```

### 2.1.3 Step 3: Send ACK (MANDATORY)

Send an acknowledgment using the `agent-messaging` skill:
- **Recipient**: `{{SENDER}}` (the sender's session name)
- **Subject**: "[ACK] {{TASK_ID}} - RECEIVED"
- **Content**: JSON with `type` ("acknowledgment"), `task_id`, `message` ("[ACK] {{TASK_ID}} - RECEIVED - Document: {{FILENAME}} downloaded from {{GITHUB_COMMENT_URL}}")
- **Type**: `response`
- **Priority**: `normal`

**Verify**: confirm acknowledgment delivery.

### 2.1.4 Step 4: Store in EOA Design Storage (MANDATORY)

Downloaded documents MUST be stored in the standardized EOA Document Storage folder structure.
See **DOCUMENT_STORAGE_PROTOCOL.md** for complete details.

```bash
# Initialize storage (if not already done)
python scripts/eoa_download.py <!-- TODO: Rename to eoa_download.py --> init --project-root .

# Download and store with proper categorization
python scripts/eoa_download.py <!-- TODO: Rename to eoa_download.py --> download \
  --url "$COMMENT_URL" \
  --task-id {{TASK_ID}} \
  --category tasks \
  --doc-type delegation \
  --sender orchestrator

# Document is now stored at:
# design/received/tasks/{{TASK_ID}}/YYYYMMDD_HHMMSS_delegation.md
# Automatically set to READ-ONLY with SHA256 verification
```

**Storage Categories:**

| Category | Path | Contents |
|----------|------|----------|
| `tasks` | `design/received/tasks/{task_id}/` | Task delegations, checklists |
| `reports` | `design/received/reports/{task_id}/` | Completion, verification, blockers |
| `acks` | `design/received/acks/{task_id}/` | ACK confirmations |
| `specs` | `design/received/specs/` | Toolchain, platform configs |
| `plans` | `design/received/plans/{task_id}/` | Design docs, reviews |
| `sync` | `design/received/sync/` | Cross-agent sync reports |

**Read-Only Enforcement:**
- All downloaded files are immediately set to `chmod 444`
- Directories set to `chmod 555`
- SHA256 hash stored in metadata.json for integrity verification
- Files cannot be modified after download - serves as permanent record

### 2.1.5 Step 5: Process the Document

```bash
# Read from storage (read-only access)
TASK_DIR="design/received/tasks/{{TASK_ID}}"
cat "$TASK_DIR"/*.md

# Execute instructions, run tasks, etc.
# ...
```

---

## 2.2 ACK Requirements

### 2.2.1 When ACK is MANDATORY

Messages with `type: document_delivery` ALWAYS require ACK within 5 minutes.

**ACK Message Format:**
```
[ACK] {{TASK_ID}} - RECEIVED
Document: {{FILENAME}} downloaded from {{GITHUB_COMMENT_URL}}
Status: Processing started
```

### 2.2.2 When ACK is NOT Required

Messages without `document_delivery` type (normal conversation, status updates, questions) do NOT require ACK.

**Examples of ACK-free messages:**
- `type: status_update`
- `type: question`
- `type: notification`
- `type: progress_report` (if not document delivery)

---

**Previous:** [Part 1: Core Rules and Sender Process](./DOCUMENT_DELIVERY_PROTOCOL-part1-rules-sender.md)

**Next:** [Part 3: Orchestrator Enforcement](./DOCUMENT_DELIVERY_PROTOCOL-part3-orchestrator.md)
