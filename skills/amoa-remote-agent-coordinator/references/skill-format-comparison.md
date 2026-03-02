# Skill Format Comparison: Open Spec vs Claude Code Skills

Comparison between the Anthropic Open Agent Skills Specification and the Claude Code Skills format (the skills subset of the plugin spec).

## Contents

- [When comparing Open Spec vs Claude Code Skills](#summary)
- [When checking frontmatter field compatibility](#frontmatter-field-comparison)
- [When using the Open Agent Skills Specification](#open-agent-skills-specification)
- [When using Claude Code Skills features](#claude-code-skills-specification)
- [When checking compatibility between formats](#compatibility)
- [When writing for maximum portability](#recommendations)
- [When validating skills](#validation-strategy)
- [When following best practices](#best-practices)
- [When you need external references](#references)

## Summary

| Aspect | Open Spec (agentskills.io) | Claude Code Skills |
|--------|---------------------------|-------------------|
| **Scope** | Universal agent skills | Claude Code specific |
| **Base format** | SKILL.md + optional dirs | SKILL.md + optional dirs |
| **Tool restrictions** | `allowed-tools` (experimental) | `allowed-tools` (full support) |
| **Model selection** | Not supported | `model` field supported |
| **Script handling** | Generic | Execute scripts, consume output only |
| **Priority system** | Not defined | Enterprise > Personal > Project > Plugin |
| **Subagent integration** | Not defined | Explicit `skills` field in agents |

## Frontmatter Field Comparison

| Field | Open Spec | Claude Code Skills | Notes |
|-------|-----------|-------------------|-------|
| `name` | Required, 1-64 chars | Required, 1-64 chars | Same constraints |
| `description` | Required, 1-1024 chars | Required, max 1024 chars | Same constraints |
| `license` | Optional | Not in spec | Open Spec only |
| `compatibility` | Optional, 1-500 chars | Not in spec | Open Spec only |
| `metadata` | Optional key-value | Not in spec | Open Spec only |
| `allowed-tools` | Experimental | Full support | Claude Code is richer |
| `model` | Not supported | Optional | Claude Code only |

## Open Agent Skills Specification

**Repository**: https://github.com/agentskills/agentskills
**Documentation**: https://agentskills.io/specification

### Directory Structure

```
skill-name/
├── SKILL.md          # Required
├── scripts/          # Optional executables
├── references/       # Optional docs
└── assets/           # Optional static files
```

### SKILL.md Format

```yaml
---
name: my-skill-name
description: What this skill does and when to use it
license: Apache-2.0
compatibility: Requires Python 3.9+
metadata:
  author: Your Name
  version: 1.0.0
allowed-tools: Read Grep Glob
---

# My Skill Name

Instructions for the agent...
```

### Name Validation Rules

- 1-64 characters maximum
- **Lowercase only** (uppercase rejected)
- Alphanumeric and hyphens only
- Cannot start/end with hyphen
- No consecutive hyphens (`--`)
- Must match parent directory name

### Validation Tool

```bash
# Install from GitHub
pip install "git+https://github.com/agentskills/agentskills.git#subdirectory=skills-ref"

# Validate a skill
skills-ref validate ./my-skill

# Read properties as JSON
skills-ref read-properties ./my-skill

# Generate prompt XML
skills-ref to-prompt ./skill-a ./skill-b
```

## Claude Code Skills Specification

**Documentation**: https://code.claude.com/docs/en/skills

### Directory Structure

```
skill-name/
├── SKILL.md          # Required
├── reference.md      # Optional detailed docs
├── examples.md       # Optional usage examples
└── scripts/          # Utility scripts (executed, not loaded)
    └── helper.py
```

### SKILL.md Format

```yaml
---
name: my-skill-name
description: What this skill does and when to use it. Include trigger keywords.
allowed-tools: Read, Grep, Glob
model: claude-sonnet-4-20250514
---

# My Skill Name

## Instructions
Step-by-step guidance for Claude.

## Examples
Concrete usage examples.

## Additional resources
- For API details, see [reference.md]\(reference.md\)
- For examples, see [examples.md]\(examples.md\)

## Utility scripts
Run the validation script:
```bash
python scripts/validate.py input.txt
```
```

### Claude Code-Specific Features

#### 1. allowed-tools (Full Support)

Restricts Claude's tool access when skill is active:

```yaml
allowed-tools: Read, Grep, Glob
```

- Claude can only use listed tools without permission
- Useful for read-only workflows and security-sensitive operations
- Omit field for no restrictions

#### 2. model Field

Specify model when skill is active:

```yaml
model: claude-sonnet-4-20250514
```

- Defaults to conversation's current model if omitted

#### 3. Script Execution Pattern

Scripts are **executed**, not loaded into context:

```markdown
## Validation
Run the validation script:
```bash
python scripts/validate.py input.txt
```
```

- Script output (not source code) consumes tokens
- Source code stays out of context
- Useful for validation, data processing, consistency-critical operations

#### 4. Progressive Disclosure

Keep SKILL.md under 500 lines. Reference supporting files:

```markdown
For complete API details, see [reference.md]\(reference.md\)
```

- Claude loads files only when needed
- Keep references one level deep (avoid A → B → C chains)

#### 5. Skill Priority

| Location | Path | Priority |
|----------|------|----------|
| Enterprise | Managed settings | 1 (highest) |
| Personal | `~/.claude/skills/` | 2 |
| Project | `.claude/skills/` | 3 |
| Plugin | `plugin/skills/` | 4 (lowest) |

Same-name skills: higher priority wins.

#### 6. Subagent Integration

Subagents don't inherit skills. Grant explicitly:

```yaml
# .claude/agents/eia-code-reviewer/AGENT.md
---
name: code-reviewer
skills: pr-review, security-check
---
```

Built-in agents (Explore, Plan, Verify) cannot use skills.

## Compatibility

### What Works in Both

- `SKILL.md` with `name` and `description` frontmatter
- `scripts/` directory for executables
- `references/` directory for documentation
- `assets/` directory for static files
- `allowed-tools` field (experimental in Open Spec, full in Claude Code)

### Open Spec Only

- `license` field
- `compatibility` field
- `metadata` key-value pairs
- `skills-ref` validation CLI

### Claude Code Only

- `model` field for model selection
- Skill priority system (enterprise > personal > project > plugin)
- Subagent integration with `skills` field
- Script execution pattern (output only, not source)
- Progressive disclosure with one-level-deep references

## Recommendations

### For Maximum Portability

Use only fields supported by both:

```yaml
---
name: my-skill-name
description: What this does and when to use it
allowed-tools: Read, Grep, Glob
---
```

### For Claude Code-Specific Features

Add Claude Code fields as needed:

```yaml
---
name: my-skill-name
description: What this does and when to use it
allowed-tools: Read, Grep, Glob
model: claude-sonnet-4-20250514
---
```

### For Open Spec Distribution

Include Open Spec metadata:

```yaml
---
name: my-skill-name
description: What this does and when to use it
license: Apache-2.0
compatibility: Python 3.9+, Node.js 18+
metadata:
  author: Your Name
  version: 1.0.0
---
```

## Validation Strategy

1. **Use `skills-ref validate`** for Open Spec compliance (name, description constraints)
2. **Test in Claude Code** for full feature validation (allowed-tools, model, subagents)

```bash
# Open Spec validation
skills-ref validate ./my-skill

# Claude Code testing
# Install skill and test with Claude Code CLI
```

## Best Practices

See `skill-authoring-best-practices.md` for comprehensive Anthropic guidance on:
- Core principles (conciseness, degrees of freedom, model testing)
- Skill structure (naming, descriptions, progressive disclosure)
- Workflows and feedback loops
- Executable scripts patterns
- Anti-patterns to avoid
- Evaluation and iteration strategies

## References

- Open Spec: https://agentskills.io/specification
- Claude Code Skills: https://code.claude.com/docs/en/skills
- Claude Code Best Practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- skills-ref Package: https://github.com/agentskills/agentskills/tree/main/skills-ref
