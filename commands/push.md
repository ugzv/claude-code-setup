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

## Pre-Push: Auto-Fix, Then Verify

**Goal:** Push clean code. Don't report fixable problems — fix them automatically.

**IMPORTANT: Use direct Bash calls, NOT Task/sub-agents.** Send all checks as parallel Bash tool calls in a single message. Sub-agents add ~8k tokens of overhead each.

### Step 1: Auto-Fix (parallel Bash calls)

**Detect which tools exist** from project config (package.json, pyproject.toml, composer.json, CI config), then run all applicable fixers in parallel:

- **Formatting** — black / prettier --write / pint (auto-fix mode, not --check)
- **Linting** — ruff check --fix / eslint --fix (auto-fix mode)

Only run fixers that exist in the project. Skip what doesn't apply.

### Step 2: Commit Fixes (if anything changed)

If auto-fixers modified files, commit them as a separate `style:` commit before the push. This keeps the user's feature commits clean and the fixes attributable.

### Step 3: Verify (parallel Bash calls)

Run checks that can't be auto-fixed, plus confirm fixers worked:

- **Lockfile sync** — npm ci --dry-run / pip check / composer validate
- **Type checking** — mypy / tsc --noEmit (only if CI uses it)
- **Tests** — pytest / npm test / phpunit (only if CI runs tests)
- **Remaining lint/format errors** — run checkers (--check mode) to catch anything fixers couldn't resolve

### Gate Decision

- **All pass**: Proceed to push
- **Any fail**: Stop, report what failed and why (these are real issues that need manual attention)

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

## CI Status Check

```bash
gh run list --branch $(git branch --show-current) --limit 1
```

- **success**: "CI passed"
- **in_progress**: "CI running..."
- **failure**: Investigate with `gh run view <id> --log-failed`, offer to fix

$ARGUMENTS
