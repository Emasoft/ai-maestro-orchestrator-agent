# C/C++ Toolchain - Part 3: CI/CD and Dependencies

**Parent document**: [CPP_TOOLCHAIN.md](CPP_TOOLCHAIN.md)

---

## GitHub Actions CI Template

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        compiler: [gcc, clang, msvc]
        exclude:
          - os: windows-latest
            compiler: gcc
          - os: windows-latest
            compiler: clang
          - os: ubuntu-latest
            compiler: msvc
          - os: macos-latest
            compiler: msvc
          - os: macos-latest
            compiler: gcc

    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies (Ubuntu)
        if: runner.os == 'Linux'
        run: |
          sudo apt update
          sudo apt install -y gcc-11 g++-11 clang-14 clang-tidy-14 cmake ninja-build
          pip install conan
          conan profile detect --force

      - name: Install dependencies (macOS)
        if: runner.os == 'macOS'
        run: |
          brew install llvm cmake ninja
          pip install conan
          conan profile detect --force

      - name: Install dependencies (Windows)
        if: runner.os == 'Windows'
        run: |
          pip install conan
          conan profile detect --force

      - name: Set Compiler (GCC)
        if: matrix.compiler == 'gcc'
        run: |
          echo "CC=gcc-11" >> $GITHUB_ENV
          echo "CXX=g++-11" >> $GITHUB_ENV

      - name: Set Compiler (Clang)
        if: matrix.compiler == 'clang'
        run: |
          echo "CC=clang-14" >> $GITHUB_ENV
          echo "CXX=clang++-14" >> $GITHUB_ENV

      - name: Install Conan dependencies
        run: |
          conan install . --build=missing --output-folder=build

      - name: Configure CMake
        run: |
          cmake -S . -B build \
            -DCMAKE_BUILD_TYPE=Release \
            -DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake

      - name: Build
        run: cmake --build build --config Release

      - name: Run tests
        run: ctest --test-dir build --output-on-failure -C Release

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install clang-tidy
        run: sudo apt install -y clang-tidy-14

      - name: Run clang-tidy
        run: |
          cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
          clang-tidy-14 src/*.cpp -p build

  format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install clang-format
        run: sudo apt install -y clang-format-14

      - name: Check formatting
        run: |
          find src include -name '*.cpp' -o -name '*.h' | xargs clang-format-14 --dry-run --Werror
```

---

## Library Requirements (MANDATORY)

| Purpose | Library | Usage |
|---------|---------|-------|
| JSON | `nlohmann/json` | `nlohmann::json j = {{"key", "value"}};` |
| CLI | `CLI11` | `CLI::App app{"Description"};` |
| HTTP | `cpp-httplib` | Optional, for HTTP clients |
| Testing | `Catch2` or native CTest | `TEST_CASE("name") { ... }` |
| Logging | `spdlog` | `spdlog::info("message");` |

**VIOLATIONS (will fail review):**
- `printf()` or `std::cout` for JSON output (use `nlohmann::json`)
- Manual string building for JSON (`std::string json = "{\"key\":\"" + value + "\"}";`)
- Raw pointers without smart pointers (`std::unique_ptr`, `std::shared_ptr`)
- Manual memory management (`new`/`delete`)
- Missing `const` correctness
- Non-RAII resource management

**CORRECT JSON OUTPUT:**
```cpp
#include <nlohmann/json.hpp>
using json = nlohmann::json;

json output = {
    {"status", "success"},
    {"data", {{"key", "value"}}}
};
std::cout << output.dump(2) << std::endl;
```

**WRONG JSON OUTPUT:**
```cpp
// NEVER DO THIS
std::cout << "{\"status\":\"success\",\"data\":{\"key\":\"value\"}}" << std::endl;
```
