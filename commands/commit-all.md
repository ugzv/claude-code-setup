---
description: Commit all uncommitted changes, grouped intelligently into multiple commits
---

Find ALL uncommitted changes and commit them properly. Groups related changes into separate commits. Executes without asking for confirmation.

## 1. Discover All Changes

```bash
git status --porcelain
git diff --stat
```

If no changes found, inform user and STOP.

## 2. Analyze and Group Changes

Use the exact file paths from the git output above. Do not type paths from memory.

Group files by logical relationship:

**Grouping criteria:**
- Same feature/component (files in same directory or related names)
- Same type of change (all deletions, all config changes, renames)
- Same scope (auth-related, UI-related, etc.)
- Directory renames (deleted dir + new dir with same files = 1 commit)

## 3. Safety Check (Silent)

Skip these files automatically (don't commit, don't ask):
- `.env`, `*.pem`, `*.key` (secrets)
- `node_modules/`, `.next/`, `dist/` (should be gitignored)

If sensitive files found, mention in summary at the end.

## 4. Execute Commits

For each logical group, immediately:

```bash
git add <files-in-group>
git commit -m "type(scope): description"
```

**Commit message rules:**
- Conventional format: `type(scope): description`
- Types: feat, fix, refactor, style, docs, test, chore
- Under 72 characters, imperative mood
- NO "Co-authored-by", NO AI mentions

**For directory renames:**
```bash
git add -A docs/
git commit -m "refactor(docs): rename claude-agent-sdk to sdk-claude-agent-python"
```

## 5. Handle Issues (Don't Stop)

- Merge conflicts → skip file, note in summary
- Staging fails → skip file, continue with others

## 6. Summary

```
COMMITTED
=========
✓ abc1234 refactor(docs): rename sdk directory (62 files)
✓ def5678 fix(auth): update token validation (2 files)

Skipped:
  • .env (sensitive)
  • src/broken.ts (merge conflict)

Use /push when ready.
```

## What We Do vs Don't Do

**DO:**
- Analyze and group intelligently
- Execute commits immediately
- Report what was done

**DON'T:**
- Ask "Proceed? y/n"
- Ask "Is this grouping correct?"
- Wait for confirmation

$ARGUMENTS
