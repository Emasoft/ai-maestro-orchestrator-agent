# Templates for Human Communication - Part 5: Migration Guides

## Contents

- 6.5 Migration guide structure
  - 6.5.1 Before/after examples
  - 6.5.2 Step-by-step instructions
  - 6.5.3 Common issues and solutions
- Complete PR Template

---

## 6.5 Migration Guide Structure

Migration guides help users move between versions. Make them comprehensive and example-driven.

### 6.5.1 Before/After Examples

Show exact transformations from old to new.

**Template**:
```markdown
## Migrating [Feature Name]

### Before (v1)
```[language]
[Old code or configuration]
```

### After (v2)
```[language]
[New code or configuration]
```

### What Changed
- [Change 1]
- [Change 2]
```

**Example**:
```markdown
## Migrating Authentication

### Before (v1)
```javascript
// v1: Initialize with API key in code
const client = new ApiClient({
  apiKey: 'sk_live_xxxxx'
});
```

### After (v2)
```javascript
// v2: Initialize with environment variable
const client = new ApiClient();
// API key read from EXAMPLE_API_KEY env var
```

### What Changed
- API key no longer passed in code (security improvement)
- Client reads from environment variable by default
- Explicit key still supported: `new ApiClient({ apiKey: process.env.MY_KEY })`
```

### 6.5.2 Step-by-Step Instructions

Break migration into numbered steps that can be followed exactly.

**Template**:
```markdown
## Migration Steps

### Prerequisites
- [ ] [Requirement 1]
- [ ] [Requirement 2]

### Step 1: [Action]
[Detailed instructions]

```[language]
[Code example]
```

**Verify**: [How to confirm this step worked]

### Step 2: [Action]
...

### Step 3: [Action]
...

### Final Verification
[How to confirm complete migration]
```

**Example**:
```markdown
## Migration Steps

### Prerequisites
- [ ] Running version 2.3 or higher
- [ ] Node.js 18+
- [ ] API key available as environment variable

### Step 1: Update the SDK

```bash
npm install @example/sdk@2.4.0
```

**Verify**: Run `npm list @example/sdk` - should show `2.4.0`

### Step 2: Update Initialization Code

Find all places where you create the client:

```bash
grep -r "new ApiClient" src/
```

Update each instance:

```javascript
// Before
const client = new ApiClient({ apiKey: 'sk_live_xxxxx' });

// After
const client = new ApiClient();
```

**Verify**: Run your tests - should still pass

### Step 3: Set Environment Variable

Add to your environment:

```bash
export EXAMPLE_API_KEY=sk_live_xxxxx
```

For production, add to your deployment configuration.

**Verify**: `echo $EXAMPLE_API_KEY` should show your key

### Final Verification

Run the SDK verification script:

```bash
npx @example/sdk verify
```

Expected output:
```
✓ SDK version: 2.4.0
✓ API key: configured via environment
✓ Connection: successful
Migration complete!
```
```

### 6.5.3 Common Issues and Solutions

Anticipate problems and provide solutions.

**Template**:
```markdown
## Troubleshooting

### Issue: [Problem description]

**Symptoms**:
- [What the user sees]

**Cause**:
[Why this happens]

**Solution**:
[How to fix it]

```[language]
[Code if applicable]
```
```

**Example**:
```markdown
## Troubleshooting

### Issue: "API key not found" error after migration

**Symptoms**:
- Error message: `Error: EXAMPLE_API_KEY environment variable not set`
- Happens on client initialization

**Cause**:
The new SDK version reads the API key from environment variables by default. If you haven't set the variable, you'll get this error.

**Solution**:

Option 1: Set the environment variable
```bash
export EXAMPLE_API_KEY=your_key_here
```

Option 2: Pass key explicitly (not recommended for production)
```javascript
const client = new ApiClient({
  apiKey: process.env.MY_CUSTOM_KEY_VAR
});
```

---

### Issue: Tests fail after migration

**Symptoms**:
- Tests that worked before now fail with authentication errors
- Works in production, fails in test environment

**Cause**:
Test environment doesn't have the API key environment variable set.

**Solution**:

Add to your test setup:
```javascript
// test/setup.js
process.env.EXAMPLE_API_KEY = 'sk_test_xxxxx';
```

Or use a `.env.test` file with your test framework.

---

### Issue: Rate limits hit more frequently

**Symptoms**:
- 429 errors that didn't happen in v1
- Happens with same request volume

**Cause**:
v2 includes automatic retries, which can multiply your request count.

**Solution**:

Configure retry behavior:
```javascript
const client = new ApiClient({
  maxRetries: 2,  // Default is 5
  retryDelay: 1000
});
```
```

---

## Complete PR Template

Copy this template into your project's `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Summary

[What does this PR do and why?]

Closes #[issue]

## Changes

-
-
-

## Testing

### Automated
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests pass

### Manual
- [ ] [Test scenario 1]
- [ ] [Test scenario 2]

## Screenshots (if UI change)

### Before
[screenshot]

### After
[screenshot]

## Checklist

- [ ] Code follows project style guidelines
- [ ] Documentation updated (if needed)
- [ ] No breaking changes (or documented below)
- [ ] Reviewed my own code

## Breaking Changes

[Describe any breaking changes and migration path, or "None"]

## Notes for Reviewers

[Anything reviewers should pay special attention to?]
```

---

**Previous**: See [templates-for-humans-part4-breaking-changes.md](templates-for-humans-part4-breaking-changes.md) for breaking change communication.

**Back to Index**: See [templates-for-humans.md](templates-for-humans.md) for the full overview.
