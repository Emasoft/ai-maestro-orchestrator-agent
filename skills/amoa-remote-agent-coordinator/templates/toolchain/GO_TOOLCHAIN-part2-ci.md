# Go Toolchain - Part 2: CI/CD Configuration

**Parent**: [GO_TOOLCHAIN.md](./GO_TOOLCHAIN.md)

This file contains templates for go.mod, GitHub Actions CI, and library requirements.

---

## go.mod Template

```go
module github.com/{{GITHUB_OWNER}}/{{PROJECT_NAME}}

go 1.22

require (
	// Core dependencies
)

require (
	// Indirect dependencies (managed by go mod tidy)
)
```

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
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        go-version: ["1.22", "1.23"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Go
        uses: actions/setup-go@v5
        with:
          go-version: ${{ matrix.go-version }}
          cache: true
          cache-dependency-path: go.sum

      - name: Verify go.mod is tidy
        run: |
          go mod tidy
          git diff --exit-code go.mod go.sum

      - name: Check formatting
        run: |
          gofmt -l .
          test -z "$(gofmt -l .)"

      - name: Run go vet
        run: go vet ./...

      - name: Install golangci-lint
        run: |
          curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b $(go env GOPATH)/bin latest
          echo "$(go env GOPATH)/bin" >> $GITHUB_PATH

      - name: Run golangci-lint
        run: golangci-lint run ./... --timeout 5m

      - name: Run tests
        run: go test ./... -v -race -coverprofile=coverage.txt -covermode=atomic

      - name: Build
        run: go build -v ./...

  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Go
        uses: actions/setup-go@v5
        with:
          go-version: "1.22"
          cache: true

      - name: Run coverage
        run: go test ./... -coverprofile=coverage.out -covermode=atomic

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: coverage.out

  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    steps:
      - uses: actions/checkout@v4

      - name: Set up Go
        uses: actions/setup-go@v5
        with:
          go-version: "1.22"
          cache: true

      - name: Build binary
        run: go build -o bin/{{PROJECT_NAME}}${{ matrix.os == 'windows-latest' && '.exe' || '' }} ./cmd/{{PROJECT_NAME}}

      - name: Test binary
        run: ./bin/{{PROJECT_NAME}}${{ matrix.os == 'windows-latest' && '.exe' || '' }} --help || true
```

---

## Library Requirements (MANDATORY)

| Purpose | Library | Usage |
|---------|---------|-------|
| JSON | `encoding/json` | `json.Marshal()`, `json.Unmarshal()` |
| CLI | `github.com/spf13/cobra` | Command structure |
| HTTP Client | `net/http` | `http.Get()`, `http.Client{}` |
| HTTP Server | `net/http` | `http.ListenAndServe()` |
| Context | `context` | `context.Context`, `context.WithTimeout()` |
| Errors | `errors`, `fmt` | `errors.New()`, `fmt.Errorf()` |
| Testing | `testing` | `*testing.T`, `t.Run()` |
| Logging | `log/slog` | Structured logging (Go 1.21+) |

---

## Code Violations (Will Fail Review)

The following patterns are NOT allowed and will cause review failure:

### Manual JSON Strings
```go
// WRONG - Never do this
jsonStr := fmt.Sprintf("{\"key\":\"%s\"}", value)

// CORRECT - Use encoding/json
data := map[string]string{"key": value}
jsonBytes, _ := json.Marshal(data)
```

### Using log.Fatal() in Library Code
```go
// WRONG - Only allowed in main()
func processData() {
    log.Fatal("error occurred")  // DON'T DO THIS
}

// CORRECT - Return error instead
func processData() error {
    return fmt.Errorf("error occurred")
}
```

### Ignoring Errors
```go
// WRONG - Never ignore errors
result, _ := function()

// CORRECT - Always handle errors
result, err := function()
if err != nil {
    return fmt.Errorf("function failed: %w", err)
}
```

### Using panic() for Expected Errors
```go
// WRONG - panic is for unexpected conditions
if err != nil {
    panic(err)  // DON'T DO THIS
}

// CORRECT - Return errors
if err != nil {
    return err
}
```

### Global Mutable State
```go
// WRONG - Avoid global mutable state
var config Config  // DON'T DO THIS

// CORRECT - Pass dependencies explicitly
func New(config Config) *Service {
    return &Service{config: config}
}
```

### os.Exit() in Library Code
```go
// WRONG - Only in main package
func validate() {
    os.Exit(1)  // DON'T DO THIS
}

// CORRECT - Return error
func validate() error {
    return errors.New("validation failed")
}
```
