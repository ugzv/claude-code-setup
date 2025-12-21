---
description: Push changes and update project state
---

Push to remote and update `.claude/state.json`. Fully automatic—no confirmations needed.

## Why State Tracking Matters

Claude sessions are ephemeral. When this conversation ends, everything you learned about the project—what you were working on, what you discovered, what you shipped—evaporates. The next session starts from zero.

State tracking creates continuity. The next Claude (maybe you after context refresh, maybe a different session) can pick up where work left off instead of asking "what should we do?" when the answer is sitting in half-finished work.

## What State Captures

**lastSession:** What just happened. The next session's first question is "what did we do last time?"—this answers it. Include the date, a summary of what was accomplished, and which commits were pushed.

**shipped:** Meaningful completions. Not every commit matters at this level—routine chores don't need celebration. But features, fixes, refactors that change behavior? Those are worth recording. The question is: "Would someone reviewing the project's progress care that this happened?"

**currentFocus:** What's actively being worked on. This session's focus item should be removed when pushing (the work is done). Other sessions' focus items stay—they're still in progress elsewhere.

**backlog:** Auto-resolve items that match what was just pushed. If a commit clearly addresses a backlog item, mark it resolved. Discoveries were captured during `/commit`, not here.

## Pre-Push Lint Check

Before pushing, check for lint/format issues—but only if the project has tools configured. Don't enforce anything that doesn't exist.

### Detection

**Python:** Check `pyproject.toml` for:
- `ruff` → run `ruff check .`
- `black` → run `black --check .`
- `flake8` → run `flake8 .`

**JS/TS:** Check `package.json` for:
- `eslint` in devDependencies → run `npx eslint .`
- `prettier` in devDependencies → run `npx prettier --check .`
- `biome` in devDependencies → run `npx biome check .`

### Behavior

- **No tools found:** Skip silently, proceed to push
- **Tools found, no issues:** Proceed to push
- **Tools found, issues detected:** Stop and warn:
  ```
  Lint issues found. Run /fix to auto-fix, or push anyway with /push --force
  ```

The `--force` flag skips lint checks for cases where you know CI will handle it or issues are intentional.

## The Push Itself

Check what's being pushed first. If there's nothing to push, say so and stop.

If state.json changed, commit that separately before pushing—the state update shouldn't be tangled with feature work.

Push to remote. If it fails, report the error clearly.

## After Pushing

Summarize: how many commits, what shipped, backlog status. The user should know what just went out and what the project state looks like now.

## CI Status Check

After pushing, check if this repo has CI configured and report the status. Don't wait for completion—just report current state.

```bash
# Check latest workflow run for this branch
gh run list --branch $(git branch --show-current) --limit 1
```

**Report based on status:**
- **completed + success:** "CI passed ✓"
- **in_progress / queued:** "CI running..." (no need to wait)
- **completed + failure:** Investigate and report (see below)

### When CI Fails

Don't just report failure—dig in and help fix it.

```bash
# Get the failed run ID from gh run list, then:
gh run view <run-id> --log-failed
```

This shows the actual error output. Common failures:
- **Lint/format:** Run `/fix` locally, commit, push again
- **Type errors:** Fix the types, commit, push
- **Test failures:** Run `/test` locally to reproduce, fix, commit, push
- **Dependency issues:** Check lockfile is committed, run install locally

Report what failed and why. If it's fixable (lint, format, types), offer to fix it now. If it needs investigation, explain what you found in the logs.

If `gh` isn't available or the repo has no CI, skip silently—not every project uses GitHub Actions.

$ARGUMENTS
