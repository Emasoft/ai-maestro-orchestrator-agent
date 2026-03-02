---
procedure: support-skill
workflow-instruction: support
---

# Operation: Compile Release Readiness Checklist


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Create Feature Completion Section](#step-1-create-feature-completion-section)
- [Feature Completion](#feature-completion)
  - [Step 2: Create Quality Verification Section](#step-2-create-quality-verification-section)
- [Quality Verification](#quality-verification)
  - [Step 3: Create Documentation Section](#step-3-create-documentation-section)
- [Documentation](#documentation)
  - [Step 4: Create Versioning Section](#step-4-create-versioning-section)
- [Versioning](#versioning)
  - [Step 5: Create Deployment Section](#step-5-create-deployment-section)
- [Deployment Readiness](#deployment-readiness)
  - [Step 6: Create Communication Section](#step-6-create-communication-section)
- [Communication](#communication)
  - [Step 7: Add RULE 14 Compliance Section](#step-7-add-rule-14-compliance-section)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
  - [Step 8: Assemble Complete Checklist](#step-8-assemble-complete-checklist)
- [Feature Completion](#feature-completion)
- [Quality Verification](#quality-verification)
- [Documentation](#documentation)
- [Versioning](#versioning)
- [Deployment Readiness](#deployment-readiness)
- [Communication](#communication)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example](#example)
- [Feature Completion](#feature-completion)
- [Quality Verification](#quality-verification)
- [Documentation](#documentation)
- [Versioning](#versioning)
- [Deployment Readiness](#deployment-readiness)
- [Communication](#communication)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
- [Checklist](#checklist)

## When to Use

Use this operation when preparing a release and need to verify all release requirements are met.

## Prerequisites

- All features for release are complete
- Version number decided
- Release branch created or main branch ready
- Understanding of deployment process

## Procedure

### Step 1: Create Feature Completion Section

```markdown
## Feature Completion
- [ ] All planned features implemented
- [ ] All features pass acceptance tests
- [ ] No critical bugs remaining
- [ ] High-priority bugs addressed
- [ ] Feature freeze in effect
```

### Step 2: Create Quality Verification Section

```markdown
## Quality Verification
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] All E2E tests passing
- [ ] Performance benchmarks met
- [ ] Security scan clean
- [ ] No linting errors
- [ ] Type checks pass
```

### Step 3: Create Documentation Section

```markdown
## Documentation
- [ ] CHANGELOG.md updated
- [ ] README.md current
- [ ] API documentation generated
- [ ] Migration guide (if breaking changes)
- [ ] Release notes drafted
- [ ] User documentation updated
```

### Step 4: Create Versioning Section

```markdown
## Versioning
- [ ] Version bumped in package files
- [ ] Version consistent across all files
- [ ] Git tag prepared
- [ ] Semantic versioning followed
- [ ] Dependency versions locked
```

### Step 5: Create Deployment Section

```markdown
## Deployment Readiness
- [ ] CI/CD pipeline green
- [ ] Staging deployment successful
- [ ] Smoke tests pass on staging
- [ ] Rollback procedure documented
- [ ] Rollback tested
- [ ] Infrastructure ready
```

### Step 6: Create Communication Section

```markdown
## Communication
- [ ] Release announcement drafted
- [ ] Stakeholders notified
- [ ] Support team briefed
- [ ] Known issues documented
- [ ] Breaking changes communicated
```

### Step 7: Add RULE 14 Compliance Section

```markdown
## Requirement Compliance (RULE 14)
- [ ] USER_REQUIREMENTS.md exists and is current
- [ ] All user requirements addressed
- [ ] No technology substitutions without approval
- [ ] No scope reductions without approval
```

### Step 8: Assemble Complete Checklist

```markdown
# Release Readiness Checklist: v<version>

**Generated**: <timestamp>
**Version**: <version>
**Release Date**: <target-date>
**Release Manager**: <name>

## Feature Completion
[items from Step 1]

## Quality Verification
[items from Step 2]

## Documentation
[items from Step 3]

## Versioning
[items from Step 4]

## Deployment Readiness
[items from Step 5]

## Communication
[items from Step 6]

## Requirement Compliance (RULE 14)
[items from Step 7]

---
**Release Approval**: [ ] APPROVED / [ ] BLOCKED
**Blocking Issues**: <list if any>
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| Checklist | Markdown | Complete release readiness checklist |
| Approval Status | String | APPROVED or BLOCKED |
| Blocking Issues | Array | Issues preventing release |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Features incomplete | Scope creep or delays | Defer features to next release |
| Tests failing | Regressions | Fix before release |
| Documentation outdated | Rushed development | Pause release for docs |
| Rollback untested | Skipped step | Test rollback in staging |

## Example

```markdown
# Release Readiness Checklist: v2.1.0

**Generated**: 2024-01-20T10:00:00Z
**Version**: 2.1.0
**Release Date**: 2024-01-22
**Release Manager**: orchestrator-master

## Feature Completion
- [x] Auth module implemented (#42)
- [x] API rate limiting added (#45)
- [x] Dashboard redesign complete (#48)
- [x] All acceptance tests passing
- [x] Critical bugs: 0, High: 0
- [x] Feature freeze since Jan 18

## Quality Verification
- [x] 247 unit tests passing
- [x] 34 integration tests passing
- [x] 12 E2E tests passing
- [x] Performance: <200ms p95 response
- [x] Security scan: 0 high/critical
- [x] Linting: 0 errors, 0 warnings
- [x] Type checks: strict mode pass

## Documentation
- [x] CHANGELOG.md updated
- [x] README.md current
- [x] API docs generated (OpenAPI)
- [x] Migration guide for auth changes
- [x] Release notes drafted
- [x] User docs updated

## Versioning
- [x] version in package.json: 2.1.0
- [x] version in pyproject.toml: 2.1.0
- [x] version in __init__.py: 2.1.0
- [x] Tag v2.1.0 prepared
- [x] SemVer: minor bump (new features)
- [x] Dependencies locked

## Deployment Readiness
- [x] CI pipeline green (all checks pass)
- [x] Staging deployed successfully
- [x] Staging smoke tests: 10/10 pass
- [x] Rollback procedure documented
- [x] Rollback tested on staging
- [x] Production infra ready

## Communication
- [x] Release notes in #announcements
- [x] Stakeholders email sent
- [x] Support team training scheduled
- [x] Known issues: JWT clock skew edge case
- [x] Breaking changes: none

## Requirement Compliance (RULE 14)
- [x] USER_REQUIREMENTS.md verified
- [x] All planned requirements met
- [x] Using approved tech stack
- [x] Full scope delivered

---
**Release Approval**: [x] APPROVED / [ ] BLOCKED
**Blocking Issues**: None
**Final Sign-off**: Pending user approval
```

## Checklist

- [ ] Verify all planned features complete
- [ ] Run full test suite
- [ ] Generate documentation
- [ ] Bump version numbers
- [ ] Prepare deployment
- [ ] Draft communications
- [ ] Add RULE 14 compliance section
- [ ] Get final approval
- [ ] Execute release
