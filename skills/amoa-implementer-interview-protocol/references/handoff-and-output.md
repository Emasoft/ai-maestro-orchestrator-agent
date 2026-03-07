## Table of Contents
- [Handoff to Integrator](#handoff-to-integrator)
- [Responsibility Transfer](#responsibility-transfer)
- [Output Types](#output-types)

---

## Handoff to Integrator

### When PR is Created

After implementer creates PR and reports the number:

1. Update issue status: `status:ai-review`
2. Notify Integrator via AI Maestro (template in **amoa-messaging-templates**)
3. Transfer responsibility from orchestrator to integrator

### Responsibility Transfer

| Before PR Creation | After PR Creation |
|--------------------|-------------------|
| Orchestrator responsible | Integrator responsible |
| Implementer executes | Implementer responds to review |
| Task tracked via issue | Work tracked via PR |

---

## Output Types

| Output Type | Format | Example |
|-------------|--------|---------|
| Interview questions | Markdown message via AI Maestro | Pre-task or post-task question template |
| PROCEED approval | Markdown message | "PROCEED: Your understanding is confirmed. Begin implementation." |
| APPROVED approval | Markdown message | "APPROVED: Create PR with requirements X, Y, Z." |
| REVISE request | Markdown message | "REVISE: Issues found. Fix X, Y, Z before re-reporting." |
| Escalation to Architect | AI Maestro JSON | Design review request with concern details |
| Escalation to Manager | AI Maestro JSON | User decision request for requirement issue |
| Handoff to Integrator | AI Maestro JSON | PR ready for review notification |
