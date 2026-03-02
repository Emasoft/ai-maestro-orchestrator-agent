# Docker Troubleshooting and Container Management

## Contents

### 1. Assessing Docker Container Needs for a Project
- 1.1 Identifying target platforms (Linux, Windows, macOS)
- 1.2 Determining container purpose (dev, testing, CI/CD, production)
- 1.3 Checking existing Docker configurations
- 1.4 Listing required dependencies and tools

### 2. Selecting Appropriate Base Images
- 2.1 Python base images (`python:3.12-slim`, `python:3.12-bookworm`)
- 2.2 Node.js base images (`node:22-slim`, `node:22-bookworm`)
- 2.3 Go base images (`golang:1.23-bookworm`)
- 2.4 Rust base images (`rust:1.83-bookworm`)
- 2.5 Multi-platform base images (`ubuntu:24.04`)

### 3. Applying Docker Best Practices
- 3.1 Using multi-stage builds to reduce image size
- 3.2 Pinning dependency versions for reproducibility
- 3.3 Using non-root users for security
- 3.4 Adding health checks to containers
- 3.5 Minimizing Docker layers

### 4. Configuring Multi-Service Environments
- 4.1 Specifying service architecture in docker-compose.yml
- 4.2 Documenting required environment variables
- 4.3 Setting up volume requirements for code mounting
- 4.4 Configuring resource limits
- 4.5 Implementing health check requirements

### 5. Troubleshooting Build Failures from Disk Space Issues
- 5.1 Checking Docker disk usage with `docker system df`
- 5.2 Removing unused data with `docker system prune`
- 5.3 Cleaning up unused volumes
- 5.4 Adjusting Docker Desktop disk limits

### 6. Fixing Network Access Problems in Containers
- 6.1 Verifying network configuration with `docker network ls`
- 6.2 Configuring DNS settings
- 6.3 Testing connectivity from containers
- 6.4 Restarting Docker daemon

### 7. Resolving Permission Denied Errors on Mounted Volumes
- 7.1 Identifying host user ID mismatches
- 7.2 Creating container users with matching UIDs
- 7.3 Building images with user ID arguments
- 7.4 Running containers as current user

### 8. Optimizing Slow Image Builds
- 8.1 Using `.dockerignore` to exclude unnecessary files
- 8.2 Ordering Dockerfile commands for cache efficiency
- 8.3 Separating dependency installation from source code copying
- 8.4 Enabling BuildKit for faster builds

### 9. Debugging Containers That Exit Immediately
- 9.1 Checking container logs
- 9.2 Running containers with interactive shell
- 9.3 Verifying CMD/ENTRYPOINT configuration
- 9.4 Keeping containers alive for debugging

### 10. Managing Environment Variables in Containers
- 10.1 Defining environment variables in Dockerfile
- 10.2 Passing variables at runtime
- 10.3 Using environment files
- 10.4 Verifying environment variables inside containers

---

## 1. Assessing Docker Container Needs for a Project

### 1.1 Identifying Target Platforms

**When to do this**: Before creating any Docker configuration

**Steps**:
1. Determine which platforms you need to support:
   - Linux (native Docker support)
   - Windows (via cross-compilation or Windows containers)
   - macOS (via cross-compilation)
2. Document platform requirements in your specification
3. Note any platform-specific dependencies or tools needed

**Verification**:
- [ ] All target platforms identified
- [ ] Platform-specific requirements documented

### 1.2 Determining Container Purpose

**When to do this**: At the start of Docker setup

**Container purposes**:
- **Development**: Hot-reload, debugging tools, all dev dependencies
- **Testing**: Isolated environment, test dependencies, CI/CD integration
- **CI/CD**: Minimal dependencies, fast builds, automated testing
- **Production**: Minimal attack surface, optimized performance, security hardened

**Steps**:
1. Identify the primary use case for the container
2. List required tools and dependencies for that purpose
3. Determine resource requirements (CPU, memory, disk)
4. Plan for monitoring and logging needs

**Verification**:
- [ ] Container purpose clearly defined
- [ ] Required tools and dependencies listed
- [ ] Resource requirements estimated

### 1.3 Checking Existing Docker Configurations

**When to do this**: Before creating new Docker files in a project

**Steps**:
1. Search for existing files:
   ```bash
   find . -name "Dockerfile*" -o -name "docker-compose*.yml"
   ```
2. Review existing configurations:
   - Check base images used
   - Note installed dependencies
   - Identify any multi-stage builds
   - Check for security issues (running as root, pinned versions)
3. Document what needs to be preserved or changed

**Verification**:
- [ ] Existing Docker files located and reviewed
- [ ] Dependencies and configurations documented
- [ ] Issues identified for improvement

### 1.4 Listing Required Dependencies and Tools

**When to do this**: During container specification

**Steps**:
1. List runtime dependencies:
   - Programming language runtimes (Python, Node.js, etc.)
   - System libraries
   - Database clients
2. List build dependencies:
   - Compilers (gcc, clang, etc.)
   - Build tools (make, cmake, ninja)
   - Package managers (apt, yum, pip, npm)
3. List development tools (if dev container):
   - Debuggers (gdb, pdb, etc.)
   - Linters and formatters
   - Version control tools (git)
4. Note any platform-specific dependencies

**Verification**:
- [ ] All runtime dependencies listed
- [ ] Build dependencies documented
- [ ] Dev tools included (if applicable)

---

## 2. Selecting Appropriate Base Images

### 2.1 Python Base Images

**When to use**: Python applications or services

**Recommended images**:
- `python:3.12-slim` - Minimal Debian-based image (~50MB)
- `python:3.12-bookworm` - Full Debian with build tools (~300MB)

**Example**:
```dockerfile
# Minimal production image
FROM python:3.12-slim-bookworm

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

**Choose slim when**:
- Production deployment with minimal dependencies
- Image size is critical
- No compilation required

**Choose bookworm when**:
- Development environment
- Need to compile C extensions
- Require system tools

### 2.2 Node.js Base Images

**When to use**: JavaScript/TypeScript applications

**Recommended images**:
- `node:22-slim` - Minimal Debian-based (~70MB)
- `node:22-bookworm` - Full Debian with build tools (~350MB)

**Example**:
```dockerfile
FROM node:22-slim

WORKDIR /app
COPY package*.json .
RUN npm ci --only=production
COPY . .
CMD ["node", "server.js"]
```

### 2.3 Go Base Images

**When to use**: Go applications

**Recommended images**:
- `golang:1.23-bookworm` - Full build environment
- `scratch` or `alpine` - For final production image (multi-stage)

**Example multi-stage**:
```dockerfile
FROM golang:1.23-bookworm AS builder
WORKDIR /build
COPY . .
RUN CGO_ENABLED=0 go build -o app

FROM alpine:latest
COPY --from=builder /build/app /app
CMD ["/app"]
```

### 2.4 Rust Base Images

**When to use**: Rust applications

**Recommended images**:
- `rust:1.83-bookworm` - Full build environment
- `debian:bookworm-slim` - For final production image

**Example**:
```dockerfile
FROM rust:1.83-bookworm AS builder
WORKDIR /build
COPY . .
RUN cargo build --release

FROM debian:bookworm-slim
COPY --from=builder /build/target/release/app /app
CMD ["/app"]
```

### 2.5 Multi-Platform Base Images

**When to use**: Cross-platform builds, multiple toolchains needed

**Recommended images**:
- `ubuntu:24.04` - Wide package availability, familiar environment

**Example**:
```dockerfile
FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    build-essential cmake ninja-build \
    gcc-mingw-w64-x86-64 \
    clang lld \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
CMD ["bash"]
```

---

## 3. Applying Docker Best Practices

### 3.1 Using Multi-Stage Builds to Reduce Image Size

**Why**: Separate build environment from runtime environment, reducing final image size by 60-90%

**When to use**: Any application that requires compilation or build steps

**Pattern**:
```dockerfile
# Stage 1: Build
FROM node:22-bookworm AS builder
WORKDIR /build
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:22-slim
WORKDIR /app
COPY --from=builder /build/dist ./dist
COPY --from=builder /build/node_modules ./node_modules
CMD ["node", "dist/server.js"]
```

**Benefits**:
- Smaller final image (only runtime dependencies)
- Faster deployment (less data to transfer)
- More secure (no build tools in production)

### 3.2 Pinning Dependency Versions for Reproducibility

**Why**: Prevent unexpected changes, ensure builds are reproducible months later

**Pattern**:
```dockerfile
# Bad - uses latest
FROM python:3.12

# Good - pinned version
FROM python:3.12.1-slim-bookworm

# Also pin system packages
RUN apt-get update && apt-get install -y \
    git=1:2.39.2-1.1 \
    curl=7.88.1-10+deb12u8
```

**Verification**:
- [ ] Base image uses specific version tag
- [ ] System packages specify versions
- [ ] Language packages use lock files (requirements.txt, package-lock.json, Cargo.lock)

### 3.3 Using Non-Root Users for Security

**Why**: Limit damage if container is compromised, follow principle of least privilege

**Pattern**:
```dockerfile
FROM python:3.12-slim

# Create non-root user
RUN useradd -m -s /bin/bash appuser

WORKDIR /app
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

CMD ["python", "app.py"]
```

**For development containers with volume mounts**:
```dockerfile
ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g ${GROUP_ID} developer && \
    useradd -m -u ${USER_ID} -g ${GROUP_ID} developer

USER developer
```

Build with: `docker build --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) -t myapp .`

### 3.4 Adding Health Checks to Containers

**Why**: Allow orchestrators (Docker, Kubernetes) to detect and restart unhealthy containers

**Pattern**:
```dockerfile
FROM python:3.12-slim

COPY app.py .

# HTTP service health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "app.py"]
```

**For services without HTTP endpoints**:
```dockerfile
# Database health check
HEALTHCHECK --interval=30s --timeout=5s \
  CMD pg_isready -U postgres || exit 1

# Process health check
HEALTHCHECK --interval=30s --timeout=5s \
  CMD pgrep -f "my-service" || exit 1
```

### 3.5 Minimizing Docker Layers

**Why**: Smaller images, faster builds, more efficient caching

**Bad pattern** (multiple layers):
```dockerfile
RUN apt-get update
RUN apt-get install -y git
RUN apt-get install -y curl
RUN apt-get install -y build-essential
RUN rm -rf /var/lib/apt/lists/*
```

**Good pattern** (single layer):
```dockerfile
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
```

**Benefits**:
- Fewer layers = smaller image
- Cleanup in same layer removes files completely
- Better caching efficiency

---

## 4. Configuring Multi-Service Environments

### 4.1 Specifying Service Architecture in docker-compose.yml

**When to use**: Multiple services needed (app + database + cache)

**Pattern**:
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    environment:
      DATABASE_URL: postgres://user:pass@db:5432/mydb
      REDIS_URL: redis://redis:6379

  db:
    image: postgres:16-bookworm
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 4.2 Documenting Required Environment Variables

**Pattern**:
Create `.env.example` file:
```bash
# Database Configuration
DATABASE_URL=postgres://user:password@localhost:5432/dbname
DATABASE_POOL_SIZE=10

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_MAX_CONNECTIONS=50

# Application Configuration
APP_ENV=development
APP_PORT=8000
LOG_LEVEL=info
```

**In docker-compose.yml**:
```yaml
services:
  app:
    env_file:
      - .env
    environment:
      # Override specific variables
      APP_PORT: 8000
```

### 4.3 Setting Up Volume Requirements for Code Mounting

**For development** (hot-reload):
```yaml
services:
  app:
    build: .
    volumes:
      # Mount source code for hot-reload
      - ./src:/app/src:ro
      - ./tests:/app/tests:ro
      # Named volume for dependencies (avoid host performance issues)
      - node_modules:/app/node_modules

volumes:
  node_modules:
```

**For production** (no mounts):
```yaml
services:
  app:
    image: myapp:latest
    # No volume mounts - code baked into image
```

### 4.4 Configuring Resource Limits

**Why**: Prevent runaway containers from consuming all host resources

**Pattern**:
```yaml
services:
  app:
    image: myapp:latest
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

**For development**:
```yaml
services:
  app:
    # More generous limits for dev
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 4G
```

### 4.5 Implementing Health Check Requirements

**Pattern in docker-compose.yml**:
```yaml
services:
  app:
    build: .
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
```

---

## 5. Troubleshooting Build Failures from Disk Space Issues

### 5.1 Checking Docker Disk Usage

**Symptom**: Build fails with "no space left on device"

**Command**:
```bash
docker system df
```

**Example output**:
```
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          45        10        15.2GB    12.8GB (84%)
Containers      20        5         2.5GB     2.1GB (84%)
Local Volumes   30        8         8.7GB     6.3GB (72%)
Build Cache     150       0         4.2GB     4.2GB (100%)
```

**Interpretation**:
- **RECLAIMABLE**: Space that can be freed by cleanup
- High reclaimable percentage = cleanup needed

### 5.2 Removing Unused Data

**Safe cleanup** (removes only unused data):
```bash
# Remove all stopped containers, unused networks, dangling images, build cache
docker system prune

# More aggressive - removes ALL unused images, not just dangling
docker system prune -a

# Non-interactive (no confirmation prompt)
docker system prune -a -f
```

**What gets removed**:
- All stopped containers
- All networks not used by at least one container
- All dangling images (not tagged, not referenced)
- All build cache
- With `-a`: All images not used by running containers

**What's preserved**:
- Running containers
- Images used by running containers
- Volumes (unless specifically pruned)

### 5.3 Cleaning Up Unused Volumes

**Warning**: This can delete data! Make sure volumes are truly unused.

**Command**:
```bash
# List volumes
docker volume ls

# Remove unused volumes
docker volume prune

# Remove specific volume
docker volume rm volume_name
```

**Safe approach**:
1. List volumes first
2. Check which containers use which volumes:
   ```bash
   docker ps -a --filter volume=volume_name
   ```
3. Only remove volumes not referenced by any container

### 5.4 Adjusting Docker Desktop Disk Limits

**For macOS/Windows Docker Desktop**:

**Steps**:
1. Open Docker Desktop
2. Go to Settings → Resources → Advanced
3. Increase "Disk image size" (default is often 64GB)
4. Click "Apply & Restart"

**For Linux**:
Docker uses host filesystem, no artificial limit. Check actual disk space:
```bash
df -h /var/lib/docker
```

If low on space, move Docker data directory:
```bash
sudo systemctl stop docker
sudo mv /var/lib/docker /new/path/docker
sudo ln -s /new/path/docker /var/lib/docker
sudo systemctl start docker
```

---

## 6. Fixing Network Access Problems in Containers

### 6.1 Verifying Network Configuration

**Symptom**: Container cannot reach external services or other containers

**Check available networks**:
```bash
docker network ls
```

**Expected output**:
```
NETWORK ID     NAME      DRIVER    SCOPE
abc123def456   bridge    bridge    local
def789ghi012   host      host      local
ghi345jkl678   none      null      local
```

**Check which network a container is using**:
```bash
docker inspect <container-id> | grep NetworkMode
```

**Connect container to network**:
```bash
docker network connect <network-name> <container-id>
```

### 6.2 Configuring DNS Settings

**Symptom**: Container cannot resolve domain names

**Test DNS resolution**:
```bash
docker run --rm alpine nslookup google.com
```

**If it fails, specify DNS servers**:
```bash
docker run --dns 8.8.8.8 --dns 8.8.4.4 --rm alpine nslookup google.com
```

**Make DNS persistent in docker-compose.yml**:
```yaml
services:
  app:
    image: myapp
    dns:
      - 8.8.8.8
      - 8.8.4.4
```

**Or in Dockerfile**:
```dockerfile
# /etc/docker/daemon.json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```

Then restart Docker daemon:
```bash
sudo systemctl restart docker
```

### 6.3 Testing Connectivity from Containers

**Test external connectivity**:
```bash
docker run --rm alpine ping -c 3 google.com
```

**Test container-to-container connectivity**:
```bash
# Start first container
docker run -d --name container1 --network mynetwork alpine sleep 1000

# Test from second container
docker run --rm --network mynetwork alpine ping -c 3 container1
```

**Check if firewall is blocking**:
```bash
# On Linux host
sudo iptables -L -n | grep DOCKER
```

### 6.4 Restarting Docker Daemon

**When to do**: After network configuration changes or persistent network issues

**Linux**:
```bash
sudo systemctl restart docker
```

**macOS/Windows Docker Desktop**:
- Click Docker icon in menu bar
- Select "Restart"

**Or from command line**:
```bash
docker restart $(docker ps -q)
```

---

## 7. Resolving Permission Denied Errors on Mounted Volumes

### 7.1 Identifying Host User ID Mismatches

**Symptom**: "Permission denied" when container tries to write to mounted volume

**Cause**: Container runs as user with UID 1000, host user has UID 1001

**Check host user ID**:
```bash
id -u
id -g
```

**Check container user ID**:
```bash
docker run --rm myimage id -u
```

**If they don't match**, files created by container won't be accessible to host user (and vice versa).

### 7.2 Creating Container Users with Matching UIDs

**In Dockerfile**:
```dockerfile
ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g ${GROUP_ID} developer && \
    useradd -m -u ${USER_ID} -g ${GROUP_ID} -s /bin/bash developer

USER developer
WORKDIR /home/developer
```

### 7.3 Building Images with User ID Arguments

**Build command**:
```bash
docker build \
  --build-arg USER_ID=$(id -u) \
  --build-arg GROUP_ID=$(id -g) \
  -t myapp:dev .
```

**In docker-compose.yml**:
```yaml
services:
  app:
    build:
      context: .
      args:
        USER_ID: ${USER_ID:-1000}
        GROUP_ID: ${GROUP_ID:-1000}
    volumes:
      - ./src:/app/src
```

**Run with**:
```bash
USER_ID=$(id -u) GROUP_ID=$(id -g) docker-compose up
```

### 7.4 Running Containers as Current User

**Alternative approach** (no Dockerfile changes needed):
```bash
docker run --user $(id -u):$(id -g) -v $(pwd):/app myimage
```

**In docker-compose.yml**:
```yaml
services:
  app:
    image: myimage
    user: "${UID}:${GID}"
    volumes:
      - ./src:/app/src
```

**Run with**:
```bash
UID=$(id -u) GID=$(id -g) docker-compose up
```

**Caveat**: Container user won't have a home directory or shell, may cause issues with some tools.

---

## 8. Optimizing Slow Image Builds

### 8.1 Using `.dockerignore` to Exclude Unnecessary Files

**Why**: Reduces context size sent to Docker daemon, speeds up builds

**Create `.dockerignore`** in same directory as Dockerfile:
```
# Version control
.git
.gitignore

# Dependencies (reinstalled in container)
node_modules
.venv
__pycache__

# IDE files
.vscode
.idea
*.swp

# Documentation
*.md
docs/

# Tests (unless needed)
tests/
*.test.js

# Build artifacts
dist/
build/
*.o
*.so

# Logs
*.log
logs/

# Environment files
.env
.env.local
```

**Verification**:
```bash
# Check what's being sent to Docker
docker build --no-cache -t test . 2>&1 | head -n 5
```

Look for "Sending build context" size - should be under 1MB for typical projects.

### 8.2 Ordering Dockerfile Commands for Cache Efficiency

**Principle**: Order instructions from least to most frequently changing

**Bad order** (cache breaks often):
```dockerfile
FROM python:3.12-slim
COPY . /app
RUN pip install -r requirements.txt
```

**Good order** (cache preserved):
```dockerfile
FROM python:3.12-slim

# Copy dependency files first (change rarely)
COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt

# Copy source code last (changes often)
COPY . /app
```

**Result**: Dependency installation cached, only source code copy and later steps re-run.

### 8.3 Separating Dependency Installation from Source Code Copying

**Pattern for Python**:
```dockerfile
FROM python:3.12-slim
WORKDIR /app

# Step 1: Install dependencies (cached)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 2: Copy source code (invalidates cache only from here)
COPY . .

CMD ["python", "app.py"]
```

**Pattern for Node.js**:
```dockerfile
FROM node:22-slim
WORKDIR /app

# Step 1: Install dependencies (cached)
COPY package*.json .
RUN npm ci --only=production

# Step 2: Copy source code
COPY . .

CMD ["node", "server.js"]
```

**Pattern for Go**:
```dockerfile
FROM golang:1.23-bookworm AS builder
WORKDIR /build

# Step 1: Download dependencies (cached)
COPY go.mod go.sum .
RUN go mod download

# Step 2: Copy source and build
COPY . .
RUN CGO_ENABLED=0 go build -o app

FROM alpine:latest
COPY --from=builder /build/app /app
CMD ["/app"]
```

### 8.4 Enabling BuildKit for Faster Builds

**Why**: Parallel builds, better caching, build secrets support

**Enable BuildKit** (one-time):
```bash
export DOCKER_BUILDKIT=1
```

**Or make permanent** (add to `~/.bashrc` or `~/.zshrc`):
```bash
echo 'export DOCKER_BUILDKIT=1' >> ~/.bashrc
```

**Or in docker-compose.yml**:
```yaml
services:
  app:
    build:
      context: .
      cache_from:
        - myapp:latest
      target: production
```

**Features enabled**:
- Parallel stage execution
- Better layer caching
- Build secrets (passwords not in image history)
- SSH forwarding for private repos

**BuildKit-specific Dockerfile features**:
```dockerfile
# Syntax directive (enables BuildKit features)
# syntax=docker/dockerfile:1.4

FROM python:3.12-slim

# Mount secrets without copying into image
RUN --mount=type=secret,id=pip_config \
    pip install --no-cache-dir -r requirements.txt

# Mount SSH keys for private repo access
RUN --mount=type=ssh \
    pip install git+ssh://git@github.com/private/repo.git
```

**Build with secrets**:
```bash
docker build --secret id=pip_config,src=~/.pip/pip.conf -t myapp .
```

---

## 9. Debugging Containers That Exit Immediately

### 9.1 Checking Container Logs

**Symptom**: Container starts then immediately stops

**Check logs**:
```bash
# Get container ID (even stopped)
docker ps -a

# View logs
docker logs <container-id>

# Follow logs in real-time
docker logs -f <container-id>

# Show timestamps
docker logs -t <container-id>

# Show last 100 lines
docker logs --tail 100 <container-id>
```

**Common error patterns**:
- `exec format error`: Wrong architecture (ARM vs x86)
- `no such file or directory`: Missing binary or library
- `permission denied`: File not executable or user lacks permissions
- Application-specific errors: Check application logs

### 9.2 Running Containers with Interactive Shell

**Purpose**: Get shell access to debug startup issues

**Override entrypoint**:
```bash
docker run -it --entrypoint /bin/bash myimage
```

**Or for Alpine-based images** (no bash):
```bash
docker run -it --entrypoint /bin/sh myimage
```

**With docker-compose**:
```bash
docker-compose run --entrypoint /bin/bash app
```

**Once inside**:
```bash
# Check if files are in expected locations
ls -la /app

# Try running the command manually
python app.py

# Check environment variables
env | grep DATABASE

# Check if dependencies are installed
pip list
```

### 9.3 Verifying CMD/ENTRYPOINT Configuration

**Check what command is being run**:
```bash
docker inspect myimage | grep -A 5 "Cmd\|Entrypoint"
```

**Common mistakes**:

**Bad CMD** (exits immediately):
```dockerfile
CMD ["echo", "Hello"]  # Runs and exits
```

**Good CMD** (long-running):
```dockerfile
CMD ["python", "app.py"]  # Stays running
```

**CMD vs ENTRYPOINT**:
- `ENTRYPOINT`: Main command (not easily overridden)
- `CMD`: Default arguments (easily overridden)

**Pattern for flexibility**:
```dockerfile
ENTRYPOINT ["python"]
CMD ["app.py"]
```

Run default: `docker run myimage`
Run different script: `docker run myimage other.py`

### 9.4 Keeping Containers Alive for Debugging

**Temporary hack** to prevent exit:
```dockerfile
CMD ["tail", "-f", "/dev/null"]
```

Or at runtime:
```bash
docker run -d myimage tail -f /dev/null
```

**Then exec into it**:
```bash
docker exec -it <container-id> /bin/bash
```

**Run your actual command manually**:
```bash
python app.py
```

**Remove this hack** once you've identified the issue!

---

## 10. Managing Environment Variables in Containers

### 10.1 Defining Environment Variables in Dockerfile

**Pattern**:
```dockerfile
FROM python:3.12-slim

# Set default environment variables
ENV APP_ENV=production \
    APP_PORT=8000 \
    LOG_LEVEL=info \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .

CMD ["python", "app.py"]
```

**Benefits**:
- Defaults baked into image
- Can be overridden at runtime
- Documented in Dockerfile

### 10.2 Passing Variables at Runtime

**Single variable**:
```bash
docker run -e DATABASE_URL=postgres://... myimage
```

**Multiple variables**:
```bash
docker run \
  -e DATABASE_URL=postgres://... \
  -e REDIS_URL=redis://... \
  -e LOG_LEVEL=debug \
  myimage
```

**Override Dockerfile ENV**:
```bash
docker run -e APP_ENV=development myimage
```

### 10.3 Using Environment Files

**Create `.env` file**:
```bash
DATABASE_URL=postgres://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379
LOG_LEVEL=info
APP_PORT=8000
```

**Use with docker run**:
```bash
docker run --env-file .env myimage
```

**Use with docker-compose.yml**:
```yaml
services:
  app:
    image: myimage
    env_file:
      - .env
      - .env.local  # Override with local values
```

**Multiple env files** (later files override earlier):
```yaml
services:
  app:
    env_file:
      - .env.defaults   # Base defaults
      - .env            # Environment-specific
      - .env.local      # Local overrides (gitignored)
```

### 10.4 Verifying Environment Variables Inside Containers

**Check all variables**:
```bash
docker exec <container-id> env
```

**Check specific variable**:
```bash
docker exec <container-id> printenv DATABASE_URL
```

**Or from inside container**:
```bash
docker exec -it <container-id> /bin/bash
echo $DATABASE_URL
```

**Common issues**:

**Variable not set**:
- Check spelling in Dockerfile or docker-compose.yml
- Check if env file is being loaded
- Check if variable is being overridden somewhere

**Variable has wrong value**:
- Check order of env_file entries (later files override)
- Check if docker-compose.yml has explicit `environment:` that overrides
- Check if host environment variable is interfering

**Variable not visible to application**:
- Some applications require variables to be exported
- Check application-specific configuration
- Check if application is reading from correct source (.env file vs environment)

---

## Summary

This reference document covers:
1. **Assessment**: How to identify Docker requirements for your project
2. **Base Images**: Choosing the right foundation for your containers
3. **Best Practices**: Multi-stage builds, security, health checks, layer optimization
4. **Multi-Service**: Configuring docker-compose.yml for complex environments
5. **Troubleshooting**: Solutions for 6 common Docker problems:
   - Disk space issues
   - Network problems
   - Permission errors
   - Slow builds
   - Containers exiting immediately
   - Environment variable issues

**When to use this document**: Reference when encountering Docker configuration challenges, build failures, or runtime issues. Each section provides step-by-step procedures with commands and verification steps.
