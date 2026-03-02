# Docker Integration Template for Monorepo

This template defines Docker integration for monorepo projects, including Dockerfiles per language, docker-compose for multi-service development, CI docker builds, and volume mounts.

**IMPORTANT:** Containerized testing is EXCLUDED from this template. Docker usage is case-by-case and determined per project requirements, not a standard practice.

---

## Document Structure

This template is split into multiple parts for easier navigation:

| Part | File | Contents |
|------|------|----------|
| **Part 1** | [DOCKER_INTEGRATION-part1-dockerfiles.md](./DOCKER_INTEGRATION-part1-dockerfiles.md) | Template variables, directory structure, Dockerfile templates (Rust, Node.js, Python) |
| **Part 2** | [DOCKER_INTEGRATION-part2-compose.md](./DOCKER_INTEGRATION-part2-compose.md) | Docker Compose for development and production, volume mounts, hot reload |
| **Part 3** | [DOCKER_INTEGRATION-part3-ci-scripts.md](./DOCKER_INTEGRATION-part3-ci-scripts.md) | CI/CD workflows, .dockerignore, build scripts, verification checklist, best practices |

---

## Quick Reference

### Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{MONOREPO_NAME}}` | Monorepo project name | `xls-platform` |
| `{{DOCKER_REGISTRY}}` | Container registry | `ghcr.io`, `docker.io` |
| `{{DOCKER_NAMESPACE}}` | Registry namespace | `{{GITHUB_OWNER}}` |
| `{{RUST_WORKSPACE}}` | Rust workspace path | `rust-workspace/` |
| `{{JS_WORKSPACE}}` | JS workspace path | `js-workspace/` |
| `{{PYTHON_WORKSPACE}}` | Python workspace path | `python-workspace/` |
| `{{SERVICE_NAME}}` | Service name | `api`, `web`, `cli` |
| `{{PORT}}` | Service port | `3000`, `8080` |
| `{{TASK_ID}}` | Associated task ID | `GH-42` |

### Docker Directory Structure

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

## Part Contents Overview

### Part 1: Dockerfile Templates
- Template variables reference
- Docker directory structure
- **Rust Dockerfile** - Multi-stage build with cargo
- **Node.js Dockerfile** - Multi-stage build with pnpm
- **Python Dockerfile** - Multi-stage build with uv
- Key Dockerfile patterns and security practices

### Part 2: Docker Compose
- **Development environment** - Full docker-compose.yml with hot reload
- **Production environment** - docker-compose.prod.yml with health checks
- **Volume mounts** - Hot reload configuration per language
- Volume mount best practices
- Development vs production comparison

### Part 3: CI and Scripts
- **CI workflow** - GitHub Actions for building and pushing images
- **.dockerignore** - Complete template for excluding files
- **Build scripts** - docker-build-all.sh and docker-push-all.sh
- **Verification checklist** - Pre-deployment checks
- **Error recovery** - Common issues and fixes
- **Best practices** - DO and DON'T guidelines

---

## Quick Start

1. **Set up Dockerfiles**: See [Part 1](./DOCKER_INTEGRATION-part1-dockerfiles.md)
2. **Configure Compose**: See [Part 2](./DOCKER_INTEGRATION-part2-compose.md)
3. **Set up CI/CD**: See [Part 3](./DOCKER_INTEGRATION-part3-ci-scripts.md)

### Common Commands

```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f

# Rebuild single service
docker-compose up -d --build rust-api

# Build all images
./scripts/docker-build-all.sh

# Push to registry
./scripts/docker-push-all.sh
```

---

## Verification Checklist Summary

### Dockerfiles
- [ ] Multi-stage builds for all languages
- [ ] Non-root user in final stage
- [ ] Minimal base images (slim/alpine)

### Docker Compose
- [ ] All services defined
- [ ] Volume mounts for development
- [ ] Service dependencies declared

### CI/CD
- [ ] Build workflow for each service
- [ ] Multi-platform builds (amd64, arm64)
- [ ] Build cache configured

### Production
- [ ] Health checks pass
- [ ] Secrets not baked into images
- [ ] Resource limits defined

---

## Error Recovery Quick Reference

| Error | Fix |
|-------|-----|
| Build context too large | Add to .dockerignore |
| Permission denied | Use non-root user in Dockerfile |
| Volume mount not updating | Use `:cached` mount option |
| Can't connect to service | Use service name, not localhost |
| Out of disk space | `docker system prune -a` |

---

## Best Practices Summary

### DO
- Use multi-stage builds
- Run as non-root user
- Use named volumes for dependencies
- Pin base image versions
- Add health checks

### DON'T
- Include secrets in Dockerfiles
- Use `latest` tag in production
- Copy entire repo into image
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
  parts:
    - DOCKER_INTEGRATION-part1-dockerfiles.md
    - DOCKER_INTEGRATION-part2-compose.md
    - DOCKER_INTEGRATION-part3-ci-scripts.md
```
