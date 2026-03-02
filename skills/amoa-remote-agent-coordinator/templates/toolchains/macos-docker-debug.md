---
name: macos-docker-debug
type: toolchain-template
platform: macos
connection: docker
version: 0.1.0
status: stub
---

# macOS Docker Debugging Template

## Purpose

This template provides configuration for debugging Docker containers on macOS. Use this when:

- Debugging containerized applications locally on macOS
- Attaching debuggers to running Docker containers
- Setting up development containers with debug capabilities

## Docker Configuration

```yaml
# TODO: Define Docker daemon connection
docker_host: "unix:///var/run/docker.sock"
api_version: "auto"
tls_verify: false
```

## Debug Container Settings

```yaml
# TODO: Define debug container configuration
image: ""
container_name: "debug-container"
privileged: false
network_mode: "bridge"
volumes: []
ports: []
```

## Debugger Integration

```yaml
# TODO: Define debugger attachment settings
debugger_type: ""  # lldb, gdb, delve, node-inspect, etc.
debug_port: 0
attach_on_start: false
break_on_entry: false
```

## macOS-Specific Settings

```yaml
# TODO: Define macOS-specific configurations
use_rosetta: false
hyperkit_memory: "4g"
hyperkit_cpus: 2
file_sharing_paths: []
```

## Logging Configuration

```yaml
# TODO: Define logging and output settings
log_driver: "json-file"
log_opts:
  max-size: "10m"
  max-file: "3"
stream_stdout: true
stream_stderr: true
```

---

> **TODO**: This is a stub template. Full implementation requires:
> - Docker Desktop for Mac integration
> - Rosetta 2 compatibility for ARM64
> - Volume mount performance optimization (cached/delegated)
> - Debug symbol path mapping
> - Source map configuration
