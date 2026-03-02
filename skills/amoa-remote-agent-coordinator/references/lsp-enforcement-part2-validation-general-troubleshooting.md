# LSP Enforcement Checklist - Part 2: Validation and General Troubleshooting


## Contents

- [Table of Contents](#table-of-contents)
- [Web Languages Remediation](#web-languages-remediation)
  - [PHP (Intelephense) Remediation](#php-intelephense-remediation)
  - [Ruby (Solargraph) Remediation](#ruby-solargraph-remediation)
  - [HTML/CSS (Standalone Language Servers) Remediation](#htmlcss-standalone-language-servers-remediation)
- [When validating agent's work before PR approval](#when-validating-agents-work-before-pr-approval)
  - [1. LSP Diagnostics Check](#1-lsp-diagnostics-check)
  - [2. Type Safety Verification](#2-type-safety-verification)
  - [3. Code Navigation Test](#3-code-navigation-test)
  - [4. Quality Gates](#4-quality-gates)
- [When enforcing LSP requirements throughout workflows](#when-enforcing-lsp-requirements-throughout-workflows)
- [Rejection Criteria](#rejection-criteria)
- [Benefits Tracked](#benefits-tracked)
- [When LSP features fail or behave unexpectedly](#when-lsp-features-fail-or-behave-unexpectedly)
  - [LSP Server Won't Start](#lsp-server-wont-start)
  - [LSP Diagnostics Not Appearing](#lsp-diagnostics-not-appearing)
  - [Performance Issues](#performance-issues)
- [Language-Specific Issues](#language-specific-issues)
  - [Python (pyright) Issues](#python-pyright-issues)
  - [TypeScript Issues](#typescript-issues)
  - [Rust (rust-analyzer) Issues](#rust-rust-analyzer-issues)

---

Covers web language remediation, PR validation, enforcement workflows, and general troubleshooting.

## Table of Contents

1. [Web Languages Remediation](#web-languages-remediation)
   - 1.1 PHP (Intelephense) Remediation
   - 1.2 Ruby (Solargraph) Remediation
   - 1.3 HTML/CSS Remediation
2. [When validating agent's work before PR approval](#when-validating-agents-work-before-pr-approval)
   - 2.1 LSP Diagnostics Check
   - 2.2 Type Safety Verification (all languages)
   - 2.3 Code Navigation Test
   - 2.4 Quality Gates
3. [When enforcing LSP requirements throughout workflows](#when-enforcing-lsp-requirements-throughout-workflows)
4. [Rejection Criteria](#rejection-criteria)
5. [Benefits Tracked](#benefits-tracked)
6. [When LSP features fail or behave unexpectedly](#when-lsp-features-fail-or-behave-unexpectedly)
   - 6.1 LSP Server Won't Start
   - 6.2 LSP Diagnostics Not Appearing
   - 6.3 Performance Issues
7. [Language-Specific Issues (Python, TypeScript, Rust)](#language-specific-issues)
   - 7.1 Python (pyright) Issues
   - 7.2 TypeScript Issues
   - 7.3 Rust (rust-analyzer) Issues

**See Also:**
- [Part 1: Setup and Core Remediation](lsp-enforcement-part1-setup-core-remediation.md)
- [Part 3: Language-Specific Troubleshooting](lsp-enforcement-part3-language-troubleshooting.md)

---

## Web Languages Remediation

### PHP (Intelephense) Remediation

**If binary missing:**
```bash
# Install via npm
npm install -g intelephense

# Verify installation
which intelephense
intelephense --version
```

**If plugin missing:**
```bash
# Install Claude Code plugin
/plugin install intelephense-lsp

# Verify plugin loaded
/plugin list | grep intelephense
```

**If both missing:**
```bash
# Run automated installation
python scripts/install_lsp.py --language php --project-path /path/to/project
```

### Ruby (Solargraph) Remediation

**If binary missing:**
```bash
# Install via gem
gem install solargraph

# Download Ruby core documentation
solargraph download-core

# Verify installation
ruby --version  # Ruby 2.7+ required
which solargraph
solargraph --version
```

**If plugin missing:**
```bash
# Install Claude Code plugin
/plugin install solargraph-lsp

# Verify plugin loaded
/plugin list | grep solargraph
```

**If both missing:**
```bash
# Run automated installation
python scripts/install_lsp.py --language ruby --project-path /path/to/project
```

### HTML/CSS (Standalone Language Servers) Remediation

**If binary missing:**
```bash
# Install standalone servers (not VS Code dependent, just npm package name)
npm install -g vscode-langservers-extracted

# Verify installation
which vscode-html-language-server
which vscode-css-language-server
```

**If plugin missing:**
```bash
# Install Claude Code plugins
/plugin install html-lsp
/plugin install css-lsp

# Verify plugins loaded
/plugin list | grep html
/plugin list | grep css
```

**If both missing:**
```bash
# Run automated installation
python scripts/install_lsp.py --language html --project-path /path/to/project
python scripts/install_lsp.py --language css --project-path /path/to/project
```

## When validating agent's work before PR approval

After remote agent completes work, orchestrator MUST verify:

### 1. LSP Diagnostics Check
```bash
# Review LSP errors in modified files
/plugin errors

# Expected: No errors in changed files
# If errors found: Request fixes before PR approval
```

### 2. Type Safety Verification

**Python:**
```bash
# Run pyright on changed files
pyright src/module.py
# Expected: 0 errors, 0 warnings
```

**TypeScript:**
```bash
# Run tsc on changed files
npx tsc --noEmit src/module.ts
# Expected: no errors
```

**Rust:**
```bash
# Run cargo check on changed files
cargo check
# Expected: no errors
```

**Go:**
```bash
# Run gopls check on changed files
gopls check ./...
# Expected: no errors
```

**Java:**
```bash
# Run jdtls check on changed files (via build tool)
./gradlew compileJava
# or
mvn compile
# Expected: BUILD SUCCESS
```

**Kotlin:**
```bash
# Run Kotlin compiler check
./gradlew compileKotlin
# or
kotlinc -Werror src/main.kt
# Expected: no errors
```

**C/C++:**
```bash
# Run clang-tidy on changed files
clang-tidy -p compile_commands.json src/module.cpp
# Expected: no warnings or errors
```

**C#:**
```bash
# Run dotnet build to verify types
dotnet build --no-restore
# Expected: Build succeeded
```

**PHP:**
```bash
# Run phpstan for static analysis
vendor/bin/phpstan analyse src/
# Expected: no errors found
```

**Ruby:**
```bash
# Run solargraph type checking
solargraph typecheck
# Expected: no problems found
```

### 3. Code Navigation Test

Verify LSP features work on modified code:
- [ ] Go to definition works for new symbols
- [ ] Find references finds all usages
- [ ] Hover shows correct type information
- [ ] Auto-complete suggests appropriate symbols

### 4. Quality Gates

Before accepting agent's work:
- [ ] All LSP diagnostics resolved
- [ ] Type checking passes for all languages
- [ ] No "any" types in TypeScript (unless explicitly allowed)
- [ ] No "type: ignore" in Python (unless documented)
- [ ] Rust code has no unsafe blocks (unless justified)
- [ ] Go code follows official style guide (verified by gopls)
- [ ] Java code has no raw types (unless justified)
- [ ] Kotlin code uses null-safety properly (no `!!` abuse)
- [ ] C/C++ code passes clang-tidy with no warnings
- [ ] C# code has no nullable reference warnings (unless documented)
- [ ] PHP code passes phpstan at level 6+ (or configured level)
- [ ] Ruby code has YARD documentation for public methods

## When enforcing LSP requirements throughout workflows

The orchestrator MUST:

1. **Before task assignment**: Run LSP verification script
2. **On failure**: Block assignment until LSP installed
3. **In task instructions**: Include "Ensure LSP diagnostics pass"
4. **On PR review**: Verify no LSP errors in changed files

## Rejection Criteria

Reject remote agent assignment if:
- LSP binaries not installed for project languages
- /plugin errors shows LSP failures
- Agent reports "executable not found" errors

## Benefits Tracked

Track LSP benefits in progress reports:
- Type errors caught before PR submission
- Reduced review cycles due to fewer basic errors
- Faster navigation to definitions/references

## When LSP features fail or behave unexpectedly

### LSP Server Won't Start

**Symptoms:**
- `/plugin errors` shows LSP initialization failures
- "Executable not found in $PATH" errors
- LSP features (go-to-definition, hover) not working

**Diagnosis Steps:**
1. Verify binary installed: `which <lsp-binary>`
2. Check plugin loaded: `/plugin list | grep <lsp-name>`
3. Review debug logs: `~/.claude/debug/lsp-*.log`
4. Test binary manually: `<lsp-binary> --version`

**Common Fixes:**
- Binary not in PATH: Add to PATH and restart Claude Code
- Plugin not loaded: Run `/plugin install <lsp-name>`
- Binary permissions: `chmod +x $(which <lsp-binary>)`
- Conflicting versions: Uninstall old versions, install latest

### LSP Diagnostics Not Appearing

**Symptoms:**
- No errors/warnings shown for obviously broken code
- `/plugin errors` shows "No diagnostics"

**Diagnosis:**
1. Check LSP server running: `/plugin list` (should show "active")
2. Verify file extension mapped: Check plugin's `extensionToLanguage`
3. Review initialization: Check `~/.claude/debug/lsp-*.log` for init errors

**Common Fixes:**
- File extension not mapped: Update plugin's `extensionToLanguage`
- LSP crashed: Restart Claude Code to restart LSP
- Wrong working directory: Ensure LSP started in project root

### Performance Issues

**Symptoms:**
- Slow auto-completion
- High CPU usage by LSP process
- Delayed diagnostics

**Solutions:**
- Exclude large directories (node_modules, .venv) in LSP settings
- Reduce diagnostics scope in initializationOptions
- Increase LSP memory limits in plugin config
- Use faster LSP implementations (e.g., pyright over pylsp)

## Language-Specific Issues

### Python (pyright) Issues

**Issue: "Cannot find module" errors for installed packages**

**Cause:** Virtual environment not detected or wrong Python interpreter

**Solution:**
```bash
# Check current Python interpreter
which python

# Activate virtual environment
source .venv/bin/activate

# Verify pyright sees packages
pyright --pythonpath .venv/lib/python*/site-packages src/

# Create pyrightconfig.json
cat > pyrightconfig.json <<EOF
{
  "venvPath": ".",
  "venv": ".venv",
  "executionEnvironments": [
    {
      "root": "src"
    }
  ]
}
EOF
```

**Issue: "Type is partially unknown" warnings**

**Cause:** Missing type stubs for third-party libraries

**Solution:**
```bash
# Install type stubs
pip install types-requests types-pyyaml types-redis

# Or use pyright's stub generation
pyright --createstub <library-name>
```

### TypeScript Issues

**Issue: "Cannot find name" for global types**

**Cause:** Missing @types packages or incorrect tsconfig.json

**Solution:**
```bash
# Install missing @types packages
npm install --save-dev @types/node @types/jest

# Check tsconfig.json includes types
cat tsconfig.json
# Should have:
{
  "compilerOptions": {
    "types": ["node", "jest"],
    "typeRoots": ["./node_modules/@types"]
  }
}

# Reload TypeScript server
npx tsc --build --clean && npx tsc --noEmit
```

**Issue: "Property does not exist on type" after adding new field**

**Cause:** Stale TypeScript server cache

**Solution:**
```bash
# Clear TypeScript build cache
rm -rf .tsbuildinfo
npx tsc --build --clean

# Restart typescript-language-server
/plugin reload typescript-lsp

# Verify type definitions updated
npx tsc --noEmit --listFiles | grep <your-file>
```

### Rust (rust-analyzer) Issues

**Issue: "Unresolved import" for workspace crates**

**Cause:** Cargo workspace not properly configured

**Solution:**
```bash
# Verify Cargo.toml workspace configuration
cat Cargo.toml
# Should have:
[workspace]
members = ["crate1", "crate2"]

# Regenerate Cargo.lock
cargo clean
cargo update

# Force rust-analyzer to reload
cargo check
```

**Issue: "Proc macro not expanded" errors**

**Cause:** Procedural macros not being expanded by rust-analyzer

**Solution:**
```bash
# Enable proc-macro expansion in rust-analyzer config
# Create .vscode/settings.json or rust-analyzer.toml
{
  "rust-analyzer.cargo.buildScripts.enable": true,
  "rust-analyzer.procMacro.enable": true,
  "rust-analyzer.procMacro.attributes.enable": true
}

# Rebuild with proc-macros
cargo clean && cargo build
```

**Issue: "Could not resolve macro" for custom derives**

**Cause:** Build scripts or dependencies not compiled

**Solution:**
```bash
# Run cargo build to compile proc-macros
cargo build

# Check build script execution
cargo build -vv | grep "Running"

# Reload rust-analyzer
cargo clean && cargo check
```

---

**Previous:** [Part 1: Setup and Core Remediation](lsp-enforcement-part1-setup-core-remediation.md)

**Next:** [Part 3: Language-Specific Troubleshooting](lsp-enforcement-part3-language-troubleshooting.md)
