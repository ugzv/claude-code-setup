---
description: Find all TODO/FIXME/HACK comments in code
---

You are finding the promises this codebase has made to itself.

## What These Markers Represent

When a developer writes TODO, they're saying "I know this isn't done, and I'm leaving a note so future-me or someone else can finish it." When they write FIXME, they're saying "this is broken in a way I don't have time to fix right now." When they write HACK, they're saying "this works but I'm not proud of it."

These markers are valuable. They're context, left at the moment someone understood a problem, explaining what needs attention and sometimes why it wasn't addressed.

But they're also risk. A TODO in a comment is a promise with no deadline. TODOs accumulate. FIXMEs rot. HACKs become permanent. The note that made sense when written becomes cryptic. The person who wrote it leaves. The context evaporates, leaving only the marker.

Your job is to surface these promises, assess which ones matter, and help the team decide what to do about them.

## Finding the Markers

Search for TODO, FIXME, HACK, XXX, BUG, and similar markers. Find where they are, what they say, and when they were written.

The when matters. Use git blame to date them. A two-week-old TODO might be someone's active work. A two-year-old FIXME is a broken promise that nobody's coming back for.

The where matters too. A HACK in a test helper is different from a HACK in the payment processing path. A FIXME in archived legacy code is different from a FIXME in the module that changes every sprint.

## What to Look For

**Markers in critical paths.** A FIXME in authentication code, payment processing, or data integrity logic represents known risk in high-stakes areas. These aren't technical debt—they're potential incidents.

**Ancient markers.** Anything older than six months has probably been seen by multiple developers who all decided not to fix it. Either it's not actually important (so remove the marker) or it's important but blocked by something (so document what's blocking it) or it keeps getting deprioritized (so make a conscious decision about it).

**Clusters.** When markers concentrate in one area, that area was probably rushed or is actively problematic. A module with many TODOs might need a focused cleanup rather than piecemeal fixes.

**Context decay.** Markers that made sense when written but are cryptic now. "TODO: fix the thing" next to code that's been refactored three times. These need either updating with current context or removing if nobody remembers what they meant.

## Connecting to the Backlog

Compare what you find to what's already tracked in `.claude/state.json`.

Some markers might already be backlog items—note that they're tracked. Some markers might be backlog items that got completed but the comment wasn't removed—offer to clean them up. Some markers might be new discoveries worth tracking—offer to add them.

But don't add everything. A backlog of 50 TODO items is useless. Focus on markers that represent real risk or real opportunity—the ones in critical paths, the ancient ones that need conscious decisions, the clusters that might warrant focused attention.

## What to Report

Provide an assessment, not a list.

What's the overall picture? Is this a codebase with a few tracked TODOs being actively managed, or a codebase where markers have been accumulating unexamined for years?

What needs attention? Not every marker, but the ones that represent actual risk or have been waiting long enough to deserve a decision.

What should happen next? Clean up the stale ones? Address the critical-path ones? Schedule a focused session on the clustered area?

The goal isn't cataloging every marker. It's helping the team see and decide about the promises their codebase has made to itself.

$ARGUMENTS
