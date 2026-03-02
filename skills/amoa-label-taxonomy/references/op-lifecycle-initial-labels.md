---
procedure: support-skill
workflow-instruction: support
---

# Operation: Set Initial Labels on Issue Creation


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Determine Issue Type](#step-1-determine-issue-type)
  - [Step 2: Identify Component (if known)](#step-2-identify-component-if-known)
  - [Step 3: Apply Initial Labels](#step-3-apply-initial-labels)
  - [Step 4: Verify Labels Applied](#step-4-verify-labels-applied)
- [Output](#output)
- [Error Handling](#error-handling)
- [Examples](#examples)
  - [Example 1: Bug Report](#example-1-bug-report)
  - [Example 2: Feature Request](#example-2-feature-request)
  - [Example 3: Unknown Component](#example-3-unknown-component)
- [Checklist](#checklist)

## When to Use

Use this operation when a new issue is created and needs its initial labels set.

## Prerequisites

- Issue has just been created
- GitHub CLI (`gh`) authenticated
- Understanding of required minimum labels

## Procedure

### Step 1: Determine Issue Type

Analyze the issue content to identify its type:

| Type Label | Indicators |
|------------|------------|
| `type:bug` | Error report, regression, unexpected behavior |
| `type:feature` | New functionality request |
| `type:enhancement` | Improvement to existing feature |
| `type:docs` | Documentation changes |
| `type:test` | Test additions or fixes |
| `type:refactor` | Code restructuring without behavior change |
| `type:chore` | Maintenance, dependencies, tooling |

### Step 2: Identify Component (if known)

If the issue content indicates affected areas:

| Component Label | Scope |
|-----------------|-------|
| `component:api` | API endpoints, REST interfaces |
| `component:auth` | Authentication, authorization |
| `component:ui` | User interface |
| `component:core` | Core logic, business rules |
| `component:infra` | Infrastructure, deployment |
| `component:tests` | Test infrastructure |

### Step 3: Apply Initial Labels

```bash
# Minimum required labels for new issue
gh issue edit <ISSUE_NUM> \
  --add-label "type:<type>,status:backlog"

# With component if known
gh issue edit <ISSUE_NUM> \
  --add-label "type:<type>,status:backlog,component:<component>"
```

### Step 4: Verify Labels Applied

```bash
gh issue view <ISSUE_NUM> --json labels --jq '.labels[].name'
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| Labels Applied | Array | List of initial labels set |
| Issue State | String | Issue now has `status:backlog` |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Cannot determine type | Issue content unclear | Default to `type:bug` and note in comment |
| Multiple types seem applicable | Ambiguous issue | Choose primary type, note others in comment |

## Examples

### Example 1: Bug Report

```bash
# User reports: "Login fails with error 500"
gh issue edit 123 --add-label "type:bug,status:backlog,component:auth"
```

### Example 2: Feature Request

```bash
# User requests: "Add dark mode support"
gh issue edit 124 --add-label "type:feature,status:backlog,component:ui"
```

### Example 3: Unknown Component

```bash
# Issue unclear on affected component
gh issue edit 125 --add-label "type:enhancement,status:backlog"
gh issue comment 125 --body "Issue triaged. Component will be determined during detailed analysis."
```

## Checklist

- [ ] Read issue content to determine type
- [ ] Identify component if mentioned
- [ ] Apply `type:*` label (required)
- [ ] Apply `status:backlog` (required)
- [ ] Apply `component:*` if known (optional at this stage)
- [ ] Verify labels with `gh issue view`
