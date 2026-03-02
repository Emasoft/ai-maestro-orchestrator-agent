# Automation Scripts


## Contents

- [Table of Contents](#table-of-contents)
- [11.1 Traceability and Requirements Scripts](#111-traceability-and-requirements-scripts)
  - [traceability_validator.py](#traceability_validatorpy)
- [11.2 Evidence Collection Scripts](#112-evidence-collection-scripts)
  - [evidence_store.py](#evidence_storepy)
- [11.3 Consistency and Verification Scripts](#113-consistency-and-verification-scripts)
  - [consistency_verifier.py](#consistency_verifierpy)
  - [with_server.py](#with_serverpy)
- [11.4 Code Quality Scripts](#114-code-quality-scripts)
  - [quality_pattern_detector.py](#quality_pattern_detectorpy)
- [11.5 Scoring and Analysis Scripts](#115-scoring-and-analysis-scripts)
  - [scoring_framework.py](#scoring_frameworkpy)
  - [comparison_analyzer.py](#comparison_analyzerpy)
- [11.6 Testing and Validation Scripts](#116-testing-and-validation-scripts)
  - [ab_test_calculator.py](#ab_test_calculatorpy)
  - [checklist_validator.py](#checklist_validatorpy)

---

## Table of Contents

- [11.1 Traceability and Requirements Scripts](#111-traceability-and-requirements-scripts)
  - 11.1.1 traceability_validator.py usage
  - 11.1.2 Purpose and features
  - 11.1.3 When to use
- [11.2 Evidence Collection Scripts](#112-evidence-collection-scripts)
  - 11.2.1 evidence_store.py add, filter, stats commands
  - 11.2.2 Evidence types: FINDING, OBSERVATION, EVENT, ISSUE
  - 11.2.3 Features: deduplication, filtering, persistence
- [11.3 Consistency and Verification Scripts](#113-consistency-and-verification-scripts)
  - 11.3.1 consistency_verifier.py file, git, url, json, batch
  - 11.3.2 with_server.py multi-server orchestration
- [11.4 Code Quality Scripts](#114-code-quality-scripts)
  - 11.4.1 quality_pattern_detector.py usage
  - 11.4.2 Built-in anti-patterns
  - 11.4.3 Supported languages
- [11.5 Scoring and Analysis Scripts](#115-scoring-and-analysis-scripts)
  - 11.5.1 scoring_framework.py weighted scoring
  - 11.5.2 comparison_analyzer.py gap analysis
- [11.6 Testing and Validation Scripts](#116-testing-and-validation-scripts)
  - 11.6.1 ab_test_calculator.py statistical testing
  - 11.6.2 checklist_validator.py dependency tracking

---

## 11.1 Traceability and Requirements Scripts

### traceability_validator.py

```bash
python scripts/traceability_validator.py --requirements reqs.md --implementation impl/
```

**Purpose:** Validate 100% requirements coverage and research citations

**Features:**
- Verifies all requirements have corresponding implementation
- Validates research citations are properly referenced
- Generates traceability matrix
- Reports coverage percentage
- Flags orphaned implementations (code without requirements)

**When to Use:**
- Before marking a feature as complete
- During code review to ensure all requirements are met
- When validating research-backed implementations
- As part of CI/CD pipeline to enforce traceability standards

---

## 11.2 Evidence Collection Scripts

### evidence_store.py

```bash
# Add evidence and save to file
python scripts/evidence_store.py add --type finding --source "audit.py" --content "SQL injection vulnerability" --output evidence.json

# Filter evidence by type
python scripts/evidence_store.py filter --input evidence.json --type issue --output issues.json

# Generate statistics
python scripts/evidence_store.py stats --input evidence.json
```

**Purpose:** Polymorphic evidence collection with deduplication and filtering

**Evidence Types:**

| Type | Description |
|------|-------------|
| `FINDING` | Discovered issues or problems |
| `OBSERVATION` | Neutral observations during analysis |
| `EVENT` | Timestamped occurrences |
| `ISSUE` | Tracked problems requiring resolution |

**Features:**
- Automatic deduplication by content hash
- Time-range filtering
- Custom predicate filtering
- JSON persistence with atomic writes

---

## 11.3 Consistency and Verification Scripts

### consistency_verifier.py

```bash
# Verify a file exists and matches checksum
python scripts/consistency_verifier.py file --path config.json --checksum abc123

# Verify git branch state
python scripts/consistency_verifier.py git --path /repo --branch main --clean

# Verify URL is accessible
python scripts/consistency_verifier.py url --url https://api.example.com/health --status 200

# Verify JSON structure
python scripts/consistency_verifier.py json --path data.json --has-keys "name,version,dependencies"

# Batch verification from config
python scripts/consistency_verifier.py batch --config checks.json --output report.json
```

**Purpose:** Source-routed verification with pluggable backends

**Verification Types:**

| Type | What it verifies |
|------|------------------|
| `file` | File existence, checksum, size, permissions |
| `git` | Branch state, clean status, commit presence |
| `url` | HTTP status, response content, headers |
| `json` | Structure validation, required keys, schema |

**Features:**
- Batch verification with error aggregation
- Parallel execution for performance
- Detailed failure reporting

### with_server.py

```bash
# Start server, run tests, cleanup
python scripts/with_server.py --server "python -m http.server 8080" --port 8080 -- pytest tests/

# Multiple servers
python scripts/with_server.py \
  --server "docker-compose up" --port 5432 \
  --server "npm run dev" --port 3000 \
  -- npm test
```

**Purpose:** Server orchestration for integration testing

**Features:**
- Multi-server startup with port polling
- Graceful cleanup via SIGTERM/SIGKILL
- Configurable startup timeout
- Exit code propagation from test command

---

## 11.4 Code Quality Scripts

### quality_pattern_detector.py

```bash
# Detect anti-patterns in Python files
python scripts/quality_pattern_detector.py --path src/ --lang python

# Detect all patterns with JSON output
python scripts/quality_pattern_detector.py --path . --format json --output patterns.json

# Custom pattern detection
python scripts/quality_pattern_detector.py --path src/ --pattern "TODO|FIXME|HACK" --name "technical-debt"
```

**Purpose:** Regex-based multi-language anti-pattern detection

**Built-in Patterns:**

| Pattern | Description |
|---------|-------------|
| `hardcoded-secret` | API keys, passwords in code |
| `sql-injection` | String concatenation in SQL |
| `eval-usage` | Dynamic code execution |
| `any-usage` | TypeScript `any` type |
| `bare-except` | Python bare except clauses |
| `mutable-default` | Mutable default arguments |
| `console-log` | Debug statements left in code |
| `magic-number` | Unexplained numeric literals |

**Languages:** Python, TypeScript, JavaScript, Go, Rust, Java

---

## 11.5 Scoring and Analysis Scripts

### scoring_framework.py

```bash
# Score entities from CSV
python scripts/scoring_framework.py --entities products.csv --metrics metrics.json --output scores.json

# Rank and export top N
python scripts/scoring_framework.py --entities data.json --metrics config.json --top 10 --format markdown
```

**Purpose:** Weighted multi-dimension scoring for entity comparison

**Normalization Functions:**

| Function | Description |
|----------|-------------|
| `linear` | Min-max scaling to 0-1 |
| `log` | Logarithmic scaling for exponential data |
| `sigmoid` | S-curve normalization for bounded output |
| `inverse` | Inverse scaling (lower is better) |

**Features:**
- Configurable weights per metric
- Multiple normalization strategies
- Ranking with tie-breaking
- Export to JSON, CSV, Markdown

### comparison_analyzer.py

```bash
# Compare against baseline
python scripts/comparison_analyzer.py --baseline v1.json --target v2.json --output gaps.json

# Multi-entity comparison
python scripts/comparison_analyzer.py --baseline reference.json --targets "a.json,b.json,c.json" --report comparison.md
```

**Purpose:** Gap analysis with baseline comparison

**Features:**
- Strengths and weaknesses identification
- Percentage difference calculation
- Automated recommendations generation
- Multi-dimensional comparison support

---

## 11.6 Testing and Validation Scripts

### ab_test_calculator.py

```bash
# Calculate significance for conversion test
python scripts/ab_test_calculator.py --control-conv 0.12 --control-n 1000 --variant-conv 0.15 --variant-n 1000

# Full analysis with confidence intervals
python scripts/ab_test_calculator.py --input test_data.json --output results.json --confidence 0.95
```

**Purpose:** Statistical hypothesis testing for A/B tests

**Tests:**
- Chi-square test for categorical data
- Z-test for conversion rate comparison
- T-test for continuous metrics

**Features:**
- Confidence interval calculation
- Sample size recommendations
- Power analysis
- Effect size calculation

### checklist_validator.py

```bash
# Validate checklist completion
python scripts/checklist_validator.py --checklist release.json --status progress.json

# Get next actions
python scripts/checklist_validator.py --checklist tasks.json --status current.json --next-actions

# Detect blockers
python scripts/checklist_validator.py --checklist workflow.json --status state.json --blockers
```

**Purpose:** Hierarchical checklist validation with dependency tracking

**Features:**
- Dependency-aware progress tracking
- Circular dependency detection via DFS
- Blocker identification
- Next-action recommendations
- Progress percentage calculation
