---
description: "Push changes and update state [--force to skip checks]"
---

Push to remote and update `.claude/state.json`. Fully automatic.

## Why State Tracking

Claude sessions are ephemeral. State tracking creates continuity - next session picks up where work left off.

## What State Captures

- **lastSession**: Date, summary, commits pushed
- **shipped**: Last 10 completions only (older history in git commits)
- **currentFocus**: Remove this session's focus when pushing; others stay
- **backlog**: Auto-resolve items that match what was pushed

**Keep state.json small**: Trim shipped to 10 entries when saving. For older history, use `git log`.

## Pre-Push CI Checks (Parallel)

**Run same checks CI will run** to prevent push → fail → fix → push cycle.

**Spawn all checks at once:**

```
┌────────────────────────────────────────────────────────┐
│  SPAWN ALL AT ONCE                                     │
├────────────────────────────────────────────────────────┤
│  0. lockfile-checker (CRITICAL)                        │
│     → Verify lockfile matches manifest                 │
│     → Return: pass/fail + what's out of sync           │
│                                                        │
│  1. format-checker                                     │
│     → black --check / prettier --check / pint --test   │
│     → Return: pass/fail + files needing format         │
│                                                        │
│  2. lint-checker                                       │
│     → ruff check / eslint / phpstan / phpcs            │
│     → Return: pass/fail + error count                  │
│                                                        │
│  3. type-checker (if CI uses it)                       │
│     → mypy / tsc --noEmit                              │
│     → Return: pass/fail + error count                  │
│                                                        │
│  4. test-runner (if CI runs tests)                     │
│     → pytest / npm test / phpunit                      │
│     → Return: pass/fail + failure summary              │
└────────────────────────────────────────────────────────┘
```

### Gate Decision

- **All pass**: Proceed to push
- **Any fail**: Stop, report which failed, suggest `/fix` or `--force` to skip

## The Push

Check what's being pushed first. If nothing, say so and stop.

If state.json changed, commit separately before pushing.

## After Pushing

Summarize: commits pushed, what shipped, backlog status.

## Handoff Cleanup

If `.claude/handoffs.json` exists with active handoffs:

```
For each active handoff:
  If ALL phases have status "complete":
    Check if related files are committed (git status clean)
    If yes:
      → Move entry from active[] to archived[]
      → Add summary + completed date
      → Delete .claude/handoffs/{id}.md (it's in git history)
      → Log: "Archived handoff: {title}"
    If no:
      → Keep as-is, warn: "Handoff complete but has uncommitted files"
  Else:
    → Keep as-is (in progress)
```

**Why auto-archive:** Completed handoffs clutter the active list. Once code is pushed, the .md file lives in git history. Archiving keeps the system clean while preserving history.

## CI Status Check

```bash
gh run list --branch $(git branch --show-current) --limit 1
```

- **success**: "CI passed"
- **in_progress**: "CI running..."
- **failure**: Investigate with `gh run view <id> --log-failed`, offer to fix

$ARGUMENTS
