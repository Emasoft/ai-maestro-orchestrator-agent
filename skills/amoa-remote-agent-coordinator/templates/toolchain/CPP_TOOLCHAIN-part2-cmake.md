# C/C++ Toolchain - Part 2: CMake Templates

**Parent document**: [CPP_TOOLCHAIN.md](CPP_TOOLCHAIN.md)

---

## CMakeLists.txt Template

```cmake
cmake_minimum_required(VERSION 3.25)
project({{PROJECT_NAME}}
    VERSION 0.1.0
    DESCRIPTION "{{DESCRIPTION}}"
    LANGUAGES CXX
)

# ============================================================
# Configuration
# ============================================================

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Export compile commands for clang-tidy
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# ============================================================
# Conan Integration
# ============================================================

# Include Conan toolchain if it exists
if(EXISTS "${CMAKE_BINARY_DIR}/conan_toolchain.cmake")
    include("${CMAKE_BINARY_DIR}/conan_toolchain.cmake")
endif()

# ============================================================
# Dependencies
# ============================================================

find_package(nlohmann_json REQUIRED)
find_package(CLI11 REQUIRED)

# ============================================================
# Target Definition
# ============================================================

add_executable(${PROJECT_NAME}
    src/main.cpp
    # Add more sources here
)

target_include_directories(${PROJECT_NAME}
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_link_libraries(${PROJECT_NAME}
    PRIVATE
        nlohmann_json::nlohmann_json
        CLI11::CLI11
)

# Compiler warnings
target_compile_options(${PROJECT_NAME}
    PRIVATE
        $<$<CXX_COMPILER_ID:GNU,Clang>:-Wall -Wextra -Wpedantic -Werror>
        $<$<CXX_COMPILER_ID:MSVC>:/W4 /WX>
)

# ============================================================
# Testing
# ============================================================

enable_testing()

add_subdirectory(tests)

# ============================================================
# Installation
# ============================================================

install(TARGETS ${PROJECT_NAME}
    RUNTIME DESTINATION bin
)
```

---

## tests/CMakeLists.txt Template

```cmake
# Test executable
add_executable(${PROJECT_NAME}_tests
    test_main.cpp
    # Add more test files here
)

target_link_libraries(${PROJECT_NAME}_tests
    PRIVATE
        nlohmann_json::nlohmann_json
)

target_include_directories(${PROJECT_NAME}_tests
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/../src
)

# Register tests with CTest
add_test(NAME ${PROJECT_NAME}_tests COMMAND ${PROJECT_NAME}_tests)
```

---

## conanfile.txt Template

```ini
[requires]
nlohmann_json/3.11.3
cli11/2.4.1

[generators]
CMakeDeps
CMakeToolchain

[options]
# Add package-specific options here

[layout]
cmake_layout
```

---

## Alternative: vcpkg.json Template

```json
{
  "name": "{{PROJECT_NAME}}",
  "version": "0.1.0",
  "dependencies": [
    "nlohmann-json",
    "cli11"
  ],
  "builtin-baseline": "latest"
}
```
