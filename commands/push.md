---
description: Push changes and update project state
---

Push to remote and update `.claude/state.json`. Execute without unnecessary confirmations.

## 1. Check What's Being Pushed

```bash
git branch --show-current
git log @{upstream}..HEAD --oneline 2>/dev/null || git log origin/main..HEAD --oneline
```

If nothing to push, inform user and STOP.

## 2. Check State File

```bash
test -f .claude/state.json && echo "EXISTS" || echo "MISSING"
```

If missing, create it:
```json
{
  "project": "[folder name]",
  "currentFocus": null,
  "lastSession": null,
  "backlog": [],
  "shipped": []
}
```

## 3. Backlog Auto-Check

Scan commits being pushed against open backlog items:
- If a commit clearly resolves a backlog item → mark as resolved automatically
- If unclear → leave as open (don't ask)

## 4. Update State File

**lastSession** - always update:
```json
"lastSession": {
  "date": "[today]",
  "summary": "[what was accomplished]",
  "commits": ["abc1234"]
}
```

**shipped** - only if feat/fix/refactor (skip chore/style/docs):
- Determine change type from commit messages
- If `feat`, `fix`, or `refactor` → add to shipped
- If `chore`, `style`, `docs` → skip shipped, just update lastSession

```json
"shipped": [
  {
    "date": "[today]",
    "type": "feat|fix|refactor",
    "summary": "[one-line summary]",
    "commits": ["abc1234"]
  }
]
```

**backlog** - auto-resolve what was addressed, keep the rest.

## 5. Commit State + Push

```bash
git add .claude/state.json
git diff --cached --quiet || git commit -m "chore: update project state"
git push
```

## 6. Quick Summary

```
Pushed: 3 commits
Shipped: feat(ui): add modal component
Backlog: 1 resolved, 2 open
```

Done.

## 7. Only Ask If Needed

**DO NOT ask for confirmation on:**
- Whether to push
- Whether to update state
- Backlog resolution (auto-detect)

**ONLY ask if:**
- Push fails (report error)
- Ambiguous change type and can't determine from commits

$ARGUMENTS
