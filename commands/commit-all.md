---
description: Commit all uncommitted changes, grouped intelligently into multiple commits
---

Find ALL uncommitted changes and commit them properly, grouping related changes into separate commits.

## 1. Discover All Changes

```bash
git status --porcelain
git diff --stat
git diff --cached --stat
```

If no changes found, inform user and STOP.

## 2. Categorize All Changes

List every changed file and categorize:

```
UNCOMMITTED CHANGES FOUND
=========================

Staged:
  M  src/components/Button.tsx
  A  src/components/Modal.tsx

Unstaged:
  M  src/utils/auth.ts
  M  src/utils/api.ts
  D  src/old-file.ts

Untracked:
  ?  src/components/NewFeature.tsx
  ?  .env.example
```

## 3. Analyze and Group Changes

Analyze the changes and group them by logical relationship:

**Grouping criteria:**
- Same feature/component (files in same directory or with related names)
- Same type of change (all deletions, all config changes, all test files)
- Same scope (auth-related, UI-related, etc.)
- Dependencies (if file A imports file B and both changed, group them)

**Read changed files if needed** to understand what changed and group properly.

## 4. Propose Commit Plan

Show the user a commit plan:

```
PROPOSED COMMIT PLAN
====================

Commit 1: feat(ui): add Modal component
  • src/components/Modal.tsx (new)
  • src/components/Button.tsx (updated - uses Modal)

Commit 2: refactor(auth): update authentication utilities
  • src/utils/auth.ts
  • src/utils/api.ts

Commit 3: chore: remove deprecated files
  • src/old-file.ts (deleted)

Commit 4: chore: add environment example
  • .env.example (new)

──────────────────────
Total: 4 commits for 6 files

Proceed with this plan? (y/n/edit)
```

**If user says "edit":** Ask which grouping to change and adjust.

## 5. Safety Checks

Before committing, verify:

**Do NOT commit these files (warn user):**
- `.env` (secrets)
- `*.pem`, `*.key` (private keys)
- `credentials.json`, `secrets.*`
- `node_modules/`, `.next/`, `dist/` (should be gitignored)

If found, warn:
```
⚠️  WARNING: Found potentially sensitive files:
  • .env (contains secrets)

These will be SKIPPED. Add to .gitignore if not already.
```

## 6. Execute Commits

For each group in the plan:

```bash
# Stage files for this commit
git add <file1> <file2> ...

# Commit with quality message
git commit -m "type(scope): description"
```

**Commit message rules:**
- Conventional format: `type(scope): description`
- Types: feat, fix, refactor, style, docs, test, chore
- Under 72 characters
- Imperative mood
- NO "Co-authored-by" or AI mentions

## 7. Handle Conflicts/Issues

**If a file has merge conflicts:**
- Skip it
- Report: "Skipped file.ts - has merge conflicts. Resolve manually."

**If staging fails:**
- Report the error
- Continue with other commits

## 8. Summary

```
COMMIT COMPLETE
===============

Created 4 commits:
  ✓ abc1234 feat(ui): add Modal component (2 files)
  ✓ def5678 refactor(auth): update authentication utilities (2 files)
  ✓ 789abcd chore: remove deprecated files (1 file)
  ✓ cde0123 chore: add environment example (1 file)

Skipped:
  • .env (sensitive file)

Still uncommitted:
  (none)

Use /push when ready to push.
```

## 9. Edge Cases

**If everything is one logical change:**
- Create just one commit
- Don't force multiple commits unnecessarily

**If changes are too intermingled to separate:**
- Ask user: "These changes are interrelated. Commit as single commit or try to separate?"

**If there are 20+ unrelated files:**
- Group by directory first
- Then refine by relationship
- Ask user to confirm before proceeding

$ARGUMENTS
