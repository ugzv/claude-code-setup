---
description: Review and manage backlog items
---

Show what to work on next and manage the backlog.

## 1. Read State

```bash
cat .claude/state.json 2>/dev/null || echo "NO_STATE_FILE"
```

If no state file: "No state.json found. Run `/migrate` first." and STOP.

## 2. Show What's Next

Focus on the actionable. Display like this:

```
NEXT UP
=======
→ [high] Split InvestigationProvider.tsx into composable hooks
  Context: 1,200 lines, mixed concerns

Also open:
• [high] Markdown pipeline needs unified test suite
• [medium] Extract reader_mcp.py tool definitions

Current focus: investigation-provider-decomposition
```

Rules:
- Lead with the highest priority open item as "next up"
- Show remaining open items as a simple bullet list (no tables)
- Show current focus if set
- Skip resolved items unless user asks

## 3. Wait for Direction

Don't show a menu. Just wait. The user will either:
- Start working ("let's do it", "work on #1")
- Ask to manage ("mark #2 resolved", "add a bug", "clean up old items")
- Move on ("done", "thanks")

## 4. Handle Requests

**Working on an item:**
- First, validate: read the relevant code and verify the issue still exists
- Backlog items can be stale - the codebase is the source of truth, not the description
- If the issue was already fixed or changed significantly, update or resolve the item
- If still valid, understand the current state before planning the approach
- Then begin implementation

**Mark resolved:** Update status to "resolved", set date

**Mark wont-do:** Update status to "wont-do", set date, ask for brief reason

**Add item:** Ask for description, type, priority, context

**Remove:** Confirm, then delete from array

**Clean up:** Remove resolved/wont-do items older than 7 days

**Show all:** Display full backlog including resolved items

## 5. Save Changes

After any modification, write state.json and confirm briefly.

$ARGUMENTS
