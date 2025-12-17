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

## The Push Itself

Check what's being pushed first. If there's nothing to push, say so and stop.

If state.json changed, commit that separately before pushing—the state update shouldn't be tangled with feature work.

Push to remote. If it fails, report the error clearly.

## After Pushing

Summarize: how many commits, what shipped, backlog status. The user should know what just went out and what the project state looks like now.

$ARGUMENTS
