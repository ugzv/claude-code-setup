---
description: Commit only the changes YOU made in this session
---

Commit the code changes that YOU (this Claude Code session) made. Execute without asking for confirmation.

## 1. Identify Your Changes
- Recall which files YOU modified during this conversation
- Run `git status` and `git diff` to see changes

## 2. Stage Your Files
- Stage ONLY files YOU edited: `git add <files>`
- If you see changes you don't recognize, leave them alone

## 3. Commit Immediately
- Use conventional format: `type(scope): description`
- Types: `feat`, `fix`, `refactor`, `style`, `docs`, `test`, `chore`
- Under 72 characters, imperative mood
- NO "Co-authored-by", NO AI mentions

```bash
git add <your-files>
git commit -m "type(scope): description"
```

## 4. Report
Show the commit hash and message. Done.

Do NOT push - use `/push` when ready.

$ARGUMENTS
