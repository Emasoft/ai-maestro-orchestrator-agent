#!/usr/bin/env bash
# sync_cpv_validators.sh — Fetch latest validation scripts from CPV repo
#
# Downloads the 20 validation-chain files from Emasoft/claude-plugins-validation
# into this plugin's scripts/ directory. Requires gh CLI and network access.
# Fail-safe: exits 0 even on errors so it never blocks a push.

set -uo pipefail

REPO="Emasoft/claude-plugins-validation"
REF="master"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# The 20 files that form the validation chain
FILES=(
  cpv_validation_common.py
  gitignore_filter.py
  smart_exec.py
  validate_plugin.py
  validate_agent.py
  validate_command.py
  validate_documentation.py
  validate_encoding.py
  validate_enterprise.py
  validate_hook.py
  validate_lsp.py
  validate_marketplace_pipeline.py
  validate_marketplace.py
  validate_mcp.py
  validate_rules.py
  validate_scoring.py
  validate_security.py
  validate_skill_comprehensive.py
  validate_skill.py
  validate_xref.py
)

# Check prerequisites
if ! command -v gh &> /dev/null; then
  echo "Warning: gh CLI not found. Skipping CPV sync."
  exit 0
fi

SYNCED=0
FAILED=0

for file in "${FILES[@]}"; do
  # Fetch file content via GitHub API (base64 encoded)
  CONTENT=$(gh api "repos/${REPO}/contents/scripts/${file}?ref=${REF}" --jq '.content' 2>/dev/null)
  if [ -z "$CONTENT" ] || [ "$CONTENT" = "null" ]; then
    echo "Warning: Could not fetch ${file}"
    FAILED=$((FAILED + 1))
    continue
  fi

  # Decode base64 and write to scripts/
  # GitHub API returns base64 with embedded newlines; strip them before decoding
  # macOS base64 uses -D, GNU base64 uses -d
  DECODED=$(echo "$CONTENT" | tr -d '\n' | base64 -D 2>/dev/null || echo "$CONTENT" | tr -d '\n' | base64 -d 2>/dev/null)
  if [ -z "$DECODED" ]; then
    echo "Warning: Failed to decode ${file}"
    FAILED=$((FAILED + 1))
    continue
  fi
  echo "$DECODED" > "${SCRIPT_DIR}/${file}"
  chmod +x "${SCRIPT_DIR}/${file}"
  SYNCED=$((SYNCED + 1))
done

echo "CPV sync complete: ${SYNCED} synced, ${FAILED} failed (of ${#FILES[@]} total)"

# Clean up old validation_common.py if cpv_validation_common.py exists
if [ -f "${SCRIPT_DIR}/cpv_validation_common.py" ] && [ -f "${SCRIPT_DIR}/validation_common.py" ]; then
  rm -f "${SCRIPT_DIR}/validation_common.py"
  echo "Removed old validation_common.py (replaced by cpv_validation_common.py)"
fi

exit 0
