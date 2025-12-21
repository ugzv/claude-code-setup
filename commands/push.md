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

## Pre-Push CI Check

Before pushing, run the **exact same checks that CI will run**. This prevents the "push → CI fails → fix → push again" cycle.

### Detection Priority

1. **CI config is the source of truth.** Check `.github/workflows/*.yml` to see what commands CI actually runs.
2. **Fallback to pyproject.toml / package.json** if no CI config exists.

### Parse CI Config

```bash
# Look for lint/format commands in CI
grep -E "black|ruff|eslint|prettier|flake8|mypy|pytest" .github/workflows/*.yml
```

Common patterns to detect:
- `black --check` → run `black --check .`
- `ruff check` → run `ruff check .`
- `eslint` → run `npx eslint .`
- `prettier --check` → run `npx prettier --check .`
- `pytest` → consider running tests too

### Fallback Detection

If no CI config exists:

**Python:** Check `pyproject.toml` for:
- `[tool.ruff]` → run `ruff check .`
- `[tool.black]` → run `black --check .`

**JS/TS:** Check `package.json` devDependencies for:
- `eslint` → run `npx eslint .`
- `prettier` → run `npx prettier --check .`

### Behavior

- **No CI config or tools found:** Skip silently, proceed to push
- **Checks pass:** Proceed to push
- **Checks fail:** Stop and warn:
  ```
  CI checks would fail:
  - black --check: 3 files need formatting

  Run /fix to auto-fix, or /push --force to push anyway.
  ```

The `--force` flag skips checks for cases where you intentionally want CI to run first.

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
