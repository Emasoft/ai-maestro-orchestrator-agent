# C/C++ Toolchain - Part 4: Cross-Platform Build and Verification

**Parent document**: [CPP_TOOLCHAIN.md](CPP_TOOLCHAIN.md)

---

## Cross-Platform Build Notes

### Using CMAKE_TOOLCHAIN_FILE

**With Conan:**
```bash
conan install . --build=missing --output-folder=build
cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake
cmake --build build
```

**With vcpkg:**
```bash
cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=/path/to/vcpkg/scripts/buildsystems/vcpkg.cmake
cmake --build build
```

### Platform-Specific Notes

**macOS:**
- Universal binaries: Add `-DCMAKE_OSX_ARCHITECTURES="x86_64;arm64"`
- Xcode generator: `-G Xcode`

**Windows:**
- MSVC: `-G "Visual Studio 17 2022" -A x64`
- Use Developer Command Prompt for VS 2022

**Linux:**
- Prefer Ninja generator: `-G Ninja`
- Static linking: `-DCMAKE_FIND_LIBRARY_SUFFIXES=".a"`

---

## Verification Checklist

```markdown
## C++ Toolchain Verification - {{TASK_ID}}

### Installation
- [ ] g++ or clang++ installed: `g++ --version` shows 11+
- [ ] cmake installed: `cmake --version` shows 3.25+
- [ ] conan installed: `conan --version` shows 2.0+
- [ ] clang-format installed: `clang-format --version`
- [ ] clang-tidy installed: `clang-tidy --version`

### Configuration
- [ ] .clang-format exists with EOA standard config
- [ ] .clang-tidy exists with EOA standard config
- [ ] CMakeLists.txt uses modern CMake (target-based)
- [ ] conanfile.txt or vcpkg.json includes nlohmann_json
- [ ] conanfile.txt or vcpkg.json includes CLI11

### Dependencies
- [ ] `conan install . --build=missing` succeeds
- [ ] nlohmann_json available: Check build/conan_toolchain.cmake
- [ ] CLI11 available: Check build/conan_toolchain.cmake

### Build
- [ ] `cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake` succeeds
- [ ] `cmake --build build` compiles without errors
- [ ] No warnings with `-Wall -Wextra -Werror`

### Testing
- [ ] `ctest --test-dir build --output-on-failure` passes
- [ ] Coverage reports generated (if configured)

### Linting/Formatting
- [ ] `clang-tidy src/*.cpp` passes (no warnings)
- [ ] `clang-format --dry-run --Werror src/*.cpp` passes
- [ ] CMAKE_EXPORT_COMPILE_COMMANDS=ON in CMakeLists.txt

### CI/CD
- [ ] .github/workflows/ci.yml exists
- [ ] Matrix includes: ubuntu (gcc, clang), macos (clang), windows (msvc)
- [ ] Separate lint and format jobs configured
- [ ] Uses Conan or vcpkg for dependency management

### EOA Compliance
- [ ] Labels configured in GitHub
- [ ] Branch follows convention: `feature/{{TASK_ID}}-*`
- [ ] Commits follow convention: `feat({{TASK_ID}}): *`
- [ ] No raw pointers or manual memory management
- [ ] All JSON output uses nlohmann::json
```

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
```
