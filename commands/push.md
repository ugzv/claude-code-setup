---
description: Push changes and update project state
---

Push to remote and update `.claude/state.json`. No unnecessary y/n confirmations, but still prompts for important input.

## 1. Check What's Being Pushed

```bash
git branch --show-current
git log @{upstream}..HEAD --oneline 2>/dev/null || git log origin/main..HEAD --oneline
```

If nothing to push, inform user and STOP.

## 2. Check State File

```bash
test -f .claude/state.json && cat .claude/state.json
```

If missing, create it automatically:
```json
{
  "project": "[folder name]",
  "currentFocus": null,
  "lastSession": null,
  "backlog": [],
  "shipped": []
}
```

## 3. Backlog Auto-Resolution

Scan commits being pushed against open backlog items:
- If a commit clearly resolves a backlog item → mark as resolved automatically
- If unclear → leave as open

Show what was auto-resolved:
```
Backlog: Auto-resolved #2 "Mobile menu bug" (addressed by commit fix(ui): mobile menu)
```

## 4. Update State File

**lastSession** - always update:
```json
"lastSession": {
  "date": "[today]",
  "summary": "[what was accomplished]",
  "commits": ["abc1234"]
}
```

**shipped** - determine type from commit messages:
- `feat`, `fix`, `refactor` → add to shipped
- `chore`, `style`, `docs` → skip shipped (no behavior change)

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

Keep last 10 entries in shipped.

## 5. Prompt for New Backlog Items

Ask: "Did you notice anything during this work to add to the backlog? (tech debt, bugs, ideas) - or 'no'"

If yes, collect:
- Task description
- Type: tech-debt / bug / idea / improvement
- Priority: high / medium / low

Add to backlog with status "open".

If "no", skip.

## 6. CurrentFocus Check

If currentFocus is set, ask: "Current focus: `[currentFocus]`. Still accurate? (yes / update to X / clear)"

- "yes" or no response → keep as is
- "update to X" → update currentFocus
- "clear" → set to null

If currentFocus is null, ask: "What's the current focus? (or 'none')"

## 7. Commit State + Push

```bash
git add .claude/state.json
git diff --cached --quiet || git commit -m "chore: update project state"
git push
```

**If push fails:**
- Report the error
- Tell user: "State committed locally. Fix push issue and run `git push` manually."
- Do NOT try to undo

## 8. Summary

```
PUSHED
======
Commits: 3 (abc1234, def5678, ghi9012)
Shipped: feat(ui): add modal component
Backlog: 1 auto-resolved, 2 open, 1 added
Focus: "Implementing dark mode"
```

## What We Ask vs Don't Ask

**DO ask (important input):**
- New backlog items discovered
- CurrentFocus still accurate

**DON'T ask (just do it):**
- "Proceed with push?" → just push
- "Update state?" → just update
- "Mark as resolved?" → auto-detect

$ARGUMENTS
