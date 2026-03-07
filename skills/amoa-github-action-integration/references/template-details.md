## Table of Contents

- [PR Review Workflow](#pr-review-workflow)
- [Mention Response Workflow](#mention-response-workflow)
- [Issue Triage Workflow](#issue-triage-workflow)

---

## PR Review Workflow

**File**: `templates/workflows/claude-pr-review.yml`

**Triggers**:
- Pull request opened
- New commits pushed to PR
- PR marked ready for review
- PR reopened

**Features**:
- Comprehensive code review (quality, bugs, security, performance)
- Inline comments on specific code issues
- Summary comment with overall assessment
- Concurrency control (one review per PR at a time)
- Draft PR handling (skips drafts)

**Review Categories**:
1. Code Quality - patterns, naming, organization, DRY
2. Potential Bugs - null handling, edge cases, race conditions
3. Security - injection, XSS, auth issues
4. Performance - complexity, queries, caching
5. Testing - coverage, edge cases, clarity

## Mention Response Workflow

**File**: `templates/workflows/claude-mention.yml`

**Triggers**:
- @claude mentioned in issue comment
- @claude mentioned in PR comment

**Features**:
- Responds to direct questions
- Provides code explanations
- Suggests fixes for reported issues
- Answers architecture questions

## Issue Triage Workflow

**File**: `templates/workflows/claude-issue-triage.yml`

**Triggers**:
- New issue opened

**Features**:
- Automatic label assignment
- Priority assessment
- Initial response to reporter
- Related issue linking
