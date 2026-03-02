# Docker Integration - Part 2: Docker Compose

This document contains Docker Compose configurations for development and production environments.

**Parent document:** [DOCKER_INTEGRATION.md](./DOCKER_INTEGRATION.md)

---

## Docker Compose for Development

```yaml
# docker-compose.yml
# Development environment for {{MONOREPO_NAME}}
# Task: {{TASK_ID}}

services:
  # Rust API service
  rust-api:
    build:
      context: .
      dockerfile: docker/rust.Dockerfile
      target: builder  # Use builder stage for faster rebuilds
    volumes:
      - ./{{RUST_WORKSPACE}}:/app:cached
      - rust-cargo-cache:/usr/local/cargo/registry
      - rust-target-cache:/app/target
    environment:
      - RUST_LOG=debug
      - DATABASE_URL=postgres://postgres:postgres@postgres:5432/db
    ports:
      - "8080:8080"
    depends_on:
      - postgres
    command: cargo watch -x run

  # Node.js web service
  nodejs-web:
    build:
      context: .
      dockerfile: docker/nodejs.Dockerfile
      target: deps  # Use deps stage for development
    volumes:
      - ./{{JS_WORKSPACE}}:/app:cached
      - nodejs-node-modules:/app/node_modules
    environment:
      - NODE_ENV=development
      - API_URL=http://rust-api:8080
    ports:
      - "3000:3000"
    depends_on:
      - rust-api
    command: pnpm run dev

  # Python worker service
  python-worker:
    build:
      context: .
      dockerfile: docker/python.Dockerfile
      target: builder
    volumes:
      - ./{{PYTHON_WORKSPACE}}:/app:cached
      - python-venv-cache:/app/.venv
    environment:
      - PYTHONUNBUFFERED=1
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    command: uv run python -m worker

  # PostgreSQL database
  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=db
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # Redis cache
  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"

volumes:
  rust-cargo-cache:
  rust-target-cache:
  nodejs-node-modules:
  python-venv-cache:
  postgres-data:
  redis-data:
```

---

## Docker Compose for Production

```yaml
# docker-compose.prod.yml
# Production environment for {{MONOREPO_NAME}}
# Task: {{TASK_ID}}

services:
  rust-api:
    image: {{DOCKER_REGISTRY}}/{{DOCKER_NAMESPACE}}/{{MONOREPO_NAME}}-rust-api:${VERSION:-latest}
    restart: unless-stopped
    environment:
      - RUST_LOG=info
      - DATABASE_URL=${DATABASE_URL}
    ports:
      - "8080:8080"
    depends_on:
      - postgres
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nodejs-web:
    image: {{DOCKER_REGISTRY}}/{{DOCKER_NAMESPACE}}/{{MONOREPO_NAME}}-nodejs-web:${VERSION:-latest}
    restart: unless-stopped
    environment:
      - NODE_ENV=production
      - API_URL=http://rust-api:8080
    ports:
      - "3000:3000"
    depends_on:
      - rust-api
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  python-worker:
    image: {{DOCKER_REGISTRY}}/{{DOCKER_NAMESPACE}}/{{MONOREPO_NAME}}-python-worker:${VERSION:-latest}
    restart: unless-stopped
    environment:
      - PYTHONUNBUFFERED=1
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - postgres-data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis-data:/data

volumes:
  postgres-data:
  redis-data:
```

---

## Volume Mounts for Development

### Hot Reload Configuration

**Rust (cargo-watch):**
```yaml
volumes:
  - ./{{RUST_WORKSPACE}}:/app:cached
  - rust-cargo-cache:/usr/local/cargo/registry
  - rust-target-cache:/app/target
command: cargo watch -x run
```

**Node.js (Vite/Next.js):**
```yaml
volumes:
  - ./{{JS_WORKSPACE}}:/app:cached
  - nodejs-node-modules:/app/node_modules
command: pnpm run dev
```

**Python (watchfiles):**
```yaml
volumes:
  - ./{{PYTHON_WORKSPACE}}:/app:cached
  - python-venv-cache:/app/.venv
command: uv run watchfiles 'python -m app' src/
```

### Volume Mount Best Practices

- Use `:cached` on macOS for better performance
- Mount source directories read-write for hot reload
- Use named volumes for dependencies (node_modules, target/, .venv)
- Exclude build artifacts from host mount

---

## Development vs Production Comparison

| Aspect | Development | Production |
|--------|-------------|------------|
| Build target | `builder` stage | Final stage |
| Volumes | Source mounted | No mounts |
| Command | Watch/dev mode | Production CMD |
| Restart policy | None | `unless-stopped` |
| Health checks | Optional | Required |
| Logging | Debug level | Info level |
| Images | Local build | Registry pull |

---

## Common Development Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Restart single service
docker-compose restart rust-api

# Rebuild and restart
docker-compose up -d --build rust-api

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

**Previous:** [Part 1: Dockerfiles](./DOCKER_INTEGRATION-part1-dockerfiles.md)
**Next:** [Part 3: CI and Scripts](./DOCKER_INTEGRATION-part3-ci-scripts.md)
