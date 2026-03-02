# Templates for Human Communication - Part 3: Release Notes

## Contents

- 6.3 Release notes format
  - 6.3.1 User-facing language
  - 6.3.2 Grouping by type
  - 6.3.3 Linking to issues and PRs

---

## 6.3 Release Notes Format

Release notes are for *users*, not developers. Write in their language.

### 6.3.1 User-Facing Language

Translate technical changes into benefits.

**Developer language** (wrong for release notes):
```
Refactored the authentication middleware to use JWT RS256 instead of HS256
```

**User language** (right for release notes):
```
Improved security for user authentication with enhanced token encryption
```

**Translation examples**:
| Technical | User-facing |
|-----------|-------------|
| "Fixed null pointer exception in profile handler" | "Fixed a bug where some user profiles wouldn't load" |
| "Migrated from REST to GraphQL" | "New: More flexible data querying (see API docs)" |
| "Reduced bundle size by 40%" | "App loads faster, especially on slow connections" |
| "Added Redis caching layer" | "Improved performance for frequently accessed data" |

### 6.3.2 Grouping by Type

Organize changes so users can quickly find what matters to them.

**Template**:
```markdown
# Release Notes - v[X.Y.Z]

Released: [Date]

## Highlights
[1-3 most important changes, explained for users]

## New Features
- [Feature]: [User benefit]

## Improvements
- [Improvement]: [User benefit]

## Bug Fixes
- Fixed: [What was broken]

## Breaking Changes
- [Change]: [What users need to do]

## Deprecations
- [Feature]: Will be removed in v[X]. Use [alternative] instead.

## Security
- [Security fix]: [What was addressed, no exploit details]
```

**Example**:
```markdown
# Release Notes - v2.4.0

Released: January 15, 2024

## Highlights
- **Two-factor authentication**: Secure your account with TOTP-based 2FA
- **50% faster exports**: Large data exports now complete in half the time
- **Dark mode**: Finally! Enable in Settings > Appearance

## New Features
- Two-factor authentication (Settings > Security)
- Dark mode support across all screens
- Export to CSV in addition to existing Excel format

## Improvements
- Export performance improved by 50% for large datasets
- Search now includes archived items (toggle in search options)
- Mobile app startup time reduced by 2 seconds

## Bug Fixes
- Fixed: Charts not rendering in Safari 17
- Fixed: Password reset emails sometimes not sending
- Fixed: Timezone display incorrect for users in UTC+13/14

## Breaking Changes
- API v1 endpoints removed (deprecated since v2.0). Migrate to v2 API.

## Security
- Addressed potential session fixation vulnerability (CVE-2024-XXXX)
```

### 6.3.3 Linking to Issues and PRs

Connect release notes to detailed information for those who want it.

**Template**:
```markdown
- [Feature description] ([#PR](link)) - Thanks @contributor!
```

**Example**:
```markdown
## New Features
- Two-factor authentication ([#456](https://github.com/org/repo/pull/456))
- Dark mode support ([#423](https://github.com/org/repo/pull/423)) - Thanks @community-contributor!

## Bug Fixes
- Fixed: Charts not rendering in Safari 17 ([#489](https://github.com/org/repo/issues/489))
```

---

**Previous**: See [templates-for-humans-part2-commit-messages.md](templates-for-humans-part2-commit-messages.md) for commit message guidelines.

**Next**: See [templates-for-humans-part4-breaking-changes.md](templates-for-humans-part4-breaking-changes.md) for breaking change communication.
