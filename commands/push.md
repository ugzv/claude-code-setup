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

**Goal:** Keep the active handoffs list focused on real work-in-progress. Archive completed work while preserving learnings.

**When to archive:** A handoff is ready for archiving when:
1. All phases have `status: "complete"`
2. The working tree is clean (`git status` shows no uncommitted changes)

The second check matters because we delete the `.md` plan file during archiving—if work is uncommitted, the plan might still be needed.

**What to preserve:** When archiving, synthesize value from the work:
- `summary`: One line describing what was accomplished
- `totalLearnings`: Consolidate insights from all phase `learnings` fields into the key takeaway for future sessions
- `completed`: Today's date

**The cleanup:**
1. Read `.claude/handoffs.json`
2. For each active handoff meeting archive criteria: move to `archived[]`, delete `.claude/handoffs/{id}.md`
3. Write updated handoffs.json
4. Report: "Archived: {title}" for each

**If phases complete but uncommitted changes exist:** Keep active, note: "Handoff '{title}' complete but has uncommitted changes—will archive after commit."

**Why this matters:** Completed handoffs clutter the active list and create noise on session start. The `.md` plan lives in git history. Learnings persist in the archive. Clean state = clear focus.

## CI Status Check

```bash
gh run list --branch $(git branch --show-current) --limit 1
```

- **success**: "CI passed"
- **in_progress**: "CI running..."
- **failure**: Investigate with `gh run view <id> --log-failed`, offer to fix

$ARGUMENTS
