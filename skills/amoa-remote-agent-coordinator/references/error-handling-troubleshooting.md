## Table of Contents
- [AI Maestro Messages Not Delivered](#issue-ai-maestro-messages-not-being-delivered)
- [Agent Doesn't Understand Instructions](#issue-agent-responds-but-doesnt-understand-instructions)
- [Agent Progress Stalls](#issue-agent-progress-stalls-without-reporting-blockers)
- [Module Assignment Conflicts](#issue-module-assignment-conflicts-between-agents)
- [PR Fails Verification](#issue-agent-completes-work-but-pr-fails-verification)

# Error Handling Troubleshooting

### Issue: AI Maestro messages not being delivered

**Cause**: API endpoint unreachable or agent identifier incorrect.

**Solution**:
1. Verify API health using the `agent-messaging` skill health check
2. Check agent ID format (use full session name, not alias)
3. Verify agent is registered in AI Maestro
4. Check network connectivity

### Issue: Agent responds but doesn't understand instructions

**Cause**: Instruction Verification Protocol not executed.

**Solution**:
1. Always execute Instruction Verification Protocol before implementation
2. Request agent to repeat key requirements in their own words
3. Correct any misunderstandings before authorizing work
4. Provide clarification for all questions asked

### Issue: Agent progress stalls without reporting blockers

**Cause**: Proactive polling not configured or agent not responding.

**Solution**:
1. Ensure 10-15 minute polling cycle is active
2. Include ALL mandatory poll questions (issues, unclear items, difficulties)
3. If no response after 2 polls, send escalation message using the `agent-messaging` skill
4. Consider reassigning if agent unresponsive

### Issue: Module assignment conflicts between agents

**Cause**: Same module assigned to multiple agents.

**Solution**:
1. Check current assignments: `/orchestration-status`
2. Use `/reassign-module` to move module to single agent
3. Notify previous assignee to stop work
4. Never assign same module to multiple agents simultaneously

### Issue: Agent completes work but PR fails verification

**Cause**: Acceptance criteria not met or 4-verification-loop not followed.

**Solution**:
1. Review PR against original acceptance criteria
2. Ensure agent followed 4-verification-loop protocol
3. Request fixes for failing criteria
4. Do NOT merge until all criteria pass
