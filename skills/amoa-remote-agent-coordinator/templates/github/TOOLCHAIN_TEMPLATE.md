---
name: toolchain-template
description: Template for toolchain configuration with sections for environment setup and tool requirements
---

# Toolchain Configuration Template

> **TODO**: This is a stub template. Expand with specific toolchain configurations and examples based on actual project requirements.

## Environment Overview

### Project Information
- **Project Name**: {project_name}
- **Repository**: {repo_url}
- **Primary Language**: {language}
- **Platform**: {macOS/Linux/Windows/Cross-platform}

### Environment Type
- [ ] Development
- [ ] Testing
- [ ] Staging
- [ ] Production

---

## Environment Setup

### System Requirements
- **OS**: {operating system and version}
- **CPU**: {minimum requirements}
- **Memory**: {minimum RAM}
- **Disk Space**: {minimum free space}

### Runtime Dependencies
| Dependency | Version | Installation |
|------------|---------|--------------|
| {runtime} | {version} | {install command} |

### Package Managers
| Manager | Version | Purpose |
|---------|---------|---------|
| {manager} | {version} | {what it manages} |

---

## Tool Configuration

### Version Control
```yaml
git:
  version: "{version}"
  config:
    user.name: "{name}"
    user.email: "{email}"
```

### Build Tools
```yaml
build:
  tool: "{tool_name}"
  version: "{version}"
  commands:
    build: "{build_command}"
    test: "{test_command}"
    lint: "{lint_command}"
```

### Linting and Formatting
| Tool | Language | Config File |
|------|----------|-------------|
| {linter} | {language} | {config_path} |

### Testing Framework
```yaml
testing:
  framework: "{framework}"
  version: "{version}"
  config: "{config_file}"
  commands:
    unit: "{unit_test_command}"
    integration: "{integration_test_command}"
    coverage: "{coverage_command}"
```

---

## CI/CD Configuration

### Pipeline Tool
- **Platform**: {GitHub Actions/GitLab CI/Jenkins/etc}
- **Config File**: {path to config}

### Required Secrets
| Secret Name | Description | Required |
|-------------|-------------|----------|
| {SECRET_NAME} | {what it's for} | {Yes/No} |

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| {VAR_NAME} | {purpose} | {default_value} |

---

## MCP Servers

### Required Servers
| Server | Purpose | Config |
|--------|---------|--------|
| {server_name} | {what it provides} | {config_path} |

### Server Configuration
```json
{
  "mcpServers": {
    "{server_name}": {
      "command": "{command}",
      "args": ["{args}"],
      "env": {}
    }
  }
}
```

---

## Scripts and Automation

### Setup Scripts
| Script | Purpose | Usage |
|--------|---------|-------|
| {script_path} | {what it does} | {how to run} |

### Utility Scripts
| Script | Purpose | Usage |
|--------|---------|-------|
| {script_path} | {what it does} | {how to run} |

---

## Troubleshooting

### Common Issues
| Issue | Cause | Solution |
|-------|-------|----------|
| {symptom} | {root cause} | {fix steps} |

### Diagnostic Commands
```bash
# Check environment
{diagnostic_command}

# Verify dependencies
{verification_command}

# Test connectivity
{test_command}
```

---

## Validation Checklist

### Environment Validation
- [ ] All runtime dependencies installed
- [ ] Package managers configured
- [ ] Environment variables set
- [ ] Secrets configured

### Tool Validation
- [ ] Build tools working
- [ ] Linters configured
- [ ] Tests running
- [ ] CI/CD pipeline functional

### Integration Validation
- [ ] MCP servers connected
- [ ] Git access verified
- [ ] API access confirmed
