## Table of Contents

- [PR Comment Writing](#pr-comment-writing)
- [Issue Communication](#issue-communication)
- [Technical Explanation](#technical-explanation)
- [Conflict Resolution](#conflict-resolution)
- [Status Updates](#status-updates)
- [Templates for Humans](#templates-for-humans)

---

# Reference Document Catalog

### PR Comment Writing
**File**: [pr-comment-writing.md](pr-comment-writing.md)

**Use when**: Writing code review comments on Pull Requests

**Contents**:
- 1.1 Writing constructive code review comments
  - 1.1.1 The praise-suggestion-question framework
  - 1.1.2 Balancing thoroughness with developer time
- 1.2 Tone guidelines for professional reviews
  - 1.2.1 Avoiding pedantic or condescending language
  - 1.2.2 Using "we" instead of "you"
- 1.3 When to request changes versus suggest
  - 1.3.1 Blocking issues that require changes
  - 1.3.2 Non-blocking suggestions and nits
  - 1.3.3 Praise-only approvals
- 1.4 Acknowledging good code patterns
- 1.5 Avoiding accusatory language
  - 1.5.1 Why "you" statements feel like attacks
  - 1.5.2 Reframing with "this" and "we"
- 1.6 Examples of good versus bad comments

---

### Issue Communication
**File**: [issue-communication.md](issue-communication.md)

**Use when**: Responding to bug reports, feature requests, or questions in issue trackers

**Contents**:
- 2.1 Bug report response workflow
  - 2.1.1 Acknowledgment template
  - 2.1.2 Reproduction confirmation
  - 2.1.3 Investigation updates
  - 2.1.4 Resolution communication
- 2.2 Feature request acknowledgment
  - 2.2.1 Thanking and validating the idea
  - 2.2.2 Setting scope expectations
  - 2.2.3 Linking to roadmap or discussions
- 2.3 Asking clarifying questions
  - 2.3.1 One question at a time rule
  - 2.3.2 Providing response options
  - 2.3.3 Explaining why you need the information
- 2.4 Setting expectations on timeline
  - 2.4.1 Never promise specific dates
  - 2.4.2 Using priority and milestone indicators
  - 2.4.3 Managing stale issues
- 2.5 Closing issues gracefully
  - 2.5.1 Duplicate handling
  - 2.5.2 Won't-fix explanations
  - 2.5.3 Inviting future feedback

---

### Technical Explanation
**File**: [technical-explanation.md](technical-explanation.md)

**Use when**: Explaining architecture, design decisions, or non-obvious code to humans

**Contents**:
- 3.1 Explaining technical decisions
  - 3.1.1 The context-decision-consequences format
  - 3.1.2 Acknowledging tradeoffs honestly
  - 3.1.3 Referencing alternatives considered
- 3.2 Justifying architectural choices
  - 3.2.1 Connecting to requirements
  - 3.2.2 Explaining scalability and maintainability
  - 3.2.3 Addressing security implications
- 3.3 Providing context for non-obvious code
  - 3.3.1 When comments are necessary
  - 3.3.2 Linking to issues or ADRs
  - 3.3.3 Explaining workarounds and technical debt
- 3.4 Linking to relevant documentation
  - 3.4.1 Internal wiki and ADRs
  - 3.4.2 External specifications
  - 3.4.3 Code examples in the codebase
- 3.5 Using code examples effectively
  - 3.5.1 Before/after comparisons
  - 3.5.2 Minimal reproducible examples
  - 3.5.3 Annotated code blocks

---

### Conflict Resolution
**File**: [conflict-resolution.md](conflict-resolution.md)

**Use when**: Disagreeing with another developer's approach or resolving technical disputes

**Contents**:
- 4.1 Disagreeing professionally
  - 4.1.1 Separating the idea from the person
  - 4.1.2 Starting with understanding
  - 4.1.3 Using "I think" not "You're wrong"
- 4.2 Offering alternatives
  - 4.2.1 The "Yes, and" technique
  - 4.2.2 Presenting options without attachment
  - 4.2.3 Showing concrete examples
- 4.3 Finding compromise
  - 4.3.1 Identifying shared goals
  - 4.3.2 Proposing incremental solutions
  - 4.3.3 Time-boxing experiments
- 4.4 Escalation paths
  - 4.4.1 When to bring in a third party
  - 4.4.2 Technical leads and architects
  - 4.4.3 Documenting the disagreement
- 4.5 When to involve maintainers
  - 4.5.1 Stalled discussions
  - 4.5.2 Blocking PRs
  - 4.5.3 Community conduct issues

---

### Status Updates
**File**: [status-updates.md](status-updates.md)

**Use when**: Reporting progress, communicating blockers, or providing completion updates

**Contents**:
- 5.1 Progress report format
  - 5.1.1 What was done (concrete deliverables)
  - 5.1.2 What's next (clear next steps)
  - 5.1.3 Blockers (actionable items)
- 5.2 Blocker communication
  - 5.2.1 Describing the blocker clearly
  - 5.2.2 What you've tried
  - 5.2.3 What you need to unblock
- 5.3 ETA setting and adjustment
  - 5.3.1 Ranges not points
  - 5.3.2 Early communication of delays
  - 5.3.3 Explaining scope changes
- 5.4 Completion notification
  - 5.4.1 Summary of changes
  - 5.4.2 Testing performed
  - 5.4.3 What reviewers should focus on
- 5.5 Post-mortem communication
  - 5.5.1 Blameless retrospective format
  - 5.5.2 What we learned
  - 5.5.3 Action items and owners

---

### Templates for Humans
**File**: [templates-for-humans.md](templates-for-humans.md)

**Use when**: Writing PRs, commits, release notes, or migration guides for human readers

**Contents**:
- 6.1 Pull Request description template
  - 6.1.1 Summary section
  - 6.1.2 Changes section with bullets
  - 6.1.3 Testing section
  - 6.1.4 Screenshots for UI changes
- 6.2 Commit message guidelines
  - 6.2.1 Conventional commits format
  - 6.2.2 Subject line rules
  - 6.2.3 Body content guidelines
- 6.3 Release notes format
  - 6.3.1 User-facing language
  - 6.3.2 Grouping by type
  - 6.3.3 Linking to issues and PRs
- 6.4 Breaking change communication
  - 6.4.1 Warning users in advance
  - 6.4.2 Deprecation notices
  - 6.4.3 Migration timeline
- 6.5 Migration guide structure
  - 6.5.1 Before/after examples
  - 6.5.2 Step-by-step instructions
  - 6.5.3 Common issues and solutions
