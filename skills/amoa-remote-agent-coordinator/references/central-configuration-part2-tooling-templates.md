# Central Configuration - Part 2: Tooling Templates


## Contents

- [Table of Contents](#table-of-contents)
- [`toolchain.md` Template](#toolchainmd-template)
- [Python Environment](#python-environment)
  - [Commands](#commands)
- [Code Formatting](#code-formatting)
- [Testing Framework](#testing-framework)
  - [Test Execution](#test-execution)
- [Git Workflow](#git-workflow)
  - [Commit Convention](#commit-convention)
- [Build System](#build-system)
- [`standards.md` Template](#standardsmd-template)
- [Python Code Standards](#python-code-standards)
  - [Naming Conventions](#naming-conventions)
  - [Documentation Requirements](#documentation-requirements)
  - [Type Hints](#type-hints)
  - [Error Handling](#error-handling)
  - [Testing Requirements](#testing-requirements)
- [TypeScript/JavaScript Standards](#typescriptjavascript-standards)
  - [Naming Conventions](#naming-conventions)
  - [Linting](#linting)
- [File Organization](#file-organization)
  - [Module Structure](#module-structure)
  - [Import Order](#import-order)
- [Prohibited Patterns](#prohibited-patterns)
- [`environment.md` Template](#environmentmd-template)
- [Required Environment Variables](#required-environment-variables)
  - [Git Configuration](#git-configuration)
  - [AI Maestro Configuration](#ai-maestro-configuration)
  - [Project-Specific Variables](#project-specific-variables)
- [Environment File Location](#environment-file-location)
  - [Loading Environment](#loading-environment)
- [CI/CD Environment](#cicd-environment)
  - [GitHub Actions Secrets](#github-actions-secrets)
  - [GitHub Actions Variables](#github-actions-variables)
- [Related Parts](#related-parts)

---

## Table of Contents

1. [If you need to create toolchain.md](#toolchainmd-template)
2. [If you need to create standards.md](#standardsmd-template)
3. [If you need to create environment.md](#environmentmd-template)

---

## `toolchain.md` Template

```markdown
# Toolchain Configuration

**Last Updated**: 2025-12-31 03:48:23
**Updated By**: orchestrator-master
**Change Summary**: Initial configuration

## Python Environment

**Version**: 3.12
**Package Manager**: uv
**Virtual Environment**: .venv

### Commands
```bash
# Create venv
uv venv --python 3.12

# Activate venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Run script
uv run script.py
```

## Code Formatting

**Tool**: ruff
**Line Length**: 88 (DO NOT CHANGE)
**Command**: `uv run ruff format --line-length=88 src/ tests/`

## Testing Framework

**Framework**: pytest
**Coverage Tool**: pytest-cov
**Minimum Coverage**: 80%

### Test Execution
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_module.py::test_function
```

## Git Workflow

**Branch Strategy**: feature-branch workflow
**Main Branch**: main
**Feature Branch Format**: feature/GH-{issue-number}-{short-description}

### Commit Convention
```
type(scope): description

- detail 1
- detail 2

Issue: GH-{number}
```

**Types**: feat, fix, docs, refactor, test, chore

## Build System

**Tool**: (none|setuptools|poetry|etc.)
**Build Command**: (if applicable)
**Distribution**: (if applicable)
```

---

## `standards.md` Template

```markdown
# Code Standards and Conventions

**Last Updated**: 2025-12-31 03:48:23
**Updated By**: orchestrator-master
**Change Summary**: Initial standards

## Python Code Standards

### Naming Conventions

- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private Methods**: `_leading_underscore`
- **Modules**: `snake_case.py`

### Documentation Requirements

**Every Function Must Have**:
```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """One-line summary of function purpose.

    Detailed description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ExceptionType: When this exception is raised
    """
```

**Every Class Must Have**:
- Docstring explaining purpose
- Attribute documentation
- Usage example

### Type Hints

**REQUIRED** for:
- All function signatures
- All class attributes
- All module-level variables

### Error Handling

**FAIL-FAST Principle**:
- NO try/except blocks that swallow errors
- NO fallback values
- NO workarounds
- Let exceptions propagate

### Testing Requirements

**Test Coverage**:
- Minimum 80% line coverage
- 100% coverage for critical paths
- Edge cases documented

**Test Structure**:
```python
def test_function_description():
    """Test that function does X when Y condition occurs."""
    # Arrange
    input_data = create_test_input()

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_output
```

## TypeScript/JavaScript Standards

(If applicable to project)

### Naming Conventions

- **Functions**: `camelCase`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Interfaces**: `PascalCase` with `I` prefix or no prefix

### Linting

**Tool**: ESLint
**Config**: .eslintrc.json
**Command**: `pnpm run lint`

## File Organization

### Module Structure

```
src/
├── module_name/
│   ├── __init__.py          # Public API exports
│   ├── core.py              # Core implementation
│   ├── utils.py             # Helper functions
│   └── types.py             # Type definitions
tests/
├── test_module_name/
│   ├── test_core.py
│   └── test_utils.py
```

### Import Order

1. Standard library
2. Third-party packages
3. Local modules

Separated by blank lines.

## Prohibited Patterns

**NEVER DO**:
- Backward compatibility code
- Commented-out code
- Multiple versions of same function
- Workarounds or bypasses
- Mock tests (use real services)
- Scripts for editing code (use Edit tool)
```

---

## `environment.md` Template

```markdown
# Environment Variables Specification

**Last Updated**: 2025-12-31 03:48:23
**Updated By**: orchestrator-master
**Change Summary**: Initial environment spec

## Required Environment Variables

### Git Configuration

```bash
export GIT_AUTHOR="Emasoft"
export GIT_AUTHOR_EMAIL="713559+Emasoft@users.noreply.github.com"
export GIT_COMMITTER="Emasoft"
export GIT_COMMITTER_EMAIL="713559+Emasoft@users.noreply.github.com"
export GITHUB_OWNER="Emasoft"
export GITHUB_PROFILE="https://github.com/Emasoft"
```

### AI Maestro Configuration

AI Maestro AMP handles routing automatically. Use the `agent-messaging` skill to send and receive messages.

```bash
# Agent session identification
export AIMAESTRO_AGENT="<session-name>"
export AIMAESTRO_POLL_INTERVAL="10"
```

### Project-Specific Variables

(Add project-specific environment variables here)

## Environment File Location

**File**: `.env` (gitignored)
**Template**: `.env.example` (committed to repo)

### Loading Environment

```bash
# Source environment
source .env

# Verify variables
echo $GIT_AUTHOR
echo $AIMAESTRO_AGENT
```

## CI/CD Environment

(If applicable)

### GitHub Actions Secrets

- `GITHUB_TOKEN` - Automatically provided
- (Add other secrets as needed)

### GitHub Actions Variables

- (Add environment-specific variables)
```

---

## Related Parts

- **Part 1**: [Overview and Structure](central-configuration-part1-overview-structure.md) - Why config matters, directory layout
- **Part 3**: [Spec Templates](central-configuration-part3-spec-templates.md) - decisions.md, requirements.md, architecture.md, interfaces.md templates
- **Part 4**: [Workflows and Protocols](central-configuration-part4-workflows-protocols.md) - Reference-based sharing, update protocols, troubleshooting
