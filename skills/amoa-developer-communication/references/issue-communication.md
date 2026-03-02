# Issue Communication Guide

## Contents

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

## 2.1 Bug Report Response Workflow

Every bug report deserves a response, even if you can't fix it immediately. Silence frustrates reporters and damages trust.

### 2.1.1 Acknowledgment Template

**Respond within 24-48 hours** with acknowledgment, even if you can't investigate yet.

**Template**:
```markdown
Thanks for reporting this, @username!

I can see this is affecting your workflow. Let me look into it.

A few quick questions to help me reproduce:
- What version are you running? (`app --version`)
- What operating system?
- Did this start recently or has it always behaved this way?

I'll update this issue once I can reproduce the behavior.
```

**Key elements**:
1. Thank the reporter (they took time to help improve the project)
2. Acknowledge the impact
3. Commit to action
4. Ask focused questions if needed

### 2.1.2 Reproduction Confirmation

Once you can reproduce the bug, confirm it publicly. This validates the reporter and sets expectations.

**Template - Can Reproduce**:
```markdown
I was able to reproduce this on:
- OS: macOS 14.2
- Version: 2.3.1
- Steps: Exactly as described

The issue is in the date parsing logic - it doesn't handle timezone offsets correctly.

Adding to the 2.4.0 milestone. I'll post updates here as I work on a fix.
```

**Template - Cannot Reproduce**:
```markdown
I've tried to reproduce this but haven't been successful yet. Here's what I tested:

- OS: macOS 14.2, Ubuntu 22.04
- Version: 2.3.1
- Steps: [exact steps tried]

Could you share:
1. The exact input file that triggers this (redacting any sensitive data)
2. Your config file (found at `~/.config/app/settings.json`)

A screen recording would also help if you have time - the behavior might be timing-related.
```

### 2.1.3 Investigation Updates

**Update every 3-5 days** during active investigation, even if just to say "still looking."

**Template - Progress**:
```markdown
Quick update: I've narrowed this down to the caching layer. The issue occurs when:
1. A request times out
2. The partial response gets cached
3. Subsequent requests return the corrupted cached data

Working on a fix that invalidates cache on timeout. Should have a PR up by end of week.
```

**Template - Blocked**:
```markdown
Update: I've confirmed this is related to a bug in our upstream dependency (example-lib). I've opened an issue there: example-lib/example-lib#123

Options:
1. Wait for upstream fix (unknown timeline)
2. Implement a workaround (adds complexity but unblocks us)
3. Pin to older version (loses security fixes)

@username - which would work best for your use case?
```

### 2.1.4 Resolution Communication

When fixed, be specific about what was fixed and when users can expect the fix.

**Template - Fix Merged**:
```markdown
Fixed in #456!

The issue was caused by timezone handling in the date parser. The fix:
- Normalizes all timestamps to UTC before comparison
- Adds validation for malformed timezone strings
- Includes regression tests

The fix will be in version 2.4.0. If you need it sooner, you can:
- Build from main branch
- Use the nightly release: `npm install app@nightly`

Thanks for reporting this - it was affecting more users than we realized!
```

**Template - Won't Fix in This Version**:
```markdown
After investigation, this is a deeper architectural issue than expected. Fixing it properly requires changes to the core data model.

This is now tracked in our 3.0 milestone (#789) which includes the necessary refactoring.

**Workaround for now**: You can avoid this by setting `legacyMode: true` in your config. This uses the old code path which doesn't have this issue.

I know this isn't the immediate fix you were hoping for. Let me know if the workaround helps.
```

---

## 2.2 Feature Request Acknowledgment

Feature requests are gifts - someone cared enough to suggest an improvement. Treat them with respect even when declining.

### 2.2.1 Thanking and Validating the Idea

**Always start with genuine appreciation**:

**Good**:
```markdown
Thanks for the suggestion, @username! I can see how this would streamline your workflow.

The use case makes sense - currently you have to export, transform, and reimport, when a direct transformation would save several steps.
```

**Not great**:
```markdown
We've heard this request before.
```

### 2.2.2 Setting Scope Expectations

Be honest about whether the feature fits the project direction.

**Template - Fits Well**:
```markdown
This aligns well with our goals for the plugin system. Adding to the backlog!

A few considerations:
- We'd want to support both sync and async transformations
- This would need to work with the existing hook system
- Performance impact on large files needs testing

No timeline yet, but this is something we want to do. Would you be interested in collaborating on the design?
```

**Template - Uncertain Fit**:
```markdown
Interesting idea! I want to think about this more before committing.

My initial thoughts:
- This would work for your use case
- But it might conflict with feature X that's in progress
- There could also be performance implications

Let me discuss with the team and get back to you. In the meantime, is there a workaround that's helping you today?
```

**Template - Does Not Fit**:
```markdown
Thanks for the detailed suggestion! I appreciate the thought you put into this.

After consideration, this doesn't fit our current direction because:
- It would add significant complexity to the core API
- The use case is specialized (only helps users doing X)
- It conflicts with our goal of keeping the tool simple

**Alternatives**:
- The plugin system lets you build this as an extension
- Tool Y is designed specifically for this workflow

I'm closing this for now, but feel free to reopen if you have additional context that might change our thinking.
```

### 2.2.3 Linking to Roadmap or Discussions

Connect feature requests to the bigger picture:

```markdown
This is related to our Q3 goal of improving export functionality. See our roadmap: [link]

I've added this to the discussion thread for export improvements: #123

The team reviews these discussions monthly. Upvotes and additional use cases help us prioritize!
```

---

## 2.3 Asking Clarifying Questions

Good questions get good answers. Bad questions waste everyone's time.

### 2.3.1 One Question at a Time Rule

**Problem**: Multiple questions confuse respondents. They answer one, forget others, or feel overwhelmed.

**Bad**:
```markdown
What version are you using? What OS? Can you share the error log? Did this work before? What changed? Can you try clearing the cache?
```

**Good**:
```markdown
To help debug this, what version of the app are you running?

You can find this with `app --version`.
```

Then follow up based on their answer.

### 2.3.2 Providing Response Options

Help respondents by offering choices rather than open-ended questions.

**Bad**:
```markdown
What kind of input causes this?
```

**Good**:
```markdown
Which of these causes the issue?
- [ ] All inputs
- [ ] Only large files (>10MB)
- [ ] Only files with special characters in the name
- [ ] Only files from a specific source

Check all that apply!
```

### 2.3.3 Explaining Why You Need the Information

People respond better when they understand the purpose.

**Bad**:
```markdown
Can you share your config file?
```

**Good**:
```markdown
Could you share your config file (`~/.app/config.json`)?

I'm specifically looking at the `timeout` and `retryCount` settings - the error you're seeing sometimes happens when these are misconfigured.

Feel free to redact any sensitive values!
```

---

## 2.4 Setting Expectations on Timeline

### 2.4.1 Never Promise Specific Dates

Dates are almost always wrong. They create disappointment and erode trust.

**Bad**:
```markdown
This will be fixed by Friday.
```

**Good**:
```markdown
This is prioritized for the next release. We typically release every 2-3 weeks, but no specific date yet.

I'll update this issue when we have a clearer timeline.
```

### 2.4.2 Using Priority and Milestone Indicators

Use labels and milestones to communicate priority without dates:

```markdown
I've added this to:
- **Priority**: High (affects core functionality)
- **Milestone**: v2.4 (next planned release)
- **Type**: Bug

This means it's in the queue ahead of lower-priority items, but behind any critical/security issues that might come up.
```

### 2.4.3 Managing Stale Issues

Issues go stale. Handle them proactively:

**Check-in Template (60 days)**:
```markdown
Hi @username - checking in on this issue.

Is this still affecting you? We've made several changes since this was reported that might have addressed it.

If you're still seeing the issue, any additional context would help us prioritize. If not, I'll close this in a week.
```

**Closing Stale Template (90 days)**:
```markdown
Closing due to inactivity. This doesn't mean the issue isn't real - just that we don't have enough information to act on it.

If you're still experiencing this, please:
1. Open a new issue
2. Include steps to reproduce with current version
3. Reference this issue for context

Thanks for understanding!
```

---

## 2.5 Closing Issues Gracefully

How you close issues matters as much as how you open them.

### 2.5.1 Duplicate Handling

**Bad**:
```markdown
Duplicate of #123
[closes issue]
```

**Good**:
```markdown
Thanks for reporting! This is tracking the same problem as #123, so I'm closing this as a duplicate.

I've added your reproduction details to that issue - they'll help with the fix. Please follow #123 for updates!
```

### 2.5.2 Won't-Fix Explanations

Declining requests requires extra care. The reporter invested time.

**Template**:
```markdown
After discussion with the team, we've decided not to implement this. Here's our thinking:

**Why not**:
- This would add complexity to the core API
- The use case is quite specialized
- It conflicts with our design principle of keeping things simple

**Alternatives**:
- The plugin system can achieve this: [link to docs]
- Tool X is specifically designed for this workflow
- We're open to a community-maintained fork that adds this

I know this isn't the answer you were hoping for. Thank you for taking the time to suggest it - it sparked a good discussion about our project direction.

If our direction changes or you have new arguments, feel free to reopen.
```

### 2.5.3 Inviting Future Feedback

End on a positive note:

```markdown
Closing this as resolved. Thanks again for reporting - this fix helps everyone using the date parsing feature!

If you hit any other issues, please open a new issue. Your reports make the project better.
```

---

## Templates Quick Reference

### Bug Acknowledgment
```markdown
Thanks for reporting this, @username! Let me look into it.

Quick questions to help me reproduce:
- Version: (`app --version`)
- OS:
- Steps to reproduce:

I'll update once I can reproduce the behavior.
```

### Feature Acknowledgment
```markdown
Thanks for the suggestion! I can see how this would help with [their use case].

Let me think about this and discuss with the team. I'll update the issue with our thoughts.
```

### Reproduction Confirmed
```markdown
Reproduced on [OS/version].

Root cause: [brief explanation]

Adding to milestone [X]. Updates to follow.
```

### Cannot Reproduce
```markdown
I've tried to reproduce but haven't succeeded yet.

Tested: [environment/steps]

Could you share [specific needed info]?
```

### Closing as Won't Fix
```markdown
After consideration, this doesn't fit our current direction because [honest reason].

Alternatives: [options]

Thanks for the suggestion. Feel free to reopen with new context.
```

### Closing as Fixed
```markdown
Fixed in #PR!

Available in version X or nightly builds. Let me know if you hit any issues.

Thanks for reporting!
```
