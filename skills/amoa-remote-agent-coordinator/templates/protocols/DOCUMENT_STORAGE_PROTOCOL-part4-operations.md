# Document Storage Protocol - Part 4: Operations

**Parent Document**: [DOCUMENT_STORAGE_PROTOCOL.md](./DOCUMENT_STORAGE_PROTOCOL.md)
**Version**: 2.0.0

---

## Read-Only Enforcement

### Immediate Lock After Download

After downloading a file, immediately set read-only permissions:

```bash
# Unix/macOS
chmod 444 "$FILE_PATH"
chmod 555 "$FOLDER_PATH"

# Verify
ls -la "$FILE_PATH"  # Should show -r--r--r--
```

### Directory Protection

```bash
# Lock entire task folder
chmod -R a-w design/agents/helper-agent-macos-arm64/received/reports/GH-42/

# Verify no write access
touch design/agents/helper-agent-macos-arm64/received/reports/GH-42/test.txt  # Should fail
```

### Integrity Verification

```bash
# Verify file hasn't been tampered with
STORED_HASH=$(jq -r '.download.sha256' metadata.json)
CURRENT_HASH=$(sha256sum completion.md | cut -d' ' -f1)

if [ "$STORED_HASH" != "$CURRENT_HASH" ]; then
  echo "ERROR: File integrity violation detected!"
  exit 1
fi
```

---

## Environment Variables

### Remote Agent Variables

```bash
# Set in remote agent environment
export ATLAS_ROLE="remote"
export ATLAS_AGENT_NAME="helper-agent-macos-arm64"
export EOA_STORAGE_ROOT="${PROJECT_ROOT}/design/received"
export ATLAS_TASKS_DIR="${EOA_STORAGE_ROOT}/tasks"
export ATLAS_SPECS_DIR="${EOA_STORAGE_ROOT}/specs"
export ATLAS_PLANS_DIR="${EOA_STORAGE_ROOT}/plans"
export ATLAS_SYNC_DIR="${EOA_STORAGE_ROOT}/sync"
```

### Orchestrator Variables

```bash
# Set in orchestrator environment
export ATLAS_ROLE="orchestrator"
export ATLAS_AGENT_NAME="orchestrator"
export EOA_STORAGE_ROOT="${PROJECT_ROOT}/design"
export ATLAS_AGENTS_DIR="${EOA_STORAGE_ROOT}/agents"
export ATLAS_SENT_DIR="${EOA_STORAGE_ROOT}/sent"
export ATLAS_INDEX_DIR="${EOA_STORAGE_ROOT}/index"
```

---

## Orchestrator Lookup Commands

### Find Documents by Agent

```bash
# List all documents from a specific agent
ls -laR "$ATLAS_AGENTS_DIR/helper-agent-macos-arm64/received/"

# Get all completion reports from an agent
find "$ATLAS_AGENTS_DIR/helper-agent-macos-arm64" -name "*completion.md"

# Count documents per agent
for agent in "$ATLAS_AGENTS_DIR"/*/; do
  echo "$(basename $agent): $(find "$agent" -name "*.md" | wc -l) documents"
done
```

### Find Documents by Task

```bash
# Find all documents related to a task across ALL agents
find "$ATLAS_AGENTS_DIR" -type d -name "GH-42"

# Use index for faster lookup
cat "$ATLAS_INDEX_DIR/by-task/GH-42.json" | jq '.documents[].path'
```

### Find Blockers Across All Agents

```bash
# Critical: Find all blocker reports
find "$ATLAS_AGENTS_DIR" -path "*/blockers/*" -name "*.md"

# Or use category index
cat "$ATLAS_INDEX_DIR/by-category/blockers.json" | jq '.[]'
```

---

## Gitignore Configuration

Add to project `.gitignore`:

```gitignore
# EOA Document Storage (local cache, not committed)
design/

# Exception: Keep folder structure template
!design/.gitkeep
```

**CRITICAL**: The `design/` directory is NEVER committed to git. Each agent maintains its own local storage.

---

**Previous**: [Part 3 - Document Categories & Metadata](./DOCUMENT_STORAGE_PROTOCOL-part3-categories-metadata.md)
**Next**: [Part 5 - Retention, Scripts & Integration](./DOCUMENT_STORAGE_PROTOCOL-part5-retention-scripts-integration.md)
