# Emergency Procedures

## Table of Contents

- [Replacement Agent Also Fails](#replacement-agent-also-fails)
- [Handoff Document Corrupted](#handoff-document-corrupted)
- [GitHub Project Access Issues](#github-project-access-issues)

## Use-Case TOC

- When the replacement agent fails → [Replacement Agent Also Fails](#replacement-agent-also-fails)
- When handoff cannot be generated → [Handoff Document Corrupted](#handoff-document-corrupted)
- When kanban reassignment fails → [GitHub Project Access Issues](#github-project-access-issues)

---

## Replacement Agent Also Fails

If the replacement agent fails during handoff:

1. **ALERT** user immediately
2. **PRESERVE** all handoff documents
3. **DO NOT** attempt automatic re-replacement
4. **WAIT** for user guidance

---

## Handoff Document Corrupted

If handoff cannot be generated:

1. **Document** what information is available
2. **Create partial handoff** with known data
3. **Flag gaps** clearly for new agent
4. **Request new agent report** missing context immediately

---

## GitHub Project Access Issues

If kanban reassignment fails:

1. **Document** reassignment intent
2. **Manual fallback**: Instruct new agent to self-assign
3. **Log issue** for later resolution
4. **Continue** with handoff delivery
