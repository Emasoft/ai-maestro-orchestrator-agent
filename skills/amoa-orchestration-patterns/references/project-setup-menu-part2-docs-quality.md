# Project Setup Menu - Part 2: Documentation & Quality Requirements


## Contents

- [Table of Contents](#table-of-contents)
- [Documentation Strategy](#documentation-strategy)
  - [Question 10: Continuous Documentation](#question-10-continuous-documentation)
  - [Question 11: Deferred Documentation](#question-11-deferred-documentation)
- [Quality Requirements](#quality-requirements)
  - [Question 12: Test Coverage Target](#question-12-test-coverage-target)
  - [Question 13: Linting Strictness](#question-13-linting-strictness)

---

## Table of Contents

- [Documentation Strategy](#documentation-strategy)
  - [Question 10: Continuous Documentation](#question-10-continuous-documentation)
  - [Question 11: Deferred Documentation](#question-11-deferred-documentation)
- [Quality Requirements](#quality-requirements)
  - [Question 12: Test Coverage Target](#question-12-test-coverage-target)
  - [Question 13: Linting Strictness](#question-13-linting-strictness)

**Related Documents:**
- [Part 1: Team, Repository & Release Configuration](project-setup-menu-part1-team-repo-release.md)
- [Part 3: Implementation & Troubleshooting](project-setup-menu-part3-implementation-troubleshooting.md)

---

## Documentation Strategy

### Question 10: Continuous Documentation
**Prompt to User:**
```
Should documentation be automatically generated and deployed as part of CI/CD?

Continuous documentation means:
- Docstrings/JSDoc/comments are parsed automatically
- API documentation is regenerated on every commit to main
- Documentation site is deployed (GitHub Pages, ReadTheDocs, etc.)
- Broken docstrings fail CI checks

Options:
1. Yes - Full automation
   - Tool: Sphinx / MkDocs / JSDoc / rustdoc / godoc / etc.
   - Hosting: GitHub Pages / ReadTheDocs / Netlify / Vercel
   - Trigger: Every push to main / Every release tag

2. Partial - Generate locally, manual deploy
   - Generate docs on demand
   - Commit to docs/ folder in repo

3. No - Deferred until project matures
   - Just maintain good inline comments
   - Build documentation infrastructure later

If yes, which documentation tool?
- Python: Sphinx, MkDocs, pdoc
- JavaScript: JSDoc, TypeDoc, Docusaurus
- Rust: rustdoc
- Go: godoc
- Multi-language: Doxygen

Documentation hosting preference: _______
```

**Why This Matters:**
- Affects CI/CD pipeline complexity
- Determines docstring enforcement level
- Influences onboarding experience
- Impacts API discoverability

**Storage Key:** `docs.continuous`
**Format:**
```json
{
  "enabled": true,
  "tool": "sphinx" | "mkdocs" | "jsdoc" | "rustdoc",
  "hosting": "github-pages" | "readthedocs" | "netlify",
  "trigger": "push_to_main" | "release_tag",
  "fail_on_warnings": true
}
```

---

### Question 11: Deferred Documentation
**Prompt to User:**
```
If continuous documentation is NOT enabled, what's the inline documentation standard?

Requirements:
1. Comment density
   - Every public function/method must have docstring? (Yes/No)
   - Every class must have docstring? (Yes/No)
   - Every module must have header comment? (Yes/No)

2. Comment format
   - Python: Google style / NumPy style / reStructuredText
   - JavaScript: JSDoc with type annotations
   - Rust: Triple-slash comments (///)
   - Go: Godoc format

3. Enforcement
   - Linter checks for missing docstrings? (Yes/No)
   - CI fails if public API lacks documentation? (Yes/No)

4. Future documentation plan
   - When will full documentation site be built?
   - What triggers the transition? (Milestone, version, feature complete)
```

**Why This Matters:**
- Ensures code maintainability even without auto-generated docs
- Prevents technical debt accumulation
- Enables future documentation generation
- Improves code review quality

**Storage Key:** `docs.deferred`
**Format:**
```json
{
  "standards": {
    "require_function_docstrings": true,
    "require_class_docstrings": true,
    "require_module_headers": true,
    "format": "google" | "numpy" | "jsdoc"
  },
  "enforcement": {
    "linter_checks": true,
    "ci_fails_on_missing": false
  },
  "future_plan": "Build full docs at version 1.0.0"
}
```

---

## Quality Requirements

### Question 12: Test Coverage Target
**Prompt to User:**
```
What is the minimum acceptable test coverage percentage?

Industry standards:
- 80%+ = Excellent (recommended for libraries/frameworks)
- 70-79% = Good (common for applications)
- 60-69% = Acceptable (early-stage projects)
- <60% = Needs improvement

Your target: _____%

Coverage enforcement:
1. Strict - CI fails if coverage drops below target
2. Warning - CI warns but doesn't fail
3. Informational - Coverage reported but not enforced
4. Trend-based - Coverage must not decrease from baseline

Coverage scope:
- [ ] Line coverage
- [ ] Branch coverage
- [ ] Function coverage
- [ ] Statement coverage

Exclusions (files/patterns to exclude from coverage):
- test files themselves
- __init__.py / index.js
- generated code
- third-party integrations
- other: _______
```

**Why This Matters:**
- Determines if PRs can be merged with failing tests
- Affects test writing expectations
- Influences refactoring safety
- Impacts regression prevention

**Storage Key:** `quality.coverage`
**Format:**
```json
{
  "target_percentage": 80,
  "enforcement": "strict" | "warning" | "informational",
  "scope": ["line", "branch", "function"],
  "exclusions": ["tests/*", "__init__.py", "*/generated/*"]
}
```

---

### Question 13: Linting Strictness
**Prompt to User:**
```
How strict should linting and code quality checks be?

Linting levels:
1. Strict - Zero warnings allowed
   - All linter errors must be fixed
   - All warnings must be fixed
   - No disabled rules allowed
   - CI fails on any linting issue

2. Standard - Errors block merge, warnings don't
   - Errors must be fixed
   - Warnings are informational
   - Selective rule disabling allowed with comments
   - CI fails on errors only

3. Relaxed - Informational only
   - Linting results reported but don't block
   - Developers fix issues at discretion
   - CI never fails on linting

Linters to enable:
Python:
- [ ] Ruff (fast, comprehensive)
- [ ] Pylint (thorough, slower)
- [ ] Mypy (type checking)
- [ ] Black (formatting - always run)

JavaScript/TypeScript:
- [ ] ESLint (linting)
- [ ] Prettier (formatting)
- [ ] TypeScript compiler (strict mode)

Rust:
- [ ] Clippy (linting)
- [ ] Rustfmt (formatting)

Go:
- [ ] golangci-lint
- [ ] gofmt

Auto-fix on commit:
- Should linters auto-fix issues on commit? (Yes/No)
- Should formatters run automatically on commit? (Yes/No - recommended: Yes)
```

**Why This Matters:**
- Affects code review focus (style vs logic)
- Determines CI failure frequency
- Influences development velocity
- Impacts codebase consistency

**Storage Key:** `quality.linting`
**Format:**
```json
{
  "strictness": "strict" | "standard" | "relaxed",
  "linters": {
    "python": ["ruff", "mypy", "black"],
    "javascript": ["eslint", "prettier"]
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
```

---

**Previous:** [Part 1: Team, Repository & Release Configuration](project-setup-menu-part1-team-repo-release.md)

**Continue to:** [Part 3: Implementation & Troubleshooting](project-setup-menu-part3-implementation-troubleshooting.md)
