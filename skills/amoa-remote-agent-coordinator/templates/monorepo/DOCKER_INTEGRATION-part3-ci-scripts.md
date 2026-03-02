# Docker Integration - Part 3: CI and Scripts

This document contains CI/CD workflows, .dockerignore, build scripts, and best practices.

**Parent document:** [DOCKER_INTEGRATION.md](./DOCKER_INTEGRATION.md)

---

## CI Docker Builds

### Build and Push Workflow

```yaml
# .github/workflows/docker-build.yml
name: Docker Build

on:
  push:
    branches: [main, develop]
    tags:
      - 'v*'
  pull_request:
    paths:
      - 'docker/**'
      - '**/Dockerfile'

env:
  REGISTRY: ghcr.io
  IMAGE_PREFIX: ${{ github.repository }}

jobs:
  build-rust:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}-rust-api
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          file: docker/rust.Dockerfile
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64,linux/arm64

  build-nodejs:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}-nodejs-web
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=sha

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          file: docker/nodejs.Dockerfile
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  build-python:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}-python-worker
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=sha

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          file: docker/python.Dockerfile
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

---

## .dockerignore Template

```
# .dockerignore
# Exclude files from Docker build context

# Version control
.git/
.gitignore
.gitattributes

# CI/CD
.github/
.gitlab-ci.yml

# Documentation
*.md
docs/
LICENSE

# Build artifacts
**/target/
**/dist/
**/build/
**/.next/
**/__pycache__/
**/*.pyc
**/.pytest_cache/
**/node_modules/
**/.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Environment
.env
.env.local
**/.env*

# Testing
coverage/
**/*.test.ts
**/*.spec.ts
**/tests/

# Docker
docker-compose*.yml
Dockerfile*
.dockerignore
```

---

## Build Scripts

### Build All Images

```bash
#!/bin/bash
# scripts/docker-build-all.sh
# Build all Docker images for {{MONOREPO_NAME}}
# Task: {{TASK_ID}}

set -e

log_info() { echo -e "\033[0;32m[INFO]\033[0m $*"; }

VERSION=${VERSION:-latest}
REGISTRY=${DOCKER_REGISTRY:-ghcr.io}
NAMESPACE=${DOCKER_NAMESPACE:-{{GITHUB_OWNER}}}

log_info "Building all Docker images (version: $VERSION)..."

# Build Rust API
log_info "Building Rust API..."
docker build \
  -f docker/rust.Dockerfile \
  -t $REGISTRY/$NAMESPACE/{{MONOREPO_NAME}}-rust-api:$VERSION \
  .

# Build Node.js Web
log_info "Building Node.js Web..."
docker build \
  -f docker/nodejs.Dockerfile \
  -t $REGISTRY/$NAMESPACE/{{MONOREPO_NAME}}-nodejs-web:$VERSION \
  .

# Build Python Worker
log_info "Building Python Worker..."
docker build \
  -f docker/python.Dockerfile \
  -t $REGISTRY/$NAMESPACE/{{MONOREPO_NAME}}-python-worker:$VERSION \
  .

log_info "All images built successfully!"
```

### Push All Images

```bash
#!/bin/bash
# scripts/docker-push-all.sh
# Push all Docker images to registry
# Task: {{TASK_ID}}

set -e

log_info() { echo -e "\033[0;32m[INFO]\033[0m $*"; }

VERSION=${VERSION:-latest}
REGISTRY=${DOCKER_REGISTRY:-ghcr.io}
NAMESPACE=${DOCKER_NAMESPACE:-{{GITHUB_OWNER}}}

log_info "Pushing all Docker images (version: $VERSION)..."

# Push Rust API
log_info "Pushing Rust API..."
docker push $REGISTRY/$NAMESPACE/{{MONOREPO_NAME}}-rust-api:$VERSION

# Push Node.js Web
log_info "Pushing Node.js Web..."
docker push $REGISTRY/$NAMESPACE/{{MONOREPO_NAME}}-nodejs-web:$VERSION

# Push Python Worker
log_info "Pushing Python Worker..."
docker push $REGISTRY/$NAMESPACE/{{MONOREPO_NAME}}-python-worker:$VERSION

log_info "All images pushed successfully!"
```

---

## Verification Checklist

```markdown
## Docker Integration Verification

### Dockerfiles
- [ ] Multi-stage builds for all languages
- [ ] Non-root user in final stage
- [ ] Minimal base images (slim/alpine)
- [ ] Health checks defined (production)

### Docker Compose
- [ ] All services defined
- [ ] Volume mounts for development
- [ ] Environment variables configured
- [ ] Service dependencies declared
- [ ] Ports exposed correctly

### CI/CD
- [ ] Build workflow for each service
- [ ] Push to container registry
- [ ] Multi-platform builds (amd64, arm64)
- [ ] Build cache configured

### Development Experience
- [ ] Hot reload works: `docker-compose up`
- [ ] Can attach debugger
- [ ] Logs accessible: `docker-compose logs -f`
- [ ] Can run individual services

### Production Readiness
- [ ] Images tagged with version
- [ ] Health checks pass
- [ ] Secrets not baked into images
- [ ] Resource limits defined
```

---

## Error Recovery

| Error | Cause | Fix |
|-------|-------|-----|
| Build context too large | Including node_modules/target | Add to .dockerignore |
| Permission denied | Running as root | Use non-root user in Dockerfile |
| Volume mount not updating | Cache issue on macOS | Use `:cached` mount option |
| Can't connect to service | Wrong network | Use service name, not localhost |
| Out of disk space | Too many layers/images | `docker system prune -a` |
| Build fails on arm64 | Platform mismatch | Add `--platform linux/amd64` |

---

## Best Practices

### DO
- Use multi-stage builds to reduce image size
- Run containers as non-root user
- Use named volumes for dependencies
- Pin base image versions
- Add health checks for services

### DON'T
- Include secrets in Dockerfiles
- Use `latest` tag in production
- Copy entire repo into image
- Run as root user
- Skip .dockerignore

---

## Template Metadata

```yaml
template:
  name: DOCKER_INTEGRATION
  version: 1.0.0
  eoa_compatible: true
  parent_template: MONOREPO_BASE
  requires:
    - MONOREPO_BASE
    - Docker
    - docker-compose
  generates:
    - Dockerfiles per language
    - docker-compose.yml
    - .dockerignore
    - build scripts
    - CI workflows
  note: |
    Containerized testing EXCLUDED - case-by-case basis only.
    Docker usage is optional and project-specific.
```

---

**Previous:** [Part 2: Docker Compose](./DOCKER_INTEGRATION-part2-compose.md)
