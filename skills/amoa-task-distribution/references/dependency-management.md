## Table of Contents
- [Dependency Types](#dependency-types)
- [Dependency Resolution](#dependency-resolution)
- [Circular Dependency Detection](#circular-dependency-detection)

---

## Dependency Types

| Type | Example | Handling |
|------|---------|----------|
| Hard | Module B needs Module A's API | Block B until A complete |
| Soft | Testing can start with stubs | Assign with note about dependency |
| None | Independent tasks | Assign in parallel |

## Dependency Resolution

```
Task A: status:in-progress, blocks: [B, C]
Task B: status:ready, blockedBy: [A] -> Cannot assign yet
Task C: status:ready, blockedBy: [A] -> Cannot assign yet

When Task A completes:
- Update A: status:done
- B and C become assignable
```

## Circular Dependency Detection

If detected, STOP and report to user:

```
CIRCULAR DEPENDENCY:
Task A -> depends on -> Task B
Task B -> depends on -> Task A

Cannot proceed. User decision required.
```
