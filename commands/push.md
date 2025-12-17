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
  "currentFocus": [],
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

**shipped** - add items that represent meaningful progress. Ask: "Would someone care that this happened?" Features, fixes, and refactors that change behavior count. Routine maintenance (`chore: bump deps`) usually doesn't—but use judgment. A chore that sets up CI/CD is meaningful. A docs change adding a tutorial is meaningful.

**currentFocus** - remove this session's focus item from the array (match by description of what you were working on). Other sessions' focus items stay.

**backlog**:
- Auto-resolve items that match pushed commits (mark as `"status": "resolved"`)
- Discoveries are captured during `/commit`, not here

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
Backlog: 1 resolved, 2 open
```

Done.

## No Questions - Smart Automation

- Auto-resolves backlog items addressed by commits
- No prompts, no confirmations

Discoveries are captured during `/commit` while context is fresh.

To manually manage backlog: `/backlog`

$ARGUMENTS
