---
description: Push changes and update project state
---

Ship your work: push to remote and update `.claude/state.json`.

## 1. Detect Branch and Remote

```bash
git branch --show-current
git rev-parse --abbrev-ref @{upstream} 2>/dev/null || echo "NO_UPSTREAM"
```

## 2. Review What's Being Pushed

```bash
git log @{upstream}..HEAD --oneline 2>/dev/null || git log origin/$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')..HEAD --oneline
```

If nothing to push, inform user and STOP.

Show the commits that will be pushed.

## 3. Check State File Exists

```bash
test -f .claude/state.json && echo "EXISTS" || echo "MISSING"
```

If missing, ask: "State file not found. Run `/migrate` first, or create now?"

If create now, initialize with:
```json
{
  "project": "[folder name]",
  "currentFocus": null,
  "lastSession": null,
  "backlog": [],
  "shipped": []
}
```

## 4. Read Current State

Read `.claude/state.json` to understand:
- Current backlog items
- What currentFocus was

## 5. Backlog Auto-Resolve Check

Review the commits being pushed. For EACH open backlog item, assess:
- Does this push address/resolve this item?

Show the user:
```
BACKLOG CHECK
=============
Analyzing commits against open backlog items...

✓ LIKELY RESOLVED:
  #2 [bug] Mobile menu doesn't close - your commit "fix(ui): mobile menu navigation" addresses this

? POSSIBLY RELATED:
  #1 [tech-debt] Refactor status constants - commit touches related files, unclear if resolved

• UNAFFECTED:
  #3 [idea] Add keyboard shortcuts
  #4 [improvement] Add dark mode

Mark #2 as resolved? (y/n)
Is #1 resolved? (y/n)
```

Wait for user confirmation before marking anything resolved.

## 6. Update State File

Update `.claude/state.json`:

**lastSession:**
```json
"lastSession": {
  "date": "[today]",
  "summary": "[describe what was accomplished based on commits]",
  "commits": ["abc1234", "def5678"]
}
```

**shipped** (prepend, keep last 10):

**ONLY add to shipped if it's a meaningful change:**
- ✓ `feat` - new features (always add)
- ✓ `fix` - bug fixes (always add)
- ✓ `refactor` - only if significant/breaking
- ✗ `chore` - skip (cleanup, delete unused files)
- ✗ `style` - skip (formatting)
- ✗ `docs` - skip unless significant

Ask user: "Is this a meaningful change to log? (feat/fix = yes, chore/cleanup = no)"

If yes:
```json
"shipped": [
  {
    "date": "[today]",
    "type": "feat|fix",
    "summary": "[one-line user-facing summary]",
    "commits": ["abc1234"]
  }
]
```

If no (chore/cleanup), skip adding to shipped.

**backlog:**
- Mark confirmed items as resolved with today's date
- Keep wont-do and resolved items (cleanup via `/backlog clean`)

## 7. Prompt for New Backlog Items

Ask: "Did you notice anything during this work to add to the backlog? (tech debt, bugs, ideas)"

If yes:
- Ask for task description
- Ask for type (tech-debt / bug / idea / improvement)
- Ask for priority (high / medium / low)
- Add to backlog with status "open"

If no, skip.

## 8. Current Focus Check

Ask: "Current focus is: `[currentFocus]`. Is this still accurate?"

Options:
- Keep as is
- Update to: [new focus]
- Clear (no specific focus)

Update state.json accordingly.

## 9. Commit State Changes

```bash
git add .claude/state.json
git diff --cached --quiet || git commit -m "chore: update project state"
```

## 10. Push

```bash
git push
```

If push fails:
- Report error
- Tell user: "State was committed locally. Fix push issue and run `git push` manually."

## 11. Summary

```
PUSH COMPLETE
=============
Commits pushed: 3
Shipped: fix(ui): mobile menu navigation
Backlog: 1 resolved, 3 open, 1 added
Current focus: "Implementing dark mode"

State file updated ✓
```

$ARGUMENTS
