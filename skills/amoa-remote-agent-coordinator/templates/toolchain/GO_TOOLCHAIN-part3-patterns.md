# Go Toolchain - Part 3: Patterns and Verification

**Parent**: [GO_TOOLCHAIN.md](./GO_TOOLCHAIN.md)

This file contains verification checklists and common Go patterns for EOA Compliance.

---

## Verification Checklist

```markdown
## Go Toolchain Verification - {{TASK_ID}}

### Installation
- [ ] Go installed: `go version` (1.22+)
- [ ] GOPATH set: `echo $GOPATH`
- [ ] GOBIN in PATH: `which golangci-lint`

### Configuration
- [ ] go.mod exists with correct module path
- [ ] go.sum exists (after dependencies installed)
- [ ] .golangci.yml exists with EOA standard config
- [ ] Standard directory structure: cmd/, pkg/, internal/, test/

### Verification Commands Pass
- [ ] `go fmt ./...` - formatting correct (no output)
- [ ] `go vet ./...` - static analysis passes
- [ ] `golangci-lint run ./...` - no linting errors
- [ ] `go test ./...` - all tests pass
- [ ] `go test ./... -race` - no race conditions
- [ ] `go build ./cmd/{{PROJECT_NAME}}` - builds successfully

### CI/CD
- [ ] .github/workflows/ci.yml exists
- [ ] Uses `actions/setup-go@v5`
- [ ] Matrix includes: ubuntu, macos, windows
- [ ] Tests run with `-race` flag
- [ ] Coverage job configured
- [ ] go.mod tidy check present

### EOA Compliance
- [ ] Labels configured in GitHub
- [ ] Branch follows convention
- [ ] Commits follow convention
- [ ] No `log.Fatal()` in library code
- [ ] All errors properly checked
- [ ] Uses structured logging (slog)
```

---

## Common Go Patterns for EOA

### Error Handling Pattern

```go
// CORRECT: Return errors, don't panic
func process() error {
    if err := validate(); err != nil {
        return fmt.Errorf("validation failed: %w", err)
    }
    return nil
}

// WRONG: Using panic for normal errors
func process() {
    if err := validate(); err != nil {
        panic(err) // DON'T DO THIS
    }
}
```

### JSON Handling Pattern

```go
// CORRECT: Use json.Marshal/Unmarshal
data := map[string]string{"key": "value"}
jsonBytes, err := json.Marshal(data)
if err != nil {
    return err
}

// WRONG: Manual JSON strings
jsonStr := fmt.Sprintf("{\"key\":\"%s\"}", value) // DON'T DO THIS
```

### CLI Structure with Cobra

```go
package main

import (
    "github.com/spf13/cobra"
    "os"
)

func main() {
    if err := rootCmd.Execute(); err != nil {
        os.Exit(1)
    }
}

var rootCmd = &cobra.Command{
    Use:   "{{PROJECT_NAME}}",
    Short: "Description",
    RunE: func(cmd *cobra.Command, args []string) error {
        return run()
    },
}

func run() error {
    // Implementation
    return nil
}
```

### Testing Pattern (Table-Driven Tests)

```go
package main

import "testing"

func TestFunction(t *testing.T) {
    tests := []struct {
        name    string
        input   string
        want    string
        wantErr bool
    }{
        {
            name:  "valid input",
            input: "test",
            want:  "test-result",
        },
        {
            name:    "invalid input",
            input:   "",
            wantErr: true,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := function(tt.input)
            if (err != nil) != tt.wantErr {
                t.Errorf("wantErr = %v, error = %v", tt.wantErr, err)
                return
            }
            if got != tt.want {
                t.Errorf("got = %v, want %v", got, tt.want)
            }
        })
    }
}
```

---

## Context Pattern

```go
import (
    "context"
    "time"
)

func fetchWithTimeout(ctx context.Context, url string) error {
    // Create context with timeout
    ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
    defer cancel()

    // Use context in HTTP request
    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return fmt.Errorf("create request: %w", err)
    }

    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return fmt.Errorf("execute request: %w", err)
    }
    defer resp.Body.Close()

    return nil
}
```

---

## Structured Logging Pattern (slog)

```go
import "log/slog"

func main() {
    // Create structured logger
    logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
    slog.SetDefault(logger)

    // Log with context
    slog.Info("starting service",
        "version", "1.0.0",
        "port", 8080,
    )

    // Log errors with context
    if err := run(); err != nil {
        slog.Error("service failed",
            "error", err,
        )
        os.Exit(1)
    }
}
```

---

## Graceful Shutdown Pattern

```go
func main() {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    // Handle shutdown signals
    sigCh := make(chan os.Signal, 1)
    signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)

    go func() {
        <-sigCh
        slog.Info("shutdown signal received")
        cancel()
    }()

    if err := run(ctx); err != nil {
        slog.Error("service failed", "error", err)
        os.Exit(1)
    }
}
```
