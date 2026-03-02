# LSP Enforcement Checklist - Part 1: Setup and Core Remediation


## Contents

- [Table of Contents](#table-of-contents)
- [When preparing to assign work to remote agents](#when-preparing-to-assign-work-to-remote-agents)
- [When verifying that all required LSP servers are installed](#when-verifying-that-all-required-lsp-servers-are-installed)
  - [Core Languages](#core-languages)
    - [Python](#python)
    - [TypeScript/JavaScript](#typescriptjavascript)
    - [Go](#go)
    - [Rust](#rust)
  - [JVM Languages](#jvm-languages)
    - [Java](#java)
    - [Kotlin](#kotlin)
  - [Systems Languages](#systems-languages)
    - [C/C++](#cc)
    - [C#](#c)
  - [Web Languages](#web-languages)
    - [PHP](#php)
    - [Ruby](#ruby)
    - [HTML/CSS](#htmlcss)
- [Automated Verification](#automated-verification)
- [When LSP verification fails for any language](#when-lsp-verification-fails-for-any-language)
  - [Python (pyright) Remediation](#python-pyright-remediation)
  - [TypeScript (typescript-language-server) Remediation](#typescript-typescript-language-server-remediation)
  - [Rust (rust-analyzer) Remediation](#rust-rust-analyzer-remediation)
  - [Go (gopls) Remediation](#go-gopls-remediation)
  - [Java (jdtls) Remediation](#java-jdtls-remediation)
  - [Kotlin (kotlin-language-server) Remediation](#kotlin-kotlin-language-server-remediation)
  - [C/C++ (clangd) Remediation](#cc-clangd-remediation)
  - [C# (OmniSharp/csharp-ls) Remediation](#c-omnisharpcsharp-ls-remediation)

---

Covers preparation, verification, and remediation for core languages supported by Claude Code LSP.

## Table of Contents

1. [When preparing to assign work to remote agents](#when-preparing-to-assign-work-to-remote-agents)
2. [When verifying that all required LSP servers are installed](#when-verifying-that-all-required-lsp-servers-are-installed)
   - 2.1 Core Languages (Python, TypeScript, Go, Rust)
   - 2.2 JVM Languages (Java, Kotlin)
   - 2.3 Systems Languages (C/C++, C#)
   - 2.4 Web Languages (PHP, Ruby, HTML/CSS)
   - 2.5 Automated Verification
3. [When LSP verification fails - Core Language Remediation](#when-lsp-verification-fails-for-any-language)
   - 3.1 Python (pyright) Remediation
   - 3.2 TypeScript Remediation
   - 3.3 Rust (rust-analyzer) Remediation
   - 3.4 Go (gopls) Remediation
   - 3.5 Java (jdtls) Remediation
   - 3.6 Kotlin Remediation
   - 3.7 C/C++ (clangd) Remediation
   - 3.8 C# (OmniSharp) Remediation

**See Also:**
- [Part 2: Validation and General Troubleshooting](lsp-enforcement-part2-validation-general-troubleshooting.md)
- [Part 3: Language-Specific Troubleshooting](lsp-enforcement-part3-language-troubleshooting.md)

---

## When preparing to assign work to remote agents

Before assigning work to a remote agent:

- [ ] Identify project languages (Python, TypeScript, Go, Rust, Java, Kotlin, C/C++, C#, PHP, Ruby, HTML/CSS)
- [ ] List required LSP servers for each language
- [ ] Verify agent has access to package managers (pip, npm, cargo, go, gem, dotnet, brew/apt)

## When verifying that all required LSP servers are installed

For each language in the project:

### Core Languages

#### Python
- [ ] pyright binary installed: `which pyright-langserver`
- [ ] pyright-lsp plugin installed: `/plugin list | grep pyright`

#### TypeScript/JavaScript
- [ ] typescript-language-server installed: `which typescript-language-server`
- [ ] typescript-lsp plugin installed: `/plugin list | grep typescript`

#### Go
- [ ] gopls installed: `which gopls`
- [ ] go-lsp plugin installed: `/plugin list | grep gopls`

#### Rust
- [ ] rust-analyzer installed: `which rust-analyzer`
- [ ] rust-lsp plugin installed: `/plugin list | grep rust`

### JVM Languages

#### Java
- [ ] jdtls installed: `which jdtls`
- [ ] JDK 11+ installed: `java --version`
- [ ] java-lsp plugin installed: `/plugin list | grep java`

#### Kotlin
- [ ] kotlin-language-server installed: `which kotlin-language-server`
- [ ] JDK 11+ installed: `java --version`
- [ ] kotlin-lsp plugin installed: `/plugin list | grep kotlin`

### Systems Languages

#### C/C++
- [ ] clangd installed: `which clangd`
- [ ] compile_commands.json exists (for project-aware analysis)
- [ ] cpp-lsp plugin installed: `/plugin list | grep clangd`

#### C#
- [ ] OmniSharp or csharp-ls installed: `which OmniSharp` or `dotnet tool list -g | grep csharp-ls`
- [ ] .NET SDK 6.0+ installed: `dotnet --version`
- [ ] csharp-lsp plugin installed: `/plugin list | grep omnisharp`

### Web Languages

#### PHP
- [ ] intelephense installed: `which intelephense`
- [ ] php-lsp plugin installed: `/plugin list | grep intelephense`

#### Ruby
- [ ] solargraph installed: `which solargraph`
- [ ] Ruby 2.7+ installed: `ruby --version`
- [ ] ruby-lsp plugin installed: `/plugin list | grep solargraph`

#### HTML/CSS
- [ ] html-language-server installed: `which vscode-html-language-server`
- [ ] css-language-server installed: `which vscode-css-language-server`
- [ ] html-lsp/css-lsp plugins installed: `/plugin list | grep html`

## Automated Verification

Run verification script:
```bash
python scripts/install_lsp.py --project-path /path/to/project --verify-only
```

Expected output:
```
[OK] python: pyright-langserver installed
[OK] typescript: typescript-language-server installed
```

If any show [MISSING], run without --verify-only to install.

## When LSP verification fails for any language

If LSP verification fails for any language, follow these remediation steps:

### Python (pyright) Remediation

**If binary missing:**
```bash
# Install via npm (recommended)
npm install -g pyright

# Verify installation
which pyright-langserver
pyright --version
```

**If plugin missing:**
```bash
# Install Claude Code plugin
/plugin install pyright-lsp

# Verify plugin loaded
/plugin list | grep pyright
```

**If both missing:**
```bash
# Run automated installation
python scripts/install_lsp.py --language python --project-path /path/to/project
```

### TypeScript (typescript-language-server) Remediation

**If binary missing:**
```bash
# Install via npm
npm install -g typescript-language-server typescript

# Verify installation
which typescript-language-server
typescript-language-server --version
```

**If plugin missing:**
```bash
# Install Claude Code plugin
/plugin install typescript-lsp

# Verify plugin loaded
/plugin list | grep typescript
```

**If both missing:**
```bash
# Run automated installation
python scripts/install_lsp.py --language typescript --project-path /path/to/project
```

### Rust (rust-analyzer) Remediation

**If binary missing:**
```bash
# Install via rustup (recommended)
rustup component add rust-analyzer

# Or via cargo
cargo install rust-analyzer

# Verify installation
which rust-analyzer
rust-analyzer --version
```

**If plugin missing:**
```bash
# Install Claude Code plugin
/plugin install rust-lsp

# Verify plugin loaded
/plugin list | grep rust
```

**If both missing:**
```bash
# Run automated installation
python scripts/install_lsp.py --language rust --project-path /path/to/project
```

### Go (gopls) Remediation

**If binary missing:**
```bash
# Install via go install
go install golang.org/x/tools/gopls@latest

# Ensure $GOPATH/bin is in PATH
export PATH=$PATH:$(go env GOPATH)/bin

# Verify installation
which gopls
gopls version
```

**If plugin missing:**
```bash
# Install Claude Code plugin
/plugin install gopls-lsp

# Verify plugin loaded
/plugin list | grep gopls
```

**If both missing:**
```bash
# Run automated installation
python scripts/install_lsp.py --language go --project-path /path/to/project
```

### Java (jdtls) Remediation

**If binary missing:**
```bash
# macOS
brew install jdtls

# Linux (via SDKMAN)
curl -s "https://get.sdkman.io" | bash
sdk install java 21-tem
# Then download jdtls from Eclipse

# Verify installation
which jdtls
java --version  # JDK 11+ required
```

**If plugin missing:**
```bash
# Install Claude Code plugin
/plugin install jdtls-lsp

# Verify plugin loaded
/plugin list | grep java
```

**If both missing:**
```bash
# Run automated installation
python scripts/install_lsp.py --language java --project-path /path/to/project
```

### Kotlin (kotlin-language-server) Remediation

**If binary missing:**
```bash
# macOS
brew install kotlin-language-server

# Via npm (cross-platform)
npm install -g kotlin-language-server

# Verify installation
which kotlin-language-server
java --version  # JDK 11+ required
```

**If plugin missing:**
```bash
# Install Claude Code plugin
/plugin install kotlin-lsp

# Verify plugin loaded
/plugin list | grep kotlin
```

**If both missing:**
```bash
# Run automated installation
python scripts/install_lsp.py --language kotlin --project-path /path/to/project
```

### C/C++ (clangd) Remediation

**If binary missing:**
```bash
# macOS
brew install llvm
export PATH="/opt/homebrew/opt/llvm/bin:$PATH"

# Linux (Debian/Ubuntu)
sudo apt install clangd

# Verify installation
which clangd
clangd --version
```

**If plugin missing:**
```bash
# Install Claude Code plugin
/plugin install clangd-lsp

# Verify plugin loaded
/plugin list | grep clangd
```

**If compile_commands.json missing:**
```bash
# For CMake projects
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ..

# For Make projects
bear -- make

# For Meson projects
meson compile -C builddir --ninja-args=-t,compdb > compile_commands.json
```

**If both missing:**
```bash
# Run automated installation
python scripts/install_lsp.py --language cpp --project-path /path/to/project
```

### C# (OmniSharp/csharp-ls) Remediation

**If binary missing:**
```bash
# Via .NET SDK (recommended)
dotnet tool install -g csharp-ls

# macOS (OmniSharp alternative)
brew install omnisharp-roslyn

# Verify installation
dotnet --version  # .NET SDK 6.0+ required
which csharp-ls || which OmniSharp
```

**If plugin missing:**
```bash
# Install Claude Code plugin
/plugin install omnisharp-lsp

# Verify plugin loaded
/plugin list | grep omnisharp
```

**If both missing:**
```bash
# Run automated installation
python scripts/install_lsp.py --language csharp --project-path /path/to/project
```

---

**Next:** [Part 2: Validation and General Troubleshooting](lsp-enforcement-part2-validation-general-troubleshooting.md)
