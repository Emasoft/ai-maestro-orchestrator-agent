## Table of Contents

- [Decision Tree: Choosing Communication Type](#decision-tree-choosing-communication-type)

---

# Decision Tree: Choosing Communication Type

```
Is this about code you're reviewing?
├── YES → See pr-comment-writing.md
│   ├── Is it a blocking issue? → Request Changes
│   ├── Is it a suggestion? → Comment (non-blocking)
│   └── Is it praise? → Approve with comment
│
└── NO → Is this about an issue/ticket?
    ├── YES → See issue-communication.md
    │   ├── Bug report? → Acknowledge, reproduce, respond
    │   ├── Feature request? → Thank, set expectations
    │   └── Question? → Answer or redirect
    │
    └── NO → Is this explaining technical decisions?
        ├── YES → See technical-explanation.md
        │
        └── NO → Is this a conflict or disagreement?
            ├── YES → See conflict-resolution.md
            │
            └── NO → Is this a progress/status update?
                ├── YES → See status-updates.md
                │
                └── NO → See templates-for-humans.md for general formats
```
