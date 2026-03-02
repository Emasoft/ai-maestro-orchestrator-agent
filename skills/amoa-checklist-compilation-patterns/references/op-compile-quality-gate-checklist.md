---
procedure: support-skill
workflow-instruction: support
---

# Operation: Compile Quality Gate Checklist


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Determine Gate Type](#step-1-determine-gate-type)
  - [Step 2: Create Test Section](#step-2-create-test-section)
- [Tests](#tests)
  - [Step 3: Create Coverage Section](#step-3-create-coverage-section)
- [Code Coverage](#code-coverage)
  - [Step 4: Create Static Analysis Section](#step-4-create-static-analysis-section)
- [Static Analysis](#static-analysis)
  - [Step 5: Create Security Section](#step-5-create-security-section)
- [Security](#security)
  - [Step 6: Create Performance Section (if applicable)](#step-6-create-performance-section-if-applicable)
- [Performance](#performance)
  - [Step 7: Create Verification Loop Section](#step-7-create-verification-loop-section)
- [Verification Loops](#verification-loops)
  - [Step 8: Add RULE 14 Compliance Section](#step-8-add-rule-14-compliance-section)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
  - [Step 9: Assemble Complete Checklist](#step-9-assemble-complete-checklist)
- [Tests](#tests)
- [Code Coverage](#code-coverage)
- [Static Analysis](#static-analysis)
- [Security](#security)
- [Performance](#performance)
- [Verification Loops](#verification-loops)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example](#example)
- [Tests](#tests)
- [Code Coverage](#code-coverage)
- [Static Analysis](#static-analysis)
- [Security](#security)
- [Verification Loops](#verification-loops)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
- [Checklist](#checklist)

## When to Use

Use this operation when you need to create a checklist that verifies quality standards before code progression (merge, release, deployment).

## Prerequisites

- Quality standards defined for the project
- CI/CD pipeline configuration understood
- Code quality tools identified (linters, type checkers, security scanners)

## Procedure

### Step 1: Determine Gate Type

| Gate Type | When Used |
|-----------|-----------|
| Pre-Commit | Before local commit |
| Pre-Merge | Before PR merge |
| Pre-Release | Before version release |
| Pre-Deploy | Before production deployment |

### Step 2: Create Test Section

```markdown
## Tests
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] No skipped tests without justification
- [ ] Test execution time within limits (<5 min)
```

### Step 3: Create Coverage Section

```markdown
## Code Coverage
- [ ] Overall coverage >= 80%
- [ ] New code coverage >= 90%
- [ ] Critical paths 100% covered
- [ ] No coverage regressions
```

### Step 4: Create Static Analysis Section

```markdown
## Static Analysis
- [ ] No linting errors (ruff/eslint)
- [ ] No linting warnings on new code
- [ ] Type checks pass (mypy/tsc)
- [ ] Complexity within limits (cyclomatic < 10)
```

### Step 5: Create Security Section

```markdown
## Security
- [ ] Security scan clean (no high/critical)
- [ ] Dependency vulnerabilities addressed
- [ ] No secrets in code
- [ ] No SQL injection vectors
- [ ] Input sanitization verified
```

### Step 6: Create Performance Section (if applicable)

```markdown
## Performance
- [ ] No performance regressions
- [ ] Memory usage within limits
- [ ] Load tests passing
- [ ] Database queries optimized
```

### Step 7: Create Verification Loop Section

```markdown
## Verification Loops
- [ ] Loop 1: Initial verification complete
- [ ] Loop 2: Post-fix verification complete
- [ ] Loop 3: Edge case verification complete
- [ ] Loop 4: Final verification complete
```

### Step 8: Add RULE 14 Compliance Section

```markdown
## Requirement Compliance (RULE 14)
- [ ] USER_REQUIREMENTS.md exists and is current
- [ ] All user requirements addressed
- [ ] No technology substitutions without approval
- [ ] No scope reductions without approval
```

### Step 9: Assemble Complete Checklist

```markdown
# Quality Gate: <gate-name>

**Generated**: <timestamp>
**Gate Type**: <Pre-Merge|Pre-Release|etc>
**Target**: <branch/version/environment>

## Tests
[items from Step 2]

## Code Coverage
[items from Step 3]

## Static Analysis
[items from Step 4]

## Security
[items from Step 5]

## Performance
[items from Step 6 if applicable]

## Verification Loops
[items from Step 7]

## Requirement Compliance (RULE 14)
[items from Step 8]

---
**Pass Criteria**: ALL items must be checked for gate to pass.
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| Checklist | Markdown | Complete quality gate checklist |
| Gate Type | String | Type of quality gate |
| Pass Criteria | String | Requirements to pass the gate |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Standards undefined | No quality policy | Define minimum standards first |
| Tools not configured | Missing CI/CD setup | Configure quality tools |
| Conflicting requirements | Multiple stakeholders | Prioritize and document decisions |

## Example

```markdown
# Quality Gate: Pre-Merge

**Generated**: 2024-01-15T14:00:00Z
**Gate Type**: Pre-Merge
**Target**: feature/auth-module -> main

## Tests
- [ ] All 47 unit tests passing
- [ ] All 12 integration tests passing
- [ ] No skipped tests
- [ ] Test suite completes in < 3 min

## Code Coverage
- [ ] Overall coverage >= 80% (current: 83%)
- [ ] auth-core module >= 85%
- [ ] No files below 70%
- [ ] No coverage decrease from main

## Static Analysis
- [ ] ruff check passes (0 errors)
- [ ] mypy passes (strict mode)
- [ ] No TODO comments
- [ ] Cyclomatic complexity < 10 per function

## Security
- [ ] bandit scan: 0 high, 0 medium
- [ ] pip-audit: 0 vulnerabilities
- [ ] No hardcoded credentials
- [ ] CORS properly configured

## Verification Loops
- [ ] Loop 1: All tests pass on clean checkout
- [ ] Loop 2: Tests pass after addressing review comments
- [ ] Loop 3: Edge cases verified manually
- [ ] Loop 4: Final CI run green

## Requirement Compliance (RULE 14)
- [ ] USER_REQUIREMENTS.md verified
- [ ] All auth requirements implemented
- [ ] Using approved libraries only
- [ ] Full feature set as specified
```

## Checklist

- [ ] Determine gate type (pre-merge/pre-release/etc)
- [ ] Create test verification items
- [ ] Create coverage verification items
- [ ] Create static analysis items
- [ ] Create security verification items
- [ ] Create performance items (if applicable)
- [ ] Add 4 verification loop items
- [ ] Add RULE 14 compliance section
- [ ] Define pass criteria
- [ ] Write to project docs or CI config
