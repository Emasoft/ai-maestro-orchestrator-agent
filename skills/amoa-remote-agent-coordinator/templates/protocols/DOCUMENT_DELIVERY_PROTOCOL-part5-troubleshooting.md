# Document Delivery Protocol - Part 5: Troubleshooting and Checklists

**Parent:** [DOCUMENT_DELIVERY_PROTOCOL.md](./DOCUMENT_DELIVERY_PROTOCOL.md)

---

## 5.1 Troubleshooting

### 5.1.1 Issue: Agent Did Not Receive Document

**Symptoms:** No ACK received within 5 minutes.

**Resolution:**
1. Check agent's Claude Code session is running: `tmux ls | grep libs-svg-svgbbox`
2. Check AI Maestro subconscious is running (see official skill: `~/.claude/skills/agent-messaging/SKILL.md`)
3. Verify GitHub comment URL: `gh issue view {{ISSUE_NUMBER}} --json comments`
4. Resend message with same URL
5. Check AI Maestro message logs: `the `agent-messaging` skill to check inbox`

**Note:** AI Maestro's subconscious automatically checks for new messages every 5 minutes and notifies idle agents via tmux send-keys. No manual inbox watcher setup required.

### 5.1.2 Issue: GitHub Attachment Upload Failed

**Symptoms:** `gh issue comment` returns error.

**Resolution:**
1. Verify file exists: `ls -lh {{FILENAME}}`
2. Check file size (<25MB for GitHub): `du -h {{FILENAME}}`
3. Verify GitHub authentication: `gh auth status`
4. Check issue exists: `gh issue view {{ISSUE_NUMBER}}`
5. Try manual upload via GitHub web UI

### 5.1.3 Issue: Recipient Cannot Download Attachment

**Symptoms:** Agent reports "404 Not Found" or "403 Forbidden".

**Resolution:**
1. Verify comment URL is correct
2. Check agent has GitHub auth: `gh auth status` (in agent's tmux session)
3. Verify issue is accessible (not private repo without access)
4. Use alternative download method:
   ```bash
   # Download via API
   gh api repos/{{OWNER}}/{{REPO}}/issues/comments/{{COMMENT_ID}} \
     --jq '.body' | grep -o 'https://.*\.md' | xargs curl -L -o {{FILENAME}}
   ```

### 5.1.4 Issue: ACK Timeout False Positive

**Symptoms:** Orchestrator escalates missing ACK, but agent already sent it.

**Resolution:**
1. Check ACK message format matches protocol
2. Verify `task_id` in ACK matches original message
3. Check AI Maestro message delivery: `the `agent-messaging` skill to check inbox`
4. Review ACK tracking code for race condition
5. Increase ACK timeout if network latency is high

---

## 5.2 Implementation Checklist

### 5.2.1 Sender Checklist

- [ ] Document created locally (`.md` file)
- [ ] GitHub issue exists for this task/topic
- [ ] Document uploaded to GitHub issue comment (`gh issue comment --attach`)
- [ ] Comment URL retrieved (`gh issue view --json comments`)
- [ ] AI Maestro message sent with `type: document_delivery`
- [ ] Message includes `github_comment_url`, `filename`, `task_id`
- [ ] Message marked `requires_ack: true`
- [ ] ACK tracking started with 5-minute expected window

### 5.2.2 Recipient Checklist

- [ ] Received AI Maestro message with `type: document_delivery`
- [ ] Extracted `github_comment_url` from message
- [ ] Downloaded `.md` file from GitHub comment
- [ ] Sent ACK message within 5 minutes
- [ ] ACK includes `task_id`, `filename`, `github_comment_url`
- [ ] Document processing started
- [ ] Progress updates posted to same GitHub issue

### 5.2.3 Orchestrator Checklist

- [ ] Validation function `validate_outgoing_message()` implemented
- [ ] Rejection mechanism for invalid messages implemented
- [ ] ACK tracking dictionary/database initialized
- [ ] ACK timeout checker scheduled (every 1 minute)
- [ ] Escalation function for missing ACKs implemented
- [ ] Audit log for all document deliveries maintained

---

## 5.3 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-05 | Initial protocol definition |

---

## 5.4 Related Protocols

- **DOCUMENT_STORAGE_PROTOCOL.md** - Standardized folder structure for downloaded documents (MANDATORY)
- **TASK_DELEGATION_PROTOCOL.md** - How to structure task delegation documents
- **PROGRESS_REPORTING_PROTOCOL.md** - How to format progress reports
- **GITHUB_INTEGRATION_PROTOCOL.md** - GitHub issue management guidelines

---

## 5.5 Storage Protocol Integration

All document deliveries MUST follow both this protocol AND `DOCUMENT_STORAGE_PROTOCOL.md`:

1. **This Protocol** - Defines HOW documents are shared (GitHub URLs, ACK responses)
2. **Storage Protocol** - Defines WHERE documents are stored (design/received/ structure)

The storage protocol ensures:
- Permanent, immutable record of all received instructions
- Standardized folder paths agents can rely on
- Read-only enforcement prevents tampering
- SHA256 integrity verification for audit trails

---

## 5.6 Enforcement

This protocol is MANDATORY for all agents and orchestrators. Violations will result in:

1. **Warning:** First violation - log warning, notify agent
2. **Block:** Second violation - block message, require protocol compliance
3. **Escalation:** Third violation - escalate to user, review agent configuration

---

**Previous:** [Part 4: Message Examples and Document Types](./DOCUMENT_DELIVERY_PROTOCOL-part4-examples-types.md)

**END OF DOCUMENT DELIVERY PROTOCOL**
