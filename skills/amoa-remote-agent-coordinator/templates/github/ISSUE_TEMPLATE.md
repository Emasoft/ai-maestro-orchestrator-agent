# GitHub Issue Template with Toolchain Awareness

## Issue Title Format

```
[{{TASK_ID}}] {{TITLE}}
```

Example: `[EOA-001] Implement remote Docker agent deployment`

## Issue Body Template

```markdown
## Task Overview

**Task ID:** {{TASK_ID}}
**Component:** {{COMPONENT}}
**Priority:** {{PRIORITY}}
**Complexity:** {{COMPLEXITY_TIER}}

## Description

{{DESCRIPTION}}

## Toolchain Specification

**Platform:** {{PLATFORM}}
**Toolchain Template:** [Link to toolchain template]({{TOOLCHAIN_TEMPLATE_PATH}})

### Required Tools
- {{TOOL_1}}
- {{TOOL_2}}
- {{TOOL_3}}

### Environment Requirements
```yaml
platform: {{PLATFORM}}
python_version: {{PYTHON_VERSION}}
node_version: {{NODE_VERSION}}
system_dependencies:
  - {{DEPENDENCY_1}}
  - {{DEPENDENCY_2}}
```

## Acceptance Criteria

- [ ] {{CRITERION_1}}
- [ ] {{CRITERION_2}}
- [ ] {{CRITERION_3}}
- [ ] All tests pass locally
- [ ] All tests pass in CI
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] Toolchain verified on target platform

## Linked Resources

- **Toolchain Template:** `{{TOOLCHAIN_TEMPLATE_PATH}}`
- **Related Issues:** #{{ISSUE_NUMBER}}
- **Parent Epic:** #{{EPIC_NUMBER}}
- **Documentation:** [Link]({{DOC_URL}})

## Agent Assignment

**Assigned Agent:** {{AGENT_NAME}}
**Agent Platform:** {{AGENT_PLATFORM}}
**Agent Session:** {{AGENT_SESSION_ID}}

## Implementation Notes

{{IMPLEMENTATION_NOTES}}

## Testing Requirements

### Unit Tests
- [ ] {{TEST_REQUIREMENT_1}}
- [ ] {{TEST_REQUIREMENT_2}}

### Integration Tests
- [ ] {{INTEGRATION_TEST_1}}
- [ ] {{INTEGRATION_TEST_2}}

### Platform-Specific Tests
- [ ] Verify on {{PLATFORM}}
- [ ] Check toolchain compatibility
- [ ] Validate environment setup

## Labels to Apply

Apply these labels when creating the issue:

```bash
gh issue create \
  --title "[{{TASK_ID}}] {{TITLE}}" \
  --body "$(cat issue-body.md)" \
  --label "status:backlog" \
  --label "priority:{{PRIORITY}}" \
  --label "platform:{{PLATFORM}}" \
  --label "type:{{TYPE}}" \
  --label "toolchain:{{TOOLCHAIN}}" \
  --label "agent:{{AGENT_TYPE}}" \
  --assignee "{{ASSIGNEE}}" \
  --project "{{PROJECT_NUMBER}}"
```

## Pre-Creation Checklist

Before creating this issue, verify:

- [ ] Task ID is unique
- [ ] Toolchain template exists at specified path
- [ ] All required tools are available on target platform
- [ ] Platform is one of: macos, linux, docker, cloud, windows
- [ ] Priority is one of: critical, high, medium, low
- [ ] Type is one of: feature, bugfix, refactor, test, docs, chore
- [ ] Acceptance criteria are specific and measurable
- [ ] Complexity tier is appropriate
- [ ] Component name matches project structure

## Example Issues

### Example 1: Feature Implementation

```markdown
## Task Overview

**Task ID:** EOA-042
**Component:** remote-agent-coordinator
**Priority:** high
**Complexity:** Medium

## Description

Implement SSH key management for remote agent authentication. The orchestrator needs to securely distribute SSH keys to remote agents and verify their identity during connection.

## Toolchain Specification

**Platform:** linux
**Toolchain Template:** [templates/toolchains/linux-ssh-agent.md](../toolchains/linux-ssh-agent.md)

### Required Tools
- openssh-client >= 8.0
- python3.12
- uv
- ssh-keygen

### Environment Requirements
```yaml
platform: linux
python_version: "3.12"
system_dependencies:
  - openssh-client
  - openssh-server
  - python3.12-dev
```

## Acceptance Criteria

- [ ] SSH key pair generated securely
- [ ] Public key deployed to remote agent
- [ ] Private key stored encrypted locally
- [ ] Connection authenticated via SSH key
- [ ] Failed authentication logged and alerted
- [ ] All tests pass locally
- [ ] All tests pass in CI
- [ ] Code reviewed and approved
- [ ] Documentation updated

## Linked Resources

- **Toolchain Template:** `templates/toolchains/linux-ssh-agent.md`
- **Related Issues:** #38 (Remote agent security)
- **Parent Epic:** #35 (Remote agent deployment)
- **Documentation:** `[SSH Authentication Guide]\(docs/ssh-auth.md\)`

## Agent Assignment

**Assigned Agent:** remote-linux-01
**Agent Platform:** linux
**Agent Session:** session_20260105_153045

## Implementation Notes

Use paramiko or fabric for SSH operations. Store keys in `~/design/keys/` with 0600 permissions. Implement key rotation mechanism.

## Testing Requirements

### Unit Tests
- [ ] Test key generation with different algorithms (RSA, Ed25519)
- [ ] Test key validation and format checking
- [ ] Test encryption/decryption of private keys

### Integration Tests
- [ ] Test full SSH connection with generated keys
- [ ] Test authentication failure handling
- [ ] Test key rotation without connection interruption

### Platform-Specific Tests
- [ ] Verify on Ubuntu 22.04
- [ ] Verify on Debian 12
- [ ] Check toolchain compatibility with different SSH versions
- [ ] Validate environment setup script
```

### Example 2: Bug Fix

```markdown
## Task Overview

**Task ID:** EOA-087
**Component:** task-router
**Priority:** critical
**Complexity:** Simple

## Description

Task routing fails when agent platform is specified as "docker" but the container is running on macOS host. The router incorrectly identifies platform as "macos" instead of "docker".

## Toolchain Specification

**Platform:** macos
**Toolchain Template:** [templates/toolchains/macos-docker-debug.md](../toolchains/macos-docker-debug.md)

### Required Tools
- docker desktop >= 4.25
- python3.12
- uv
- docker-py

### Environment Requirements
```yaml
platform: macos
python_version: "3.12"
system_dependencies:
  - docker-desktop
```

## Acceptance Criteria

- [ ] Router correctly identifies "docker" platform
- [ ] Router does not confuse host OS with container OS
- [ ] Existing tests still pass
- [ ] New test added for docker-on-macos scenario
- [ ] Bug does not regress with other platform combinations
- [ ] All tests pass locally
- [ ] All tests pass in CI
- [ ] Code reviewed and approved

## Linked Resources

- **Toolchain Template:** `templates/toolchains/macos-docker-debug.md`
- **Bug Report:** #85
- **Related Issues:** #72 (Platform detection refactor)

## Agent Assignment

**Assigned Agent:** local-orchestrator
**Agent Platform:** macos
**Agent Session:** session_20260105_140000

## Implementation Notes

Check if `EOA_PLATFORM_OVERRIDE` environment variable is set before detecting platform from host OS. Docker containers should explicitly set this variable in their startup script.

## Testing Requirements

### Unit Tests
- [ ] Test platform detection with override variable
- [ ] Test platform detection without override (host OS)
- [ ] Test invalid override values are rejected

### Integration Tests
- [ ] Test routing to docker container on macos host
- [ ] Test routing to docker container on linux host
- [ ] Test routing to native macos agent

### Platform-Specific Tests
- [ ] Verify on macOS with Docker Desktop
- [ ] Verify in Linux Docker container
- [ ] Check toolchain compatibility
```

## gh CLI Command Examples

### Create Issue from Template

```bash
# Save issue body to file
cat > issue-body.md << 'EOF'
## Task Overview
...
EOF

# Create issue with all metadata
gh issue create \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --title "[EOA-042] Implement SSH key management" \
  --body "$(cat issue-body.md)" \
  --label "status:backlog" \
  --label "priority:high" \
  --label "platform:linux" \
  --label "type:feature" \
  --label "toolchain:python" \
  --label "assign:remote" \
  --assignee "{{ASSIGNEE}}" \
  --project "{{PROJECT_NUMBER}}"
```

### Create Issue Interactively

```bash
# gh will open editor for body
gh issue create \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --title "[{{TASK_ID}}] {{TITLE}}" \
  --label "status:backlog" \
  --label "priority:{{PRIORITY}}" \
  --label "platform:{{PLATFORM}}" \
  --web
```

### Update Issue with Toolchain Info

```bash
# Add toolchain info to existing issue
gh issue edit {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --add-label "toolchain:{{TOOLCHAIN}}" \
  --body "$(cat updated-body.md)"
```

### Add Issue to Project

```bash
# Get issue URL
ISSUE_URL=$(gh issue view {{ISSUE_NUMBER}} --repo {{GITHUB_OWNER}}/{{REPO_NAME}} --json url --jq .url)

# Add to project
gh project item-add {{PROJECT_NUMBER}} \
  --owner {{GITHUB_OWNER}} \
  --url "$ISSUE_URL"
```

### Set Project Fields

```bash
# Set custom fields on project item
gh project item-edit \
  --project-id {{PROJECT_ID}} \
  --id {{ITEM_ID}} \
  --field-id {{STATUS_FIELD_ID}} \
  --value "Backlog"

gh project item-edit \
  --project-id {{PROJECT_ID}} \
  --id {{ITEM_ID}} \
  --field-id {{PLATFORM_FIELD_ID}} \
  --text "{{PLATFORM}}"
```

## Automated Issue Creation Script

Save as `scripts/create-eoa-issue.sh`:

```bash
#!/bin/bash
set -e

# Usage: ./create-eoa-issue.sh TASK_ID TITLE PLATFORM PRIORITY

TASK_ID="$1"
TITLE="$2"
PLATFORM="$3"
PRIORITY="${4:-medium}"

GITHUB_OWNER="${GITHUB_OWNER:-myorg}"
REPO_NAME="${REPO_NAME:-myrepo}"
PROJECT_NUMBER="${PROJECT_NUMBER:-1}"

# Create issue body from template
cat > /tmp/issue-body.md << EOF
## Task Overview

**Task ID:** ${TASK_ID}
**Component:** TBD
**Priority:** ${PRIORITY}
**Complexity:** TBD

## Description

${TITLE}

## Toolchain Specification

**Platform:** ${PLATFORM}
**Toolchain Template:** TBD

### Required Tools
- TBD

### Environment Requirements
\`\`\`yaml
platform: ${PLATFORM}
\`\`\`

## Acceptance Criteria

- [ ] Requirements defined
- [ ] Implementation complete
- [ ] Tests pass
- [ ] Code reviewed
- [ ] Documentation updated

## Labels to Apply

- status:backlog
- priority:${PRIORITY}
- platform:${PLATFORM}
EOF

# Create issue
ISSUE_URL=$(gh issue create \
  --repo "$GITHUB_OWNER/$REPO_NAME" \
  --title "[${TASK_ID}] ${TITLE}" \
  --body "$(cat /tmp/issue-body.md)" \
  --label "status:backlog" \
  --label "priority:${PRIORITY}" \
  --label "platform:${PLATFORM}" \
  --project "$PROJECT_NUMBER" \
  --json url \
  --jq .url)

echo "Issue created: $ISSUE_URL"

# Clean up
rm /tmp/issue-body.md
```

## Troubleshooting

### Issue Not Added to Project
- Verify project number is correct (not project ID)
- Check repository is linked to project
- Use `gh project link` if needed

### Labels Not Applied
- Verify labels exist: `gh label list --repo {{GITHUB_OWNER}}/{{REPO_NAME}}`
- Create missing labels using PROJECT_SETUP.md

### Cannot Set Assignee
- Verify assignee has repository access
- Use GitHub username, not display name
- Check organization permissions

### Toolchain Template Path Invalid
- Use relative paths from repository root
- Verify template file exists
- Use forward slashes even on Windows
