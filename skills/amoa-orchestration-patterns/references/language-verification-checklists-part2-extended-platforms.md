# Language-Specific Verification Checklists - Part 2: Extended Platforms


## Contents

- [Table of Contents](#table-of-contents)
- [C#/.NET Verification Checklist](#cnet-verification-checklist)
  - [Core Requirements](#core-requirements)
  - [Build and Distribution](#build-and-distribution)
  - [Optional (Recommended)](#optional-recommended)
- [Unity Verification Checklist](#unity-verification-checklist)
  - [Core Requirements](#core-requirements)
  - [Unity-Specific Patterns](#unity-specific-patterns)
  - [Build](#build)
  - [Optional (Recommended)](#optional-recommended)
- [Android Verification Checklist](#android-verification-checklist)
  - [Core Requirements](#core-requirements)
  - [Jetpack Compose Patterns](#jetpack-compose-patterns)
  - [Kotlin Coroutines](#kotlin-coroutines)
  - [Release Checklist](#release-checklist)
- [C/C++ Verification Checklist](#cc-verification-checklist)
  - [Core Requirements (CMake)](#core-requirements-cmake)
  - [Modern C++ Patterns](#modern-c-patterns)
  - [C-Specific (No C++)](#c-specific-no-c)
- [Flutter Verification Checklist](#flutter-verification-checklist)
  - [Core Requirements](#core-requirements)
  - [Flutter-Specific Patterns](#flutter-specific-patterns)
  - [Platform Channels](#platform-channels)
- [React Native Verification Checklist](#react-native-verification-checklist)
  - [Core Requirements](#core-requirements)
  - [React Native Patterns](#react-native-patterns)
  - [iOS-Specific](#ios-specific)
- [ML/AI Verification Checklist (PyTorch, HuggingFace)](#mlai-verification-checklist-pytorch-huggingface)
  - [Core Requirements](#core-requirements)
  - [PyTorch-Specific](#pytorch-specific)
  - [HuggingFace Transformers](#huggingface-transformers)
  - [HuggingFace Diffusers](#huggingface-diffusers)
  - [Experiment Tracking](#experiment-tracking)
- [Embedded/IoT Verification Checklist](#embeddediot-verification-checklist)
  - [Core Requirements](#core-requirements)
  - [Embedded-Specific Patterns](#embedded-specific-patterns)
  - [Hardware Testing](#hardware-testing)
- [Extending This Document](#extending-this-document)
- [Related Documents](#related-documents)

---

This document provides comprehensive verification checklists for extended platforms and specialized development environments (C#/.NET, Unity, Android, C/C++, Flutter, React Native, ML/AI, Embedded/IoT).

## Table of Contents

- [C#/.NET Verification Checklist](#cnet-verification-checklist)
  - Core Requirements
  - Build and Distribution
  - Optional (Recommended)
- [Unity Verification Checklist](#unity-verification-checklist)
  - Core Requirements
  - Unity-Specific Patterns
  - Build
  - Optional (Recommended)
- [Android Verification Checklist](#android-verification-checklist)
  - Core Requirements
  - Jetpack Compose Patterns
  - Kotlin Coroutines
  - Release Checklist
- [C/C++ Verification Checklist](#cc-verification-checklist)
  - Core Requirements (CMake)
  - Modern C++ Patterns
  - C-Specific (No C++)
- [Flutter Verification Checklist](#flutter-verification-checklist)
  - Core Requirements
  - Flutter-Specific Patterns
  - Platform Channels
- [React Native Verification Checklist](#react-native-verification-checklist)
  - Core Requirements
  - React Native Patterns
  - iOS-Specific
- [ML/AI Verification Checklist](#mlai-verification-checklist-pytorch-huggingface)
  - Core Requirements
  - PyTorch-Specific
  - HuggingFace Transformers
  - HuggingFace Diffusers
  - Experiment Tracking
- [Embedded/IoT Verification Checklist](#embeddediot-verification-checklist)
  - Core Requirements
  - Embedded-Specific Patterns
  - Hardware Testing
- [Extending This Document](#extending-this-document)

---

## C#/.NET Verification Checklist

Use this checklist for C#/.NET projects (ASP.NET, Console apps, Libraries).

### Core Requirements
- [ ] **Project file** (.csproj or .sln) complete
  - [ ] TargetFramework specified (net6.0, net7.0, net8.0, net9.0)
  - [ ] `<Nullable>enable</Nullable>` enabled
  - [ ] `<ImplicitUsings>enable</ImplicitUsings>` (for modern C#)
  - [ ] Package references with versions
  - [ ] XML documentation enabled (if library)
- [ ] **dotnet build** succeeds
  - [ ] Run: `dotnet build --no-restore`
  - [ ] Zero errors, zero warnings (or TreatWarningsAsErrors)
  - [ ] All target frameworks build
- [ ] **dotnet test** passes
  - [ ] Run: `dotnet test --no-build`
  - [ ] All tests pass
  - [ ] Coverage >80%: `dotnet test --collect:"XPlat Code Coverage"`
- [ ] **dotnet format** passes
  - [ ] Run: `dotnet format --verify-no-changes`
  - [ ] Zero formatting issues
  - [ ] EditorConfig rules enforced
- [ ] **Analyzers** pass
  - [ ] StyleCop.Analyzers or Roslynator enabled
  - [ ] Zero analyzer warnings
- [ ] **README.md** with usage
  - [ ] Installation: `dotnet add package`
  - [ ] Build instructions
  - [ ] Usage examples

### Build and Distribution
- [ ] **NuGet package builds**: `dotnet pack -c Release`
- [ ] **Package metadata complete**: title, description, tags, license
- [ ] **Installation from package works**: `dotnet add package ./bin/Release/*.nupkg`

### Optional (Recommended)
- [ ] Central Package Management (Directory.Packages.props)
- [ ] GitHub Actions CI
- [ ] DocFX or xmldoc for documentation

---

## Unity Verification Checklist

Use this checklist for Unity game projects.

### Core Requirements
- [ ] **Unity version** matches project
  - [ ] Check ProjectSettings/ProjectVersion.txt
  - [ ] Unity Hub shows correct version
- [ ] **Package dependencies** resolved
  - [ ] Packages/manifest.json valid
  - [ ] All packages cached/installed
- [ ] **Assembly definitions** (.asmdef) configured
  - [ ] Runtime assemblies defined
  - [ ] Editor assemblies separated
  - [ ] Test assemblies configured
- [ ] **Console clean** (no errors)
  - [ ] Open Unity Console (Ctrl+Shift+C)
  - [ ] Zero red errors
  - [ ] Warnings reviewed
- [ ] **Play mode** works
  - [ ] Press Play in Editor
  - [ ] No runtime exceptions
  - [ ] Core gameplay functional
- [ ] **Tests pass**
  - [ ] Edit Mode tests: Window > General > Test Runner
  - [ ] Play Mode tests: All pass
  - [ ] Run via CLI: `Unity -batchmode -runTests -testPlatform PlayMode`

### Unity-Specific Patterns
- [ ] **MonoBehaviour lifecycle** respected
  - [ ] Awake -> OnEnable -> Start -> Update -> LateUpdate order
  - [ ] No heavy work in Update (use coroutines/jobs)
- [ ] **Serialization** correct
  - [ ] `[SerializeField]` for inspector fields (not public)
  - [ ] `[System.Serializable]` for nested classes
  - [ ] ScriptableObjects for shared data
- [ ] **Performance patterns**
  - [ ] No Find() in Update loops
  - [ ] Object pooling for frequently instantiated objects
  - [ ] Coroutines stopped in OnDisable/OnDestroy

### Build
- [ ] **Build succeeds**: File > Build Settings > Build
- [ ] **Target platform configured**
- [ ] **Player settings complete**: Icons, splash, bundle ID

### Optional (Recommended)
- [ ] Addressables for asset management
- [ ] CI/CD with GameCI or custom Unity CLI scripts
- [ ] Profiler checks before release

---

## Android Verification Checklist

Use this checklist for Android projects (Native Kotlin/Java, Jetpack Compose).

### Core Requirements
- [ ] **Gradle files** complete
  - [ ] build.gradle.kts (or .gradle) valid
  - [ ] Correct Gradle version in gradle-wrapper.properties
  - [ ] AGP (Android Gradle Plugin) up to date
- [ ] **SDK requirements** met
  - [ ] compileSdk, targetSdk, minSdk set
  - [ ] targetSdk meets Play Store requirements
- [ ] **Build succeeds**
  - [ ] Run: `./gradlew assembleDebug`
  - [ ] Run: `./gradlew assembleRelease`
  - [ ] Zero errors
- [ ] **Tests pass**
  - [ ] Unit tests: `./gradlew test`
  - [ ] Instrumented: `./gradlew connectedAndroidTest`
- [ ] **Lint passes**
  - [ ] Run: `./gradlew lint`
  - [ ] Zero critical issues
  - [ ] ktlint or detekt for Kotlin

### Jetpack Compose Patterns
- [ ] **State management** correct
  - [ ] `remember { mutableStateOf() }` for local state
  - [ ] `rememberSaveable` for config change survival
  - [ ] ViewModel for shared/persistent state
- [ ] **Side effects** proper
  - [ ] `LaunchedEffect` for coroutines on composition
  - [ ] `DisposableEffect` for cleanup
  - [ ] Never call suspend functions in composition

### Kotlin Coroutines
- [ ] **Scope management**
  - [ ] viewModelScope or lifecycleScope (NEVER GlobalScope)
  - [ ] `repeatOnLifecycle` for Flow collection
  - [ ] Cancellation handled properly

### Release Checklist
- [ ] **ProGuard/R8 rules** configured
- [ ] **Signing config** for release builds
- [ ] **Version code/name** incremented
- [ ] **Privacy policy** URL set

---

## C/C++ Verification Checklist

Use this checklist for C/C++ projects (CMake, Makefile, embedded).

### Core Requirements (CMake)
- [ ] **CMakeLists.txt** complete
  - [ ] cmake_minimum_required(VERSION 3.14+)
  - [ ] project() with version and languages
  - [ ] target_* commands (not global)
  - [ ] FetchContent for dependencies
- [ ] **cmake configure** succeeds
  - [ ] Run: `cmake -B build -DCMAKE_BUILD_TYPE=Release`
  - [ ] Zero errors
- [ ] **cmake build** succeeds
  - [ ] Run: `cmake --build build`
  - [ ] Zero warnings with `-Wall -Wextra -Werror`
- [ ] **Tests pass**
  - [ ] Run: `ctest --test-dir build`
  - [ ] All tests pass
- [ ] **Sanitizers clean**
  - [ ] AddressSanitizer: `-fsanitize=address`
  - [ ] UndefinedBehaviorSanitizer: `-fsanitize=undefined`
  - [ ] ThreadSanitizer: `-fsanitize=thread` (for multi-threaded)
- [ ] **clang-format** applied
  - [ ] Run: `clang-format -i src/*.cpp include/*.h`
  - [ ] .clang-format in repository
- [ ] **clang-tidy** passes
  - [ ] Run: `clang-tidy src/*.cpp`
  - [ ] Zero warnings

### Modern C++ Patterns
- [ ] **Smart pointers** over raw pointers
  - [ ] std::unique_ptr for single ownership
  - [ ] std::shared_ptr only when truly shared
  - [ ] No naked new/delete
- [ ] **RAII** for all resources
- [ ] **const correctness** enforced
- [ ] **noexcept** where applicable

### C-Specific (No C++)
- [ ] **No buffer overflows**
  - [ ] strncpy, snprintf (not strcpy, sprintf)
  - [ ] Bounds checking on all arrays
- [ ] **Memory management**
  - [ ] All malloc paired with free
  - [ ] Pointers set to NULL after free
- [ ] **No undefined behavior**
  - [ ] Variables initialized before use
  - [ ] No signed integer overflow

---

## Flutter Verification Checklist

Use this checklist for Flutter mobile/web projects.

### Core Requirements
- [ ] **pubspec.yaml** complete
  - [ ] name, description, version
  - [ ] SDK constraints (sdk: '>=3.0.0 <4.0.0')
  - [ ] Dependencies pinned
  - [ ] Assets declared
- [ ] **flutter analyze** passes
  - [ ] Run: `flutter analyze`
  - [ ] Zero errors, zero warnings
- [ ] **flutter test** passes
  - [ ] Run: `flutter test`
  - [ ] All tests pass
  - [ ] Run: `flutter test --coverage`
  - [ ] Coverage >80%
- [ ] **dart format** applied
  - [ ] Run: `dart format .`
  - [ ] All files formatted
- [ ] **Build succeeds**
  - [ ] Android: `flutter build apk`
  - [ ] iOS: `flutter build ios` (on macOS)
  - [ ] Web: `flutter build web`

### Flutter-Specific Patterns
- [ ] **Widget lifecycle** correct
  - [ ] `super.initState()` called first
  - [ ] `super.dispose()` called last
  - [ ] Controllers disposed in dispose()
- [ ] **State management** consistent
  - [ ] Provider, Riverpod, or Bloc
  - [ ] `setState()` only for local widget state
- [ ] **Keys** used for stateful widgets in lists
- [ ] **const constructors** where possible

### Platform Channels
- [ ] **Platform exceptions** handled
- [ ] **Main thread** not blocked
- [ ] **Async** properly awaited

---

## React Native Verification Checklist

Use this checklist for React Native mobile projects.

### Core Requirements
- [ ] **package.json** complete
  - [ ] dependencies and devDependencies
  - [ ] react-native version specified
  - [ ] scripts for build/test/lint
- [ ] **Metro bundler** starts
  - [ ] Run: `bunx react-native start` (or npx)
  - [ ] No bundler errors
- [ ] **TypeScript** configured
  - [ ] tsconfig.json with strict mode
  - [ ] tsc --noEmit passes
- [ ] **ESLint** passes
  - [ ] Run: `bun run lint` (or npm/yarn)
  - [ ] Zero errors
- [ ] **Tests pass**
  - [ ] Run: `bun test`
  - [ ] Jest tests pass
  - [ ] Detox E2E tests pass (if configured)
- [ ] **Builds succeed**
  - [ ] Android: `bunx react-native run-android`
  - [ ] iOS: `bunx react-native run-ios`

### React Native Patterns
- [ ] **Bridge crossings** minimized
  - [ ] Batch native calls
  - [ ] Use Turbo Modules where possible
- [ ] **Navigation** type-safe
  - [ ] RootStackParamList defined
  - [ ] useNavigation properly typed
- [ ] **FlatList** for long lists (not ScrollView)
- [ ] **Hermes** enabled for performance

### iOS-Specific
- [ ] **Pods installed**: `cd ios && pod install`
- [ ] **Xcode build succeeds**

---

## ML/AI Verification Checklist (PyTorch, HuggingFace)

Use this checklist for machine learning projects.

### Core Requirements
- [ ] **Environment reproducible**
  - [ ] requirements.txt or pyproject.toml
  - [ ] Python version specified
  - [ ] CUDA version documented (if GPU)
- [ ] **Seeds set** for reproducibility
  - [ ] torch.manual_seed(seed)
  - [ ] numpy.random.seed(seed)
  - [ ] random.seed(seed)
- [ ] **Code quality**
  - [ ] ruff check passes
  - [ ] mypy passes (with torch stubs)
- [ ] **Tests pass**
  - [ ] pytest for non-training code
  - [ ] Smoke tests for model loading

### PyTorch-Specific
- [ ] **Device management** consistent
  - [ ] `.to(device)` on all tensors and models
  - [ ] torch.cuda.is_available() checked
- [ ] **Gradient management** correct
  - [ ] optimizer.zero_grad() before backward()
  - [ ] torch.no_grad() for inference
  - [ ] .detach() for tensors stored outside graph
- [ ] **Memory management**
  - [ ] No GPU memory leaks
  - [ ] .item() for scalar logging

### HuggingFace Transformers
- [ ] **Model loading** correct
  - [ ] AutoModel/AutoTokenizer used
  - [ ] trust_remote_code=True only if needed
  - [ ] torch_dtype specified (float16/bfloat16)
- [ ] **Tokenization** configured
  - [ ] padding and truncation set
  - [ ] return_tensors='pt' for PyTorch
  - [ ] max_length within model limits

### HuggingFace Diffusers
- [ ] **Pipeline loading** efficient
  - [ ] torch_dtype=torch.float16
  - [ ] use_safetensors=True
- [ ] **Memory optimizations** enabled
  - [ ] enable_attention_slicing()
  - [ ] enable_vae_slicing()
  - [ ] enable_model_cpu_offload() for low VRAM

### Experiment Tracking
- [ ] **Metrics logged** (W&B, TensorBoard, MLflow)
- [ ] **Checkpoints saved** regularly
- [ ] **Config/hyperparameters** tracked

---

## Embedded/IoT Verification Checklist

Use this checklist for embedded systems (Arduino, PlatformIO, bare-metal).

### Core Requirements
- [ ] **platformio.ini** or equivalent configured
  - [ ] Board specified
  - [ ] Framework (arduino, espidf, etc.)
  - [ ] Platform libraries listed
- [ ] **Build succeeds**
  - [ ] Run: `pio run`
  - [ ] Zero errors
- [ ] **Upload succeeds** (hardware connected)
  - [ ] Run: `pio run --target upload`
  - [ ] Device responds

### Embedded-Specific Patterns
- [ ] **ISR safety**
  - [ ] ISRs are short and fast
  - [ ] volatile for ISR-shared variables
  - [ ] No printf/malloc in ISRs
- [ ] **Memory constraints** respected
  - [ ] Stack usage checked (`-fstack-usage`)
  - [ ] Heap minimized on constrained devices
  - [ ] PROGMEM for constant strings (AVR)
- [ ] **Real-time constraints**
  - [ ] No blocking delays in time-critical code
  - [ ] Timer interrupts for precise timing
  - [ ] Watchdog fed regularly

### Hardware Testing
- [ ] **Logic analyzer** traces verified
- [ ] **Serial output** checked
- [ ] **Power consumption** measured (battery devices)

---

## Extending This Document

To add a new language or platform:
1. Create a new section with "## Language Name Verification Checklist"
2. List core requirements (build, test, lint, format)
3. Include language-specific tools and patterns
4. Provide optional recommendations
5. Add troubleshooting tips specific to that language/platform

---

## Related Documents

- [Part 1: Core Languages](language-verification-checklists-part1-core-languages.md) - Python, Go, JavaScript/TypeScript, Rust, Swift, Universal TDD, Orchestration Usage, Automation Scripts, Troubleshooting
