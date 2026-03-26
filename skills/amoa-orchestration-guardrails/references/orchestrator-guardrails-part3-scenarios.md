# Orchestrator Guardrails - Part 3: Common Scenarios


## Contents

- [4.0 Common Scenarios](#40-common-scenarios)
  - [4.1 Research Phase](#41-research-phase)
  - [4.2 Experimentation Phase](#42-experimentation-phase)
  - [4.3 Planning Phase](#43-planning-phase)
  - [4.4 Delegation Phase](#44-delegation-phase)
  - [4.5 Monitoring Phase](#45-monitoring-phase)

---

**Parent Document**: [orchestrator-guardrails.md](./orchestrator-guardrails.md)

---

## 4.0 Common Scenarios

### 4.1 Research Phase

**Goal**: Understand the codebase, requirements, and constraints

**Allowed Actions**:
```bash
# Reading files
Read tool: /path/to/file.py

# Searching codebase
Grep: pattern="class.*Controller"
Glob: pattern="**/*.test.ts"

# Understanding git history
git log --oneline -20
git diff main..feature-branch --stat

# Checking GitHub state
gh issue list
gh pr list
```

**NOT Allowed**:
```bash
# These are implementation, not research
npm install  # NO - document requirements instead
cargo build  # NO - delegate build to agent
pytest       # NO - delegate testing to agent
```

### 4.2 Experimentation Phase

**Goal**: Verify toolchain behavior, API syntax, or config validity before delegating

**Allowed Actions** (SMALL experiments only):
```bash
# API verification (single request)
curl -s "https://api.github.com/users/octocat" | jq '.login'

# Syntax testing (one-liner)
echo '{"test": 1}' | jq .test

# Tool behavior check
uv run python -c "import sys; print(sys.version)"
docker pull --quiet electronuserland/builder:wine 2>&1 | head -1

# Config validation (read-only)
docker-compose config

# Quick temp script (< 20 lines, in scripts_dev/)
cat > /tmp/test_api.py << 'EOF'
import requests
r = requests.get("https://api.example.com/health")
print(r.status_code)
EOF
uv run /tmp/test_api.py
rm /tmp/test_api.py  # ALWAYS delete after
```

**NOT Allowed** (LARGE experiments - delegate instead):
```bash
# These exceed experiment limits
python scripts/full_integration_test.py  # > 20 lines → Delegate
docker-compose up -d                      # Infrastructure → Delegate
cargo build --release                     # Full build → Delegate
npm run test                              # Test suite → Delegate
```

**Size Limits Reminder**:
- < 20 lines of code
- < 5 minutes runtime
- Single temp file in /tmp or scripts_dev/
- MUST delete after verification
- No production impact

### 4.3 Planning Phase

**Goal**: Create detailed task specifications and plans

**Allowed Actions**:
```markdown
# Writing plan documents
Write: /path/to/docs/plan.md
Write: /path/to/docs/task-spec.md

# Updating todo lists
TodoWrite: [tasks...]

# Creating delegation templates
Write: /path/to/tasks/delegation-GH-42.md
```

**NOT Allowed**:
```markdown
# These are implementation, not planning
Write: /path/to/src/new_feature.py  # NO - code is implementation
Write: /path/to/docker-compose.yml  # NO - config is implementation
```

### 4.4 Delegation Phase

**Goal**: Send tasks to remote agents with complete instructions

**Allowed Actions**:
```bash
# Sending AI Maestro messages
# Use the agent-messaging skill to send task delegations
# Specify: recipient, subject, content, type, priority

# Creating delegation documents
Write: /path/to/tasks/delegation-GH-42.md

# Uploading docs to GitHub (via message)
"Upload this doc to issue #42 and send URL to agent"
```

**NOT Allowed**:
```bash
# Implementation belongs to the delegated agent
npm run build        # NO - agent runs this
git push             # NO - agent pushes
docker-compose up    # NO - agent sets up infrastructure
```

### 4.5 Monitoring Phase

**Goal**: Track progress and handle escalations

**Allowed Actions**:
```bash
# Checking for messages
# Use the agent-messaging skill to check inbox for unread messages

# Reading PR status
gh pr view 42

# Checking CI status
gh run list
gh run view 12345
```

**NOT Allowed**:
```bash
# Even if blocked, don't do implementation yourself
npm run build        # NO - ask agent to retry
git commit --amend   # NO - ask agent to fix
```

---

**Previous**: [Part 2: Decision Trees](./orchestrator-guardrails-part2-decision-trees.md)

**Next**: [Part 4: Violation Detection and Examples](./orchestrator-guardrails-part4-violations-and-examples.md)
