# Agent Selection Guide - Part 1: Language-Specific Agents


## Contents

- [Use-Case Quick Reference for This Section](#use-case-quick-reference-for-this-section)
- [Agent Selection by Task Type](#agent-selection-by-task-type)
  - [Language-Specific Agents](#language-specific-agents)
    - [Python Projects](#python-projects)
    - [JavaScript/TypeScript Projects](#javascripttypescript-projects)
    - [Go Projects](#go-projects)
    - [Rust Projects](#rust-projects)
    - [Native Platform Development](#native-platform-development)
- [Language Selection Quick Reference](#language-selection-quick-reference)
- [Related Files](#related-files)

---

## Use-Case Quick Reference for This Section

**When to use this file:**
- When you need to select a developer agent for Python/JS/Go/Rust work
- When you need to select a test-writer agent for a specific language
- When you need to select a code-fixer agent for a specific language
- When working with native platform development (macOS, iOS, Windows, Android)

---

## Agent Selection by Task Type

### Language-Specific Agents

#### Python Projects

| Task Type | Agent Name | Key Tools | When to Use | Output Format |
|-----------|------------|-----------|-------------|---------------|
| Python CLI/Library Development | `python-developer` | uv, pytest, ruff, mypy, black | New Python projects, major refactoring | Minimal report + file paths |
| Python Tests | `python-test-writer` | pytest, coverage, hypothesis | Writing comprehensive test suites | Test count + coverage % |
| Python Code Quality | `python-code-fixer` | ruff, mypy, black, isort | After editing Python files, pre-commit | Issues fixed count |
| Python Data Science | `data-scientist` | pandas, numpy, scikit-learn, jupyter | Statistical analysis, ML modeling | Analysis summary + results file |

**Python Agent Selection Rules:**
- Use `python-developer` for implementation tasks
- Use `python-test-writer` when test coverage < 80% or adding new features
- ALWAYS use `python-code-fixer` after editing Python files
- Use `data-scientist` for any statistical or ML work

---

#### JavaScript/TypeScript Projects

| Task Type | Agent Name | Key Tools | When to Use | Output Format |
|-----------|------------|-----------|-------------|---------------|
| JS/TS Development | `js-developer` | pnpm, vitest, eslint, tsc, prettier | Node.js, web apps, libraries | Minimal report + file paths |
| JS/TS Tests | `js-test-writer` | vitest, jest, playwright | Writing JS/TS test suites | Test count + coverage % |
| JS/TS Code Quality | `js-code-fixer` | eslint, prettier, tsc | After editing JS/TS files, pre-commit | Issues fixed count |
| React/Vue Development | `frontend-developer` | vite, react, vue, tailwind | Frontend UI components | Component count + status |

**JavaScript/TypeScript Agent Selection Rules:**
- Use `js-developer` for implementation tasks
- Use `js-test-writer` when adding new features or coverage < 80%
- ALWAYS use `js-code-fixer` after editing JS/TS files
- Use `frontend-developer` for UI-specific work

---

#### Go Projects

| Task Type | Agent Name | Key Tools | When to Use | Output Format |
|-----------|------------|-----------|-------------|---------------|
| Go CLI/Service | `go-developer` | go build, go test, golangci-lint | Go services, CLIs, libraries | Minimal report + file paths |
| Go Tests | `go-test-writer` | go test, testify, gomock | Writing Go test suites | Test count + coverage % |
| Go Code Quality | `go-code-fixer` | golangci-lint, gofmt, goimports | After editing Go files, pre-commit | Issues fixed count |

**Go Agent Selection Rules:**
- Use `go-developer` for implementation tasks
- Use `go-test-writer` when adding new features
- ALWAYS use `go-code-fixer` after editing Go files

---

#### Rust Projects

| Task Type | Agent Name | Key Tools | When to Use | Output Format |
|-----------|------------|-----------|-------------|---------------|
| Rust CLI/Library | `rust-developer` | cargo, clippy, rustfmt | Rust projects, performance-critical code | Minimal report + file paths |
| Rust Tests | `rust-test-writer` | cargo test, proptest | Writing Rust test suites | Test count + coverage % |
| Rust Code Quality | `rust-code-fixer` | clippy, rustfmt | After editing Rust files, pre-commit | Issues fixed count |

**Rust Agent Selection Rules:**
- Use `rust-developer` for implementation tasks
- Use `rust-test-writer` when adding new features
- ALWAYS use `rust-code-fixer` after editing Rust files

---

#### Native Platform Development

| Platform | Agent Name | Key Tools | When to Use | Output Format |
|----------|------------|-----------|-------------|---------------|
| macOS | `macos-developer` | xcodebuild, swift, swiftlint | macOS native apps, frameworks | Build status + artifact paths |
| iOS | `ios-developer` | xcodebuild, swift, swiftlint, swiftformat | iOS apps, frameworks | Build status + artifact paths |
| Windows | `windows-developer` | msbuild, dotnet, visual studio | Windows native apps, services | Build status + artifact paths |
| Android | `android-developer` | gradle, kotlin, android studio | Android apps, libraries | Build status + artifact paths |

**Native Platform Agent Selection Rules:**
- Use platform-specific agents for native development
- Never mix platform agents in same task
- Always specify target OS version

---

## Language Selection Quick Reference

```
Language?
├── Python → python-* agents
├── JavaScript/TypeScript → js-* agents
├── Go → go-* agents
├── Rust → rust-* agents
├── Swift (macOS/iOS) → macos-developer / ios-developer
├── Kotlin (Android) → android-developer
├── C# (Windows) → windows-developer
└── Multiple → Separate agents per language
```

---

## Related Files

- [Part 2: Specialized Agents](./agent-selection-guide-part2-specialized-agents.md) - Code quality, search, testing, DevOps agents
- [Part 3: Decision & Selection](./agent-selection-guide-part3-decision-selection.md) - Decision tree and selection checklist
- [Part 4: Patterns & Practices](./agent-selection-guide-part4-patterns-practices.md) - Anti-patterns and best practices
- [Part 5: Advanced Topics](./agent-selection-guide-part5-advanced.md) - Advanced topics and troubleshooting
- [Index](./agent-selection-guide.md) - Main overview and quick reference
