# Project Setup Menu - Part 1: Team, Repository & Release Configuration


## Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Use-Case Quick Reference](#use-case-quick-reference)
- [Team Configuration](#team-configuration)
  - [Question 1: Human Developers](#question-1-human-developers)
  - [Question 2: AI Remote Agents](#question-2-ai-remote-agents)
  - [Question 3: Access Permissions](#question-3-access-permissions)
- [Repository Configuration](#repository-configuration)
  - [Question 4: Branch Protection](#question-4-branch-protection)
  - [Question 5: Required Reviews](#question-5-required-reviews)
  - [Question 6: CI Requirements](#question-6-ci-requirements)
- [Release Strategy](#release-strategy)
  - [Question 7: Alpha-Only Development](#question-7-alpha-only-development)
  - [Question 8: Package Publishing](#question-8-package-publishing)
  - [Question 9: Versioning Scheme](#question-9-versioning-scheme)

---

## Table of Contents

- [Overview](#overview)
- [Use-Case Quick Reference](#use-case-quick-reference)
- [Team Configuration](#team-configuration)
  - [Question 1: Human Developers](#question-1-human-developers)
  - [Question 2: AI Remote Agents](#question-2-ai-remote-agents)
  - [Question 3: Access Permissions](#question-3-access-permissions)
- [Repository Configuration](#repository-configuration)
  - [Question 4: Branch Protection](#question-4-branch-protection)
  - [Question 5: Required Reviews](#question-5-required-reviews)
  - [Question 6: CI Requirements](#question-6-ci-requirements)
- [Release Strategy](#release-strategy)
  - [Question 7: Alpha-Only Development](#question-7-alpha-only-development)
  - [Question 8: Package Publishing](#question-8-package-publishing)
  - [Question 9: Versioning Scheme](#question-9-versioning-scheme)

---

## Overview

Before starting any project work, the orchestrator MUST conduct an interactive setup session with the user to establish project parameters, team configuration, and quality standards. This prevents assumptions, ensures alignment, and establishes clear boundaries for automated operations.

**CRITICAL RULE**: Never assume defaults. Always ask. Store responses in project memory for future reference.

## Use-Case Quick Reference

**When to use this guide:**
- When starting a new project for the first time → [Menu Implementation](project-setup-menu-part3-implementation-troubleshooting.md#menu-implementation)
- If configuration file is missing or corrupted → [Troubleshooting](project-setup-menu-part3-implementation-troubleshooting.md#troubleshooting) > Missing Configuration File
- When you need to understand team structure → [Team Configuration](#team-configuration)
- If you need to set up AI Maestro remote agents → [Team Configuration](#team-configuration) > Question 2: AI Remote Agents
- When configuring branch protection rules → [Repository Configuration](#repository-configuration) > Question 4: Branch Protection
- If deciding on alpha-only development strategy → [Release Strategy](#release-strategy) > Question 7: Alpha-Only Development
- When setting up package publishing → [Release Strategy](#release-strategy) > Question 8: Package Publishing
- If user changes mind mid-project → [Troubleshooting](project-setup-menu-part3-implementation-troubleshooting.md#troubleshooting) > Changed Mind Mid-Project
- When referencing stored configuration → [Response Handling](project-setup-menu-part3-implementation-troubleshooting.md#response-handling) > Using Stored Configuration

**Related Documents:**
- [Part 2: Documentation & Quality Requirements](project-setup-menu-part2-docs-quality.md)
- [Part 3: Implementation & Troubleshooting](project-setup-menu-part3-implementation-troubleshooting.md)

---

## Team Configuration

### Question 1: Human Developers
**Prompt to User:**
```
How many human developers will work on this project (including yourself)?

Options:
1. Solo (just you)
2. Small team (2-5 developers)
3. Medium team (6-15 developers)
4. Large team (16+ developers)

Please specify the number and provide GitHub usernames if known.
```

**Why This Matters:**
- Affects PR review requirements
- Determines communication patterns
- Influences branch strategy
- Impacts merge conflict probability

**Storage Key:** `team.human_developers`
**Format:** `{ "count": <number>, "usernames": ["user1", "user2", ...] }`

---

### Question 2: AI Remote Agents
**Prompt to User:**
```
Will AI agents work on this project alongside humans?

Options:
1. No AI agents - human-only development
2. Local AI agents only (Claude Code sessions on your machine)
3. Remote AI agents via AI Maestro messaging

If using remote AI agents, provide their AI Maestro session IDs:
Example: libs-svg-svgbbox, apps-media-processor, utils-test-runner

Format: domain-subdomain-name (full session names, not aliases)
```

**Why This Matters:**
- AI agents need coordination to avoid simultaneous git operations
- Determines if AI Maestro messaging hooks are required
- Affects task delegation strategy
- Influences commit attribution

**Storage Key:** `team.ai_agents`
**Format:**
```json
{
  "enabled": true/false,
  "type": "local_only" | "remote_maestro",
  "session_ids": ["full-session-name-1", "full-session-name-2"]
}
```

---

### Question 3: Access Permissions
**Prompt to User:**
```
Are there any access restrictions for team members?

Consider:
- GitHub repository access levels (read, triage, write, maintain, admin)
- Branch protection bypass permissions
- Required status check exemptions
- Force push permissions
- Secrets and environment access

Please list any restrictions or confirm "No restrictions - all team members have equal access"
```

**Why This Matters:**
- Determines who can merge PRs
- Affects automated workflow permissions
- Influences task delegation (can't delegate to agents without write access)
- Impacts security policy enforcement

**Storage Key:** `team.permissions`
**Format:**
```json
{
  "restrictions": true/false,
  "details": "Description of restrictions",
  "members": {
    "username": "access_level"
  }
}
```

---

## Repository Configuration

### Question 4: Branch Protection
**Prompt to User:**
```
Which branches should have protection rules?

Common patterns:
1. main/master only
2. main + develop
3. main + release/* + develop
4. All branches matching pattern: _______

For each protected branch, specify:
- Require pull request before merging?
- Require status checks to pass?
- Require conversation resolution before merging?
- Require signed commits?
- Require linear history?
- Allow force pushes? (Usually: No)
- Allow deletions? (Usually: No)
```

**Why This Matters:**
- Prevents accidental force pushes to critical branches
- Enforces code review workflow
- Ensures CI passes before merge
- Protects release integrity

**Storage Key:** `repo.branch_protection`
**Format:**
```json
{
  "protected_branches": [
    {
      "pattern": "main",
      "require_pr": true,
      "require_status_checks": true,
      "require_conversation_resolution": true,
      "require_signed_commits": false,
      "require_linear_history": true,
      "allow_force_pushes": false,
      "allow_deletions": false
    }
  ]
}
```

---

### Question 5: Required Reviews
**Prompt to User:**
```
How many approvals are required for pull requests?

Options:
1. No approvals required (solo development, AI agents can auto-merge)
2. 1 approval required
3. 2 approvals required
4. Custom: _____ approvals required

Additional review settings:
- Dismiss stale reviews when new commits are pushed? (Recommended: Yes)
- Require review from code owners? (If CODEOWNERS file exists)
- Restrict who can dismiss reviews? (Recommended for large teams)
```

**Why This Matters:**
- Affects AI agent autonomy (can agents approve each other's PRs?)
- Determines PR merge latency
- Influences code quality gates
- Impacts solo vs collaborative workflow

**Storage Key:** `repo.required_reviews`
**Format:**
```json
{
  "count": 1,
  "dismiss_stale": true,
  "require_code_owners": false,
  "restrict_dismissals": false
}
```

---

### Question 6: CI Requirements
**Prompt to User:**
```
Must CI/CD checks pass before merging pull requests?

Options:
1. Yes - All status checks must pass (strict)
2. Yes - But allow manual override by maintainers
3. No - CI is informational only
4. Conditional - Required for main branch, optional for feature branches

Which CI/CD platforms are you using?
- GitHub Actions
- Travis CI
- CircleCI
- Jenkins
- GitLab CI
- Other: _______

List required status checks that must pass:
Example: "build", "test", "lint", "security-scan"
```

**Why This Matters:**
- Determines if orchestrator can auto-merge PRs
- Affects release automation safety
- Influences testing strategy
- Impacts deployment pipeline

**Storage Key:** `repo.ci_requirements`
**Format:**
```json
{
  "required": true,
  "allow_override": false,
  "platforms": ["github-actions"],
  "required_checks": ["build", "test", "lint"],
  "branch_specific": {
    "main": "strict",
    "feature/*": "optional"
  }
}
```

---

## Release Strategy

### Question 7: Alpha-Only Development
**Prompt to User:**
```
Should this project remain in ALPHA status during active development?

Alpha-only development means:
- Version: 0.0.x (never reaches 0.1.0 or 1.0.0 during development)
- Releases: GitHub releases only (no package registry publishing)
- Stability: Breaking changes allowed without major version bump
- Audience: Developers and early testers only

Options:
1. Yes - Stay in alpha (0.0.x) until feature-complete
2. No - Progress through alpha → beta → stable as milestones complete
3. Custom strategy: _______

If alpha-only, when should the project exit alpha?
- Specific milestone: _______
- Feature checklist completion
- User decision (ask before promoting)
```

**Why This Matters:**
- Controls version numbering automation
- Determines publishing scope
- Affects breaking change policy
- Influences stability commitments

**Storage Key:** `release.alpha_only`
**Format:**
```json
{
  "enabled": true,
  "exit_condition": "milestone" | "checklist" | "manual",
  "exit_trigger": "Description of when to exit alpha"
}
```

---

### Question 8: Package Publishing
**Prompt to User:**
```
When the project reaches beta/stable, which package registries should receive automated publishes?

Select all that apply:
- [ ] PyPI (Python packages)
- [ ] Crates.io (Rust crates)
- [ ] NPM (Node.js packages)
- [ ] Homebrew (macOS/Linux binaries)
- [ ] Bun registry (JavaScript/TypeScript)
- [ ] RubyGems (Ruby gems)
- [ ] Maven Central (Java/JVM)
- [ ] NuGet (C#/.NET)
- [ ] Go packages (pkg.go.dev)
- [ ] Docker Hub (container images)
- [ ] GitHub Packages (any language)
- [ ] Other: _______

Publishing triggers:
1. Manual - require explicit user approval for each publish
2. Automated on tag - auto-publish when version tag is pushed
3. Automated on release - auto-publish when GitHub release is created
4. Hybrid - auto-publish alpha/beta, manual approval for stable

Package naming convention: _______
```

**Why This Matters:**
- Determines CI/CD publish workflow
- Affects credential management (PyPI tokens, NPM tokens, etc.)
- Influences version bumping automation
- Impacts rollback procedures

**Storage Key:** `release.package_publishing`
**Format:**
```json
{
  "enabled": true,
  "registries": ["pypi", "npm", "homebrew"],
  "trigger": "automated_on_tag" | "manual" | "automated_on_release",
  "package_name": "my-package",
  "credentials_location": "GitHub Secrets"
}
```

---

### Question 9: Versioning Scheme
**Prompt to User:**
```
What versioning scheme should the project use?

Options:
1. Semantic Versioning (SemVer)
   - Format: MAJOR.MINOR.PATCH (e.g., 1.4.2)
   - Breaking changes → MAJOR bump
   - New features → MINOR bump
   - Bug fixes → PATCH bump

2. Calendar Versioning (CalVer)
   - Format: YYYY.MM.DD or YYYY.MM.MICRO (e.g., 2025.01.15)
   - Based on release date, not change significance

3. Custom scheme: _______

Pre-release identifiers:
- Alpha: 0.0.x-alpha.N or 0.0.x.aN
- Beta: 0.x.y-beta.N or 0.x.y.bN
- Release Candidate: x.y.z-rc.N

Initial version: _______ (default: 0.0.1)
```

**Why This Matters:**
- Controls automated version bumping logic
- Affects changelog generation
- Determines breaking change communication
- Influences user upgrade expectations

**Storage Key:** `release.versioning`
**Format:**
```json
{
  "scheme": "semver" | "calver" | "custom",
  "initial_version": "0.0.1",
  "prerelease_format": {
    "alpha": "0.0.x-alpha.N",
    "beta": "0.x.y-beta.N",
    "rc": "x.y.z-rc.N"
  }
}
```

---

**Continue to:** [Part 2: Documentation & Quality Requirements](project-setup-menu-part2-docs-quality.md)
