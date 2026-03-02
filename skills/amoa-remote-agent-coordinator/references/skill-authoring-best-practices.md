# Skill Authoring Best Practices

Official Anthropic guidance for writing effective Claude Code Skills.

**Source**: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

## Contents

- [When you need to understand core principles](#core-principles)
- [When setting up skill structure and naming](#skill-structure)
- [When implementing progressive disclosure](#progressive-disclosure-patterns)
- [When creating workflows and feedback loops](#workflows-and-feedback-loops)
- [When writing skill content](#content-guidelines)
- [When using common patterns](#common-patterns)
- [When creating executable scripts](#executable-scripts)
- [When you need to avoid common mistakes](#anti-patterns-to-avoid)
- [When evaluating and iterating on skills](#evaluation-and-iteration)
- [When validating skill quality](#checklist-for-effective-skills)

## Core Principles

### 1. Concise is Key

Context window is shared with system prompt, conversation history, other Skills, and requests.

**Default assumption**: Claude is already very smart. Only add context Claude doesn't have.

Challenge each piece of information:
- "Does Claude really need this explanation?"
- "Can I assume Claude knows this?"
- "Does this paragraph justify its token cost?"

**Good** (~50 tokens):
```markdown
## Extract PDF text
Use pdfplumber for text extraction:
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
```

**Bad** (~150 tokens): Long explanations about what PDFs are.

### 2. Set Appropriate Degrees of Freedom

| Freedom Level | Use When | Example |
|--------------|----------|---------|
| **High** (text instructions) | Multiple approaches valid, decisions depend on context | Code review process |
| **Medium** (pseudocode/scripts with params) | Preferred pattern exists, some variation acceptable | Report generation template |
| **Low** (specific scripts, few params) | Operations fragile, consistency critical | Database migrations |

**Analogy**:
- **Narrow bridge with cliffs**: Only one safe way → specific guardrails (low freedom)
- **Open field with no hazards**: Many paths lead to success → general direction (high freedom)

### 3. Test with All Models

| Model | Consideration |
|-------|--------------|
| **Haiku** (fast, economical) | Does Skill provide enough guidance? |
| **Sonnet** (balanced) | Is Skill clear and efficient? |
| **Opus** (powerful reasoning) | Does Skill avoid over-explaining? |

## Skill Structure

### YAML Frontmatter Requirements

```yaml
---
name: my-skill-name       # Max 64 chars, lowercase, alphanumeric + hyphens
description: What it does and when to use it  # Max 1024 chars
---
```

**Name constraints**:
- Maximum 64 characters
- Lowercase letters, numbers, hyphens only
- No XML tags
- No reserved words: "anthropic", "claude"

### Naming Conventions

Use **gerund form** (verb + -ing):

**Good**:
- `processing-pdfs`
- `analyzing-spreadsheets`
- `managing-databases`
- `testing-code`

**Acceptable alternatives**:
- Noun phrases: `pdf-processing`
- Action-oriented: `process-pdfs`

**Avoid**:
- Vague: `helper`, `utils`, `tools`
- Generic: `documents`, `data`, `files`

### Writing Effective Descriptions

**ALWAYS write in third person**:
- **Good**: "Processes Excel files and generates reports"
- **Avoid**: "I can help you process Excel files"
- **Avoid**: "You can use this to process Excel files"

**Include both what and when**:
```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

## Progressive Disclosure Patterns

### Keep SKILL.md Under 500 Lines

Split content into separate files when approaching limit.

### Directory Structure

```
pdf/
├── SKILL.md              # Main instructions (loaded when triggered)
├── FORMS.md              # Form-filling guide (loaded as needed)
├── reference.md          # API reference (loaded as needed)
├── examples.md           # Usage examples (loaded as needed)
└── scripts/
    ├── analyze_form.py   # Utility script (executed, not loaded)
    ├── fill_form.py      # Form filling script
    └── validate.py       # Validation script
```

### Pattern 1: High-Level Guide with References

```markdown
# PDF Processing

## Quick start
[Basic example code]

## Advanced features
**Form filling**: See `[FORMS.md]\(FORMS.md\)` for complete guide
**API reference**: See `[REFERENCE.md]\(REFERENCE.md\)` for all methods
```

### Pattern 2: Domain-Specific Organization

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing)
    ├── sales.md (pipeline)
    ├── product.md (API usage)
    └── marketing.md (campaigns)
```

### Avoid Deeply Nested References

Keep references **one level deep** from SKILL.md.

**Bad**:
```
SKILL.md → advanced.md → details.md → actual_info.md
```

**Good**:
```
SKILL.md
  ├→ advanced.md
  ├→ reference.md
  └→ examples.md
```

### Table of Contents for Long Files

For files >100 lines, include TOC at top.

### TOC-Driven Progressive Disclosure (Critical Trick)

**The secret to efficient progressive disclosure**: Always embed the TOC of each referenced .md file directly in SKILL.md. This lets Claude immediately understand WHEN to read each reference file without opening it first.

**Requirements**:
1. ALL reference files MUST have a TOC at the top
2. TOC entries MUST describe USE CASES, not just subjects
3. SKILL.md MUST include the TOC when referencing a file

**Wrong** (subject-only headings):
```markdown
# Claude Tasks Reference

## Contents
- 1.7 Claude Tasks syntax
- 1.8 Claude Tasks commands
- 1.9 Claude Tasks configuration
```

**Correct** (use-case-oriented headings):
```markdown
# Claude Tasks Reference

## Contents
- 1.7 Updating a permanent task list using Claude Tasks
  - 1.7.1 Claude Tasks basic CLI syntax
  - 1.7.2 Claude Tasks batch operations syntax
- 1.8 Scheduling recurring tasks with Claude Tasks cron expressions
- 1.9 Configuring Claude Tasks for team-wide task sharing
```

**In SKILL.md, embed the TOC**:
```markdown
## Task Management

For Claude Code native Task list operations, see `[tasks-reference.md]\(references/tasks-reference.md\)`:
- 1.7 Updating a permanent task list using Claude Tasks
  - 1.7.1 Claude Tasks basic CLI syntax
  - 1.7.2 Claude Tasks batch operations syntax
- 1.8 Scheduling recurring tasks with Claude Tasks cron expressions
- 1.9 Configuring Claude Tasks for team-wide task sharing
```

This way, Claude sees the use cases immediately and knows exactly which section to read for the current task, without loading the entire reference file first.

## Workflows and Feedback Loops

### Use Checklists for Complex Tasks

```markdown
## PDF form filling workflow

Copy this checklist and check off items as you complete them:

```
Task Progress:
- [ ] Step 1: Analyze the form (run analyze_form.py)
- [ ] Step 2: Create field mapping (edit fields.json)
- [ ] Step 3: Validate mapping (run validate_fields.py)
- [ ] Step 4: Fill the form (run fill_form.py)
- [ ] Step 5: Verify output (run verify_output.py)
```
```

### Implement Feedback Loops

**Pattern**: Run validator → fix errors → repeat

```markdown
## Document editing process

1. Make your edits to `word/document.xml`
2. **Validate immediately**: `python scripts/validate.py unpacked_dir/`
3. If validation fails:
   - Review the error message carefully
   - Fix the issues in the XML
   - Run validation again
4. **Only proceed when validation passes**
5. Rebuild and test
```

## Content Guidelines

### Avoid Time-Sensitive Information

**Bad**:
```markdown
If you're doing this before August 2025, use the old API.
```

**Good**:
```markdown
## Current method
Use the v2 API endpoint.

## Old patterns
<details>
<summary>Legacy v1 API (deprecated 2025-08)</summary>
[Legacy info]
</details>
```

### Use Consistent Terminology

Choose one term and use it throughout:
- Always "API endpoint" (not "URL", "route", "path")
- Always "field" (not "box", "element", "control")
- Always "extract" (not "pull", "get", "retrieve")

## Common Patterns

### Template Pattern

**For strict requirements**:
```markdown
## Report structure
ALWAYS use this exact template structure:
[template]
```

**For flexible guidance**:
```markdown
## Report structure
Here is a sensible default format, but use your best judgment:
[template]
```

### Examples Pattern

Provide input/output pairs:

```markdown
## Commit message format

**Example 1:**
Input: Added user authentication with JWT tokens
Output:
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```
```

### Conditional Workflow Pattern

```markdown
## Document modification workflow

1. Determine the modification type:
   **Creating new content?** → Follow "Creation workflow"
   **Editing existing content?** → Follow "Editing workflow"
```

## Executable Scripts

### Solve, Don't Punt

Handle errors explicitly instead of failing:

**Good**:
```python
def process_file(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        print(f"File {path} not found, creating default")
        with open(path, 'w') as f:
            f.write('')
        return ''
```

### No Magic Numbers

**Good**:
```python
# HTTP requests typically complete within 30 seconds
REQUEST_TIMEOUT = 30

# Three retries balances reliability vs speed
MAX_RETRIES = 3
```

**Bad**:
```python
TIMEOUT = 47  # Why 47?
RETRIES = 5   # Why 5?
```

### Provide Utility Scripts

Benefits:
- More reliable than generated code
- Save tokens (no code in context)
- Save time (no generation)
- Ensure consistency

Make clear whether Claude should:
- **Execute**: "Run `analyze_form.py` to extract fields"
- **Read as reference**: "See `analyze_form.py` for the algorithm"

### Create Verifiable Intermediate Outputs

**Plan-validate-execute pattern**:
1. Analyze
2. Create plan file (e.g., `changes.json`)
3. Validate plan
4. Execute
5. Verify

Make validation scripts verbose with specific error messages.

## Anti-Patterns to Avoid

### Avoid Windows-Style Paths

- ✓ `scripts/helper.py`
- ✗ `scripts\helper.py`

### Avoid Too Many Options

**Bad**:
"You can use pypdf, or pdfplumber, or PyMuPDF, or..."

**Good**:
"Use pdfplumber for text extraction.
For scanned PDFs requiring OCR, use pdf2image with pytesseract instead."

### Don't Assume Tools Are Installed

**Bad**: "Use the pdf library to process the file."

**Good**:
```markdown
Install required package: `pip install pypdf`

Then use it:
```python
from pypdf import PdfReader
```
```

### MCP Tool References

Always use fully qualified names: `ServerName:tool_name`

```markdown
Use the BigQuery:bigquery_schema tool to retrieve table schemas.
```

## Evaluation and Iteration

### Build Evaluations First

1. Identify gaps (run Claude without Skill)
2. Create evaluations (3 scenarios minimum)
3. Establish baseline
4. Write minimal instructions
5. Iterate

### Develop Iteratively with Claude

- **Claude A**: Helps design/refine Skill
- **Claude B**: Tests Skill in real tasks
- Observe Claude B's behavior
- Bring insights back to Claude A
- Repeat

### Observe Navigation Patterns

Watch for:
- Unexpected exploration paths
- Missed connections to important files
- Overreliance on certain sections
- Ignored content

## Checklist for Effective Skills

### Core Quality
- [ ] Description is specific and includes key terms
- [ ] Description includes both what and when
- [ ] SKILL.md body under 500 lines
- [ ] Additional details in separate files
- [ ] No time-sensitive information
- [ ] Consistent terminology throughout
- [ ] Concrete examples
- [ ] File references one level deep
- [ ] Progressive disclosure used appropriately
- [ ] Workflows have clear steps

### Code and Scripts
- [ ] Scripts solve problems (don't punt to Claude)
- [ ] Error handling explicit and helpful
- [ ] No magic constants (all values justified)
- [ ] Required packages listed
- [ ] Scripts have clear documentation
- [ ] No Windows-style paths
- [ ] Validation steps for critical operations
- [ ] Feedback loops for quality-critical tasks

### Testing
- [ ] At least three evaluations created
- [ ] Tested with Haiku, Sonnet, and Opus
- [ ] Tested with real usage scenarios
- [ ] Team feedback incorporated
