# Status Updates - Part 1: Progress Report Format

## Contents
- 5.1 Progress report format
  - 5.1.1 What was done (concrete deliverables)
  - 5.1.2 What's next (clear next steps)
  - 5.1.3 Blockers (actionable items)

---

## 5.1 Progress Report Format

Good status updates answer three questions: What did you do? What's next? What's blocking you?

### 5.1.1 What Was Done (Concrete Deliverables)

List specific, verifiable accomplishments. Not activities, but outcomes.

**Bad** (activities):
```
- Worked on the authentication feature
- Had meetings about the API design
- Reviewed some PRs
```

**Good** (deliverables):
```
- Completed: JWT token generation and validation (#123)
- Merged: User authentication middleware (PR #456)
- Drafted: API specification for password reset flow (shared in Notion)
```

**Format guidelines**:
- Use past tense for completed items
- Include PR/issue numbers for traceability
- Link to artifacts (docs, designs, repos)

### 5.1.2 What's Next (Clear Next Steps)

Describe upcoming work with enough detail that someone could verify completion.

**Bad** (vague):
```
- Continue working on authentication
- More testing
- Documentation
```

**Good** (specific):
```
- Implement password reset endpoint (target: Tuesday)
- Add integration tests for full auth flow (target: Wednesday)
- Document auth API in OpenAPI spec (target: Thursday)
```

**Format guidelines**:
- Use future tense
- Include target completion (day, not time)
- Break large tasks into verifiable chunks

### 5.1.3 Blockers (Actionable Items)

Blockers should include who can resolve them and what resolution looks like.

**Bad** (unclear):
```
- Blocked on environment issues
- Waiting for feedback
```

**Good** (actionable):
```
- Blocked: Need AWS credentials for staging environment
  - Who: @devops-team
  - Needed: IAM role with S3 read access
  - Impact: Cannot test file upload feature

- Blocked: Waiting for API contract review
  - Who: @backend-lead
  - Needed: Approval of authentication flow design doc
  - Impact: Cannot finalize implementation details
```

---

**Next**: [Part 2: Blocker Communication](status-updates-part2-blocker-communication.md)
