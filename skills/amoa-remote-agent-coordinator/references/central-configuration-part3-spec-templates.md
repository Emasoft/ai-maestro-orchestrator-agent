# Central Configuration - Part 3: Specification Templates


## Contents

- [Table of Contents](#table-of-contents)
- [`decisions.md` Template](#decisionsmd-template)
- [ADR-001: Use `uv` for Python Package Management](#adr-001-use-uv-for-python-package-management)
  - [Context](#context)
  - [Decision](#decision)
  - [Rationale](#rationale)
  - [Consequences](#consequences)
  - [Alternatives Considered](#alternatives-considered)
- [ADR-002: FAIL-FAST Error Handling](#adr-002-fail-fast-error-handling)
  - [Context](#context)
  - [Decision](#decision)
  - [Rationale](#rationale)
  - [Consequences](#consequences)
- [ADR-NNN: (Template for New Decision)](#adr-nnn-template-for-new-decision)
  - [Context](#context)
  - [Decision](#decision)
  - [Rationale](#rationale)
  - [Consequences](#consequences)
  - [Alternatives Considered](#alternatives-considered)
- [`requirements.md` Template](#requirementsmd-template)
- [Core Features](#core-features)
  - [Feature: User Authentication](#feature-user-authentication)
  - [Feature: (Template)](#feature-template)
- [`architecture.md` Template](#architecturemd-template)
- [System Overview](#system-overview)
- [Architecture Diagram](#architecture-diagram)
- [Components](#components)
  - [Component: Web API](#component-web-api)
  - [Component: (Template)](#component-template)
- [Data Flow](#data-flow)
- [Deployment Architecture](#deployment-architecture)
- [`interfaces.md` Template](#interfacesmd-template)
- [REST API Endpoints](#rest-api-endpoints)
  - [POST /api/auth/login](#post-apiauthlogin)
- [Function Signatures](#function-signatures)
  - [Module: `auth.service`](#module-authservice)
    - [`authenticate_user()`](#authenticate_user)
- [Database Schema](#database-schema)
  - [Table: `users`](#table-users)
- [Message Contracts](#message-contracts)
  - [Message Type: `task-completion`](#message-type-task-completion)
- [Related Parts](#related-parts)

---

## Table of Contents

1. [If you need to create decisions.md (ADRs)](#decisionsmd-template)
2. [If you need to create requirements.md](#requirementsmd-template)
3. [If you need to create architecture.md](#architecturemd-template)
4. [If you need to create interfaces.md](#interfacesmd-template)

---

## `decisions.md` Template

```markdown
# Architecture Decision Records (ADRs)

**Format**: Each decision is numbered and dated with rationale.

---

## ADR-001: Use `uv` for Python Package Management

**Date**: 2025-12-31
**Status**: Accepted
**Decided By**: orchestrator-master

### Context

Python package management needs to be fast, reliable, and support virtual environments.

### Decision

Use `uv` as the primary package manager for Python projects.

### Rationale

- Faster than pip
- Built-in virtual environment support
- Compatible with existing pip workflows
- Modern tool actively maintained

### Consequences

**Positive**:
- Faster dependency installation
- Consistent environment management
- Future-proof tooling

**Negative**:
- Team must learn new tool
- Some CI systems may need updates

### Alternatives Considered

- **pip**: Standard but slower
- **poetry**: More opinionated, heavier
- **pipenv**: Slower, less active

---

## ADR-002: FAIL-FAST Error Handling

**Date**: 2025-12-31
**Status**: Accepted
**Decided By**: orchestrator-master

### Context

Error handling strategy needed for codebase consistency.

### Decision

Adopt FAIL-FAST principle: no error swallowing, no fallbacks, let errors propagate.

### Rationale

- Errors surface immediately during development
- No hidden bugs in production
- Clearer debugging
- Forces proper error handling at boundaries

### Consequences

**Positive**:
- Bugs caught early
- Clear failure points
- No mysterious "it sometimes works" issues

**Negative**:
- May require more explicit error boundaries
- Less forgiving during development

---

## ADR-NNN: (Template for New Decision)

**Date**: YYYY-MM-DD
**Status**: Proposed|Accepted|Rejected|Deprecated
**Decided By**: <agent-id or user>

### Context

What is the issue that we're seeing that is motivating this decision or change?

### Decision

What is the change that we're proposing and/or doing?

### Rationale

Why are we making this decision?

### Consequences

**Positive**:
- Benefit 1
- Benefit 2

**Negative**:
- Drawback 1
- Drawback 2

### Alternatives Considered

- **Alternative 1**: Why rejected
- **Alternative 2**: Why rejected
```

---

## `requirements.md` Template

```markdown
# Functional Requirements

**Last Updated**: 2025-12-31 03:48:23
**Updated By**: orchestrator-master

## Core Features

### Feature: User Authentication

**Priority**: High
**Status**: Planned
**Issue**: GH-101

**Description**: Users must be able to log in with email and password.

**Acceptance Criteria**:
- [ ] User can register with email and password
- [ ] User can log in with valid credentials
- [ ] User sees error message for invalid credentials
- [ ] User session persists across page reloads
- [ ] User can log out

**Non-Functional Requirements**:
- Password must be hashed with bcrypt
- Session token must expire after 24 hours
- Login attempt rate limited to 5/minute

---

### Feature: (Template)

**Priority**: Low|Medium|High|Critical
**Status**: Planned|In Progress|Completed|Blocked
**Issue**: GH-NNN

**Description**: What the feature does.

**Acceptance Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2

**Non-Functional Requirements**:
- Performance requirement
- Security requirement
- Scalability requirement
```

---

## `architecture.md` Template

```markdown
# System Architecture

**Last Updated**: 2025-12-31 03:48:23
**Updated By**: orchestrator-master

## System Overview

High-level description of the system and its purpose.

## Architecture Diagram

(ASCII art or reference to diagram file)

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│   Frontend  │─────▶│   Backend    │─────▶│   Database   │
└─────────────┘      └──────────────┘      └──────────────┘
```

## Components

### Component: Web API

**Responsibility**: Handle HTTP requests and responses

**Technology**: FastAPI

**Interfaces**:
- REST API endpoints (see `interfaces.md`)
- Database queries via SQLAlchemy

**Dependencies**:
- Database component
- Authentication service

---

### Component: (Template)

**Responsibility**: What this component does

**Technology**: What tools/frameworks it uses

**Interfaces**:
- Interface 1
- Interface 2

**Dependencies**:
- Dependency 1
- Dependency 2

## Data Flow

1. User sends HTTP request
2. API validates request
3. Service processes business logic
4. Database stores/retrieves data
5. Response returned to user

## Deployment Architecture

(If applicable)

- Development environment
- Staging environment
- Production environment
```

---

## `interfaces.md` Template

```markdown
# API Contracts and Interfaces

**Last Updated**: 2025-12-31 03:48:23
**Updated By**: orchestrator-master

## REST API Endpoints

### POST /api/auth/login

**Description**: Authenticate user and create session

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response** (200 OK):
```json
{
  "token": "jwt-token-here",
  "user": {
    "id": 123,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Response** (401 Unauthorized):
```json
{
  "error": "Invalid credentials"
}
```

---

## Function Signatures

### Module: `auth.service`

#### `authenticate_user()`

```python
def authenticate_user(email: str, password: str) -> User | None:
    """Authenticate user with email and password.

    Args:
        email: User's email address
        password: Plain text password (will be hashed)

    Returns:
        User object if authentication successful, None otherwise

    Raises:
        ValueError: If email or password is empty
    """
```

---

## Database Schema

### Table: `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | User ID |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Email address |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt hash |
| created_at | TIMESTAMP | NOT NULL | Registration time |

---

## Message Contracts

(For inter-agent communication)

### Message Type: `task-completion`

```json
{
  "type": "task-completion",
  "task_id": "GH-101",
  "status": "success|failed|blocked",
  "pr_url": "https://github.com/owner/repo/pull/42",
  "test_results": "All 15 tests passed",
  "notes": "No issues encountered"
}
```
```

---

## Related Parts

- **Part 1**: [Overview and Structure](central-configuration-part1-overview-structure.md) - Why config matters, directory layout
- **Part 2**: [Tooling Templates](central-configuration-part2-tooling-templates.md) - toolchain.md, standards.md, environment.md templates
- **Part 4**: [Workflows and Protocols](central-configuration-part4-workflows-protocols.md) - Reference-based sharing, update protocols, troubleshooting
