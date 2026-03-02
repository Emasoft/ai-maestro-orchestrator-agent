---
name: toolchain-installation
description: Instructions and automation scripts for installing development toolchains, language runtimes, and build tools
---

# Toolchain Installation

## Purpose

This reference document provides installation instructions for development toolchains. Use this guide when you need to:

- Install missing language runtimes or compilers
- Set up build tools and package managers
- Configure development environments for specific languages
- Automate toolchain provisioning for remote agents

> **TODO**: This is a stub file that needs comprehensive installation procedures, version management strategies, and automated provisioning scripts for all supported toolchains.

## Installation by Platform

### macOS (using Homebrew)

```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install common toolchains
brew install python@3.12
brew install node
brew install rustup
brew install go
```

### Linux (Debian/Ubuntu)

```bash
# Update package lists
sudo apt update

# Install common toolchains
sudo apt install python3 python3-pip
sudo apt install nodejs npm
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### Linux (Fedora/RHEL)

```bash
# Install common toolchains
sudo dnf install python3 python3-pip
sudo dnf install nodejs npm
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

## Version Management

### Python (pyenv/uv)

```bash
# Using uv for Python version management
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.12
```

### Node.js (nvm)

```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install --lts
```

### Rust (rustup)

```bash
# Rustup handles version management
rustup default stable
rustup update
```

## Post-Installation Verification

After installing toolchains, verify with detection:

```bash
# Run detection to confirm installation
./detect-toolchains.sh
```

## Automated Provisioning

Script template for automated toolchain provisioning in CI/CD or remote agent environments.

## Related References

- See [TOOLCHAIN_DETECTION.md](./TOOLCHAIN_DETECTION.md) for detecting installed toolchains
