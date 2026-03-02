# Artifact Sharing Protocol

## Contents

- [When you need to understand artifact categories](#artifact-types) - Know what types of files can be shared
- [When you need to choose a sharing method](#sharing-methods) - Select the right method for your artifact size/type
- [When you need to document what was shared](#artifact-manifest) - Create manifest of shared artifacts
- [When you need to request artifacts from agents](#artifact-request) - How to ask agents for specific artifacts
- [When you need to clean up old artifacts](#cleanup-policy) - Manage retention and cleanup
- [When you need to secure artifact sharing](#security) - Protect credentials and verify integrity
- [When sharing times out](#timeout-handling) - Handle unresponsive agents
- [When sharing fails](#error-states) - Recover from errors and failures
- [When you need to integrate with other protocols](#integration) - Reference other related specifications

## Purpose

Define how build artifacts, test results, logs, and other generated files are shared between orchestrator and remote agents.

## Artifact Types

| Type | Extension | Storage Location |
|------|-----------|------------------|
| Build outputs | `.zip`, `.tar.gz` | `artifacts/builds/` |
| Test results | `.json`, `.xml` | `artifacts/tests/` |
| Logs | `.log`, `.txt` | `artifacts/logs/` |
| Coverage reports | `.html`, `.json` | `artifacts/coverage/` |
| Screenshots | `.png`, `.jpg` | `artifacts/screenshots/` |

## Sharing Methods

### Method 1: Git Repository (Preferred)

For projects with Git:

```bash
# Agent commits artifacts to feature branch
git add artifacts/
git commit -m "Add test results for GH-42"
git push origin feature/GH-42-auth
```

Orchestrator retrieves:
```bash
git fetch origin feature/GH-42-auth
git checkout origin/feature/GH-42-auth -- artifacts/
```

### Method 2: GitHub Actions Artifacts

For CI/CD integration:

```yaml
- name: Upload test results
  uses: actions/upload-artifact@v4
  with:
    name: test-results-${{ github.run_id }}
    path: artifacts/tests/
    retention-days: 7
```

### Method 3: Direct Message (Small Artifacts Only)

For artifacts < 100KB:

```json
{
  "type": "artifact-share",
  "task_id": "GH-42",
  "artifact": {
    "name": "test-summary.json",
    "type": "test-results",
    "encoding": "base64",
    "content": "eyJ0ZXN0cyI6IDQ1LCAicGFzc2VkIjogNDIsICJmYWlsZWQiOiAzfQ=="
  }
}
```

## Artifact Manifest

Every artifact share includes manifest:

```json
{
  "manifest_version": "1.0",
  "task_id": "GH-42",
  "agent_id": "dev-agent-1",
  "created_at": "2025-12-31T03:00:00Z",
  "artifacts": [
    {
      "name": "test-results.json",
      "type": "test-results",
      "size_bytes": 2048,
      "checksum": "sha256:abc123...",
      "location": "artifacts/tests/test-results.json"
    }
  ]
}
```

## Artifact Request

Orchestrator requests specific artifacts:

```json
{
  "type": "artifact-request",
  "task_id": "GH-42",
  "requested": ["test-results", "coverage-report"],
  "format": "git-commit"
}
```

Agent responds:

```json
{
  "type": "artifact-response",
  "task_id": "GH-42",
  "commit": "abc123def",
  "branch": "feature/GH-42-auth",
  "manifest": { ... }
}
```

## Cleanup Policy

- Build artifacts: Delete after PR merge
- Test results: Keep for 30 days
- Logs: Keep for 7 days
- Coverage: Keep latest only per branch

## Security

- NEVER share credentials or secrets as artifacts
- Sanitize logs before sharing (remove tokens, passwords)
- Use checksums to verify integrity
- Artifacts are project-internal only

## Timeout Handling

If agent doesn't respond to artifact-request within timeout:

| Artifact Size | Timeout | Action if No Response |
|--------------|---------|----------------------|
| Small (<10MB) | 5 min | Retry once, then mark unavailable |
| Medium (10-50MB) | 10 min | Retry once, then escalate |
| Large (>50MB) | 15 min | Retry once, then escalate |

### Timeout Flow

1. Send artifact-request
2. Wait for response within timeout
3. IF no response:
   - Send retry request with `retry: true` flag
   - Wait for 50% of original timeout
4. IF still no response:
   - Mark artifact as unavailable
   - Log non-responsive agent
   - Escalate to orchestrator
   - Consider regenerating artifact locally

## Error States

| State | Meaning | Action |
|-------|---------|--------|
| `artifact-not-found` | Artifact doesn't exist | Request regeneration |
| `checksum-mismatch` | Integrity check failed | Re-request artifact |
| `storage-full` | Cannot commit/upload | Clean old artifacts, retry |
| `git-conflict` | Merge conflict on commit | Manual resolution required |
| `size-exceeded` | Artifact > 100MB | Use GitHub Actions method |
| `permission-denied` | Cannot access artifact | Check permissions, escalate |

### Error Response Format

```json
{
  "type": "artifact-response",
  "request_id": "req-456",
  "status": "error",
  "error": {
    "code": "artifact-not-found",
    "message": "Artifact 'build/output.zip' not found in commit abc123",
    "suggestion": "Regenerate artifact with 'make build'"
  }
}
```

## Integration

This protocol integrates with:

- `echo-acknowledgment-protocol.md` - Use acknowledgment pattern for artifact requests
- `task-instruction-format.md` - Artifact paths referenced in task files
- `test-report-format.md` - Test results are shared as artifacts
- `messaging-protocol.md` - Artifact messages use standard message envelope
- `change-notification-protocol.md` - Config changes may affect artifact locations

---

## Troubleshooting

### Problem: Artifact Checksum Mismatch

**Symptoms**: Received artifact fails integrity verification.

**Solution**:
1. Re-request artifact with fresh transfer
2. If using git, verify commit hash matches manifest
3. Check for network issues causing corruption
4. If persistent, ask agent to regenerate artifact
5. Verify agent's local artifact matches their reported checksum

### Problem: Artifact Too Large for Message

**Symptoms**: AI Maestro rejects message with artifact content.

**Solution**:
1. Switch from direct message (Method 3) to git commit (Method 1)
2. If git not available, use GitHub Actions upload (Method 2)
3. Compress artifact before sharing
4. Split large artifacts into smaller chunks
5. Share artifact path/URL instead of content

### Problem: Git Conflict When Pushing Artifacts

**Symptoms**: Agent cannot push artifact commit due to conflicts.

**Solution**:
1. Have agent fetch latest changes first
2. Rebase artifact commit on updated branch
3. If conflict in artifact files, regenerate after merge
4. Use dedicated artifacts branch to avoid main branch conflicts
5. Consider using GitHub Actions upload to avoid git conflicts entirely

### Problem: Agent Cannot Find Requested Artifact

**Symptoms**: Agent reports `artifact-not-found` error.

**Solution**:
1. Verify artifact path in request matches where agent generates it
2. Check if artifact was generated (may be a build step issue)
3. Confirm artifact retention policy hasn't deleted it
4. Request agent to regenerate artifact
5. Update task instructions if artifact path is wrong

### Problem: Storage Quota Exceeded

**Symptoms**: Cannot upload/commit artifacts due to space limits.

**Solution**:
1. Run cleanup of old artifacts immediately
2. Check retention policy - may need to be more aggressive
3. Compress artifacts before storage
4. Use external storage (S3, GCS) for large artifacts
5. Prioritize which artifacts are critical to keep

### Problem: Sensitive Data in Artifacts

**Symptoms**: Credentials/tokens found in committed artifacts.

**Solution**:
1. IMMEDIATELY revoke exposed credentials
2. Remove artifact commit with sensitive data
3. Add sanitization step to artifact generation
4. Update `.gitignore` to prevent future leaks
5. Review artifact generation process for other potential leaks

### Problem: Agent Responds But Artifact Missing

**Symptoms**: Agent sends artifact-response with commit hash, but artifact not in commit.

**Solution**:
1. Verify agent committed to correct branch
2. Check if artifact was staged before commit
3. Verify artifact path in manifest matches actual location
4. Have agent re-add and re-commit artifacts
5. If pattern repeats, review agent's git workflow
