---
description: Commit only the changes YOU made in this session
---

Commit the code changes that YOU (this Claude Code session) made, and capture any discoveries while context is fresh. Execute without asking for confirmation.

## 1. Identify Your Changes

Recall which files YOU modified during this conversation. Run `git status` and `git diff` to see changes.

## 2. Stage and Commit

Stage ONLY files YOU edited. If you see changes you don't recognize, leave them alone.

Use conventional format: `type(scope): description`
- Types: `feat`, `fix`, `refactor`, `style`, `docs`, `test`, `chore`
- Under 72 characters, imperative mood
- NO "Co-authored-by", NO AI mentions

## 3. Capture Discoveries

While working, you likely noticed things: tech debt, potential bugs, improvement opportunities, TODOs worth tracking. This is the moment to capture them—your context is fresh.

Read `.claude/state.json` (create if missing). Add any discoveries to the backlog:

```json
{
  "description": "what you found",
  "type": "tech-debt | bug | improvement | idea",
  "priority": "high | medium | low",
  "status": "open",
  "context": "where/how you discovered it",
  "added": "YYYY-MM-DD"
}
```

Only add genuine discoveries—things that would be valuable to address later. Don't pad the backlog with noise.

If you discovered nothing worth tracking, that's fine. Not every session produces backlog items.

## 4. Commit State If Changed

If you added backlog items:
```bash
git add .claude/state.json
git commit -m "chore: capture session discoveries"
```

## 5. Report

Show what was committed and what was discovered:
```
COMMITTED
=========
abc1234 feat(auth): add token refresh

Discoveries added to backlog:
- [tech-debt] Rate limiting logic duplicated in 3 places
- [bug] Token expiry not handled in offline mode
```

Or if no discoveries: "No new backlog items."

Do NOT push—use `/push` when ready.

$ARGUMENTS
