# Docker Integration - Part 1: Dockerfile Templates

This document contains Dockerfile templates for multi-language monorepos.

**Parent document:** [DOCKER_INTEGRATION.md](./DOCKER_INTEGRATION.md)

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{MONOREPO_NAME}}` | Monorepo project name | `xls-platform` |
| `{{DOCKER_REGISTRY}}` | Container registry | `ghcr.io`, `docker.io` |
| `{{DOCKER_NAMESPACE}}` | Registry namespace | `{{GITHUB_OWNER}}`, `mycompany` |
| `{{RUST_WORKSPACE}}` | Rust workspace path | `rust-workspace/` |
| `{{JS_WORKSPACE}}` | JS workspace path | `js-workspace/` |
| `{{PYTHON_WORKSPACE}}` | Python workspace path | `python-workspace/` |
| `{{SERVICE_NAME}}` | Service name | `api`, `web`, `cli` |
| `{{PORT}}` | Service port | `3000`, `8080` |
| `{{TASK_ID}}` | Associated task ID | `GH-42` |

---

## Docker Directory Structure

```
{{MONOREPO_NAME}}/
├── docker/
│   ├── rust.Dockerfile            # Rust service image
│   ├── nodejs.Dockerfile          # Node.js service image
│   ├── python.Dockerfile          # Python service image
│   └── nginx.Dockerfile           # Static file server (optional)
├── docker-compose.yml             # Development environment
├── docker-compose.prod.yml        # Production environment
├── .dockerignore                  # Exclude files from context
└── scripts/
    ├── docker-build-all.sh        # Build all images
    └── docker-push-all.sh         # Push all images
```

---

## Dockerfile Templates

### Rust Dockerfile (Multi-stage)

```dockerfile
# docker/rust.Dockerfile
# Multi-stage build for Rust applications
# Task: {{TASK_ID}}

# ============================================================
# Stage 1: Builder
# ============================================================
FROM rust:{{RUST_VERSION}}-slim AS builder

WORKDIR /build

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy workspace manifest
COPY {{RUST_WORKSPACE}}/Cargo.toml {{RUST_WORKSPACE}}/Cargo.lock ./

# Copy all packages
COPY {{RUST_WORKSPACE}}/packages ./packages
COPY {{RUST_WORKSPACE}}/apps ./apps

# Build release binary
RUN cargo build --release --bin {{SERVICE_NAME}}

# ============================================================
# Stage 2: Runtime
# ============================================================
FROM debian:bookworm-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy binary from builder
COPY --from=builder /build/target/release/{{SERVICE_NAME}} /app/{{SERVICE_NAME}}

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE {{PORT}}

CMD ["/app/{{SERVICE_NAME}}"]
```

### Node.js Dockerfile (Multi-stage with pnpm)

```dockerfile
# docker/nodejs.Dockerfile
# Multi-stage build for Node.js applications
# Task: {{TASK_ID}}

# ============================================================
# Stage 1: Dependencies
# ============================================================
FROM node:{{NODE_VERSION}}-slim AS deps

WORKDIR /app

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy workspace configuration
COPY {{JS_WORKSPACE}}/package.json {{JS_WORKSPACE}}/pnpm-lock.yaml {{JS_WORKSPACE}}/pnpm-workspace.yaml ./

# Copy all package manifests
COPY {{JS_WORKSPACE}}/packages/*/package.json ./packages/
COPY {{JS_WORKSPACE}}/apps/*/package.json ./apps/

# Install dependencies
RUN pnpm install --frozen-lockfile --prod=false

# ============================================================
# Stage 2: Builder
# ============================================================
FROM node:{{NODE_VERSION}}-slim AS builder

WORKDIR /app

RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/package.json /app/pnpm-lock.yaml /app/pnpm-workspace.yaml ./

# Copy source code
COPY {{JS_WORKSPACE}}/packages ./packages
COPY {{JS_WORKSPACE}}/apps ./apps
COPY {{JS_WORKSPACE}}/tsconfig.*.json ./

# Build
RUN pnpm run build --filter={{SERVICE_NAME}}

# ============================================================
# Stage 3: Runtime
# ============================================================
FROM node:{{NODE_VERSION}}-slim

WORKDIR /app

RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy built artifacts
COPY --from=builder /app/apps/{{SERVICE_NAME}}/dist ./dist
COPY --from=builder /app/apps/{{SERVICE_NAME}}/package.json ./

# Install production dependencies only
RUN pnpm install --prod --frozen-lockfile

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE {{PORT}}

CMD ["node", "dist/index.js"]
```

### Python Dockerfile (Multi-stage with uv)

```dockerfile
# docker/python.Dockerfile
# Multi-stage build for Python applications
# Task: {{TASK_ID}}

# ============================================================
# Stage 1: Builder
# ============================================================
FROM python:{{PYTHON_VERSION}}-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy project files
COPY {{PYTHON_WORKSPACE}}/pyproject.toml {{PYTHON_WORKSPACE}}/uv.lock ./
COPY {{PYTHON_WORKSPACE}}/packages ./packages
COPY {{PYTHON_WORKSPACE}}/apps/{{SERVICE_NAME}} ./apps/{{SERVICE_NAME}}

# Install dependencies and build
RUN uv sync --frozen
RUN uv build

# ============================================================
# Stage 2: Runtime
# ============================================================
FROM python:{{PYTHON_VERSION}}-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy built wheel and install
COPY --from=builder /app/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

# Copy application code
COPY --from=builder /app/apps/{{SERVICE_NAME}} /app/{{SERVICE_NAME}}

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE {{PORT}}

CMD ["python", "-m", "{{SERVICE_NAME}}"]
```

---

## Key Dockerfile Patterns

### Multi-stage Build Benefits

1. **Smaller images**: Final image contains only runtime dependencies
2. **Faster builds**: Layer caching between stages
3. **Security**: Build tools not in production image
4. **Reproducibility**: Same build process locally and in CI

### Security Best Practices

- Run as non-root user (`appuser`)
- Use minimal base images (`slim`, `alpine`)
- Remove package manager caches
- Pin base image versions

---

**Next:** [Part 2: Docker Compose](./DOCKER_INTEGRATION-part2-compose.md)
