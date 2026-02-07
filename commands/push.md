---
description: "Push changes and update state [--force to skip checks]"
---

Push to remote and update `.claude/state.json`. Fully automatic.

## Guiding Principles

**Momentum over investigation.** This is a push command, not a debugging session. When something unexpected happens — unfamiliar errors, files in odd states, tools misbehaving — note it for the summary and keep moving. Two tool calls to understand an anomaly is fine; eight is a rabbit hole.

**Fix, don't report.** If a problem is auto-fixable (formatting, simple lint), fix it. Only block the push on issues that genuinely need human attention.

**Direct Bash calls, not sub-agents.** Sub-agents add ~8k tokens of overhead each. Run all checks as parallel Bash calls in a single message.

## Pre-Push: Detect → Fix → Verify → Gate

### Detect

Read config files (package.json, pyproject.toml, CI workflows, etc.) to learn what tools and checks exist. Only run tools you've confirmed are available — never guess at paths or CLI flags.

### Fix and Commit

Run formatters and linters in auto-fix mode (parallel). If anything changed, stage only the files fixers modified — not unrelated changes — and commit as a separate `style:` commit to keep feature commits clean.

### Verify

Run checks that can't be auto-fixed — type checking, tests, remaining lint errors — in parallel. These confirm the code is push-ready.

### Gate

All pass → push. Any failure → stop and report what needs manual attention.

## Push and Summarize

Check what commits the current branch has ahead of its upstream. If nothing to push, say so and stop. Commit state.json separately if it changed, then push.

Summarize: commits pushed, what shipped, backlog changes.

## State Tracking

Sessions are ephemeral. `state.json` creates continuity so the next session picks up where this one left off.

**What to update:**
- **lastSession**: Date, summary, commits pushed
- **shipped**: Add entry for what's being pushed (keep max 10, drop oldest). Write state.json in a single atomic update, not incremental edits
- **currentFocus**: Clear this session's focus; leave others
- **backlog**: Resolve items addressed by what was pushed

If `state.json` isn't a committed file or doesn't exist on disk, skip state tracking and tell the user.

## Handoff Cleanup

Delete completed handoffs — their work is already tracked in `shipped`. A handoff is done when all phases are complete AND the working tree is clean (the `.md` plan file gets deleted, so uncommitted work should keep it around). Report what you cleaned up.

## CI Status Check

After pushing, poll CI until all jobs pass or ~10 minutes elapse — if still running, report status and let the user decide whether to wait. Match runs to the exact pushed SHA. On failure, show which job failed and how to view logs. Detect the provider from `git remote get-url origin` (GitHub → `gh`, GitLab → `glab`). No CI or unknown provider → push is done, inform user.

$ARGUMENTS
