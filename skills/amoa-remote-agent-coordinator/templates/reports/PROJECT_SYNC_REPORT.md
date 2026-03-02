# Project Synchronization Report

## Date: {{TIMESTAMP}}
## Project: {{PROJECT_NAME}}
## Repository: {{REPO_OWNER}}/{{REPO_NAME}}
## Orchestrator: {{ORCHESTRATOR_AGENT}}

---

## Synchronization Overview

**Sync Status**: {{SYNC_STATUS}}
**Last Sync**: {{LAST_SYNC_TIME}}
**Sync Duration**: {{SYNC_DURATION}}
**Issues Synced**: {{ISSUES_SYNCED}}
**Agents Coordinated**: {{AGENTS_COUNT}}
**Conflicts Detected**: {{CONFLICTS_COUNT}}

---

## GitHub Issue Status

### Open Issues

**Total Open**: {{OPEN_ISSUES_TOTAL}}
**In Progress**: {{ISSUES_IN_PROGRESS}}
**Blocked**: {{ISSUES_BLOCKED}}
**Ready for Review**: {{ISSUES_READY_REVIEW}}

| Issue # | Title | Status | Agent | Priority | Updated |
|---------|-------|--------|-------|----------|---------|
| {{ISSUE_1_NUM}} | {{ISSUE_1_TITLE}} | {{ISSUE_1_STATUS}} | {{ISSUE_1_AGENT}} | {{ISSUE_1_PRIORITY}} | {{ISSUE_1_UPDATED}} |
| {{ISSUE_2_NUM}} | {{ISSUE_2_TITLE}} | {{ISSUE_2_STATUS}} | {{ISSUE_2_AGENT}} | {{ISSUE_2_PRIORITY}} | {{ISSUE_2_UPDATED}} |
| {{ISSUE_3_NUM}} | {{ISSUE_3_TITLE}} | {{ISSUE_3_STATUS}} | {{ISSUE_3_AGENT}} | {{ISSUE_3_PRIORITY}} | {{ISSUE_3_UPDATED}} |

### Recently Closed Issues

| Issue # | Title | Closed By | Closed At | Resolution |
|---------|-------|-----------|-----------|------------|
| {{CLOSED_1_NUM}} | {{CLOSED_1_TITLE}} | {{CLOSED_1_AGENT}} | {{CLOSED_1_TIME}} | {{CLOSED_1_RESOLUTION}} |
| {{CLOSED_2_NUM}} | {{CLOSED_2_TITLE}} | {{CLOSED_2_AGENT}} | {{CLOSED_2_TIME}} | {{CLOSED_2_RESOLUTION}} |
| {{CLOSED_3_NUM}} | {{CLOSED_3_TITLE}} | {{CLOSED_3_AGENT}} | {{CLOSED_3_TIME}} | {{CLOSED_3_RESOLUTION}} |

### Blocked Issues

{{BLOCKED_ISSUES_DETAILS}}

---

## Kanban Board Position

**Board**: {{BOARD_NAME}}
**Board URL**: {{BOARD_URL}}

### Column Status

| Column | Issues | Agents Active | Last Updated |
|--------|--------|---------------|--------------|
| {{COLUMN_1}} | {{COLUMN_1_COUNT}} | {{COLUMN_1_AGENTS}} | {{COLUMN_1_UPDATED}} |
| {{COLUMN_2}} | {{COLUMN_2_COUNT}} | {{COLUMN_2_AGENTS}} | {{COLUMN_2_UPDATED}} |
| {{COLUMN_3}} | {{COLUMN_3_COUNT}} | {{COLUMN_3_AGENTS}} | {{COLUMN_3_UPDATED}} |
| {{COLUMN_4}} | {{COLUMN_4_COUNT}} | {{COLUMN_4_AGENTS}} | {{COLUMN_4_UPDATED}} |

### Recent Board Movements

| Issue | From | To | Moved By | When |
|-------|------|-----|----------|------|
| {{MOVE_1_ISSUE}} | {{MOVE_1_FROM}} | {{MOVE_1_TO}} | {{MOVE_1_AGENT}} | {{MOVE_1_WHEN}} |
| {{MOVE_2_ISSUE}} | {{MOVE_2_FROM}} | {{MOVE_2_TO}} | {{MOVE_2_AGENT}} | {{MOVE_2_WHEN}} |
| {{MOVE_3_ISSUE}} | {{MOVE_3_FROM}} | {{MOVE_3_TO}} | {{MOVE_3_AGENT}} | {{MOVE_3_WHEN}} |

---

## Branch Status

### Active Branches

| Branch | Issue | Agent | Status | Last Commit | Behind Main |
|--------|-------|-------|--------|-------------|-------------|
| {{BRANCH_1}} | {{BRANCH_1_ISSUE}} | {{BRANCH_1_AGENT}} | {{BRANCH_1_STATUS}} | {{BRANCH_1_COMMIT}} | {{BRANCH_1_BEHIND}} |
| {{BRANCH_2}} | {{BRANCH_2_ISSUE}} | {{BRANCH_2_AGENT}} | {{BRANCH_2_STATUS}} | {{BRANCH_2_COMMIT}} | {{BRANCH_2_BEHIND}} |
| {{BRANCH_3}} | {{BRANCH_3_ISSUE}} | {{BRANCH_3_AGENT}} | {{BRANCH_3_STATUS}} | {{BRANCH_3_COMMIT}} | {{BRANCH_3_BEHIND}} |

### Stale Branches

**Branches inactive > {{STALE_DAYS}} days**: {{STALE_BRANCHES_COUNT}}

{{STALE_BRANCHES_LIST}}

### Branch Conflicts

**Branches with merge conflicts**: {{CONFLICT_BRANCHES_COUNT}}

{{CONFLICT_BRANCHES_LIST}}

---

## Toolchain Consistency Check

**Consistency Status**: {{TOOLCHAIN_CONSISTENCY_STATUS}}

### Language/Runtime Versions

| Agent | Language | Version | Expected | Status |
|-------|----------|---------|----------|--------|
| {{AGENT_1}} | {{AGENT_1_LANG}} | {{AGENT_1_VERSION}} | {{EXPECTED_VERSION}} | {{AGENT_1_STATUS}} |
| {{AGENT_2}} | {{AGENT_2_LANG}} | {{AGENT_2_VERSION}} | {{EXPECTED_VERSION}} | {{AGENT_2_STATUS}} |
| {{AGENT_3}} | {{AGENT_3_LANG}} | {{AGENT_3_VERSION}} | {{EXPECTED_VERSION}} | {{AGENT_3_STATUS}} |

### Dependency Versions

| Dependency | Agent 1 | Agent 2 | Agent 3 | Expected | Status |
|------------|---------|---------|---------|----------|--------|
| {{DEP_1}} | {{A1_DEP_1}} | {{A2_DEP_1}} | {{A3_DEP_1}} | {{EXP_DEP_1}} | {{DEP_1_STATUS}} |
| {{DEP_2}} | {{A1_DEP_2}} | {{A2_DEP_2}} | {{A3_DEP_2}} | {{EXP_DEP_2}} | {{DEP_2_STATUS}} |
| {{DEP_3}} | {{A1_DEP_3}} | {{A2_DEP_3}} | {{A3_DEP_3}} | {{EXP_DEP_3}} | {{DEP_3_STATUS}} |

### Tool Versions

| Tool | Agent 1 | Agent 2 | Agent 3 | Expected | Status |
|------|---------|---------|---------|----------|--------|
| {{TOOL_1}} | {{A1_TOOL_1}} | {{A2_TOOL_1}} | {{A3_TOOL_1}} | {{EXP_TOOL_1}} | {{TOOL_1_STATUS}} |
| {{TOOL_2}} | {{A1_TOOL_2}} | {{A2_TOOL_2}} | {{A3_TOOL_2}} | {{EXP_TOOL_2}} | {{TOOL_2_STATUS}} |
| {{TOOL_3}} | {{A1_TOOL_3}} | {{A2_TOOL_3}} | {{A3_TOOL_3}} | {{EXP_TOOL_3}} | {{TOOL_3_STATUS}} |

### Consistency Issues

{{CONSISTENCY_ISSUES}}

---

## Agent Assignments

### Active Agents

| Agent | Issues | Branches | Status | Last Active | Workload |
|-------|--------|----------|--------|-------------|----------|
| {{AGENT_1_NAME}} | {{AGENT_1_ISSUES}} | {{AGENT_1_BRANCHES}} | {{AGENT_1_STATUS}} | {{AGENT_1_ACTIVE}} | {{AGENT_1_WORKLOAD}} |
| {{AGENT_2_NAME}} | {{AGENT_2_ISSUES}} | {{AGENT_2_BRANCHES}} | {{AGENT_2_STATUS}} | {{AGENT_2_ACTIVE}} | {{AGENT_2_WORKLOAD}} |
| {{AGENT_3_NAME}} | {{AGENT_3_ISSUES}} | {{AGENT_3_BRANCHES}} | {{AGENT_3_STATUS}} | {{AGENT_3_ACTIVE}} | {{AGENT_3_WORKLOAD}} |

### Agent Workload Distribution

| Workload Level | Agent Count | Issues |
|----------------|-------------|--------|
| Overloaded (>5) | {{OVERLOADED_COUNT}} | {{OVERLOADED_ISSUES}} |
| Busy (3-5) | {{BUSY_COUNT}} | {{BUSY_ISSUES}} |
| Normal (1-2) | {{NORMAL_COUNT}} | {{NORMAL_ISSUES}} |
| Idle (0) | {{IDLE_COUNT}} | 0 |

### Agent Conflicts

**Agents working on conflicting files**: {{AGENT_CONFLICTS_COUNT}}

{{AGENT_CONFLICTS_LIST}}

---

## Cross-Agent Dependencies

### Blocking Dependencies

| Blocked Issue | Blocked By | Agent Blocked | Agent Blocking | Status |
|---------------|------------|---------------|----------------|--------|
| {{BLOCK_1_ISSUE}} | {{BLOCK_1_BY}} | {{BLOCK_1_AGENT}} | {{BLOCK_1_BLOCKER}} | {{BLOCK_1_STATUS}} |
| {{BLOCK_2_ISSUE}} | {{BLOCK_2_BY}} | {{BLOCK_2_AGENT}} | {{BLOCK_2_BLOCKER}} | {{BLOCK_2_STATUS}} |
| {{BLOCK_3_ISSUE}} | {{BLOCK_3_BY}} | {{BLOCK_3_AGENT}} | {{BLOCK_3_BLOCKER}} | {{BLOCK_3_STATUS}} |

### Dependency Chain

{{DEPENDENCY_CHAIN}}

---

## Communication Log

### Recent Messages

| Time | From | To | Subject | Priority | Status |
|------|------|-----|---------|----------|--------|
| {{MSG_1_TIME}} | {{MSG_1_FROM}} | {{MSG_1_TO}} | {{MSG_1_SUBJECT}} | {{MSG_1_PRIORITY}} | {{MSG_1_STATUS}} |
| {{MSG_2_TIME}} | {{MSG_2_FROM}} | {{MSG_2_TO}} | {{MSG_2_SUBJECT}} | {{MSG_2_PRIORITY}} | {{MSG_2_STATUS}} |
| {{MSG_3_TIME}} | {{MSG_3_FROM}} | {{MSG_3_TO}} | {{MSG_3_SUBJECT}} | {{MSG_3_PRIORITY}} | {{MSG_3_STATUS}} |

### Unread Messages by Agent

| Agent | Unread Count | Oldest Unread | Priority High |
|-------|--------------|---------------|---------------|
| {{AGENT_1_NAME}} | {{AGENT_1_UNREAD}} | {{AGENT_1_OLDEST}} | {{AGENT_1_HIGH}} |
| {{AGENT_2_NAME}} | {{AGENT_2_UNREAD}} | {{AGENT_2_OLDEST}} | {{AGENT_2_HIGH}} |
| {{AGENT_3_NAME}} | {{AGENT_3_UNREAD}} | {{AGENT_3_OLDEST}} | {{AGENT_3_HIGH}} |

---

## Synchronization Issues

**Total Issues**: {{SYNC_ISSUES_COUNT}}

### Critical Issues

{{SYNC_CRITICAL_ISSUES}}

### Warnings

{{SYNC_WARNINGS}}

### Resolution Status

| Issue Type | Count | Resolved | Pending | Action Required |
|------------|-------|----------|---------|-----------------|
| {{ISSUE_TYPE_1}} | {{TYPE_1_COUNT}} | {{TYPE_1_RESOLVED}} | {{TYPE_1_PENDING}} | {{TYPE_1_ACTION}} |
| {{ISSUE_TYPE_2}} | {{TYPE_2_COUNT}} | {{TYPE_2_RESOLVED}} | {{TYPE_2_PENDING}} | {{TYPE_2_ACTION}} |
| {{ISSUE_TYPE_3}} | {{TYPE_3_COUNT}} | {{TYPE_3_RESOLVED}} | {{TYPE_3_PENDING}} | {{TYPE_3_ACTION}} |

---

## Project Metrics

### Velocity

**Issues Completed (7 days)**: {{ISSUES_COMPLETED_7D}}
**Issues Completed (30 days)**: {{ISSUES_COMPLETED_30D}}
**Average Issue Duration**: {{AVG_ISSUE_DURATION}}
**Average PR Merge Time**: {{AVG_PR_MERGE_TIME}}

### Quality Metrics

**Test Coverage**: {{TEST_COVERAGE}}%
**Build Success Rate**: {{BUILD_SUCCESS_RATE}}%
**Review Approval Rate**: {{REVIEW_APPROVAL_RATE}}%
**First-time CI Pass Rate**: {{CI_FIRST_PASS_RATE}}%

### Activity Metrics

**Commits (7 days)**: {{COMMITS_7D}}
**PRs Opened (7 days)**: {{PRS_OPENED_7D}}
**PRs Merged (7 days)**: {{PRS_MERGED_7D}}
**Active Contributors**: {{ACTIVE_CONTRIBUTORS}}

---

## Recommended Actions

### Immediate Actions Required

{{IMMEDIATE_ACTIONS}}

### Optimization Opportunities

{{OPTIMIZATION_OPPORTUNITIES}}

### Potential Risks

{{POTENTIAL_RISKS}}

---

## Next Sync

**Scheduled**: {{NEXT_SYNC_TIME}}
**Auto-sync Interval**: {{SYNC_INTERVAL}}
**Manual Sync Trigger**: `{{SYNC_COMMAND}}`

---

## Artifacts

**Full Sync Log**: {{SYNC_LOG_PATH}}
**Conflict Report**: {{CONFLICT_REPORT_PATH}}
**Agent Status Report**: {{AGENT_STATUS_PATH}}
**Metrics Dashboard**: {{METRICS_DASHBOARD_URL}}

---

*Report generated by {{GENERATOR}} on {{TIMESTAMP}}*
