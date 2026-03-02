# Changelog Writing Guidelines

## Table of Contents (Use-Case Oriented)

- **1.0 When you need to write a changelog entry for a new release** --> [Overview: What a Changelog Is and Why It Matters](#1-overview-what-a-changelog-is-and-why-it-matters)
- **2.0 When you need to decide how to group and categorize changes** --> [Impact Categories](#2-impact-categories)
  - **2.1 Choosing the right category for each change** --> [Category Definitions and Examples](#21-category-definitions-and-examples)
  - **2.2 Ordering categories within an entry** --> [Category Order](#22-category-order)
- **3.0 When you need to write a specific change description** --> [Writing Effective Change Descriptions](#3-writing-effective-change-descriptions)
  - **3.1 Avoiding vague or generic descriptions** --> [Good vs Bad Examples](#31-good-vs-bad-examples)
  - **3.2 Referencing issues and pull requests** --> [Linking to Issues and PRs](#32-linking-to-issues-and-prs)
  - **3.3 Crediting contributors** --> [Contributor Attribution](#33-contributor-attribution)
- **4.0 When the release includes breaking changes** --> [Documenting Breaking Changes](#4-documenting-breaking-changes)
  - **4.1 Writing migration instructions** --> [Migration Guide Format](#41-migration-guide-format)
- **5.0 When formatting the changelog file** --> [Keep a Changelog Format Specification](#5-keep-a-changelog-format-specification)
  - **5.1 Structuring the version heading** --> [Version Heading Format](#51-version-heading-format)
  - **5.2 Handling pre-release versions** --> [Pre-Release Changelog Sections](#52-pre-release-changelog-sections)
- **6.0 Example: A complete changelog entry for a minor release** --> [Complete Minor Release Example](#6-complete-minor-release-example)
- **7.0 Example: A breaking change entry with migration guide** --> [Complete Breaking Change Example](#7-complete-breaking-change-example)
- **8.0 Quick-reference checklist for reviewing a changelog entry** --> [Changelog Review Checklist](#8-changelog-review-checklist)

---

## 1. Overview: What a Changelog Is and Why It Matters

A **changelog** (short for "change log") is a file -- usually named `CHANGELOG.md` -- that records all notable changes made to a software project, organized by version number and date.

**Why changelogs matter for the Orchestrator:**
- Many CI/CD pipelines validate that a changelog entry exists before allowing a release. If the entry is missing, the release is blocked.
- Users and contributors read changelogs to understand what changed between versions.
- Good changelogs reduce support requests because users can self-diagnose whether upgrading will affect them.
- Changelogs serve as a historical record of the project's evolution.

**Key principle**: The changelog is written for humans, not machines. Every entry should be understandable by someone who uses the software but does not read the source code.

---

## 2. Impact Categories

Changes are grouped into categories based on their impact on users. This grouping helps readers quickly find the information relevant to them.

### 2.1 Category Definitions and Examples

| Category | Definition | When to Use |
|----------|-----------|-------------|
| **New Features** | Entirely new functionality that did not exist before | A new API endpoint, a new command-line flag, a new UI panel |
| **Improvements** | Enhancements to existing functionality | Faster performance, better error messages, improved accessibility |
| **Bug Fixes** | Corrections to behavior that was not working as designed | Crash fixes, data corruption fixes, incorrect calculation fixes |
| **Breaking Changes** | Changes that require users to modify their code, configuration, or workflow | Renamed API parameters, removed deprecated features, changed default behavior |
| **Deprecations** | Features that still work but are marked for removal in a future version | An old API endpoint replaced by a new one, a configuration key that will be renamed |
| **Security** | Fixes for security vulnerabilities | Patched XSS vulnerability, fixed authentication bypass, updated vulnerable dependency |

### 2.2 Category Order

List categories in this order within each version entry. This order puts the most impactful information first:

1. Breaking Changes (users need to act immediately)
2. Security (users need to update immediately)
3. New Features (users want to know about new capabilities)
4. Improvements (users want to know about enhancements)
5. Bug Fixes (users want to know what was fixed)
6. Deprecations (users should plan for future changes)

Omit any category that has no entries for the release. Do not include empty categories.

---

## 3. Writing Effective Change Descriptions

### 3.1 Good vs Bad Examples

Every change description must answer: **what changed** and **why a user should care**.

**BAD examples** (vague, unhelpful):

```markdown
- Fixed bug
- Updated dependencies
- Improved performance
- Code cleanup
- Various fixes and improvements
- Refactored module
```

**GOOD examples** (specific, actionable):

```markdown
- Fixed crash when opening files larger than 100MB on systems with less than 4GB of RAM
- Updated the `requests` library from 2.28.0 to 2.31.0 to patch CVE-2023-32681 (cookie handling vulnerability)
- Reduced startup time from 8 seconds to 2 seconds by lazy-loading the plugin system
- Fixed incorrect total in invoice calculations when discounts exceed 50%
- Added retry logic for database connections, resolving intermittent "connection refused" errors during deployment
- Fixed file upload failing silently when the server returns a 413 (payload too large) response
```

**Rules for writing good descriptions:**

1. **Start with a verb**: "Fixed", "Added", "Removed", "Changed", "Improved", "Updated"
2. **Name the specific component**: "Fixed crash in the file processor" not "Fixed crash"
3. **Include the trigger condition**: "when opening files larger than 100MB" not just "when opening files"
4. **Include the observable symptom**: "resulting in blank output" or "causing a TypeError on line 42"
5. **Quantify improvements**: "Reduced memory usage by 40%" not "Improved memory usage"

### 3.2 Linking to Issues and PRs

Reference related GitHub issues and pull requests using the `#N` syntax (where N is the issue or PR number). This creates clickable links in the rendered markdown on GitHub.

**Format:**

```markdown
- Fixed crash when processing Unicode filenames (#123)
- Added CSV export endpoint (#45, #67)
- Fixed memory leak in file processor (PR #48)
```

**Rules:**
- Use `#N` for issues: "Fixed the bug reported in #123"
- Use `PR #N` for pull requests when referencing the implementation: "Implemented in PR #48"
- Use `Fixes #N` when the change directly resolves an open issue (GitHub will automatically close the issue when the changelog is merged)
- Multiple references are separated by commas: "(#12, #34, #56)"

### 3.3 Contributor Attribution

Credit contributors by their GitHub username when they contributed a significant change. This is especially important for external contributors (people who do not work on the project full-time).

**Format:**

```markdown
- Added dark mode support (contributed by @username) (#78)
- Fixed race condition in WebSocket handler (reported by @reporter, fixed by @developer) (#92)
```

**Rules:**
- Use the `@username` format for GitHub usernames
- Credit both the reporter and the fixer when they are different people
- Attribution is optional for routine changes by core maintainers
- Attribution is mandatory for contributions from external contributors

---

## 4. Documenting Breaking Changes

A **breaking change** is any change that requires users to modify their existing code, configuration, or workflow in order to continue using the software after upgrading.

Breaking changes must be documented more thoroughly than other changes because users need clear instructions on how to adapt.

### 4.1 Migration Guide Format

Every breaking change entry must include:

1. **What changed**: The specific behavior that is different
2. **Why it changed**: The reason for the breaking change
3. **How to migrate**: Step-by-step instructions for updating

**Example of a well-documented breaking change:**

```markdown
### Breaking Changes

- **Changed**: The `--output` flag now defaults to `json` instead of `text`.
  - **Why**: JSON output is more reliable for automated pipelines and prevents parsing errors with special characters.
  - **Migration**: If your scripts depend on text output, add `--output text` to your commands.
  - **Before**: `mytool export` (produced text output)
  - **After**: `mytool export --output text` (to get the same text output as before)

- **Removed**: The `/api/v1/users` endpoint has been removed after being deprecated in version 2.5.0.
  - **Why**: The v1 endpoint did not support pagination, causing performance issues with large user lists.
  - **Migration**: Replace all calls to `/api/v1/users` with `/api/v2/users`. The v2 endpoint returns paginated results by default (50 items per page). Add `?page=1&per_page=100` to control pagination.
  - **Before**: `GET /api/v1/users` (returned all users in a single response)
  - **After**: `GET /api/v2/users?per_page=100` (returns up to 100 users per page with pagination headers)
```

---

## 5. Keep a Changelog Format Specification

The "Keep a Changelog" format (from keepachangelog.com) is a widely adopted standard for changelog files. This section describes the required format.

### 5.1 Version Heading Format

Each version entry uses a level-2 markdown heading (`##`) with the version number and an optional title:

```markdown
## 2.8.0 - CSV Export and Stability Improvements
```

**Format rules:**
- Use `##` (level-2 heading), not `#` or `###`
- The version number comes first, without a `v` prefix (use `2.8.0` not `v2.8.0`), unless the project convention is to include the `v` prefix -- in that case, match the project convention consistently
- A hyphen separates the version from the optional title
- The title is a short (3-8 word) summary of the release theme
- Category sub-headings use `###` (level-3 heading)
- Separate entries from the previous version with a horizontal rule (`---`)

**Complete structure of a single version entry:**

```markdown
## X.Y.Z - Release Title

### Breaking Changes
- Description of breaking change with migration instructions

### New Features
- Description of new feature (#issue)

### Improvements
- Description of improvement

### Bug Fixes
- Description of fix (#issue)

---
```

### 5.2 Pre-Release Changelog Sections

For pre-release versions (alpha, beta, release candidates), use the standard semver pre-release suffix in the heading:

```markdown
## 3.0.0-beta.1 - First Beta of Version 3

### Breaking Changes
- [PREVIEW] Changed authentication from API keys to OAuth2.
  This change is being tested in beta and may be adjusted before stable release.

### New Features
- Added OAuth2 login flow (experimental)

---
```

**Rules for pre-release changelogs:**
- Mark experimental entries with `[PREVIEW]` or `[EXPERIMENTAL]` to signal they may change
- When the stable version is released, consolidate all pre-release entries into a single stable changelog entry
- Remove the `[PREVIEW]` markers from entries that are finalized in the stable release

---

## 6. Complete Minor Release Example

This example shows a complete changelog entry for a minor release that adds new features and fixes bugs:

```markdown
## 2.8.0 - CSV Export and Stability Improvements

### New Features
- Added CSV export endpoint at /api/v2/export for bulk data download (#45)
- Added configurable timeout for long-running API requests via the `request_timeout` setting (#52)

### Improvements
- Reduced dashboard loading time from 4.2 seconds to 1.1 seconds by implementing query result caching (#49)
- Improved error messages for authentication failures to include the specific OAuth2 error code (#55)

### Bug Fixes
- Fixed memory leak in the file processor that caused the server to run out of memory after processing approximately 10,000 files without restart (#48)
- Fixed incorrect currency formatting for Japanese Yen (was showing decimal places, JPY has none) (#51)
- Fixed file upload returning HTTP 200 success when the file was silently rejected due to exceeding the size limit (#53)

### Dependencies
- Updated the `requests` library from 2.28.0 to 2.31.0 to patch CVE-2023-32681 (#50)

---
```

---

## 7. Complete Breaking Change Example

This example shows a changelog entry for a major release with breaking changes and migration instructions:

```markdown
## 3.0.0 - Authentication Overhaul

### Breaking Changes
- **Changed**: Authentication now uses OAuth2 instead of API keys.
  - **Why**: API keys were transmitted in URL parameters, which are logged by web servers and proxies, creating a security risk.
  - **Migration**:
    1. Register your application at /settings/oauth to get a client ID and secret
    2. Replace `Authorization: ApiKey YOUR_KEY` header with `Authorization: Bearer YOUR_TOKEN`
    3. Implement the OAuth2 client credentials flow to obtain tokens (see /docs/auth for examples)
  - **Before**: `curl -H "Authorization: ApiKey abc123" https://api.example.com/data`
  - **After**: `curl -H "Authorization: Bearer eyJhbG..." https://api.example.com/data`

- **Removed**: The `--legacy-format` flag has been removed.
  - **Why**: The legacy format was deprecated in version 2.5.0 and has had zero usage in telemetry for 6 months.
  - **Migration**: Remove `--legacy-format` from your commands. The current format (introduced in 2.5.0) is now the only format.

- **Changed**: The default database connection pool size changed from 5 to 20.
  - **Why**: Most production deployments were manually increasing this value. The new default matches typical production needs.
  - **Migration**: If you are running in a memory-constrained environment, explicitly set `pool_size: 5` in your configuration file to restore the previous behavior.

### New Features
- Added OAuth2 authentication with support for client credentials and authorization code flows (#78)
- Added connection pool metrics endpoint at /api/v3/metrics/pool (#82)

### Bug Fixes
- Fixed rare deadlock when multiple clients request authentication tokens simultaneously (#80)

---
```

---

## 8. Changelog Review Checklist

Use this checklist when reviewing a changelog entry before approving a release:

```
FORMAT CHECKS:
- [ ] Version heading uses ## (level 2) markdown heading
- [ ] Version number matches the version in project configuration files
- [ ] Entry is at the TOP of the file (newest first)
- [ ] Categories use ### (level 3) headings
- [ ] Entry ends with a horizontal rule (---)
- [ ] No empty categories are included

CONTENT CHECKS:
- [ ] Every change description starts with a verb (Fixed, Added, Removed, etc.)
- [ ] Every change description is specific (names the component, trigger, and symptom)
- [ ] No vague entries like "Fixed bug" or "Various improvements"
- [ ] Related issue numbers are referenced using #N syntax
- [ ] External contributors are credited with @username
- [ ] Breaking changes include migration instructions with Before/After examples
- [ ] Security fixes reference the CVE number if applicable
- [ ] Quantifiable improvements include numbers (percentage, time, size)

COMPLETENESS CHECKS:
- [ ] All merged PRs since the last release are represented
- [ ] All resolved issues since the last release are represented
- [ ] No changes are missing from the entry
- [ ] Deprecation notices include the planned removal version
```

---

## See Also

- [release-coordination-procedure.md](release-coordination-procedure.md) -- The complete 5-step release process
- [workflow-checklists.md](workflow-checklists.md) -- General task delegation checklists
