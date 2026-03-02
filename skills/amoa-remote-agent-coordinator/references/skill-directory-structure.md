# Remote Agent Coordinator - Directory Structure

## Table of Contents

- 1.0 Top-Level Structure
- 2.0 References Directory
- 3.0 Scripts Directory
- 4.0 Templates Directory

---

## 1.0 Top-Level Structure

```
eoa-remote-agent-coordinator/
+-- SKILL.md                              # Main skill file (map/index)
+-- references/                           # Reference documentation
+-- scripts/                              # Python utility scripts
+-- templates/                            # Message and protocol templates
```

---

## 2.0 References Directory

| File | Purpose |
|------|---------|
| `agent-onboarding.md` | New agent onboarding guide |
| `agent-registration.md` | Agent roster management |
| `agent-response-templates.md` | Template usage in delegations |
| `artifact-sharing-protocol.md` | Build artifact sharing |
| `bug-reporting-protocol.md` | Bug report handling |
| `central-configuration.md` | Central source of truth |
| `change-notification-protocol.md` | Change notification system |
| `document-storage-protocol.md` | Document storage protocol |
| `echo-acknowledgment-protocol.md` | ACK protocol |
| `error-handling-protocol.md` | FAIL-FAST and error reports |
| `escalation-procedures.md` | Escalation rules |
| `examples-remote-coordination.md` | Usage examples |
| `lsp-enforcement-checklist.md` | Pre-assignment LSP check |
| `lsp-installation-guide.md` | Per-language LSP install |
| `lsp-plugin-template.md` | Custom LSP plugin templates |
| `lsp-servers-overview.md` | LSP plugins overview |
| `messaging-protocol.md` | AI Maestro protocol details |
| `orchestrator-lsp-management.md` | Orchestrator LSP guide |
| `overnight-operation.md` | Overnight autonomous guide |
| `progress-monitoring-protocol.md` | Proactive monitoring |
| `rule-14-immutable-requirements.md` | User requirements rule |
| `rule-15-no-implementation.md` | No orchestrator coding rule |
| `skill-authoring-best-practices.md` | Skill writing guidance |
| `skill-directory-structure.md` | This file |
| `skill-format-comparison.md` | Open Spec vs Claude Code |
| `task-instruction-format.md` | Complete instruction template |
| `toolchain-template-system.md` | Template system guide |
| `toolchain-setup.md` | Toolchain configuration |
| `verification-loops-protocol.md` | 4-loop PR verification |

---

## 3.0 Scripts Directory

| Script | Purpose |
|--------|---------|
| `install_lsp.py` | LSP installation automation |
| `validate_skill.py` | Skill validation |
| `eoa_orchestrator_init.py` | Initialize storage directories |
| `eoa_register_agent.py` | Register agents in roster |
| `eoa_orchestrator_download.py` | Download documents from agents |
| `eoa_search.py` | Cross-agent document search |
| `eoa_download.py` | Basic document download |

---

## 4.0 Templates Directory

```
templates/
+-- protocols/
    +-- DOCUMENT_DELIVERY_PROTOCOL.md
    +-- DOCUMENT_STORAGE_PROTOCOL.md
```

Template files provide standardized formats for:
- Document delivery between agents
- Document storage and retrieval operations
