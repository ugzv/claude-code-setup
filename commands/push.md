---
description: Push changes and update project state
---

Push to remote and update `.claude/state.json`. Fully automatic - no questions.

## 1. Check What's Being Pushed

```bash
git branch --show-current
git log @{upstream}..HEAD --oneline 2>/dev/null || git log origin/main..HEAD --oneline
```

If nothing to push, inform user and STOP.

## 2. Read/Create State File

```bash
test -f .claude/state.json && cat .claude/state.json
```

If missing, create automatically:
```json
{
  "project": "[folder name]",
  "currentFocus": null,
  "lastSession": null,
  "backlog": [],
  "shipped": []
}
```

## 3. Auto-Update State

**lastSession** - always update:
```json
"lastSession": {
  "date": "[today]",
  "summary": "[what was accomplished based on commits]",
  "commits": ["abc1234"]
}
```

**shipped** - auto-determine from commit messages:
- `feat`, `fix`, `refactor` → add to shipped
- `chore`, `style`, `docs` → skip (no behavior change)

**backlog** - auto-resolve items that match pushed commits, keep the rest.

## 4. Commit State + Push

```bash
git add .claude/state.json
git diff --cached --quiet || git commit -m "chore: update project state"
git push
```

If push fails, report error and stop.

## 5. Summary

```
PUSHED
======
Commits: 3
Shipped: feat(ui): add modal
Backlog: 1 auto-resolved, 2 open
```

Done.

## No Questions

This command asks nothing. Just executes.

To add backlog items manually: `/backlog`
To update currentFocus manually: edit `.claude/state.json` or tell Claude

$ARGUMENTS
