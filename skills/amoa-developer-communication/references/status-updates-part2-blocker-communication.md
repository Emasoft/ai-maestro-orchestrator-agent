# Status Updates - Part 2: Blocker Communication

## Contents
- 5.2 Blocker communication
  - 5.2.1 Describing the blocker clearly
  - 5.2.2 What you've tried
  - 5.2.3 What you need to unblock

---

## 5.2 Blocker Communication

When you hit a blocker, communicate it proactively. Don't wait for someone to ask why you're stuck.

### 5.2.1 Describing the Blocker Clearly

State the problem in terms that let someone help you.

**Template**:
```
**What I'm trying to do**: [Goal]
**What's happening instead**: [Actual behavior]
**Error message/evidence**: [Specific error or symptom]
**Environment**: [Relevant context]
```

**Example**:
```
**What I'm trying to do**: Deploy the auth service to staging
**What's happening instead**: Deployment fails with access denied error
**Error message**:
```
ERROR: AccessDenied: User is not authorized to perform
sts:AssumeRole on resource arn:aws:iam::123456:role/staging-deploy
```
**Environment**: CI/CD pipeline, GitHub Actions runner
```

### 5.2.2 What You've Tried

Show that you've made an effort before asking for help.

**Template**:
```
**What I've tried**:
1. [Attempt 1] - Result: [outcome]
2. [Attempt 2] - Result: [outcome]
3. [Attempt 3] - Result: [outcome]

**What I haven't tried** (and why):
- [Option]: [Reason for not trying, e.g., "don't have access"]
```

**Example**:
```
**What I've tried**:
1. Verified AWS credentials are set in GitHub secrets - they are
2. Compared IAM policy with production (which works) - identical
3. Tried running deployment from local machine - same error

**What I haven't tried**:
- Checking CloudTrail logs - don't have access to AWS console
- Creating new IAM role - need admin permissions
```

### 5.2.3 What You Need to Unblock

Be specific about the help you need.

**Template**:
```
**To unblock, I need one of these**:
- Option A: [Specific action] from [Person/Team]
- Option B: [Alternative approach] requiring [resources]

**My preference**: [Which option and why]
**Urgency**: [When this becomes critical, e.g., "blocks release 2.1"]
```

**Example**:
```
**To unblock, I need one of these**:
- Option A: @devops to update IAM role with sts:AssumeRole permission
- Option B: Someone to run the deployment manually using admin credentials
- Option C: Workaround using different deployment method (if it exists)

**My preference**: Option A - permanent fix
**Urgency**: Blocks today's staging deployment; release is Friday
```

---

**Previous**: [Part 1: Progress Reports](status-updates-part1-progress-reports.md)
**Next**: [Part 3: ETA Management](status-updates-part3-eta-management.md)
