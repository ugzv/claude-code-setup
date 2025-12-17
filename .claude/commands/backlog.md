---
description: Review and manage backlog items
---

## The Problem You're Solving

Work gets lost between sessions. Ideas noticed while debugging, tech debt spotted while adding features, bugs found while testing—these insights evaporate when the conversation ends.

The backlog is persistent memory. Your job is to surface what's actionable and help the user pick something to work on.

## What Matters

**Actionability over completeness.** The user came here to start working, not to review a database. Lead with what they can do right now. High priority items first. Clear enough to act on.

**Code truth over backlog truth.** Backlog items are hypotheses written in the past. The codebase is reality now. Before working on any item, verify it still applies. Files get refactored, problems get solved incidentally, scope changes. An item that says "split this 1,200 line file" might describe a file that's already been split.

**Friction kills momentum.** The path from "show me the backlog" to "I'm working on something" should be one decision. Number the items. User says "2" and you're off. No menus, no confirmations, no "are you sure."

## Reading the Backlog

Read `.claude/state.json`. If missing, tell the user to run `/migrate` first.

Show open items numbered by priority (high → medium → low). Include enough context that the user can pick without asking follow-up questions. Show current focus if set.

End with a simple prompt—the user should know they can pick a number or ask for something else (add, resolve, clean).

## When the User Picks an Item

This is the critical moment. Don't start implementing the backlog description. Start by validating it.

### 1. Check for Conflicts

Before starting, identify what files this work will likely touch. Then check `currentFocus` array for overlaps:

- If another focus item lists files that overlap with this work, **warn the user**:
  ```
  ⚠️ Potential conflict: "[other focus description]" is working on:
    - src/auth.ts
    - src/middleware/auth.ts

  This task may also touch those files. Continue anyway?
  ```

- If no overlap or user confirms, proceed.

### 2. Validate the Item

Read the relevant code. Does the problem still exist? Is it the same shape as described? Sometimes you'll find it's already fixed. Sometimes it's worse than described. Sometimes the whole context has changed.

If stale: update or resolve the item, tell the user what you found.

### 3. Register Your Focus

If valid, add to `currentFocus` array before starting work:
```json
{
  "description": "short description of work",
  "files": ["files", "you'll", "touch"],
  "started": "YYYY-MM-DD"
}
```

Then begin work.

## Managing the Backlog

Users may want to add items, mark things resolved, or clean up old entries. Handle these naturally—no rigid command syntax required. "mark 2 done", "add a bug about the login timeout", "clean up old stuff" should all work.

After any change, save state.json and confirm briefly.

$ARGUMENTS
