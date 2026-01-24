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
│  0. lockfile-checker (CRITICAL - CI's #1 failure)      │
│     → npm ci / pnpm install --frozen-lockfile /        │
│       yarn install --frozen-lockfile                   │
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

**Goal:** Keep the active handoffs list focused on real work-in-progress. Delete completed handoffs—their work is already tracked in `state.json` shipped history.

**When to remove:** A handoff is ready for removal when:
1. All phases have `status: "complete"`
2. The working tree is clean (`git status` shows no uncommitted changes)

The second check matters because we delete the `.md` plan file—if work is uncommitted, the plan might still be needed.

**The cleanup:**
1. Read `.claude/handoffs.json`
2. For each active handoff meeting removal criteria: delete from `active[]`, delete `.claude/handoffs/{id}.md`
3. Write updated handoffs.json
4. Report: "Completed: {title}" for each

**If phases complete but uncommitted changes exist:** Keep active, note: "Handoff '{title}' complete but has uncommitted changes—will remove after commit."

**Why delete, not archive:** The shipped array in `state.json` already captures what was completed. The `.md` plan lives in git history if needed. Archiving creates duplicate data that never gets used.

## CI Status Check (Post-Push)

After pushing, verify CI passes before considering push complete.

### Why This Matters

Push → CI fail → fix → push again wastes time. Catching failures immediately lets you fix while context is fresh.

### Principles

1. **Verify the exact commit** — Match CI runs/pipelines to the pushed SHA, not "latest on branch"
2. **All jobs must pass** — If multiple workflows/jobs exist, wait for all of them
3. **Graceful degradation** — Unknown provider or no CI configured = push is done, inform user
4. **Time-bounded** — Cap at ~10 minutes, then report status and let user decide
5. **Actionable failures** — On failure, show which job failed and how to view logs

### Provider Detection

Check `git remote get-url origin`:
- `github.com` → use `gh` CLI
- `gitlab` anywhere in URL → use `glab` CLI (covers self-hosted)
- Neither → skip CI check gracefully

### Implementation Notes

Use each provider's CLI to:
1. Find runs/pipelines matching the pushed commit SHA
2. Poll until all complete (first check ~30s after push, then ~60s intervals)
3. On failure, provide the command to view failed logs

The specific CLI commands vary by provider version — use `gh run list --help` or `glab ci --help` to find current syntax. The principles above define what you're trying to achieve.

$ARGUMENTS
