## Table of Contents
- [Even Distribution](#even-distribution)
- [Specialization](#specialization)

---

## Even Distribution

When multiple agents can handle a task:

1. Check current load (active tasks per agent)
2. Prefer agent with lowest load
3. If equal load, prefer agent who completed similar tasks recently

## Specialization

Some tasks benefit from agent specialization:

| Task Type | Preferred Agent |
|-----------|-----------------|
| Code review | Agent who wrote the code (context) |
| Bug fix | Agent who implemented feature |
| New feature | Agent with matching skills |
