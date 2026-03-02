# Project Setup Menu - Part 3: Implementation & Troubleshooting


## Contents

- [Table of Contents](#table-of-contents)
- [Menu Implementation](#menu-implementation)
  - [Using AskUserQuestion Tool](#using-askuserquestion-tool)
  - [Interactive Flow Pattern](#interactive-flow-pattern)
- [Response Handling](#response-handling)
  - [Storage Location](#storage-location)
  - [Using Stored Configuration](#using-stored-configuration)
  - [Configuration Updates](#configuration-updates)
- [Troubleshooting](#troubleshooting)
  - [User Skips Setup](#user-skips-setup)
  - [Conflicting Answers](#conflicting-answers)
  - [Changed Mind Mid-Project](#changed-mind-mid-project)
  - [Missing Configuration File](#missing-configuration-file)
- [Best Practices](#best-practices)
  - [DO:](#do)
  - [DON'T:](#dont)
- [Example Session](#example-session)

---

## Table of Contents

- [Menu Implementation](#menu-implementation)
  - [Using AskUserQuestion Tool](#using-askuserquestion-tool)
  - [Interactive Flow Pattern](#interactive-flow-pattern)
- [Response Handling](#response-handling)
  - [Storage Location](#storage-location)
  - [Using Stored Configuration](#using-stored-configuration)
  - [Configuration Updates](#configuration-updates)
- [Troubleshooting](#troubleshooting)
  - [User Skips Setup](#user-skips-setup)
  - [Conflicting Answers](#conflicting-answers)
  - [Changed Mind Mid-Project](#changed-mind-mid-project)
  - [Missing Configuration File](#missing-configuration-file)
- [Best Practices](#best-practices)
- [Example Session](#example-session)

**Related Documents:**
- [Part 1: Team, Repository & Release Configuration](project-setup-menu-part1-team-repo-release.md)
- [Part 2: Documentation & Quality Requirements](project-setup-menu-part2-docs-quality.md)

---

## Menu Implementation

### Using AskUserQuestion Tool

The orchestrator must present these questions using the following format:

```python
# Pseudo-code for implementation
questions = [
    {
        "id": "team.human_developers",
        "prompt": "How many human developers will work on this project?",
        "type": "choice_with_input",
        "options": ["Solo (just you)", "Small team (2-5)", "Medium team (6-15)", "Large team (16+)"],
        "follow_up": "Please provide GitHub usernames if known (comma-separated):"
    },
    {
        "id": "team.ai_agents",
        "prompt": "Will AI agents work on this project?",
        "type": "choice",
        "options": ["No AI agents", "Local AI agents only", "Remote AI agents via AI Maestro"],
        "conditional_follow_up": {
            "Remote AI agents via AI Maestro": "Provide AI Maestro session IDs (comma-separated):"
        }
    },
    # ... continue for all 13 questions
]

# Present questions sequentially
for question in questions:
    response = ask_user_question(question)
    store_response(question["id"], response)

# After all questions answered
confirm_settings_with_user()
save_to_project_config()
```

### Interactive Flow Pattern

1. **Welcome Message:**
   ```
   Before we begin, I need to ask you 13 quick questions to set up this project correctly.
   This ensures I understand your workflow, quality standards, and team structure.

   This will take approximately 5-10 minutes. Ready? (Yes/No)
   ```

2. **Present Questions Sequentially:**
   - Show question number (X of 13)
   - Present question with clear options
   - Validate response
   - Show confirmation of what was understood
   - Move to next question

3. **Summary and Confirmation:**
   ```
   Here's what I understood:

   Team: 1 human developer (you), 3 AI remote agents
   Repository: Branch protection on main, 1 approval required, CI must pass
   Releases: Alpha-only until milestone "MVP Complete", then publish to PyPI
   Versioning: Semantic Versioning, starting at 0.0.1
   Documentation: Deferred - inline docstrings only, full docs at v1.0.0
   Coverage: 80% target, strict enforcement
   Linting: Standard strictness, Ruff + Mypy + Black

   Is this correct? (Yes to confirm, No to restart, Edit to change specific answers)
   ```

4. **Save Configuration:**
   - Write to `.claude/project-config.json` (local)
   - Create `PROJECT_SETUP.md` in docs_dev (human-readable reference)
   - Add to orchestrator working memory

---

## Response Handling

### Storage Location

All responses MUST be stored in:
```
.claude/project-config.json
```

**Format:**
```json
{
  "config_version": "1.0.0",
  "created_at": "2025-12-31T00:41:00Z",
  "created_by": "orchestrator",
  "team": {
    "human_developers": {
      "count": 1,
      "usernames": ["Emasoft"]
    },
    "ai_agents": {
      "enabled": true,
      "type": "remote_maestro",
      "session_ids": ["libs-svg-svgbbox", "utils-media-processor"]
    },
    "permissions": {
      "restrictions": false,
      "details": "No restrictions - single developer"
    }
  },
  "repo": {
    "branch_protection": {
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
    },
    "required_reviews": {
      "count": 0,
      "dismiss_stale": false,
      "require_code_owners": false,
      "restrict_dismissals": false
    },
    "ci_requirements": {
      "required": true,
      "allow_override": false,
      "platforms": ["github-actions"],
      "required_checks": ["build", "test", "lint"],
      "branch_specific": {
        "main": "strict"
      }
    }
  },
  "release": {
    "alpha_only": {
      "enabled": true,
      "exit_condition": "milestone",
      "exit_trigger": "MVP Complete"
    },
    "package_publishing": {
      "enabled": false,
      "registries": [],
      "trigger": "manual",
      "package_name": "",
      "credentials_location": ""
    },
    "versioning": {
      "scheme": "semver",
      "initial_version": "0.0.1",
      "prerelease_format": {
        "alpha": "0.0.x-alpha.N",
        "beta": "0.x.y-beta.N",
        "rc": "x.y.z-rc.N"
      }
    }
  },
  "docs": {
    "continuous": {
      "enabled": false
    },
    "deferred": {
      "standards": {
        "require_function_docstrings": true,
        "require_class_docstrings": true,
        "require_module_headers": true,
        "format": "google"
      },
      "enforcement": {
        "linter_checks": true,
        "ci_fails_on_missing": false
      },
      "future_plan": "Build full docs at version 1.0.0"
    }
  },
  "quality": {
    "coverage": {
      "target_percentage": 80,
      "enforcement": "strict",
      "scope": ["line", "branch"],
      "exclusions": ["tests/*", "__init__.py"]
    },
    "linting": {
      "strictness": "standard",
      "linters": {
        "python": ["ruff", "mypy", "black"]
      },
      "auto_fix": {
        "on_commit": true,
        "formatters_only": true
      },
      "ci_enforcement": {
        "fail_on_errors": true,
        "fail_on_warnings": false
      }
    }
  }
}
```

### Using Stored Configuration

Throughout the project lifecycle, the orchestrator must reference this configuration for:

1. **Task Delegation:**
   - Check `team.ai_agents.session_ids` before sending AI Maestro messages
   - Verify permissions before assigning git operations

2. **PR Management:**
   - Respect `repo.required_reviews.count` before auto-merging
   - Check `repo.ci_requirements.required_checks` status

3. **Version Bumping:**
   - Use `release.versioning.scheme` to calculate next version
   - Respect `release.alpha_only.enabled` when bumping versions

4. **Publishing:**
   - Only publish to `release.package_publishing.registries`
   - Use `release.package_publishing.trigger` to determine if auto-publish is allowed

5. **Documentation:**
   - If `docs.continuous.enabled`, ensure docs are generated on commit
   - If `docs.deferred`, enforce `docs.deferred.standards` in linting

6. **Quality Gates:**
   - Fail PR if coverage < `quality.coverage.target_percentage`
   - Run linters specified in `quality.linting.linters`
   - Apply `quality.linting.strictness` to determine CI pass/fail

### Configuration Updates

Configuration can be updated mid-project by:

1. User explicitly requests: "Change coverage target to 90%"
2. Orchestrator re-asks relevant question
3. Updates `.claude/project-config.json`
4. Logs change in `PROJECT_SETUP.md`
5. Applies new setting immediately

**Never** silently override stored configuration. Always confirm with user first.

---

## Troubleshooting

### User Skips Setup
**Problem:** User says "just start coding" without answering setup questions.

**Solution:**
```
I understand you want to move quickly, but I need to ask 13 essential questions first.
Without these answers, I might make incorrect assumptions about:
- Can I auto-merge PRs? (Depends on review requirements)
- Can I publish releases? (Depends on package registry configuration)
- What test coverage is acceptable? (Affects PR approval)

This takes 5-10 minutes but prevents hours of rework later. Shall we proceed?
```

### Conflicting Answers
**Problem:** User says "strict linting" but also "no CI failures on warnings"

**Solution:**
```
I noticed a potential conflict:
- You selected "strict linting" (zero warnings allowed)
- But also "CI fails on errors only, not warnings"

These are contradictory. Strict linting means warnings should fail CI.

Would you like:
1. Strict linting with CI failures on warnings (truly strict)
2. Standard linting with warnings as informational (more practical)
```

### Changed Mind Mid-Project
**Problem:** User initially said "no package publishing" but now wants to publish to PyPI.

**Solution:**
```
I see you want to publish to PyPI now. Let me update the project configuration.

Current setting: release.package_publishing.enabled = false
New setting: release.package_publishing.enabled = true, registries = ["pypi"]

This requires:
1. PyPI account and API token
2. CI/CD workflow updates
3. Package metadata in setup.py / pyproject.toml

Shall I proceed with these changes?
```

### Missing Configuration File
**Problem:** `.claude/project-config.json` doesn't exist (first run, deleted, corrupted)

**Solution:**
```
I don't have a project configuration file. This means either:
1. This is the first time I'm working on this project
2. The configuration was deleted
3. The configuration is corrupted

I'll need to run the project setup questionnaire. This takes 5-10 minutes.
Ready to begin?
```

---

## Best Practices

### DO:
- Always run setup questionnaire for new projects
- Store responses in `.claude/project-config.json`
- Create human-readable summary in `PROJECT_SETUP.md`
- Reference configuration before every automated operation
- Ask for confirmation before overriding stored settings
- Validate responses (e.g., coverage can't be 150%)
- Provide clear option lists, not open-ended questions
- Show progress (Question 5 of 13)
- Summarize and confirm before saving

### DON'T:
- Never assume defaults without asking
- Never skip questions to "save time"
- Never override configuration silently
- Never ask vague questions ("What are your preferences?")
- Never store responses only in conversation memory (write to file!)
- Never proceed if configuration file is missing
- Never ask all questions in one giant block (sequential only)
- Never forget to validate input (catch invalid values)

---

## Example Session

```
Orchestrator: Before we begin working on this project, I need to set it up correctly.
              I'll ask you 13 questions about your team, workflow, and quality standards.
              This takes about 5-10 minutes. Ready?

User: Yes

Orchestrator: Question 1 of 13 - Team Configuration
              How many human developers will work on this project (including yourself)?

              Options:
              1. Solo (just you)
              2. Small team (2-5 developers)
              3. Medium team (6-15 developers)
              4. Large team (16+ developers)

User: Solo

Orchestrator: Understood: 1 developer (you).

              Question 2 of 13 - AI Agents
              Will AI agents work on this project alongside you?

              Options:
              1. No AI agents - human-only development
              2. Local AI agents only (Claude Code sessions on your machine)
              3. Remote AI agents via AI Maestro messaging

User: Remote AI agents

Orchestrator: Please provide the AI Maestro session IDs (full names, comma-separated):
              Example: libs-svg-svgbbox, apps-media-processor

User: libs-svg-svgbbox, utils-test-runner, docs-generator-main

Orchestrator: Understood: 3 remote AI agents (libs-svg-svgbbox, utils-test-runner, docs-generator-main)

              Question 3 of 13 - Access Permissions
              Are there any GitHub repository access restrictions for team members?

              Options:
              1. No restrictions - all team members have equal access
              2. Yes, there are restrictions (I'll specify)

User: No restrictions

Orchestrator: Understood: No access restrictions.

              [... continues through all 13 questions ...]

              All questions answered! Here's the configuration summary:

              Project Configuration Summary

              **Team:**
              - Human developers: 1 (solo)
              - AI agents: 3 remote (AI Maestro)
                - libs-svg-svgbbox
                - utils-test-runner
                - docs-generator-main
              - Permissions: No restrictions

              **Repository:**
              - Branch protection: main (PR required, CI required, linear history)
              - Required reviews: 0 (solo developer)
              - CI must pass: Yes (strict)

              **Releases:**
              - Strategy: Alpha-only until "Feature Complete" milestone
              - Package publishing: Disabled during alpha, enable PyPI at beta
              - Versioning: Semantic (0.0.x for alpha)

              **Documentation:**
              - Continuous docs: No
              - Inline docs: Required (Google-style docstrings)
              - Full docs: Build at v1.0.0

              **Quality:**
              - Test coverage: 80% minimum (strict enforcement)
              - Linting: Standard strictness (Ruff, Mypy, Black)
              - Auto-fix: Yes (formatters on commit)

              Is this correct?

              Options:
              1. Yes - Save and proceed
              2. No - Restart questionnaire
              3. Edit - Change specific answers

User: Yes

Orchestrator: Configuration saved to .claude/project-config.json
              Summary written to docs_dev/PROJECT_SETUP.md

              I'm ready to work! What should we build first?
```

---

**Previous:** [Part 2: Documentation & Quality Requirements](project-setup-menu-part2-docs-quality.md)
