# Release Coordination Procedure

## Table of Contents (Use-Case Oriented)

- **1.0 When you need to coordinate a software release** --> [Overview of the 5-Step Release Process](#1-overview-of-the-5-step-release-process)
  - **1.1 Understanding the release flow from branch to published release** --> [Release Flow Diagram](#11-release-flow-diagram)
  - **1.2 Deciding whether to use manual or automated release** --> [Manual vs Automated Release](#12-manual-vs-automated-release)
- **2.0 When assigning the version bump task to an implementer** --> [Step 1: Bump Version](#2-step-1-bump-version)
  - **2.1 Deciding which version number to use (major, minor, or patch)** --> [Semantic Versioning Decision Rules](#21-semantic-versioning-decision-rules)
  - **2.2 Verifying the version bump was performed correctly** --> [Version Bump Verification](#22-version-bump-verification)
- **3.0 When assigning the changelog update task to an implementer** --> [Step 2: Update CHANGELOG](#3-step-2-update-changelog)
  - **3.1 Verifying the changelog entry is complete and correct** --> [Changelog Verification Checklist](#31-changelog-verification-checklist)
- **4.0 When assigning the pull request creation task** --> [Step 3: Create Pull Request to Main Branch](#4-step-3-create-pull-request-to-main-branch)
- **5.0 When verifying the merge and automated pipeline** --> [Step 4: Merge to Main and Monitor Automation](#5-step-4-merge-to-main-and-monitor-automation)
- **6.0 When verifying the release was published correctly** --> [Step 5: Post-Release Verification](#6-step-5-post-release-verification)
- **7.0 When a release step fails** --> [Error Handling for Each Step](#7-error-handling-for-each-step)
- **8.0 Example: Complete release coordination message to implementer** --> [Example Delegation Messages](#8-example-delegation-messages)
- **9.0 Post-release verification checklist** --> [Post-Release Verification Checklist](#9-post-release-verification-checklist)

---

## 1. Overview of the 5-Step Release Process

A "release" is the process of publishing a new version of the software so that users can download or install it. The Orchestrator coordinates this process by assigning each step to an implementer (a Programmer Agent or human developer) and verifying completion before advancing to the next step.

The five steps are:

| Step | Name | Who Performs It | Orchestrator Role |
|------|------|-----------------|-------------------|
| 1 | Bump Version | Implementer | Assign task, provide semver rules, verify result |
| 2 | Update CHANGELOG | Implementer | Assign task, verify completeness and formatting |
| 3 | Create Pull Request to main | Implementer | Assign task, ensure CI tests pass before merge |
| 4 | Merge to main | Implementer or maintainer | Monitor automated pipeline, verify tag creation |
| 5 | Post-Release Verification | Orchestrator | Check GitHub Actions, Releases page, README badge |

**Important terms used in this document:**

- **Semantic Versioning (semver)**: A versioning scheme using three numbers: MAJOR.MINOR.PATCH (for example, 2.8.1). Each number has specific rules for when it increments. See section 2.1 for full rules.
- **CHANGELOG**: A file (usually named `CHANGELOG.md`) in the project root that records what changed in each version, in human-readable format.
- **Main branch**: The primary branch (often called `main` or `master`) that represents the production-ready state of the code.
- **Development branch**: The branch where active development happens (often called `develop` or a feature branch), before merging to main.
- **Git tag**: A label attached to a specific commit in the git history, used to mark release points (for example, `v2.8.0`).
- **CI/CD pipeline**: Continuous Integration / Continuous Delivery -- automated workflows that run tests, build artifacts, and publish releases when triggered by events like merging code or pushing tags.

### 1.1 Release Flow Diagram

The following diagram shows the complete release flow from the development branch to a published release:

```
  development branch                  main branch
  ------------------                  -----------
       |                                   |
       |  Step 1: Bump version             |
       |  (implementer runs version        |
       |   bump script or edits            |
       |   version files manually)         |
       |                                   |
       v                                   |
  +-----------+                            |
  | v2.8.0    |  Step 2: Update CHANGELOG  |
  | commit    |  (implementer adds entry   |
  | with new  |   for new version)         |
  | version   |                            |
  +-----------+                            |
       |                                   |
       |  Step 3: Create PR to main        |
       |  (implementer pushes branch,      |
       |   opens pull request)             |
       +---------------------------------->|
                                           |
                            Step 4: Merge  v
                                     +-----------+
                                     | v2.8.0    |
                                     | on main   |
                                     +-----+-----+
                                           |
                          +----------------+----------------+
                          |   Automated CI/CD Pipeline      |
                          +---------------------------------+
                          | a. Detect version > latest tag  |
                          | b. Validate CHANGELOG entry     |
                          | c. Create git tag (v2.8.0)      |
                          | d. Build artifacts              |
                          | e. Run security scans           |
                          | f. Publish GitHub Release       |
                          | g. Update README badge          |
                          +---------------------------------+
                                           |
                            Step 5: Verify release
                            (orchestrator checks
                             Actions, Releases, README)
```

### 1.2 Manual vs Automated Release

**Use the automated release process** (described in this document) when:
- The project has a CI/CD pipeline configured (for example, GitHub Actions workflows for release preparation and publishing)
- The release follows the normal development cycle
- All tests pass on the development branch

**Use a manual release** only in emergencies when:
- The automated pipeline is broken and cannot be fixed quickly
- A critical security fix must be published immediately
- The CI/CD infrastructure is unavailable

To perform a manual release, create a git tag directly on the main branch:

```bash
# WARNING: Only use this in emergencies
# Ensure the version in your project configuration files matches the tag
git tag -a v2.8.0 -m "Release v2.8.0"
git push origin v2.8.0
```

Manual releases carry risk because they bypass changelog validation, automated tests, and build verification. Always return to the automated process as soon as possible.

---

## 2. Step 1: Bump Version

**What this step does**: The implementer updates all version number references in the project to reflect the new release version.

**What the Orchestrator must provide to the implementer:**
1. The new version number (or the bump type: patch, minor, or major)
2. Which files contain version numbers that must be updated
3. The rule that the working directory must be clean (no uncommitted changes) before bumping

**What the implementer must do:**
1. Verify the git working directory is clean (`git status` shows no uncommitted changes)
2. Run the version bump command or manually edit version files
3. Commit the version change with a conventional commit message: `chore: bump version to X.Y.Z`

**Example version bump command** (if the project has a bump script):

```bash
# For a patch release (bug fixes only)
node scripts/bump-version.js patch

# For a minor release (new features, backwards compatible)
node scripts/bump-version.js minor

# For a major release (breaking changes)
node scripts/bump-version.js major

# For a specific version number
node scripts/bump-version.js 2.8.0
```

If the project does not have a bump script, the implementer must manually edit each file that contains a version number. Common locations include:
- `package.json` (Node.js projects)
- `pyproject.toml` (Python projects)
- `Cargo.toml` (Rust projects)
- `__init__.py` or `__version__.py` (Python modules)
- Any configuration files that embed the version string

### 2.1 Semantic Versioning Decision Rules

Semantic Versioning uses the format MAJOR.MINOR.PATCH (for example, 2.8.1). The Orchestrator must decide which number to increment based on the changes included in the release.

| Bump Type | When to Use | Example |
|-----------|-------------|---------|
| **PATCH** (0.0.X) | Bug fixes that do not change existing behavior. Documentation corrections. Performance improvements with no API changes. | 2.8.0 --> 2.8.1 |
| **MINOR** (0.X.0) | New features that are backwards compatible. New optional configuration options. New API endpoints that do not change existing ones. Deprecation of existing features (the features still work but are marked for future removal). | 2.8.1 --> 2.9.0 |
| **MAJOR** (X.0.0) | Breaking changes that require users to modify their code or configuration. Removal of previously deprecated features. Changes to existing API contracts. Database schema changes that require migration. | 2.9.0 --> 3.0.0 |

**Decision flowchart:**

```
Does this release remove or change existing behavior
that users depend on?
  |
  +-- YES --> MAJOR bump
  |
  +-- NO --> Does this release add new functionality?
               |
               +-- YES --> MINOR bump
               |
               +-- NO --> PATCH bump
```

**Examples of each bump type:**

PATCH bump examples:
- "Fixed crash when opening files larger than 100MB"
- "Corrected typo in error message for invalid input"
- "Improved startup time by 15% with no API changes"

MINOR bump examples:
- "Added dark mode support (opt-in via settings)"
- "New /api/v2/export endpoint for CSV export"
- "Added support for YAML configuration files alongside existing JSON"

MAJOR bump examples:
- "Renamed configuration key `db_url` to `database_connection_string`"
- "Removed deprecated /api/v1/users endpoint (use /api/v2/users instead)"
- "Changed default authentication from API keys to OAuth2"

### 2.2 Version Bump Verification

After the implementer reports that the version bump is complete, the Orchestrator must verify:

```
- [ ] The version number follows semantic versioning rules (MAJOR.MINOR.PATCH)
- [ ] All version files were updated consistently (no file still shows old version)
- [ ] The commit message follows conventional commit format: "chore: bump version to X.Y.Z"
- [ ] The git working directory was clean before the bump (no unrelated changes mixed in)
- [ ] The new version is strictly greater than the current latest tag
```

---

## 3. Step 2: Update CHANGELOG

**What this step does**: The implementer adds a human-readable entry to CHANGELOG.md describing what changed in this version.

**Why this step is critical**: Many release pipelines validate that a changelog entry exists for the version being released. If the entry is missing, the automated release will fail and block the entire pipeline.

**What the Orchestrator must provide to the implementer:**
1. The version number (must match the version from Step 1)
2. A summary of changes to include (gathered from completed tasks, merged PRs, and resolved issues)
3. The changelog format required by the project (see changelog-writing-guidelines.md for detailed formatting rules)

**What the implementer must do:**
1. Add a new entry at the top of CHANGELOG.md with the version number as the heading
2. Group changes by category (New Features, Improvements, Bug Fixes, Breaking Changes)
3. Include specific descriptions (not vague summaries)
4. Reference related issue numbers where applicable
5. Include migration instructions for any breaking changes
6. Amend the version bump commit to include the changelog update:

```bash
git add CHANGELOG.md
git commit --amend --no-edit
```

### 3.1 Changelog Verification Checklist

After the implementer reports that the changelog is updated, the Orchestrator must verify:

```
- [ ] The CHANGELOG.md heading matches the version from Step 1 exactly (for example, "## 2.8.0")
- [ ] Changes are grouped by impact category
- [ ] Each entry is specific (not "Fixed bugs" but "Fixed crash when processing files over 100MB")
- [ ] Breaking changes are clearly marked with migration instructions
- [ ] Related issue numbers are referenced using #N syntax (for example, "Fixes #123")
- [ ] The changelog entry is at the TOP of the file (newest version first)
- [ ] The commit now includes both the version bump and the changelog update
```

For detailed changelog writing rules, see [changelog-writing-guidelines.md](changelog-writing-guidelines.md).

---

## 4. Step 3: Create Pull Request to Main Branch

**What this step does**: The implementer pushes the development branch and creates a pull request targeting the main branch.

**What the Orchestrator must provide to the implementer:**
1. The target branch name (usually `main` or `master`)
2. The PR title format (for example, "Release v2.8.0")
3. Instructions to verify that all CI checks pass before requesting merge

**What the implementer must do:**
1. Push the development branch to the remote repository
2. Create a pull request targeting the main branch
3. Wait for all automated checks (tests, linting, security scans) to pass
4. Request review if the project requires PR approval

**Example commands:**

```bash
# Push the branch
git push origin develop

# Create the pull request using GitHub CLI
gh pr create --base main --title "Release v2.8.0" --body "Release version 2.8.0. See CHANGELOG.md for details."
```

**Orchestrator verification before approving merge:**

```
- [ ] All CI checks pass (tests, lint, security)
- [ ] The PR contains only the version bump commit and changelog update
- [ ] No unrelated changes are included in the PR
- [ ] The PR targets the correct base branch (main)
```

---

## 5. Step 4: Merge to Main and Monitor Automation

**What this step does**: After the PR is approved and merged, the CI/CD pipeline automatically detects the version bump and creates a release.

**What the Orchestrator must monitor:**
1. The merge completes successfully
2. The release preparation workflow detects the new version
3. The changelog validation passes (the pipeline confirms the entry exists)
4. A git tag is created automatically (for example, `v2.8.0`)
5. The release build workflow is triggered by the new tag

**Typical automated pipeline sequence:**

| Step | What Happens | What to Check |
|------|-------------|---------------|
| a | Pipeline detects version in project files is greater than latest git tag | Workflow run starts in GitHub Actions |
| b | Pipeline validates CHANGELOG.md has an entry for this version | No "CHANGELOG VALIDATION FAILED" error |
| c | Pipeline creates an annotated git tag | Tag appears in repository tags list |
| d | Tag creation triggers the release build workflow | Second workflow run starts |
| e | Build workflow compiles artifacts for all platforms | All build jobs succeed |
| f | Release is published on GitHub Releases page | Release page shows new version |

**Important**: If the project uses a Personal Access Token (PAT) for tag creation (required because GitHub's default GITHUB_TOKEN does not trigger downstream workflows when it pushes tags), verify that the PAT is configured and not expired.

---

## 6. Step 5: Post-Release Verification

**What this step does**: The Orchestrator verifies that the release was published correctly and all artifacts are available.

See section 9 for the complete verification checklist.

---

## 7. Error Handling for Each Step

### If Step 1 (Version Bump) Fails

| Problem | Cause | What to Do |
|---------|-------|------------|
| Working directory is not clean | Uncommitted changes exist | Instruct the implementer to commit or stash changes before bumping |
| Version files are inconsistent | Some files were updated, others were not | Instruct the implementer to check all version file locations and update them all |
| New version is not greater than current tag | Wrong bump type or version string | Verify the latest tag with `git tag -l 'v*' --sort=-version:refname | head -1` and choose a higher version |

### If Step 2 (Changelog Update) Fails

| Problem | Cause | What to Do |
|---------|-------|------------|
| Changelog entry is vague | Implementer wrote generic descriptions | Provide specific change descriptions gathered from task records and merged PRs |
| Version heading does not match | Typo or format mismatch | Verify the heading format matches exactly (for example, `## 2.8.0` not `## v2.8.0` unless the project uses the `v` prefix) |
| Missing breaking change documentation | Changes were not identified as breaking | Review the list of changes and identify any that alter existing behavior |

### If Step 3 (Pull Request) Fails

| Problem | Cause | What to Do |
|---------|-------|------------|
| CI checks fail | Tests broken, lint errors, security issues | Instruct the implementer to fix the failing checks on the development branch before re-creating the PR |
| PR contains unrelated changes | Branch was not clean | Instruct the implementer to create a clean branch from the latest development branch with only the version bump and changelog commits |
| Merge conflicts | Main branch has changes not in the development branch | Instruct the implementer to rebase the development branch on main and resolve conflicts |

### If Step 4 (Automated Pipeline) Fails

| Problem | Cause | What to Do |
|---------|-------|------------|
| Pipeline did not trigger | Version was not greater than latest tag, or the push event was not detected | Check `git tag -l 'v*' --sort=-version:refname | head -1` and verify the version in project files is greater |
| Changelog validation failed | The pipeline could not find the version heading in CHANGELOG.md | Push a commit to main that adds the missing changelog entry, then the pipeline will retry |
| Tag was created but release build failed | Build error, dependency issue, or infrastructure problem | Do NOT reuse the failed version number. Fix the issue, bump to a new patch version, and restart from Step 1 |
| Tag push did not trigger release workflow | Using GITHUB_TOKEN instead of a PAT for tag push | Configure a Personal Access Token with `repo` scope and update the workflow secret |

### If Step 5 (Verification) Fails

| Problem | Cause | What to Do |
|---------|-------|------------|
| Release page is missing | Build workflow failed or did not complete | Check GitHub Actions for the release workflow run and review error logs |
| README badge shows old version | README update step failed or release was incomplete | Manually trigger the README update or wait for the next successful release |
| Artifacts are missing or incomplete | Platform-specific build failed | Check the build matrix results for each platform and fix the failing platform |

---

## 8. Example Delegation Messages

### Example: Assigning the complete release task to an implementer

```
TASK: Prepare release v2.8.0

CONTEXT:
The following changes are ready for release:
- Added CSV export endpoint (PR #45)
- Fixed memory leak in file processor (PR #48)
- Updated dependency X to version 3.2.1 (PR #50)

STEPS YOU MUST PERFORM:

1. BUMP VERSION
   - Verify your working directory is clean (git status shows no changes)
   - Run: node scripts/bump-version.js minor
   - This creates a commit "chore: bump version to 2.8.0"

2. UPDATE CHANGELOG
   - Open CHANGELOG.md
   - Add this entry at the TOP of the file:

     ## 2.8.0 - CSV Export and Stability Improvements

     ### New Features
     - Added CSV export endpoint at /api/v2/export (#45)

     ### Bug Fixes
     - Fixed memory leak when processing files larger than 500MB (#48)

     ### Dependencies
     - Updated dependency X from 3.1.0 to 3.2.1 (#50)

     ---

   - Amend the version bump commit:
     git add CHANGELOG.md
     git commit --amend --no-edit

3. CREATE PULL REQUEST
   - Push your branch: git push origin develop
   - Create PR: gh pr create --base main --title "Release v2.8.0"
   - Wait for all CI checks to pass
   - Report back with the PR URL

SUCCESS CRITERIA:
- Version is 2.8.0 in all project files
- CHANGELOG.md has entry for 2.8.0 with all three changes listed
- PR is created targeting main with all CI checks passing
- Report the PR URL when done
```

---

## 9. Post-Release Verification Checklist

Use this checklist after the merge to main and automated pipeline completion:

```
RELEASE VERIFICATION: v2.8.0

CI/CD Pipeline:
- [ ] Release preparation workflow completed successfully
- [ ] Changelog validation passed (no "CHANGELOG VALIDATION FAILED" error)
- [ ] Git tag v2.8.0 was created automatically
- [ ] Release build workflow was triggered and completed

GitHub Releases Page:
- [ ] New release v2.8.0 appears on the Releases page
- [ ] Release notes match the CHANGELOG.md entry
- [ ] All expected build artifacts are attached (if applicable)
- [ ] Download links are functional

Repository State:
- [ ] README badge shows version 2.8.0 (if the project has version badges)
- [ ] No open issues reporting problems with the release
- [ ] Main branch is in a clean state (no broken CI)

Notifications:
- [ ] Team has been notified of the new release
- [ ] Any external stakeholders have been informed (if applicable)
```

---

## See Also

- [changelog-writing-guidelines.md](changelog-writing-guidelines.md) -- Detailed rules for writing good release notes
- [workflow-checklists.md](workflow-checklists.md) -- General task delegation checklists
- [verification-loops.md](verification-loops.md) -- Verification loop protocol before creating PRs
