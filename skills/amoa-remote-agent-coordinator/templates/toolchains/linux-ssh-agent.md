---
name: linux-ssh-agent
type: toolchain-template
platform: linux
connection: ssh
version: 0.1.0
status: stub
---

# Linux SSH Agent Configuration Template

## Purpose

This template provides configuration for remote Linux agents connected via SSH. Use this when:

- Deploying tasks to Linux servers or VMs
- Running builds on remote Linux CI runners
- Accessing Linux-based development environments

## Connection Configuration

```yaml
# TODO: Define SSH connection parameters
host: ""
port: 22
user: ""
identity_file: ""
known_hosts_check: true
```

## Agent Environment

```yaml
# TODO: Define agent environment setup
shell: /bin/bash
working_directory: /tmp/agent-workspace
environment_variables: {}
```

## Capability Detection

```yaml
# TODO: Define capability detection commands
detect_python: "python3 --version"
detect_node: "node --version"
detect_docker: "docker --version"
```

## Security Configuration

```yaml
# TODO: Define security constraints
allowed_commands: []
forbidden_paths: []
max_execution_time: 3600
```

---

> **TODO**: This is a stub template. Full implementation requires:
> - SSH connection pooling configuration
> - Key management integration
> - Host fingerprint verification
> - Timeout and retry policies
> - Output streaming configuration
