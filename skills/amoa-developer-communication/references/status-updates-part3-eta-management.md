# Status Updates - Part 3: ETA Setting and Adjustment

## Contents
- 5.3 ETA setting and adjustment
  - 5.3.1 Ranges not points
  - 5.3.2 Early communication of delays
  - 5.3.3 Explaining scope changes

---

## 5.3 ETA Setting and Adjustment

Estimates are uncertain. Communicate them in ways that set realistic expectations.

### 5.3.1 Ranges Not Points

Point estimates are almost always wrong. Ranges communicate uncertainty honestly.

**Bad** (false precision):
```
This will be done by Thursday at 2pm.
```

**Good** (honest ranges):
```
Optimistic: Wednesday (if no surprises)
Realistic: Thursday-Friday
Pessimistic: Next Monday (if we hit the edge cases I'm worried about)

I'll update if I move between these estimates.
```

**How to determine ranges**:
- **Optimistic**: Everything goes perfectly, no blockers, no scope creep
- **Realistic**: Normal amount of issues, some testing iteration
- **Pessimistic**: Hit major blockers, discover hidden complexity

### 5.3.2 Early Communication of Delays

Report delays as soon as you know, not when the deadline passes.

**Bad** (after the fact):
```
[Friday 5pm] Sorry, the feature isn't ready. Ran into issues.
```

**Good** (proactive):
```
[Wednesday, when you realize]

Heads up: The auth feature is taking longer than expected.

**Original estimate**: Thursday
**New estimate**: Friday-Monday

**What happened**: The OAuth library doesn't support our use case. I need to either:
1. Implement custom token refresh logic (~1 day)
2. Switch libraries (~2 days to evaluate and migrate)

I'm going with option 1. Will update tomorrow on progress.
```

### 5.3.3 Explaining Scope Changes

When scope changes affect timeline, explain the tradeoff clearly.

**Template**:
```
**Scope change request**: [New requirement]
**Impact on timeline**: [Delay amount]
**Options**:
1. Accept delay: [New timeline]
2. Cut scope: Remove [feature] to keep original timeline
3. Add resources: [What/who would help]

**My recommendation**: [Option] because [reasoning]
**Need decision by**: [Date]
```

**Example**:
```
**Scope change request**: Add multi-factor authentication to the auth feature
**Impact on timeline**: +3-5 days

**Options**:
1. Accept delay: Deliver full feature by next Wednesday instead of Friday
2. Cut scope: Ship basic auth Friday, add MFA in v1.1 (next sprint)
3. Add resources: If @backend-dev can help with MFA, might make original timeline

**My recommendation**: Option 2 - ship basic auth, add MFA next sprint
- MFA is valuable but not blocking launch
- Allows us to get user feedback on core flow first
- Lower risk than rushing MFA implementation

**Need decision by**: Tomorrow morning to adjust sprint planning
```

---

**Previous**: [Part 2: Blocker Communication](status-updates-part2-blocker-communication.md)
**Next**: [Part 4: Completion Notification](status-updates-part4-completion-notification.md)
