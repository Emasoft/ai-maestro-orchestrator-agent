# Agent Environment Setup - Part 1: Toolchain & LSP Installation

## Phase 1: Toolchain Installation

### 1.1 Detect Required Toolchain

Reference: [../toolchain/TOOLCHAIN_DETECTION.md](../toolchain/TOOLCHAIN_DETECTION.md)

```bash
# Auto-detect from project
python3 detect_language.py {{PROJECT_ROOT}}
# Output: python, nodejs, rust, go, cpp, etc.

TOOLCHAIN=$(python3 detect_language.py {{PROJECT_ROOT}})
echo "Detected toolchain: $TOOLCHAIN"
```

### 1.2 Install Toolchain

Reference: [../toolchain/TOOLCHAIN_INSTALLATION.md](../toolchain/TOOLCHAIN_INSTALLATION.md)

Use the appropriate installation script from toolchain templates:

```bash
# For Python
bash ../toolchain/install-scripts/install_python.sh

# For Node.js
bash ../toolchain/install-scripts/install_nodejs.sh

# For Rust
bash ../toolchain/install-scripts/install_rust.sh

# For Go
bash ../toolchain/install-scripts/install_go.sh

# For C++
bash ../toolchain/install-scripts/install_cpp.sh
```

### 1.3 Verify Toolchain

```bash
# Python
python3 --version
pip --version || pipx --version || uv --version

# Node.js
node --version
npm --version || pnpm --version

# Rust
rustc --version
cargo --version

# Go
go version

# C++
g++ --version || clang++ --version
```

## Phase 2: LSP Server Installation

### 2.1 Select LSP Server

Reference: [LSP_SELECTION_GUIDE.md](./LSP_SELECTION_GUIDE.md)

```bash
# Auto-select based on detected language
bash select_lsp.sh {{PROJECT_ROOT}}
# Output: JSON LSP configuration
```

### 2.2 Install LSP Server

Reference: [../references/lsp-installation-guide.md](../references/lsp-installation-guide.md)

```bash
# Use centralized installation script
python3 ../references/scripts/install_lsp.py --language $TOOLCHAIN

# Or install manually per language:

# Python
pipx install python-lsp-server
# or: npm install -g pyright

# JavaScript/TypeScript
npm install -g typescript-language-server typescript

# Rust
rustup component add rust-analyzer

# Go
go install golang.org/x/tools/gopls@latest

# C++
brew install llvm  # macOS
# apt-get install clangd  # Linux
```

### 2.3 Verify LSP Server

```bash
# Check installation
which pylsp || which pyright || \
which typescript-language-server || \
which rust-analyzer || \
which gopls || \
which clangd

# Test LSP server
bash verify-lsp.sh $LSP_COMMAND
```

---

**Next**: [Part 2 - Skills & Project Configuration](./AGENT_ENVIRONMENT_SETUP-part2-skills-config.md)
