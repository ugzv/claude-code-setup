---
description: "Push changes and update state [--force to skip checks]"
---

Push to remote and update `.state/state.json` (fall back to legacy `.claude/state.json` only when needed). Fully automatic.

## Guiding Principles

**Momentum over investigation.** This is a push command, not a debugging session. When something unexpected happens — unfamiliar errors, files in odd states, tools misbehaving — note it for the summary and keep moving. Two tool calls to understand an anomaly is fine; eight is a rabbit hole.

**Fix, don't report.** If a problem is auto-fixable (formatting, simple lint), fix it. Only block the push on issues that genuinely need human attention.

**Direct Bash calls, not sub-agents.** Sub-agents add ~8k tokens of overhead each. Run all checks as parallel Bash calls in a single message.

**No silent long waits.** If a check or CI poll runs for more than a couple of minutes, report what is still running and what evidence you have so far. Keep going, but don't leave the user guessing whether the command is stuck.

## Pre-Push: Detect → Fix → Verify → Gate

### Detect

Read config files (package.json, pyproject.toml, CI workflows, etc.) to learn what tools and checks exist. Only run tools you've confirmed are available — never guess at paths or CLI flags.

### Fix and Commit

Run formatters and linters in auto-fix mode (parallel). If anything changed, stage only the files fixers modified — not unrelated changes — and commit as a separate `style:` commit to keep feature commits clean.

### Verify

Run checks that can't be auto-fixed — type checking, tests, remaining lint errors — in parallel. These confirm the code is push-ready.

For long-running checks, prefer commands that stream or periodically show progress. If a tool can hang indefinitely, wrap it in the repo's normal timeout mechanism when available, or use a reasonable shell timeout and report that timeout explicitly if it fires.

### Gate

All pass → push. Any failure → stop and report what needs manual attention.

## Push and Summarize

Check what commits the current branch has ahead of its upstream. If nothing to push, say so and stop. Update `state.json` on disk when state tracking exists, but do **not** stage or commit it. Push code/docs commits only.

Summarize: commits pushed, what shipped, state update result, backlog changes.

## State Tracking

Sessions are ephemeral. `state.json` creates continuity so the next session picks up where this one left off.

**State path order:**
1. Prefer `.state/state.json`
2. If missing, fall back to legacy `.claude/state.json`
3. If neither exists, skip state tracking and tell the user

`.state/` is excluded from git via `.git/info/exclude` — this is intentional. State is local-only and should **never be committed or pushed**. Just update the file on disk.

**What to update:**
- **lastSession**: Date, concise summary, commits pushed, and uncommitted status if already tracked
- **shipped**: Add one entry for what's being pushed, then keep max 10 and drop oldest entries. New entries should use this shape:
  - `date`: today's date
  - `type`: conventional commit type summary derived from pushed commits, e.g. `fix`, `feat+fix`, `docs`
  - `summary`: one compact sentence, usually under 300 characters; describe outcomes, not every file path or test name
  - `commits`: short SHAs that were pushed
- **currentFocus**: Clear this session's focus; leave others
- **backlog**: Resolve items addressed by what was pushed

**State editing rules:**
- Existing state may contain older entries with missing fields. Treat `type`, `commits`, and other keys as optional when reading or summarizing history.
- Use targeted Edit calls on `state.json` — never rewrite the whole file, as JSON serializers reformat it and create noisy diffs.
- After editing, validate JSON with an available parser such as `python3 -m json.tool` or `jq empty`; fix validation errors before pushing.

## Handoff Cleanup

Delete completed handoffs — their work is already tracked in `shipped`. A handoff is done when all phases are complete AND the working tree is clean (the `.md` plan file gets deleted, so uncommitted work should keep it around). Report what you cleaned up.

## CI Status Check

After pushing, poll CI until all jobs pass or ~10 minutes elapse — if still running, report status and let the user decide whether to wait. Match runs to the exact pushed SHA. On failure, show which job failed and how to view logs. Detect the provider from `git remote get-url origin` (GitHub → `gh`, GitLab → `glab`). No CI or unknown provider → push is done, inform user.

$ARGUMENTS
