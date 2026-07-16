# Common Toolchain Core

The shared, language-independent core that every language toolchain template
applies before its own language-specific parts. The blocks below are byte-identical
across the C++, Go, JavaScript, Python, Rust, and Swift toolchain templates, so they
live here once instead of being repeated in each.

Each language template points back here with a line naming the sections it applies,
then supplies only what is genuinely specific to that language.

---

## §1 Workflow Trigger Header

Opens the `.github/workflows/ci.yml` of every language. Identical in all six
language templates — apply it verbatim.

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
```

Some languages insert a top-level `env:` block immediately after this header
(Rust sets `CARGO_TERM_COLOR` / `RUSTFLAGS`; Swift sets `SWIFT_VERSION`). Those
belong to the language template, not here.

---

## §2 Cross-Platform Matrix Job Scaffold

Opens the primary build/test job, immediately after §1 (and after the language's
optional `env:` block). Apply it verbatim, substituting `{{CI_JOB_NAME}}`:

```yaml
jobs:
  {{CI_JOB_NAME}}:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
```

`{{CI_JOB_NAME}}` is `test` for Go, JavaScript, and Python; `build` for C++ and
Rust. The job's `steps:` are always language-specific and stay in the language
template.

**Swift deviates and does not apply this section** — it runs a two-OS matrix
(`[ubuntu-latest, macos-latest]`, no Windows) and gives the job a display
`name:`. Its scaffold is written out in the Swift template itself.

---

## Applying This Core

1. Apply §1 verbatim.
2. Add the language's optional top-level `env:` block, if it has one.
3. Apply §2, substituting `{{CI_JOB_NAME}}` (Swift: use its own scaffold instead).
4. Continue with the language-specific `steps:` and any extra jobs (`lint`,
   `format`, `coverage`, `build`) from the language template.
