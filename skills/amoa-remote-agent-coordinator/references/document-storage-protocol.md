# Document Storage Protocol v2.0


## Contents

- [Table of Contents](#table-of-contents)
- [1.0 Overview](#10-overview)
- [2.0 Storage Architecture](#20-storage-architecture)
  - [2.1 Directory Structure](#21-directory-structure)
- [3.0 Document Delivery Rules](#30-document-delivery-rules)
  - [3.1 Mandatory Rules for All Document Delivery](#31-mandatory-rules-for-all-document-delivery)
  - [3.2 GitHub Issue Comment URL Sharing](#32-github-issue-comment-url-sharing)
  - [3.3 Integrity Verification with SHA256](#33-integrity-verification-with-sha256)
- [4.0 Orchestrator Scripts](#40-orchestrator-scripts)
  - [4.1 Available Scripts and Their Purposes](#41-available-scripts-and-their-purposes)
  - [4.2 Usage Examples](#42-usage-examples)
- [5.0 Remote Agent Storage Skill](#50-remote-agent-storage-skill)
  - [5.1 What the Skill Provides](#51-what-the-skill-provides)
  - [5.2 Installation on Remote Agent](#52-installation-on-remote-agent)

---

## Table of Contents

- 1.0 Overview
- 1.1 When to use this protocol
- 1.2 Why documents are never embedded in messages
- 2.0 Storage Architecture
- 2.1 Directory structure
- 2.2 Per-agent tracking
- 2.3 Index directories
- 3.0 Document Delivery Rules
- 3.1 Mandatory rules for all document delivery
- 3.2 GitHub issue comment URL sharing
- 3.3 Integrity verification with SHA256
- 4.0 Orchestrator Scripts
- 4.1 Available scripts and their purposes
- 4.2 Usage examples
- 5.0 Remote Agent Storage Skill
- 5.1 What the skill provides
- 5.2 Installation on remote agents

---

## 1.0 Overview

The orchestrator tracks ALL documents sent to and received from agents using a standardized local storage system. Documents are NEVER embedded in AI Maestro messages - only GitHub issue comment URLs are shared.

---

## 2.0 Storage Architecture

### 2.1 Directory Structure

```
design/
+-- agents/                          # Per-agent tracking (orchestrator only)
|   +-- {agent-full-name}/           # e.g., helper-agent-macos-arm64
|   |   +-- agent.json               # Agent metadata
|   |   +-- received/                # Documents FROM this agent
|   |       +-- reports/             # Completion, verification, status
|   |       +-- acks/                # Acknowledgments
|   |       +-- sync/                # Sync reports
+-- sent/                            # Documents SENT TO agents
|   +-- {agent-full-name}/
|   |   +-- tasks/{task_id}/
+-- index/                           # Cross-agent search indexes
    +-- by-task/
    +-- by-agent/
    +-- by-date/
    +-- by-category/
```

---

## 3.0 Document Delivery Rules

### 3.1 Mandatory Rules for All Document Delivery

1. **NEVER** embed .md content directly in AI Maestro messages
2. **ALWAYS** upload to GitHub issue comment as attachment
3. **ALWAYS** share URL only in messages
4. **ALWAYS** require ACK with SHA256 hash for `document_delivery` type
5. **ALWAYS** lock files read-only after download

### 3.2 GitHub Issue Comment URL Sharing

Documents are shared by:
1. Uploading document as attachment to GitHub issue comment
2. Copying the attachment URL
3. Sending only the URL in the AI Maestro message

### 3.3 Integrity Verification with SHA256

When receiving documents, verify integrity:
1. Calculate SHA256 hash of downloaded file
2. Include hash in ACK message
3. Orchestrator verifies hash matches original

---

## 4.0 Orchestrator Scripts

### 4.1 Available Scripts and Their Purposes

| Script | Purpose |
|--------|---------|
| `scripts/eoa_orchestrator_init.py <!-- TODO: Rename to eoa_orchestrator_init.py -->` | Initialize orchestrator storage structure |
| `scripts/eoa_register_agent.py <!-- TODO: Rename to eoa_register_agent.py -->` | Register new agents, list registered agents |
| `scripts/eoa_orchestrator_download.py <!-- TODO: Rename to eoa_orchestrator_download.py -->` | Download documents from agents to per-agent folders |
| `scripts/eoa_search.py <!-- TODO: Rename to eoa_search.py -->` | Search across all agents by task, agent, date, category |

### 4.2 Usage Examples

```bash
# Initialize orchestrator storage
python scripts/eoa_orchestrator_init.py <!-- TODO: Rename to eoa_orchestrator_init.py --> --project-root .

# Register a new agent
python scripts/eoa_register_agent.py <!-- TODO: Rename to eoa_register_agent.py --> register \
  --name helper-agent-macos-arm64 \
  --platform macos \
  --architecture arm64

# Download document from agent
python scripts/eoa_orchestrator_download.py <!-- TODO: Rename to eoa_orchestrator_download.py --> download \
  --url "https://github.com/.../issues/42#issuecomment-123456" \
  --agent helper-agent-macos-arm64 \
  --task-id GH-42 \
  --category reports

# Search for blockers across all agents
python scripts/eoa_search.py <!-- TODO: Rename to eoa_search.py --> blockers

# Find all documents for a task
python scripts/eoa_search.py <!-- TODO: Rename to eoa_search.py --> by-task GH-42
```

---

## 5.0 Remote Agent Storage Skill

### 5.1 What the Skill Provides

Remote agents should install the `eoa-agent-storage` skill for managing their local document storage. This skill provides:

- Download script for receiving documents from orchestrator
- Read-only enforcement
- Integrity verification via SHA256
- ACK template for confirmations

### 5.2 Installation on Remote Agent

```bash
cp -r eoa-agent-storage ~/.claude/skills/
```

See `templates/protocols/DOCUMENT_STORAGE_PROTOCOL.md` for complete protocol specification.
