# Templates for Human Communication - Part 4: Breaking Changes

## Contents

- 6.4 Breaking change communication
  - 6.4.1 Warning users in advance
  - 6.4.2 Deprecation notices
  - 6.4.3 Migration timeline

---

## 6.4 Breaking Change Communication

Breaking changes require extra care. Users need time to prepare.

### 6.4.1 Warning Users in Advance

Announce breaking changes at least one release before they happen.

**Timeline**:
1. **v2.3**: Deprecation warning added
2. **v2.4**: Feature still works, louder warnings
3. **v2.5**: Feature removed

**Announcement template**:
```markdown
## Upcoming Breaking Change: [Feature Name]

**Timeline**:
- v2.3 (current): Deprecation warnings added
- v2.4 (next month): Warnings become errors (can be disabled with flag)
- v2.5 (in 3 months): Feature removed entirely

**What's changing**:
[Clear description of the change]

**Why**:
[Reason for the change]

**What you need to do**:
[Step-by-step migration instructions]

**Need help?**:
[Link to migration guide, support channels]
```

### 6.4.2 Deprecation Notices

Deprecation notices should appear everywhere users might encounter the feature.

**Where to add notices**:
- Release notes
- API response headers
- Console warnings
- Documentation
- In-app UI (if applicable)

**Deprecation notice format**:
```
DEPRECATION WARNING: [Feature] is deprecated and will be removed in v[X].
Migrate to [alternative]. See: [migration-guide-url]
```

**Code example** (API header):
```
X-Deprecation-Warning: The /v1/users endpoint is deprecated.
Use /v2/users instead. Removal date: 2024-06-01.
See: https://docs.example.com/migration/v1-to-v2
```

### 6.4.3 Migration Timeline

Give users a realistic timeline with clear milestones.

**Template**:
```markdown
## Migration Timeline: [Old Feature] to [New Feature]

| Date | Version | What Happens |
|------|---------|--------------|
| [Date] | v2.3 | Deprecation warnings begin |
| [Date] | v2.4 | New feature available (opt-in) |
| [Date] | v2.5 | New feature is default, old feature opt-in |
| [Date] | v2.6 | Old feature removed |

### Recommended Migration Path

**Phase 1** (by [date]): Audit your usage
- [ ] Identify all uses of [old feature]
- [ ] Review migration guide

**Phase 2** (by [date]): Test new feature
- [ ] Enable new feature in staging
- [ ] Run integration tests
- [ ] Fix any issues

**Phase 3** (by [date]): Migrate production
- [ ] Enable new feature in production
- [ ] Monitor for issues
- [ ] Remove old feature usage
```

---

**Previous**: See [templates-for-humans-part3-release-notes.md](templates-for-humans-part3-release-notes.md) for release notes format.

**Next**: See [templates-for-humans-part5-migration-guides.md](templates-for-humans-part5-migration-guides.md) for migration guide structure.
