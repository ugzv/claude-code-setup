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

## Pre-Push CI Checks (Parallel)

Before pushing, run the **exact same checks that CI will run**. This prevents the "push → CI fails → fix → push again" cycle.

**IMPORTANT: Run all pre-push checks in parallel using subagents.** Don't wait for linting to finish before starting type checking.

### Detection Phase (Quick)

First, detect what CI runs:

```bash
# Parse CI config for tools
grep -E "black|ruff|eslint|prettier|flake8|mypy|pytest|tsc" .github/workflows/*.yml 2>/dev/null
```

Fallback to `pyproject.toml` / `package.json` if no CI config.

### Parallel Check Phase

**Spawn subagents for each detected check simultaneously:**

```
┌─────────────────────────────────────────────────────────┐
│  SPAWN ALL AT ONCE (single message, multiple Task calls)│
├─────────────────────────────────────────────────────────┤
│  0. lockfile-checker (ALWAYS RUN FIRST)                 │
│     → Verify lockfile matches manifest                  │
│     → Return: pass/fail + what's out of sync            │
│                                                         │
│  1. format-checker                                      │
│     → black --check / prettier --check                  │
│     → Return: pass/fail + files needing format          │
│                                                         │
│  2. lint-checker                                        │
│     → ruff check / eslint                               │
│     → Return: pass/fail + error count                   │
│                                                         │
│  3. type-checker (if CI uses it)                        │
│     → mypy / tsc --noEmit                               │
│     → Return: pass/fail + error count                   │
│                                                         │
│  4. test-runner (if CI runs tests)                      │
│     → pytest / npm test                                 │
│     → Return: pass/fail + failure summary               │
└─────────────────────────────────────────────────────────┘
```

### Lockfile Sync Check (Critical)

**Why this matters:** Lockfiles often get out of sync when dependencies are added/removed but the lockfile isn't regenerated. This passes locally but fails in CI with `--frozen-lockfile`.

**Detection and verification by package manager:**

| Lockfile | Manifest | Check Command |
|----------|----------|---------------|
| `pnpm-lock.yaml` | `package.json` | `pnpm install --frozen-lockfile` |
| `package-lock.json` | `package.json` | `npm ci` (or `npm install --package-lock-only`) |
| `yarn.lock` | `package.json` | `yarn install --frozen-lockfile` |
| `uv.lock` | `pyproject.toml` | `uv lock --check` |
| `poetry.lock` | `pyproject.toml` | `poetry check --lock` |
| `Cargo.lock` | `Cargo.toml` | `cargo check --locked` |

**On failure, report clearly:**
```
✗ lockfile: pnpm-lock.yaml is out of sync with package.json
  → 1 dependency removed from package.json but still in lockfile

  Fix: Run 'pnpm install' to regenerate lockfile, then commit it.
```

**Auto-fix option:** If lockfile is out of sync, offer to run the install command and commit the updated lockfile before proceeding.

**Example subagent prompt:**
```
Run format check for this project. Use the tool that CI uses:
- If black in CI: black --check .
- If prettier in CI: npx prettier --check .
- If ruff format in CI: ruff format --check .

Return: {"pass": true/false, "files_to_fix": [...]}
```

### Gate Decision

After all checks complete:
- **All pass:** Proceed to push
- **Any fail:** Stop and report which checks failed:
  ```
  Pre-push checks failed:
  ✗ lockfile: pnpm-lock.yaml out of sync (1 removed dep)
  ✗ format: 3 files need formatting
  ✗ lint: 12 errors
  ✓ types: passed

  Run /fix to auto-fix, or /push --force to skip checks.
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
