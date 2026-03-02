# C/C++ Toolchain Template

Extends: `BASE_TOOLCHAIN.md`
Build System: CMake 3.25+
Package Manager: Conan or vcpkg
Preferred for: High-performance tools, systems programming, cross-platform CLI

---

## Table of Contents

This document is split into multiple parts for easier navigation:

### Part 1: Setup Script
**File**: [CPP_TOOLCHAIN-part1-setup.md](CPP_TOOLCHAIN-part1-setup.md)
- Platform detection (macOS, Linux, Windows)
- Compiler installation (gcc, clang, MSVC)
- Conan package manager setup
- clang-format and clang-tidy installation
- Default configuration files (.clang-format, .clang-tidy)
- Installation verification

### Part 2: CMake Templates
**File**: [CPP_TOOLCHAIN-part2-cmake.md](CPP_TOOLCHAIN-part2-cmake.md)
- CMakeLists.txt template (main project)
- tests/CMakeLists.txt template
- conanfile.txt template
- vcpkg.json template (alternative)

### Part 3: CI/CD and Dependencies
**File**: [CPP_TOOLCHAIN-part3-ci-deps.md](CPP_TOOLCHAIN-part3-ci-deps.md)
- GitHub Actions CI template (multi-platform matrix)
- Lint and format jobs
- Library requirements (nlohmann/json, CLI11, etc.)
- Correct vs incorrect JSON output patterns
- Code violations that will fail review

### Part 4: Cross-Platform Build and Verification
**File**: [CPP_TOOLCHAIN-part4-build-verification.md](CPP_TOOLCHAIN-part4-build-verification.md)
- CMAKE_TOOLCHAIN_FILE usage (Conan, vcpkg)
- Platform-specific notes (macOS, Windows, Linux)
- Complete verification checklist
- Template metadata

---

## Quick Reference

| Component | Tool | Version | Install |
|-----------|------|---------|---------|
| Language | gcc/clang | gcc 11+ / clang 14+ | System package manager |
| Build System | cmake | 3.25+ | `brew install cmake` / `apt install cmake` |
| Package Manager | conan | 2.0+ | `pip install conan` or vcpkg |
| Formatter | clang-format | 14+ | `apt install clang-format` |
| Linter | clang-tidy | 14+ | `apt install clang-tidy` |
| Test Runner | ctest | bundled with cmake | - |
| Coverage | gcov / llvm-cov | bundled | - |

---

## Variable Substitutions

```yaml
LANGUAGE: cpp
LANGUAGE_VERSION: "20"
LANGUAGE_CMD: g++
LANGUAGE_VERSION_CMD: "g++ --version"
LANGUAGE_INSTALL_CMD: |
  # macOS
  xcode-select --install 2>/dev/null || true
  brew install gcc llvm cmake

  # Linux (Ubuntu/Debian)
  sudo apt update && sudo apt install -y build-essential gcc-11 g++-11 clang-14 cmake

  # Windows
  # Install Visual Studio 2022 with C++ Desktop Development workload
  # Or: winget install -e --id Microsoft.VisualStudio.2022.BuildTools

PACKAGE_MANAGER: conan
PACKAGE_MANAGER_VERSION: "2.0+"
PACKAGE_MANAGER_INSTALL_CMD: "pip install 'conan>=2.0'"
INSTALL_DEPS_CMD: "conan install . --build=missing"

FORMATTER: clang-format
FORMATTER_CMD: "clang-format -i src/**/*.cpp src/**/*.h"
FORMATTER_CONFIG: ".clang-format"

LINTER: clang-tidy
LINTER_CMD: "clang-tidy src/**/*.cpp -- -std=c++20"
LINTER_CONFIG: ".clang-tidy"

TYPE_CHECKER: "-"
TYPE_CHECKER_CMD: "# C++ is statically typed"
TYPE_CHECKER_CONFIG: "-"

TEST_RUNNER: ctest
TEST_CMD: "ctest --output-on-failure"
COVERAGE_CMD: "gcov src/*.cpp"

BUILD_COMMAND: "cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build"
VERIFY_ALL_CMD: "cmake --build build && ctest --test-dir build && clang-tidy src/**/*.cpp"

CONFIG_FILES_LIST: "CMakeLists.txt, conanfile.txt, .clang-format, .clang-tidy"
```

---

## Quick Start

1. **Run setup script** (from Part 1):
   ```bash
   ./setup-cpp-toolchain.sh
   ```

2. **Create project structure**:
   ```
   project/
   ├── CMakeLists.txt          # From Part 2
   ├── conanfile.txt           # From Part 2
   ├── .clang-format           # Created by setup script
   ├── .clang-tidy             # Created by setup script
   ├── src/
   │   └── main.cpp
   ├── include/
   └── tests/
       ├── CMakeLists.txt      # From Part 2
       └── test_main.cpp
   ```

3. **Build and test**:
   ```bash
   conan install . --build=missing --output-folder=build
   cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake
   cmake --build build
   ctest --test-dir build --output-on-failure
   ```

4. **Set up CI** (from Part 3):
   - Copy GitHub Actions template to `.github/workflows/ci.yml`

5. **Verify compliance** (from Part 4):
   - Use the verification checklist before submitting

---

## Template Metadata

```yaml
template:
  name: CPP_TOOLCHAIN
  version: 1.0.0
  eoa_compatible: true
  requires:
    - git
    - cmake 3.25+
    - gcc 11+ OR clang 14+ OR MSVC 2022
    - conan 2.0+ OR vcpkg
  generates:
    - CMakeLists.txt
    - conanfile.txt OR vcpkg.json
    - .clang-format
    - .clang-tidy
    - setup script
    - verification checklist
  parts:
    - CPP_TOOLCHAIN-part1-setup.md
    - CPP_TOOLCHAIN-part2-cmake.md
    - CPP_TOOLCHAIN-part3-ci-deps.md
    - CPP_TOOLCHAIN-part4-build-verification.md
```
