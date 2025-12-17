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

**backlog**:
- Auto-resolve items that match pushed commits
- Auto-ADD any tech debt, bugs, or improvements discovered during THIS session
- Claude should recall what it noticed while working and add those automatically

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
Backlog: 1 resolved, 1 added (found TODO in auth.ts), 2 open
```

Done.

## No Questions - Smart Automation

- Auto-resolves backlog items addressed by commits
- Auto-adds discoveries from this session (tech debt, TODOs, improvements noticed)
- No prompts, no confirmations

To manually manage backlog: `/backlog`

$ARGUMENTS
