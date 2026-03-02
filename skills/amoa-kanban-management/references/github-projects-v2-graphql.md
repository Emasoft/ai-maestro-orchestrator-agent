# GitHub Projects V2 GraphQL Mutations

## Table of Contents

- 2.1 Querying project fields and their IDs - Getting field and option IDs
- 2.2 Moving an item to a different column - updateProjectV2ItemFieldValue mutation
- 2.3 Adding columns to a field - updateProjectV2Field mutation (DANGER: replaces all options)
- 2.4 Creating a project item from an issue - addProjectV2ItemById mutation
- 2.5 Deleting a project item - deleteProjectV2Item mutation
- 2.6 Common parameter mistakes - fieldId vs projectId confusion
- 2.7 Working examples with gh api graphql - Copy-paste ready commands

---

## 2.1 Querying project fields and their IDs

Before making any mutations, you need the IDs of the project, its fields, and the field options (column names). Use this query to get all of them at once.

**Query: Get project ID, field IDs, and option IDs**

```bash
gh api graphql -f query='
  query($owner: String!, $number: Int!) {
    user(login: $owner) {
      projectV2(number: $number) {
        id
        title
        fields(first: 20) {
          nodes {
            ... on ProjectV2SingleSelectField {
              id
              name
              options {
                id
                name
              }
            }
            ... on ProjectV2Field {
              id
              name
            }
            ... on ProjectV2IterationField {
              id
              name
            }
          }
        }
      }
    }
  }
' -f owner="Emasoft" -F number=1
```

**Example output (relevant parts):**

```json
{
  "data": {
    "user": {
      "projectV2": {
        "id": "PVT_kwHOAAVQbc4A...",
        "title": "My Project",
        "fields": {
          "nodes": [
            {
              "id": "PVTF_lAHOAAVQbc4A...",
              "name": "Status",
              "options": [
                {"id": "f75ad846", "name": "Backlog"},
                {"id": "47fc9ee4", "name": "Todo"},
                {"id": "98236657", "name": "In Progress"},
                {"id": "0d8fcf92", "name": "Done"}
              ]
            }
          ]
        }
      }
    }
  }
}
```

**Key IDs you need:**
- `projectV2.id` = the project ID (starts with `PVT_`)
- `fields.nodes[].id` = the field ID (starts with `PVTF_`)
- `options[].id` = the option ID for each column

**For organization-owned projects**, replace `user(login: $owner)` with `organization(login: $owner)`.

---

## 2.2 Moving an item to a different column

Use the `updateProjectV2ItemFieldValue` mutation to change an item's status (move it to a different column).

**Mutation: updateProjectV2ItemFieldValue**

```graphql
mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
  updateProjectV2ItemFieldValue(
    input: {
      projectId: $projectId
      itemId: $itemId
      fieldId: $fieldId
      value: {
        singleSelectOptionId: $optionId
      }
    }
  ) {
    projectV2Item {
      id
    }
  }
}
```

**Parameters:**
- `projectId`: The project ID (from Section 2.1, starts with `PVT_`)
- `itemId`: The project item ID (starts with `PVTI_`)
- `fieldId`: The Status field ID (starts with `PVTF_`)
- `optionId`: The target column's option ID (from Section 2.1)

**Example using gh CLI:**

```bash
gh api graphql -f query='
  mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
    updateProjectV2ItemFieldValue(
      input: {
        projectId: $projectId
        itemId: $itemId
        fieldId: $fieldId
        value: {
          singleSelectOptionId: $optionId
        }
      }
    ) {
      projectV2Item {
        id
      }
    }
  }
' -f projectId="PVT_kwHOAAVQbc4A..." \
  -f itemId="PVTI_lAHOAAVQbc4A..." \
  -f fieldId="PVTF_lAHOAAVQbc4A..." \
  -f optionId="47fc9ee4"
```

**Alternative using gh project item-edit (simpler):**

```bash
gh project item-edit \
  --project-id "PVT_kwHOAAVQbc4A..." \
  --id "PVTI_lAHOAAVQbc4A..." \
  --field-id "PVTF_lAHOAAVQbc4A..." \
  --single-select-option-id "47fc9ee4"
```

---

## 2.3 Adding columns to a field

**DANGER: The `updateProjectV2Field` mutation REPLACES all options. If you do not include existing option IDs in the mutation, ALL existing column assignments will be lost. See [kanban-pitfalls.md](kanban-pitfalls.md) Section 3.2.**

**Mutation: updateProjectV2Field**

```graphql
mutation($fieldId: ID!, $name: String!, $options: [ProjectV2SingleSelectFieldOptionInput!]!) {
  updateProjectV2Field(
    input: {
      fieldId: $fieldId
      name: $name
      singleSelectOptions: $options
    }
  ) {
    projectV2Field {
      ... on ProjectV2SingleSelectField {
        id
        name
        options {
          id
          name
        }
      }
    }
  }
}
```

**CRITICAL: This mutation does NOT accept `projectId`.** It only takes `fieldId`. The project context is implicit from the field. Passing `projectId` will cause this error:

```
InputObject 'UpdateProjectV2FieldInput' doesn't accept argument 'projectId'
```

**Parameters:**
- `fieldId`: The field ID (starts with `PVTF_`)
- `name`: The field name (e.g., "Status")
- `singleSelectOptions`: Array of ALL options (existing + new). Each option has:
  - `name`: Column name (string)
  - `id`: Existing option ID (string) - REQUIRED for existing options to preserve assignments
  - `color`: Optional color
  - `description`: Optional description

**Safe procedure for adding columns:**

1. First, query existing options (Section 2.1)
2. Build the options array including ALL existing options with their IDs
3. Append new options (without IDs - GitHub will generate them)
4. Execute the mutation with the complete options array
5. Verify existing assignments survived

**ALWAYS use `scripts/gh-project-add-columns.sh` instead of calling this mutation directly.** The script handles the safe preservation of existing options automatically.

---

## 2.4 Creating a project item from an issue

Use the `addProjectV2ItemById` mutation to add an existing issue to a project board.

**Mutation: addProjectV2ItemById**

```graphql
mutation($projectId: ID!, $contentId: ID!) {
  addProjectV2ItemById(
    input: {
      projectId: $projectId
      contentId: $contentId
    }
  ) {
    item {
      id
    }
  }
}
```

**Parameters:**
- `projectId`: The project ID (starts with `PVT_`)
- `contentId`: The issue or PR node ID (the GraphQL node ID, NOT the issue number)

**Getting the issue node ID:**

```bash
gh api graphql -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      issue(number: $number) {
        id
        title
      }
    }
  }
' -f owner="Emasoft" -f repo="myproject" -F number=42
```

**Alternative using gh CLI (simpler):**

```bash
gh project item-add <project-number> --owner Emasoft --url "https://github.com/Emasoft/myproject/issues/42"
```

---

## 2.5 Deleting a project item

Use the `deleteProjectV2Item` mutation to remove an item from a project board.

**Mutation: deleteProjectV2Item**

```graphql
mutation($projectId: ID!, $itemId: ID!) {
  deleteProjectV2Item(
    input: {
      projectId: $projectId
      itemId: $itemId
    }
  ) {
    deletedItemId
  }
}
```

**Parameters:**
- `projectId`: The project ID (starts with `PVT_`)
- `itemId`: The item ID (starts with `PVTI_`)

**Note:** Deleting a project item does NOT close or delete the underlying issue. It only removes the item from the project board.

---

## 2.6 Common parameter mistakes

### Mistake 1: Passing `projectId` to `updateProjectV2Field`

**Wrong:**
```graphql
mutation {
  updateProjectV2Field(input: {
    projectId: "PVT_..."    # ERROR: not accepted
    fieldId: "PVTF_..."
    name: "Status"
    singleSelectOptions: [...]
  }) { ... }
}
```

**Error message:**
```
InputObject 'UpdateProjectV2FieldInput' doesn't accept argument 'projectId'
```

**Correct:**
```graphql
mutation {
  updateProjectV2Field(input: {
    fieldId: "PVTF_..."     # Only fieldId is needed
    name: "Status"
    singleSelectOptions: [...]
  }) { ... }
}
```

The `fieldId` already implies the project. No `projectId` is needed.

### Mistake 2: Omitting existing option IDs when updating field

**Wrong (loses all existing assignments):**
```json
{
  "singleSelectOptions": [
    {"name": "New Column 1"},
    {"name": "New Column 2"}
  ]
}
```

**Correct (preserves existing assignments):**
```json
{
  "singleSelectOptions": [
    {"id": "f75ad846", "name": "Backlog"},
    {"id": "47fc9ee4", "name": "Todo"},
    {"id": "98236657", "name": "In Progress"},
    {"id": "0d8fcf92", "name": "Done"},
    {"name": "New Column 1"},
    {"name": "New Column 2"}
  ]
}
```

### Mistake 3: Using issue number instead of node ID for addProjectV2ItemById

**Wrong:**
```json
{"contentId": "42"}
```

**Correct:**
```json
{"contentId": "I_kwDOAAVQbc5..."}
```

The `contentId` is the GraphQL node ID, NOT the issue number. Use the query in Section 2.4 to get it, or use `gh project item-add` which accepts the URL directly.

---

## 2.7 Working examples with gh api graphql

### Example 1: List all columns in a project's Status field

```bash
gh api graphql -f query='
  query($owner: String!, $number: Int!) {
    user(login: $owner) {
      projectV2(number: $number) {
        fields(first: 20) {
          nodes {
            ... on ProjectV2SingleSelectField {
              name
              options {
                id
                name
              }
            }
          }
        }
      }
    }
  }
' -f owner="Emasoft" -F number=1 | jq '.data.user.projectV2.fields.nodes[] | select(.options) | select(.name == "Status")'
```

### Example 2: Get all items and their current column

```bash
gh api graphql -f query='
  query($owner: String!, $number: Int!) {
    user(login: $owner) {
      projectV2(number: $number) {
        items(first: 100) {
          nodes {
            fieldValues(first: 10) {
              nodes {
                ... on ProjectV2ItemFieldSingleSelectValue {
                  name
                  field {
                    ... on ProjectV2SingleSelectField {
                      name
                    }
                  }
                }
              }
            }
            content {
              ... on Issue {
                number
                title
              }
            }
          }
        }
      }
    }
  }
' -f owner="Emasoft" -F number=1
```

### Example 3: Move issue #42 from "In Progress" to "AI Review"

```bash
# Step 1: Get project ID, item ID, field ID, and option ID
PROJECT_DATA=$(gh api graphql -f query='
  query($owner: String!, $number: Int!) {
    user(login: $owner) {
      projectV2(number: $number) {
        id
        fields(first: 20) {
          nodes {
            ... on ProjectV2SingleSelectField {
              id
              name
              options { id name }
            }
          }
        }
        items(first: 100) {
          nodes {
            id
            content {
              ... on Issue { number }
            }
          }
        }
      }
    }
  }
' -f owner="Emasoft" -F number=1)

PROJECT_ID=$(echo "$PROJECT_DATA" | jq -r '.data.user.projectV2.id')
ITEM_ID=$(echo "$PROJECT_DATA" | jq -r '.data.user.projectV2.items.nodes[] | select(.content.number == 42) | .id')
FIELD_ID=$(echo "$PROJECT_DATA" | jq -r '.data.user.projectV2.fields.nodes[] | select(.name == "Status") | .id')
OPTION_ID=$(echo "$PROJECT_DATA" | jq -r '.data.user.projectV2.fields.nodes[] | select(.name == "Status") | .options[] | select(.name == "AI Review") | .id')

# Step 2: Move item
gh api graphql -f query='
  mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
    updateProjectV2ItemFieldValue(input: {
      projectId: $projectId
      itemId: $itemId
      fieldId: $fieldId
      value: { singleSelectOptionId: $optionId }
    }) {
      projectV2Item { id }
    }
  }
' -f projectId="$PROJECT_ID" -f itemId="$ITEM_ID" -f fieldId="$FIELD_ID" -f optionId="$OPTION_ID"
```

### Example 4: Create a new project

```bash
gh project create --owner Emasoft --title "New Project Board"
```

This creates a project with only the default "Status" field and default columns (Todo, In Progress, Done). Use `scripts/gh-project-add-columns.sh` to add the full 8-column system.
